import importlib
import sys
from types import SimpleNamespace

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


def create_course_file(tmp_path, relative_path, contents, *, binary=False):
    path = tmp_path / "CMSC132" / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if binary:
        path.write_bytes(contents)
    else:
        path.write_text(contents, encoding="utf-8")
    return path


def test_search_file_matches_literal_case_insensitively_and_merges_context(
    monkeypatch,
    tmp_path,
):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    create_course_file(
        tmp_path,
        "notes/week1.txt",
        "intro\nRECURSION recursion\nbetween\nrecursion!\nend\n",
    )

    result = service.search_file(
        "CMSC132",
        "notes/week1.txt",
        "recursion",
        context_lines=1,
    )

    assert result == {
        "course_title": "CMSC132",
        "file_path": "notes/week1.txt",
        "keyword": "recursion",
        "match_count": 2,
        "truncated": False,
        "excerpts": [
            {
                "start_line": 1,
                "end_line": 5,
                "match_lines": [2, 4],
                "lines": [
                    {"line_number": 1, "text": "intro"},
                    {"line_number": 2, "text": "RECURSION recursion"},
                    {"line_number": 3, "text": "between"},
                    {"line_number": 4, "text": "recursion!"},
                    {"line_number": 5, "text": "end"},
                ],
            }
        ],
    }


@pytest.mark.parametrize("keyword", ["two words", "!", " "])
def test_search_file_accepts_literal_whitespace_and_punctuation(
    monkeypatch,
    tmp_path,
    keyword,
):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    create_course_file(tmp_path, "notes.txt", "two words!\n")

    result = service.search_file(
        "CMSC132",
        "notes.txt",
        keyword,
        context_lines=0,
    )

    assert result["match_count"] == 1


def test_search_file_returns_empty_excerpts_for_no_matches(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    create_course_file(tmp_path, "notes.txt", "iteration\n")

    result = service.search_file("CMSC132", "notes.txt", "recursion")

    assert result["match_count"] == 0
    assert result["truncated"] is False
    assert result["excerpts"] == []


def test_search_file_truncates_marked_matches_but_keeps_context(
    monkeypatch,
    tmp_path,
):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    create_course_file(tmp_path, "notes.txt", "match one\nmatch two\n")

    result = service.search_file(
        "CMSC132",
        "notes.txt",
        "match",
        context_lines=1,
        max_results=1,
    )

    assert result["match_count"] == 2
    assert result["truncated"] is True
    assert result["excerpts"][0]["match_lines"] == [1]
    assert result["excerpts"][0]["lines"] == [
        {"line_number": 1, "text": "match one"},
        {"line_number": 2, "text": "match two"},
    ]


@pytest.mark.parametrize(
    ("keyword", "context_lines", "max_results", "message"),
    [
        ("", 3, 20, "keyword must not be empty"),
        ("match", -1, 20, "context_lines must be an integer from 0 to 20"),
        ("match", 21, 20, "context_lines must be an integer from 0 to 20"),
        ("match", 3, 0, "max_results must be an integer from 1 to 100"),
        ("match", 3, 101, "max_results must be an integer from 1 to 100"),
    ],
)
def test_search_file_validates_search_arguments(
    monkeypatch,
    tmp_path,
    keyword,
    context_lines,
    max_results,
    message,
):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)

    with pytest.raises(ValueError, match=message):
        service.search_file(
            "CMSC132",
            "notes.txt",
            keyword,
            context_lines,
            max_results,
        )


def test_search_file_rejects_invalid_course_and_file_paths(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    create_course_file(tmp_path, "notes.txt", "content\n")
    other_course = tmp_path / "CMSC216"
    other_course.mkdir()
    (other_course / "secret.txt").write_text("secret\n")

    with pytest.raises(ValueError, match="direct course directory"):
        service.search_file("CMSC132/nested", "notes.txt", "content")
    with pytest.raises(ValueError, match="relative to the course"):
        service.search_file("CMSC132", str(tmp_path / "outside.txt"), "content")
    with pytest.raises(ValueError, match="outside course directory"):
        service.search_file("CMSC132", "../CMSC216/secret.txt", "secret")


def test_search_file_rejects_symlink_escape(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    create_course_file(tmp_path, "notes.txt", "content\n")
    outside = tmp_path / "outside.txt"
    outside.write_text("secret\n")
    (tmp_path / "CMSC132" / "link.txt").symlink_to(outside)

    with pytest.raises(ValueError, match="outside course directory"):
        service.search_file("CMSC132", "link.txt", "secret")


def test_search_file_rejects_missing_directory_and_non_utf8_file(
    monkeypatch,
    tmp_path,
):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    create_course_file(tmp_path, "binary.dat", b"\xff\xfe", binary=True)
    (tmp_path / "CMSC132" / "folder").mkdir()

    with pytest.raises(FileNotFoundError, match="does not exist"):
        service.search_file("CMSC132", "missing.txt", "text")
    with pytest.raises(IsADirectoryError, match="not a file"):
        service.search_file("CMSC132", "folder", "text")
    with pytest.raises(ValueError, match="not valid UTF-8"):
        service.search_file("CMSC132", "binary.dat", "text")


class FakePdfPage:
    def __init__(self, text=None, error=None):
        self.text = text
        self.error = error

    def extract_text(self):
        if self.error is not None:
            raise self.error
        return self.text


def test_search_file_reports_pdf_pages_and_page_local_lines(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    create_course_file(tmp_path, "LECTURE.PDF", b"pdf", binary=True)
    pages = [
        FakePdfPage("intro\nRecursion\nend"),
        FakePdfPage("recursion again\nlast"),
    ]
    monkeypatch.setattr(
        module,
        "PdfReader",
        lambda path: SimpleNamespace(is_encrypted=False, pages=pages),
    )

    result = service.search_file(
        "CMSC132",
        "LECTURE.PDF",
        "recursion",
        context_lines=1,
    )

    assert result["match_count"] == 2
    assert [excerpt["page"] for excerpt in result["excerpts"]] == [1, 2]
    assert [excerpt["match_lines"] for excerpt in result["excerpts"]] == [
        [2],
        [1],
    ]
    assert result["excerpts"][1]["start_line"] == 1


def test_search_file_rejects_unsearchable_pdfs(monkeypatch, tmp_path):
    module = load_file_service(monkeypatch, tmp_path)
    service = module.FileService(tmp_path)
    create_course_file(tmp_path, "lecture.pdf", b"pdf", binary=True)

    monkeypatch.setattr(
        module,
        "PdfReader",
        lambda path: SimpleNamespace(is_encrypted=True, pages=[]),
    )
    with pytest.raises(ValueError, match="PDF is encrypted"):
        service.search_file("CMSC132", "lecture.pdf", "keyword")

    monkeypatch.setattr(
        module,
        "PdfReader",
        lambda path: SimpleNamespace(
            is_encrypted=False,
            pages=[FakePdfPage(" \n")],
        ),
    )
    with pytest.raises(ValueError, match="no extractable text"):
        service.search_file("CMSC132", "lecture.pdf", "keyword")

    monkeypatch.setattr(
        module,
        "PdfReader",
        lambda path: (_ for _ in ()).throw(RuntimeError("corrupt")),
    )
    with pytest.raises(ValueError, match="Unable to read PDF"):
        service.search_file("CMSC132", "lecture.pdf", "keyword")
