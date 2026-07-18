import re


class Processing:

    @staticmethod
    def preprocess_text(text: str):

        text = Processing.normalize_unicode(text)

        text = Processing.fix_hyphenation(text)

        text = Processing.remove_headers(text)

        text = Processing.remove_page_numbers(text)

        text = Processing.remove_figure_captions(text)

        text = Processing.remove_table_captions(text)

        text = Processing.remove_inline_citations(text)

        text = Processing.remove_references(text)

        text = Processing.remove_extra_whitespace(text)

        return text
    
    @staticmethod
    def normalize_unicode(text):

        replacements = {

            "￾": " ",

            "ﬁ": "fi",

            "ﬂ": "fl",

            "—": "-",

            "–": "-",

            "“": '"',

            "”": '"',

            "’": "'",

            "\u00a0": " "

        }

        for old, new in replacements.items():

            text = text.replace(old, new)

        return text
    
    @staticmethod
    def fix_hyphenation(text):

        text = re.sub(
            r"(\w)-\s*\n\s*(\w)",
            r"\1\2",
            text
        )

        text = re.sub(
            r"(\w)\s*\n\s*(\w)",
            r"\1 \2",
            text
        )

        return text
    
    @staticmethod
    def remove_headers(text):

        lines = []

        for line in text.split("\n"):

            if len(line.strip()) < 4:

                continue

            if "arXiv:" in line:

                continue

            lines.append(line)

        return "\n".join(lines)
    
    @staticmethod
    def remove_page_numbers(text):

        return re.sub(
            r"\n\s*\d+\s*\n",
            "\n",
            text
        )
    
    @staticmethod
    def remove_figure_captions(text):

        return re.sub(

            r"Figure\s+\d+[:.]?.*?(?=\n[A-Z]|\Z)",

            "",

            text,

            flags=re.DOTALL
        )
    
    @staticmethod
    def remove_table_captions(text):

        return re.sub(

            r"Table\s+\d+[:.]?.*?(?=\n[A-Z]|\Z)",

            "",

            text,

            flags=re.DOTALL
        )
    
    @staticmethod
    def remove_inline_citations(text):

        return re.sub(

            r"\([A-Za-z].*?\d{4}[a-z]?\)",

            "",

            text
        )

    @staticmethod
    def remove_references(text):

        markers = [

            "references",

            "bibliography"

        ]

        lower = text.lower()

        for marker in markers:

            idx = lower.find(marker)

            if idx != -1:

                return text[:idx]

        return text
    
    @staticmethod
    def remove_extra_whitespace(text):

        text = text.replace("\n", " ")

        text = re.sub(

            r"\s+",

            " ",

            text

        )

        return text.strip()
    
    