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


import hashlib

import json

import logging

import os

import time

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

        "3500",

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

        "2200",

    )

)


DEFAULT_CHUNK_MAX_TOKENS = int(

    os.getenv(

        "CURRICULUM_CHUNK_MAX_TOKENS",

        "1200",

    )

)


DEFAULT_CHUNK_DELAY_SECONDS = float(

    os.getenv(

        "CURRICULUM_CHUNK_DELAY_SECONDS",

        "21",

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
# ============================================================
# curriculum/extractor.py
# CHUNK 2/8
#
# GROQ / LLAMA CLIENT + EXTRACTION PROMPTS
# ============================================================


# ============================================================
# 21. GROQ IMPORT
# ============================================================

try:

    from groq import Groq

except ImportError:

    Groq = None


# ============================================================
# 22. EXTRACTOR CONFIGURATION
# ============================================================

class ExtractorConfig:
    """
    Configuration for the curriculum extraction engine.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: int = 120,
    ):

        self.api_key = (

            api_key

            or os.getenv(
                "GROQ_API_KEY"
            )

        )


        self.model = (

            model

            or DEFAULT_MODEL

        )


        self.temperature = (

            DEFAULT_TEMPERATURE

            if temperature is None

            else temperature

        )


        self.max_tokens = (

            max_tokens

            or DEFAULT_MAX_TOKENS

        )


        self.timeout = timeout


    def validate(
        self,
    ) -> None:
        """
        Validate configuration before making
        an API request.
        """

        if Groq is None:

            raise ImportError(

                (
                    "Groq package is not installed. "
                    "Install it using: "
                    "pip install groq"
                )

            )


        if not self.api_key:

            raise ValueError(

                (
                    "GROQ_API_KEY is not configured. "
                    "Set it in the environment or "
                    "Streamlit secrets."
                )

            )


# ============================================================
# 23. GROQ CLIENT FACTORY
# ============================================================

def create_groq_client(
    config: Optional[
        ExtractorConfig
    ] = None,
):
    """
    Create a Groq client.

    Example:

        config = ExtractorConfig()

        client = create_groq_client(config)
    """

    config = (

        config

        or ExtractorConfig()

    )


    config.validate()


    return Groq(

        api_key=config.api_key,

    )


# ============================================================
# 24. SYSTEM PROMPT
# ============================================================

CURRICULUM_SYSTEM_PROMPT = """
You are an expert AI Curriculum Intelligence system.

Your task is to analyze an academic syllabus and convert it
into a complete, structured curriculum representation.

You are NOT merely a summarization system.

You must identify:

1. Institution information
2. Course information
3. Academic structure
4. Modules / Units
5. Topics
6. Subtopics
7. Concepts
8. Skills
9. Tools
10. Technologies
11. Programming languages
12. Frameworks
13. Platforms
14. Projects
15. Case studies
16. Learning objectives
17. Prerequisites
18. Course Outcomes (CO)
19. Program Outcomes (PO)
20. Program Specific Outcomes (PSO)
21. Bloom's taxonomy levels
22. Theory / practical / lab components
23. Industry-relevant skills
24. Emerging technologies
25. References
26. Textbooks
27. Assessment information

IMPORTANT RULES:

- Use ONLY information supported by the supplied syllabus.
- Do NOT invent university names.
- Do NOT invent course codes.
- Do NOT invent modules that have no evidence in the source.
- Do NOT invent CO/PO/PSO statements.
- If information is missing, use null or [].
- Normalize duplicated topics.
- Preserve the original meaning.
- Keep module ordering.
- Keep topic ordering where possible.
- Separate concepts from tools and technologies.
- Identify skills explicitly and implicitly supported by topics.
- Do not treat every noun as a skill.
- Distinguish academic concepts from software tools.
- Distinguish tools from technologies/frameworks.
- Projects must be explicitly mentioned or strongly supported.
- Use concise descriptions.
- Preserve important academic terminology.

CONFIDENCE:

For extracted information, estimate confidence from 0 to 100.

Confidence should reflect evidence in the source document,
NOT how certain you are as an AI.

OUTPUT:

Return ONLY valid JSON.

Do not use Markdown.

Do not use ```json fences.

Do not include explanations before or after the JSON.
"""


# ============================================================
# 25. JSON SCHEMA INSTRUCTIONS
# ============================================================

CURRICULUM_JSON_INSTRUCTIONS = """
Return a JSON object using exactly this high-level structure:

{
  "metadata": {},
  "title": "",
  "description": "",
  "objectives": [],
  "prerequisites": [],
  "modules": [],
  "concepts": [],
  "skills": [],
  "tools": [],
  "technologies": [],
  "projects": [],
  "course_outcomes": [],
  "program_outcomes": [],
  "program_specific_outcomes": [],
  "co_po_mappings": [],
  "co_pso_mappings": [],
  "total_hours": 0,
  "total_credits": 0,
  "extraction_confidence": 0,
  "notes": []
}

METADATA:

{
  "university": null,
  "college": null,
  "department": null,
  "faculty_name": null,
  "program": null,
  "branch": null,
  "course_name": null,
  "subject_name": null,
  "course_code": null,
  "semester": null,
  "academic_year": null,
  "regulation": null,
  "credits": null,
  "lecture_hours": null,
  "tutorial_hours": null,
  "practical_hours": null,
  "total_hours": null,
  "prerequisites": [],
  "course_type": null,
  "source_file": null,
  "source_type": null,
  "extraction_confidence": null
}

MODULE:

{
  "module_id": null,
  "module_name": "",
  "description": null,
  "sequence": null,
  "hours": 0,
  "credits": null,
  "topics": [],
  "concepts": [],
  "skills": [],
  "tools": [],
  "technologies": [],
  "projects": [],
  "case_studies": [],
  "learning_objectives": [],
  "prerequisites": [],
  "bloom_levels": [],
  "difficulty": "Intermediate",
  "industry_relevance_score": 0,
  "academic_relevance_score": 50,
  "currency_score": 50,
  "recommended": false,
  "enhancement_notes": [],
  "co_mapping": []
}

TOPIC:

{
  "topic_id": null,
  "topic_name": "",
  "description": null,
  "hours": 0,
  "sequence": null,
  "learning_type": "Theory",
  "difficulty": "Intermediate",
  "bloom_level": "Understand",
  "concepts": [],
  "skills": [],
  "tools": [],
  "technologies": [],
  "prerequisites": [],
  "learning_objectives": [],
  "projects": [],
  "case_studies": [],
  "references": [],
  "industry_relevance_score": 0,
  "importance_score": 50,
  "current": true,
  "recommended_enhancement": false
}

CONCEPT:

{
  "name": "",
  "description": null,
  "concept_type": "Core",
  "importance_score": 50,
  "industry_relevance_score": 0,
  "difficulty": "Intermediate",
  "prerequisites": [],
  "related_concepts": [],
  "emerging": false,
  "industry_used": false,
  "source_references": []
}

SKILL:

{
  "name": "",
  "normalized_name": null,
  "category": "Other",
  "description": null,
  "proficiency_level": "Intermediate",
  "importance_score": 50,
  "industry_relevance_score": 0,
  "years_relevance": null,
  "aliases": [],
  "source_topics": []
}

TOOL:

{
  "name": "",
  "category": null,
  "purpose": null,
  "version": null,
  "industry_relevance_score": 0,
  "recommended": false
}

TECHNOLOGY:

{
  "name": "",
  "category": null,
  "description": null,
  "current_version": null,
  "industry_relevance_score": 0,
  "emerging": false,
  "recommended": false
}

PROJECT:

{
  "title": "",
  "description": null,
  "project_type": "Project",
  "difficulty": "Intermediate",
  "duration_hours": null,
  "skills": [],
  "concepts": [],
  "tools": [],
  "technologies": [],
  "industry_relevance_score": 0,
  "portfolio_ready": false,
  "real_world_problem": false
}

COURSE OUTCOME:

{
  "code": "",
  "description": "",
  "bloom_level": "Understand",
  "knowledge_area": null,
  "mapped_modules": [],
  "mapped_topics": [],
  "assessment_methods": []
}

PROGRAM OUTCOME:

{
  "code": "",
  "description": "",
  "category": null
}

PROGRAM SPECIFIC OUTCOME:

{
  "code": "",
  "description": "",
  "category": null
}

CO-PO MAPPING:

{
  "co_code": "",
  "po_code": "",
  "correlation": 0,
  "justification": null
}

CO-PSO MAPPING:

{
  "co_code": "",
  "pso_code": "",
  "correlation": 0,
  "justification": null
}
"""


# ============================================================
# 26. PROMPT BUILDER
# ============================================================

def build_curriculum_prompt(
    syllabus_text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> str:
    """
    Build the final LLM extraction prompt.
    """

    source_name = (
        clean_text(
            source_file
        )
        if source_file
        else "Unknown"
    )


    detected_type = detect_source_type(

        filename=source_file,

        source_type=source_type,

    )


    statistics = get_text_statistics(
        syllabus_text
    )


    sections = detect_sections(
        syllabus_text
    )


    section_text = (

        "\n".join(

            f"- {section}"

            for section in sections

        )

        if sections

        else "No obvious sections detected."

    )


    return f"""
{CURRICULUM_JSON_INSTRUCTIONS}

SOURCE INFORMATION:

Filename:
{source_name}

Source Type:
{detected_type}

SOURCE STATISTICS:

Characters:
{statistics["characters"]}

Words:
{statistics["words"]}

Lines:
{statistics["lines"]}

Likely Sections:
{section_text}

SYLLABUS TEXT:

---------------- BEGIN SYLLABUS ----------------

{syllabus_text}

----------------- END SYLLABUS -----------------

FINAL REQUIREMENT:

Return ONLY the JSON object.

Every extracted item must be grounded in the supplied
syllabus text.
"""


# ============================================================
# 27. GROQ CHAT COMPLETION
# ============================================================

def call_groq(
    prompt: str,
    system_prompt: str = CURRICULUM_SYSTEM_PROMPT,
    config: Optional[
        ExtractorConfig
    ] = None,
) -> str:
    """
    Call Groq chat completion.

    This function isolates all provider-specific code.
    """

    config = (

        config

        or ExtractorConfig()

    )


    client = create_groq_client(
        config
    )


    log_info(

        (
            "Calling Groq model: "
            f"{config.model}"
        )

    )


    response = client.chat.completions.create(

        model=config.model,

        messages=[

            {
                "role":
                    "system",

                "content":
                    system_prompt,

            },

            {
                "role":
                    "user",

                "content":
                    prompt,

            },

        ],

        temperature=config.temperature,

        max_tokens=config.max_tokens,

        # GPT-OSS models expose reasoning separately. Hide reasoning
        # so the assistant content channel contains the JSON payload.
        reasoning_format="hidden",

        # The extractor requires machine-readable JSON. Groq supports
        # JSON Object Mode for GPT-OSS 120B.
        response_format={
            "type": "json_object",
        },

    )


    if not response.choices:

        raise RuntimeError(
            "Groq returned no choices."
        )


    message = response.choices[0].message

    # Groq GPT-OSS responses can expose reasoning separately from
    # the assistant content. We intentionally parse ONLY content.
    content = getattr(
        message,
        "content",
        None,
    )

    if content:

        content = str(content).strip()

    if not content:

        reasoning = getattr(
            message,
            "reasoning",
            None,
        )

        refusal = getattr(
            message,
            "refusal",
            None,
        )

        tool_calls = getattr(
            message,
            "tool_calls",
            None,
        )

        logger.warning(
            (
                "Groq returned HTTP 200 but empty "
                "message.content; reasoning=%s, "
                "tool_calls=%s, refusal=%s"
            ),
            bool(reasoning),
            bool(tool_calls),
            bool(refusal),
        )

        if refusal:
            raise RuntimeError(
                "Groq refused the extraction request: "
                f"{refusal}"
            )

        if tool_calls:
            raise RuntimeError(
                "Groq returned tool calls instead of "
                "curriculum JSON."
            )

        # Some GPT-OSS responses may expose useful structured
        # output in the reasoning field when content is empty.
        # Only accept it when it actually contains valid JSON.
        if reasoning:
            reasoning_text = str(reasoning).strip()
            reasoning_payload = extract_json_object(
                reasoning_text
            )
            if reasoning_payload is not None:
                logger.warning(
                    "Groq content was empty; recovered valid JSON "
                    "from the reasoning field."
                )
                return json.dumps(
                    reasoning_payload,
                    ensure_ascii=False,
                )

        raise RuntimeError(
            "Groq returned HTTP 200 but no assistant content. "
            "The response contained no usable JSON content."
        )

    return content


# ============================================================
# 28. RETRYABLE GROQ CALL
# ============================================================

def call_groq_with_retry(
    prompt: str,
    system_prompt: str = CURRICULUM_SYSTEM_PROMPT,
    config: Optional[
        ExtractorConfig
    ] = None,
    retries: int = 2,
) -> str:
    """
    Call Groq with a small retry mechanism.
    """

    last_error: Optional[
        Exception
    ] = None


    for attempt in range(

        retries + 1

    ):

        try:

            return call_groq(

                prompt=prompt,

                system_prompt=system_prompt,

                config=config,

            )

        except Exception as exc:

            last_error = exc


            log_warning(

                (
                    f"Groq attempt "
                    f"{attempt + 1}/"
                    f"{retries + 1} failed: "
                    f"{exc}"
                )

            )


            if attempt >= retries:

                break


    raise RuntimeError(

        (
            "Groq extraction failed after "
            f"{retries + 1} attempts. "
            f"Last error: {last_error}"
        )

    ) from last_error


# ============================================================
# 29. LLM EXTRACTION RESPONSE
# ============================================================

def generate_curriculum_json(
    syllabus_text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
    config: Optional[
        ExtractorConfig
    ] = None,
) -> Dict[str, Any]:
    """
    Send syllabus text to Groq/Llama and return
    parsed JSON.
    """

    prepared_text = prepare_input_text(
        syllabus_text
    )


    prompt = build_curriculum_prompt(

        syllabus_text=prepared_text,

        source_file=source_file,

        source_type=source_type,

    )


    raw_response = call_groq_with_retry(

        prompt=prompt,

        system_prompt=CURRICULUM_SYSTEM_PROMPT,

        config=config,

    )


    parsed = extract_json_object(
        raw_response
    )


    if parsed is None:

        logger.error(

            (
                "Unable to parse Groq response "
                "as JSON. Raw response:\n%s",
                raw_response[:5000],
            )

        )


        raise ValueError(

            (
                "LLM returned invalid JSON. "
                "Please retry extraction."
            )

        )


    return parsed


# ============================================================
# 30. END OF CHUNK 2
# ============================================================
# ============================================================
# curriculum/extractor.py
# CHUNK 3/8
#
# RAW LLM JSON NORMALIZATION
# ============================================================


# ============================================================
# 31. GENERIC DICTIONARY HELPER
# ============================================================

def ensure_dict(
    value: Any,
) -> Dict[str, Any]:
    """
    Safely convert a value into a dictionary.
    """

    if isinstance(
        value,
        dict,
    ):
        return value


    return {}


# ============================================================
# 32. GENERIC LIST HELPER
# ============================================================

def ensure_list(
    value: Any,
) -> List[Any]:
    """
    Safely convert arbitrary data into a list.
    """

    if value is None:

        return []


    if isinstance(
        value,
        list,
    ):

        return value


    if isinstance(
        value,
        tuple,
    ):

        return list(
            value
        )


    return [value]


# ============================================================
# 33. GET FIRST AVAILABLE KEY
# ============================================================

def get_first(
    data: Dict[str, Any],
    keys: List[str],
    default: Any = None,
) -> Any:
    """
    Return the first available value from multiple
    possible keys.

    Useful because LLMs may return:

        module
        modules
        units
        course_modules
    """

    for key in keys:

        if key in data:

            value = data[key]


            if value is not None:

                return value


    return default


# ============================================================
# 34. NORMALIZE KEY
# ============================================================

def normalize_key(
    value: Any,
) -> str:
    """
    Normalize a JSON key for comparison.
    """

    if value is None:

        return ""


    text = str(
        value
    ).strip().lower()


    text = text.replace(
        "-",
        "_",
    )


    text = text.replace(
        " ",
        "_",
    )


    return text


# ============================================================
# 35. NORMALIZE DICTIONARY KEYS
# ============================================================

def normalize_dict_keys(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize dictionary keys.

    Example:

        "Course Name"
            →
        "course_name"
    """

    result: Dict[
        str,
        Any
    ] = {}


    for key, value in data.items():

        normalized = normalize_key(
            key
        )


        result[normalized] = value


    return result


# ============================================================
# 36. NORMALIZE ROOT RESPONSE
# ============================================================

def normalize_root_payload(
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize the top-level LLM response.

    Supports responses such as:

        {
            "curriculum": {...}
        }

    or:

        {
            "syllabus": {...}
        }

    or a direct curriculum object.
    """

    payload = ensure_dict(
        payload
    )


    # --------------------------------------------------------
    # Check nested containers
    # --------------------------------------------------------

    for key in [

        "curriculum",

        "syllabus",

        "course",

        "course_curriculum",

        "structured_curriculum",

        "result",

        "data",

    ]:

        nested = payload.get(
            key
        )


        if isinstance(
            nested,
            dict,
        ):

            return normalize_dict_keys(
                nested
            )


    return normalize_dict_keys(
        payload
    )


# ============================================================
# 37. NORMALIZE METADATA
# ============================================================

def normalize_metadata(
    raw: Any,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Normalize course metadata.
    """

    data = normalize_dict_keys(
        ensure_dict(
            raw
        )
    )


    result = {

        "university":
            get_first(
                data,
                [
                    "university",
                    "university_name",
                    "institution",
                    "institution_name",
                ],
            ),

        "college":
            get_first(
                data,
                [
                    "college",
                    "college_name",
                    "institute",
                    "institute_name",
                ],
            ),

        "department":
            get_first(
                data,
                [
                    "department",
                    "department_name",
                ],
            ),

        "faculty_name":
            get_first(
                data,
                [
                    "faculty_name",
                    "faculty",
                    "instructor",
                    "teacher",
                ],
            ),

        "program":
            get_first(
                data,
                [
                    "program",
                    "program_name",
                    "degree",
                    "degree_program",
                ],
            ),

        "branch":
            get_first(
                data,
                [
                    "branch",
                    "branch_name",
                    "specialization",
                    "specialisation",
                ],
            ),

        "course_name":
            get_first(
                data,
                [
                    "course_name",
                    "course",
                    "subject",
                    "subject_name",
                ],
            ),

        "subject_name":
            get_first(
                data,
                [
                    "subject_name",
                    "subject",
                    "course_name",
                ],
            ),

        "course_code":
            get_first(
                data,
                [
                    "course_code",
                    "course_id",
                    "subject_code",
                    "code",
                ],
            ),

        "semester":
            get_first(
                data,
                [
                    "semester",
                    "sem",
                    "term",
                ],
            ),

        "academic_year":
            get_first(
                data,
                [
                    "academic_year",
                    "academic_session",
                    "year",
                ],
            ),

        "regulation":
            get_first(
                data,
                [
                    "regulation",
                    "regulation_year",
                    "curriculum_regulation",
                ],
            ),

        "credits":
            get_first(
                data,
                [
                    "credits",
                    "credit",
                    "course_credits",
                ],
            ),

        "lecture_hours":
            get_first(
                data,
                [
                    "lecture_hours",
                    "lectures",
                    "theory_hours",
                    "l_hours",
                ],
            ),

        "tutorial_hours":
            get_first(
                data,
                [
                    "tutorial_hours",
                    "tutorial",
                    "t_hours",
                ],
            ),

        "practical_hours":
            get_first(
                data,
                [
                    "practical_hours",
                    "lab_hours",
                    "practical",
                    "p_hours",
                ],
            ),

        "total_hours":
            get_first(
                data,
                [
                    "total_hours",
                    "contact_hours",
                    "hours",
                ],
            ),

        "prerequisites":
            clean_string_list(
                get_first(
                    data,
                    [
                        "prerequisites",
                        "prerequisite",
                        "pre_requisites",
                    ],
                    [],
                )
            ),

        "course_type":
            get_first(
                data,
                [
                    "course_type",
                    "type",
                    "category",
                ],
            ),

        "source_file":
            source_file
            or get_first(
                data,
                [
                    "source_file",
                    "filename",
                ],
            ),

        "source_type":
            source_type
            or get_first(
                data,
                [
                    "source_type",
                    "document_type",
                ],
            ),

        "extraction_confidence":
            clamp_score(
                get_first(
                    data,
                    [
                        "extraction_confidence",
                        "confidence",
                    ],
                    0,
                )
            ),

    }


    # --------------------------------------------------------
    # Numeric fields
    # --------------------------------------------------------

    for key in [

        "credits",

        "lecture_hours",

        "tutorial_hours",

        "practical_hours",

        "total_hours",

    ]:

        if result[key] is not None:

            result[key] = safe_float(
                result[key]
            )


    # --------------------------------------------------------
    # String fields
    # --------------------------------------------------------

    for key in [

        "university",

        "college",

        "department",

        "faculty_name",

        "program",

        "branch",

        "course_name",

        "subject_name",

        "course_code",

        "semester",

        "academic_year",

        "regulation",

        "course_type",

        "source_file",

        "source_type",

    ]:

        if result[key] is not None:

            result[key] = clean_text(
                result[key]
            )


    return result


# ============================================================
# 38. NORMALIZE OBJECTIVES
# ============================================================

def normalize_objectives(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize course objectives.
    """

    result = []


    for index, item in enumerate(

        ensure_list(
            raw
        ),

        start=1,

    ):

        if isinstance(
            item,
            str,
        ):

            result.append({

                "code":
                    f"OBJ{index}",

                "description":
                    clean_text(
                        item
                    ),

                "bloom_level":
                    None,

            })

            continue


        data = normalize_dict_keys(
            ensure_dict(
                item
            )
        )


        description = get_first(

            data,

            [
                "description",
                "objective",
                "text",
                "statement",
            ],

            "",

        )


        if not description:

            continue


        result.append({

            "code":
                get_first(
                    data,
                    [
                        "code",
                        "id",
                        "objective_id",
                    ],
                    f"OBJ{index}",
                ),

            "description":
                clean_text(
                    description
                ),

            "bloom_level":
                normalize_bloom_level(
                    get_first(
                        data,
                        [
                            "bloom_level",
                            "bloom",
                            "cognitive_level",
                        ],
                    )
                ),

        })


    return result


# ============================================================
# 39. NORMALIZE BLOOM LEVEL
# ============================================================

def normalize_bloom_level(
    value: Any,
) -> Optional[str]:
    """
    Normalize Bloom taxonomy values.
    """

    if value is None:

        return None


    text = clean_text(
        value
    ).lower()


    mapping = {

        "remember":
            "Remember",

        "recall":
            "Remember",

        "knowledge":
            "Remember",

        "understand":
            "Understand",

        "comprehend":
            "Understand",

        "explain":
            "Understand",

        "apply":
            "Apply",

        "application":
            "Apply",

        "use":
            "Apply",

        "analyze":
            "Analyze",

        "analyse":
            "Analyze",

        "analysis":
            "Analyze",

        "evaluate":
            "Evaluate",

        "evaluation":
            "Evaluate",

        "assess":
            "Evaluate",

        "create":
            "Create",

        "creation":
            "Create",

        "design":
            "Create",

    }


    for key, normalized in mapping.items():

        if key in text:

            return normalized


    return "Understand"


# ============================================================
# 40. NORMALIZE DIFFICULTY
# ============================================================

def normalize_difficulty(
    value: Any,
) -> str:
    """
    Normalize difficulty values.
    """

    if value is None:

        return "Intermediate"


    text = clean_text(
        value
    ).lower()


    if any(

        word in text

        for word in [
            "beginner",
            "basic",
            "introductory",
            "foundation",
        ]

    ):

        return "Beginner"


    if any(

        word in text

        for word in [
            "expert",
            "specialist",
            "master",
        ]

    ):

        return "Expert"


    if "advanced" in text:

        return "Advanced"


    return "Intermediate"


# ============================================================
# 41. NORMALIZE LEARNING TYPE
# ============================================================

def normalize_learning_type(
    value: Any,
) -> str:
    """
    Normalize learning activity types.
    """

    if value is None:

        return "Theory"


    text = clean_text(
        value
    ).lower()


    if any(

        word in text

        for word in [
            "lab",
            "laboratory",
        ]

    ):

        return "Lab"


    if any(

        word in text

        for word in [
            "practical",
            "hands-on",
            "hands on",
        ]

    ):

        return "Practical"


    if "project" in text:

        return "Project"


    if any(

        word in text

        for word in [
            "case study",
            "case-study",
        ]

    ):

        return "Case Study"


    if "research" in text:

        return "Research"


    if "discussion" in text:

        return "Discussion"


    if "assessment" in text:

        return "Assessment"


    return "Theory"


# ============================================================
# 42. NORMALIZE MODULES
# ============================================================

def normalize_modules(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize modules/units.

    Supports:

        modules
        units
        course_modules
        syllabus_modules
    """

    raw_modules = ensure_list(
        raw
    )


    result = []


    for index, item in enumerate(

        raw_modules,

        start=1,

    ):

        if isinstance(
            item,
            str,
        ):

            result.append({

                "module_id":
                    f"M{index}",

                "module_name":
                    clean_text(
                        item
                    ),

                "sequence":
                    index,

                "topics":
                    [],

            })

            continue


        data = normalize_dict_keys(
            ensure_dict(
                item
            )
        )


        module_name = get_first(

            data,

            [
                "module_name",
                "module",
                "unit_name",
                "unit",
                "chapter_name",
                "chapter",
                "title",
                "name",
            ],

            f"Module {index}",

        )


        topics = get_first(

            data,

            [
                "topics",
                "topic",
                "subtopics",
                "contents",
                "content",
            ],

            [],

        )


        result.append({

            "module_id":
                get_first(
                    data,
                    [
                        "module_id",
                        "unit_id",
                        "chapter_id",
                        "id",
                        "code",
                    ],
                    f"M{index}",
                ),

            "module_name":
                clean_text(
                    module_name
                ),

            "description":
                clean_text(
                    get_first(
                        data,
                        [
                            "description",
                            "summary",
                        ],
                        "",
                    )
                )
                or None,

            "sequence":
                safe_int(
                    get_first(
                        data,
                        [
                            "sequence",
                            "order",
                            "number",
                            "module_number",
                        ],
                        index,
                    ),
                    index,
                ),

            "hours":
                safe_float(
                    get_first(
                        data,
                        [
                            "hours",
                            "teaching_hours",
                            "contact_hours",
                        ],
                        0,
                    )
                ),

            "credits":
                (
                    safe_float(
                        get_first(
                            data,
                            [
                                "credits",
                                "credit",
                            ],
                        )
                    )
                    if get_first(
                        data,
                        [
                            "credits",
                            "credit",
                        ],
                    )
                    is not None
                    else None
                ),

            "topics":
                normalize_topics(
                    topics
                ),

            "concepts":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "concepts",
                        ],
                        [],
                    )
                ),

            "skills":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "skills",
                        ],
                        [],
                    )
                ),

            "tools":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "tools",
                        ],
                        [],
                    )
                ),

            "technologies":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "technologies",
                            "technology",
                            "frameworks",
                        ],
                        [],
                    )
                ),

            "projects":
                normalize_projects(
                    get_first(
                        data,
                        [
                            "projects",
                            "project",
                        ],
                        [],
                    )
                ),

            "case_studies":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "case_studies",
                            "case_study",
                            "case_studies_examples",
                        ],
                        [],
                    )
                ),

            "learning_objectives":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "learning_objectives",
                            "objectives",
                            "learning_outcomes",
                        ],
                        [],
                    )
                ),

            "prerequisites":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "prerequisites",
                            "prerequisite",
                        ],
                        [],
                    )
                ),

            "bloom_levels":
                normalize_bloom_levels(
                    get_first(
                        data,
                        [
                            "bloom_levels",
                            "bloom",
                        ],
                        [],
                    )
                ),

            "difficulty":
                normalize_difficulty(
                    get_first(
                        data,
                        [
                            "difficulty",
                            "level",
                        ],
                        "Intermediate",
                    )
                ),

            "industry_relevance_score":
                clamp_score(
                    get_first(
                        data,
                        [
                            "industry_relevance_score",
                            "industry_relevance",
                        ],
                        0,
                    )
                ),

            "academic_relevance_score":
                clamp_score(
                    get_first(
                        data,
                        [
                            "academic_relevance_score",
                            "academic_relevance",
                        ],
                        50,
                    )
                ),

            "currency_score":
                clamp_score(
                    get_first(
                        data,
                        [
                            "currency_score",
                            "current_score",
                        ],
                        50,
                    )
                ),

            "recommended":
                bool(
                    get_first(
                        data,
                        [
                            "recommended",
                        ],
                        False,
                    )
                ),

            "enhancement_notes":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "enhancement_notes",
                            "recommendations",
                        ],
                        [],
                    )
                ),

            "co_mapping":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "co_mapping",
                            "co_mappings",
                            "course_outcomes",
                        ],
                        [],
                    )
                ),

        })


    return result


# ============================================================
# 43. NORMALIZE BLOOM LEVEL LIST
# ============================================================

def normalize_bloom_levels(
    values: Any,
) -> List[str]:
    """
    Normalize a list of Bloom levels.
    """

    result = []


    for value in ensure_list(
        values
    ):

        normalized = normalize_bloom_level(
            value
        )


        if normalized and normalized not in result:

            result.append(
                normalized
            )


    return result


# ============================================================
# 44. NORMALIZE TOPICS
# ============================================================

def normalize_topics(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize topics/subtopics.
    """

    result = []


    for index, item in enumerate(

        ensure_list(
            raw
        ),

        start=1,

    ):

        if isinstance(
            item,
            str,
        ):

            result.append({

                "topic_id":
                    f"T{index}",

                "topic_name":
                    clean_text(
                        item
                    ),

                "sequence":
                    index,

                "hours":
                    0,

                "learning_type":
                    "Theory",

                "difficulty":
                    "Intermediate",

                "bloom_level":
                    "Understand",

            })

            continue


        data = normalize_dict_keys(
            ensure_dict(
                item
            )
        )


        topic_name = get_first(

            data,

            [
                "topic_name",
                "topic",
                "subtopic_name",
                "subtopic",
                "title",
                "name",
            ],

            f"Topic {index}",

        )


        result.append({

            "topic_id":
                get_first(
                    data,
                    [
                        "topic_id",
                        "subtopic_id",
                        "id",
                    ],
                    f"T{index}",
                ),

            "topic_name":
                clean_text(
                    topic_name
                ),

            "description":
                clean_text(
                    get_first(
                        data,
                        [
                            "description",
                            "summary",
                        ],
                        "",
                    )
                )
                or None,

            "hours":
                safe_float(
                    get_first(
                        data,
                        [
                            "hours",
                            "teaching_hours",
                        ],
                        0,
                    )
                ),

            "sequence":
                safe_int(
                    get_first(
                        data,
                        [
                            "sequence",
                            "order",
                            "number",
                        ],
                        index,
                    ),
                    index,
                ),

            "learning_type":
                normalize_learning_type(
                    get_first(
                        data,
                        [
                            "learning_type",
                            "type",
                            "activity_type",
                        ],
                        "Theory",
                    )
                ),

            "difficulty":
                normalize_difficulty(
                    get_first(
                        data,
                        [
                            "difficulty",
                            "level",
                        ],
                        "Intermediate",
                    )
                ),

            "bloom_level":
                normalize_bloom_level(
                    get_first(
                        data,
                        [
                            "bloom_level",
                            "bloom",
                            "cognitive_level",
                        ],
                        "Understand",
                    )
                ),

            "concepts":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "concepts",
                            "concept",
                        ],
                        [],
                    )
                ),

            "skills":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "skills",
                            "skill",
                        ],
                        [],
                    )
                ),

            "tools":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "tools",
                            "tool",
                        ],
                        [],
                    )
                ),

            "technologies":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "technologies",
                            "technology",
                            "frameworks",
                        ],
                        [],
                    )
                ),

            "prerequisites":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "prerequisites",
                            "prerequisite",
                        ],
                        [],
                    )
                ),

            "learning_objectives":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "learning_objectives",
                            "objectives",
                        ],
                        [],
                    )
                ),

            "projects":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "projects",
                            "project",
                        ],
                        [],
                    )
                ),

            "case_studies":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "case_studies",
                            "case_study",
                        ],
                        [],
                    )
                ),

            "references":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "references",
                            "reference",
                            "resources",
                        ],
                        [],
                    )
                ),

            "industry_relevance_score":
                clamp_score(
                    get_first(
                        data,
                        [
                            "industry_relevance_score",
                            "industry_relevance",
                        ],
                        0,
                    )
                ),

            "importance_score":
                clamp_score(
                    get_first(
                        data,
                        [
                            "importance_score",
                            "importance",
                        ],
                        50,
                    )
                ),

            "current":
                bool(
                    get_first(
                        data,
                        [
                            "current",
                            "is_current",
                        ],
                        True,
                    )
                ),

            "recommended_enhancement":
                bool(
                    get_first(
                        data,
                        [
                            "recommended_enhancement",
                            "enhancement_recommended",
                        ],
                        False,
                    )
                ),

        })


    return result


# ============================================================
# 45. NORMALIZE PROJECTS
# ============================================================

def normalize_projects(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize projects.
    """

    result = []


    for item in ensure_list(
        raw
    ):

        if isinstance(
            item,
            str,
        ):

            title = clean_text(
                item
            )


            if title:

                result.append({

                    "title":
                        title,

                    "project_type":
                        "Project",

                })


            continue


        data = normalize_dict_keys(
            ensure_dict(
                item
            )
        )


        title = get_first(

            data,

            [
                "title",
                "project_title",
                "project_name",
                "name",
            ],

            "",

        )


        if not title:

            continue


        result.append({

            "title":
                clean_text(
                    title
                ),

            "description":
                clean_text(
                    get_first(
                        data,
                        [
                            "description",
                            "summary",
                        ],
                        "",
                    )
                )
                or None,

            "project_type":
                normalize_learning_type(
                    get_first(
                        data,
                        [
                            "project_type",
                            "type",
                        ],
                        "Project",
                    )
                ),

            "difficulty":
                normalize_difficulty(
                    get_first(
                        data,
                        [
                            "difficulty",
                            "level",
                        ],
                        "Intermediate",
                    )
                ),

            "duration_hours":
                (
                    safe_float(
                        get_first(
                            data,
                            [
                                "duration_hours",
                                "hours",
                            ],
                        )
                    )
                    if get_first(
                        data,
                        [
                            "duration_hours",
                            "hours",
                        ],
                    )
                    is not None
                    else None
                ),

            "skills":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "skills",
                        ],
                        [],
                    )
                ),

            "concepts":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "concepts",
                        ],
                        [],
                    )
                ),

            "tools":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "tools",
                        ],
                        [],
                    )
                ),

            "technologies":
                clean_string_list(
                    get_first(
                        data,
                        [
                            "technologies",
                            "technology",
                        ],
                        [],
                    )
                ),

            "industry_relevance_score":
                clamp_score(
                    get_first(
                        data,
                        [
                            "industry_relevance_score",
                            "industry_relevance",
                        ],
                        0,
                    )
                ),

            "portfolio_ready":
                bool(
                    get_first(
                        data,
                        [
                            "portfolio_ready",
                        ],
                        False,
                    )
                ),

            "real_world_problem":
                bool(
                    get_first(
                        data,
                        [
                            "real_world_problem",
                            "real_world",
                        ],
                        False,
                    )
                ),

        })


    return result


# ============================================================
# END OF CHUNK 3
# ============================================================
# ============================================================
# curriculum/extractor.py
# CHUNK 4/8
#
# CONCEPT / SKILL / TECHNOLOGY / OUTCOME NORMALIZATION
# ============================================================


# ============================================================
# 46. NORMALIZE CONCEPTS
# ============================================================

def normalize_concepts(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize curriculum concepts.

    Supports both:

        ["Python", "Regression"]

    and:

        [
            {
                "name": "Regression",
                "description": "...",
                "concept_type": "Core"
            }
        ]
    """

    result: List[Dict[str, Any]] = []

    seen = set()


    for item in ensure_list(raw):

        if isinstance(item, str):

            name = clean_text(item)

            if not name:
                continue

            key = name.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                {
                    "name": name,
                    "description": None,
                    "concept_type": "Core",
                    "importance_score": 50,
                    "industry_relevance_score": 0,
                    "difficulty": "Intermediate",
                    "prerequisites": [],
                    "related_concepts": [],
                    "emerging": False,
                    "industry_used": False,
                    "source_references": [],
                }
            )

            continue


        data = normalize_dict_keys(
            ensure_dict(item)
        )


        name = get_first(
            data,
            [
                "name",
                "concept_name",
                "concept",
                "title",
            ],
            "",
        )


        name = clean_text(name)


        if not name:
            continue


        key = name.lower()

        if key in seen:
            continue

        seen.add(key)


        result.append(
            {
                "name": name,

                "description": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "description",
                                "summary",
                            ],
                            "",
                        )
                    )
                    or None
                ),

                "concept_type": normalize_concept_type(
                    get_first(
                        data,
                        [
                            "concept_type",
                            "type",
                            "category",
                        ],
                        "Core",
                    )
                ),

                "importance_score": clamp_score(
                    get_first(
                        data,
                        [
                            "importance_score",
                            "importance",
                        ],
                        50,
                    )
                ),

                "industry_relevance_score": clamp_score(
                    get_first(
                        data,
                        [
                            "industry_relevance_score",
                            "industry_relevance",
                        ],
                        0,
                    )
                ),

                "difficulty": normalize_difficulty(
                    get_first(
                        data,
                        [
                            "difficulty",
                            "level",
                        ],
                        "Intermediate",
                    )
                ),

                "prerequisites": clean_string_list(
                    get_first(
                        data,
                        [
                            "prerequisites",
                            "prerequisite",
                        ],
                        [],
                    )
                ),

                "related_concepts": clean_string_list(
                    get_first(
                        data,
                        [
                            "related_concepts",
                            "related",
                        ],
                        [],
                    )
                ),

                "emerging": bool(
                    get_first(
                        data,
                        [
                            "emerging",
                            "is_emerging",
                        ],
                        False,
                    )
                ),

                "industry_used": bool(
                    get_first(
                        data,
                        [
                            "industry_used",
                            "used_in_industry",
                        ],
                        False,
                    )
                ),

                "source_references": clean_string_list(
                    get_first(
                        data,
                        [
                            "source_references",
                            "references",
                            "sources",
                        ],
                        [],
                    )
                ),
            }
        )


    return result


# ============================================================
# 47. NORMALIZE CONCEPT TYPE
# ============================================================

def normalize_concept_type(
    value: Any,
) -> str:
    """
    Normalize concept classification.
    """

    if value is None:
        return "Core"


    text = clean_text(value).lower()


    if any(
        word in text
        for word in [
            "fundamental",
            "foundation",
            "basic",
        ]
    ):
        return "Fundamental"


    if "advanced" in text:
        return "Advanced"


    if any(
        word in text
        for word in [
            "emerging",
            "new",
            "trending",
        ]
    ):
        return "Emerging"


    if "industry" in text:
        return "Industry"


    if "practical" in text:
        return "Practical"


    if "prerequisite" in text:
        return "Prerequisite"


    if "related" in text:
        return "Related"


    return "Core"


# ============================================================
# 48. NORMALIZE SKILLS
# ============================================================

def normalize_skills(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize curriculum skills.
    """

    result: List[Dict[str, Any]] = []

    seen = set()


    for item in ensure_list(raw):

        if isinstance(item, str):

            name = clean_text(item)

            if not name:
                continue

            key = name.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                {
                    "name": name,
                    "normalized_name": normalize_skill_name(name),
                    "category": "Other",
                    "description": None,
                    "proficiency_level": "Intermediate",
                    "importance_score": 50,
                    "industry_relevance_score": 0,
                    "years_relevance": None,
                    "aliases": [],
                    "source_topics": [],
                }
            )

            continue


        data = normalize_dict_keys(
            ensure_dict(item)
        )


        name = get_first(
            data,
            [
                "name",
                "skill_name",
                "skill",
                "title",
            ],
            "",
        )


        name = clean_text(name)


        if not name:
            continue


        key = name.lower()

        if key in seen:
            continue

        seen.add(key)


        result.append(
            {
                "name": name,

                "normalized_name": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "normalized_name",
                                "canonical_name",
                                "canonical",
                            ],
                            normalize_skill_name(name),
                        )
                    )
                    or normalize_skill_name(name)
                ),

                "category": normalize_skill_category(
                    get_first(
                        data,
                        [
                            "category",
                            "skill_category",
                            "type",
                        ],
                        "Other",
                    )
                ),

                "description": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "description",
                                "summary",
                            ],
                            "",
                        )
                    )
                    or None
                ),

                "proficiency_level": normalize_difficulty(
                    get_first(
                        data,
                        [
                            "proficiency_level",
                            "level",
                            "difficulty",
                        ],
                        "Intermediate",
                    )
                ),

                "importance_score": clamp_score(
                    get_first(
                        data,
                        [
                            "importance_score",
                            "importance",
                        ],
                        50,
                    )
                ),

                "industry_relevance_score": clamp_score(
                    get_first(
                        data,
                        [
                            "industry_relevance_score",
                            "industry_relevance",
                        ],
                        0,
                    )
                ),

                "years_relevance": (
                    safe_float(
                        get_first(
                            data,
                            [
                                "years_relevance",
                                "years",
                            ],
                        )
                    )
                    if get_first(
                        data,
                        [
                            "years_relevance",
                            "years",
                        ],
                    ) is not None
                    else None
                ),

                "aliases": clean_string_list(
                    get_first(
                        data,
                        [
                            "aliases",
                            "alternative_names",
                        ],
                        [],
                    )
                ),

                "source_topics": clean_string_list(
                    get_first(
                        data,
                        [
                            "source_topics",
                            "topics",
                        ],
                        [],
                    )
                ),
            }
        )


    return result


# ============================================================
# 49. NORMALIZE SKILL NAME
# ============================================================

def normalize_skill_name(
    name: str,
) -> str:
    """
    Produce a simple canonical skill name.

    This is intentionally conservative.
    Detailed taxonomy matching belongs in:
        industry/taxonomy.py
    """

    text = clean_text(name)

    aliases = {
        "python programming": "Python",
        "python programming language": "Python",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "artificial intelligence": "Artificial Intelligence",
        "ai": "Artificial Intelligence",
        "natural language processing": "NLP",
        "natural language understanding": "NLU",
        "generative artificial intelligence": "Generative AI",
        "generative ai": "Generative AI",
        "large language models": "Large Language Models",
        "large language model": "Large Language Models",
        "llm": "Large Language Models",
        "sql programming": "SQL",
        "structured query language": "SQL",
        "data analysis": "Data Analysis",
        "data analytics": "Data Analytics",
        "computer vision": "Computer Vision",
        "cloud computing": "Cloud Computing",
        "devops": "DevOps",
        "mlops": "MLOps",
    }


    return aliases.get(
        text.lower(),
        text,
    )


# ============================================================
# 50. NORMALIZE SKILL CATEGORY
# ============================================================

def normalize_skill_category(
    value: Any,
) -> str:
    """
    Normalize skill categories.
    """

    if value is None:
        return "Other"


    text = clean_text(value).lower()


    mappings = [
        (
            [
                "program",
                "coding",
                "programming",
            ],
            "Programming",
        ),

        (
            [
                "data",
                "analytics",
                "analysis",
            ],
            "Data",
        ),

        (
            [
                "machine learning",
                "ml",
            ],
            "Machine Learning",
        ),

        (
            [
                "deep learning",
                "dl",
            ],
            "Deep Learning",
        ),

        (
            [
                "generative ai",
                "genai",
            ],
            "Generative AI",
        ),

        (
            [
                "agentic",
                "agent",
            ],
            "Agentic AI",
        ),

        (
            [
                "cloud",
                "aws",
                "azure",
                "gcp",
            ],
            "Cloud",
        ),

        (
            [
                "devops",
            ],
            "DevOps",
        ),

        (
            [
                "mlops",
            ],
            "MLOps",
        ),

        (
            [
                "database",
                "sql",
            ],
            "Database",
        ),

        (
            [
                "web",
                "frontend",
                "backend",
            ],
            "Web",
        ),

        (
            [
                "security",
                "cyber",
            ],
            "Cybersecurity",
        ),

        (
            [
                "business",
                "management",
            ],
            "Business",
        ),

        (
            [
                "soft skill",
                "communication",
                "leadership",
            ],
            "Soft Skill",
        ),

        (
            [
                "tool",
                "software",
            ],
            "Tool",
        ),
    ]


    for keywords, category in mappings:

        if any(
            keyword in text
            for keyword in keywords
        ):
            return category


    return "Other"


# ============================================================
# 51. NORMALIZE TOOLS
# ============================================================

def normalize_tools(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize software tools.
    """

    result: List[Dict[str, Any]] = []

    seen = set()


    for item in ensure_list(raw):

        if isinstance(item, str):

            name = clean_text(item)

            if not name:
                continue

            key = name.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                {
                    "name": name,
                    "category": None,
                    "purpose": None,
                    "version": None,
                    "industry_relevance_score": 0,
                    "recommended": False,
                }
            )

            continue


        data = normalize_dict_keys(
            ensure_dict(item)
        )


        name = get_first(
            data,
            [
                "name",
                "tool_name",
                "tool",
                "title",
            ],
            "",
        )


        name = clean_text(name)


        if not name:
            continue


        key = name.lower()

        if key in seen:
            continue

        seen.add(key)


        result.append(
            {
                "name": name,

                "category": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "category",
                                "type",
                            ],
                            "",
                        )
                    )
                    or None
                ),

                "purpose": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "purpose",
                                "use",
                                "description",
                            ],
                            "",
                        )
                    )
                    or None
                ),

                "version": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "version",
                            ],
                            "",
                        )
                    )
                    or None
                ),

                "industry_relevance_score": clamp_score(
                    get_first(
                        data,
                        [
                            "industry_relevance_score",
                            "industry_relevance",
                        ],
                        0,
                    )
                ),

                "recommended": bool(
                    get_first(
                        data,
                        [
                            "recommended",
                        ],
                        False,
                    )
                ),
            }
        )


    return result


# ============================================================
# 52. NORMALIZE TECHNOLOGIES
# ============================================================

def normalize_technologies(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize technologies, frameworks,
    platforms and ecosystems.
    """

    result: List[Dict[str, Any]] = []

    seen = set()


    for item in ensure_list(raw):

        if isinstance(item, str):

            name = clean_text(item)

            if not name:
                continue

            key = name.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                {
                    "name": name,
                    "category": None,
                    "description": None,
                    "current_version": None,
                    "industry_relevance_score": 0,
                    "emerging": False,
                    "recommended": False,
                }
            )

            continue


        data = normalize_dict_keys(
            ensure_dict(item)
        )


        name = get_first(
            data,
            [
                "name",
                "technology_name",
                "technology",
                "framework",
                "platform",
                "title",
            ],
            "",
        )


        name = clean_text(name)


        if not name:
            continue


        key = name.lower()

        if key in seen:
            continue

        seen.add(key)


        result.append(
            {
                "name": name,

                "category": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "category",
                                "type",
                            ],
                            "",
                        )
                    )
                    or None
                ),

                "description": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "description",
                                "summary",
                            ],
                            "",
                        )
                    )
                    or None
                ),

                "current_version": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "current_version",
                                "version",
                            ],
                            "",
                        )
                    )
                    or None
                ),

                "industry_relevance_score": clamp_score(
                    get_first(
                        data,
                        [
                            "industry_relevance_score",
                            "industry_relevance",
                        ],
                        0,
                    )
                ),

                "emerging": bool(
                    get_first(
                        data,
                        [
                            "emerging",
                            "is_emerging",
                        ],
                        False,
                    )
                ),

                "recommended": bool(
                    get_first(
                        data,
                        [
                            "recommended",
                        ],
                        False,
                    )
                ),
            }
        )


    return result


# ============================================================
# 53. NORMALIZE COURSE OUTCOMES
# ============================================================

def normalize_course_outcomes(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize CO / Course Outcomes.

    Supports:

        CO1: Explain...
        CO2: Apply...

    and structured objects.
    """

    result: List[Dict[str, Any]] = []


    # --------------------------------------------------------
    # Dictionary form
    # --------------------------------------------------------

    if isinstance(
        raw,
        dict,
    ):

        converted = []

        for code, description in raw.items():

            converted.append(
                {
                    "code": code,
                    "description": description,
                }
            )

        raw = converted


    for index, item in enumerate(
        ensure_list(raw),
        start=1,
    ):

        if isinstance(
            item,
            str,
        ):

            text = clean_text(item)


            match = re.match(
                r"^(CO\s*[-_]?\s*\d+)\s*[:\-–]\s*(.*)$",
                text,
                re.IGNORECASE,
            )


            if match:

                code = (
                    match.group(1)
                    .upper()
                    .replace(" ", "")
                    .replace("_", "")
                    .replace("-", "")
                )

                description = clean_text(
                    match.group(2)
                )

            else:

                code = f"CO{index}"

                description = text


            result.append(
                {
                    "code": code,
                    "description": description,
                    "bloom_level": "Understand",
                    "knowledge_area": None,
                    "mapped_modules": [],
                    "mapped_topics": [],
                    "assessment_methods": [],
                }
            )

            continue


        data = normalize_dict_keys(
            ensure_dict(item)
        )


        code = get_first(
            data,
            [
                "code",
                "co_code",
                "id",
                "outcome_code",
            ],
            f"CO{index}",
        )


        description = get_first(
            data,
            [
                "description",
                "outcome",
                "statement",
                "text",
            ],
            "",
        )


        description = clean_text(
            description
        )


        if not description:
            continue


        result.append(
            {
                "code": clean_text(code).upper(),

                "description": description,

                "bloom_level": normalize_bloom_level(
                    get_first(
                        data,
                        [
                            "bloom_level",
                            "bloom",
                        ],
                        "Understand",
                    )
                ),

                "knowledge_area": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "knowledge_area",
                                "area",
                            ],
                            "",
                        )
                    )
                    or None
                ),

                "mapped_modules": clean_string_list(
                    get_first(
                        data,
                        [
                            "mapped_modules",
                            "modules",
                        ],
                        [],
                    )
                ),

                "mapped_topics": clean_string_list(
                    get_first(
                        data,
                        [
                            "mapped_topics",
                            "topics",
                        ],
                        [],
                    )
                ),

                "assessment_methods": clean_string_list(
                    get_first(
                        data,
                        [
                            "assessment_methods",
                            "assessment",
                            "methods",
                        ],
                        [],
                    )
                ),
            }
        )


    return result


# ============================================================
# 54. NORMALIZE PROGRAM OUTCOMES
# ============================================================

def normalize_program_outcomes(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize Program Outcomes.
    """

    return normalize_outcome_list(
        raw,
        prefix="PO",
    )


# ============================================================
# 55. NORMALIZE PROGRAM SPECIFIC OUTCOMES
# ============================================================

def normalize_program_specific_outcomes(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize Program Specific Outcomes.
    """

    return normalize_outcome_list(
        raw,
        prefix="PSO",
    )


# ============================================================
# 56. GENERIC OUTCOME LIST NORMALIZER
# ============================================================

def normalize_outcome_list(
    raw: Any,
    prefix: str,
) -> List[Dict[str, Any]]:
    """
    Normalize PO / PSO structures.
    """

    result: List[Dict[str, Any]] = []


    if isinstance(
        raw,
        dict,
    ):

        raw = [

            {
                "code": code,
                "description": description,
            }

            for code, description in raw.items()

        ]


    for index, item in enumerate(
        ensure_list(raw),
        start=1,
    ):

        if isinstance(
            item,
            str,
        ):

            text = clean_text(item)


            match = re.match(
                rf"^({prefix}\s*[-_]?\s*\d+)\s*[:\-–]\s*(.*)$",
                text,
                re.IGNORECASE,
            )


            if match:

                code = (
                    match.group(1)
                    .upper()
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("_", "")
                )

                description = clean_text(
                    match.group(2)
                )

            else:

                code = f"{prefix}{index}"

                description = text


            if description:

                result.append(
                    {
                        "code": code,
                        "description": description,
                        "category": None,
                    }
                )

            continue


        data = normalize_dict_keys(
            ensure_dict(item)
        )


        code = clean_text(
            get_first(
                data,
                [
                    "code",
                    "id",
                    "outcome_code",
                ],
                f"{prefix}{index}",
            )
        )


        description = clean_text(
            get_first(
                data,
                [
                    "description",
                    "outcome",
                    "statement",
                    "text",
                ],
                "",
            )
        )


        if not description:
            continue


        result.append(
            {
                "code": code.upper(),

                "description": description,

                "category": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "category",
                                "type",
                            ],
                            "",
                        )
                    )
                    or None
                ),
            }
        )


    return result


# ============================================================
# 57. NORMALIZE CO-PO MAPPINGS
# ============================================================

def normalize_co_po_mappings(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize CO-PO mapping data.

    Supports:

        [
            {
                "co_code": "CO1",
                "po_code": "PO1",
                "correlation": 3
            }
        ]

    and matrix-style dictionaries.
    """

    result: List[Dict[str, Any]] = []


    if isinstance(
        raw,
        dict,
    ):

        # Matrix format:
        #
        # {
        #   "CO1": {
        #       "PO1": 3,
        #       "PO2": 2
        #   }
        # }

        for co_code, po_values in raw.items():

            if not isinstance(
                po_values,
                dict,
            ):
                continue


            for po_code, correlation in po_values.items():

                result.append(
                    {
                        "co_code": clean_text(
                            co_code
                        ),

                        "po_code": clean_text(
                            po_code
                        ),

                        "correlation": max(
                            0,
                            min(
                                3,
                                safe_int(
                                    correlation
                                ),
                            ),
                        ),

                        "justification": None,
                    }
                )


        return result


    for item in ensure_list(raw):

        data = normalize_dict_keys(
            ensure_dict(item)
        )


        co_code = clean_text(
            get_first(
                data,
                [
                    "co_code",
                    "co",
                    "course_outcome",
                ],
                "",
            )
        )


        po_code = clean_text(
            get_first(
                data,
                [
                    "po_code",
                    "po",
                    "program_outcome",
                ],
                "",
            )
        )


        if not co_code or not po_code:
            continue


        correlation = safe_int(
            get_first(
                data,
                [
                    "correlation",
                    "mapping",
                    "strength",
                    "level",
                ],
                0,
            )
        )


        result.append(
            {
                "co_code": co_code.upper(),

                "po_code": po_code.upper(),

                "correlation": max(
                    0,
                    min(
                        3,
                        correlation,
                    ),
                ),

                "justification": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "justification",
                                "reason",
                            ],
                            "",
                        )
                    )
                    or None
                ),
            }
        )


    return result


# ============================================================
# 58. NORMALIZE CO-PSO MAPPINGS
# ============================================================

def normalize_co_pso_mappings(
    raw: Any,
) -> List[Dict[str, Any]]:
    """
    Normalize CO-PSO mappings.
    """

    result: List[Dict[str, Any]] = []


    if isinstance(
        raw,
        dict,
    ):

        for co_code, pso_values in raw.items():

            if not isinstance(
                pso_values,
                dict,
            ):
                continue


            for pso_code, correlation in pso_values.items():

                result.append(
                    {
                        "co_code": clean_text(
                            co_code
                        ).upper(),

                        "pso_code": clean_text(
                            pso_code
                        ).upper(),

                        "correlation": max(
                            0,
                            min(
                                3,
                                safe_int(
                                    correlation
                                ),
                            ),
                        ),

                        "justification": None,
                    }
                )


        return result


    for item in ensure_list(raw):

        data = normalize_dict_keys(
            ensure_dict(item)
        )


        co_code = clean_text(
            get_first(
                data,
                [
                    "co_code",
                    "co",
                    "course_outcome",
                ],
                "",
            )
        )


        pso_code = clean_text(
            get_first(
                data,
                [
                    "pso_code",
                    "pso",
                    "program_specific_outcome",
                ],
                "",
            )
        )


        if not co_code or not pso_code:
            continue


        correlation = safe_int(
            get_first(
                data,
                [
                    "correlation",
                    "mapping",
                    "strength",
                    "level",
                ],
                0,
            )
        )


        result.append(
            {
                "co_code": co_code.upper(),

                "pso_code": pso_code.upper(),

                "correlation": max(
                    0,
                    min(
                        3,
                        correlation,
                    ),
                ),

                "justification": (
                    clean_text(
                        get_first(
                            data,
                            [
                                "justification",
                                "reason",
                            ],
                            "",
                        )
                    )
                    or None
                ),
            }
        )


    return result


# ============================================================
# END OF CHUNK 4
# ============================================================
# ============================================================
# curriculum/extractor.py
# CHUNK 5/8
#
# PYDANTIC OBJECT BUILDERS
#
# RAW NORMALIZED JSON
#        ↓
# Pydantic Curriculum Models
#        ↓
# Curriculum
# Module
# Topic
# Concept
# Skill
# Tool
# Technology
# Project
# CO / PO / PSO
# ============================================================


# ============================================================
# 59. GENERIC MODEL CREATION HELPER
# ============================================================

def create_model_safe(
    model_class: Any,
    data: Dict[str, Any],
    model_name: str = "model",
) -> Any:
    """
    Safely create a Pydantic model.

    If validation fails, the error is logged and re-raised
    with a cleaner message.
    """

    try:

        return model_class.model_validate(
            data
        )

    except ValidationError as exc:

        log_error(
            (
                f"Validation failed for "
                f"{model_name}: {exc}"
            )
        )

        raise ValueError(
            (
                f"Unable to construct {model_name}. "
                f"Validation error: {exc}"
            )
        ) from exc


# ============================================================
# 60. BUILD COURSE METADATA
# ============================================================

def build_course_metadata(
    raw: Any,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> CourseMetadata:
    """
    Build CourseMetadata from normalized metadata.
    """

    data = normalize_metadata(
        raw,
        source_file=source_file,
        source_type=source_type,
    )


    return create_model_safe(
        CourseMetadata,
        data,
        "CourseMetadata",
    )


# ============================================================
# 61. BUILD COURSE OBJECTIVE
# ============================================================

def build_course_objective(
    data: Dict[str, Any],
    index: int = 1,
) -> CourseObjective:
    """
    Build a CourseObjective object.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )


    description = clean_text(
        get_first(
            normalized,
            [
                "description",
                "objective",
                "text",
            ],
            "",
        )
    )


    if not description:

        description = (
            f"Course objective {index}"
        )


    payload = {

        "code":
            clean_text(
                get_first(
                    normalized,
                    [
                        "code",
                        "id",
                    ],
                    f"OBJ{index}",
                )
            ),

        "description":
            description,

        "bloom_level":
            normalize_bloom_level(
                get_first(
                    normalized,
                    [
                        "bloom_level",
                        "bloom",
                    ],
                    "Understand",
                )
            ),

    }


    return create_model_safe(
        CourseObjective,
        payload,
        f"CourseObjective[{index}]",
    )


# ============================================================
# 62. BUILD COURSE OBJECTIVES
# ============================================================

def build_course_objectives(
    raw: Any,
) -> List[CourseObjective]:
    """
    Build all course objectives.
    """

    normalized = normalize_objectives(
        raw
    )


    return [

        build_course_objective(
            item,
            index=index,
        )

        for index, item in enumerate(
            normalized,
            start=1,
        )

    ]


# ============================================================
# 63. BUILD CONCEPT
# ============================================================

def build_concept(
    data: Dict[str, Any],
    index: int = 1,
) -> Concept:
    """
    Build Concept model.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )


    name = clean_text(
        get_first(
            normalized,
            [
                "name",
                "concept_name",
                "concept",
            ],
            f"Concept {index}",
        )
    )


    payload = {

        "name":
            name,

        "description":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "description",
                            "summary",
                        ],
                        "",
                    )
                )
                or None
            ),

        "concept_type":
            normalize_concept_type(
                get_first(
                    normalized,
                    [
                        "concept_type",
                        "type",
                        "category",
                    ],
                    "Core",
                )
            ),

        "importance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "importance_score",
                        "importance",
                    ],
                    50,
                )
            ),

        "industry_relevance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "industry_relevance_score",
                        "industry_relevance",
                    ],
                    0,
                )
            ),

        "difficulty":
            normalize_difficulty(
                get_first(
                    normalized,
                    [
                        "difficulty",
                        "level",
                    ],
                    "Intermediate",
                )
            ),

        "prerequisites":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "prerequisites",
                    ],
                    [],
                )
            ),

        "related_concepts":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "related_concepts",
                        "related",
                    ],
                    [],
                )
            ),

        "emerging":
            bool(
                get_first(
                    normalized,
                    [
                        "emerging",
                        "is_emerging",
                    ],
                    False,
                )
            ),

        "industry_used":
            bool(
                get_first(
                    normalized,
                    [
                        "industry_used",
                        "used_in_industry",
                    ],
                    False,
                )
            ),

        "source_references":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "source_references",
                        "references",
                    ],
                    [],
                )
            ),

    }


    return create_model_safe(
        Concept,
        payload,
        f"Concept[{index}]",
    )


# ============================================================
# 64. BUILD SKILL
# ============================================================

def build_skill(
    data: Dict[str, Any],
    index: int = 1,
) -> Skill:
    """
    Build Skill model.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )


    name = clean_text(
        get_first(
            normalized,
            [
                "name",
                "skill_name",
                "skill",
            ],
            f"Skill {index}",
        )
    )


    payload = {

        "name":
            name,

        "normalized_name":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "normalized_name",
                        ],
                        normalize_skill_name(
                            name
                        ),
                    )
                )
                or normalize_skill_name(
                    name
                )
            ),

        "category":
            normalize_skill_category(
                get_first(
                    normalized,
                    [
                        "category",
                        "skill_category",
                    ],
                    "Other",
                )
            ),

        "description":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "description",
                            "summary",
                        ],
                        "",
                    )
                )
                or None
            ),

        "proficiency_level":
            normalize_difficulty(
                get_first(
                    normalized,
                    [
                        "proficiency_level",
                        "level",
                    ],
                    "Intermediate",
                )
            ),

        "importance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "importance_score",
                        "importance",
                    ],
                    50,
                )
            ),

        "industry_relevance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "industry_relevance_score",
                        "industry_relevance",
                    ],
                    0,
                )
            ),

        "years_relevance":
            (
                safe_float(
                    get_first(
                        normalized,
                        [
                            "years_relevance",
                            "years",
                        ],
                    )
                )
                if get_first(
                    normalized,
                    [
                        "years_relevance",
                        "years",
                    ],
                ) is not None
                else None
            ),

        "aliases":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "aliases",
                        "alternative_names",
                    ],
                    [],
                )
            ),

        "source_topics":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "source_topics",
                        "topics",
                    ],
                    [],
                )
            ),

    }


    return create_model_safe(
        Skill,
        payload,
        f"Skill[{index}]",
    )


# ============================================================
# 65. BUILD TOOL
# ============================================================

def build_tool(
    data: Dict[str, Any],
    index: int = 1,
) -> Tool:
    """
    Build Tool model.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )


    payload = {

        "name":
            clean_text(
                get_first(
                    normalized,
                    [
                        "name",
                        "tool_name",
                        "tool",
                    ],
                    f"Tool {index}",
                )
            ),

        "category":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "category",
                            "type",
                        ],
                        "",
                    )
                )
                or None
            ),

        "purpose":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "purpose",
                            "use",
                            "description",
                        ],
                        "",
                    )
                )
                or None
            ),

        "version":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "version",
                        ],
                        "",
                    )
                )
                or None
            ),

        "industry_relevance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "industry_relevance_score",
                        "industry_relevance",
                    ],
                    0,
                )
            ),

        "recommended":
            bool(
                get_first(
                    normalized,
                    [
                        "recommended",
                    ],
                    False,
                )
            ),

    }


    return create_model_safe(
        Tool,
        payload,
        f"Tool[{index}]",
    )


# ============================================================
# 66. BUILD TECHNOLOGY
# ============================================================

def build_technology(
    data: Dict[str, Any],
    index: int = 1,
) -> Technology:
    """
    Build Technology model.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )


    payload = {

        "name":
            clean_text(
                get_first(
                    normalized,
                    [
                        "name",
                        "technology_name",
                        "technology",
                        "framework",
                        "platform",
                    ],
                    f"Technology {index}",
                )
            ),

        "category":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "category",
                            "type",
                        ],
                        "",
                    )
                )
                or None
            ),

        "description":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "description",
                            "summary",
                        ],
                        "",
                    )
                )
                or None
            ),

        "current_version":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "current_version",
                            "version",
                        ],
                        "",
                    )
                )
                or None
            ),

        "industry_relevance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "industry_relevance_score",
                        "industry_relevance",
                    ],
                    0,
                )
            ),

        "emerging":
            bool(
                get_first(
                    normalized,
                    [
                        "emerging",
                        "is_emerging",
                    ],
                    False,
                )
            ),

        "recommended":
            bool(
                get_first(
                    normalized,
                    [
                        "recommended",
                    ],
                    False,
                )
            ),

    }


    return create_model_safe(
        Technology,
        payload,
        f"Technology[{index}]",
    )


# ============================================================
# 67. BUILD PROJECT
# ============================================================

def build_project(
    data: Dict[str, Any],
    index: int = 1,
) -> Project:
    """
    Build Project model.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )


    payload = {

        "title":
            clean_text(
                get_first(
                    normalized,
                    [
                        "title",
                        "project_title",
                        "project_name",
                        "name",
                    ],
                    f"Project {index}",
                )
            ),

        "description":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "description",
                            "summary",
                        ],
                        "",
                    )
                )
                or None
            ),

        "project_type":
            clean_text(
                get_first(
                    normalized,
                    [
                        "project_type",
                        "type",
                    ],
                    "Project",
                )
            ),

        "difficulty":
            normalize_difficulty(
                get_first(
                    normalized,
                    [
                        "difficulty",
                        "level",
                    ],
                    "Intermediate",
                )
            ),

        "duration_hours":
            (
                safe_float(
                    get_first(
                        normalized,
                        [
                            "duration_hours",
                            "hours",
                        ],
                    )
                )
                if get_first(
                    normalized,
                    [
                        "duration_hours",
                        "hours",
                    ],
                ) is not None
                else None
            ),

        "skills":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "skills",
                    ],
                    [],
                )
            ),

        "concepts":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "concepts",
                    ],
                    [],
                )
            ),

        "tools":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "tools",
                    ],
                    [],
                )
            ),

        "technologies":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "technologies",
                        "technology",
                    ],
                    [],
                )
            ),

        "industry_relevance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "industry_relevance_score",
                        "industry_relevance",
                    ],
                    0,
                )
            ),

        "portfolio_ready":
            bool(
                get_first(
                    normalized,
                    [
                        "portfolio_ready",
                    ],
                    False,
                )
            ),

        "real_world_problem":
            bool(
                get_first(
                    normalized,
                    [
                        "real_world_problem",
                        "real_world",
                    ],
                    False,
                )
            ),

    }


    return create_model_safe(
        Project,
        payload,
        f"Project[{index}]",
    )


# ============================================================
# 68. BUILD TOPIC
# ============================================================

def build_topic(
    data: Dict[str, Any],
    index: int = 1,
) -> Topic:
    """
    Build Topic model.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )


    topic_name = clean_text(
        get_first(
            normalized,
            [
                "topic_name",
                "topic",
                "subtopic_name",
                "subtopic",
                "title",
                "name",
            ],
            f"Topic {index}",
        )
    )


    payload = {

        "topic_id":
            clean_text(
                get_first(
                    normalized,
                    [
                        "topic_id",
                        "subtopic_id",
                        "id",
                    ],
                    f"T{index}",
                )
            ),

        "topic_name":
            topic_name,

        "description":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "description",
                            "summary",
                        ],
                        "",
                    )
                )
                or None
            ),

        "hours":
            safe_float(
                get_first(
                    normalized,
                    [
                        "hours",
                        "teaching_hours",
                    ],
                    0,
                )
            ),

        "sequence":
            safe_int(
                get_first(
                    normalized,
                    [
                        "sequence",
                        "order",
                        "number",
                    ],
                    index,
                ),
                index,
            ),

        "learning_type":
            normalize_learning_type(
                get_first(
                    normalized,
                    [
                        "learning_type",
                        "type",
                    ],
                    "Theory",
                )
            ),

        "difficulty":
            normalize_difficulty(
                get_first(
                    normalized,
                    [
                        "difficulty",
                        "level",
                    ],
                    "Intermediate",
                )
            ),

        "bloom_level":
            normalize_bloom_level(
                get_first(
                    normalized,
                    [
                        "bloom_level",
                        "bloom",
                    ],
                    "Understand",
                )
            ),

        "concepts":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "concepts",
                    ],
                    [],
                )
            ),

        "skills":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "skills",
                    ],
                    [],
                )
            ),

        "tools":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "tools",
                    ],
                    [],
                )
            ),

        "technologies":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "technologies",
                        "technology",
                    ],
                    [],
                )
            ),

        "prerequisites":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "prerequisites",
                    ],
                    [],
                )
            ),

        "learning_objectives":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "learning_objectives",
                        "objectives",
                    ],
                    [],
                )
            ),

        "projects":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "projects",
                        "project",
                    ],
                    [],
                )
            ),

        "case_studies":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "case_studies",
                        "case_study",
                    ],
                    [],
                )
            ),

        "references":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "references",
                        "reference",
                        "resources",
                    ],
                    [],
                )
            ),

        "industry_relevance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "industry_relevance_score",
                        "industry_relevance",
                    ],
                    0,
                )
            ),

        "importance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "importance_score",
                        "importance",
                    ],
                    50,
                )
            ),

        "current":
            bool(
                get_first(
                    normalized,
                    [
                        "current",
                        "is_current",
                    ],
                    True,
                )
            ),

        "recommended_enhancement":
            bool(
                get_first(
                    normalized,
                    [
                        "recommended_enhancement",
                        "enhancement_recommended",
                    ],
                    False,
                )
            ),

    }


    return create_model_safe(
        Topic,
        payload,
        f"Topic[{index}]",
    )


# ============================================================
# 69. BUILD MODULE
# ============================================================

def build_module(
    data: Dict[str, Any],
    index: int = 1,
) -> Module:
    """
    Build Module model including all child Topics and Projects.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )


    raw_topics = get_first(
        normalized,
        [
            "topics",
            "topic",
            "subtopics",
            "contents",
        ],
        [],
    )


    raw_projects = get_first(
        normalized,
        [
            "projects",
            "project",
        ],
        [],
    )


    topic_data = normalize_topics(
        raw_topics
    )


    project_data = normalize_projects(
        raw_projects
    )


    topics = [

        build_topic(
            topic,
            index=topic_index,
        )

        for topic_index, topic in enumerate(
            topic_data,
            start=1,
        )

    ]


    projects = [

        build_project(
            project,
            index=project_index,
        )

        for project_index, project in enumerate(
            project_data,
            start=1,
        )

    ]


    module_name = clean_text(
        get_first(
            normalized,
            [
                "module_name",
                "module",
                "unit_name",
                "unit",
                "chapter_name",
                "chapter",
                "title",
                "name",
            ],
            f"Module {index}",
        )
    )


    payload = {

        "module_id":
            clean_text(
                get_first(
                    normalized,
                    [
                        "module_id",
                        "unit_id",
                        "chapter_id",
                        "id",
                    ],
                    f"M{index}",
                )
            ),

        "module_name":
            module_name,

        "description":
            (
                clean_text(
                    get_first(
                        normalized,
                        [
                            "description",
                            "summary",
                        ],
                        "",
                    )
                )
                or None
            ),

        "sequence":
            safe_int(
                get_first(
                    normalized,
                    [
                        "sequence",
                        "order",
                        "number",
                    ],
                    index,
                ),
                index,
            ),

        "hours":
            safe_float(
                get_first(
                    normalized,
                    [
                        "hours",
                        "teaching_hours",
                        "contact_hours",
                    ],
                    0,
                )
            ),

        "credits":
            (
                safe_float(
                    get_first(
                        normalized,
                        [
                            "credits",
                            "credit",
                        ],
                    )
                )
                if get_first(
                    normalized,
                    [
                        "credits",
                        "credit",
                    ],
                ) is not None
                else None
            ),

        "topics":
            topics,

        "concepts":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "concepts",
                    ],
                    [],
                )
            ),

        "skills":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "skills",
                    ],
                    [],
                )
            ),

        "tools":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "tools",
                    ],
                    [],
                )
            ),

        "technologies":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "technologies",
                        "technology",
                    ],
                    [],
                )
            ),

        "projects":
            projects,

        "case_studies":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "case_studies",
                        "case_study",
                    ],
                    [],
                )
            ),

        "learning_objectives":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "learning_objectives",
                        "objectives",
                    ],
                    [],
                )
            ),

        "prerequisites":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "prerequisites",
                    ],
                    [],
                )
            ),

        "bloom_levels":
            normalize_bloom_levels(
                get_first(
                    normalized,
                    [
                        "bloom_levels",
                        "bloom",
                    ],
                    [],
                )
            ),

        "difficulty":
            normalize_difficulty(
                get_first(
                    normalized,
                    [
                        "difficulty",
                        "level",
                    ],
                    "Intermediate",
                )
            ),

        "industry_relevance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "industry_relevance_score",
                        "industry_relevance",
                    ],
                    0,
                )
            ),

        "academic_relevance_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "academic_relevance_score",
                        "academic_relevance",
                    ],
                    50,
                )
            ),

        "currency_score":
            clamp_score(
                get_first(
                    normalized,
                    [
                        "currency_score",
                        "current_score",
                    ],
                    50,
                )
            ),

        "recommended":
            bool(
                get_first(
                    normalized,
                    [
                        "recommended",
                    ],
                    False,
                )
            ),

        "enhancement_notes":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "enhancement_notes",
                        "recommendations",
                    ],
                    [],
                )
            ),

        "co_mapping":
            clean_string_list(
                get_first(
                    normalized,
                    [
                        "co_mapping",
                        "co_mappings",
                    ],
                    [],
                )
            ),

    }


    return create_model_safe(
        Module,
        payload,
        f"Module[{index}]",
    )


# ============================================================
# 70. BUILD MODULE LIST
# ============================================================

def build_modules(
    raw: Any,
) -> List[Module]:
    """
    Build all Module objects.
    """

    normalized_modules = normalize_modules(
        raw
    )


    modules: List[Module] = []


    for index, module_data in enumerate(
        normalized_modules,
        start=1,
    ):

        modules.append(
            build_module(
                module_data,
                index=index,
            )
        )


    return modules


# ============================================================
# END OF CHUNK 5
# ============================================================
# ============================================================
# curriculum/extractor.py
# CHUNK 6/8
#
# COMPLETE CURRICULUM ASSEMBLY
#
# NORMALIZED DATA
#       ↓
# MODULES
#       ↓
# GLOBAL AGGREGATION
#       ↓
# CURRICULUM
#       ↓
# STATISTICS + METADATA
# ============================================================


# ============================================================
# 71. BUILD COURSE OUTCOME
# ============================================================

def build_course_outcome(
    data: Dict[str, Any],
    index: int = 1,
) -> CourseOutcome:
    """
    Build CourseOutcome model.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )

    code = clean_text(
        get_first(
            normalized,
            [
                "code",
                "co_code",
                "id",
                "outcome_code",
            ],
            f"CO{index}",
        )
    )

    description = clean_text(
        get_first(
            normalized,
            [
                "description",
                "outcome",
                "statement",
                "text",
            ],
            "",
        )
    )

    if not description:
        description = (
            f"Course outcome {index}"
        )

    payload = {
        "code": code.upper(),

        "description": description,

        "bloom_level": normalize_bloom_level(
            get_first(
                normalized,
                [
                    "bloom_level",
                    "bloom",
                ],
                "Understand",
            )
        ),

        "knowledge_area": (
            clean_text(
                get_first(
                    normalized,
                    [
                        "knowledge_area",
                        "area",
                    ],
                    "",
                )
            )
            or None
        ),

        "mapped_modules": clean_string_list(
            get_first(
                normalized,
                [
                    "mapped_modules",
                    "modules",
                ],
                [],
            )
        ),

        "mapped_topics": clean_string_list(
            get_first(
                normalized,
                [
                    "mapped_topics",
                    "topics",
                ],
                [],
            )
        ),

        "assessment_methods": clean_string_list(
            get_first(
                normalized,
                [
                    "assessment_methods",
                    "assessment",
                    "methods",
                ],
                [],
            )
        ),
    }

    return create_model_safe(
        CourseOutcome,
        payload,
        f"CourseOutcome[{index}]",
    )


# ============================================================
# 72. BUILD COURSE OUTCOMES
# ============================================================

def build_course_outcomes(
    raw: Any,
) -> List[CourseOutcome]:
    """
    Build Course Outcome objects.
    """

    normalized = normalize_course_outcomes(
        raw
    )

    return [
        build_course_outcome(
            item,
            index=index,
        )
        for index, item in enumerate(
            normalized,
            start=1,
        )
    ]


# ============================================================
# 73. BUILD PROGRAM OUTCOME
# ============================================================

def build_program_outcome(
    data: Dict[str, Any],
    index: int = 1,
) -> ProgramOutcome:
    """
    Build ProgramOutcome model.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )

    code = clean_text(
        get_first(
            normalized,
            [
                "code",
                "po_code",
                "id",
            ],
            f"PO{index}",
        )
    )

    description = clean_text(
        get_first(
            normalized,
            [
                "description",
                "outcome",
                "statement",
                "text",
            ],
            "",
        )
    )

    if not description:
        description = (
            f"Program outcome {index}"
        )

    payload = {
        "code": code.upper(),

        "description": description,

        "category": (
            clean_text(
                get_first(
                    normalized,
                    [
                        "category",
                        "type",
                    ],
                    "",
                )
            )
            or None
        ),
    }

    return create_model_safe(
        ProgramOutcome,
        payload,
        f"ProgramOutcome[{index}]",
    )


# ============================================================
# 74. BUILD PROGRAM OUTCOMES
# ============================================================

def build_program_outcomes(
    raw: Any,
) -> List[ProgramOutcome]:
    """
    Build PO objects.
    """

    normalized = normalize_program_outcomes(
        raw
    )

    return [
        build_program_outcome(
            item,
            index=index,
        )
        for index, item in enumerate(
            normalized,
            start=1,
        )
    ]


# ============================================================
# 75. BUILD PROGRAM SPECIFIC OUTCOME
# ============================================================

def build_program_specific_outcome(
    data: Dict[str, Any],
    index: int = 1,
) -> ProgramSpecificOutcome:
    """
    Build PSO model.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )

    code = clean_text(
        get_first(
            normalized,
            [
                "code",
                "pso_code",
                "id",
            ],
            f"PSO{index}",
        )
    )

    description = clean_text(
        get_first(
            normalized,
            [
                "description",
                "outcome",
                "statement",
                "text",
            ],
            "",
        )
    )

    if not description:
        description = (
            f"Program specific outcome {index}"
        )

    payload = {
        "code": code.upper(),

        "description": description,

        "category": (
            clean_text(
                get_first(
                    normalized,
                    [
                        "category",
                        "type",
                    ],
                    "",
                )
            )
            or None
        ),
    }

    return create_model_safe(
        ProgramSpecificOutcome,
        payload,
        f"ProgramSpecificOutcome[{index}]",
    )


# ============================================================
# 76. BUILD PSO LIST
# ============================================================

def build_program_specific_outcomes(
    raw: Any,
) -> List[ProgramSpecificOutcome]:
    """
    Build PSO objects.
    """

    normalized = normalize_program_specific_outcomes(
        raw
    )

    return [
        build_program_specific_outcome(
            item,
            index=index,
        )
        for index, item in enumerate(
            normalized,
            start=1,
        )
    ]


# ============================================================
# 77. BUILD CO-PO MAPPING
# ============================================================

def build_co_po_mapping(
    data: Dict[str, Any],
    index: int = 1,
) -> COPOMapping:
    """
    Build a CO-PO mapping.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )

    payload = {
        "co_code": clean_text(
            get_first(
                normalized,
                [
                    "co_code",
                    "co",
                    "course_outcome",
                ],
                "",
            )
        ).upper(),

        "po_code": clean_text(
            get_first(
                normalized,
                [
                    "po_code",
                    "po",
                    "program_outcome",
                ],
                "",
            )
        ).upper(),

        "correlation": max(
            0,
            min(
                3,
                safe_int(
                    get_first(
                        normalized,
                        [
                            "correlation",
                            "mapping",
                            "strength",
                            "level",
                        ],
                        0,
                    )
                ),
            ),
        ),

        "justification": (
            clean_text(
                get_first(
                    normalized,
                    [
                        "justification",
                        "reason",
                    ],
                    "",
                )
            )
            or None
        ),
    }

    if not payload["co_code"]:
        raise ValueError(
            f"CO-PO mapping {index} has no CO code."
        )

    if not payload["po_code"]:
        raise ValueError(
            f"CO-PO mapping {index} has no PO code."
        )

    return create_model_safe(
        COPOMapping,
        payload,
        f"COPOMapping[{index}]",
    )


# ============================================================
# 78. BUILD CO-PO MAPPINGS
# ============================================================

def build_co_po_mappings(
    raw: Any,
) -> List[COPOMapping]:
    """
    Build all CO-PO mappings.
    """

    normalized = normalize_co_po_mappings(
        raw
    )

    result = []

    seen = set()

    for index, item in enumerate(
        normalized,
        start=1,
    ):

        key = (
            item.get("co_code", "").upper(),
            item.get("po_code", "").upper(),
        )

        if key in seen:
            continue

        seen.add(key)

        result.append(
            build_co_po_mapping(
                item,
                index=index,
            )
        )

    return result


# ============================================================
# 79. BUILD CO-PSO MAPPING
# ============================================================

def build_co_pso_mapping(
    data: Dict[str, Any],
    index: int = 1,
) -> COPSOmapping:
    """
    Build a CO-PSO mapping.
    """

    normalized = normalize_dict_keys(
        ensure_dict(data)
    )

    payload = {
        "co_code": clean_text(
            get_first(
                normalized,
                [
                    "co_code",
                    "co",
                    "course_outcome",
                ],
                "",
            )
        ).upper(),

        "pso_code": clean_text(
            get_first(
                normalized,
                [
                    "pso_code",
                    "pso",
                    "program_specific_outcome",
                ],
                "",
            )
        ).upper(),

        "correlation": max(
            0,
            min(
                3,
                safe_int(
                    get_first(
                        normalized,
                        [
                            "correlation",
                            "mapping",
                            "strength",
                            "level",
                        ],
                        0,
                    )
                ),
            ),
        ),

        "justification": (
            clean_text(
                get_first(
                    normalized,
                    [
                        "justification",
                        "reason",
                    ],
                    "",
                )
            )
            or None
        ),
    }

    if not payload["co_code"]:
        raise ValueError(
            f"CO-PSO mapping {index} has no CO code."
        )

    if not payload["pso_code"]:
        raise ValueError(
            f"CO-PSO mapping {index} has no PSO code."
        )

    return create_model_safe(
        COPSOmapping,
        payload,
        f"COPSOmapping[{index}]",
    )


# ============================================================
# 80. BUILD CO-PSO MAPPINGS
# ============================================================

def build_co_pso_mappings(
    raw: Any,
) -> List[COPSOmapping]:
    """
    Build all CO-PSO mappings.
    """

    normalized = normalize_co_pso_mappings(
        raw
    )

    result = []

    seen = set()

    for index, item in enumerate(
        normalized,
        start=1,
    ):

        key = (
            item.get("co_code", "").upper(),
            item.get("pso_code", "").upper(),
        )

        if key in seen:
            continue

        seen.add(key)

        result.append(
            build_co_pso_mapping(
                item,
                index=index,
            )
        )

    return result


# ============================================================
# 81. UNIQUE STRING LIST
# ============================================================

def unique_strings(
    values: Any,
) -> List[str]:
    """
    Deduplicate strings while preserving order.
    """

    result = []

    seen = set()

    for value in ensure_list(
        values
    ):

        text = clean_text(
            value
        )

        if not text:
            continue

        key = text.lower()

        if key in seen:
            continue

        seen.add(key)

        result.append(
            text
        )

    return result


# ============================================================
# 82. AGGREGATE MODULE CONCEPTS
# ============================================================

def aggregate_module_concepts(
    modules: List[Module],
) -> List[Concept]:
    """
    Collect concepts from:

        Module.concepts
        Topic.concepts

    and return unique Concept objects.
    """

    names: List[str] = []

    for module in modules:

        names.extend(
            module.concepts
        )

        for topic in module.topics:

            names.extend(
                topic.concepts
            )

    names = unique_strings(
        names
    )

    result = []

    for index, name in enumerate(
        names,
        start=1,
    ):

        result.append(
            build_concept(
                {
                    "name": name,
                    "concept_type": "Core",
                    "importance_score": 50,
                },
                index=index,
            )
        )

    return result


# ============================================================
# 83. MERGE CONCEPT OBJECTS
# ============================================================

def merge_concepts(
    primary: List[Concept],
    secondary: List[Concept],
) -> List[Concept]:
    """
    Merge concept objects and remove duplicates.

    Primary information is retained.
    """

    result: List[Concept] = []

    index_by_name: Dict[
        str,
        int
    ] = {}


    for concept in primary:

        key = concept.name.lower()

        if key in index_by_name:
            continue

        index_by_name[key] = len(
            result
        )

        result.append(
            concept
        )


    for concept in secondary:

        key = concept.name.lower()

        if key in index_by_name:

            existing = result[
                index_by_name[key]
            ]

            # Keep the strongest score.

            if (
                concept.importance_score
                >
                existing.importance_score
            ):

                result[
                    index_by_name[key]
                ] = concept

            continue


        index_by_name[key] = len(
            result
        )

        result.append(
            concept
        )


    return result


# ============================================================
# 84. AGGREGATE MODULE SKILLS
# ============================================================

def aggregate_module_skills(
    modules: List[Module],
) -> List[Skill]:
    """
    Collect skill names from modules and topics.
    """

    names: List[str] = []

    for module in modules:

        names.extend(
            module.skills
        )

        for topic in module.topics:

            names.extend(
                topic.skills
            )

            for project_name in topic.projects:

                # Project names are not automatically
                # treated as skills.

                _ = project_name


    names = unique_strings(
        names
    )

    result = []

    for index, name in enumerate(
        names,
        start=1,
    ):

        result.append(
            build_skill(
                {
                    "name": name,
                    "normalized_name":
                        normalize_skill_name(
                            name
                        ),
                    "category":
                        normalize_skill_category(
                            name
                        ),
                    "importance_score":
                        50,
                },
                index=index,
            )
        )

    return result


# ============================================================
# 85. MERGE SKILLS
# ============================================================

def merge_skills(
    primary: List[Skill],
    secondary: List[Skill],
) -> List[Skill]:
    """
    Merge skills by normalized name.
    """

    result: List[Skill] = []

    index_by_name: Dict[
        str,
        int
    ] = {}


    for skill in primary:

        key = (
            skill.normalized_name
            or skill.name
        ).lower()

        if key in index_by_name:
            continue

        index_by_name[key] = len(
            result
        )

        result.append(
            skill
        )


    for skill in secondary:

        key = (
            skill.normalized_name
            or skill.name
        ).lower()

        if key in index_by_name:

            existing = result[
                index_by_name[key]
            ]

            if (
                skill.industry_relevance_score
                >
                existing.industry_relevance_score
            ):

                result[
                    index_by_name[key]
                ] = skill

            continue


        index_by_name[key] = len(
            result
        )

        result.append(
            skill
        )


    return result


# ============================================================
# 86. AGGREGATE TOOLS
# ============================================================

def aggregate_module_tools(
    modules: List[Module],
) -> List[Tool]:
    """
    Collect tools from modules and topics.
    """

    names: List[str] = []

    for module in modules:

        names.extend(
            module.tools
        )

        for topic in module.topics:

            names.extend(
                topic.tools
            )


    names = unique_strings(
        names
    )

    return [

        build_tool(
            {
                "name": name,
            },
            index=index,
        )

        for index, name in enumerate(
            names,
            start=1,
        )

    ]


# ============================================================
# 87. MERGE TOOLS
# ============================================================

def merge_tools(
    primary: List[Tool],
    secondary: List[Tool],
) -> List[Tool]:
    """
    Merge tools by name.
    """

    result: List[Tool] = []

    seen = set()


    for tool in [
        *primary,
        *secondary,
    ]:

        key = tool.name.lower()

        if key in seen:
            continue

        seen.add(key)

        result.append(
            tool
        )


    return result


# ============================================================
# 88. AGGREGATE TECHNOLOGIES
# ============================================================

def aggregate_module_technologies(
    modules: List[Module],
) -> List[Technology]:
    """
    Collect technologies from modules and topics.
    """

    names: List[str] = []

    for module in modules:

        names.extend(
            module.technologies
        )

        for topic in module.topics:

            names.extend(
                topic.technologies
            )


    names = unique_strings(
        names
    )

    return [

        build_technology(
            {
                "name": name,
            },
            index=index,
        )

        for index, name in enumerate(
            names,
            start=1,
        )

    ]


# ============================================================
# 89. MERGE TECHNOLOGIES
# ============================================================

def merge_technologies(
    primary: List[Technology],
    secondary: List[Technology],
) -> List[Technology]:
    """
    Merge technologies by name.
    """

    result: List[Technology] = []

    seen = set()


    for technology in [
        *primary,
        *secondary,
    ]:

        key = technology.name.lower()

        if key in seen:
            continue

        seen.add(key)

        result.append(
            technology
        )


    return result


# ============================================================
# 90. AGGREGATE PROJECTS
# ============================================================

def aggregate_module_projects(
    modules: List[Module],
) -> List[Project]:
    """
    Collect projects defined at module level.
    """

    result: List[Project] = []

    seen = set()


    for module in modules:

        for project in module.projects:

            key = project.title.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                project
            )


    return result


# ============================================================
# 91. CALCULATE TOTAL HOURS
# ============================================================

def calculate_total_hours(
    modules: List[Module],
) -> float:
    """
    Calculate total curriculum hours.

    If module hours are missing, topic hours are used.
    """

    module_hours = sum(
        module.hours
        for module in modules
    )


    if module_hours > 0:

        return round(
            module_hours,
            2,
        )


    topic_hours = 0.0

    for module in modules:

        topic_hours += sum(

            topic.hours

            for topic in module.topics

        )


    return round(
        topic_hours,
        2,
    )


# ============================================================
# 92. CALCULATE TOTAL CREDITS
# ============================================================

def calculate_total_credits(
    modules: List[Module],
    metadata: CourseMetadata,
) -> float:
    """
    Calculate total credits.
    """

    module_credits = sum(

        module.credits or 0

        for module in modules

    )


    if module_credits > 0:

        return round(
            module_credits,
            2,
        )


    return round(
        metadata.credits or 0,
        2,
    )


# ============================================================
# 93. BUILD COMPLETE CURRICULUM
# ============================================================

def build_curriculum(
    payload: Dict[str, Any],
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Curriculum:
    """
    Build the complete Curriculum object from
    normalized LLM output.

    This is the main internal assembly function.
    """

    payload = normalize_root_payload(
        payload
    )


    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata_raw = get_first(
        payload,
        [
            "metadata",
            "course_metadata",
            "course_information",
            "course_info",
        ],
        {},
    )


    metadata = build_course_metadata(
        metadata_raw,
        source_file=source_file,
        source_type=source_type,
    )


    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title = clean_text(
        get_first(
            payload,
            [
                "title",
                "course_title",
                "course_name",
                "subject_name",
            ],
            metadata.course_name
            or metadata.subject_name
            or "",
        )
    )


    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    description = (
        clean_text(
            get_first(
                payload,
                [
                    "description",
                    "course_description",
                    "summary",
                ],
                "",
            )
        )
        or None
    )


    # --------------------------------------------------------
    # Objectives
    # --------------------------------------------------------

    objectives = build_course_objectives(
        get_first(
            payload,
            [
                "objectives",
                "course_objectives",
                "learning_objectives",
            ],
            [],
        )
    )


    # --------------------------------------------------------
    # Modules
    # --------------------------------------------------------

    modules = build_modules(
        get_first(
            payload,
            [
                "modules",
                "units",
                "course_modules",
                "syllabus_modules",
                "chapters",
            ],
            [],
        )
    )


    # --------------------------------------------------------
    # Global concepts
    # --------------------------------------------------------

    explicit_concepts = [

        build_concept(
            item,
            index=index,
        )

        for index, item in enumerate(
            normalize_concepts(
                get_first(
                    payload,
                    [
                        "concepts",
                        "core_concepts",
                    ],
                    [],
                )
            ),
            start=1,
        )

    ]


    module_concepts = (
        aggregate_module_concepts(
            modules
        )
    )


    concepts = merge_concepts(
        explicit_concepts,
        module_concepts,
    )


    # --------------------------------------------------------
    # Global skills
    # --------------------------------------------------------

    explicit_skills = [

        build_skill(
            item,
            index=index,
        )

        for index, item in enumerate(
            normalize_skills(
                get_first(
                    payload,
                    [
                        "skills",
                        "core_skills",
                        "industry_skills",
                    ],
                    [],
                )
            ),
            start=1,
        )

    ]


    module_skills = (
        aggregate_module_skills(
            modules
        )
    )


    skills = merge_skills(
        explicit_skills,
        module_skills,
    )


    # --------------------------------------------------------
    # Global tools
    # --------------------------------------------------------

    explicit_tools = [

        build_tool(
            item,
            index=index,
        )

        for index, item in enumerate(
            normalize_tools(
                get_first(
                    payload,
                    [
                        "tools",
                        "software_tools",
                    ],
                    [],
                )
            ),
            start=1,
        )

    ]


    module_tools = (
        aggregate_module_tools(
            modules
        )
    )


    tools = merge_tools(
        explicit_tools,
        module_tools,
    )


    # --------------------------------------------------------
    # Global technologies
    # --------------------------------------------------------

    explicit_technologies = [

        build_technology(
            item,
            index=index,
        )

        for index, item in enumerate(
            normalize_technologies(
                get_first(
                    payload,
                    [
                        "technologies",
                        "technology",
                        "frameworks",
                        "platforms",
                    ],
                    [],
                )
            ),
            start=1,
        )

    ]


    module_technologies = (
        aggregate_module_technologies(
            modules
        )
    )


    technologies = merge_technologies(
        explicit_technologies,
        module_technologies,
    )


    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    explicit_projects = [

        build_project(
            item,
            index=index,
        )

        for index, item in enumerate(
            normalize_projects(
                get_first(
                    payload,
                    [
                        "projects",
                        "major_projects",
                        "course_projects",
                    ],
                    [],
                )
            ),
            start=1,
        )

    ]


    module_projects = (
        aggregate_module_projects(
            modules
        )
    )


    projects = []

    seen_projects = set()


    for project in [
        *explicit_projects,
        *module_projects,
    ]:

        key = project.title.lower()

        if key in seen_projects:
            continue

        seen_projects.add(key)

        projects.append(
            project
        )


    # --------------------------------------------------------
    # Outcomes
    # --------------------------------------------------------

    course_outcomes = build_course_outcomes(
        get_first(
            payload,
            [
                "course_outcomes",
                "course_outcome",
                "CO",
                "cos",
            ],
            [],
        )
    )


    program_outcomes = build_program_outcomes(
        get_first(
            payload,
            [
                "program_outcomes",
                "program_outcome",
                "PO",
                "pos",
            ],
            [],
        )
    )


    program_specific_outcomes = (
        build_program_specific_outcomes(
            get_first(
                payload,
                [
                    "program_specific_outcomes",
                    "program_specific_outcome",
                    "PSO",
                    "psos",
                ],
                [],
            )
        )
    )


    # --------------------------------------------------------
    # CO-PO mappings
    # --------------------------------------------------------

    co_po_mappings = build_co_po_mappings(
        get_first(
            payload,
            [
                "co_po_mappings",
                "co_po_mapping",
                "CO_PO",
                "co_po",
            ],
            [],
        )
    )


    # --------------------------------------------------------
    # CO-PSO mappings
    # --------------------------------------------------------

    co_pso_mappings = build_co_pso_mappings(
        get_first(
            payload,
            [
                "co_pso_mappings",
                "co_pso_mapping",
                "CO_PSO",
                "co_pso",
            ],
            [],
        )
    )


    # --------------------------------------------------------
    # Total hours
    # --------------------------------------------------------

    total_hours = safe_float(
        get_first(
            payload,
            [
                "total_hours",
                "hours",
            ],
            0,
        )
    )


    if total_hours <= 0:

        total_hours = calculate_total_hours(
            modules
        )


    # --------------------------------------------------------
    # Total credits
    # --------------------------------------------------------

    total_credits = safe_float(
        get_first(
            payload,
            [
                "total_credits",
                "credits",
            ],
            0,
        )
    )


    if total_credits <= 0:

        total_credits = calculate_total_credits(
            modules,
            metadata,
        )


    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    extraction_confidence = clamp_score(
        get_first(
            payload,
            [
                "extraction_confidence",
                "confidence",
            ],
            metadata.extraction_confidence or 0,
        )
    )


    # --------------------------------------------------------
    # Notes
    # --------------------------------------------------------

    notes = clean_string_list(
        get_first(
            payload,
            [
                "notes",
                "extraction_notes",
                "remarks",
            ],
            [],
        )
    )


    # --------------------------------------------------------
    # Construct Curriculum
    # --------------------------------------------------------

    curriculum_payload = {

        "metadata":
            metadata,

        "title":
            title or None,

        "description":
            description,

        "objectives":
            objectives,

        "prerequisites":
            unique_strings(
                [
                    *metadata.prerequisites,
                    *clean_string_list(
                        get_first(
                            payload,
                            [
                                "prerequisites",
                            ],
                            [],
                        )
                    ),
                ]
            ),

        "modules":
            modules,

        "concepts":
            concepts,

        "skills":
            skills,

        "tools":
            tools,

        "technologies":
            technologies,

        "projects":
            projects,

        "course_outcomes":
            course_outcomes,

        "program_outcomes":
            program_outcomes,

        "program_specific_outcomes":
            program_specific_outcomes,

        "co_po_mappings":
            co_po_mappings,

        "co_pso_mappings":
            co_pso_mappings,

        "total_hours":
            total_hours,

        "total_credits":
            total_credits,

        "extraction_confidence":
            extraction_confidence,

        "notes":
            notes,

    }


    curriculum = create_model_safe(
        Curriculum,
        curriculum_payload,
        "Curriculum",
    )


    log_info(
        (
            "Curriculum assembled successfully: "
            f"{len(curriculum.modules)} modules, "
            f"{len(curriculum.skills)} skills, "
            f"{len(curriculum.concepts)} concepts, "
            f"{len(curriculum.technologies)} technologies."
        )
    )


    return curriculum


# ============================================================
# 94. END OF CHUNK 6
# ============================================================
# ============================================================
# curriculum/extractor.py
# CHUNK 7/8
#
# MAIN EXTRACTION WORKFLOW
#
# TEXT
#   ↓
# GROQ / LLAMA
#   ↓
# JSON
#   ↓
# NORMALIZATION
#   ↓
# PYDANTIC CURRICULUM
#   ↓
# STATISTICS
#   ↓
# VALIDATION
#   ↓
# EXTRACTION RESULT
# ============================================================


# ============================================================
# 95. EXTRACTION RESULT
# ============================================================

class CurriculumExtractionResult:
    """
    Container returned by the extraction pipeline.

    Keeps the final Curriculum together with useful
    diagnostics from the extraction process.
    """

    def __init__(
        self,
        curriculum: Curriculum,
        raw_payload: Optional[
            Dict[str, Any]
        ] = None,
        raw_response: Optional[str] = None,
        statistics: Optional[
            CurriculumStatistics
        ] = None,
        validation: Optional[
            Any
        ] = None,
        source_file: Optional[str] = None,
        source_type: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
    ):

        self.curriculum = curriculum

        self.raw_payload = (
            raw_payload
            or {}
        )

        self.raw_response = (
            raw_response
            or ""
        )

        self.statistics = (
            statistics
            or calculate_curriculum_statistics(
                curriculum
            )
        )

        self.validation = validation

        self.source_file = (
            source_file
        )

        self.source_type = (
            source_type
        )

        self.success = success

        self.error = error


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert extraction result into a serializable
        dictionary.
        """

        return {

            "success":
                self.success,

            "error":
                self.error,

            "source_file":
                self.source_file,

            "source_type":
                self.source_type,

            "curriculum":
                model_to_dict(
                    self.curriculum
                ),

            "statistics":
                model_to_dict(
                    self.statistics
                ),

            "validation":
                (
                    model_to_dict(
                        self.validation
                    )
                    if self.validation
                    else None
                ),

        }


# ============================================================
# 96. EXTRACTION PIPELINE CONFIGURATION
# ============================================================

class ExtractionPipelineConfig:
    """
    High-level configuration for extraction.
    """

    def __init__(
        self,
        groq_config: Optional[
            ExtractorConfig
        ] = None,
        validate: bool = True,
        calculate_statistics: bool = True,
        retries: int = 2,
        allow_fallback: bool = True,
    ):

        self.groq_config = (
            groq_config
            or ExtractorConfig()
        )

        self.validate = validate

        self.calculate_statistics = (
            calculate_statistics
        )

        self.retries = max(
            0,
            retries,
        )

        self.allow_fallback = (
            allow_fallback
        )


# ============================================================
# 97. EXTRACT FROM RAW TEXT
# ============================================================

def extract_curriculum(
    syllabus_text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
    config: Optional[
        ExtractionPipelineConfig
    ] = None,
) -> CurriculumExtractionResult:
    """
    Main curriculum extraction API.

    Example:

        result = extract_curriculum(
            syllabus_text=text,
            source_file="AI_Syllabus.pdf",
            source_type="pdf",
        )

        curriculum = result.curriculum
    """

    pipeline_config = (
        config
        or ExtractionPipelineConfig()
    )


    detected_source_type = detect_source_type(

        filename=source_file,

        source_type=source_type,

    )


    try:

        # ----------------------------------------------------
        # Validate source text
        # ----------------------------------------------------

        prepared_text = prepare_input_text(
            syllabus_text
        )


        log_info(
            (
                "Starting curriculum extraction "
                f"from {detected_source_type}"
            )
        )


        # ----------------------------------------------------
        # LLM extraction
        #
        # IMPORTANT: The current Groq organization has an
        # 8,000 TPM limit. Large syllabi must therefore be
        # processed in small independent requests.
        # ----------------------------------------------------

        if len(prepared_text) > 7000:

            payload = extract_large_curriculum_payload(
                syllabus_text=prepared_text,
                source_file=source_file,
                source_type=detected_source_type,
                pipeline_config=pipeline_config,
            )

            raw_response = json.dumps(
                payload,
                ensure_ascii=False,
            )

        else:

            raw_response = generate_curriculum_response(
                syllabus_text=prepared_text,
                source_file=source_file,
                source_type=detected_source_type,
                config=pipeline_config,
            )

            # ------------------------------------------------
            # Parse JSON
            # ------------------------------------------------

            payload = extract_json_object(
                raw_response
            )

            if payload is None:
                raise ValueError(
                    "LLM response could not be parsed as JSON."
                )


        if payload is None:

            raise ValueError(
                "LLM response could not be parsed as JSON."
            )


        # ----------------------------------------------------
        # Build curriculum
        # ----------------------------------------------------

        curriculum = build_curriculum(

            payload=payload,

            source_file=source_file,

            source_type=detected_source_type,

        )


        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        statistics = None

        if pipeline_config.calculate_statistics:

            statistics = (
                calculate_curriculum_statistics(
                    curriculum
                )
            )


        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        validation = None

        if pipeline_config.validate:

            validation = (
                build_validation_report(
                    curriculum
                )
            )


        log_info(
            (
                "Curriculum extraction completed "
                "successfully."
            )
        )


        return CurriculumExtractionResult(

            curriculum=curriculum,

            raw_payload=payload,

            raw_response=raw_response,

            statistics=statistics,

            validation=validation,

            source_file=source_file,

            source_type=detected_source_type,

            success=True,

        )


    except Exception as exc:

        log_error(
            (
                "Curriculum extraction failed: "
                f"{exc}"
            )
        )


        # ----------------------------------------------------
        # Optional fallback
        # ----------------------------------------------------

        if pipeline_config.allow_fallback:

            try:

                fallback_curriculum = (
                    create_fallback_curriculum(
                        syllabus_text=prepared_text,
                        source_file=source_file,
                        source_type=detected_source_type,
                    )
                )


                statistics = (
                    calculate_curriculum_statistics(
                        fallback_curriculum
                    )
                )


                validation = None

                if pipeline_config.validate:

                    validation = (
                        build_validation_report(
                            fallback_curriculum
                        )
                    )


                return CurriculumExtractionResult(

                    curriculum=fallback_curriculum,

                    raw_payload={},

                    raw_response="",

                    statistics=statistics,

                    validation=validation,

                    source_file=source_file,

                    source_type=detected_source_type,

                    success=False,

                    error=str(exc),

                )


            except Exception as fallback_error:

                log_error(
                    (
                        "Fallback curriculum creation "
                        f"also failed: {fallback_error}"
                    )
                )


        # ----------------------------------------------------
        # Last-resort empty curriculum
        # ----------------------------------------------------

        empty_curriculum = (
            create_empty_curriculum(
                source_file=source_file,
                source_type=detected_source_type,
            )
        )


        return CurriculumExtractionResult(

            curriculum=empty_curriculum,

            raw_payload={},

            raw_response="",

            statistics=(
                calculate_curriculum_statistics(
                    empty_curriculum
                )
            ),

            validation=None,

            source_file=source_file,

            source_type=detected_source_type,

            success=False,

            error=str(exc),

        )


# ============================================================
# CHUNKED LARGE-DOCUMENT EXTRACTION
# ============================================================

CHUNK_EXTRACTION_SYSTEM_PROMPT = """
You are a precise university syllabus extraction engine.

Extract ONLY information explicitly supported by the supplied
syllabus section.

Return ONLY valid JSON. No Markdown. No explanation.
Do not invent information.

Use this compact structure:
{
  "metadata": {},
  "title": null,
  "description": null,
  "objectives": [],
  "prerequisites": [],
  "modules": [],
  "concepts": [],
  "skills": [],
  "tools": [],
  "technologies": [],
  "projects": [],
  "course_outcomes": [],
  "program_outcomes": [],
  "program_specific_outcomes": [],
  "co_po_mappings": [],
  "co_pso_mappings": [],
  "total_hours": 0,
  "total_credits": 0,
  "extraction_confidence": 0,
  "notes": []
}

For modules preserve names, order, topics, hours and descriptions.
For outcomes preserve their original codes and wording.
If information is absent, use [] or null.
"""


def build_chunk_extraction_prompt(
    chunk: str,
    chunk_index: int,
    total_chunks: int,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> str:
    return f"""
SOURCE FILE: {source_file or 'Unknown'}
SOURCE TYPE: {source_type or 'text'}
SECTION: {chunk_index} of {total_chunks}

{CHUNK_EXTRACTION_SYSTEM_PROMPT}

SYLLABUS SECTION:
---------------- BEGIN SECTION ----------------
{chunk}
----------------- END SECTION -----------------

Return ONLY JSON.
"""


def merge_chunk_payloads(
    payloads: List[Dict[str, Any]],
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Merge chunk-level JSON locally; never send the merged payload back to Groq."""

    merged: Dict[str, Any] = {
        "metadata": {},
        "title": None,
        "description": None,
        "objectives": [],
        "prerequisites": [],
        "modules": [],
        "concepts": [],
        "skills": [],
        "tools": [],
        "technologies": [],
        "projects": [],
        "course_outcomes": [],
        "program_outcomes": [],
        "program_specific_outcomes": [],
        "co_po_mappings": [],
        "co_pso_mappings": [],
        "total_hours": 0,
        "total_credits": 0,
        "extraction_confidence": 0,
        "notes": [],
    }

    list_fields = [
        "objectives",
        "prerequisites",
        "modules",
        "concepts",
        "skills",
        "tools",
        "technologies",
        "projects",
        "course_outcomes",
        "program_outcomes",
        "program_specific_outcomes",
        "co_po_mappings",
        "co_pso_mappings",
        "notes",
    ]

    def item_key(item: Any) -> str:
        if isinstance(item, dict):
            # Prefer semantic identifiers when present.
            for key in (
                "module_id", "topic_id", "code", "name",
                "title", "skill", "tool", "technology",
            ):
                value = item.get(key)
                if value:
                    return f"{key}:{str(value).strip().lower()}"
            return json.dumps(item, sort_keys=True, default=str).lower()
        return str(item).strip().lower()

    for payload in payloads:
        if not isinstance(payload, dict):
            continue

        metadata = payload.get("metadata")
        if isinstance(metadata, dict):
            for key, value in metadata.items():
                if value not in (None, "", [], {}) and not merged["metadata"].get(key):
                    merged["metadata"][key] = value

        for scalar in ("title", "description"):
            value = payload.get(scalar)
            if value not in (None, "") and not merged.get(scalar):
                merged[scalar] = value

        for field in list_fields:
            values = payload.get(field, [])
            if not isinstance(values, list):
                values = [values]

            existing = {
                item_key(item)
                for item in merged[field]
            }

            for item in values:
                if item is None:
                    continue
                key = item_key(item)
                if key not in existing:
                    merged[field].append(item)
                    existing.add(key)

        for scalar in ("total_hours", "total_credits"):
            value = payload.get(scalar)
            if isinstance(value, (int, float)) and value > 0:
                merged[scalar] += value

        confidence = payload.get("extraction_confidence")
        if isinstance(confidence, (int, float)):
            merged["extraction_confidence"] = max(
                merged["extraction_confidence"],
                confidence,
            )

    if source_file:
        merged["metadata"].setdefault("source_file", source_file)
    if source_type:
        merged["metadata"].setdefault("source_type", source_type)

    return merged


def extract_large_curriculum_payload(
    syllabus_text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
    pipeline_config: Optional[ExtractionPipelineConfig] = None,
) -> Dict[str, Any]:
    """Extract a large syllabus in small Groq requests."""

    pipeline_config = pipeline_config or ExtractionPipelineConfig()

    chunks = chunk_text(
        syllabus_text,
        chunk_size=DEFAULT_BATCH_SIZE,
        overlap=100,
    )

    if not chunks:
        raise ValueError("No usable syllabus chunks were created.")

    logger.info(
        "Large syllabus detected: %s characters -> %s chunks",
        len(syllabus_text),
        len(chunks),
    )

    payloads: List[Dict[str, Any]] = []

    for index, chunk in enumerate(chunks, start=1):
        logger.info(
            "Extracting syllabus chunk %s/%s (%s characters)",
            index,
            len(chunks),
            len(chunk),
        )

        chunk_config = ExtractorConfig(
            api_key=pipeline_config.groq_config.api_key,
            model=pipeline_config.groq_config.model,
            temperature=0.0,
            max_tokens=DEFAULT_CHUNK_MAX_TOKENS,
            timeout=pipeline_config.groq_config.timeout,
        )

        prompt = build_chunk_extraction_prompt(
            chunk=chunk,
            chunk_index=index,
            total_chunks=len(chunks),
            source_file=source_file,
            source_type=source_type,
        )

        try:
            response = call_groq_with_retry(
                prompt=prompt,
                system_prompt=CHUNK_EXTRACTION_SYSTEM_PROMPT,
                config=chunk_config,
                retries=0,
            )

            payload = extract_json_object(response)

        except Exception as chunk_error:
            logger.warning(
                "Chunk %s/%s failed: %s",
                index,
                len(chunks),
                chunk_error,
            )
            payload = None

        if payload is None:
            # Keep processing other chunks. A missing chunk should not
            # destroy the entire syllabus extraction.
            logger.warning(
                "Skipping chunk %s/%s because no valid JSON was returned.",
                index,
                len(chunks),
            )
        else:
            payloads.append(payload)

        # The current Groq organization reports an 8K TPM limit.
        # A short delay prevents consecutive chunk requests from
        # immediately exceeding that rolling limit.
        if index < len(chunks):
            time.sleep(DEFAULT_CHUNK_DELAY_SECONDS)

    if not payloads:
        raise RuntimeError(
            "All syllabus chunks failed to produce valid JSON. "
            "Check the Groq model, API key, rate limit, and response format."
        )

    return merge_chunk_payloads(
        payloads=payloads,
        source_file=source_file,
        source_type=source_type,
    )


# ============================================================
# 98. GENERATE CURRICULUM RESPONSE
# ============================================================

def generate_curriculum_response(
    syllabus_text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
    config: Optional[
        ExtractionPipelineConfig
    ] = None,
) -> str:
    """
    Generate the raw LLM response.

    Includes retry and JSON-repair attempts.
    """

    pipeline_config = (
        config
        or ExtractionPipelineConfig()
    )


    groq_config = (
        pipeline_config.groq_config
    )


    # --------------------------------------------------------
    # First attempt
    # --------------------------------------------------------

    try:

        return call_groq_with_retry(

            prompt=build_curriculum_prompt(

                syllabus_text=syllabus_text,

                source_file=source_file,

                source_type=source_type,

            ),

            system_prompt=CURRICULUM_SYSTEM_PROMPT,

            config=groq_config,

            retries=pipeline_config.retries,

        )

    except Exception as first_error:

        log_warning(
            (
                "Primary curriculum extraction "
                f"failed: {first_error}"
            )
        )


        # ----------------------------------------------------
        # JSON repair attempt
        # ----------------------------------------------------

        repair_prompt = build_json_repair_prompt(
            syllabus_text=syllabus_text,
            source_file=source_file,
            source_type=source_type,
        )


        try:

            return call_groq_with_retry(

                prompt=repair_prompt,

                system_prompt=CURRICULUM_SYSTEM_PROMPT,

                config=groq_config,

                retries=1,

            )

        except Exception as repair_error:

            raise RuntimeError(

                (
                    "Both primary and repair "
                    "LLM extraction attempts failed. "
                    f"Primary: {first_error}; "
                    f"Repair: {repair_error}"
                )

            ) from repair_error


# ============================================================
# 99. JSON REPAIR PROMPT
# ============================================================

def build_json_repair_prompt(
    syllabus_text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> str:
    """
    Build a more conservative extraction prompt.

    Used when the primary extraction failed.
    """

    return f"""
You are a strict academic syllabus extraction engine.

Extract structured curriculum information from the syllabus
below.

The previous extraction attempt failed.

This time:

1. Return ONLY valid JSON.
2. Do NOT use Markdown.
3. Do NOT include commentary.
4. Do NOT invent missing information.
5. Use null for unavailable scalar fields.
6. Use [] for unavailable list fields.
7. Preserve the order of modules and topics.
8. Extract Course Outcomes exactly when present.
9. Extract Program Outcomes exactly when present.
10. Extract Program Specific Outcomes exactly when present.

Required top-level JSON:

{{
  "metadata": {{}},
  "title": null,
  "description": null,
  "objectives": [],
  "prerequisites": [],
  "modules": [],
  "concepts": [],
  "skills": [],
  "tools": [],
  "technologies": [],
  "projects": [],
  "course_outcomes": [],
  "program_outcomes": [],
  "program_specific_outcomes": [],
  "co_po_mappings": [],
  "co_pso_mappings": [],
  "total_hours": 0,
  "total_credits": 0,
  "extraction_confidence": 0,
  "notes": []
}}

SOURCE FILE:
{source_file or "Unknown"}

SOURCE TYPE:
{source_type or "text"}

SYLLABUS:

---------------- BEGIN ----------------

{syllabus_text}

----------------- END -----------------

Return ONLY JSON.
"""


# ============================================================
# 100. FALLBACK CURRICULUM CREATOR
# ============================================================

def create_fallback_curriculum(
    syllabus_text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Curriculum:
    """
    Create a lightweight curriculum when LLM extraction
    fails completely.

    This does NOT attempt semantic AI extraction.

    It preserves useful document information so the UI
    can still show something instead of crashing.
    """

    text = clean_text(
        syllabus_text
    )


    metadata = build_course_metadata(
        {
            "source_file":
                source_file,

            "source_type":
                source_type,

        },
        source_file=source_file,
        source_type=source_type,
    )


    # --------------------------------------------------------
    # Detect obvious title
    # --------------------------------------------------------

    lines = [

        clean_text(line)

        for line in text.split("\n")

        if clean_text(line)

    ]


    title = None


    if lines:

        for line in lines[:20]:

            lowered = line.lower()


            if any(

                keyword in lowered

                for keyword in [
                    "syllabus",
                    "course",
                    "subject",
                    "curriculum",
                ]

            ):

                title = line

                break


        if title is None:

            title = lines[0]


    # --------------------------------------------------------
    # Basic module detection
    # --------------------------------------------------------

    modules: List[Module] = []


    module_pattern = re.compile(

        r"^(unit|module|chapter)"
        r"\s*[-:]?\s*(\d+)"
        r"\s*[:.\-–]?\s*(.*)$",

        re.IGNORECASE,

    )


    current_module = None

    current_topics = []


    def flush_module() -> None:

        nonlocal current_module
        nonlocal current_topics


        if not current_module:

            return


        module_data = {

            "module_id":
                current_module["module_id"],

            "module_name":
                current_module["module_name"],

            "sequence":
                current_module["sequence"],

            "topics":
                current_topics,

        }


        modules.append(

            build_module(

                module_data,

                index=len(modules) + 1,

            )

        )


        current_module = None

        current_topics = []


    for line in lines:

        match = module_pattern.match(
            line
        )


        if match:

            flush_module()


            number = safe_int(
                match.group(2),
                len(modules) + 1,
            )


            name = clean_text(
                match.group(3)
            )


            if not name:

                name = (
                    f"Module {number}"
                )


            current_module = {

                "module_id":
                    f"M{number}",

                "module_name":
                    name,

                "sequence":
                    number,

            }


            continue


        # ----------------------------------------------------
        # Topic-like lines
        # ----------------------------------------------------

        if current_module:

            if (
                len(line) <= 250
                and not line.endswith(":")
            ):

                current_topics.append(
                    {
                        "topic_id":
                            f"T{len(current_topics) + 1}",

                        "topic_name":
                            line,

                        "sequence":
                            len(current_topics) + 1,

                    }
                )


    flush_module()


    # --------------------------------------------------------
    # If no modules were detected
    # --------------------------------------------------------

    if not modules:

        fallback_topics = []


        for index, line in enumerate(
            lines[:50],
            start=1,
        ):

            if len(line) > 250:
                continue


            if len(line) < 3:
                continue


            fallback_topics.append(
                {
                    "topic_id":
                        f"T{index}",

                    "topic_name":
                        line,

                    "sequence":
                        index,

                }
            )


        if fallback_topics:

            modules = [

                build_module(

                    {
                        "module_id":
                            "M1",

                        "module_name":
                            "Extracted Content",

                        "sequence":
                            1,

                        "topics":
                            fallback_topics,

                    },

                    index=1,

                )

            ]


    return create_model_safe(

        Curriculum,

        {

            "metadata":
                metadata,

            "title":
                title,

            "description":
                (
                    "Fallback curriculum generated "
                    "from document text."
                ),

            "objectives":
                [],

            "prerequisites":
                [],

            "modules":
                modules,

            "concepts":
                [],

            "skills":
                [],

            "tools":
                [],

            "technologies":
                [],

            "projects":
                [],

            "course_outcomes":
                [],

            "program_outcomes":
                [],

            "program_specific_outcomes":
                [],

            "co_po_mappings":
                [],

            "co_pso_mappings":
                [],

            "total_hours":
                calculate_total_hours(
                    modules
                ),

            "total_credits":
                calculate_total_credits(
                    modules,
                    metadata,
                ),

            "extraction_confidence":
                20,

            "notes":
                [
                    (
                        "AI extraction failed. "
                        "Fallback structural extraction "
                        "was used."
                    )
                ],

        },

        "Fallback Curriculum",

    )


# ============================================================
# 101. EXTRACT CURRICULUM FROM DICTIONARY
# ============================================================

def extract_curriculum_from_payload(
    payload: Dict[str, Any],
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
    validate: bool = True,
) -> CurriculumExtractionResult:
    """
    Build a Curriculum directly from an existing JSON payload.

    Useful when:

        - Testing
        - Loading cached LLM results
        - Reprocessing previous extraction
        - Unit tests
    """

    try:

        curriculum = build_curriculum(

            payload=payload,

            source_file=source_file,

            source_type=source_type,

        )


        statistics = (
            calculate_curriculum_statistics(
                curriculum
            )
        )


        validation = None


        if validate:

            validation = (
                build_validation_report(
                    curriculum
                )
            )


        return CurriculumExtractionResult(

            curriculum=curriculum,

            raw_payload=payload,

            statistics=statistics,

            validation=validation,

            source_file=source_file,

            source_type=source_type,

            success=True,

        )


    except Exception as exc:

        log_error(
            (
                "Payload curriculum extraction "
                f"failed: {exc}"
            )
        )


        empty = create_empty_curriculum(

            source_file=source_file,

            source_type=source_type,

        )


        return CurriculumExtractionResult(

            curriculum=empty,

            raw_payload=payload,

            statistics=(
                calculate_curriculum_statistics(
                    empty
                )
            ),

            source_file=source_file,

            source_type=source_type,

            success=False,

            error=str(exc),

        )


# ============================================================
# 102. EXTRACT FROM FILE TEXT
# ============================================================

def extract_curriculum_from_text(
    text: str,
    filename: Optional[str] = None,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
    config: Optional[
        ExtractionPipelineConfig
    ] = None,
    **kwargs: Any,
) -> CurriculumExtractionResult:
    """
    Convenience API for document loaders.

    Example:

        text = extract_pdf_text(...)
        result = extract_curriculum_from_text(
            text,
            "syllabus.pdf"
        )
    """

    effective_source_file = (
        source_file
        or filename
    )

    effective_source_type = detect_source_type(
        filename=effective_source_file,
        source_type=source_type,
    )

    return extract_curriculum(

        syllabus_text=text,

        source_file=effective_source_file,

        source_type=effective_source_type,

        config=config,

        **kwargs,

    )


# ============================================================
# 103. EXTRACT FROM PDF/DOCX/OCR OUTPUT
# ============================================================

def extract_curriculum_from_document_text(
    text: str,
    filename: Optional[str] = None,
    source_type: Optional[str] = None,
    config: Optional[
        ExtractionPipelineConfig
    ] = None,
) -> CurriculumExtractionResult:
    """
    General document extraction API.

    The document loading itself is intentionally handled
    outside this module.

    Recommended architecture:

        rag/pdf_loader.py
                 ↓
              text
                 ↓
        extractor.py
    """

    return extract_curriculum(

        syllabus_text=text,

        source_file=filename,

        source_type=source_type,

        config=config,

    )


# ============================================================
# 104. QUICK EXTRACTION
# ============================================================

def quick_extract(
    text: str,
) -> Curriculum:
    """
    Simple API when only Curriculum is required.

    Example:

        curriculum = quick_extract(text)
    """

    result = extract_curriculum(
        syllabus_text=text
    )


    return result.curriculum


# ============================================================
# 105. END OF CHUNK 7
# ============================================================
# ============================================================
# curriculum/extractor.py
# CHUNK 8/8
#
# FINAL UTILITIES
#
# Serialization
# Loading
# Merging
# Versioning
# Diagnostics
# Public API
# Standalone Test
# ============================================================


# ============================================================
# 106. MODEL TO DICTIONARY
# ============================================================

def model_to_dict(
    model: Any,
) -> Dict[str, Any]:
    """
    Convert a Pydantic model or regular object to dict.
    """

    if model is None:

        return {}


    if hasattr(
        model,
        "model_dump",
    ):

        return model.model_dump(
            mode="json"
        )


    if hasattr(
        model,
        "dict",
    ):

        return model.dict()


    if isinstance(
        model,
        dict,
    ):

        return model


    try:

        return dict(
            model
        )

    except Exception:

        return {}


# ============================================================
# 107. CURRICULUM TO DICT
# ============================================================

def curriculum_to_dict(
    curriculum: Curriculum,
) -> Dict[str, Any]:
    """
    Convert Curriculum into JSON-compatible dictionary.
    """

    return model_to_dict(
        curriculum
    )


# ============================================================
# 108. CURRICULUM TO JSON
# ============================================================

def curriculum_to_json(
    curriculum: Curriculum,
    indent: int = 2,
) -> str:
    """
    Serialize Curriculum to JSON.
    """

    data = curriculum_to_dict(
        curriculum
    )


    return json.dumps(
        data,
        indent=indent,
        ensure_ascii=False,
        default=str,
    )


# ============================================================
# 109. SAVE CURRICULUM JSON
# ============================================================

def save_curriculum_json(
    curriculum: Curriculum,
    filepath: str,
    indent: int = 2,
) -> str:
    """
    Save Curriculum to a JSON file.

    Returns the absolute file path.
    """

    path = Path(
        filepath
    ).expanduser().resolve()


    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    content = curriculum_to_json(
        curriculum,
        indent=indent,
    )


    path.write_text(
        content,
        encoding="utf-8",
    )


    log_info(
        f"Curriculum saved: {path}"
    )


    return str(
        path
    )


# ============================================================
# 110. LOAD CURRICULUM JSON
# ============================================================

def load_curriculum_json(
    filepath: str,
) -> Curriculum:
    """
    Load a Curriculum from a JSON file.
    """

    path = Path(
        filepath
    ).expanduser().resolve()


    if not path.exists():

        raise FileNotFoundError(
            f"Curriculum file not found: {path}"
        )


    content = path.read_text(
        encoding="utf-8"
    )


    payload = json.loads(
        content
    )


    if not isinstance(
        payload,
        dict,
    ):

        raise ValueError(
            "Curriculum JSON root must be an object."
        )


    return build_curriculum(
        payload
    )


# ============================================================
# 111. CURRICULUM SUMMARY
# ============================================================

def curriculum_summary(
    curriculum: Curriculum,
) -> Dict[str, Any]:
    """
    Generate a compact summary suitable for
    Streamlit dashboards.
    """

    statistics = (
        calculate_curriculum_statistics(
            curriculum
        )
    )


    return {

        "title":
            curriculum.title,

        "university":
            curriculum.metadata.university,

        "college":
            curriculum.metadata.college,

        "department":
            curriculum.metadata.department,

        "program":
            curriculum.metadata.program,

        "branch":
            curriculum.metadata.branch,

        "course_name":
            curriculum.metadata.course_name,

        "course_code":
            curriculum.metadata.course_code,

        "semester":
            curriculum.metadata.semester,

        "credits":
            curriculum.total_credits,

        "hours":
            curriculum.total_hours,

        "modules":
            statistics.total_modules,

        "topics":
            statistics.total_topics,

        "concepts":
            statistics.total_concepts,

        "skills":
            statistics.total_skills,

        "tools":
            statistics.total_tools,

        "technologies":
            statistics.total_technologies,

        "projects":
            statistics.total_projects,

        "course_outcomes":
            statistics.total_course_outcomes,

        "program_outcomes":
            statistics.total_program_outcomes,

        "program_specific_outcomes":
            statistics.total_program_specific_outcomes,

        "extraction_confidence":
            curriculum.extraction_confidence,

    }


# ============================================================
# 112. CALCULATE CURRICULUM STATISTICS
# ============================================================

def calculate_curriculum_statistics(
    curriculum: Curriculum,
) -> CurriculumStatistics:
    """
    Calculate curriculum-level statistics.
    """

    total_modules = len(
        curriculum.modules
    )


    total_topics = sum(

        len(
            module.topics
        )

        for module in curriculum.modules

    )


    total_concepts = len(
        curriculum.concepts
    )


    total_skills = len(
        curriculum.skills
    )


    total_tools = len(
        curriculum.tools
    )


    total_technologies = len(
        curriculum.technologies
    )


    total_projects = len(
        curriculum.projects
    )


    total_course_outcomes = len(
        curriculum.course_outcomes
    )


    total_program_outcomes = len(
        curriculum.program_outcomes
    )


    total_program_specific_outcomes = len(
        curriculum.program_specific_outcomes
    )


    total_case_studies = 0


    total_learning_objectives = len(
        curriculum.objectives
    )


    for module in curriculum.modules:

        total_case_studies += len(
            module.case_studies
        )


        total_learning_objectives += len(
            module.learning_objectives
        )


        for topic in module.topics:

            total_case_studies += len(
                topic.case_studies
            )


            total_learning_objectives += len(
                topic.learning_objectives
            )


    return create_statistics_model(
        {
            "total_modules":
                total_modules,

            "total_topics":
                total_topics,

            "total_concepts":
                total_concepts,

            "total_skills":
                total_skills,

            "total_tools":
                total_tools,

            "total_technologies":
                total_technologies,

            "total_projects":
                total_projects,

            "total_case_studies":
                total_case_studies,

            "total_course_outcomes":
                total_course_outcomes,

            "total_program_outcomes":
                total_program_outcomes,

            "total_program_specific_outcomes":
                total_program_specific_outcomes,

            "total_learning_objectives":
                total_learning_objectives,

            "total_hours":
                curriculum.total_hours,

            "total_credits":
                curriculum.total_credits,

            "extraction_confidence":
                curriculum.extraction_confidence,

        }
    )


# ============================================================
# 113. CREATE STATISTICS MODEL
# ============================================================

def create_statistics_model(
    data: Dict[str, Any],
) -> CurriculumStatistics:
    """
    Create CurriculumStatistics safely.
    """

    try:

        return CurriculumStatistics.model_validate(
            data
        )

    except ValidationError:

        # ----------------------------------------------------
        # If the installed models.py uses a smaller schema,
        # create only fields accepted by that schema.
        # ----------------------------------------------------

        try:

            fields = (
                CurriculumStatistics.model_fields
            )


            filtered = {

                key: value

                for key, value in data.items()

                if key in fields

            }


            return CurriculumStatistics.model_validate(
                filtered
            )

        except Exception as exc:

            raise ValueError(
                (
                    "Unable to create "
                    f"CurriculumStatistics: {exc}"
                )
            ) from exc


# ============================================================
# 114. VALIDATION REPORT
# ============================================================

def build_validation_report(
    curriculum: Curriculum,
) -> Dict[str, Any]:
    """
    Perform practical structural validation.

    Returns a dictionary rather than raising errors.

    This is useful for Streamlit.
    """

    errors: List[str] = []

    warnings: List[str] = []

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    if not curriculum.metadata.course_name:

        warnings.append(
            "Course/Subject name was not identified."
        )


    if not curriculum.metadata.course_code:

        warnings.append(
            "Course/Subject code was not identified."
        )


    # --------------------------------------------------------
    # Modules
    # --------------------------------------------------------

    if not curriculum.modules:

        warnings.append(
            "No modules/units were extracted."
        )


    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    for module in curriculum.modules:

        if not module.topics:

            warnings.append(
                (
                    f"{module.module_name}: "
                    "No topics were extracted."
                )
            )


    # --------------------------------------------------------
    # Outcomes
    # --------------------------------------------------------

    if not curriculum.course_outcomes:

        warnings.append(
            "No Course Outcomes were identified."
        )


    # --------------------------------------------------------
    # Duplicate modules
    # --------------------------------------------------------

    module_names = [

        module.module_name.lower()

        for module in curriculum.modules

    ]


    duplicate_modules = (
        find_duplicates(
            module_names
        )
    )


    if duplicate_modules:

        warnings.append(
            (
                "Duplicate module names detected: "
                + ", ".join(
                    duplicate_modules
                )
            )
        )


    # --------------------------------------------------------
    # Duplicate topics
    # --------------------------------------------------------

    topic_names = []


    for module in curriculum.modules:

        topic_names.extend(

            topic.topic_name.lower()

            for topic in module.topics

        )


    duplicate_topics = (
        find_duplicates(
            topic_names
        )
    )


    if duplicate_topics:

        warnings.append(
            (
                "Duplicate topic names detected: "
                + ", ".join(
                    duplicate_topics[:10]
                )
            )
        )


    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    if curriculum.extraction_confidence < 40:

        warnings.append(
            "Extraction confidence is low."
        )


    elif curriculum.extraction_confidence < 70:

        warnings.append(
            "Extraction confidence is moderate."
        )


    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

        "warnings":
            warnings,

        "error_count":
            len(errors),

        "warning_count":
            len(warnings),

        "confidence":
            curriculum.extraction_confidence,

    }


# ============================================================
# 115. FIND DUPLICATES
# ============================================================

def find_duplicates(
    values: List[str],
) -> List[str]:
    """
    Return duplicate values while preserving order.
    """

    seen = set()

    duplicates = set()

    result = []


    for value in values:

        key = clean_text(
            value
        ).lower()


        if not key:
            continue


        if key in seen:

            if key not in duplicates:

                duplicates.add(
                    key
                )

                result.append(
                    value
                )

        else:

            seen.add(
                key
            )


    return result


# ============================================================
# 116. MERGE CURRICULUMS
# ============================================================

def merge_curriculums(
    base: Curriculum,
    additional: Curriculum,
) -> Curriculum:
    """
    Merge two curriculum objects.

    Useful when:

        - syllabus spans multiple documents
        - regulation documents are split
        - theory and practical syllabus are separate
        - multiple pages were independently processed
    """

    # --------------------------------------------------------
    # Modules
    # --------------------------------------------------------

    modules = list(
        base.modules
    )


    existing_modules = {
        module.module_name.lower()
        for module in modules
    }


    for module in additional.modules:

        key = module.module_name.lower()


        if key not in existing_modules:

            modules.append(
                module
            )

            existing_modules.add(
                key
            )


    # --------------------------------------------------------
    # Concepts
    # --------------------------------------------------------

    concepts = merge_concepts(

        base.concepts,

        additional.concepts,

    )


    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    skills = merge_skills(

        base.skills,

        additional.skills,

    )


    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    tools = merge_tools(

        base.tools,

        additional.tools,

    )


    # --------------------------------------------------------
    # Technologies
    # --------------------------------------------------------

    technologies = merge_technologies(

        base.technologies,

        additional.technologies,

    )


    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    projects = []

    seen_projects = set()


    for project in [

        *base.projects,

        *additional.projects,

    ]:

        key = project.title.lower()


        if key in seen_projects:

            continue


        seen_projects.add(
            key
        )


        projects.append(
            project
        )


    # --------------------------------------------------------
    # Objectives
    # --------------------------------------------------------

    objectives = merge_objectives(

        base.objectives,

        additional.objectives,

    )


    # --------------------------------------------------------
    # Outcomes
    # --------------------------------------------------------

    course_outcomes = merge_outcome_models(

        base.course_outcomes,

        additional.course_outcomes,

        "code",

    )


    program_outcomes = merge_outcome_models(

        base.program_outcomes,

        additional.program_outcomes,

        "code",

    )


    program_specific_outcomes = (
        merge_outcome_models(

            base.program_specific_outcomes,

            additional.program_specific_outcomes,

            "code",

        )
    )


    # --------------------------------------------------------
    # Mappings
    # --------------------------------------------------------

    co_po_mappings = merge_mapping_models(

        base.co_po_mappings,

        additional.co_po_mappings,

        (
            "co_code",
            "po_code",
        ),

    )


    co_pso_mappings = merge_mapping_models(

        base.co_pso_mappings,

        additional.co_pso_mappings,

        (
            "co_code",
            "pso_code",
        ),

    )


    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = base.metadata


    # Prefer additional metadata when base is missing.
    metadata = merge_metadata(
        base.metadata,
        additional.metadata,
    )


    # --------------------------------------------------------
    # Build merged curriculum
    # --------------------------------------------------------

    merged_payload = {

        "metadata":
            model_to_dict(
                metadata
            ),

        "title":
            base.title
            or additional.title,

        "description":
            base.description
            or additional.description,

        "objectives":
            [
                model_to_dict(
                    item
                )
                for item in objectives
            ],

        "prerequisites":
            unique_strings(
                [
                    *base.prerequisites,
                    *additional.prerequisites,
                ]
            ),

        "modules":
            [
                model_to_dict(
                    item
                )
                for item in modules
            ],

        "concepts":
            [
                model_to_dict(
                    item
                )
                for item in concepts
            ],

        "skills":
            [
                model_to_dict(
                    item
                )
                for item in skills
            ],

        "tools":
            [
                model_to_dict(
                    item
                )
                for item in tools
            ],

        "technologies":
            [
                model_to_dict(
                    item
                )
                for item in technologies
            ],

        "projects":
            [
                model_to_dict(
                    item
                )
                for item in projects
            ],

        "course_outcomes":
            [
                model_to_dict(
                    item
                )
                for item in course_outcomes
            ],

        "program_outcomes":
            [
                model_to_dict(
                    item
                )
                for item in program_outcomes
            ],

        "program_specific_outcomes":
            [
                model_to_dict(
                    item
                )
                for item in program_specific_outcomes
            ],

        "co_po_mappings":
            [
                model_to_dict(
                    item
                )
                for item in co_po_mappings
            ],

        "co_pso_mappings":
            [
                model_to_dict(
                    item
                )
                for item in co_pso_mappings
            ],

        "total_hours":
            calculate_total_hours(
                modules
            ),

        "total_credits":
            calculate_total_credits(
                modules,
                metadata,
            ),

        "extraction_confidence":
            max(
                base.extraction_confidence,
                additional.extraction_confidence,
            ),

        "notes":
            unique_strings(
                [
                    *base.notes,
                    *additional.notes,
                ]
            ),

    }


    return build_curriculum(
        merged_payload
    )


# ============================================================
# 117. MERGE OBJECTIVES
# ============================================================

def merge_objectives(
    primary: List[Any],
    secondary: List[Any],
) -> List[Any]:
    """
    Merge objective objects.
    """

    result = []

    seen = set()


    for item in [
        *primary,
        *secondary,
    ]:

        description = clean_text(
            getattr(
                item,
                "description",
                "",
            )
        )


        key = description.lower()


        if not key:
            continue


        if key in seen:
            continue


        seen.add(
            key
        )


        result.append(
            item
        )


    return result


# ============================================================
# 118. MERGE OUTCOME MODELS
# ============================================================

def merge_outcome_models(
    primary: List[Any],
    secondary: List[Any],
    key_field: str,
) -> List[Any]:
    """
    Merge outcome models by code.
    """

    result = []

    seen = set()


    for item in [
        *primary,
        *secondary,
    ]:

        key = clean_text(
            getattr(
                item,
                key_field,
                "",
            )
        ).upper()


        if not key:
            continue


        if key in seen:
            continue


        seen.add(
            key
        )


        result.append(
            item
        )


    return result


# ============================================================
# 119. MERGE MAPPING MODELS
# ============================================================

def merge_mapping_models(
    primary: List[Any],
    secondary: List[Any],
    key_fields: tuple,
) -> List[Any]:
    """
    Merge mapping objects by composite key.
    """

    result = []

    seen = set()


    for item in [
        *primary,
        *secondary,
    ]:

        key = tuple(

            clean_text(
                getattr(
                    item,
                    field,
                    "",
                )
            ).upper()

            for field in key_fields

        )


        if key in seen:
            continue


        seen.add(
            key
        )


        result.append(
            item
        )


    return result


# ============================================================
# 120. MERGE METADATA
# ============================================================

def merge_metadata(
    base: CourseMetadata,
    additional: CourseMetadata,
) -> CourseMetadata:
    """
    Prefer non-empty base metadata, otherwise use
    additional metadata.
    """

    base_data = model_to_dict(
        base
    )


    additional_data = model_to_dict(
        additional
    )


    merged = dict(
        base_data
    )


    for key, value in additional_data.items():

        current = merged.get(
            key
        )


        if (
            current is None
            or current == ""
            or current == []
            or current == 0
        ):

            merged[key] = value


    return create_model_safe(
        CourseMetadata,
        merged,
        "Merged CourseMetadata",
    )


# ============================================================
# 121. CREATE EMPTY CURRICULUM
# ============================================================

def create_empty_curriculum(
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Curriculum:
    """
    Create a valid empty Curriculum.

    Used when extraction completely fails.
    """

    metadata = build_course_metadata(

        {
            "source_file":
                source_file,

            "source_type":
                source_type,

        },

        source_file=source_file,

        source_type=source_type,

    )


    payload = {

        "metadata":
            model_to_dict(
                metadata
            ),

        "title":
            None,

        "description":
            None,

        "objectives":
            [],

        "prerequisites":
            [],

        "modules":
            [],

        "concepts":
            [],

        "skills":
            [],

        "tools":
            [],

        "technologies":
            [],

        "projects":
            [],

        "course_outcomes":
            [],

        "program_outcomes":
            [],

        "program_specific_outcomes":
            [],

        "co_po_mappings":
            [],

        "co_pso_mappings":
            [],

        "total_hours":
            0,

        "total_credits":
            0,

        "extraction_confidence":
            0,

        "notes":
            [
                "No curriculum data could be extracted."
            ],

    }


    return create_model_safe(
        Curriculum,
        payload,
        "Empty Curriculum",
    )


# ============================================================
# 122. DETECT SOURCE TYPE
# ============================================================

def detect_source_type(
    filename: Optional[str] = None,
    source_type: Optional[str] = None,
) -> str:
    """
    Determine document type.
    """

    if source_type:

        return clean_text(
            source_type
        ).lower()


    if not filename:

        return "text"


    extension = Path(
        filename
    ).suffix.lower()


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

        ".webp":
            "image",

        ".tif":
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
        "text",
    )


# ============================================================
# 123. PREPARE INPUT TEXT
# ============================================================

def prepare_input_text(
    text: str,
    max_characters: Optional[int] = None,
) -> str:
    """
    Clean extracted document text before sending it
    to the LLM.
    """

    if text is None:

        raise ValueError(
            "Syllabus text cannot be None."
        )


    text = str(
        text
    )


    # --------------------------------------------------------
    # Normalize line endings
    # --------------------------------------------------------

    text = text.replace(
        "\r\n",
        "\n",
    )


    text = text.replace(
        "\r",
        "\n",
    )


    # --------------------------------------------------------
    # Remove null characters
    # --------------------------------------------------------

    text = text.replace(
        "\x00",
        "",
    )


    # --------------------------------------------------------
    # Collapse excessive whitespace
    # --------------------------------------------------------

    lines = []

    previous_blank = False


    for line in text.split(
        "\n"
    ):

        line = line.strip()


        if not line:

            if previous_blank:
                continue

            previous_blank = True

            lines.append(
                ""
            )

            continue


        previous_blank = False

        lines.append(
            line
        )


    cleaned = "\n".join(
        lines
    ).strip()


    if not cleaned:

        raise ValueError(
            "Syllabus text is empty."
        )


    # --------------------------------------------------------
    # Optional truncation
    # --------------------------------------------------------

    if (
        max_characters
        and len(cleaned)
        > max_characters
    ):

        log_warning(
            (
                "Syllabus text exceeds "
                f"{max_characters} characters. "
                "Input will be truncated."
            )
        )


        cleaned = cleaned[
            :max_characters
        ]


    return cleaned


# ============================================================
# 124. EXTRACTION DIAGNOSTICS
# ============================================================

def extraction_diagnostics(
    result: CurriculumExtractionResult,
) -> Dict[str, Any]:
    """
    Return diagnostics for Streamlit UI and logging.
    """

    curriculum = (
        result.curriculum
    )


    statistics = (
        result.statistics
    )


    validation = (
        result.validation
    )


    return {

        "success":
            result.success,

        "error":
            result.error,

        "source_file":
            result.source_file,

        "source_type":
            result.source_type,

        "confidence":
            curriculum.extraction_confidence,

        "modules":
            statistics.total_modules,

        "topics":
            statistics.total_topics,

        "concepts":
            statistics.total_concepts,

        "skills":
            statistics.total_skills,

        "tools":
            statistics.total_tools,

        "technologies":
            statistics.total_technologies,

        "projects":
            statistics.total_projects,

        "course_outcomes":
            statistics.total_course_outcomes,

        "program_outcomes":
            statistics.total_program_outcomes,

        "program_specific_outcomes":
            statistics.total_program_specific_outcomes,

        "validation_valid":
            (
                validation.get(
                    "valid",
                    False,
                )
                if isinstance(
                    validation,
                    dict,
                )
                else None
            ),

        "warnings":
            (
                validation.get(
                    "warnings",
                    [],
                )
                if isinstance(
                    validation,
                    dict,
                )
                else []
            ),

        "errors":
            (
                validation.get(
                    "errors",
                    [],
                )
                if isinstance(
                    validation,
                    dict,
                )
                else []
            ),

    }


# ============================================================
# 125. EXPORT EXTRACTION RESULT
# ============================================================

def save_extraction_result(
    result: CurriculumExtractionResult,
    filepath: str,
) -> str:
    """
    Save the complete extraction result.

    Includes:
        curriculum
        statistics
        validation
        metadata
        diagnostics
    """

    path = Path(
        filepath
    ).expanduser().resolve()


    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    data = result.to_dict()


    data["diagnostics"] = (
        extraction_diagnostics(
            result
        )
    )


    path.write_text(

        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),

        encoding="utf-8",

    )


    log_info(
        f"Extraction result saved: {path}"
    )


    return str(
        path
    )


# ============================================================
# 126. RELOAD EXTRACTION RESULT
# ============================================================

def load_extraction_result(
    filepath: str,
) -> CurriculumExtractionResult:
    """
    Load a previously saved extraction result.
    """

    path = Path(
        filepath
    ).expanduser().resolve()


    if not path.exists():

        raise FileNotFoundError(
            f"Extraction result not found: {path}"
        )


    data = json.loads(

        path.read_text(
            encoding="utf-8"
        )

    )


    curriculum_data = data.get(
        "curriculum",
        {},
    )


    curriculum = build_curriculum(
        curriculum_data
    )


    statistics = (
        calculate_curriculum_statistics(
            curriculum
        )
    )


    validation = (
        build_validation_report(
            curriculum
        )
    )


    return CurriculumExtractionResult(

        curriculum=curriculum,

        raw_payload=data.get(
            "raw_payload",
            {},
        ),

        raw_response=data.get(
            "raw_response",
            "",
        ),

        statistics=statistics,

        validation=validation,

        source_file=data.get(
            "source_file"
        ),

        source_type=data.get(
            "source_type"
        ),

        success=data.get(
            "success",
            True,
        ),

        error=data.get(
            "error"
        ),

    )


# ============================================================
# 127. CURRICULUM VERSION
# ============================================================

EXTRACTOR_VERSION = "1.0.0"


def curriculum_version() -> str:
    """
    Return extractor version.
    """

    return EXTRACTOR_VERSION


# ============================================================
# 128. CURRICULUM FINGERPRINT
# ============================================================

def curriculum_fingerprint(
    curriculum: Curriculum,
) -> str:
    """
    Generate a deterministic fingerprint.

    Useful for detecting whether a curriculum changed.
    """

    content = curriculum_to_json(
        curriculum,
        indent=0,
    )


    return hashlib.sha256(
        content.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# 129. COMPARE CURRICULUM FINGERPRINTS
# ============================================================

def curriculum_changed(
    old: Curriculum,
    new: Curriculum,
) -> bool:
    """
    Return True when curriculum content differs.
    """

    return (
        curriculum_fingerprint(
            old
        )
        !=
        curriculum_fingerprint(
            new
        )
    )

# ============================================================
# COMPATIBILITY API
# ============================================================

def extract_syllabus(
    text: str,
    source_file: Optional[str] = None,
    source_type: Optional[str] = None,
    **kwargs: Any,
):
    """
    Backward-compatible syllabus extraction API.

    This function is used by:
        pages/01_Extract_Syllabus.py

    Internally it delegates to the existing
    extract_curriculum_from_text() implementation.
    """

    if text is None:
        raise ValueError(
            "Syllabus text cannot be None."
        )

    text = prepare_input_text(
        text,
        max_characters=kwargs.get(
            "max_characters",
            DEFAULT_MAX_INPUT_CHARS,
        ),
    )

    result = extract_curriculum_from_text(
        text=text,
        source_file=source_file,
        source_type=(
            source_type
            or detect_source_type(
                filename=source_file
            )
        ),
        **{
            key: value
            for key, value in kwargs.items()
            if key != "max_characters"
        },
    )

    if not isinstance(
        result,
        CurriculumExtractionResult,
    ):
        raise ValueError(
            "Unexpected curriculum extraction result."
        )

    if not result.success:
        raise ValueError(
            result.error
            or "Curriculum extraction failed."
        )

    return model_to_dict(
        result.curriculum
    )
    
# ============================================================
# 130. PUBLIC EXTRACTION API
# ============================================================

__all__ = [

    # --------------------------------------------------------
    # Main extraction
    # --------------------------------------------------------
    "extract_syllabus",
    
    "extract_curriculum",

    "extract_curriculum_from_text",

    "extract_curriculum_from_document_text",

    "extract_curriculum_from_payload",

    "quick_extract",


    # --------------------------------------------------------
    # Builders
    # --------------------------------------------------------

    "build_curriculum",

    "build_modules",

    "build_module",

    "build_topic",

    "build_concept",

    "build_skill",

    "build_tool",

    "build_technology",

    "build_project",

    "build_course_outcomes",

    "build_program_outcomes",

    "build_program_specific_outcomes",


    # --------------------------------------------------------
    # Normalizers
    # --------------------------------------------------------

    "normalize_root_payload",

    "normalize_metadata",

    "normalize_modules",

    "normalize_topics",

    "normalize_concepts",

    "normalize_skills",

    "normalize_tools",

    "normalize_technologies",

    "normalize_projects",

    "normalize_course_outcomes",

    "normalize_program_outcomes",

    "normalize_program_specific_outcomes",

    "normalize_co_po_mappings",

    "normalize_co_pso_mappings",


    # --------------------------------------------------------
    # Statistics / validation
    # --------------------------------------------------------

    "calculate_curriculum_statistics",

    "build_validation_report",

    "curriculum_summary",

    "extraction_diagnostics",


    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    "curriculum_to_dict",

    "curriculum_to_json",

    "save_curriculum_json",

    "load_curriculum_json",

    "save_extraction_result",

    "load_extraction_result",


    # --------------------------------------------------------
    # Curriculum management
    # --------------------------------------------------------

    "merge_curriculums",

    "curriculum_fingerprint",

    "curriculum_changed",

    "curriculum_version",


    # --------------------------------------------------------
    # Utility
    # --------------------------------------------------------

    "detect_source_type",

    "prepare_input_text",

    "create_empty_curriculum",

    "EXTRACTOR_VERSION",

]


# ============================================================
# 131. STANDALONE TEST
# ============================================================

def _standalone_test() -> None:
    """
    Minimal local test.

    This test does NOT call Groq.

    It verifies that:
        - normalization works
        - module building works
        - curriculum construction works
        - statistics work
        - validation works
        - serialization works
    """

    sample_payload = {

        "metadata": {

            "university":
                "Sample University",

            "college":
                "Sample Engineering College",

            "department":
                "Computer Science",

            "program":
                "B.Tech",

            "branch":
                "Artificial Intelligence",

            "course_name":
                "Generative AI",

            "course_code":
                "AI501",

            "semester":
                "VII",

            "credits":
                4,

        },

        "title":
            "Generative Artificial Intelligence",

        "description":
            "Introduction to modern Generative AI.",

        "objectives": [

            {
                "code":
                    "OBJ1",

                "description":
                    "Understand Generative AI",

                "bloom_level":
                    "Understand",

            }

        ],

        "modules": [

            {

                "module_id":
                    "M1",

                "module_name":
                    "Introduction to Generative AI",

                "sequence":
                    1,

                "hours":
                    10,

                "topics": [

                    {

                        "topic_id":
                            "T1",

                        "topic_name":
                            "Large Language Models",

                        "hours":
                            4,

                        "skills": [
                            "Prompt Engineering"
                        ],

                        "concepts": [
                            "Transformers"
                        ],

                        "technologies": [
                            "LLM"
                        ],

                    },

                    {

                        "topic_id":
                            "T2",

                        "topic_name":
                            "RAG",

                        "hours":
                            6,

                        "skills": [
                            "RAG"
                        ],

                        "concepts": [
                            "Vector Search"
                        ],

                        "tools": [
                            "FAISS"
                        ],

                    },

                ],

                "skills": [

                    "Python",

                    "Prompt Engineering",

                ],

                "technologies": [

                    "LangChain",

                    "LangGraph",

                ],

            },

        ],

        "course_outcomes": [

            {

                "code":
                    "CO1",

                "description":
                    "Explain Generative AI concepts",

                "bloom_level":
                    "Understand",

            },

            {

                "code":
                    "CO2",

                "description":
                    "Develop a RAG application",

                "bloom_level":
                    "Create",

            },

        ],

        "program_outcomes": [

            {

                "code":
                    "PO1",

                "description":
                    "Apply engineering knowledge",

            }

        ],

        "program_specific_outcomes": [

            {

                "code":
                    "PSO1",

                "description":
                    "Develop AI solutions",

            }

        ],

        "co_po_mappings": [

            {

                "co_code":
                    "CO1",

                "po_code":
                    "PO1",

                "correlation":
                    3,

            }

        ],

        "co_pso_mappings": [

            {

                "co_code":
                    "CO2",

                "pso_code":
                    "PSO1",

                "correlation":
                    3,

            }

        ],

    }


    # --------------------------------------------------------
    # Build
    # --------------------------------------------------------

    curriculum = build_curriculum(

        sample_payload,

        source_file=
            "sample_syllabus.json",

        source_type=
            "json",

    )


    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    statistics = (
        calculate_curriculum_statistics(
            curriculum
        )
    )


    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    validation = (
        build_validation_report(
            curriculum
        )
    )


    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print(
        "\n"
        "==========================================\n"
        "CURRICULUM EXTRACTOR TEST\n"
        "=========================================="
    )


    print(
        "\nTitle:",
        curriculum.title,
    )


    print(
        "Course:",
        curriculum.metadata.course_name,
    )


    print(
        "Modules:",
        statistics.total_modules,
    )


    print(
        "Topics:",
        statistics.total_topics,
    )


    print(
        "Concepts:",
        statistics.total_concepts,
    )


    print(
        "Skills:",
        statistics.total_skills,
    )


    print(
        "Tools:",
        statistics.total_tools,
    )


    print(
        "Technologies:",
        statistics.total_technologies,
    )


    print(
        "Projects:",
        statistics.total_projects,
    )


    print(
        "Course Outcomes:",
        statistics.total_course_outcomes,
    )


    print(
        "Validation:",
        validation["valid"],
    )


    print(
        "Warnings:",
        len(
            validation["warnings"]
        ),
    )


    print(
        "Fingerprint:",
        curriculum_fingerprint(
            curriculum
        )[:16],
        "...",
    )


    print(
        "\n==========================================\n"
        "TEST COMPLETED\n"
        "=========================================="
    )


# ============================================================
# 132. PYTHON ENTRY POINT
# ============================================================

if __name__ == "__main__":

    _standalone_test()


# ============================================================
# END OF curriculum/extractor.py
# ============================================================