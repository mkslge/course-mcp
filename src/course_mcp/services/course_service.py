from typing import Protocol


class FileService(Protocol):
    def list_dirs(self, relative_path: str = "") -> list[str]:
        pass

    def list_files(self, relative_path: str = "") -> list[str]:
        pass


class CourseService:
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def get_courses(self) -> list[str]:
        return self.file_service.list_dirs()

    def get_files(self, course_title: str) -> list[str]:
        return self.file_service.list_files(course_title)


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
