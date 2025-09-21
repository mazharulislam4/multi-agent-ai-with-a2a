from uuid import uuid4
from a2a.server.agent_execution import AgentExecutor,RequestContext
from a2a.server.events import EventQueue
from a2a.types import Message, Role, Part, TextPart
from .agent import CiscoIntersightAgent
from .card import AGENT_CARD

import logging
logger = logging.getLogger(__name__)

class CiscoIntersightAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = CiscoIntersightAgent()
        self.agent_card = AGENT_CARD.model_dump(mode="json", exclude_none=True)

    async def execute(self, context : RequestContext, event_queue: EventQueue) -> None:
        logging.info("Cisco Intersight Agent Executor started.")
        prompt = context.get_user_input()
        logging.info(f"Prompt: {prompt}")
        
        try:
            result = await self.agent.run(prompt)
            logging.info(f"Result: {result}")
            message = Message(
                role=Role.agent,
                message_id=str(uuid4()),
                metadata={"name": self.agent_card["name"]},
                parts=[Part(TextPart(text=result))]
            )
            logging.info(f"Message: {message}")
            await event_queue.enqueue_event(message)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel the current execution"""
        logging.info("Cisco Intersight Agent execution cancelled.")
        # Add any cleanup logic here if needed