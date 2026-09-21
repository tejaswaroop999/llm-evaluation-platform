# Architecture

```text
Dataset
   |
   v
Evaluation Runner
   |
   v
Model Provider Adapter
   |
   v
Model Response
   |
   v
Evaluators
   |
   v
Metrics + Failure Classification
   |
   v
Persistence
   |
   +--> FastAPI
   |
   +--> Next.js Dashboard
```

The project should evolve incrementally. Avoid adding infrastructure until the current milestone requires it.
