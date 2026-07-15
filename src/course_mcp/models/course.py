from dataclasses import dataclass


@dataclass(frozen=True)
class Course:
    def __init__(self, title):
        """Store the title that identifies a course."""
        self.title = title
