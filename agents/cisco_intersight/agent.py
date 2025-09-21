import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from re import A
from .prompts import prompt
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from common.llm import get_llm

class CiscoIntersightAgent:
    def __init__(self):
        self.llm = get_llm() or None
        self.graph = self._build_graph()
    
    # build graph 
    def _build_graph(self) -> CompiledStateGraph:
        
        if not self.llm:
            self.llm = get_llm()
        
        workflow = StateGraph(MessagesState)
        
        workflow.add_node("greeting", self._greeting)
        workflow.add_edge("greeting", END)
        workflow.set_entry_point("greeting")
        return workflow.compile()
    

    # greeting state
    def _greeting(self, state: MessagesState) -> MessagesState:
        
        if not self.llm:
            self.llm = get_llm()

        user_message = state["messages"][-1].content if state["messages"] else ""

        chain = prompt | self.llm
        
        response = chain.invoke({"message": user_message})
        
        return {"messages": [AIMessage(content=response.content)]}
    
    async def run(self, message: str) -> str:
        
        try:
            initial_state = MessagesState(messages=[HumanMessage(content=message)])
            result = await self.graph.ainvoke(initial_state)
            return result["messages"][-1].content if result["messages"] else ""
        except Exception as e:
            print(f"Error occurred: {e}")
            return "An error occurred while processing your request."
