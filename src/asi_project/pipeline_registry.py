"""Rejestrowanie pipeline'ów Kedro."""

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline


def register_pipelines() -> dict[str, Pipeline]:
    """Wykryj pipeline'y i połącz je w pipeline domyślny."""
    pipelines = find_pipelines()
    pipelines["__default__"] = sum(pipelines.values())
    return pipelines
