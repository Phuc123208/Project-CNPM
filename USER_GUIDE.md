# User guide

## Demo setup

1. Start the backend from `backend` with the dependencies in `requirements.txt`.
2. Start the frontend from `frontend` with `npm install` and `npm run dev`.
3. If the database schema is not initialized, run the explicit initialization command in the root README. Startup does not mutate Supabase by default.
4. Sign in with one of the demo accounts documented in the root README.

## Recommended UAV dataset workflow

1. Open **Datasets** and upload a CSV containing `vehicle_id`, `timestamp`,
   `segment_id`, `speed`, `lat`, and `lon`.
2. Open the dataset and review the validation report and preview.
3. Open **Traffic Analysis**, select the dataset version, choose an aggregation
   interval, and click **Compute features**. Use **1 minute** for the two short
   sample files because they contain only 13–16 minutes of observations.
4. Open **Forecasting**, create one ARIMA experiment and one Prophet experiment
   for the same dataset version.
5. Open each experiment, select a segment, set the test window and horizon, and
   run the forecast. The chart shows actual test values, test predictions,
   future forecasts, and confidence intervals.
6. Return to **Forecasting** and use **Compare experiments** to compare the
   completed model runs by MAE, RMSE, MAPE, and R².
7. Generate PDF or Excel reports from Analysis or an Experiment, then download
   them from **Reports**.

## Interpreting a short-data warning

Forecasting requires at least `test_size + 5` aggregated points per segment.
If the warning says there are not enough points, return to Traffic Analysis,
recompute features with a smaller interval, or use a longer dataset.
