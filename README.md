# Smart Credit Risk Platform

Scaffold for a credit risk ML platform. Place your dataset at `data/bank_loan.csv` (<50MB recommended) and follow the ML scripts in `ml/` to preprocess, train, and evaluate models. Run the backend with:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Prefect flows live in `prefect/flow.py`.
