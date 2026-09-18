# AI Health Check

A conversational assistant that helps you make sense of symptoms in plain
language. It's grounded in curated symptom/disease datasets, runs its
language model locally via [Ollama](https://ollama.com), and keeps a record
of your conversation so you can pick up where you left off.

**This is a starting point for understanding what you're experiencing — not
a diagnosis, and not a replacement for a doctor's judgment.**

## Stack

- **Backend:** Flask, serving a JSON REST API (no server-rendered HTML)
- **Frontend:** React (Vite), talking to Flask over `fetch`
- **Database:** SQLite (`database/users.db`) — users, chat history, saved results
- **LLM:** [Ollama](https://ollama.com) running `llama3.2` locally, via `langchain-ollama`
- **Datasets:** symptom/disease/precaution CSVs in `utils/`, used to ground chatbot responses

## Project structure

```
AIHealthCheck/
├── app.py                     # Flask JSON API — auth, chat, results, serves the built frontend in prod
├── requirements.txt
├── database/
│   └── users.db                # created by utils/db_setup.py
├── utils/
│   ├── db_setup.py              # creates the SQLite schema
│   ├── chatbot.py                # loads datasets, builds prompts, calls Ollama
│   └── *.csv                      # symptom/disease/precaution datasets
└── frontend/                  # React app (Vite)
    ├── index.html
    ├── vite.config.js          # dev-mode proxy: /api -> Flask on :5000
    └── src/
        ├── main.jsx, App.jsx    # entry point, routes
        ├── api/client.js         # fetch wrapper for all /api calls
        ├── context/AuthContext.jsx
        ├── styles/                # design tokens + global styles
        ├── components/
        │   ├── layout/             # Navbar, Footer, PublicLayout, AppShell (sidebar)
        │   ├── auth/                # AuthForm, ProtectedRoute
        │   ├── chat/                # ChatWindow, MessageList, MessageBubble, MessageInput
        │   └── ui/                   # Button, Card, Alert, FormField
        └── pages/                  # Home, About, Login, Signup, Dashboard, Chatbot
```

## API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/auth/signup` | POST | Create an account, starts a session |
| `/api/auth/login` | POST | Log in |
| `/api/auth/logout` | POST | Log out |
| `/api/auth/me` | GET | Check current session |
| `/api/chat/history` | GET | Load past chat turns |
| `/api/chat/message` | POST | Send a message, get a reply |
| `/api/results` | GET / POST | Saved results (currently unused by the frontend — see Known gaps) |

## Running locally

**1. Backend**

```bash
pip install -r requirements.txt
python utils/db_setup.py    # creates database/users.db if it doesn't exist
python app.py                # runs on http://127.0.0.1:5000
```

Ollama needs to be running separately with the model pulled:
```bash
ollama pull llama3.2
```
(`ollama serve` usually runs automatically in the background once installed — if you see
`bind: address already in use` when trying to start it manually, it's already running.)

**2. Frontend (development)**

In a second terminal:
```bash
cd frontend
npm install       # only needed once, or after package.json changes
npm run dev        # runs on http://127.0.0.1:5173, proxies /api to Flask
```

Open **http://127.0.0.1:5173** while both are running.

**3. Production build (single server)**

```bash
cd frontend
npm run build       # outputs frontend/dist
cd ..
python app.py         # Flask now serves the built React app directly
```
Open **http://127.0.0.1:5000**.

## Known gaps / possible next steps

- `app.secret_key` in `app.py` is a hardcoded placeholder — move it to an
  environment variable before deploying anywhere public.
- No password reset flow.
- `/api/results` exists but nothing in the UI currently produces a "result" —
  it's there for a future feature (e.g. a structured symptom-checker form),
  not wired to anything yet.
- Flask's built-in dev server (`app.run(debug=True)`) isn't meant for
  production — use something like `gunicorn` or `waitress` in front of it
  for real deployment.
