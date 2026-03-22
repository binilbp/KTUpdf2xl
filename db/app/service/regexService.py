from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.app.db.models.user import Scheme, RegexPattern


class RegexService:
    REQUIRED_PATTERNS = [
        "main_title_marker",
        "department_split_marker",
        "course_code_regex",
        "course_code_name_regex",
        "student_id_pattern",
        "arrear_pattern",
        "debarred_pattern",
    ]

    def __init__(self, session: Session):
        self.session = session

    def get_scheme_by_name(self, scheme_name: str) -> Scheme:
        scheme = (
            self.session.query(Scheme)
            .filter(Scheme.name == scheme_name)
            .first()
        )

        if not scheme:
            raise HTTPException(
                status_code=404,
                detail=f"Scheme '{scheme_name}' not found"
            )

        return scheme

    def get_patterns_by_scheme(self, scheme_name: str) -> dict:
        rows = (
            self.session.query(RegexPattern)
            .join(Scheme, Scheme.id == RegexPattern.scheme_id)
            .filter(Scheme.name == scheme_name)
            .all()
        )

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No regex patterns found for scheme '{scheme_name}'"
            )

        pattern_dict = {row.name: row.pattern for row in rows}
        self.validate_patterns(pattern_dict)
        return pattern_dict

    def get_pattern_rows_by_scheme(self, scheme_name: str):
        scheme = self.get_scheme_by_name(scheme_name)

        rows = (
            self.session.query(RegexPattern)
            .filter(RegexPattern.scheme_id == scheme.id)
            .all()
        )

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No regex patterns found for scheme '{scheme_name}'"
            )

        return rows

    def validate_patterns(self, pattern_dict: dict):
        missing = [key for key in self.REQUIRED_PATTERNS if key not in pattern_dict]
        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Missing regex patterns for scheme: {missing}"
            )