from typing import Any, Protocol


class FileService(Protocol):
    def list_dirs(self, relative_path: str = "") -> list[str]:
        """Return direct child directories beneath a relative path."""
        pass

    def list_files(self, relative_path: str = "") -> list[str]:
        """Return direct child files beneath a relative path."""
        pass

    def search_file(
        self,
        course_title: str,
        file_path: str,
        keyword: str,
        context_lines: int = 3,
        max_results: int = 20,
    ) -> dict[str, Any]:
        """Search one file within a course and return structured excerpts."""
        pass

    def search_course(
        self,
        course_title: str,
        keyword: str,
        context_lines: int = 3,
        max_results: int = 20,
    ) -> dict[str, Any]:
        """Search eligible files recursively within one course."""
        pass


class CourseService:
    def __init__(self, file_service: FileService):
        """Create a course service backed by an injected filesystem service."""
        self.file_service = file_service

    def get_courses(self) -> list[str]:
        """Return the configured top-level course directories."""
        return self.file_service.list_dirs()

    def get_files(self, course_title: str) -> list[str]:
        """Return the direct child files belonging to a course."""
        return self.file_service.list_files(course_title)

    def search_file(
        self,
        course_title: str,
        file_path: str,
        keyword: str,
        context_lines: int = 3,
        max_results: int = 20,
    ) -> dict[str, Any]:
        """Search a selected course file using the filesystem service."""
        return self.file_service.search_file(
            course_title,
            file_path,
            keyword,
            context_lines,
            max_results,
        )

    def search_course(
        self,
        course_title: str,
        keyword: str,
        context_lines: int = 3,
        max_results: int = 20,
    ) -> dict[str, Any]:
        """Search a course recursively using the filesystem service."""
        return self.file_service.search_course(
            course_title,
            keyword,
            context_lines,
            max_results,
        )


course_service: CourseService | None = None


def get_course_service() -> CourseService:
    """Return the lazily initialized module-level course service."""
    global course_service

    if course_service is None:
        # Delay config-backed filesystem creation until this facade is requested.
        from course_mcp.services.file_service import file_service

        course_service = CourseService(file_service)

    return course_service


def get_courses() -> list[str]:
    """Return courses through the module-level course service."""
    return get_course_service().get_courses()


def get_files(course_title: str) -> list[str]:
    """Return course files through the module-level course service."""
    return get_course_service().get_files(course_title)


def search_file(
    course_title: str,
    file_path: str,
    keyword: str,
    context_lines: int = 3,
    max_results: int = 20,
) -> dict[str, Any]:
    """Search a course file through the module-level course service."""
    return get_course_service().search_file(
        course_title,
        file_path,
        keyword,
        context_lines,
        max_results,
    )


def search_course(
    course_title: str,
    keyword: str,
    context_lines: int = 3,
    max_results: int = 20,
) -> dict[str, Any]:
    """Search a course recursively through the module-level service."""
    return get_course_service().search_course(
        course_title,
        keyword,
        context_lines,
        max_results,
    )
