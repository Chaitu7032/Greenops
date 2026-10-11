# Production Deployment Architecture

GreenOps is engineered for low-cost, scalable deployment on modern cloud platforms.

```
                  ┌──────────────────────┐
                  │      GitHub PR       │
                  └──────────┬───────────┘
                             │ Webhook POST
                             ▼
┌────────────────────────────────────────────────────────┐
│                   Render / Railway                     │
│  FastAPI Ingestion Gateway & Async Service             │
│  • Listening on 0.0.0.0:${PORT}                        │
│  • HMAC Verification & Policy Gatekeeper               │
└────────────────┬───────────────────────┬───────────────┘
                 │                       │
                 │ Queries & Updates     │ Redis Broker / Cache
                 ▼                       ▼
   ┌────────────────────────┐  ┌─────────────────────────┐
   │    Supabase Cloud      │  │     Upstash Redis       │
   │  PostgreSQL Database   │  │  Carbon Intensity Cache │
   │  • Alembic Migrations  │  │  Celery Task Queue      │
   └────────────────────────┘  └─────────────┬───────────┘
                                             │
                                             ▼
                               ┌─────────────────────────┐
                               │  Celery Worker Process  │
                               │  • Low-Carbon Window    │
                               │  • Workflow Dispatch    │
                               └─────────────────────────┘
                                             ▲
                                             │ REST API
┌────────────────────────────────────────────┴───────────┐
│                      Vercel                            │
│  Next.js 14 SPM & FinOps Command Center Dashboard      │
└────────────────────────────────────────────────────────┘
```

## Production Environment Variables

### Backend (Render / Railway)
- `DATABASE_URL`: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`
- `GITHUB_WEBHOOK_SECRET`: Secure 32+ character random string
- `GITHUB_TOKEN`: GitHub Personal Access Token (or GitHub App private key) with `repo` and `workflow` scopes
- `ELECTRICITY_MAPS_API_KEY`: API token from electricitymaps.com
- `REDIS_URL`: `rediss://default:[PASSWORD]@[HOST]:6379`
- `CELERY_BROKER_URL`: Same as `REDIS_URL`
- `CELERY_RESULT_BACKEND`: Same as `REDIS_URL`
- `ENVIRONMENT`: `production`
- `LOG_LEVEL`: `INFO`

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL`: `https://your-backend.onrender.com`
