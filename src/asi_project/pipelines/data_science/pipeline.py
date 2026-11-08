from kedro.pipeline import Pipeline, node
from .nodes import evaluate_model, split_data, train_model

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                split_data, 
                ["model_input_data", "params:split"], 
                ["X_train", "X_test", "y_train", "y_test"], 
                name="split_train_test",
            ),
            node(
                train_model, 
                ["X_train", "y_train"], 
                "model", 
                name="train_model"
            ),
            node(
                evaluate_model, 
                ["model", "X_test", "y_test"], 
                "metrics", 
                name="evaluate_model",
            ),
        ]
    )