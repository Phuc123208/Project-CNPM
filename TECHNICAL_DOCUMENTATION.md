# Technical documentation

## Architecture

The backend is a Flask REST API organized into API controllers, application
services, repositories, domain models, and SQLAlchemy infrastructure. The
frontend is a Vite React single-page application. React Router provides
protected role-based routes and Recharts renders analysis and forecast charts.

## Data flow

1. `DatasetService` stores the uploaded CSV and creates a dataset version.
2. `ValidationService` checks schema, missing values, duplicates, timestamps,
   coordinates, and speed.
3. `AnalysisService` aggregates trajectories by segment and time bucket and
   persists traffic features.
4. `ForecastingService` trains ARIMA or Prophet, evaluates the holdout window,
   and produces future forecasts with intervals.
5. `ExperimentService` stores experiment configuration, metrics, forecast rows,
   and the test-series metadata required to restore the chart after reload.
6. `ReportService` exports traffic and forecast reports as PDF or Excel.

## Reproducibility

Each experiment stores the dataset version, model type, parameters, evaluation
metrics, random seed, and test-series metadata. The selected aggregation
interval is recorded in the traffic-analysis audit entry and should be included
in experiment names for clear comparison.

## Database safety

Application startup does not create tables or seed data by default. Set
`DB_INIT_ON_STARTUP=true` to create the schema and separately set
`DB_SEED_ON_INIT=true` to add demo users. `/api/health` executes `SELECT 1` and
returns HTTP 503 when the database is unavailable.

## Main API groups

* `/api/auth`: registration, login, profile, and password changes.
* `/api/datasets`: upload, versions, preview, validation, archive, restore.
* `/api/analysis`: feature computation and KPI/trend/heatmap endpoints.
* `/api/experiments`: experiment CRUD, forecast execution, comparison/results.
* `/api/reports`: PDF/Excel generation, listing, and authenticated downloads.
* `/api/audit`: administrator-only audit trail.
* `/api/dashboard/summary`: dashboard counters.
