"""
Prepare data for ML tasks: cleaning, feature engineering, preprocessing and save processed datasets.
Saves:
 - data/processed/for_classification.csv
 - data/processed/for_regression.csv
 - models/preprocessor.joblib
"""
from pathlib import Path
import pandas as pd
import numpy as np
from .features import add_derived_features, build_preprocessor, apply_preprocessor
import joblib
from scipy import sparse
from sklearn.decomposition import TruncatedSVD

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'data' / 'bank_loan.csv'
OUT_DIR = ROOT / 'data' / 'processed'
MODELS_DIR = ROOT / 'models'
OUT_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def prepare():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    # Normalize common column names (case-insensitive) to expected keys
    col_map = {c.lower().strip(): c for c in df.columns}

    def find_col(candidates):
        for cand in candidates:
            key = cand.lower()
            if key in col_map:
                return col_map[key]
        return None

    # common name candidates
    loan_status_col = find_col(['loan_status', 'loan status', 'loanstatus', 'status'])
    loan_amount_col = find_col(['loan_amount', 'current loan amount', 'loan amnt', 'loanamount', 'loan amount'])
    interest_col = find_col(['interest_rate', 'int_rate', 'interest rate', 'int rate'])
    income_col = find_col(['annual income', 'annual_income', 'income'])
    employment_col = find_col(['years in current job', 'employment_length', 'emp_length', 'years_current_job'])
    purpose_col = find_col(['purpose'])
    term_col = find_col(['term'])

    rename_map = {}
    if loan_status_col:
        rename_map[loan_status_col] = 'loan_status'
    if loan_amount_col:
        rename_map[loan_amount_col] = 'loan_amount'
    if interest_col:
        rename_map[interest_col] = 'interest_rate'
    if income_col:
        rename_map[income_col] = 'income'
    if employment_col:
        rename_map[employment_col] = 'employment_length'
    if purpose_col:
        rename_map[purpose_col] = 'purpose'
    if term_col:
        rename_map[term_col] = 'term'

    if rename_map:
        df = df.rename(columns=rename_map)

    df = add_derived_features(df)

    # basic target handling: ensure loan_status exists for classification
    # convert loan_status to binary (if multi-class, keep as-is)
    if 'loan_status' in df.columns:
        # try to normalize common labels
        df['loan_status'] = df['loan_status'].astype(str).str.lower().map(
            lambda x: 'default' if 'default' in x or 'charged' in x or 'late' in x else ('approved' if 'appr' in x or 'paid' in x or 'fully' in x else x)
        )

    preprocessor = build_preprocessor(df, saved_path=MODELS_DIR / 'preprocessor.joblib')
    # fit preprocessor on whole data
    preprocessor.fit(df)
    joblib.dump(preprocessor, MODELS_DIR / 'preprocessor.joblib')
    
    # Save the column names and types for use in prediction
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for t in ["loan_status", "loan_amount", "interest_rate"]:
        if t in numeric_cols:
            numeric_cols.remove(t)
    categorical_cols = df.select_dtypes(include=[object, "category"]).columns.tolist()
    
    config = {
        'numeric_cols': numeric_cols,
        'categorical_cols': categorical_cols,
        'all_cols': df.columns.tolist()
    }
    joblib.dump(config, MODELS_DIR / 'preprocessor_config.joblib')

    # transform and save features; handle sparse outputs safely
    X, feature_names = apply_preprocessor(preprocessor, df)

    # If X is sparse or very wide, reduce dimensionality with TruncatedSVD
    if sparse.issparse(X) or (hasattr(X, 'shape') and X.shape[1] > 1000):
        n_components = min(50, X.shape[1] if hasattr(X, 'shape') else 50)
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        X_reduced = svd.fit_transform(X)
        df_X = pd.DataFrame(X_reduced, columns=[f'svd_{i}' for i in range(X_reduced.shape[1])])
        joblib.dump(svd, MODELS_DIR / 'svd_transformer.joblib')
    else:
        # dense case
        df_X = pd.DataFrame(X, columns=feature_names) if feature_names else pd.DataFrame(X)

    # attach targets if present and save for classification
    if 'loan_status' in df.columns:
        df_X['loan_status'] = df['loan_status'].values
    df_X.to_csv(OUT_DIR / 'for_classification.csv', index=False)

    # regression target: prefer loan_amount then interest_rate
    if 'loan_amount' in df.columns:
        df_X_reg = df_X.copy()
        df_X_reg['loan_amount'] = df['loan_amount'].values
        df_X_reg.to_csv(OUT_DIR / 'for_regression.csv', index=False)
    elif 'interest_rate' in df.columns:
        df_X_reg = df_X.copy()
        df_X_reg['interest_rate'] = df['interest_rate'].values
        df_X_reg.to_csv(OUT_DIR / 'for_regression.csv', index=False)
    else:
        df_X.to_csv(OUT_DIR / 'for_regression.csv', index=False)

    print(f"Saved processed data to {OUT_DIR} and preprocessor to {MODELS_DIR / 'preprocessor.joblib'}")


if __name__ == '__main__':
    prepare()
