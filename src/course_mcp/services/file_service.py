
from pathlib import Path

from course_mcp.config import ROOT_DIR


class FileService:

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()

    def resolve_path(self, relative_path: str) -> Path:
        path = (self.root_dir / relative_path).resolve()

        if not path.is_relative_to(self.root_dir):
            raise ValueError(f"Path is outside ROOT_DIR: {relative_path}")

        return path

    def get_contents(
        self,
        relative_path: str,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> str:
        path = self.resolve_path(relative_path)

        # read whole file
        if start_line is None and end_line is None:
            return path.read_text()

        #otherwise file into lines 
        lines = path.read_text().splitlines(keepends=True)
        start_index = 0 if start_line is None else max(start_line - 1, 0)
        end_index = None if end_line is None else end_line

        #get only those lines
        return "".join(lines[start_index:end_index])


file_service = FileService(ROOT_DIR)


def get_contents(
    relative_path: str,
    start_line: int | None = None,
    end_line: int | None = None,
) -> str:
    return file_service.get_contents(relative_path, start_line, end_line)
