import asyncio
import importlib
import json
import sys

import pytest


def load_server(monkeypatch, root_dir):
    monkeypatch.setenv("ROOT_DIR", str(root_dir))
    monkeypatch.delenv("ROOT_DIR_", raising=False)

    sys.modules.pop("course_mcp.config", None)
    sys.modules.pop("course_mcp.config.config", None)
    sys.modules.pop("course_mcp.services.file_service", None)
    sys.modules.pop("course_mcp.server", None)

    return importlib.import_module("course_mcp.server")


class FakeCourseService:
    def __init__(self):
        self.search_arguments = None

    def get_courses(self):
        return ["CMSC132"]

    def get_files(self, course_title):
        assert course_title == "CMSC132"
        return ["CMSC132/syllabus.pdf", "CMSC132/project1.md"]

    def search_file(
        self,
        course_title,
        file_path,
        keyword,
        context_lines,
        max_results,
    ):
        self.search_arguments = (
            course_title,
            file_path,
            keyword,
            context_lines,
            max_results,
        )
        return {
            "course_title": course_title,
            "file_path": file_path,
            "keyword": keyword,
            "match_count": 0,
            "truncated": False,
            "excerpts": [],
        }


def test_list_tools_includes_course_files_tool(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)

    tools = asyncio.run(server.handle_list_tools())

    tool_names = [tool.name for tool in tools]
    assert "list-courses" in tool_names
    assert "list-course-files" in tool_names

    course_files_tool = next(
        tool for tool in tools if tool.name == "list-course-files"
    )
    assert course_files_tool.inputSchema["required"] == ["course_title"]


def test_list_tools_includes_search_course_file_tool(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)

    tools = asyncio.run(server.handle_list_tools())

    search_tool = next(tool for tool in tools if tool.name == "search-course-file")
    schema = search_tool.inputSchema
    assert schema["required"] == ["course_title", "file_path", "keyword"]
    assert schema["properties"]["keyword"]["minLength"] == 1
    assert schema["properties"]["context_lines"] == {
        "type": "integer",
        "minimum": 0,
        "maximum": 20,
        "default": 3,
        "description": "Lines of context before and after each match.",
    }
    assert schema["properties"]["max_results"]["minimum"] == 1
    assert schema["properties"]["max_results"]["maximum"] == 100
    assert schema["properties"]["max_results"]["default"] == 20


def test_list_course_files_returns_files(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)
    monkeypatch.setattr(server, "course_service", FakeCourseService())

    result = asyncio.run(
        server.handle_call_tool(
            "list-course-files",
            {"course_title": "CMSC132"},
        )
    )

    assert result[0].text == "CMSC132/syllabus.pdf\nCMSC132/project1.md"


def test_list_course_files_requires_course_title(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="Missing required argument: course_title"):
        asyncio.run(server.handle_call_tool("list-course-files", {}))


def test_search_course_file_returns_json_and_uses_defaults(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)
    fake_service = FakeCourseService()
    monkeypatch.setattr(server, "course_service", fake_service)

    result = asyncio.run(
        server.handle_call_tool(
            "search-course-file",
            {
                "course_title": "CMSC132",
                "file_path": "notes/week1.txt",
                "keyword": "recursion",
            },
        )
    )

    assert fake_service.search_arguments == (
        "CMSC132",
        "notes/week1.txt",
        "recursion",
        3,
        20,
    )
    assert json.loads(result[0].text) == {
        "course_title": "CMSC132",
        "file_path": "notes/week1.txt",
        "keyword": "recursion",
        "match_count": 0,
        "truncated": False,
        "excerpts": [],
    }


@pytest.mark.parametrize("missing_argument", ["course_title", "file_path", "keyword"])
def test_search_course_file_requires_arguments(
    monkeypatch,
    tmp_path,
    missing_argument,
):
    server = load_server(monkeypatch, tmp_path)
    arguments = {
        "course_title": "CMSC132",
        "file_path": "notes.txt",
        "keyword": "recursion",
    }
    arguments.pop(missing_argument)

    with pytest.raises(
        ValueError,
        match=f"Missing required argument: {missing_argument}",
    ):
        asyncio.run(server.handle_call_tool("search-course-file", arguments))
