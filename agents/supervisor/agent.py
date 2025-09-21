import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from urllib import response
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from .graph.graph import SupervisorGraph

class SupervisorAgent(AgentExecutor):
    def __init__(self):
        self.agent = SupervisorGraph()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_input = context.get_user_input()
        response = await self.agent.graph.ainvoke({"messages": [{"content": user_input}]})
        await event_queue.enqueue_event(response)  # type: ignore
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel the current execution"""
        # Add any cleanup logic here if needed
        pass
    