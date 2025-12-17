"""
Basic EDA for `data/bank_loan.csv`.
Saves summary JSON and basic histograms to `data/processed/`.
"""
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "bank_loan.csv"
OUT_DIR = PROJECT_ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def summarize(df: pd.DataFrame) -> dict:
    summary = {}
    summary['shape'] = df.shape
    summary['columns'] = list(df.columns)
    summary['dtypes'] = {c: str(df[c].dtype) for c in df.columns}
    summary['missing'] = {c: int(df[c].isna().sum()) for c in df.columns}
    numeric = df.select_dtypes(include=['number']).columns.tolist()
    summary['numeric_columns'] = numeric
    if numeric:
        desc = df[numeric].describe().to_dict()
        summary['numeric_describe'] = desc
        # correlations
        summary['correlation'] = df[numeric].corr().to_dict()
    return summary


def save_histograms(df: pd.DataFrame, numeric_cols):
    for col in numeric_cols:
        plt.figure(figsize=(6,4))
        try:
            df[col].dropna().hist(bins=50)
            plt.title(col)
            out = OUT_DIR / f"hist_{col}.png"
            plt.savefig(out)
        except Exception as e:
            print(f"Could not plot {col}: {e}")
        finally:
            plt.close()


def run_eda():
    if not DATA_PATH.exists():
        print(f"Data not found at {DATA_PATH}. Run scripts/import_dataset.py to copy the CSV.")
        return
    df = pd.read_csv(DATA_PATH)
    s = summarize(df)
    # convert non-serializable items
    s['shape'] = list(s['shape'])
    (OUT_DIR / 'eda_summary.json').write_text(json.dumps(s, indent=2))
    print(f"Saved summary to {(OUT_DIR / 'eda_summary.json')}")
    if s.get('numeric_columns'):
        save_histograms(df, s['numeric_columns'])
        print(f"Saved histograms to {OUT_DIR}")


if __name__ == '__main__':
    run_eda()
