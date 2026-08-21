"""Module 3 - Forecasting.
Builds ARIMA / Prophet models on the traffic-density time series produced by
the Traffic Pattern Analysis module (Module 2) and evaluates them with
MAE, RMSE, MAPE and R^2 (per the research methodology, item 8).
"""
import numpy as np
import pandas as pd
from domain.exceptions import NotFoundException, ValidationException
from infrastructure.repositories.dataset_repository import DatasetRepository

try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except Exception:
    ARIMA_AVAILABLE = False

# Prophet (and the matplotlib/fontTools chain it pulls in) is imported lazily,
# only the first time a Prophet forecast is actually requested. Importing it
# eagerly at module load time can add tens of seconds (sometimes minutes on
# Windows, due to matplotlib's font-cache scan) to every server startup and
# every Flask debug-reloader restart, even for users who only ever use ARIMA.


def _try_import_prophet():
    try:
        from prophet import Prophet
        return Prophet
    except Exception:
        return None


_PROPHET_CLASS = None
_PROPHET_CHECKED = False


def _get_prophet_class():
    global _PROPHET_CLASS, _PROPHET_CHECKED
    if not _PROPHET_CHECKED:
        _PROPHET_CLASS = _try_import_prophet()
        _PROPHET_CHECKED = True
    return _PROPHET_CLASS


def prophet_available():
    return _get_prophet_class() is not None


def _evaluate(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    denom = np.where(y_true == 0, 1e-6, y_true)
    mape = float(np.mean(np.abs((y_true - y_pred) / denom)) * 100)
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2)) or 1e-6
    r2 = float(1 - ss_res / ss_tot)
    return {"MAE": round(mae, 4), "RMSE": round(rmse, 4), "MAPE": round(mape, 4), "R2": round(r2, 4)}


class ForecastingService:
    def __init__(self, repository: DatasetRepository = None):
        self.repository = repository or DatasetRepository()

    def _series_for_segment(self, version_id, segment_id):
        rows = self.repository.get_features(version_id, segment_id)
        if not rows:
            return pd.Series(dtype=float)
        df = pd.DataFrame([{"ts": r.timestamp_val, "y": r.traffic_density} for r in rows])
        df = df.sort_values("ts").drop_duplicates(subset="ts")
        s = pd.Series(df["y"].values, index=pd.DatetimeIndex(df["ts"]))
        return s

    def run_forecast(self, version_id, segment_id, model_type="arima",
                      horizon=4, test_size=4, params=None):
        """Train/test split forecast + evaluation for a single segment.
        horizon: number of future steps (short-term, e.g. 15-60 min ahead
        depending on the aggregation interval used in Module 2)."""
        params = params or {}
        series = self._series_for_segment(version_id, segment_id)
        if len(series) < (test_size + 5):
            raise ValidationException(
                "Not enough data points for this segment to train/evaluate a forecast "
                "(need at least test_size + 5 aggregated points). Run traffic analysis "
                "with a smaller interval or upload more data."
            )

        train = series.iloc[:-test_size]
        test = series.iloc[-test_size:]

        if model_type == "prophet" and prophet_available():
            metrics, test_pred, future_pred, future_index, bounds = self._run_prophet(
                train, test, series, horizon, params)
        else:
            if model_type == "prophet" and not prophet_available():
                model_type = "arima"  # graceful fallback
            metrics, test_pred, future_pred, future_index, bounds = self._run_arima(
                train, test, series, horizon, params)

        return {
            "model_type": model_type,
            "metrics": metrics,
            "test_actual": [float(v) for v in test.values],
            "test_predicted": [float(v) for v in test_pred],
            "test_index": [str(i) for i in test.index],
            "forecast": [
                {
                    "timestamp": str(ts),
                    "predicted_density": float(val),
                    "lower_bound": float(lo),
                    "upper_bound": float(hi),
                }
                for ts, val, (lo, hi) in zip(future_index, future_pred, bounds)
            ],
        }

    def _run_arima(self, train, test, full_series, horizon, params):
        order = tuple(params.get("order", (2, 1, 2)))
        try:
            model = ARIMA(train.values, order=order) if ARIMA_AVAILABLE else None
            if model is None:
                raise RuntimeError("statsmodels not available")
            fitted = model.fit()
            test_pred = fitted.forecast(steps=len(test))

            full_model = ARIMA(full_series.values, order=order).fit()
            forecast_res = full_model.get_forecast(steps=horizon)
            future_pred = forecast_res.predicted_mean
            conf_int = forecast_res.conf_int(alpha=0.2)
            bounds = list(zip(conf_int[:, 0], conf_int[:, 1]))
        except Exception:
            # Fallback: naive moving-average forecast if ARIMA fails to converge
            window = min(3, len(train))
            baseline = float(train.values[-window:].mean())
            test_pred = np.full(len(test), baseline)
            future_pred = np.full(horizon, baseline)
            spread = float(full_series.std() or 1.0)
            bounds = [(baseline - spread, baseline + spread)] * horizon

        metrics = _evaluate(test.values, test_pred)
        freq = pd.infer_freq(full_series.index) or "15min"
        future_index = pd.date_range(start=full_series.index[-1], periods=horizon + 1, freq=freq)[1:]
        return metrics, test_pred, future_pred, future_index, bounds

    def _run_prophet(self, train, test, full_series, horizon, params):
        Prophet = _get_prophet_class()
        df_train = pd.DataFrame({"ds": train.index, "y": train.values})
        m = Prophet(interval_width=0.8, daily_seasonality=True,
                    weekly_seasonality=False, yearly_seasonality=False)
        m.fit(df_train)

        future_test = pd.DataFrame({"ds": test.index})
        pred_test = m.predict(future_test)
        test_pred = pred_test["yhat"].values

        df_full = pd.DataFrame({"ds": full_series.index, "y": full_series.values})
        m_full = Prophet(interval_width=0.8, daily_seasonality=True,
                          weekly_seasonality=False, yearly_seasonality=False)
        m_full.fit(df_full)
        freq = pd.infer_freq(full_series.index) or "15min"
        future = m_full.make_future_dataframe(periods=horizon, freq=freq, include_history=False)
        fc = m_full.predict(future)
        future_pred = fc["yhat"].values
        bounds = list(zip(fc["yhat_lower"].values, fc["yhat_upper"].values))
        future_index = fc["ds"].values

        metrics = _evaluate(test.values, test_pred)
        return metrics, test_pred, future_pred, future_index, bounds

    def compare_models(self, version_id, segment_id, horizon=4, test_size=4):
        results = {}
        for m in (["arima", "prophet"] if prophet_available() else ["arima"]):
            try:
                results[m] = self.run_forecast(version_id, segment_id, model_type=m,
                                                horizon=horizon, test_size=test_size)
            except ValidationException:
                raise
            except Exception as e:
                results[m] = {"error": str(e)}
        return results
