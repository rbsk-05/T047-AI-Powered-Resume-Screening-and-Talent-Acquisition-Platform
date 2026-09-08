"""Experience calculation engine.

Parses date ranges, handles month formats, present/current jobs, merges overlapping intervals,
and calculates unique total experience duration in years without double-counting.
"""

from datetime import datetime
import re

from app.resume.schemas import WorkExperience

_MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9, "sept": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


class ExperienceCalculator:
    """Non-overlapping experience duration calculator."""

    @classmethod
    def parse_month_year(cls, text: str, is_end: bool = False) -> tuple[int, int] | None:
        """Parse a month-year fragment into (year, month)."""
        if not text:
            return None
        text_clean = text.strip().lower()

        if text_clean in ("present", "current", "now", "till date"):
            now = datetime.now()
            return now.year, now.month

        # Try Month YYYY (e.g. "MAR 2026", "Aug 2024", "03/2026", "2026-03")
        m_ym = re.search(r"([a-z]{3,9})\s+(\d{4})", text_clean)
        if m_ym:
            month_str, year_str = m_ym.group(1), m_ym.group(2)
            month = _MONTH_MAP.get(month_str[:3], 1 if not is_end else 12)
            return int(year_str), month

        # Try YYYY-MM or MM/YYYY
        m_num = re.search(r"(\d{4})[-/](\d{1,2})", text_clean)
        if m_num:
            return int(m_num.group(1)), int(m_num.group(2))
        m_num_rev = re.search(r"(\d{1,2})[-/](\d{4})", text_clean)
        if m_num_rev:
            return int(m_num_rev.group(2)), int(m_num_rev.group(1))

        # Try Year only (e.g. "2026")
        m_y = re.search(r"\b(\d{4})\b", text_clean)
        if m_y:
            year = int(m_y.group(1))
            month = 12 if is_end else 1
            return year, month

        return None

    @classmethod
    def parse_date_range(cls, duration_str: str) -> tuple[tuple[int, int], tuple[int, int]] | None:
        """Parse a range string like 'MAR 2026 - OCT 2026' or 'DEVS - Designer | AUG 2024 - SEP 2025'."""
        if not duration_str:
            return None

        # Regex search for date range pattern inside text
        range_match = re.search(
            r"((?:[A-Za-z]{3,9}\s+)?\d{4})\s*[-–]\s*((?:[A-Za-z]{3,9}\s+)?(?:\d{4}|Present|Current|Now))",
            duration_str,
            re.IGNORECASE,
        )
        if range_match:
            start_parsed = cls.parse_month_year(range_match.group(1), is_end=False)
            end_parsed = cls.parse_month_year(range_match.group(2), is_end=True)
            if start_parsed and end_parsed:
                return start_parsed, end_parsed

        # Fallback: split by separator
        parts = re.split(r"\s*(?:[-–]|to)\s*", duration_str, maxsplit=1)
        if len(parts) == 2:
            start_parsed = cls.parse_month_year(parts[0], is_end=False)
            end_parsed = cls.parse_month_year(parts[1], is_end=True)
            if start_parsed and end_parsed:
                return start_parsed, end_parsed

        single_start = cls.parse_month_year(duration_str, is_end=False)
        if single_start:
            return single_start, single_start
        return None

    @classmethod
    def calculate_total_experience_years(cls, experiences: list[WorkExperience]) -> float:
        """Calculate unique, non-overlapping work experience in years."""
        intervals: list[tuple[int, int]] = []

        for exp in experiences:
            date_range = None
            if exp.start_date and exp.end_date:
                s = cls.parse_month_year(exp.start_date, is_end=False)
                e = cls.parse_month_year(exp.end_date, is_end=True)
                if s and e:
                    date_range = (s, e)
            elif exp.duration_text:
                date_range = cls.parse_date_range(exp.duration_text)

            if date_range:
                (sy, sm), (ey, em) = date_range
                start_idx = sy * 12 + sm
                end_idx = ey * 12 + em
                if end_idx >= start_idx:
                    intervals.append((start_idx, end_idx))

        if not intervals:
            for exp in experiences:
                if exp.duration_text:
                    m = re.search(r"\b(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)", exp.duration_text, re.IGNORECASE)
                    if m:
                        return float(m.group(1))
            return 0.0

        intervals.sort(key=lambda item: item[0])
        merged: list[list[int]] = []
        for start, end in intervals:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        total_months = sum(end - start + 1 for start, end in merged)
        total_years = round(total_months / 12.0, 1)
        return total_years
