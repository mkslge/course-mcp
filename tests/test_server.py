import asyncio
import importlib
import json
import sys

import pytest
import mcp.types as types


def load_server(monkeypatch, root_dir):
    monkeypatch.setenv("ROOT_DIR", str(root_dir))
    monkeypatch.delenv("ROOT_DIR_", raising=False)

    sys.modules.pop("course_mcp.config", None)
    sys.modules.pop("course_mcp.config.config", None)
    sys.modules.pop("course_mcp.services.file_service", None)
    sys.modules.pop("course_mcp.server", None)

    return importlib.import_module("course_mcp.server")


def call_registered_tool(server_module, name, arguments):
    request = types.CallToolRequest(
        params=types.CallToolRequestParams(
            name=name,
            arguments=arguments,
        )
    )
    handler = server_module.server.request_handlers[types.CallToolRequest]
    return asyncio.run(handler(request)).root


class FakeCourseService:
    def __init__(self):
        self.search_arguments = None
        self.course_search_arguments = None

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

    def search_course(
        self,
        course_title,
        keyword,
        context_lines,
        max_results,
    ):
        self.course_search_arguments = (
            course_title,
            keyword,
            context_lines,
            max_results,
        )
        return {
            "course_title": course_title,
            "keyword": keyword,
            "matching_file_count": 0,
            "match_count": 0,
            "files": [],
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
    output_schema = search_tool.outputSchema
    assert output_schema is not None
    assert output_schema["additionalProperties"] is False
    assert output_schema["required"] == [
        "course_title",
        "file_path",
        "keyword",
        "match_count",
        "truncated",
        "excerpts",
    ]
    excerpt_schema = output_schema["properties"]["excerpts"]["items"]
    assert "page" in excerpt_schema["properties"]
    assert "page" not in excerpt_schema["required"]
    assert excerpt_schema["additionalProperties"] is False
    assert (
        excerpt_schema["properties"]["lines"]["items"]["additionalProperties"]
        is False
    )


def test_list_tools_includes_search_course_tool(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)

    tools = asyncio.run(server.handle_list_tools())

    search_tool = next(tool for tool in tools if tool.name == "search-course")
    schema = search_tool.inputSchema
    assert schema["required"] == ["course_title", "keyword"]
    assert schema["properties"]["keyword"]["minLength"] == 1
    assert schema["properties"]["context_lines"]["default"] == 3
    assert schema["properties"]["context_lines"]["maximum"] == 20
    assert schema["properties"]["max_results"]["default"] == 20
    assert schema["properties"]["max_results"]["maximum"] == 100
    output_schema = search_tool.outputSchema
    assert output_schema is not None
    assert output_schema["additionalProperties"] is False
    assert output_schema["required"] == [
        "course_title",
        "keyword",
        "matching_file_count",
        "match_count",
        "files",
    ]
    file_schema = output_schema["properties"]["files"]["items"]
    assert file_schema["additionalProperties"] is False
    assert file_schema["required"] == [
        "file_path",
        "match_count",
        "truncated",
        "excerpts",
    ]


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


def test_search_course_file_returns_result_and_uses_defaults(monkeypatch, tmp_path):
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
    assert result == {
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


def test_search_course_returns_result_and_uses_defaults(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)
    fake_service = FakeCourseService()
    monkeypatch.setattr(server, "course_service", fake_service)

    result = asyncio.run(
        server.handle_call_tool(
            "search-course",
            {"course_title": "CMSC430", "keyword": "compile"},
        )
    )

    assert fake_service.course_search_arguments == (
        "CMSC430",
        "compile",
        3,
        20,
    )
    assert result == {
        "course_title": "CMSC430",
        "keyword": "compile",
        "matching_file_count": 0,
        "match_count": 0,
        "files": [],
    }


@pytest.mark.parametrize("missing_argument", ["course_title", "keyword"])
def test_search_course_requires_arguments(monkeypatch, tmp_path, missing_argument):
    server = load_server(monkeypatch, tmp_path)
    arguments = {"course_title": "CMSC430", "keyword": "compile"}
    arguments.pop(missing_argument)

    with pytest.raises(
        ValueError,
        match=f"Missing required argument: {missing_argument}",
    ):
        asyncio.run(server.handle_call_tool("search-course", arguments))


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected"),
    [
        (
            "search-course-file",
            {
                "course_title": "CMSC132",
                "file_path": "notes.txt",
                "keyword": "recursion",
            },
            {
                "course_title": "CMSC132",
                "file_path": "notes.txt",
                "keyword": "recursion",
                "match_count": 0,
                "truncated": False,
                "excerpts": [],
            },
        ),
        (
            "search-course",
            {"course_title": "CMSC132", "keyword": "recursion"},
            {
                "course_title": "CMSC132",
                "keyword": "recursion",
                "matching_file_count": 0,
                "match_count": 0,
                "files": [],
            },
        ),
    ],
)
def test_registered_search_tools_return_structured_and_compatibility_content(
    monkeypatch,
    tmp_path,
    tool_name,
    arguments,
    expected,
):
    server = load_server(monkeypatch, tmp_path)
    monkeypatch.setattr(server, "course_service", FakeCourseService())

    result = call_registered_tool(server, tool_name, arguments)

    assert result.isError is False
    assert result.structuredContent == expected
    assert len(result.content) == 1
    assert isinstance(result.content[0], types.TextContent)
    assert json.loads(result.content[0].text) == expected


def test_registered_search_tool_reports_input_validation_errors(
    monkeypatch,
    tmp_path,
):
    server = load_server(monkeypatch, tmp_path)

    result = call_registered_tool(
        server,
        "search-course-file",
        {"course_title": "CMSC132", "keyword": "recursion"},
    )

    assert result.isError is True
    assert result.structuredContent is None
    assert "Input validation error" in result.content[0].text
    assert "file_path" in result.content[0].text


def test_registered_search_tool_reports_service_errors(monkeypatch, tmp_path):
    server = load_server(monkeypatch, tmp_path)
    fake_service = FakeCourseService()

    def fail_search(*args):
        raise ValueError("Course is not available")

    fake_service.search_file = fail_search
    monkeypatch.setattr(server, "course_service", fake_service)

    result = call_registered_tool(
        server,
        "search-course-file",
        {
            "course_title": "CMSC999",
            "file_path": "notes.txt",
            "keyword": "recursion",
        },
    )

    assert result.isError is True
    assert result.structuredContent is None
    assert result.content[0].text == "Course is not available"


def test_registered_search_tool_rejects_invalid_structured_output(
    monkeypatch,
    tmp_path,
):
    server = load_server(monkeypatch, tmp_path)
    fake_service = FakeCourseService()

    def malformed_search(*args):
        return {"course_title": "CMSC132"}

    fake_service.search_file = malformed_search
    monkeypatch.setattr(server, "course_service", fake_service)

    result = call_registered_tool(
        server,
        "search-course-file",
        {
            "course_title": "CMSC132",
            "file_path": "notes.txt",
            "keyword": "recursion",
        },
    )

    assert result.isError is True
    assert result.structuredContent is None
    assert "Output validation error" in result.content[0].text
