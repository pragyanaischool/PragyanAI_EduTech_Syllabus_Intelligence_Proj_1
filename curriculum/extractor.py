"""
PragyanAI Curriculum Intelligence
curriculum/extractor.py

Robust syllabus extraction engine.

Design:
    raw document text
        -> deterministic academic parser
        -> bounded Groq semantic extraction
        -> safe JSON parsing
        -> intelligent merge
        -> validation
        -> normalized curriculum dictionary

The deterministic parser is intentionally authoritative for information
that is explicitly present in the syllabus text: institution metadata,
modules, objectives, prerequisites, CO/PO/PSO, references, tools, etc.

Groq is used for semantic enrichment and for syllabus structures that
cannot be safely recovered with simple patterns.

This module keeps both functional and class-based APIs for compatibility:
    extract_syllabus(...)
    extract_curriculum_from_text(...)
    CurriculumExtractor
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from groq import Groq
except Exception:
    Groq = None


logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)

DEFAULT_TEMPERATURE = float(
    os.getenv("GROQ_TEMPERATURE", "0.1")
)

DEFAULT_MAX_TOKENS = int(
    os.getenv("GROQ_MAX_TOKENS", "1400")
)

DEFAULT_CHUNK_SIZE = int(
    os.getenv("CURRICULUM_CHUNK_SIZE", "2200")
)

DEFAULT_CHUNK_OVERLAP = int(
    os.getenv("CURRICULUM_CHUNK_OVERLAP", "350")
)

DEFAULT_RETRIES = int(
    os.getenv("GROQ_RETRIES", "1")
)

# Groq on-demand TPM can be restrictive. A pause between large
# requests reduces burst pressure. Set to 0 if your tier permits.
DEFAULT_REQUEST_DELAY = float(
    os.getenv("GROQ_REQUEST_DELAY", "2.0")
)


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class ExtractorConfig:
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    retries: int = DEFAULT_RETRIES
    request_delay: float = DEFAULT_REQUEST_DELAY


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_text(value: Any) -> str:
    """Normalize whitespace without destroying meaningful punctuation."""
    if value is None:
        return ""

    text = str(value)
    text = text.replace("\x00", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_string_list(values: Any) -> List[str]:
    """Return a de-duplicated list of meaningful strings."""
    if values is None:
        return []

    if isinstance(values, str):
        values = re.split(r"[\n;]+", values)

    if not isinstance(values, (list, tuple, set)):
        return []

    result: List[str] = []

    for value in values:
        value = clean_text(value)

        value = re.sub(
            r"^[\-\*\u2022\u25CF\d]+[\.\):\-]?\s*",
            "",
            value,
        )

        if not value:
            continue

        if value not in result:
            result.append(value)

    return result


PLACEHOLDER_VALUES = {
    "",
    "unknown",
    "n/a",
    "na",
    "not available",
    "not provided",
    "not specified",
    "none",
    "null",
    "nil",
}


def is_placeholder(value: Any) -> bool:
    """Detect fabricated/generic placeholder values."""
    if value is None:
        return True

    text = clean_text(value).lower()

    if text in PLACEHOLDER_VALUES:
        return True

    if re.fullmatch(
        r"(module|unit|chapter|topic|section)\s*\d+",
        text,
        re.IGNORECASE,
    ):
        return True

    return False


def first_non_empty(*values: Any) -> Any:
    """Return first value that is not empty/placeholder."""
    for value in values:
        if value is None:
            continue

        if isinstance(value, str):
            if not value.strip() or is_placeholder(value):
                continue

        return value

    return None


def unique_dicts(
    items: Iterable[Dict[str, Any]],
    key_fields: Tuple[str, ...],
) -> List[Dict[str, Any]]:
    """De-duplicate dictionaries using selected fields."""
    result: List[Dict[str, Any]] = []
    seen = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        key = tuple(
            clean_text(item.get(field, "")).lower()
            for field in key_fields
        )

        if not any(key):
            continue

        if key in seen:
            continue

        seen.add(key)
        result.append(item)

    return result


# ============================================================
# TEXT / SECTION HELPERS
# ============================================================

def normalize_lines(text: str) -> List[str]:
    """Convert extracted document text to clean logical lines."""
    lines: List[str] = []

    for raw in clean_text(text).split("\n"):
        line = clean_text(raw)

        if not line:
            continue

        lines.append(line)

    return lines


def is_heading(line: str) -> bool:
    """Heuristic academic heading detector."""
    normalized = clean_text(line).lower()

    heading_terms = (
        "course objectives",
        "objectives",
        "prerequisites",
        "course outcomes",
        "course outcome",
        "program outcomes",
        "program specific outcomes",
        "textbooks",
        "reference books",
        "references",
        "online resources",
        "tools",
        "technologies",
        "projects",
        "case studies",
        "assessment",
        "teaching and learning",
        "laboratory",
        "practical",
        "modules and topics",
    )

    if normalized in heading_terms:
        return True

    if normalized.endswith(":"):
        return True

    return False


def section_lines(
    text: str,
    headings: Iterable[str],
) -> List[str]:
    """
    Extract lines following a heading until another major heading.
    """
    lines = normalize_lines(text)

    wanted = {
        clean_text(x).lower()
        for x in headings
    }

    result: List[str] = []
    active = False

    stop_terms = {
        "course objectives",
        "objectives",
        "prerequisites",
        "modules and topics",
        "course outcomes",
        "program outcomes",
        "program specific outcomes",
        "co-po / co-pso mapping",
        "teaching & learning methods",
        "teaching and learning methods",
        "practical / laboratory",
        "assessment pattern",
        "textbooks",
        "reference books",
        "online resources",
        "tools & technologies",
        "tools and technologies",
        "datasets",
        "projects & case studies",
        "projects and case studies",
        "other extracted information",
    }

    for line in lines:
        normalized = line.lower().strip(" :")

        if normalized in wanted:
            active = True
            continue

        if active and normalized in stop_terms and normalized not in wanted:
            break

        if active:
            result.append(line)

    return result


# ============================================================
# LABELED VALUE EXTRACTION
# ============================================================

def extract_labeled_value(
    text: str,
    labels: Iterable[str],
) -> Optional[str]:
    """Extract 'Label: value' from document text."""
    label_list = list(labels)

    for label in label_list:
        pattern = re.compile(
            rf"^\s*{re.escape(label)}\s*[:\-]\s*(.+?)\s*$",
            re.IGNORECASE,
        )

        for line in normalize_lines(text):
            match = pattern.match(line)

            if match:
                value = clean_text(match.group(1))

                if value and not is_placeholder(value):
                    return value

    return None


def extract_numeric_labeled_value(
    text: str,
    labels: Iterable[str],
) -> Optional[float]:
    value = extract_labeled_value(text, labels)

    if value is None:
        return None

    match = re.search(
        r"\d+(?:\.\d+)?",
        value,
    )

    if not match:
        return None

    try:
        return float(match.group(0))
    except Exception:
        return None


# ============================================================
# DOCUMENT METADATA
# ============================================================

def extract_basic_metadata(
    text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Deterministically extract academic metadata.

    This is intentionally done before/alongside LLM extraction so
    explicit values are not lost during chunking.
    """
    lines = normalize_lines(text)
    metadata: Dict[str, Any] = {}

    metadata["university"] = extract_labeled_value(
        text,
        ["University", "University Name"],
    )

    metadata["college"] = extract_labeled_value(
        text,
        ["College", "College Name", "Institute", "Institution"],
    )

    metadata["program"] = extract_labeled_value(
        text,
        ["Program", "Programme", "Degree", "Course"],
    )

    metadata["department"] = extract_labeled_value(
        text,
        ["Department", "Department Name"],
    )

    metadata["semester"] = extract_labeled_value(
        text,
        ["Semester", "Term"],
    )

    metadata["academic_year"] = extract_labeled_value(
        text,
        ["Academic Year", "Academic Session", "Session"],
    )

    metadata["regulation"] = extract_labeled_value(
        text,
        ["Regulation", "Regulation Year", "Scheme"],
    )

    metadata["category"] = extract_labeled_value(
        text,
        ["Category", "Course Category"],
    )

    metadata["subject_name"] = extract_labeled_value(
        text,
        [
            "Subject Name",
            "Subject Title",
            "Subject",
            "Course Title",
            "Course Name",
        ],
    )

    metadata["subject_code"] = extract_labeled_value(
        text,
        [
            "Subject Code",
            "Course Code",
            "Course ID",
            "Subject ID",
            "Course/Subject Code",
            "Code",
        ],
    )

    metadata["credits"] = extract_numeric_labeled_value(
        text,
        ["Credits", "Credit"],
    )

    metadata["contact_hours"] = extract_numeric_labeled_value(
        text,
        [
            "Contact Hours",
            "Teaching Hours",
            "Total Hours",
        ],
    )

    # --------------------------------------------------------
    # Header fallback
    # --------------------------------------------------------

    # Example:
    # Greenfield Institute of Technology
    # B.E. CSE (AI & Machine Learning) — 2025 Scheme
    #
    # Only use fallback if no explicit labels exist.
    if not metadata.get("college") and lines:
        first = lines[0]

        if (
            len(first) >= 4
            and not is_heading(first)
            and not re.match(
                r"^(course metadata|syllabus|curriculum)$",
                first,
                re.IGNORECASE,
            )
        ):
            metadata["college"] = first

    if not metadata.get("program") and len(lines) >= 2:
        second = lines[1]

        if not is_heading(second):
            # The test syllabi use the second line as program/subject title.
            metadata["program"] = second

    # Source information
    if source_file:
        metadata["source_file"] = str(source_file)

    if source_type:
        metadata["source_type"] = str(source_type)

    return metadata


