## quick start

### frontend setup

1. navigate to frontend directory:
```bash
cd atatl-25
```

2. install dependencies:
```bash
npm install
```

3. create `.env` file:
```bash
cp .env.example .env
```

4. add your supabase credentials to `.env`:
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

5. run development server:
```bash
npm run dev
```

frontend will be available at `http://localhost:3000`

### backend setup

1. navigate to backend directory:
```bash
cd backend
```

2. create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # on windows: venv\Scripts\activate
```

3. install dependencies:
```bash
pip install -r requirements.txt
```

4. create `.env` file:
```bash
cp .env.example .env
```

5. add your ai api keys to `.env`:
```
AI_API_KEY=your_api_key_here
```

6. run development server:
```bash
uvicorn main:app --reload
```

backend will be available at `http://localhost:8000`

## features

- **next.js 14+** with pages router
- **typescript** for type safety
- **tailwind css** for styling
- **shadcn/ui** components ready (dependencies installed)
- **framer motion** for animations
- **supabase** client setup
- **fastapi** backend with cors configured
- responsive navigation component
- example page with server-side data fetching

## tech stack

### frontend
- next.js 16
- react 19
- typescript
- tailwind css v4
- framer motion
- supabase js client

### backend
- fastapi
- uvicorn
- pydantic

## development

### frontend commands
- `npm run dev` - start development server
- `npm run build` - build for production
- `npm run start` - start production server

### backend commands
- `uvicorn main:app --reload` - start development server
- `uvicorn main:app` - start production server

## api documentation

when backend is running:
- swagger ui: `http://localhost:8000/docs`
- redoc: `http://localhost:8000/redoc`

## next steps

1. set up your supabase project and add credentials
2. create database tables as needed
3. integrate ai service in `backend/main.py`
4. customize components in `atatl-25/components/`
5. add more pages in `atatl-25/pages/`

## fastapi vs flask recommendation

**fastapi** was chosen for this hackathon setup because:

- **async support**: native async/await for better performance
- **automatic docs**: swagger ui and redoc out of the box
- **type safety**: pydantic models for request/response validation
- **modern**: built for modern python with type hints
- **fast**: one of the fastest python frameworks
- **easy setup**: minimal boilerplate, quick to get started

fastapi's automatic documentation and type validation help you move faster and catch errors early.


