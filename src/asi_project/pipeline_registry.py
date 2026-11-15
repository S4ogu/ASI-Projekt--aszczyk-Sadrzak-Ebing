"""Rejestrowanie pipeline'ów Kedro."""

from kedro.pipeline import Pipeline

from asi_project.pipelines.data_processing.pipeline import create_pipeline as dp_create
from asi_project.pipelines.data_science.pipeline import create_pipeline as ds_create


def register_pipelines() -> dict[str, Pipeline]:
    """Zarejestruj pipeline'y nazwane i pipeline domyślny."""
    dp_pipeline = dp_create()
    ds_pipeline = ds_create()

    return {
        "__default__": dp_pipeline + ds_pipeline,
        "data_processing": dp_pipeline,
        "data_science": ds_pipeline,
    }
