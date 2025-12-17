"""
Copy a dataset into the project `data/` folder.
Usage:
  python scripts/import_dataset.py --src "C:\\Users\\awais\\Downloads\\Compressed\\credit_train.csv"
If no `--src` provided, the script will attempt to copy from the path shown in the attachment.
"""
import argparse
import shutil
from pathlib import Path

DEFAULT_ATTACHMENT_PATH = Path(r"C:\Users\awais\Downloads\Compressed\credit_train.csv")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEST = PROJECT_ROOT / "data" / "bank_loan.csv"
DEST.parent.mkdir(parents=True, exist_ok=True)


def copy_dataset(src: Path):
    if not src.exists():
        print(f"Source not found: {src}")
        return False
    shutil.copy2(src, DEST)
    print(f"Copied {src} -> {DEST}")
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, help='Path to source CSV')
    args = parser.parse_args()
    src = Path(args.src) if args.src else DEFAULT_ATTACHMENT_PATH
    ok = copy_dataset(src)
    if not ok:
        print("Please place your CSV at the expected path or provide --src path.")
