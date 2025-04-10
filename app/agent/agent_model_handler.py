import joblib
import pandas as pd
import os

class StrategyModelHandler:
    def __init__(self):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../model'))

        self.models = {
            "split": {
                "model": joblib.load(os.path.join(base_path, "splitting_model.pkl")),
                "encoder": joblib.load(os.path.join(base_path, "splitting_label_encoder.pkl")),
                "features": ["player_total", "dealer_card"]
            },
            "stand_hit_double": {
                "model": joblib.load(os.path.join(base_path, "basic_strategy_model.pkl")),
                "encoder": joblib.load(os.path.join(base_path, "basic_strategy_label_encoder.pkl")),
                "features": ["player_total", "dealer_card", "is_soft"]
            }
        }

        print("modèles chargés correctement")

    def predict(self, strategy, feature_values):
        info = self.models[strategy]
        X = pd.DataFrame([feature_values], columns=info["features"])
        pred_encoded = info["model"].predict(X)[0]
        return info["encoder"].inverse_transform([pred_encoded])[0]