import asyncio
import logging
import re
from uvicorn import Config, Server
from a2a.server.apps import A2AFastAPIApplication
from  a2a.server.tasks import InMemoryTaskStore
from a2a.server.request_handlers import DefaultRequestHandler
from .agent_executor import CiscoIntersightAgentExecutor
from .card import AGENT_CARD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    
    logging.info("Starting Cisco Intersight Agent Server...")
    request_handler = DefaultRequestHandler(agent_executor=CiscoIntersightAgentExecutor(), task_store=InMemoryTaskStore()) # type: ignore
    app = A2AFastAPIApplication(agent_card=AGENT_CARD, http_handler=request_handler)  # pyright: ignore[reportCallIssue]
    
    config = Config(
        app = app,
        host = "0.0.0.0",
        port = 8002,
        log_level = "info",
    )
    
    uvicorn_server = Server(config)
    await uvicorn_server.serve()

if __name__ == "__main__":
    asyncio.run(main())