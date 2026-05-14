from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


METADATA_COLUMNS = {
    "sample_id",
    "household_id",
    "participant_id",
    "visit_day",
    "symptom_status",
    "virus_status",
    "platform",
    "fastq_path",
    "emu_output",
    "bracken_output",
    "synthetic",
    "read_count",
}


def train_symptom_classifier(
    feature_path: str | Path,
    output_dir: str | Path,
    label_column: str = "symptom_status",
) -> dict[str, object]:
    feature_df = pd.read_csv(feature_path, sep="\t")
    if label_column not in feature_df:
        raise ValueError(f"Missing label column: {label_column}")

    feature_columns = [
        column for column in feature_df.columns if column not in METADATA_COLUMNS and column != label_column
    ]
    X = feature_df[feature_columns]
    y = feature_df[label_column].astype(str)

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    model = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value=0.0)),
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=5000, class_weight="balanced")),
        ]
    )

    min_class_size = y.value_counts().min()
    metrics: dict[str, float] = {}
    if min_class_size >= 2 and len(label_encoder.classes_) > 1:
        folds = min(3, int(min_class_size))
        cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=5994)
        scores = cross_validate(
            model,
            X,
            y_encoded,
            cv=cv,
            scoring=["accuracy", "f1_macro"],
            return_train_score=False,
        )
        metrics = {
            "accuracy": float(scores["test_accuracy"].mean()),
            "f1_macro": float(scores["test_f1_macro"].mean()),
        }

    model.fit(X, y_encoded)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out / "symptom_status_classifier.joblib")
    joblib.dump(label_encoder, out / "symptom_status_label_encoder.joblib")
    joblib.dump(feature_columns, out / "feature_columns.joblib")

    return {
        "model_path": out / "symptom_status_classifier.joblib",
        "label_encoder_path": out / "symptom_status_label_encoder.joblib",
        "feature_columns_path": out / "feature_columns.joblib",
        "classes": list(label_encoder.classes_),
        "metrics": metrics,
        "feature_count": len(feature_columns),
        "sample_count": int(feature_df.shape[0]),
    }

