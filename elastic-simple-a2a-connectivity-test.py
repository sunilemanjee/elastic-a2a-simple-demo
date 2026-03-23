"""Simple A2A SDK connectivity test for the Elastic potter-answers agent."""

import asyncio
import os
from uuid import uuid4

import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import AgentCard, Message, Part, TextPart
from dotenv import load_dotenv

load_dotenv("variables.env")

KIBANA_URL = os.getenv("KIBANA_URL")
API_KEY = os.getenv("API_KEY")
AGENT_NAME = "potter-answers"
AGENT_CARD_URL = f"{KIBANA_URL}/api/agent_builder/a2a/{AGENT_NAME}.json"


async def main():
    print("=" * 60)
    print("A2A SDK Connectivity Test — potter-answers agent")
    print("=" * 60 + "\n")

    headers = {"Authorization": f"ApiKey {API_KEY}"}

    async with httpx.AsyncClient(headers=headers, timeout=120.0) as httpx_client:
        # 1. Fetch agent card directly (Elastic serves it at a custom URL)
        print(f"1. Fetching agent card from:\n   {AGENT_CARD_URL}")
        try:
            resp = await httpx_client.get(AGENT_CARD_URL)
            resp.raise_for_status()
            agent_card = AgentCard(**resp.json())
        except Exception as e:
            print(f"   Failed to fetch agent card: {e}")
            return

        print(f"   Agent Name: {agent_card.name}")
        print(f"   Description: {agent_card.description}")
        print(f"   URL: {agent_card.url}")
        if agent_card.skills:
            print(f"   Skills: {[s.name for s in agent_card.skills]}")
        print("\n   Agent card retrieved successfully!\n")

        # 2. Send a test message using ClientFactory
        print(f"2. Sending test message to: {agent_card.url}")
        config = ClientConfig(httpx_client=httpx_client, streaming=False)
        factory = ClientFactory(config)
        client = factory.create(agent_card)

        message = Message(
            role="user",
            parts=[Part(root=TextPart(text="What is your expertise?"))],
            messageId=uuid4().hex,
        )

        try:
            async for result in client.send_message(message):
                if isinstance(result, Message):
                    for part in result.parts:
                        print(f"   Agent: {part.root.text}")
                else:
                    task, event = result
                    if event and hasattr(event, "status"):
                        print(f"   Task status: {event.status.state.value}")
                    if event and hasattr(event, "artifact"):
                        for part in event.artifact.parts:
                            print(f"   Agent: {part.root.text}")
            print("\n   Message sent successfully!")
        except Exception as e:
            print(f"   Error sending message: {e}")

    print("\n" + "=" * 60)
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
