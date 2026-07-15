from typing import Any, Protocol


class FileService(Protocol):
    def list_dirs(self, relative_path: str = "") -> list[str]:
        pass

    def list_files(self, relative_path: str = "") -> list[str]:
        pass

    def search_file(
        self,
        course_title: str,
        file_path: str,
        keyword: str,
        context_lines: int = 3,
        max_results: int = 20,
    ) -> dict[str, Any]:
        pass


class CourseService:
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def get_courses(self) -> list[str]:
        return self.file_service.list_dirs()

    def get_files(self, course_title: str) -> list[str]:
        return self.file_service.list_files(course_title)

    def search_file(
        self,
        course_title: str,
        file_path: str,
        keyword: str,
        context_lines: int = 3,
        max_results: int = 20,
    ) -> dict[str, Any]:
        return self.file_service.search_file(
            course_title,
            file_path,
            keyword,
            context_lines,
            max_results,
        )


course_service: CourseService | None = None


def get_course_service() -> CourseService:
    global course_service

    if course_service is None:
        from course_mcp.services.file_service import file_service

        course_service = CourseService(file_service)

    return course_service


def get_courses() -> list[str]:
    return get_course_service().get_courses()


def get_files(course_title: str) -> list[str]:
    return get_course_service().get_files(course_title)


def search_file(
    course_title: str,
    file_path: str,
    keyword: str,
    context_lines: int = 3,
    max_results: int = 20,
) -> dict[str, Any]:
    return get_course_service().search_file(
        course_title,
        file_path,
        keyword,
        context_lines,
        max_results,
    )
