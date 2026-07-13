import asyncio
import importlib
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
    def get_courses(self):
        return ["CMSC132"]

    def get_files(self, course_title):
        assert course_title == "CMSC132"
        return ["CMSC132/syllabus.pdf", "CMSC132/project1.md"]


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
