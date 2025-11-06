import asyncio
import logging
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, voice
from livekit.plugins import openai
from config import AppConfig

logging.basicConfig(
    level=getattr(logging, AppConfig.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


def _create_realtime_model():
    from livekit.plugins.openai.realtime.realtime_model import TurnDetection
    
    return openai.realtime.RealtimeModel(
        voice=AppConfig.VOICE_MODEL,
        temperature=0.8,
        modalities=["text", "audio"],
        turn_detection=TurnDetection(
            type="server_vad",
            threshold=0.8,
            prefix_padding_ms=300,
            silence_duration_ms=600,
        ),
    )


def _create_voice_agent(realtime_model):
    return voice.Agent(
        instructions=AppConfig.SYSTEM_PROMPT,
        llm=realtime_model,
        tts=openai.TTS(voice=AppConfig.VOICE_MODEL),
    )


async def _maintain_session(room):
    while room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
        await asyncio.sleep(0.5)


async def handle_session(job_ctx: JobContext):
    try:
        log.info(f"Session started: {job_ctx.room.name}")
        
        await job_ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        log.info(f"Connected to room: {job_ctx.room.name}")
        
        participant = await job_ctx.wait_for_participant()
        log.info(f"Participant joined: {participant.identity}")
        
        model = _create_realtime_model()
        voice_agent = _create_voice_agent(model)
        
        session = voice.AgentSession()
        await session.start(voice_agent, room=job_ctx.room)
        
        await _maintain_session(job_ctx.room)
        
        log.info("Session ended")
        
    except Exception as e:
        log.error(f"Session error: {e}", exc_info=True)
        raise


def start_worker():
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=handle_session,
            api_key=AppConfig.LIVEKIT_API_KEY,
            api_secret=AppConfig.LIVEKIT_API_SECRET,
            ws_url=AppConfig.LIVEKIT_URL,
        )
    )


if __name__ == "__main__":
    try:
        start_worker()
    except KeyboardInterrupt:
        log.info("Shutting down...")
    except Exception as e:
        log.error(f"Fatal error: {e}", exc_info=True)
