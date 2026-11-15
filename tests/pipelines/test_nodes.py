import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from asi_project.config import get_contract, load_project_config
from asi_project.data import load_dataset
from asi_project.pipelines.data_processing.nodes import (
    filter_training_data,
    normalize,
    validate_contract,
)
from asi_project.pipelines.data_science.nodes import evaluate_model, split_data, train_model


@pytest.fixture
def _load_project():
    config = load_project_config()
    contract = get_contract(config)
    return config, contract


@pytest.fixture
def sample_data(_load_project):
    config, contract = _load_project
    data = load_dataset(config, contract, mode="sample")
    return data


@pytest.fixture
def validate_data(sample_data):
    return validate_contract(sample_data)


@pytest.fixture
def normalize_data(validate_data):
    return normalize(validate_data)


@pytest.fixture
def filter_data(normalize_data):
    return filter_training_data(normalize_data)


@pytest.fixture
def split_filtered_data(filter_data):
    split_params = {"test_size": 0.2, "random_state": 42}
    return split_data(filter_data, split_params)


@pytest.fixture
def train_model_on_split(split_filtered_data):
    X_train, _, y_train, _ = split_filtered_data
    return train_model(X_train, y_train)


def test_validate_contract(sample_data, validate_data):
    assert isinstance(validate_data, pd.DataFrame)
    assert len(validate_data) == len(sample_data)


def test_normalize(validate_data, normalize_data):
    assert isinstance(normalize_data, pd.DataFrame)
    assert len(normalize_data) == len(validate_data)


def test_filter_training_data(normalize_data, filter_data):
    assert isinstance(filter_data, pd.DataFrame)
    assert len(filter_data) <= len(normalize_data)


def test_split_data(split_filtered_data):
    X_train, X_test, y_train, y_test = split_filtered_data
    assert isinstance(X_train, pd.DataFrame)
    assert isinstance(X_test, pd.DataFrame)
    assert isinstance(y_train, pd.Series)
    assert isinstance(y_test, pd.Series)
    assert len(X_train) > 0
    assert len(X_test) > 0


def test_train_model(train_model_on_split):
    assert isinstance(train_model_on_split, Pipeline)
    assert hasattr(train_model_on_split, "predict")


def test_evaluate_model(train_model_on_split, split_filtered_data):
    _, X_test, _, y_test = split_filtered_data
    metrics = evaluate_model(train_model_on_split, X_test, y_test)
    assert isinstance(metrics, dict)
    assert len(metrics) > 0
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
