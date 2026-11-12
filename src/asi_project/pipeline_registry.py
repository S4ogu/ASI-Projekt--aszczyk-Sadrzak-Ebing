"""Rejestrowanie pipeline'ów Kedro (Sprint 2).

Po przygotowaniu ``create_pipeline()`` w podpakietach
``data_processing`` oraz ``data_science`` Kedro wykrywa je automatycznie.
Ten plik NIE zawiera implementacji nodów ani gotowego pipeline'u.
"""

from kedro.pipeline import Pipeline

# def register_pipelines() -> dict[str, Pipeline]:
#   """Wykryj pipeline'y z ``src/asi_project/pipelines/``."""
#  return find_pipelines()
from asi_project.pipelines.data_processing.pipeline import create_pipeline as dp_create
from asi_project.pipelines.data_science.pipeline import create_pipeline as ds_create


def register_pipelines() -> dict[str, Pipeline]:
    dp_pipeline = dp_create()
    ds_pipeline = ds_create()

    return {
        "__default__": dp_pipeline + ds_pipeline,
        "data_processing": dp_pipeline,
        "data_science": ds_pipeline,
    }
