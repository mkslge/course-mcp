

from os import path

from course_mcp.config import ROOT_DIR
from pathlib import Path

class CourseService:
    def __init__(self):
        self.directory = Path(ROOT_DIR)
        None

    def get_courses():
        classes = [course for course in self.directory.iterdir()] 
        return classes

    
    def get_files(course : str ) -> List[str]:
        