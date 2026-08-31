import re


def preprocess_text(text: str):

    text = remove_references(text)

    text = remove_extra_whitespace(text)

    return text


def remove_extra_whitespace(text: str):

    text = text.replace("\n", " ")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def remove_references(text: str):

    markers = [
        "references",
        "bibliography"
    ]

    lower_text = text.lower()

    for marker in markers:

        if marker in lower_text:

            index = lower_text.find(marker)

            return text[:index]

    return text