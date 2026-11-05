import pandas as pd

from asi_project.config import DatasetContract, ProjectConfig, get_contract, load_project_config
from asi_project.data import (
    assert_valid,
    filter_training_rows,
    normalize_column_names,
    normalize_input,
)


# lokalna funkcja, ładuje config projektu
def _load_project() -> tuple[ProjectConfig, DatasetContract]:
    config = load_project_config()
    return config, get_contract(config)


def validate_contract(raw_data: pd.DataFrame) -> pd.DataFrame:
    config, contract = _load_project()
    df = normalize_column_names(raw_data)
    assert_valid(df, contract, config)
    return df


def normalize(valid_data: pd.DataFrame) -> pd.DataFrame:
    return normalize_input(valid_data)


def filter_training_data(norm_data: pd.DataFrame) -> pd.DataFrame:
    config, contract = _load_project()
    filtered = filter_training_rows(norm_data, contract)
    return filtered
