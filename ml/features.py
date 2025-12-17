import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from pathlib import Path
import joblib


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "income" in df.columns and "loan_amount" in df.columns:
        df["debt_to_income"] = df["loan_amount"] / (df["income"] + 1e-9)
    return df


def build_preprocessor(df: pd.DataFrame, saved_path: Path = None) -> Pipeline:
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # exclude the targets if present
    for t in ["loan_status", "loan_amount", "interest_rate"]:
        if t in numeric_cols:
            numeric_cols.remove(t)
    categorical_cols = df.select_dtypes(include=[object, "category"]).columns.tolist()

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    # Use sparse_output where available (scikit-learn >=1.2), fall back to sparse for older versions
    # prefer sparse output to avoid exploding memory with high-cardinality categories
    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    except TypeError:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=True)

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", ohe)
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ],
        remainder="drop",
    )

    if saved_path:
        saved_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(preprocessor, saved_path)

    return preprocessor


def apply_preprocessor(preprocessor: Pipeline, df: pd.DataFrame):
    # returns transformed matrix (may be sparse) and feature names when safe to build
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for t in ["loan_status", "loan_amount", "interest_rate"]:
        if t in numeric_cols:
            numeric_cols.remove(t)
    categorical_cols = df.select_dtypes(include=[object, "category"]).columns.tolist()
    X = preprocessor.transform(df)

    # avoid building huge dense feature name lists for high-cardinality encoders
    feature_names = None
    try:
        # only build feature names if encoder produces dense output or reasonably small
        if hasattr(preprocessor.named_transformers_["cat"].named_steps["onehot"], "get_feature_names_out"):
            ohe = preprocessor.named_transformers_["cat"].named_steps["onehot"]
            cat_names = ohe.get_feature_names_out(categorical_cols).tolist()
            feature_names = numeric_cols + cat_names
    except Exception:
        feature_names = None

    return X, feature_names
