# AGENTS.md — Codex Instructions

You are working on the AI Finance Assistant. Read the project documents before implementing features.

## Main rules
1. Follow `docs/01_PRD.md` for scope.
2. Follow `docs/02_TECHNICAL_OVERVIEW.md` for the stack and folder structure.
3. Follow `docs/03_DATABASE.md` and `docs/04_API_SPEC.md` for data and API design.
4. Follow `docs/05_UI_SPEC.md` for the visual design.
5. Follow `docs/06_ML_FEATURES.md` for ML behavior.
6. Build one feature at a time. Do not generate the whole application in one huge change.
7. Inspect existing files before editing. Do not overwrite working code unnecessarily.
8. Keep frontend in `client/` and backend in `server/`.
9. Never hardcode secrets or commit `.env`.
10. Never store plain-text passwords.
11. Every database query for personal data must be scoped to the logged-in user's ID.
12. Do not trust a `user_id` sent by the frontend.
13. Keep ML training code separate from Flask route handlers.
14. Financial calculations must be performed or verified by the backend.
15. Add or update tests when implementing each feature.
16. Do not claim something works unless you ran the relevant test or build.
17. Do not add deployment, bank integrations, payment processing, upcoming payments, or savings goals unless asked.

## For each task
- First inspect the relevant files.
- Implement only the requested milestone.
- Run relevant tests or build checks.
- Summarize files changed, tests run, and any remaining issue.
