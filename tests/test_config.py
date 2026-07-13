import importlib
import sys

import pytest


def reload_config(monkeypatch, root_dir=None, root_dir_fallback=None):
    if root_dir is None:
        monkeypatch.delenv("ROOT_DIR", raising=False)
    else:
        monkeypatch.setenv("ROOT_DIR", str(root_dir))

    if root_dir_fallback is None:
        monkeypatch.delenv("ROOT_DIR_", raising=False)
    else:
        monkeypatch.setenv("ROOT_DIR_", str(root_dir_fallback))

    sys.modules.pop("course_mcp.config", None)
    sys.modules.pop("course_mcp.config.config", None)

    return importlib.import_module("course_mcp.config.config")


def test_root_dir_uses_root_dir_environment_value(monkeypatch, tmp_path):
    config = reload_config(monkeypatch, root_dir=tmp_path)

    assert config.ROOT_DIR == tmp_path.resolve()


def test_root_dir_falls_back_to_root_dir_underscore(monkeypatch, tmp_path):
    config = reload_config(monkeypatch, root_dir=tmp_path)
    monkeypatch.delenv("ROOT_DIR", raising=False)
    monkeypatch.setenv("ROOT_DIR_", str(tmp_path))
    monkeypatch.setattr(config, "_load_env_file", lambda env_path: None)

    assert config._get_root_dir() == tmp_path.resolve()


def test_root_dir_must_exist(monkeypatch, tmp_path):
    missing_path = tmp_path / "missing"

    with pytest.raises(RuntimeError, match="ROOT_DIR does not exist"):
        reload_config(monkeypatch, root_dir=missing_path)
