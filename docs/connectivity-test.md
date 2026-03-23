# A2A Connectivity Test

A CLI script that verifies A2A connectivity to an Elastic Agent Builder agent. It fetches the agent card and sends a single test message to confirm everything is working.

> Complete the [setup steps](../README.md#setup) before running.

## Run

```bash
python elastic-simple-a2a-connectivity-test.py
```

## What it does

1. Fetches the agent card from the A2A discovery endpoint
2. Prints agent metadata (name, description, skills)
3. Sends a test message ("What is your expertise?")
4. Prints the agent's response

## Example output

```
============================================================
A2A SDK Connectivity Test — potter-answers agent
============================================================

1. Fetching agent card from:
   https://your-deployment.kb.us-east-1.aws.elastic.cloud/api/agent_builder/a2a/potter-answers.json
   Agent Name: potter-answers
   Description: ...
   Skills: [...]

   Agent card retrieved successfully!

2. Sending test message to: ...
   Agent: ...

   Message sent successfully!

============================================================
Done.
```
