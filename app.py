"""Chat UI for the Elastic potter-answers A2A agent."""

import asyncio
import os
import sys
from uuid import uuid4

import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import AgentCard, Message, Part, TextPart
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv("variables.env")

KIBANA_URL = os.getenv("KIBANA_URL")
API_KEY = os.getenv("API_KEY")
UI_PORT = int(os.getenv("UI_PORT", "8089"))
AGENT_NAME = "potter-answers"
AGENT_CARD_URL = f"{KIBANA_URL}/api/agent_builder/a2a/{AGENT_NAME}.json"

if not KIBANA_URL or not API_KEY:
    sys.exit("Error: Set KIBANA_URL and API_KEY in variables.env")

app = Flask(__name__)

# Cache the agent card so we don't fetch it on every request
_agent_card: AgentCard | None = None


async def get_agent_card() -> AgentCard:
    """Fetch and cache the agent card."""
    global _agent_card
    if _agent_card is not None:
        return _agent_card

    headers = {"Authorization": f"ApiKey {API_KEY}"}
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        resp = await client.get(AGENT_CARD_URL)
        resp.raise_for_status()
        _agent_card = AgentCard(**resp.json())
    return _agent_card


async def send_message(text: str) -> str:
    """Send a message to the agent and return the response text."""
    agent_card = await get_agent_card()
    headers = {"Authorization": f"ApiKey {API_KEY}"}

    async with httpx.AsyncClient(headers=headers, timeout=120.0) as httpx_client:
        config = ClientConfig(httpx_client=httpx_client, streaming=False)
        factory = ClientFactory(config)
        client = factory.create(agent_card)

        message = Message(
            role="user",
            parts=[Part(root=TextPart(text=text))],
            messageId=uuid4().hex,
        )

        parts = []
        async for result in client.send_message(message):
            if isinstance(result, Message):
                for part in result.parts:
                    if hasattr(part.root, "text"):
                        parts.append(part.root.text)
            else:
                _task, event = result
                if event and hasattr(event, "artifact"):
                    for part in event.artifact.parts:
                        if hasattr(part.root, "text"):
                            parts.append(part.root.text)

    return "\n".join(parts) if parts else "(no response)"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/agent")
def agent_info():
    """Return cached agent card info."""
    try:
        card = asyncio.run(get_agent_card())
        return jsonify(name=card.name, description=card.description)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Send a user message and return the agent response."""
    data = request.get_json()
    user_text = data.get("message", "").strip()
    if not user_text:
        return jsonify(error="Empty message"), 400

    try:
        reply = asyncio.run(send_message(user_text))
        return jsonify(reply=reply)
    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    print(f"Fetching agent card from {AGENT_CARD_URL} ...")
    try:
        card = asyncio.run(get_agent_card())
        print(f"Connected to agent: {card.name}")
    except Exception as e:
        sys.exit(f"Failed to fetch agent card: {e}")

    print(f"Starting UI on http://localhost:{UI_PORT}")
    app.run(host="0.0.0.0", port=UI_PORT, debug=False)
