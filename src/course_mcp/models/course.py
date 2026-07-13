from dataclasses import dataclass


@dataclass(frozen=True)
class Course:
    def __init__(self, title):
        self.title = title
    