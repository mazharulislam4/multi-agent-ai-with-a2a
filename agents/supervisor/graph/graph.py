import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from langgraph.graph import MessageGraph, MessagesState, StateGraph,END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from common.llm import get_llm
from langgraph.prebuilt import ToolNode
from ..tools import call_cisco_agent, call_service_catalog_agent

class SupervisorGraph:
    def __init__(self):
        self.llm = get_llm() or None
        self.tools = [call_cisco_agent, call_service_catalog_agent]
        self.graph = self._build_graph()
    
    # build a graph 
    def _build_graph(self) -> CompiledStateGraph:
        workflow = StateGraph(MessagesState)
        
        # routing to agent 1
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("tools",  ToolNode(self.tools))

        # set entry point 
        workflow.set_entry_point("supervisor")

        workflow.add_conditional_edges("supervisor", self.__should_continue, {
            "tools": "tools",
            "end": END
        })
        
        workflow.add_edge("tools", "supervisor")

        return workflow.compile()
    
    # supervisor greeting state
    def _supervisor_node(self, state: MessagesState) -> MessagesState:
        if not self.llm:
            self.llm = get_llm()
            # binding tools 
            self.llm.bind_tools(self.tools)
        
        user_message = state["messages"][-1].content if state["messages"] else ""

        system_message = SystemMessage(
            content="""You are a Supervisor Agent that coordinates between two agents:

Cisco Intersight : Specializes in greetings, welcomes, related to Cisco products and services
Service Catalog :  Specializes in greetings, welcomes, related to Service Catalog products and services

Based on the user's message, decide which agent to call:
- If the message seems like a greeting, starting a conversation, or saying hello → call call_cisco_agent
- If the message seems like saying goodbye, ending a conversation, or farewell → call call_service_catalog_agent

If you're unsure, default to Cisco Intersight.

Analyze this message and call the appropriate agent: {message}""".format(message=user_message)
        )
    
        messages  = [system_message] + state["messages"]
        response = self.llm.invoke(messages)
        return {"messages": [AIMessage(content=response.content)]}
    
    # should use a tool to route to the correct agent
    def __should_continue(self, state : MessagesState) -> str:
        last_message = state["messages"][-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "end"
        
    
    async def run(self, message: str) -> str:
        try:
            initial_state =  {
                "messages": [{"role": "user", "content": message}]
            }
            result = await self.graph.ainvoke(initial_state)
            
            return result["messages"][-1].content if result["messages"] else "No response from Supervisor Agent."
        except Exception as e:
            print(f"Error occurred: {e}")
            return "An error occurred while processing your request."