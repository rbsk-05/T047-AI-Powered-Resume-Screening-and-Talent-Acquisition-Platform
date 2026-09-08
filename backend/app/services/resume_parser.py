"""Backward-compatibility facade for app.services.resume_parser.

Delegates all functionality to the modular app.resume package.
"""

from app.resume.parser import ResumeParser
from app.resume.regex_extractor import RegexExtractor
from app.resume.section_detector import SectionDetector

_SKILLS = RegexExtractor.SKILLS
_SECTION_TITLES = SectionDetector.SECTION_TITLES

__all__ = [
    "ResumeParser",
    "_SKILLS",
    "_SECTION_TITLES",
]
