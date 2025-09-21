from langchain_openai import ChatOpenAI

from config.config import LLM_PROVIDER, OPENAI_API_KEY

def get_llm():
    if LLM_PROVIDER == "openai":
        return ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0 , model="gpt-3.5-turbo") # type: ignore
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")