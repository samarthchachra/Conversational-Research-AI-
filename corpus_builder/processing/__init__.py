"""Text preprocessing for the offline corpus builder.

Cleans raw PDF text before chunking and embedding. Identical logic to the
backend preprocessing_service.py but with no dependency on the backend app.
"""

from __future__ import annotations

import re


class Preprocessing:
    """Static text cleaning pipeline for raw research-paper PDF text."""

    @staticmethod
    def preprocess(text: str) -> str:
        """Run the full cleaning pipeline on raw PDF text."""
        text = Preprocessing.normalize_unicode(text)
        text = Preprocessing.fix_hyphenation(text)
        text = Preprocessing.remove_headers(text)
        text = Preprocessing.remove_page_numbers(text)
        text = Preprocessing.remove_figure_captions(text)
        text = Preprocessing.remove_table_captions(text)
        text = Preprocessing.remove_inline_citations(text)
        text = Preprocessing.remove_references(text)
        text = Preprocessing.remove_extra_whitespace(text)
        return text

    @staticmethod
    def normalize_unicode(text: str) -> str:
        replacements = {
            "\ufffe": " ",
            "\ufb01": "fi",
            "\ufb02": "fl",
            "\u2014": "-",
            "\u2013": "-",
            "\u201c": '"',
            "\u201d": '"',
            "\u2019": "'",
            "\u00a0": " ",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    @staticmethod
    def fix_hyphenation(text: str) -> str:
        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
        text = re.sub(r"(\w)\s*\n\s*(\w)", r"\1 \2", text)
        return text

    @staticmethod
    def remove_headers(text: str) -> str:
        lines = []
        for line in text.split("\n"):
            if len(line.strip()) < 4:
                continue
            if "arXiv:" in line:
                continue
            lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def remove_page_numbers(text: str) -> str:
        return re.sub(r"\n\s*\d+\s*\n", "\n", text)

    @staticmethod
    def remove_figure_captions(text: str) -> str:
        return re.sub(
            r"Figure\s+\d+[:.]?.*?(?=\n[A-Z]|\Z)",
            "",
            text,
            flags=re.DOTALL,
        )

    @staticmethod
    def remove_table_captions(text: str) -> str:
        return re.sub(
            r"Table\s+\d+[:.]?.*?(?=\n[A-Z]|\Z)",
            "",
            text,
            flags=re.DOTALL,
        )

    @staticmethod
    def remove_inline_citations(text: str) -> str:
        return re.sub(r"\([A-Za-z].*?\d{4}[a-z]?\)", "", text)

    @staticmethod
    def remove_references(text: str) -> str:
        lower = text.lower()
        for marker in ("references", "bibliography"):
            idx = lower.find(marker)
            if idx != -1:
                return text[:idx]
        return text

    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
