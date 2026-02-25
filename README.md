# Honu x Near Agent Spike

A specialized AI Agent that demonstrates the interoperability between Honu Agents and the NEAR Protocol. This agent provides a service (generating website hero images) and charges the user in NEAR tokens upon successful completion.

This project serves as a "spike" or proof-of-concept for:
- Connecting an external agent to the Honu platform.
- Using Google Gemini for multi-modal generation (Hero Images).
- Interacting with the NEAR blockchain via the NEAR MCP (Model Context Protocol) server to execute transactions.

## Features

- **Context-Aware Generation**: The agent reads the user's "Business Objects" (Business Plan, Brand Components, Website Content) to understand the visual requirements.
- **Image Generation**: Uses Google's Gemini models to generate high-quality hero images based on the business context.
- **Crypto Payments**: Integrates with the NEAR Protocol to charge a service fee (0.1 NEAR) for successful generations.

## Requirements

Before running the agent, ensure you have the following installed:

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**: Required to run the agent and its database.
- **[Ngrok](https://ngrok.com/)**: Required to expose your local agent to the internet so the Honu frontend can communicate with it.
- **Node.js & NPM**: Required to run the NEAR MCP server.
- **NEAR Account**: A NEAR Testnet account and its keystore (usually located in `~/.near-credentials`).
- **Google Cloud Platform (GCP) Account**:
  - A project with the Gemini API enabled.
  - A Storage Bucket for saving generated images.

## Configuration

1. **Environment Variables**:
   Rename `.env.example` to `.env` in the root directory and populate it:
   ```bash
   cp .env.example .env
   ```
   
   Fill in the required fields:
   - `GCP_PROJECT`: Your Google Cloud Project ID.
   - `GOOGLE_API_KEY`: API Key for Google Gemini.
   - `GENERATED_IMAGE_BUCKET_NAME`: The name of your GCP Storage Bucket.

   *Note: Database configuration is handled automatically via `docker-compose.yml`.*

2. **Ngrok Configuration**:
   If you haven't used Ngrok before, you will need to authenticate it.
   - Sign up or Log in at [dashboard.ngrok.com](https://dashboard.ngrok.com).
   - Copy your Authtoken from the dashboard.
   - Run the following command in your terminal:
     ```bash
     ngrok config add-authtoken <YOUR_TOKEN>
     ```

## Setup & Running

You will need to run three separate processes (e.g., in 3 terminal tabs).

### Tab 1: NEAR MCP Server
This server acts as a bridge between the AI Agent and the NEAR blockchain, managing wallet interactions.

**Extra details;**

Run `mkdir -p ~/.near-credentials/testnet`
Run `echo '{"account_id":"jsonic.testnet","public_key":"ed25519:Gp1MyShKbAY7fU6Hs1aAS4zNzhNSMP2XxKLctwwsVGXM","private_key":"ed25519:5k2pebopjGfnjvvG1BwHBvTqX4yrBBpdgtgZRBHmmjam6ZwaFTKW9S1LiKjrbdu8UHbRkkQdtC3UbMYtJtWYhmLo"}' > ~/.near-credentials/testnet/jsonic.testnet.json`
When running the Near MCP Server, the `/path/to/keystore` for you will be `~/.near-credentials`

```bash
# Run the NEAR MCP server on port 4000
npx @nearai/near-mcp@latest run --port 4000 --remote --key-dir ~/.near-credentials
```
*Make sure to point `--key-dir` to your actual NEAR credentials directory.*

### Tab 2: Agent Runtime (Docker)
This spins up the Agent service and its PostgreSQL database.

```bash
# Start the services
docker compose up
```

### Tab 3: Expose Agent (Ngrok)
The agent runs locally on port 7999. Use Ngrok to create a public tunnel.

```bash
ngrok http 7999
```

**After starting Ngrok:**
1. Copy the **forwarding URL** (e.g., `https://<random-id>.ngrok-free.app`) from the terminal output.
2. Go to the Honu Frontend: `https://hap.honutech.dev`.
3. Navigate to your Model.
4. Under **Engage**, click **Engage external agent**.
5. Fill in the details:
   - **Base URL**: Paste your Ngrok URL.
   - **App Name**: `near_agent`
6. Click **Confirm** and open the chat sidebar.

## Usage Workflow

1. **Introduction**: The agent will introduce itself and may ask for details if not automatically found.
2. **Context Gathering**: The agent uses the `get_business_objects` tool to read your Business Plan/Brand info.
3. **Generation**: It will propose Hero Images. You can ask for edits or request new variations.
4. **Payment**: Once you accept an image, the agent will initiate a transaction to charge 0.1 NEAR from your business wallet to the agent's wallet (`honu-agent.testnet`).

## Troubleshooting

- **Docker Connection Refused**: Ensure the database container is healthy. `docker compose logs database` can help debug issues.
- **Ngrok Issues**: If the frontend cannot reach the agent, check if the Ngrok tunnel is still active and the URL hasn't changed. FREE Ngrok sessions expire/rotate URLs on restart.
- **NEAR Transactions**: Ensure your testnet account has sufficient funds.
