from kedro.pipeline import Pipeline, node

from .nodes import filter_training_data, normalize, validate_contract


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(validate_contract, "raw_data", "valid_data", name="validate_contract"),
            node(normalize, "valid_data", "norm_data", name="input_normalization"),
            node(
                filter_training_data,
                "norm_data",
                "model_input_data",
                name="training_only_filtering",
            ),
        ]
    )
