<<<<<<< HEAD
# AI Finance Assistant

A personal finance application built with React, Flask, MongoDB, and beginner-friendly machine learning.

## Requirements
- Node.js and npm
- Python
- MongoDB Atlas account
- VS Code and Codex

## Project folders
- `client/` — React frontend
- `server/` — Flask backend and ML code
- `docs/` — project documentation

## Frontend setup
```bash
cd client
npm install
npm run dev
```

## Backend setup
```bash
cd server
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install backend packages after `requirements.txt` is created:
```bash
pip install -r requirements.txt
```

Run the Flask app using the run command implemented in `server/run.py`.

## MongoDB setup check

After putting your MongoDB Atlas URI in `server/.env`, verify the connection,
required indexes, and a temporary insert/read/delete check:

```powershell
cd server
.venv\Scripts\Activate.ps1
flask --app run:app verify-database
```

The temporary verification document is removed automatically.

## Environment variables
Create `server/.env` using `server/.env.example`. It should contain:
```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB_NAME=ai_finance_assistant
JWT_SECRET_KEY=your_long_random_secret
CORS_ORIGINS=http://localhost:5173
```

Create `client/.env`:
```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

Never commit `.env` files.

## Development
Follow `AGENTS.md` and build features in the order in `docs/08_DEVELOPMENT_STEPS.md`.

## Scope
This is an educational project. It does not connect to banks, transfer money, or provide professional financial advice.
=======
# AI-Finance-Assistant
An AI-powered personal finance management application
>>>>>>> c505ddf639786d86c5a884d4907576d8aae34488
