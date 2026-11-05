# Required by kedro to run

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline


def register_pipelines() -> dict[str, Pipeline]:
    pipelines = find_pipelines()

    # sum() makes the pipelines run one after another
    pipelines["__default__"] = sum(pipelines.values())
    return pipelines
