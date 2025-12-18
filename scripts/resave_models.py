import os
import joblib
import pickle

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

# List of model files to process (add more if needed)
model_files = [
    'classification_model.pkl',
    'clustering_model.pkl',
    'pca_model.pkl',
    'preprocessor.joblib',
    'preprocessor_config.joblib',
    'regression_model.pkl',
    'svd_transformer.joblib',
]

for filename in model_files:
    path = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(path):
        print(f"File not found: {filename}")
        continue
    try:
        if filename.endswith('.pkl'):
            # Load and re-save with pickle
            with open(path, 'rb') as f:
                model = pickle.load(f)
            with open(path, 'wb') as f:
                pickle.dump(model, f)
            print(f"Re-saved (pickle): {filename}")
        elif filename.endswith('.joblib'):
            # Load and re-save with joblib
            model = joblib.load(path)
            joblib.dump(model, path)
            print(f"Re-saved (joblib): {filename}")
        else:
            print(f"Unknown file type: {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")