# ============================================================
# MODULE EXTRACTION
# ============================================================

MODULE_PATTERN = re.compile(
    r"""
    ^\s*
    (?:
        module
        |
        unit
        |
        chapter
        |
        section
    )
    \s*
    (?:[-:]?\s*)
    (?P<number>\d+|[IVX]+)
    \s*
    (?:[-:.)]\s*)?
    (?P<name>.*?)
    (?:\s*\((?P<hours>\d+(?:\.\d+)?)\s*hours?\))?
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


def parse_hours(value: Any) -> float:
    if value is None:
        return 0.0

    match = re.search(
        r"\d+(?:\.\d+)?",
        str(value),
    )

    if not match:
        return 0.0

    try:
        return float(match.group(0))
    except Exception:
        return 0.0


def extract_modules_from_text(
    text: str,
) -> List[Dict[str, Any]]:
    """
    Extract explicit module/unit headings.

    Generic names such as 'Module 1' are rejected.
    """
    modules: List[Dict[str, Any]] = []

    for line in normalize_lines(text):
        match = MODULE_PATTERN.match(line)

        if not match:
            continue

        number = clean_text(
            match.group("number")
        )

        name = clean_text(
            match.group("name")
        )

        if is_placeholder(name):
            continue

        # Sometimes regex can capture a trailing separator.
        name = re.sub(
            r"^[\s:.\-]+|[\s:.\-]+$",
            "",
            name,
        )

        if is_placeholder(name):
            continue

        hours = parse_hours(
            match.group("hours")
        )

        modules.append(
            {
                "number": number,
                "name": name,
                "hours": hours,
                "topics": [],
            }
        )

    # If headings are repeated in OCR/text, keep first occurrence.
    return unique_dicts(
        modules,
        ("number", "name"),
    )


# ============================================================
# MODULE TOPIC EXTRACTION
# ============================================================

def extract_topics_by_module(
    text: str,
) -> List[Dict[str, Any]]:
    """
    Deterministically associate bullet/list lines with module headings.
    """
    lines = normalize_lines(text)

    modules: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None

    for line in lines:

        match = MODULE_PATTERN.match(line)

        if match:

            name = clean_text(
                match.group("name")
            )

            if is_placeholder(name):
                current = None
                continue

            current = {
                "number": clean_text(
                    match.group("number")
                ),
                "name": name,
                "hours": parse_hours(
                    match.group("hours")
                ),
                "topics": [],
            }

            modules.append(current)
            continue

        if current is None:
            continue

        # Stop when another major section begins.
        lower = line.lower()

        if lower in {
            "course outcomes",
            "course outcome",
            "program outcomes",
            "program specific outcomes",
            "textbooks",
            "reference books",
            "references",
            "online resources",
            "tools & technologies",
            "tools and technologies",
            "projects / case studies",
            "projects and case studies",
        }:
            current = None
            continue

        # Ignore obvious metadata lines.
        if re.match(
            r"^(university|college|program|department|semester|credits|"
            r"contact hours|regulation)\s*:",
            line,
            re.IGNORECASE,
        ):
            continue

        # Ignore the heading itself.
        if is_placeholder(line):
            continue

        # Skip empty/noise lines.
        if len(line) < 3:
            continue

        # Strip list numbering/bullets.
        topic = re.sub(
            r"^[\-\*\u2022\u25CF\d]+[\.\):\-]\s*",
            "",
            line,
        ).strip()

        if not topic:
            continue

        if topic.lower() == current["name"].lower():
            continue

        # Don't treat CO/PO/etc as topics.
        if re.match(
            r"^(CO|PO|PSO)\s*\d+\s*[:\-.)]",
            topic,
            re.IGNORECASE,
        ):
            continue

        if topic not in current["topics"]:
            current["topics"].append(topic)

    return modules


# ============================================================
# OUTCOME EXTRACTION
# ============================================================

CO_PATTERN = re.compile(
    r"""
    ^\s*
    (?P<code>CO\s*\d+)
    \s*
    [:\-.)]
    \s*
    (?P<description>.+?)
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

