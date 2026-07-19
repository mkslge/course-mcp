_SEARCH_LINE_SCHEMA = {
    "type": "object",
    "properties": {
        "line_number": {"type": "integer", "minimum": 1},
        "text": {"type": "string"},
    },
    "required": ["line_number", "text"],
    "additionalProperties": False,
}

_SEARCH_EXCERPT_SCHEMA = {
    "type": "object",
    "properties": {
        "page": {"type": "integer", "minimum": 1},
        "start_line": {"type": "integer", "minimum": 1},
        "end_line": {"type": "integer", "minimum": 1},
        "match_lines": {
            "type": "array",
            "items": {"type": "integer", "minimum": 1},
        },
        "lines": {
            "type": "array",
            "items": _SEARCH_LINE_SCHEMA,
        },
    },
    "required": ["start_line", "end_line", "match_lines", "lines"],
    "additionalProperties": False,
}

_SEARCH_FILE_RESULT_PROPERTIES = {
    "file_path": {"type": "string"},
    "match_count": {"type": "integer", "minimum": 0},
    "truncated": {"type": "boolean"},
    "excerpts": {
        "type": "array",
        "items": _SEARCH_EXCERPT_SCHEMA,
    },
}

_SEARCH_FILE_RESULT_SCHEMA = {
    "type": "object",
    "properties": _SEARCH_FILE_RESULT_PROPERTIES,
    "required": ["file_path", "match_count", "truncated", "excerpts"],
    "additionalProperties": False,
}

SEARCH_COURSE_FILE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "course_title": {"type": "string"},
        "keyword": {"type": "string"},
        **_SEARCH_FILE_RESULT_PROPERTIES,
    },
    "required": [
        "course_title",
        "file_path",
        "keyword",
        "match_count",
        "truncated",
        "excerpts",
    ],
    "additionalProperties": False,
}

SEARCH_COURSE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "course_title": {"type": "string"},
        "keyword": {"type": "string"},
        "matching_file_count": {"type": "integer", "minimum": 0},
        "match_count": {"type": "integer", "minimum": 0},
        "files": {
            "type": "array",
            "items": _SEARCH_FILE_RESULT_SCHEMA,
        },
    },
    "required": [
        "course_title",
        "keyword",
        "matching_file_count",
        "match_count",
        "files",
    ],
    "additionalProperties": False,
}
