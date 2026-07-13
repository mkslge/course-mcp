import importlib
import sys

import pytest


def load_file_service(monkeypatch, root_dir):
    monkeypatch.setenv("ROOT_DIR", str(root_dir))
    monkeypatch.delenv("ROOT_DIR_", raising=False)

    sys.modules.pop("course_mcp.config", None)
    sys.modules.pop("course_mcp.config.config", None)
    sys.modules.pop("course_mcp.services.file_service", None)

    return importlib.import_module("course_mcp.services.file_service")


def test_resolve_path_stays_inside_root(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)

    assert service.resolve_path("notes/week1.txt") == (
        tmp_path / "notes" / "week1.txt"
    ).resolve()


def test_resolve_path_rejects_paths_outside_root(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)

    with pytest.raises(ValueError, match="Path is outside ROOT_DIR"):
        service.resolve_path("../secret.txt")


def test_get_contents_reads_whole_file(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    file_path = tmp_path / "lecture.txt"
    file_path.write_text("line one\nline two\n")

    assert service.get_contents("lecture.txt") == "line one\nline two\n"


def test_get_contents_reads_line_range(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    file_path = tmp_path / "lecture.txt"
    file_path.write_text("one\ntwo\nthree\n")

    assert service.get_contents("lecture.txt", start_line=2, end_line=3) == "two\nthree\n"


def test_module_level_get_contents_uses_injected_root(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    file_path = tmp_path / "lecture.txt"
    file_path.write_text("module helper\n")

    assert module.get_contents("lecture.txt") == "module helper\n"