PO_PATTERN = re.compile(
    r"""
    ^\s*
    (?P<code>PO\s*\d+)
    \s*
    [:\-.)]
    \s*
    (?P<description>.+?)
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

PSO_PATTERN = re.compile(
    r"""
    ^\s*
    (?P<code>PSO\s*\d+)
    \s*
    [:\-.)]
    \s*
    (?P<description>.+?)
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _extract_outcomes(
    text: str,
    pattern: re.Pattern,
) -> List[Dict[str, str]]:

    result: List[Dict[str, str]] = []

    for line in normalize_lines(text):

        match = pattern.match(line)

        if not match:
            continue

        code = (
            clean_text(match.group("code"))
            .upper()
            .replace(" ", "")
        )

        description = clean_text(
            match.group("description")
        )

        if not description or is_placeholder(description):
            continue

        result.append(
            {
                "code": code,
                "description": description,
            }
        )

    return unique_dicts(
        result,
        ("code", "description"),
    )


def extract_course_outcomes_from_text(
    text: str,
) -> List[Dict[str, str]]:
    return _extract_outcomes(
        text,
        CO_PATTERN,
    )


def extract_program_outcomes_from_text(
    text: str,
) -> List[Dict[str, str]]:
    return _extract_outcomes(
        text,
        PO_PATTERN,
    )


def extract_program_specific_outcomes_from_text(
    text: str,
) -> List[Dict[str, str]]:
    return _extract_outcomes(
        text,
        PSO_PATTERN,
    )


# ============================================================
# OBJECTIVES / PREREQUISITES
# ============================================================

def extract_objectives_from_text(
    text: str,
) -> List[str]:
    """
    Extract course objectives from common syllabus layouts.

    Supports:
        Objectives:
        - item 1
        Course Objectives
        item 1
        Course Objectives: item 1; item 2
        Objectives: ['item 1', 'item 2']
    """

    lines = normalize_lines(text)

    objective_headers = {
        "course objectives",
        "course objective",
        "objectives",
        "objective",
    }

    stop_headers = {
        "prerequisites",
        "prerequisite",
        "modules and topics",
        "course outcomes",
        "course outcome",
        "program outcomes",
        "program specific outcomes",
        "co-po / co-pso mapping",
        "teaching & learning methods",
        "teaching and learning methods",
        "practical / laboratory",
        "assessment pattern",
        "textbooks",
        "reference books",
        "online resources",
        "tools & technologies",
        "tools and technologies",
        "datasets",
        "projects / case studies",
        "projects and case studies",
    }

    result: List[str] = []
    active = False

    def add_objective(value: str) -> None:
        value = clean_text(value)

        if not value:
            return

        # Handle Python-list style:
        # ['Objective one', 'Objective two']
        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = json.loads(
                    value.replace("'", '"')
                )

                if isinstance(parsed, list):
                    for item in parsed:
                        add_objective(str(item))
                    return

            except Exception:
                value = value[1:-1]

        parts = re.split(
            r"\\s*;\\s*",
            value,
        )

        for part in parts:

            part = re.sub(
                r"^[\-\*\u2022\u25CF\d]+[\.\):\-]?\s*",
                "",
                part,
            ).strip(" '\"")

            if (
                len(part) >= 10
                and not is_placeholder(part)
            ):
                result.append(part)

    for line in lines:

        normalized = line.lower().strip(" :")

        # Inline form:
        # Objectives: Understand...
        inline = re.match(
            r"^\s*(?:course\s+)?objectives?\s*[:\-]\s*(.+)$",
            line,
            re.IGNORECASE,
        )

        if inline:
            active = True
            add_objective(
                inline.group(1)
            )
            continue

        # Standalone heading
        if normalized in objective_headers:
            active = True
            continue

        if (
            active
            and normalized in stop_headers
        ):
            break

        if not active:
            continue

        add_objective(line)

    return clean_string_list(result)

