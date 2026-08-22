"""
Sales forecasting scripts.
Aggregates monthly sales, trains baseline LinearRegression and RandomForest, evaluates, and saves best model.
"""
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
import joblib

PROJ_ROOT = os.path.dirname(os.path.dirname(__file__))
CLEAN_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'cleaned_sales_data.csv')
MONTHLY_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'monthly_sales.csv')
OUT_DIR = os.path.join(PROJ_ROOT, 'outputs')
MODELS_DIR = os.path.join(PROJ_ROOT, 'models')


def prepare_monthly(df):
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    monthly = df.set_index('Order_Date').resample('ME').agg({'Sales':'sum','Profit':'sum'})
    monthly = monthly.reset_index()
    monthly['Year'] = monthly['Order_Date'].dt.year
    monthly['Month'] = monthly['Order_Date'].dt.month
    monthly['t'] = np.arange(len(monthly))
    # lag features
    monthly['lag_1'] = monthly['Sales'].shift(1)
    monthly['lag_2'] = monthly['Sales'].shift(2)
    monthly = monthly.dropna()
    return monthly


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    if not os.path.exists(MONTHLY_PATH):
        df = pd.read_csv(CLEAN_PATH, parse_dates=['Order_Date','Ship_Date'])
        monthly = prepare_monthly(df)
        monthly.to_csv(MONTHLY_PATH, index=False)
    else:
        monthly = pd.read_csv(MONTHLY_PATH, parse_dates=['Order_Date'])
        # If expected features are missing, regenerate from cleaned data
        expected = set(['t','lag_1','lag_2','Sales'])
        if not expected.issubset(set(monthly.columns)):
            df = pd.read_csv(CLEAN_PATH, parse_dates=['Order_Date','Ship_Date'])
            monthly = prepare_monthly(df)
            monthly.to_csv(MONTHLY_PATH, index=False)

    # features and target
    features = ['t','lag_1','lag_2']
    X = monthly[features]
    y = monthly['Sales']

    # chronological split: last 12 months as test
    train = monthly.iloc[:-12]
    test = monthly.iloc[-12:]
    X_train, y_train = train[features], train['Sales']
    X_test, y_test = test[features], test['Sales']

    # Linear baseline
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    pred_lr = lr.predict(X_test)

    # Random Forest
    rf = RandomForestRegressor(n_estimators=200, random_state=42)
    rf.fit(X_train, y_train)
    pred_rf = rf.predict(X_test)

    # Evaluate
    def eval(y_true, y_pred):
        return {
            'MAE': float(mean_absolute_error(y_true, y_pred)),
            'RMSE': float(np.sqrt(mean_squared_error(y_true, y_pred))),
            'R2': float(r2_score(y_true, y_pred))
        }

    metrics_lr = eval(y_test, pred_lr)
    metrics_rf = eval(y_test, pred_rf)

    results = pd.DataFrame([{'model':'LinearRegression', **metrics_lr},{'model':'RandomForest', **metrics_rf}])
    results_path = os.path.join(OUT_DIR, 'insights', 'forecast_metrics.csv')
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    results.to_csv(results_path, index=False)

    # Choose best model by RMSE
    best_model, best_pred = (lr, pred_lr) if metrics_lr['RMSE'] <= metrics_rf['RMSE'] else (rf, pred_rf)
    joblib.dump(best_model, os.path.join(MODELS_DIR, 'sales_forecasting_model.pkl'))

    # Save predictions
    preds = test.copy()
    preds['Predicted_Sales'] = best_pred
    preds.to_csv(os.path.join(OUT_DIR, 'predictions', 'monthly_sales_forecast.csv'), index=False)

    print(f'Saved forecast metrics to {results_path} and predictions to outputs/predictions/monthly_sales_forecast.csv')
