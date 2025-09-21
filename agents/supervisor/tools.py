import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import httpx 
from langchain_core.tools import tool
from a2a.types import  SendMessageResponse, SendMessageRequest, Message, Part, TextPart, Role, MessageSendParams
from config.config import SERVICE_CATALOG_AGENT_URL, CISCO_INTERSIGHT_AGENT_URL
import logging


@tool
async def call_cisco_agent(message: str) -> str:
    """
    Calls the Cisco Intersight agent with the provided message and returns the response.
    """
    logging.info(f"Calling Cisco Intersight Agent with message: {message}")
    try:
        request_data = SendMessageRequest(
            id="cisco_intersight_tool_call",
            params=MessageSendParams(
                message=Message(
                    message_id="user_message_1",
                    role=Role.user,
                    parts=[Part(TextPart(text=message))]
                )
            )
        )
  
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CISCO_INTERSIGHT_AGENT_URL}/v1/messages",
                json=request_data.model_dump(),
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            response_data = response.json()
            
            logging.info(f"Response from Cisco Intersight Agent: {response_data}")
            
            if "message" in response_data and "parts" in response_data["message"]:
                return response_data["message"]["parts"][0].get("text", "")
            else: 
                return "Cisco Intersight Agent did not return a valid response."
    except Exception as e:
        logging.error(f"Error creating request data: {e}")
        return ""




# service _catalog_tool_description  

@tool
async def call_service_catalog_agent(message: str) -> str:
    """
    Calls the Service Catalog agent with the provided message and returns the response.
    """
    logging.info(f"Calling Service Catalog Agent with message: {message}")
    try:
        request_data = SendMessageRequest(
            id="service_catalog_tool_call",
            params=MessageSendParams(
                message=Message(
                    message_id="user_message_1",
                    role=Role.user,
                    parts=[Part(TextPart(text=message))]
                )
            )
        )
  
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICE_CATALOG_AGENT_URL}/v1/messages",
                json=request_data.model_dump(),
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            response_data = response.json()
            
            logging.info(f"Response from Service Catalog Agent: {response_data}")

            if "message" in response_data and "parts" in response_data["message"]:
                return response_data["message"]["parts"][0].get("text", "")
            else: 
                return "Service Catalog Agent did not return a valid response."
    except Exception as e:
        logging.error(f"Error creating request data: {e}")
        return ""