def extract_prerequisites_from_text(
    text: str,
) -> List[str]:

    lines = normalize_lines(text)

    headers = {
        "prerequisites",
        "prerequisite",
    }

    stop_headers = {
        "modules and topics",
        "course outcomes",
        "program outcomes",
        "program specific outcomes",
        "course objectives",
        "objectives",
        "textbooks",
        "reference books",
        "tools & technologies",
        "tools and technologies",
        "projects / case studies",
        "projects and case studies",
    }

    result: List[str] = []
    active = False

    for line in lines:

        normalized = line.lower().strip(" :")

        if normalized in headers:
            active = True
            continue

        if active and normalized in stop_headers:
            break

        if not active:
            continue

        cleaned = re.sub(
            r"^[\-\*\u2022\u25CF\d]+[\.\):\-]?\s*",
            "",
            line,
        )

        if cleaned and len(cleaned) >= 3:
            result.append(cleaned)

    return clean_string_list(result)


# ============================================================
# TOOLS / TECHNOLOGIES
# ============================================================

KNOWN_TOOLS = [
    "Python",
    "NumPy",
    "Pandas",
    "Matplotlib",
    "Seaborn",
    "Scikit-learn",
    "TensorFlow",
    "Keras",
    "PyTorch",
    "Hugging Face",
    "Transformers",
    "LangChain",
    "LangGraph",
    "LlamaIndex",
    "FAISS",
    "Chroma",
    "Streamlit",
    "Gradio",
    "Docker",
    "Kubernetes",
    "FastAPI",
    "OpenCV",
    "Git",
    "GitHub",
    "MLflow",
    "Power BI",
    "SQL",
]


def extract_tools_from_text(
    text: str,
) -> List[str]:

    lower_text = clean_text(text).lower()

    found: List[str] = []

    for tool in KNOWN_TOOLS:

        if tool.lower() in lower_text:
            found.append(tool)

    # Also parse explicit Tools/Technologies sections.
    section = section_lines(
        text,
        [
            "tools & technologies",
            "tools and technologies",
            "tools",
            "technologies",
        ],
    )

    for line in section:

        parts = re.split(
            r"[,;|]",
            line,
        )

        for part in parts:

            part = clean_text(part)

            if (
                part
                and len(part) <= 80
                and not is_placeholder(part)
            ):
                found.append(part)

    return clean_string_list(found)


# ============================================================
# PROJECTS / REFERENCES
# ============================================================

def extract_projects_from_text(
    text: str,
) -> List[str]:

    section = section_lines(
        text,
        [
            "projects / case studies",
            "projects and case studies",
            "projects",
            "case studies",
        ],
    )

    return clean_string_list(section)


def extract_references_from_text(
    text: str,
) -> Dict[str, List[str]]:

    textbooks = section_lines(
        text,
        ["textbooks"],
    )

    reference_books = section_lines(
        text,
        ["reference books", "references"],
    )

    online_resources = section_lines(
        text,
        ["online resources"],
    )

    return {
        "textbooks": clean_string_list(
            textbooks
        ),
        "reference_books": clean_string_list(
            reference_books
        ),
        "online_resources": clean_string_list(
            online_resources
        ),
    }


# ============================================================
# CHUNKING
# ============================================================

def split_text_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Split long text into bounded chunks.

    Attempts to split at paragraph/line boundaries before falling
    back to character boundaries.
    """
    text = clean_text(text)

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    overlap = max(
        0,
        min(overlap, chunk_size // 2),
    )

    chunks: List[str] = []

    start = 0
    total = len(text)

    while start < total:

        end = min(
            total,
            start + chunk_size,
        )

        if end < total:

            candidates = [
                text.rfind("\n\n", start, end),
                text.rfind("\n", start, end),
                text.rfind(". ", start, end),
            ]

            good = max(candidates)

            if good > start + int(
                chunk_size * 0.60
            ):
                end = good + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= total:
            break

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


# ============================================================
# JSON PARSING
# ============================================================

def extract_json_object(
    content: Any,
) -> Optional[Dict[str, Any]]:
    """
    Parse JSON from plain LLM text.

    Supports:
      - direct JSON
      - ```json ... ```
      - JSON embedded in explanatory text
    """
    if content is None:
        return None

    text = clean_text(content)

    if not text:
        return None

    # Remove markdown fences.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    try:
        value = json.loads(text)

        if isinstance(value, dict):
            return value

    except Exception:
        pass

    # Find the first balanced JSON object.
    start = text.find("{")

    if start < 0:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(
        start,
        len(text),
    ):

        char = text[index]

        if in_string:

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if char == '"':
                in_string = False

            continue

        if char == '"':
            in_string = True
            continue

        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:

                candidate = text[
                    start:index + 1
                ]

                try:

                    value = json.loads(
                        candidate
                    )

                    if isinstance(
                        value,
                        dict,
                    ):
                        return value

                except Exception:
                    return None

    return None


# ============================================================
# GROQ CLIENT
# ============================================================

def get_groq_client() -> Any:
    if Groq is None:
        raise ImportError(
            "groq package is not installed. "
            "Add 'groq' to requirements.txt."
        )

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:
        try:
            import streamlit as st

            api_key = (
                st.secrets.get(
                    "GROQ_API_KEY"
                )
            )
        except Exception:
            api_key = None

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured. "
            "Configure it in Streamlit secrets "
            "or the environment."
        )

    return Groq(
        api_key=api_key
    )


# ============================================================
# GROQ PROMPTS
# ============================================================

SYSTEM_PROMPT = """
You are an expert university curriculum extraction engine.

Extract only information supported by the supplied syllabus text.

Return ONE JSON OBJECT and nothing else.

Do NOT use markdown fences.

Never invent values.

Never output placeholders such as:
- Module 1
- Module 2
- Topic 1
- Unknown
- N/A
- Not Available

If an actual value is not present in the supplied text, return an
empty string, empty array, or empty object.

The JSON schema is:

{
  "metadata": {
    "university": "",
    "college": "",
    "program": "",
    "department": "",
    "subject_name": "",
    "subject_code": "",
    "academic_year": "",
    "regulation": "",
    "semester": "",
    "category": "",
    "credits": 0,
    "contact_hours": 0
  },
  "objectives": [],
  "prerequisites": [],
  "modules": [
    {
      "number": "",
      "name": "",
      "hours": 0,
      "topics": []
    }
  ],
  "course_outcomes": [],
  "program_outcomes": [],
  "program_specific_outcomes": [],
  "co_po_mapping": [],
  "teaching_methods": [],
  "practical_components": [],
  "assessment_pattern": [],
  "textbooks": [],
  "reference_books": [],
  "online_resources": [],
  "tools": [],
  "datasets": [],
  "projects": [],
  "other_information": []
}
"""


def build_chunk_prompt(
    chunk: str,
    document_context: str,
    chunk_number: int,
    total_chunks: int,
) -> str:

    return f"""
