import os
from dotenv import load_dotenv
# loading .env file
load_dotenv()

# CONSTANTS 
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Transport Configuration
DEFAULT_MESSAGE_TRANSPORT = os.getenv("DEFAULT_MESSAGE_TRANSPORT", "nats")
TRANSPORT_SERVER = os.getenv("TRANSPORT_SERVER", "nats://localhost:4222")

# agent urls
SERVICE_CATALOG_AGENT_URL = os.getenv("SERVICE_CATALOG_AGENT_URL", "http://localhost:8001")
CISCO_INTERSIGHT_AGENT_URL = os.getenv("CISCO_INTERSIGHT_AGENT_URL", "http://localhost:8002")