from types import SimpleNamespace

import pandas as pd
import pytest

from asi_project.pipelines.data_science import nodes


@pytest.mark.parametrize(
    ("model_params", "expected_preset"),
    [
        ({"preset": "medium_quality", "time_limit": 60}, ["medium_quality"]),
        ({"preset": "good_quality", "time_limit": 60}, ["good_quality"]),
    ],
)
def test_train_autogluon_uses_configured_parameters(
    monkeypatch,
    model_params,
    expected_preset,
):
    class FakePredictor:
        def __init__(self, **kwargs):
            self.init_params = kwargs

        def fit(self, train_data, **kwargs):
            self.fit_data = train_data
            self.fit_params = kwargs

    monkeypatch.setattr(nodes, "_load_project", lambda: (None, None))
    monkeypatch.setattr(nodes, "TabularPredictor", FakePredictor)

    model = nodes.train_model(
        pd.DataFrame({"feature": [1, 2]}),
        pd.Series([0, 1]),
        model_type="autogluon",
        model_params=model_params,
    )

    assert model.fit_params == {"time_limit": 60, "presets": expected_preset}
    assert model.fit_data["target"].tolist() == [0, 1]


def test_evaluate_logs_model_split_and_provenance_parameters(monkeypatch):
    class FakeWandb:
        def __init__(self):
            self.config = SimpleNamespace(update=self.update_config)
            self.run = SimpleNamespace(summary={})
            self.logged_config = None

        def init(self, **kwargs):
            self.init_params = kwargs
            return self.run

        def update_config(self, config):
            self.logged_config = config

        def log(self, metrics):
            self.logged_metrics = metrics

        def finish(self):
            pass

    fake_wandb = FakeWandb()
    monkeypatch.setattr(nodes, "wandb", fake_wandb)
    monkeypatch.setattr(nodes, "_git_sha", lambda: "test-sha")
    monkeypatch.setattr(nodes, "_dataset_fingerprint", lambda: "test-fingerprint")
    monkeypatch.setenv("WANDB_PROJECT", "environment-project")

    model = SimpleNamespace(predict=lambda X: [0, 1])
    model_params = {"preset": "medium_quality", "time_limit": 60}
    split_params = {"test_size": 0.2, "random_state": 42}
    wandb_params = {"project": "team-project", "mode": "online"}

    nodes.evaluate_model(
        model,
        pd.DataFrame({"feature": [1, 2]}),
        pd.Series([0, 1]),
        run_name="baseline",
        model_type="baseline",
        model_params=model_params,
        split_params=split_params,
        wandb_params=wandb_params,
    )

    assert fake_wandb.init_params["name"] == "baseline"
    assert fake_wandb.init_params["project"] == "team-project"
    assert fake_wandb.logged_config == {
        "model_type": "baseline",
        "model_params": model_params,
        "split": split_params,
        "git_sha": "test-sha",
        "dataset_fingerprint": "test-fingerprint",
    }


def test_package_model_node_writes_package(monkeypatch, tmp_path):
    from sklearn.dummy import DummyClassifier

    monkeypatch.setattr(nodes, "_git_sha", lambda: "test-sha")
    monkeypatch.setattr(nodes, "_dataset_fingerprint", lambda: "test-fingerprint")

    model = DummyClassifier().fit(pd.DataFrame({"x": [0, 1]}), [0, 1])
    metadata = nodes.package_model(
        model,
        {"f1": 0.5},
        model_type="baseline",
        model_params={},
        package_params={"path": str(tmp_path / "pkg"), "model_name": None},
    )

    assert metadata["model_format"] == "sklearn-joblib"
    assert metadata["git_sha"] == "test-sha"
    assert (tmp_path / "pkg" / "metadata.json").is_file()
