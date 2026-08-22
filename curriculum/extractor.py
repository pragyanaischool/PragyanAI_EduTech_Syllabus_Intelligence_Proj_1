# ============================================================
# curriculum/extractor.py
# CHUNK 1/8
#
# AI CURRICULUM INTELLIGENCE PLATFORM
#
# PURPOSE
# -------
# Extract a complete structured curriculum from:
#
#   PDF
#   DOCX
#   OCR text
#   Plain text
#
# using:
#
#   Groq
#   Llama
#   Pydantic
#
# OUTPUT
# ------
# curriculum.models.Curriculum
#
# The extractor is intentionally independent from Streamlit.
# Streamlit pages should call this module rather than putting
# extraction logic directly inside the UI.
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

from __future__ import annotations


import json

import logging

import os

import re

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)


# ============================================================
# 2. PYDANTIC / MODELS
# ============================================================

from pydantic import (
    ValidationError,
)


from curriculum.models import (

    Curriculum,

    CourseMetadata,

    CourseObjective,

    CourseOutcome,

    ProgramOutcome,

    ProgramSpecificOutcome,

    Module,

    Topic,

    Concept,

    Skill,

    Tool,

    Technology,

    Project,

    BloomLevel,

    DifficultyLevel,

    LearningType,

    SkillCategory,

    ConceptType,

    CurriculumStatistics,

    build_validation_report,

    calculate_curriculum_statistics,

)


# ============================================================
# 3. LOGGING
# ============================================================

logger = logging.getLogger(
    __name__
)


if not logger.handlers:

    logging.basicConfig(

        level=logging.INFO,

        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),

    )


# ============================================================
# 4. CONSTANTS
# ============================================================

DEFAULT_MODEL = os.getenv(

    "GROQ_MODEL",

    "llama-3.3-70b-versatile",

)


DEFAULT_TEMPERATURE = float(

    os.getenv(

        "GROQ_TEMPERATURE",

        "0.1",

    )

)


DEFAULT_MAX_TOKENS = int(

    os.getenv(

        "GROQ_MAX_TOKENS",

        "16000",

    )

)


DEFAULT_MAX_INPUT_CHARS = int(

    os.getenv(

        "CURRICULUM_MAX_INPUT_CHARS",

        "120000",

    )

)


DEFAULT_BATCH_SIZE = int(

    os.getenv(

        "CURRICULUM_BATCH_SIZE",

        "12000",

    )

)


# ============================================================
# 5. EXTRACTION VERSION
# ============================================================

EXTRACTOR_VERSION = "1.0.0"


# ============================================================
# 6. LOGGER HELPER
# ============================================================

def log_info(
    message: str,
) -> None:
    """
    Log an informational message.
    """

    logger.info(
        message
    )


def log_warning(
    message: str,
) -> None:
    """
    Log a warning.
    """

    logger.warning(
        message
    )


def log_error(
    message: str,
) -> None:
    """
    Log an error.
    """

    logger.error(
        message
    )


# ============================================================
# 7. STRING UTILITIES
# ============================================================

def clean_text(
    value: Any,
) -> str:
    """
    Convert arbitrary input into clean text.
    """

    if value is None:

        return ""


    text = str(
        value
    )


    text = text.replace(
        "\x00",
        " ",
    )


    text = text.replace(
        "\r\n",
        "\n",
    )


    text = text.replace(
        "\r",
        "\n",
    )


    # Remove excessive spaces

    text = re.sub(

        r"[ \t]+",

        " ",

        text,

    )


    # Remove excessive blank lines

    text = re.sub(

        r"\n{3,}",

        "\n\n",

        text,

    )


    return text.strip()


# ============================================================
# 8. STRING LIST NORMALIZER
# ============================================================

def clean_string_list(
    values: Any,
) -> List[str]:
    """
    Convert arbitrary values into a clean unique list.
    """

    if values is None:

        return []


    if isinstance(
        values,
        str,
    ):

        values = re.split(

            r"[,;\n|]",

            values,

        )


    if not isinstance(
        values,
        list,
    ):

        values = [values]


    result: List[str] = []

    seen = set()


    for value in values:

        if value is None:

            continue


        text = clean_text(
            value
        )


        if not text:

            continue


        key = text.lower()


        if key in seen:

            continue


        seen.add(
            key
        )


        result.append(
            text
        )


    return result


