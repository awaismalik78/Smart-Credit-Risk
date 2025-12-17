"""Training script to train classification, regression, PCA and clustering models."""
from pathlib import Path
import pandas as pd
import joblib
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import f1_score

from .evaluate import classification_metrics, regression_metrics, clustering_metrics

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'data' / 'processed'
MODELS_DIR = ROOT / 'models'
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def train_classification():
    path = OUT_DIR / 'for_classification.csv'
    if not path.exists():
        print('Processed classification data not found. Run ml.prepare_data')
        return None
    df = pd.read_csv(path)
    if 'loan_status' not in df.columns:
        print('No loan_status column found for classification')
        return None
    # drop rows with missing target
    df = df[df['loan_status'].notna()].copy()
    if df.shape[0] == 0:
        print('No valid rows with loan_status for classification')
        return None
    # normalize labels
    df['loan_status'] = df['loan_status'].astype(str).str.strip()
    y = df['loan_status']
    X = df.drop(columns=['loan_status'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Use RandomForest for better confidence scores
    rf = RandomForestClassifier(n_estimators=50, max_depth=15, n_jobs=-1, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    metrics_rf = classification_metrics(y_test, y_pred_rf)

    # Also try LogisticRegression for comparison
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
    metrics_lr = classification_metrics(y_test, y_pred)

    # Use RandomForest as it gives better confidence scores
    best = ('rf', rf, metrics_rf)
    joblib.dump(best[1], MODELS_DIR / 'classification_model.pkl')
    joblib.dump({'metrics_rf': metrics_rf, 'metrics_lr': metrics_lr}, OUT_DIR / 'classification_metrics.json')
    print('Saved classification model and metrics')
    return best


def train_regression():
    path = OUT_DIR / 'for_regression.csv'
    if not path.exists():
        print('Processed regression data not found. Run ml.prepare_data')
        return None
    df = pd.read_csv(path)
    target = None
    for t in ['loan_amount', 'interest_rate']:
        if t in df.columns:
            target = t
            break
    if not target:
        print('No regression target found')
        return None
    # drop rows with missing regression target
    df = df[df[target].notna()].copy()
    if df.shape[0] == 0:
        print('No valid rows with regression target')
        return None
    y = df[target]
    X = df.drop(columns=[target])
    # keep numeric features only for regression (simple approach)
    X = X.select_dtypes(include=[np.number]).copy()
    if X.shape[1] == 0:
        print('No numeric features available for regression after preprocessing')
        return None
    X = X.fillna(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
    metrics_lr = regression_metrics(y_test, y_pred)

    # Faster RandomForest with fewer estimators and parallel jobs
    rf = RandomForestRegressor(n_estimators=20, max_depth=10, n_jobs=-1, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    metrics_rf = regression_metrics(y_test, y_pred_rf)

    best = ('lr', lr, metrics_lr) if metrics_lr['rmse'] <= metrics_rf['rmse'] else ('rf', rf, metrics_rf)
    joblib.dump(best[1], MODELS_DIR / 'regression_model.pkl')
    joblib.dump({'metrics_lr': metrics_lr, 'metrics_rf': metrics_rf}, OUT_DIR / 'regression_metrics.json')
    print('Saved regression model and metrics')
    return best


def train_pca_and_clustering(n_components=50, n_clusters=5):
    path = OUT_DIR / 'for_classification.csv'
    if not path.exists():
        print('Processed data not found for PCA/Clustering')
        return None
    df = pd.read_csv(path)
    # drop any target columns
    for c in ['loan_status', 'loan_amount', 'interest_rate']:
        if c in df.columns:
            df = df.drop(columns=[c])
    X = df.values

    # Use 50 components to match SVD from prepare_data (matches what _prepare_features returns)
    pca = PCA(n_components=min(n_components, X.shape[1], X.shape[0]), random_state=42)
    X_p = pca.fit_transform(X)
    joblib.dump(pca, MODELS_DIR / 'pca_model.pkl')
    print('Saved PCA model')

    # Use 5 clusters instead of 3 (matches n_components better)
    kmeans = KMeans(n_clusters=min(n_clusters, X_p.shape[0]), random_state=42, n_init=5)
    labels = kmeans.fit_predict(X_p)
    joblib.dump(kmeans, MODELS_DIR / 'clustering_model.pkl')
    # save cluster assignments
    out = pd.DataFrame(X_p, columns=[f'pca_{i}' for i in range(X_p.shape[1])])
    out['cluster'] = labels
    out.to_csv(OUT_DIR / 'pca_clusters.csv', index=False)

    cm = clustering_metrics(X_p, labels)
    joblib.dump(cm, OUT_DIR / 'clustering_metrics.json')
    print('Saved clustering model and metrics')
    return {'pca': pca, 'kmeans': kmeans, 'metrics': cm}


def run_all():
    print('Training classification...')
    train_classification()
    print('Training regression...')
    train_regression()
    print('PCA & clustering...')
    train_pca_and_clustering()
    print('All tasks completed')


if __name__ == '__main__':
    run_all()
