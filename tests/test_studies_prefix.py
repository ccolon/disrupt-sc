"""The ``studies:`` prefix of configuration paths (18 Nov 2026): study files live in a separate repository,
found through DISRUPT_SC_STUDIES or as the folder disrupt-sc-studies next to the code repository."""

from pathlib import Path

from disruptsc import paths
from disruptsc.config import resolve_repo_prefix


def test_studies_prefix_uses_the_environment_variable(monkeypatch, tmp_path):
    monkeypatch.setenv(paths.STUDIES_ENV_VAR, str(tmp_path))
    assert Path(resolve_repo_prefix("studies:a/b.csv")) == tmp_path.resolve() / "a" / "b.csv"


def test_studies_prefix_defaults_to_the_sibling_folder(monkeypatch):
    monkeypatch.delenv(paths.STUDIES_ENV_VAR, raising=False)
    assert Path(resolve_repo_prefix("studies:a/b.csv")) == paths.ROOT_FOLDER.parent / "disrupt-sc-studies" / "a" / "b.csv"


def test_repo_prefix_still_points_at_the_code_repository():
    assert Path(resolve_repo_prefix("repo:config/default.yaml")) == paths.ROOT_FOLDER / "config" / "default.yaml"


def test_old_repo_studies_value_falls_back_to_the_studies_repository(monkeypatch, tmp_path):
    monkeypatch.setenv(paths.STUDIES_ENV_VAR, str(tmp_path))
    old = "repo:studies/no_such_study_xyz/additional_data/file.csv"
    assert Path(resolve_repo_prefix(old)) == tmp_path.resolve() / "no_such_study_xyz" / "additional_data" / "file.csv"


def test_other_values_are_returned_unchanged():
    v = "Transport/transport.gpkg"
    assert resolve_repo_prefix(v) is v
    assert resolve_repo_prefix(None) is None