# ============================================================
# 9. SAFE FLOAT
# ============================================================

def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.
    """

    if value is None:

        return default


    if isinstance(
        value,
        bool,
    ):

        return float(
            value
        )


    try:

        if isinstance(
            value,
            str,
        ):

            value = (

                value

                .replace(
                    "%",
                    "",
                )

                .replace(
                    ",",
                    "",
                )

                .strip()

            )


        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# 10. SAFE INT
# ============================================================

def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Safely convert a value to integer.
    """

    try:

        return int(
            float(
                value
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# 11. CLAMP SCORE
# ============================================================

def clamp_score(
    value: Any,
) -> float:
    """
    Normalize score to 0-100.
    """

    score = safe_float(
        value
    )


    return max(

        0.0,

        min(
            100.0,
            score,
        ),

    )


# ============================================================
# 12. NORMALIZE ENUM
# ============================================================

def normalize_enum_value(
    value: Any,
    allowed_values: List[str],
    default: str,
) -> str:
    """
    Normalize an LLM-generated enum value.

    Example:

        "advanced level"
            →
        "Advanced"
    """

    if value is None:

        return default


    text = clean_text(
        value
    )


    if not text:

        return default


    normalized = text.lower()


    for allowed in allowed_values:

        if normalized == allowed.lower():

            return allowed


    for allowed in allowed_values:

        if allowed.lower() in normalized:

            return allowed


    return default


# ============================================================
# 13. JSON STRING CLEANER
# ============================================================

def strip_markdown_json(
    text: str,
) -> str:
    """
    Remove markdown JSON fences from LLM output.
    """

    text = clean_text(
        text
    )


    if text.startswith(
        "```json"
    ):

        text = text[
            7:
        ]


    elif text.startswith(
        "```"
    ):

        text = text[
            3:
        ]


    if text.endswith(
        "```"
    ):

        text = text[
            :-3
        ]


    return text.strip()


# ============================================================
# 14. EXTRACT JSON OBJECT
# ============================================================

def extract_json_object(
    text: str,
) -> Optional[Dict[str, Any]]:
    """
    Extract the first valid JSON object from arbitrary text.
    """

    if not text:

        return None


    cleaned = strip_markdown_json(
        text
    )


    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:

        parsed = json.loads(
            cleaned
        )


        if isinstance(
            parsed,
            dict,
        ):

            return parsed

    except json.JSONDecodeError:

        pass


    # --------------------------------------------------------
    # Locate JSON object boundaries
    # --------------------------------------------------------

    start = cleaned.find(
        "{"
    )


    end = cleaned.rfind(
        "}"
    )


    if start == -1 or end == -1:

        return None


    candidate = cleaned[
        start:
        end + 1
    ]


    try:

        parsed = json.loads(
            candidate
        )


        if isinstance(
            parsed,
            dict,
        ):

            return parsed

    except json.JSONDecodeError:

        pass


    # --------------------------------------------------------
    # Attempt common JSON cleanup
    # --------------------------------------------------------

    candidate = re.sub(

        r",\s*}",

        "}",

        candidate,

    )


    candidate = re.sub(

        r",\s*]",

        "]",

        candidate,

    )


    try:

        parsed = json.loads(
            candidate
        )


        if isinstance(
            parsed,
            dict,
        ):

            return parsed

    except json.JSONDecodeError:

        return None


    return None


# ============================================================
# 15. INPUT TEXT PREPARATION
# ============================================================

def prepare_input_text(
    text: str,
    max_chars: int = DEFAULT_MAX_INPUT_CHARS,
) -> str:
    """
    Clean and safely truncate source text.

    The extractor intentionally keeps this function
    deterministic. More advanced document chunking can
    be handled by rag/chunker.py.
    """

    text = clean_text(
        text
    )


    if not text:

        raise ValueError(
            "No syllabus text was provided."
        )


    if len(text) <= max_chars:

        return text


    log_warning(

        (
            "Syllabus text exceeded "
            f"{max_chars} characters. "
            "Input was truncated."
        )

    )


    return text[
        :max_chars
    ]


# ============================================================
# 16. SOURCE TYPE DETECTION
# ============================================================

def detect_source_type(
    filename: Optional[str] = None,
    source_type: Optional[str] = None,
) -> str:
    """
    Determine source document type.
    """

    if source_type:

        return clean_text(
            source_type
        ).lower()


    if not filename:

        return "text"


    extension = os.path.splitext(
        filename
    )[1].lower()


    mapping = {

        ".pdf":
            "pdf",

        ".docx":
            "docx",

        ".doc":
            "doc",

        ".png":
            "image",

        ".jpg":
            "image",

        ".jpeg":
            "image",

        ".tiff":
            "image",

        ".txt":
            "text",

        ".md":
            "text",

    }


    return mapping.get(

        extension,

        "unknown",

    )


# ============================================================
# 17. TEXT STATISTICS
# ============================================================

def get_text_statistics(
    text: str,
) -> Dict[str, int]:
    """
    Calculate basic source text statistics.
    """

    cleaned = clean_text(
        text
    )


    words = (

        cleaned.split()

        if cleaned

        else []

    )


    lines = [

        line

        for line in cleaned.split(
            "\n"
        )

        if line.strip()

    ]


    return {

        "characters":
            len(cleaned),

        "words":
            len(words),

        "lines":
            len(lines),

        "paragraphs":
            len(

                [

                    p

                    for p in cleaned.split(
                        "\n\n"
                    )

                    if p.strip()

                ]

            ),

    }


# ============================================================
# 18. DOCUMENT SECTION DETECTION
# ============================================================

def detect_sections(
    text: str,
) -> List[str]:
    """
    Detect likely syllabus section headings.

    This is a lightweight preprocessing step.
    """

    sections = []

    lines = text.split(
        "\n"
    )


    heading_patterns = [

        r"^(unit|module|chapter)\s*[-:]?\s*\d+",

        r"^(course\s+outcomes?)",

        r"^(program\s+outcomes?)",

        r"^(program\s+specific\s+outcomes?)",

        r"^(objectives?)",

        r"^(syllabus)",

        r"^(prerequisites?)",

        r"^(reference|references)",

        r"^(textbook|textbooks)",

        r"^(assessment)",

        r"^(course\s+contents?)",

        r"^(contents?)",

    ]


    compiled = [

        re.compile(
            pattern,
            re.IGNORECASE,
        )

        for pattern in heading_patterns

    ]


    for line in lines:

        candidate = clean_text(
            line
        )


        if not candidate:

            continue


        for pattern in compiled:

            if pattern.search(
                candidate
            ):

                sections.append(
                    candidate
                )

                break


    return clean_string_list(
        sections
    )


# ============================================================
# 19. CHUNK TEXT
# ============================================================

def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_BATCH_SIZE,
    overlap: int = 500,
) -> List[str]:
    """
    Split text into overlapping chunks.

    This is a fallback utility.

    For production RAG ingestion, use:
        rag/chunker.py
    """

    text = clean_text(
        text
    )


    if not text:

        return []


    if chunk_size <= 0:

        raise ValueError(
            "chunk_size must be greater than zero."
        )


    if overlap < 0:

        overlap = 0


    if overlap >= chunk_size:

        overlap = chunk_size // 10


    chunks = []

    start = 0

    text_length = len(
        text
    )


    while start < text_length:

        end = min(

            start + chunk_size,

            text_length,

        )


        chunk = text[
            start:end
        ].strip()


        if chunk:

            chunks.append(
                chunk
            )


        if end >= text_length:

            break


        start = end - overlap


    return chunks


# ============================================================
# 20. DEFAULT CURRICULUM
# ============================================================

def create_empty_curriculum(
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Curriculum:
    """
    Create an empty but valid Curriculum object.
    """

    metadata = CourseMetadata(

        source_file=source_file,

        source_type=source_type,

    )


    return Curriculum(

        metadata=metadata,

        modules=[],

        concepts=[],

        skills=[],

        tools=[],

        technologies=[],

        projects=[],

    )


# ============================================================
# END OF CHUNK 1
# ============================================================
