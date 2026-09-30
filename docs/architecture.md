# Backend architecture and boundaries

The implemented path is dataset CRUD → run request → provider → evaluator → SQLite snapshot → run APIs. See the root README for the diagram and commands.

- `app/schemas/runs.py`: validated request and saved record contract.
- `app/services/providers/adapters.py`: echo and Anthropic generation boundary.
- `app/services/runner.py`: sequential execution, scoring, durations, and failure accounting.
- `app/db/runs.py`: parameterized SQLite writes and reads.
- `app/api/routes/runs.py`: API configuration, request bounds, and run retrieval.

Dataset CRUD remains in memory. Saved records carry dataset and prompt snapshots so a restart or edit does not destroy the context of earlier results. The provider key is read from the server environment and is not stored in run records.

The echo adapter deliberately returns its prompt unchanged. Its comparison is a pipeline demonstration, not a model benchmark. The Anthropic adapter uses mocked HTTP transport in tests. There is no claim of validated live-provider performance.

Future boundaries: durable datasets, prompt registry, background execution, semantic evaluators, authenticated access, and a Next.js dashboard.
