# Vrixo frontend

Next.js + Tailwind + shadcn/ui client for the Vrixo API. See the repository
README for how to run it alongside the backend.

- `src/lib/api.ts` — API client (JWT in localStorage, typed responses, error messages)
- `src/lib/use-image.ts` — authenticated images as cached object URLs
- `src/components/workspace.tsx` — the main screen: polling, upload, running a tool
- `src/components/light-table.tsx` — drop zone and before / after comparison
- `src/components/film-strip.tsx` — job history as frames of film
- `src/components/tool-tray.tsx` — the five tools and their options
