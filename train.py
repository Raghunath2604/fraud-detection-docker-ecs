from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import joblib
import os

# Create synthetic fraud dataset
X, y = make_classification(
    n_samples=5000,
    n_features=4,
    n_informative=4,
    n_redundant=0,
    random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/fraud.pkl")

print("Fraud model trained.")
print(f"Model accuracy: {model.score(X_test, y_test):.4f}")
