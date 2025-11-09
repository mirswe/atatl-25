<!-- # Hackathon Frontend -->

next.js 14+ frontend with typescript, tailwind css, and supabase integration.

## quick start

1. install dependencies:
```bash
npm install
```

2. create `.env` file in this directory:
```bash
# Copy and fill in your values
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend API URL (defaults to http://localhost:8000 if not set)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. run development server:
```bash
npm run dev
```

open [http://localhost:3000](http://localhost:3000) to see the app.

## project structure

- `/components` - reusable react components
- `/lib` - utilities and helpers (supabase client, utils)
- `/pages` - next.js pages and api routes
- `/types` - typescript type definitions
- `/styles` - global styles and tailwind config

## features

- next.js 16 with pages router
- typescript
- tailwind css v4
- framer motion for animations
- shadcn/ui dependencies ready
- supabase client setup
- responsive navigation component
- example page with server-side data fetching
- backend api integration (customer management, agent chat)
- file upload support for agent processing

## development

- `npm run dev` - start development server
- `npm run build` - build for production
- `npm run start` - start production server

## see main readme

for full project setup including backend, see the root `README.md`.
