# A2A Chat UI

A web-based chat interface for interacting with an Elastic Agent Builder agent via the A2A protocol.

> Complete the [setup steps](../README.md#setup) before running.

## Run

```bash
python app.py
```

Then open `http://localhost:<UI_PORT>` in your browser (default: `http://localhost:8089`).

The port is configured via `UI_PORT` in `variables.env`.

## Features

- Chat interface with message history
- Agent name and description displayed in the header
- Thinking indicator while waiting for a response
- Enter to send, Shift+Enter for newlines

## How it works

The Flask app acts as a thin proxy between the browser and the A2A agent:

1. On startup, it fetches and caches the agent card from the A2A discovery endpoint
2. When you send a message, the backend creates an A2A `Message`, sends it via the SDK's synchronous `message/send` method, and returns the response
3. The agent card is fetched once and reused for all subsequent messages

> **Note:** Streaming is not used — the A2A server does not currently support streaming operations. All interactions use the synchronous `message/send` method, which returns a complete response after task execution completes.
