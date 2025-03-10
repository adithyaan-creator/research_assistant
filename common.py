import os
from services.llm_service import OpenAIService, ClientType


openai_instance = OpenAIService()
### Switch based on env
"""if os.getenv('LLM_TYPE') == "azure":
    llm_client_to_use = ClientType.AZURE
else:
    llm_client_to_use = ClientType.GOOGLE
audio_llm_client_to_use = ClientType.AZURE_AUDIO
    """
llm_client_to_use = ClientType.AZURE
print(f"Using LLM client :: {str(llm_client_to_use)}")
def get_google_llm():
    return openai_instance._get_client(ClientType.GOOGLE)
def get_azure_llm():
    return openai_instance._get_client(ClientType.AZURE)
def get_azure_audio_llm():
    return openai_instance._get_client(ClientType.AZURE)
