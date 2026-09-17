# API reference

All protected endpoints require:

```text
Authorization: Bearer <JWT>
```

The API returns the common shape `{ "success": true, "data": ... }` for
successful requests and `{ "success": false, "message": ... }` for errors.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/login` | Authenticate and receive a JWT |
| GET | `/api/datasets` | List datasets |
| POST | `/api/datasets` | Upload a CSV dataset |
| GET | `/api/datasets/:id/versions` | List dataset versions |
| GET | `/api/datasets/versions/:id/preview` | Preview rows |
| POST | `/api/datasets/versions/:id/validate` | Re-run quality validation |
| POST | `/api/analysis/versions/:id/compute` | Build traffic features |
| GET | `/api/analysis/versions/:id/kpis` | Retrieve traffic KPIs |
| GET | `/api/analysis/versions/:id/trend` | Retrieve trend data |
| GET | `/api/analysis/versions/:id/heatmap` | Retrieve heatmap data |
| POST | `/api/experiments` | Create an ARIMA/Prophet experiment |
| POST | `/api/experiments/:id/run` | Run a forecast |
| GET | `/api/experiments/:id/results` | Retrieve persisted future forecast rows |
| GET | `/api/experiments/compare?ids=1,2` | Compare experiment metadata and metrics |
| POST | `/api/reports/traffic/:version_id` | Generate a traffic report |
| POST | `/api/reports/forecast/:experiment_id` | Generate a forecast report |
| GET | `/api/reports/download/:id` | Authenticated report download |
| GET | `/api/health` | Database-backed health check |

For forecasting, run Traffic Analysis first. For short files, use an
aggregation interval of one minute so each segment has enough points for the
holdout window.
