# FastAPI Backend

minimal fastapi backend for hackathon ai endpoints.

## setup

1. create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # on windows: venv\Scripts\activate
```

2. install dependencies:
```bash
pip install -r requirements.txt
```

3. create `.env` file:
```bash
touch .env
```

4. add your google cloud configuration to `.env`:
```
GOOGLE_CLOUD_PROJECT_ID=ferrous-plating-477602-p2
GOOGLE_CLOUD_REGION=us-central1
```

5. set up google cloud authentication (choose one method):

   **method 1: install gcloud cli and use application default credentials:**
   ```bash
   # install gcloud cli (macos)
   brew install google-cloud-sdk
   
   # authenticate
   gcloud auth application-default login
   ```

   **method 2: service account key file (no gcloud cli needed):**
   - go to [google cloud console](https://console.cloud.google.com/)
   - navigate to iam & admin > service accounts
   - create or select a service account
   - create a json key and download it
   - save it somewhere safe (e.g., `backend/gcp-key.json`)
   - add to `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
   ```
   - **important**: add `gcp-key.json` to `.gitignore` to avoid committing secrets

6. (optional) add other api keys to `.env`:
```
AI_API_KEY=your_api_key_here
```

## running

```bash
uvicorn main:app --reload
```

api will be available at `http://localhost:8000`

## endpoints

- `GET /` - health check
- `GET /health` - health check
- `POST /api/ai/generate` - example ai endpoint
- `POST /api/agent/chat` - chat with multi-agent system

## multi-agent system

the system consists of three agents:

1. **root_agent** - main routing agent that receives prompts/files and delegates to specialized agents
2. **customer_info_agent** - specialized agent for extracting and entering customer information
3. **finances_agent** - specialized agent for extracting and entering financial data

### agent structure

- `agent_logic/agent.py` - defines all agents (root, customer_info, finances)
- `agent_logic/tools.py` - defines tools for data extraction and entry
- `main.py` - fastapi server with runner and session service

### how it works

1. user sends a prompt (and optionally file content) to `/api/agent/chat`
2. root agent analyzes the prompt/files to determine the category
3. root agent delegates to the appropriate specialized agent:
   - customer info → customer_info_agent
   - financial data → finances_agent
4. specialized agent extracts data and enters it using tools
5. response is returned with session_id for maintaining conversation state

## using the agent

### basic usage

```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add customer John Doe, email: john@example.com, phone: 555-1234"
  }'
```

### with file content

```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Process this invoice",
    "file_content": "Invoice #12345\nAmount: $500.00\nDate: 2024-01-15\nCustomer: ABC Corp"
  }'
```

### with session management

```bash
# first request - creates new session
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add customer info"}'

# response includes session_id, use it for subsequent requests
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What customer data did we enter?",
    "session_id": "your_session_id_here"
  }'
```

### example requests

**customer info:**
```json
{
  "message": "Enter customer: Jane Smith, jane@company.com, 555-9876, 123 Main St, Tech Corp"
}
```

**financial data:**
```json
{
  "message": "Record payment: $1,500.00 USD, income, 2024-01-20, salary payment, account 12345"
}
```

**mixed content (root agent will determine):**
```json
{
  "message": "Process this document",
  "file_content": "Customer: Bob Johnson\nEmail: bob@email.com\nTransaction: $250 payment on 2024-01-18"
}
```

or test it in the swagger ui at `http://localhost:8000/docs`

## documentation

swagger ui: `http://localhost:8000/docs`
redoc: `http://localhost:8000/redoc`


