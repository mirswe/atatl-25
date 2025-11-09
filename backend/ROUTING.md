# backend routing documentation

## overview

all backend routes are configured and ready for frontend integration. cors is properly set up for localhost:3000.

## base url

- development: `http://localhost:8000`
- production: set via `NEXT_PUBLIC_BACKEND_URL` environment variable

## routes

### health check endpoints

- `GET /` - root health check
  - response: `{ status: "ok", message: "Hackathon API is running" }`

- `GET /health` - health check
  - response: `{ status: "ok", message: "API is healthy" }`

### ai endpoints

- `POST /api/ai/generate` - example ai generation endpoint
  - request: `{ prompt: string, max_tokens?: number }`
  - response: `{ response: string, tokens_used?: number }`

### agent endpoints

- `POST /api/agent/chat` - chat with multi-agent system (root agent routes to specialized agents)
  - request: `{ message: string, user_id?: string, session_id?: string, file_content?: string }`
  - response: `{ response: string, session_id?: string }`

- `POST /api/agent/customer` - chat directly with customer info agent
  - request: `{ message: string, user_id?: string, session_id?: string, file_content?: string }`
  - response: `{ response: string, session_id?: string }`

- `POST /api/agent/finance` - chat directly with finance agent
  - request: `{ message: string, user_id?: string, session_id?: string, file_content?: string }`
  - response: `{ response: string, session_id?: string }`

- `GET /api/agent/session/{session_id}` - get session state
  - query params: `?user_id=string` (optional)
  - response: `{ session_id: string, customer_info?: any[], financial_data?: any[], uploaded_files?: any[], full_state?: dict }`

### storage endpoints

- `GET /api/storage` - view all stored data
  - response: `{ status: string, customer_info_count: number, financial_data_count: number, uploaded_files_count: number, customer_info: any[], financial_data: any[], uploaded_files: any[] }`

- `DELETE /api/storage` - clear all stored data
  - response: `{ status: string, message: string }`

## cors configuration

cors is configured to allow:
- origins: `http://localhost:3000`, `http://127.0.0.1:3000`
- methods: all (`*`)
- headers: all (`*`)
- credentials: enabled

## frontend integration

the frontend api client is available at `aiatl-25/lib/api.ts` with the following exports:

```typescript
import api from '@/lib/api';

// health checks
await api.healthCheck.root();
await api.healthCheck.health();

// ai
await api.ai.generate({ prompt: "hello", max_tokens: 100 });

// agents
await api.agent.chat({ message: "add customer info" });
await api.agent.customer({ message: "customer data" });
await api.agent.finance({ message: "financial data" });
await api.agent.getSession(sessionId, userId);

// storage
await api.storage.view();
await api.storage.clear();
```

## environment variables

frontend needs:
- `NEXT_PUBLIC_BACKEND_URL` (optional, defaults to `http://localhost:8000`)

backend needs:
- `GOOGLE_CLOUD_PROJECT_ID`
- `GOOGLE_CLOUD_REGION`
- `GOOGLE_APPLICATION_CREDENTIALS` (or use gcloud auth)
- `GEMINI_API_KEY` (for file extraction)
- `AI_API_KEY` (optional, for example endpoint)

## verification checklist

- [x] all routes defined in backend
- [x] cors configured for frontend
- [x] frontend api client created
- [x] typescript types added
- [x] error handling in api client
- [x] session management supported
- [x] file upload support in agent endpoints

