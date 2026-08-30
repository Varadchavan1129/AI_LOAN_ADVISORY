import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

# ---------------------------
# 1. Load Dataset
# ---------------------------
df = pd.read_csv("loan_data.csv")

# ---------------------------
# 2. Target Variable
# ---------------------------
TARGET = "loan_status"
y = df[TARGET]

# ---------------------------
# 3. Feature Selection
# (Use ALL except target)
# ---------------------------
X = df.drop(columns=[TARGET])

# ---------------------------
# 4. Separate Numeric & Categorical
# ---------------------------
numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
categorical_features = X.select_dtypes(include=["object"]).columns.tolist()

print("Numeric features:", numeric_features)
print("Categorical features:", categorical_features)

# ---------------------------
# 5. Preprocessing Pipelines
# ---------------------------
numeric_transformer = Pipeline(steps=[
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)

# ---------------------------
# 6. Model
# ---------------------------
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=2000))
])

# ---------------------------
# 7. Train/Test Split
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---------------------------
# 8. Train
# ---------------------------
model.fit(X_train, y_train)

# ---------------------------
# 9. Save Model
# ---------------------------
joblib.dump(model, "risk_model.pkl")

print("Model trained using ALL attributes and saved as risk_model.pkl")