Extract curriculum information from this syllabus section.

This is chunk {chunk_number} of {total_chunks}.

DOCUMENT CONTEXT:
{document_context}

CURRENT SYLLABUS SECTION:
{chunk}

Important rules:

1. Return ONLY a JSON object.
2. Never use markdown.
3. Never invent information.
4. Never create generic names such as "Module 1" when the real
   module name is not known.
5. Preserve exact course codes and outcome codes.
6. Preserve exact module names.
7. Preserve topic names.
8. Extract CO, PO and PSO entries when explicitly present.
9. Extract tools and technologies explicitly present.
10. If a field is not present in this chunk, return an empty value.
11. The document context may contain metadata from the first page;
    use it when it clearly identifies the document.
"""


# ============================================================
# GROQ CALL
# ============================================================

def call_groq_once(
    client: Any,
    prompt: str,
    config: ExtractorConfig,
) -> Dict[str, Any]:

    logger.info(
        "Calling Groq model: %s",
        config.model,
    )

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        reasoning_format="hidden",
    )

    if not getattr(
        response,
        "choices",
        None,
    ):
        raise RuntimeError(
            "Groq returned no choices."
        )

    choice = response.choices[0]
    message = getattr(
        choice,
        "message",
        None,
    )

    if message is None:
        raise RuntimeError(
            "Groq returned no assistant message."
        )

    content = getattr(
        message,
        "content",
        None,
    )

    if content:
        parsed = extract_json_object(
            content
        )

        if parsed is not None:
            return parsed

        raise RuntimeError(
            "Groq returned content, "
            "but it was not valid JSON."
        )

    refusal = getattr(
        message,
        "refusal",
        None,
    )

    if refusal:
        raise RuntimeError(
            f"Groq refused the request: {refusal}"
        )

    reasoning = getattr(
        message,
        "reasoning",
        None,
    )

    if reasoning:
        parsed = extract_json_object(
            reasoning
        )

        if parsed is not None:
            logger.warning(
                "Recovered JSON from reasoning content."
            )
            return parsed

    tool_calls = getattr(
        message,
        "tool_calls",
        None,
    )

    if tool_calls:
        raise RuntimeError(
            "Groq returned tool calls instead "
            "of curriculum JSON."
        )

    raise RuntimeError(
        "Groq returned HTTP 200 but "
        "message.content was empty."
    )


def call_groq_with_retry(
    prompt: str,
    config: ExtractorConfig,
    client: Optional[Any] = None,
) -> Dict[str, Any]:

    if client is None:
        client = get_groq_client()

    last_error: Optional[Exception] = None

    attempts = max(
        1,
        config.retries + 1,
    )

    for attempt in range(
        1,
        attempts + 1,
    ):

        try:

            return call_groq_once(
                client=client,
                prompt=prompt,
                config=config,
            )

        except Exception as exc:

            last_error = exc

            logger.warning(
                "Groq attempt %s/%s failed: %s",
                attempt,
                attempts,
                exc,
            )

            if attempt < attempts:
                time.sleep(
                    min(
                        5.0 * attempt,
                        15.0,
                    )
                )

    raise RuntimeError(
        "Groq extraction failed after "
        f"{attempts} attempts. "
        f"Last error: {last_error}"
    ) from last_error


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_module(
    module: Any,
) -> Optional[Dict[str, Any]]:

    if not isinstance(
        module,
        dict,
    ):
        return None

    name = first_non_empty(
        module.get("name"),
        module.get("module_name"),
        module.get("title"),
    )

    if not name or is_placeholder(name):
        return None

    topics = clean_string_list(
        module.get("topics")
        or module.get("topic_list")
        or []
    )

    return {
        "number": clean_text(
            module.get("number")
            or module.get("id")
            or ""
        ),
        "name": clean_text(name),
        "hours": parse_hours(
            module.get("hours")
        ),
        "topics": topics,
    }


def normalize_outcome(
    outcome: Any,
) -> Optional[Dict[str, str]]:

    if isinstance(
        outcome,
        str,
    ):
        text = clean_text(outcome)

        match = re.match(
            r"^(CO|PO|PSO)\s*(\d+)\s*[:\-.)]\s*(.+)$",
            text,
            re.IGNORECASE,
        )

        if match:
            return {
                "code": (
                    match.group(1).upper()
                    + match.group(2)
                ),
                "description": clean_text(
                    match.group(3)
                ),
            }

        if text:
            return {
                "code": "",
                "description": text,
            }

        return None

    if not isinstance(
        outcome,
        dict,
    ):
        return None

    code = clean_text(
        outcome.get("code")
        or outcome.get("id")
        or ""
    )

    description = first_non_empty(
        outcome.get("description"),
        outcome.get("text"),
        outcome.get("outcome"),
    )

    if not description:
        return None

    return {
        "code": code.upper().replace(" ", ""),
        "description": clean_text(
            description
        ),
    }


def normalize_curriculum(
    data: Any,
) -> Dict[str, Any]:

    if not isinstance(
        data,
        dict,
    ):
        data = {}

    metadata = data.get(
        "metadata",
        {}
    )

    if not isinstance(
        metadata,
        dict,
    ):
        metadata = {}

    modules: List[Dict[str, Any]] = []

    for module in (
        data.get("modules")
        or []
    ):

        normalized = normalize_module(
            module
        )

        if normalized:
            modules.append(
                normalized
            )

    modules = unique_dicts(
        modules,
        ("number", "name"),
    )

    def normalize_outcome_list(
        values: Any,
    ) -> List[Dict[str, str]]:

        result = []

        if not isinstance(
            values,
            list,
        ):
            values = [values] if values else []

        for value in values:

            item = normalize_outcome(
                value
            )

            if item:
                result.append(item)

        return unique_dicts(
            result,
            ("code", "description"),
        )

    result: Dict[str, Any] = {
        "metadata": metadata,
        "objectives": clean_string_list(
            data.get("objectives")
        ),
        "prerequisites": clean_string_list(
            data.get("prerequisites")
        ),
        "modules": modules,
        "course_outcomes": normalize_outcome_list(
            data.get("course_outcomes")
        ),
        "program_outcomes": normalize_outcome_list(
            data.get("program_outcomes")
        ),
        "program_specific_outcomes": normalize_outcome_list(
            data.get("program_specific_outcomes")
        ),
        "co_po_mapping": data.get(
            "co_po_mapping"
        ) or [],
        "teaching_methods": clean_string_list(
            data.get("teaching_methods")
        ),
        "practical_components": clean_string_list(
            data.get("practical_components")
        ),
        "assessment_pattern": clean_string_list(
            data.get("assessment_pattern")
        ),
        "textbooks": clean_string_list(
            data.get("textbooks")
        ),
        "reference_books": clean_string_list(
            data.get("reference_books")
        ),
        "online_resources": clean_string_list(
            data.get("online_resources")
        ),
        "tools": clean_string_list(
            data.get("tools")
        ),
        "datasets": clean_string_list(
            data.get("datasets")
        ),
        "projects": clean_string_list(
            data.get("projects")
        ),
        "other_information": clean_string_list(
            data.get("other_information")
        ),
    }


    # --------------------------------------------------------
    # TOP-LEVEL METADATA COMPATIBILITY
    # --------------------------------------------------------
    # Older Streamlit pages may read metadata directly from
    # syllabus["university"], syllabus["college"], etc.
    # Keep both representations available.
    for _key in [
        "university",
        "college",
        "program",
        "department",
        "subject_name",
        "subject_code",
        "academic_year",
        "regulation",
        "semester",
        "category",
        "credits",
        "contact_hours",
        "source_file",
        "source_type",
    ]:
        if _key in result["metadata"]:
            result[_key] = result["metadata"][_key]

    return result


# ============================================================
# SMART MERGE
# ============================================================

def merge_string_values(
    primary: Any,
    secondary: Any,
) -> List[str]:

    return clean_string_list(
        list(
            clean_string_list(primary)
            + clean_string_list(secondary)
        )
    )


def merge_deterministic_data(
    curriculum: Dict[str, Any],
    text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Merge deterministic source-text extraction into LLM output.

    Explicit source text wins over fabricated/placeholder LLM values.
    """
    curriculum = normalize_curriculum(
        curriculum
    )

    deterministic_metadata = extract_basic_metadata(
        text,
        source_file=source_file,
        source_type=source_type,
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = curriculum.get(
        "metadata",
        {}
    )

    if not isinstance(
        metadata,
        dict,
    ):
        metadata = {}

    for key, value in deterministic_metadata.items():

        if value is None:
            continue

        if (
            not metadata.get(key)
            or is_placeholder(
                metadata.get(key)
            )
        ):
            metadata[key] = value

    curriculum["metadata"] = metadata

    # --------------------------------------------------------
    # Modules
    # --------------------------------------------------------

    deterministic_modules = (
        extract_topics_by_module(
            text
        )
    )

    if not deterministic_modules:
        deterministic_modules = (
            extract_modules_from_text(
                text
            )
        )

    existing_modules = curriculum.get(
        "modules",
        []
    )

    valid_existing = [
        normalize_module(module)
        for module in existing_modules
    ]

    valid_existing = [
        module
        for module in valid_existing
        if module is not None
    ]

    # Explicit module headings from the source are authoritative.
    if deterministic_modules:

        merged_modules: List[Dict[str, Any]] = []

        for source_module in deterministic_modules:

            source_number = clean_text(
                source_module.get("number")
            )

            source_name = clean_text(
                source_module.get("name")
            )

            matching = None

            for candidate in valid_existing:

                candidate_number = clean_text(
                    candidate.get("number")
                )

                candidate_name = clean_text(
                    candidate.get("name")
                )

                if (
                    source_number
                    and candidate_number
                    and source_number == candidate_number
                ):
                    matching = candidate
                    break

                if (
                    source_name
                    and candidate_name.lower()
                    == source_name.lower()
                ):
                    matching = candidate
                    break

            if matching is None:

                matching = {
                    "number": source_number,
                    "name": source_name,
                    "hours": source_module.get(
                        "hours",
                        0.0,
                    ),
                    "topics": [],
                }

            # Source heading wins.
            matching["number"] = (
                source_number
                or matching.get("number", "")
            )

            matching["name"] = source_name

            source_hours = parse_hours(
                source_module.get("hours")
            )

            if source_hours:
                matching["hours"] = source_hours

            source_topics = clean_string_list(
                source_module.get("topics")
            )

            matching["topics"] = clean_string_list(
                list(
                    matching.get("topics", [])
                )
                + source_topics
            )

            merged_modules.append(
                matching
            )

        # Preserve valid LLM-only modules only if they have
        # real names and were not placeholders.
        existing_names = {
            clean_text(
                x.get("name")
            ).lower()
            for x in merged_modules
        }

        for candidate in valid_existing:

            name = clean_text(
                candidate.get("name")
            )

            if (
                name
                and not is_placeholder(name)
                and name.lower()
                not in existing_names
            ):
                merged_modules.append(
                    candidate
                )

        curriculum["modules"] = merged_modules

    else:

        curriculum["modules"] = valid_existing

    # --------------------------------------------------------
    # Objectives
    # --------------------------------------------------------

    deterministic_objectives = (
        extract_objectives_from_text(
            text
        )
    )

    curriculum["objectives"] = merge_string_values(
        deterministic_objectives,
        curriculum.get("objectives"),
    )

    # --------------------------------------------------------
    # Prerequisites
    # --------------------------------------------------------

    deterministic_prerequisites = (
        extract_prerequisites_from_text(
            text
        )
    )

    curriculum["prerequisites"] = merge_string_values(
        deterministic_prerequisites,
        curriculum.get("prerequisites"),
    )

    # --------------------------------------------------------
    # Outcomes
    # --------------------------------------------------------

    deterministic_cos = (
        extract_course_outcomes_from_text(
            text
        )
    )

    deterministic_pos = (
        extract_program_outcomes_from_text(
            text
        )
    )

    deterministic_psos = (
        extract_program_specific_outcomes_from_text(
            text
        )
    )

    curriculum["course_outcomes"] = unique_dicts(
        deterministic_cos
        + curriculum.get(
            "course_outcomes",
            [],
        ),
        ("code", "description"),
    )

    curriculum["program_outcomes"] = unique_dicts(
        deterministic_pos
        + curriculum.get(
            "program_outcomes",
            [],
        ),
        ("code", "description"),
    )

    curriculum["program_specific_outcomes"] = unique_dicts(
        deterministic_psos
        + curriculum.get(
            "program_specific_outcomes",
            [],
        ),
        ("code", "description"),
    )

    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    deterministic_tools = (
        extract_tools_from_text(
            text
        )
    )

    curriculum["tools"] = clean_string_list(
        deterministic_tools
        + curriculum.get(
            "tools",
            [],
        )
    )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    deterministic_projects = (
        extract_projects_from_text(
            text
        )
    )

    curriculum["projects"] = merge_string_values(
        deterministic_projects,
        curriculum.get("projects"),
    )

    # --------------------------------------------------------
    # References
    # --------------------------------------------------------

    references = extract_references_from_text(
        text
    )

    curriculum["textbooks"] = merge_string_values(
        references.get("textbooks"),
        curriculum.get("textbooks"),
    )

    curriculum["reference_books"] = merge_string_values(
        references.get("reference_books"),
        curriculum.get("reference_books"),
    )

    curriculum["online_resources"] = merge_string_values(
        references.get("online_resources"),
        curriculum.get("online_resources"),
    )

    return normalize_curriculum(
        curriculum
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_extraction_quality(
    curriculum: Dict[str, Any],
) -> List[str]:
    """
    Return warnings rather than throwing for recoverable gaps.
    """
    warnings: List[str] = []

    metadata = curriculum.get(
        "metadata",
        {}
    )

    if not metadata.get(
        "subject_name"
    ) and not metadata.get(
        "program"
    ):
        warnings.append(
            "Subject name could not be confidently extracted."
        )

    if not metadata.get(
        "subject_code"
    ):
        warnings.append(
            "Subject code could not be confidently extracted."
        )

    if not metadata.get(
        "university"
    ):
        warnings.append(
            "University name could not be confidently extracted."
        )

    modules = curriculum.get(
        "modules",
        []
    )

    if not modules:
        warnings.append(
            "No modules could be confidently extracted."
        )

    for index, module in enumerate(
        modules,
        start=1,
    ):

        if is_placeholder(
            module.get("name")
        ):
            warnings.append(
                f"Module {index} does not have "
                "a module name."
            )

    return warnings


# ============================================================
# CHUNK MERGE
# ============================================================

def merge_chunk_results(
    chunk_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Merge successful LLM chunk dictionaries."""
    merged = normalize_curriculum({})

    for chunk in chunk_results:

        if not isinstance(
            chunk,
            dict,
        ):
            continue

        chunk = normalize_curriculum(
            chunk
        )

        # Metadata
        merged_metadata = merged[
            "metadata"
        ]

        for key, value in chunk[
            "metadata"
        ].items():

            if (
                value is not None
                and not is_placeholder(value)
            ):
                if (
                    not merged_metadata.get(key)
                    or is_placeholder(
                        merged_metadata.get(key)
                    )
                ):
                    merged_metadata[key] = value

        # Lists
        for key in [
            "objectives",
            "prerequisites",
            "teaching_methods",
            "practical_components",
            "assessment_pattern",
            "textbooks",
            "reference_books",
            "online_resources",
            "tools",
            "datasets",
            "projects",
            "other_information",
        ]:

            merged[key] = merge_string_values(
                merged.get(key),
                chunk.get(key),
            )

        # Outcomes
        for key in [
            "course_outcomes",
            "program_outcomes",
            "program_specific_outcomes",
        ]:

            merged[key] = unique_dicts(
                merged.get(key, [])
                + chunk.get(key, []),
                ("code", "description"),
            )

        # Modules
        for module in chunk.get(
            "modules",
            [],
        ):

            normalized = normalize_module(
                module
            )

            if not normalized:
                continue

            found = None

            for existing in merged[
                "modules"
            ]:

                same_number = (
                    normalized.get("number")
                    and existing.get("number")
                    and normalized.get("number")
                    == existing.get("number")
                )

                same_name = (
                    normalized.get("name")
                    and existing.get("name")
                    and normalized.get("name").lower()
                    == existing.get("name").lower()
                )

                if same_number or same_name:
                    found = existing
                    break

            if found is None:

                merged["modules"].append(
                    normalized
                )

            else:

                if (
                    not found.get("name")
                    or is_placeholder(
                        found.get("name")
                    )
                ):
                    found["name"] = normalized[
                        "name"
                    ]

                if normalized.get(
                    "hours"
                ):
                    found["hours"] = normalized[
                        "hours"
                    ]

                found["topics"] = clean_string_list(
                    found.get("topics", [])
                    + normalized.get(
                        "topics",
                        [],
                    )
                )

    return normalize_curriculum(
        merged
    )


# ============================================================
# EXTRACTION FROM TEXT
# ============================================================

def extract_curriculum_from_text(
    text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
    filename: Optional[str] = None,
    config: Optional[ExtractorConfig] = None,
    client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Main extraction engine.

    Parameters are intentionally permissive for compatibility with
    previous application versions.
    """
    text = clean_text(text)

    if not text:
        raise ValueError(
            "No syllabus text was supplied."
        )

    config = config or ExtractorConfig()

    if source_file is None:
        source_file = filename

    logger.info(
        "Starting curriculum extraction from text"
    )

    # --------------------------------------------------------
    # Deterministic first pass
    # --------------------------------------------------------

    deterministic = normalize_curriculum({})

    deterministic = merge_deterministic_data(
        deterministic,
        text,
        source_file=source_file,
        source_type=source_type,
    )

    # --------------------------------------------------------
    # Chunking
    # --------------------------------------------------------

    chunks = split_text_into_chunks(
        text,
        chunk_size=config.chunk_size,
        overlap=config.chunk_overlap,
    )

    logger.info(
        "Syllabus size: %s characters -> %s chunks",
        len(text),
        len(chunks),
    )

    # Small document can still use Groq.
    # Large document gets bounded requests.
    if not chunks:
        return deterministic

    # Keep document-level context so every chunk knows what
    # syllabus it belongs to.
    context_length = min(
        3000,
        len(text),
    )

    document_context = text[
        :context_length
    ]

    chunk_results: List[Dict[str, Any]] = []

    groq_error_count = 0

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        logger.info(
            "Extracting syllabus chunk %s/%s (%s characters)",
            index,
            len(chunks),
            len(chunk),
        )

        prompt = build_chunk_prompt(
            chunk=chunk,
            document_context=document_context,
            chunk_number=index,
            total_chunks=len(chunks),
        )

        try:

            result = call_groq_with_retry(
                prompt=prompt,
                config=config,
                client=client,
            )

            if isinstance(
                result,
                dict,
            ):
                chunk_results.append(
                    result
                )

        except Exception as exc:

            groq_error_count += 1

            logger.warning(
                "Chunk %s/%s failed: %s",
                index,
                len(chunks),
                exc,
            )

            # Continue with other chunks.
            continue

        if (
            config.request_delay > 0
            and index < len(chunks)
        ):
            time.sleep(
                config.request_delay
            )

    # --------------------------------------------------------
    # Merge LLM results
    # --------------------------------------------------------

    if chunk_results:

        llm_curriculum = merge_chunk_results(
            chunk_results
        )

        curriculum = merge_deterministic_data(
            llm_curriculum,
            text,
            source_file=source_file,
            source_type=source_type,
        )

    else:

        logger.warning(
            "No valid Groq chunk results. "
            "Using deterministic extraction."
        )

        curriculum = deterministic

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    warnings = validate_extraction_quality(
        curriculum
    )

    curriculum["_warnings"] = warnings

    curriculum["_extraction"] = {
        "success": bool(
            curriculum.get("modules")
            or curriculum.get(
                "course_outcomes"
            )
            or curriculum.get(
                "metadata"
            )
        ),
        "chunks_total": len(chunks),
        "chunks_successful": len(
            chunk_results
        ),
        "chunks_failed": groq_error_count,
        "source_file": source_file,
        "source_type": source_type,
        "character_count": len(text),
        "model": config.model,
    }

    logger.info(
        "Curriculum extraction completed: "
        "%s modules, %s COs, %s tools, "
        "%s/%s chunks successful",
        len(
            curriculum.get(
                "modules",
                [],
            )
        ),
        len(
            curriculum.get(
                "course_outcomes",
                [],
            )
        ),
        len(
            curriculum.get(
                "tools",
                [],
            )
        ),
        len(chunk_results),
        len(chunks),
    )

    return curriculum


# ============================================================
# PUBLIC FUNCTION API
# ============================================================

def extract_syllabus(
    text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
    filename: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Public API used by Streamlit pages.

    Compatible calls:

        extract_syllabus(text)

        extract_syllabus(
            text,
            source_file="scheme.pdf",
            source_type="pdf",
        )
    """
    if source_file is None:
        source_file = filename

    config = kwargs.pop(
        "config",
        None,
    )

    client = kwargs.pop(
        "client",
        None,
    )

    return extract_curriculum_from_text(
        text=text,
        source_file=source_file,
        source_type=source_type,
        config=config,
        client=client,
    )


# Alias retained for compatibility.
extract_curriculum = extract_syllabus


# ============================================================
# CLASS API COMPATIBILITY
# ============================================================

class CurriculumExtractor:
    """
    Backward-compatible class interface.

    Supports older application code such as:

        extractor = CurriculumExtractor()
        result = extractor.extract(text)

    and:

        extractor.extract_syllabus(text)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        retries: Optional[int] = None,
        request_delay: Optional[float] = None,
    ):

        self.config = ExtractorConfig(
            model=model or DEFAULT_MODEL,
            temperature=(
                DEFAULT_TEMPERATURE
                if temperature is None
                else temperature
            ),
            max_tokens=(
                DEFAULT_MAX_TOKENS
                if max_tokens is None
                else max_tokens
            ),
            chunk_size=(
                DEFAULT_CHUNK_SIZE
                if chunk_size is None
                else chunk_size
            ),
            chunk_overlap=(
                DEFAULT_CHUNK_OVERLAP
                if chunk_overlap is None
                else chunk_overlap
            ),
            retries=(
                DEFAULT_RETRIES
                if retries is None
                else retries
            ),
            request_delay=(
                DEFAULT_REQUEST_DELAY
                if request_delay is None
                else request_delay
            ),
        )

    def extract(
        self,
        text: str,
        filename: Optional[str] = None,
        source_file: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> Dict[str, Any]:

        return extract_curriculum_from_text(
            text=text,
            source_file=(
                source_file
                or filename
            ),
            source_type=source_type,
            config=self.config,
        )

    def extract_syllabus(
        self,
        text: str,
        filename: Optional[str] = None,
        source_file: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> Dict[str, Any]:

        return self.extract(
            text=text,
            filename=filename,
            source_file=source_file,
            source_type=source_type,
        )


__all__ = [
    "ExtractorConfig",
    "CurriculumExtractor",
    "extract_syllabus",
    "extract_curriculum",
    "extract_curriculum_from_text",
    "split_text_into_chunks",
    "extract_json_object",
    "validate_extraction_quality",
    "merge_deterministic_data",
]
