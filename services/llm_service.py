import os
import json
import base64
from enum import Enum
from typing import List, Dict
from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

class ClientType(Enum):
    AZURE = "azure"
    GOOGLE = "google"

class OpenAIService:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_KEY")
        self.openai_azure_endpoint = os.getenv("OPENAI_AZURE_ENDPOINT")
        self.azure_deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")
        self.openai_api_version = os.getenv("OPENAI_API_VERSION")
        
        self.azure_client = self._initialize_azure_client()
        #self.google_client = self._initialize_google_client()
        print("LLM clients initialized")

    def _initialize_azure_client(self):
        return AzureOpenAI(
            api_key=self.openai_key,
            api_version=self.openai_api_version,
            azure_endpoint=self.openai_azure_endpoint
        )

    def _initialize_google_client(self):
        return OpenAI(
            api_key=self.gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    def _get_client(
            self, 
            client_type
        ):
        if client_type == ClientType.AZURE:
            return self.azure_client, self.azure_deployment_name
        return self.google_client, self.google_deployment_name

    def call_openai(
            self, 
            system_prompt, 
            user_prompt, 
            temperature: float | None = 0.4,
            client_type = ClientType.AZURE
        ):
        try:
            client,deployment_name = self._get_client(client_type)
            completion = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature
            )
            return completion
        except Exception as ex:
            print(f"Error in call_openai: {ex}")
            raise

    def call_chat_openai(
            self, 
            messages, 
            entity_model=[], 
            client_type = ClientType.AZURE
        ):
        try:
            client,deployment_name = self._get_client(client_type)
            completion = client.chat.completions.create(
                model=deployment_name,
                messages=messages
            )
            #usage = completion["usage"].to_dict()
            return completion.choices[0].message.content
        except Exception as ex:
            print(f"Error in call_chat_openai: {ex}")
            raise

    def call_openai_toolcall(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        entity_model: Dict, 
        max_retries: int = 3, 
        attempt: int = 1,
        client_type: ClientType = ClientType.AZURE
    ):
        try:
            client,deployment_name = self._get_client(client_type)
            completion = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                tools=[entity_model],
                tool_choice={"type": "function", "function": {"name": entity_model['function']['name']}}
            )
            tool_call = completion.choices[0].message.tool_calls[0]
            return json.loads(tool_call.function.arguments)
        except Exception as ex:
            print(ex)
            error_json = json.loads(ex)
            if "The response was filtered due to the prompt triggering Azure OpenAI's content management policy" in error_json.message:
                if entity_model['function']['name'] == "identify_intent":
                    return {"intent":"misbehaviour", "dont_know_answer":True}
            print(f"Error in call_openai_toolcall: {ex}")
            if attempt < max_retries:
                print(f"Retrying call_openai_toolcall... Attempt {attempt + 1}/{max_retries}")
                return self.call_openai_toolcall(system_prompt, user_prompt, entity_model, max_retries, attempt + 1, client_type)
            print("Max retries exceeded in call_openai_toolcall")
            return []

    def call_cot_jsontool_chain(
        self, 
        system_prompt_cot, 
        user_prompt_cot, 
        system_prompt_json, 
        entity_model,
        client_type = ClientType.AZURE
    ):
        try:
            cot_out = self.call_openai(system_prompt_cot, user_prompt_cot, client_type)
            cot_out_parsed = cot_out.choices[0].message.content
            print(f"COT complete\n{cot_out_parsed}")
            json_out = self.call_openai_toolcall(system_prompt_json, cot_out_parsed, entity_model, client_type=client_type)
            return cot_out_parsed, json_out
        except Exception as ex:
            print(f"Error in call_cot_jsontool_chain: {ex}")
            raise

    def call_audio_response(self, messages, entity_model, client_type = ClientType.AZURE):
        try:
            client,deployment_name = self._get_client(client_type)
            completion = client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                modalities=["text", "audio"],
                audio={"voice": "echo", "format": "wav"}
            )
            completion_json = json.loads(completion.to_json())
            audio_raw_data = completion_json['choices'][0]['message']['audio']['data']
            audio_transcript = completion_json['choices'][0]['message']['audio']['transcript']

            wav_bytes = base64.b64decode(audio_raw_data)
            with open("test.wav", "wb") as f:
                f.write(wav_bytes)
            return str(wav_bytes),audio_transcript
        except Exception as ex:
            print(f"Error in call_chat_openai: {ex}")
            raise
