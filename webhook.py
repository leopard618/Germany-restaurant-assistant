import logging
import json
import base64
import asyncio
import numpy as np

try:
    import audioop
except ModuleNotFoundError:
    import audioop_lts as audioop

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from livekit import api, rtc
import uvicorn
from config import AppConfig

logging.basicConfig(
    level=getattr(logging, AppConfig.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

app = FastAPI(title="Restaurant Reservation Voice Agent")
active_sessions = set()


def _generate_twiml_response(stream_url, call_sid, room_name, from_number):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{stream_url}">
            <Parameter name="callSid" value="{call_sid}"/>
            <Parameter name="roomName" value="{room_name}"/>
            <Parameter name="fromNumber" value="{from_number}"/>
        </Stream>
    </Connect>
</Response>"""


def _generate_error_twiml():
    return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">Sorry, there was an error connecting your call. Please try again later.</Say>
    <Hangup/>
</Response>"""


@app.post("/webhook/incoming")
async def handle_incoming_call(request: Request):
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        from_number = form_data.get("From")
        to_number = form_data.get("To")
        
        active_sessions.add(call_sid)
        
        room_name = f"call-{call_sid}"
        log.info(f"Created room '{room_name}' for call {call_sid}")
        
        webhook_base_url = request.url.scheme + "://" + request.url.netloc
        stream_url = f"{webhook_base_url.replace('http', 'ws')}/media-stream"
        
        twiml_response = _generate_twiml_response(stream_url, call_sid, room_name, from_number)
        
        log.info(f"TwiML response created for {call_sid}")
        log.info(f"Active calls: {len(active_sessions)}")
        
        return Response(
            content=twiml_response,
            media_type="application/xml"
        )
        
    except Exception as e:
        log.error(f"Error handling incoming call: {e}", exc_info=True)
        return Response(
            content=_generate_error_twiml(),
            media_type="application/xml"
        )


async def _create_livekit_token(room_name, from_number):
    token = api.AccessToken(
        AppConfig.LIVEKIT_API_KEY,
        AppConfig.LIVEKIT_API_SECRET
    )
    token.with_identity(f"phone-{from_number}")
    token.with_name("Phone Caller")
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
    ))
    return token.to_jwt()


async def _publish_phone_audio(room):
    audio_source = rtc.AudioSource(8000, 1)
    track = rtc.LocalAudioTrack.create_audio_track("phone-audio", audio_source)
    options = rtc.TrackPublishOptions()
    options.source = rtc.TrackSource.SOURCE_MICROPHONE
    await room.local_participant.publish_track(track, options)
    log.info("Published phone audio track to room")
    return audio_source


async def _process_twilio_audio(media_payload, audio_source):
    mulaw_data = base64.b64decode(media_payload)
    pcm_data = audioop.ulaw2lin(mulaw_data, 2)
    audio_array = np.frombuffer(pcm_data, dtype=np.int16)
    
    audio_frame = rtc.AudioFrame(
        data=audio_array,
        sample_rate=8000,
        num_channels=1,
        samples_per_channel=len(audio_array)
    )
    
    await audio_source.capture_frame(audio_frame)


async def _process_agent_audio(track, stream_sid, websocket):
    try:
        audio_stream = rtc.AudioStream(track)
        log.info("Streaming agent audio to Twilio")
        
        async for audio_frame_event in audio_stream:
            try:
                frame = audio_frame_event.frame
                pcm_data = frame.data.tobytes()
                
                if frame.sample_rate != 8000:
                    pcm_data, _ = audioop.ratecv(
                        pcm_data,
                        2,
                        frame.num_channels,
                        frame.sample_rate,
                        8000,
                        None
                    )
                
                if frame.num_channels == 2:
                    pcm_data = audioop.tomono(pcm_data, 2, 1, 1)
                
                mulaw_data = audioop.lin2ulaw(pcm_data, 2)
                encoded_audio = base64.b64encode(mulaw_data).decode('utf-8')
                
                media_msg = {
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {
                        "payload": encoded_audio
                    }
                }
                await websocket.send_text(json.dumps(media_msg))
                
            except Exception as e:
                log.error(f"Error processing audio frame: {e}")
                
    except Exception as e:
        log.error(f"Error streaming agent audio: {e}", exc_info=True)


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()
    log.info("Media stream WebSocket connected")
    
    call_sid = None
    room_name = None
    room = None
    audio_source = None
    stream_sid = None
    
    try:
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                event_type = data.get("event")
                
                if event_type == "start":
                    stream_sid = data.get("streamSid")
                    call_sid = data.get("start", {}).get("callSid")
                    custom_params = data.get("start", {}).get("customParameters", {})
                    room_name = custom_params.get("roomName")
                    from_number = custom_params.get("fromNumber")
                    
                    log.info(f"Stream started: {stream_sid} for call {call_sid}")
                    log.info(f"Connecting to LiveKit room: {room_name}")
                    
                    room = rtc.Room()
                    token = await _create_livekit_token(room_name, from_number)
                    await room.connect(AppConfig.LIVEKIT_URL, token)
                    log.info(f"Connected to LiveKit room: {room_name}")
                    
                    audio_source = await _publish_phone_audio(room)
                    
                    @room.on("track_subscribed")
                    def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
                        if track.kind == rtc.TrackKind.KIND_AUDIO:
                            log.info(f"Subscribed to agent audio track from {participant.identity}")
                            asyncio.create_task(_process_agent_audio(track, stream_sid, websocket))
                
                elif event_type == "media":
                    if audio_source:
                        media_payload = data.get("media", {}).get("payload")
                        if media_payload:
                            try:
                                await _process_twilio_audio(media_payload, audio_source)
                            except Exception as e:
                                log.error(f"Error processing incoming audio: {e}")
                
                elif event_type == "stop":
                    log.info(f"Stream stopped for call {call_sid}")
                    break
                    
            except json.JSONDecodeError as e:
                log.error(f"Invalid JSON from Twilio: {e}")
                continue
            except WebSocketDisconnect:
                log.info(f"WebSocket disconnected for call {call_sid}")
                break
            except Exception as e:
                log.error(f"Error in media stream: {e}", exc_info=True)
                break
    
    finally:
        if room:
            await room.disconnect()
            log.info("Disconnected from LiveKit room")
        
        if call_sid:
            active_sessions.discard(call_sid)
            log.info(f"Cleaned up call {call_sid}")


@app.post("/call-status")
async def handle_call_status(request: Request):
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        
        log.info(f"Call status update: {call_sid} - {call_status}")
        
        if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
            active_sessions.discard(call_sid)
            log.info(f"Call ended: {call_sid}. Active calls: {len(active_sessions)}")
        
        return PlainTextResponse("OK")
        
    except Exception as e:
        log.error(f"Error handling call status: {e}", exc_info=True)
        return PlainTextResponse("OK")


@app.get("/metrics")
async def get_metrics():
    return {
        "active_calls": len(active_sessions),
        "max_concurrent_calls": AppConfig.MAX_CONCURRENT_CALLS,
        "utilization_percent": (len(active_sessions) / AppConfig.MAX_CONCURRENT_CALLS) * 100
    }


def start_server():
    uvicorn.run(
        app,
        host=AppConfig.WEBHOOK_HOST,
        port=AppConfig.WEBHOOK_PORT,
        log_level=AppConfig.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    start_server()
