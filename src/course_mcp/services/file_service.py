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

    def _resolve_directory(self, relative_path: str) -> Path:
        path = self.resolve_path(relative_path)

        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {relative_path}")

        return path

    def _relative_path(self, path: Path) -> str:
        return path.relative_to(self.root_dir).as_posix()

    def list_files(self, relative_path: str = "") -> list[str]:
        directory = self._resolve_directory(relative_path)

        return sorted(
            self._relative_path(path)
            for path in directory.iterdir()
            if path.is_file()
        )

    def list_dirs(self, relative_path: str = "") -> list[str]:
        directory = self._resolve_directory(relative_path)

        return sorted(
            self._relative_path(path)
            for path in directory.iterdir()
            if path.is_dir()
        )

    def get_contents(
        self,
        relative_path: str,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> str:
        path = self.resolve_path(relative_path)

        if start_line is None and end_line is None:
            return path.read_text()

        lines = path.read_text().splitlines(keepends=True)
        start_index = 0 if start_line is None else max(start_line - 1, 0)
        end_index = None if end_line is None else end_line

        return "".join(lines[start_index:end_index])


file_service = FileService(ROOT_DIR)


def get_contents(
    relative_path: str,
    start_line: int | None = None,
    end_line: int | None = None,
) -> str:
    return file_service.get_contents(relative_path, start_line, end_line)


def list_files(relative_path: str = "") -> list[str]:
    return file_service.list_files(relative_path)


def list_dirs(relative_path: str = "") -> list[str]:
    return file_service.list_dirs(relative_path)
