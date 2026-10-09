from app.agents.prompts import SYSTEM_PROMPT
from app.tools.tool_definitions import TOOLS
from pydantic import BaseModel, Field
from settings import settings
from qdrant_client import QdrantClient, models
from logging_config import configure_logging, get_logger
from app.models.Invoice import Invoice
import requests
import json

def get_agent_decision(user_input: str):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": settings.OLLAMA_CHAT_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
           "tools": TOOLS,
            "stream": False,
            "options": {"temperature": 0},
        },
        timeout=settings.OLLAMA_TIMEOUT_SECONDS,
    )
    print("111111111111 ")

    if not response.ok:
        print("Ollama error:", response.text)
    #Find details about invoice INV-104.
    #Why does invoice INV-104 have a quantity mismatch?”
    response.raise_for_status()
    message =  response.json()["message"]
   # print("Tool calls:", message.get("tool_calls", []))
    return message


def main():
    print("Gemma chat started. Type 'exit' to stop.\n")
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("\n Thanks you....")
        return
    if not user_input:
        print("Please enter a request.")
        return
    print(f"Request received: {user_input}")
    response = get_agent_decision(user_input)
    #print(response)
    print(json.dumps(response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
