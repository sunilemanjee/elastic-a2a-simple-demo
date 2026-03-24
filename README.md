# Elastic A2A Simple Demo

A collection of tools for interacting with Elastic Agent Builder agents via the [A2A (Agent-to-Agent)](https://google.github.io/A2A/) protocol.

## Prerequisites

- Python 3.10+ (tested with 3.13)
- Access to a Kibana instance with Agent Builder enabled

## Setup

1. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # macOS / Linux
   # .venv\Scripts\activate          # Windows
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create an API key:**

   In your Kibana instance, go to **Dev Tools** and run:

   ```json
   POST /_security/api_key
   {
     "name": "agent_builder",
     "role_descriptors": {
       "mcp-access": {
         "cluster": ["all"],
         "indices": [
           {
             "names": ["*"],
             "privileges": ["read", "view_index_metadata"]
           }
         ],
         "applications": [
           {
             "application": "kibana-.kibana",
             "privileges": [
               "read_onechat",
               "space_read",
               "feature_agentBuilder.all",
               "feature_actions.read"
             ],
             "resources": ["space:default"]
           }
         ]
       }
     }
   }
   ```

   Copy the `encoded` value from the response — this is your API key.

4. **Configure environment variables:**

   ```bash
   cp variables.env.template variables.env
   ```

   Edit `variables.env` and fill in your values:

   ```
   KIBANA_URL=https://your-deployment.kb.us-east-1.aws.elastic.cloud
   API_KEY=<encoded value from step 3>
   UI_PORT=8089
   ```

## Quick Start

After completing the setup above, run both apps with a single command:

```bash
./start.sh
```

This installs dependencies, runs the connectivity test, and starts the chat UI in the background. All output is logged to `start.log`.

## Apps

| App | Description |
|-----|-------------|
| [A2A Connectivity Test](docs/connectivity-test.md) | CLI script to verify A2A connectivity to an agent |
| [A2A Chat UI](docs/chat-ui.md) | Web-based chat interface for interacting with an agent |
