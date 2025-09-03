import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from xgboost import XGBClassifier, XGBRegressor
import os
from imblearn.over_sampling import SMOTE
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
    precision_recall_curve,
    confusion_matrix
)

class ModelTrainer:
    def __init__(self):
        self.models = {
            "random_forest": RandomForestClassifier(class_weight='balanced', n_estimators=200),
            "svm": SVC(probability=True, class_weight='balanced'),
            "xgboost": XGBClassifier(eval_metric='logloss', scale_pos_weight=10)
        }

    def train_all(self):
        try:
            data = pd.read_csv("data/processed_data.csv")
            data.columns = [col.replace('[', '').replace(']', '') for col in data.columns]

            X = data[['air_temp', 'process_temp', 'rotational_speed', 'torque', 'tool_wear']]
            y = data['failure']

            #SMOTE ile veri dengeleme
            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X, y)

            #Veriyi bölme
            X_train, X_test, y_train, y_test = train_test_split(
                X_resampled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled
            )

            #Model eğitimi
            for model_name, model in self.models.items():
                print(f"\n⭐ {model_name.upper()} eğitiliyor...")
                model.fit(X_train, y_train)
                joblib.dump(model, f"models/trained_models/classification/{model_name}.joblib")
                self._evaluate_model(model, X_test, y_test)

        except Exception as e:
            print(f"\n Eğitim hatası: {str(e)}")
            raise

    def _evaluate_model(self, model, X_test, y_test):
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        print("\n📊 Performans Metrikleri:")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"Precision: {precision_score(y_test, y_pred):.4f}")
        print(f"Recall: {recall_score(y_test, y_pred):.4f}")
        print(f"F1 Score: {f1_score(y_test, y_pred):.4f}")
        print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")