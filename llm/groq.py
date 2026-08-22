# ============================================================
# llm/groq.py
# ============================================================
#
# PragyanAI Curriculum Intelligence Platform
#
# Centralized Groq + Llama LLM Service
#
# Responsibilities:
#   - Groq API client
#   - Streamlit Secrets
#   - Text generation
#   - Structured JSON generation
#   - JSON extraction
#   - Retry handling
#   - Health check
#   - Curriculum analysis
#   - Industry analysis
#   - Gap analysis
#   - Enhancement generation
#   - Learning path generation
#
# IMPORTANT:
#   No .env file is required.
#
# Streamlit:
#
#   .streamlit/secrets.toml
#
#   GROQ_API_KEY = "gsk_xxxxxxxxx"
#   GROQ_MODEL = "llama-3.3-70b-versatile"
#
# ============================================================

from __future__ import annotations

import json
import logging
import os
import re
import time

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Union,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(
    "pragyanai.llm.groq"
)


# ============================================================
# CONSTANTS
# ============================================================

GROQ_SERVICE_VERSION = "2.0.0"

DEFAULT_MODEL = (
    "llama-3.3-70b-versatile"
)

DEFAULT_TEMPERATURE = 0.2

DEFAULT_MAX_TOKENS = 4096

DEFAULT_TIMEOUT = 120

DEFAULT_MAX_RETRIES = 3

DEFAULT_TOP_P = 1.0


# ============================================================
# OPTIONAL GROQ IMPORT
# ============================================================

try:

    from groq import Groq

except ImportError:

    Groq = None


# ============================================================
# OPTIONAL STREAMLIT IMPORT
# ============================================================

try:

    import streamlit as st

except ImportError:

    st = None


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/8
#
# CONFIGURATION + RESPONSE MODELS
# ============================================================


# ============================================================
# STREAMLIT SECRET READER
# ============================================================

def get_streamlit_secret(
    key: str,
    default: Optional[str] = None,
) -> Optional[str]:

    """
    Read a value from Streamlit Secrets.

    Priority:
        Streamlit Secrets
        -> Environment fallback

    Environment fallback is retained so that
    this module can also be tested outside Streamlit.
    """

    # --------------------------------------------------------
    # Streamlit Secrets
    # --------------------------------------------------------

    if st is not None:

        try:

            value = st.secrets.get(
                key,
                None,
            )

            if value is not None:

                return str(
                    value
                )

        except Exception as exc:

            logger.debug(

                "Streamlit secret lookup failed "
                "for %s: %s",

                key,

                exc,

            )

    # --------------------------------------------------------
    # Optional environment fallback
    # --------------------------------------------------------

    value = os.getenv(
        key
    )

    if value:

        return value

    return default


# ============================================================
# RESOLVE API KEY
# ============================================================

def resolve_api_key(
    explicit_key: Optional[str] = None,
) -> Optional[str]:

    """
    Resolve Groq API key.

    Priority:

        1. Explicit argument
        2. Streamlit Secrets
        3. Environment variable
    """

    if explicit_key:

        return explicit_key

    return get_streamlit_secret(
        "GROQ_API_KEY"
    )


# ============================================================
# RESOLVE MODEL
# ============================================================

def resolve_model(
    explicit_model: Optional[str] = None,
) -> str:

    """
    Resolve Groq model.

    Priority:

        1. Explicit model
        2. Streamlit Secrets
        3. Environment variable
        4. Default model
    """

    if explicit_model:

        return explicit_model

    return (

        get_streamlit_secret(
            "GROQ_MODEL"
        )

        or

        DEFAULT_MODEL

    )


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class GroqConfig:

    api_key: Optional[str] = None

    model: Optional[str] = None

    temperature: float = (
        DEFAULT_TEMPERATURE
    )

    max_tokens: int = (
        DEFAULT_MAX_TOKENS
    )

    timeout: int = (
        DEFAULT_TIMEOUT
    )

    max_retries: int = (
        DEFAULT_MAX_RETRIES
    )

    top_p: float = (
        DEFAULT_TOP_P
    )

    system_prompt: str = (

        "You are a senior AI curriculum "
        "intelligence and industry analysis "
        "expert working for PragyanAI. "
        "Provide accurate, structured, "
        "evidence-based responses. "
        "Do not hallucinate information."

    )

    def __post_init__(self):

        self.api_key = resolve_api_key(
            self.api_key
        )

        self.model = resolve_model(
            self.model
        )


# ============================================================
# TEXT RESPONSE
# ============================================================

@dataclass
class GroqResponse:

    text: str = ""

    model: str = ""

    success: bool = False

    error: Optional[str] = None

    usage: Dict[str, Any] = field(
        default_factory=dict
    )

    raw_response: Any = None

    attempts: int = 0


# ============================================================
# STRUCTURED RESPONSE
# ============================================================

@dataclass
class StructuredResponse:

    data: Dict[str, Any] = field(
        default_factory=dict
    )

    raw_text: str = ""

    success: bool = False

    error: Optional[str] = None

    response: Optional[
        GroqResponse
    ] = None


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/8
#
# UTILITIES + JSON PARSING
# ============================================================


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(
    value: Any,
) -> str:

    if value is None:

        return ""

    return str(
        value
    ).strip()


# ============================================================
# TRUNCATE TEXT
# ============================================================

def truncate_text(
    text: Any,
    max_chars: int = 30000,
) -> str:

    text = clean_text(
        text
    )

    if len(text) <= max_chars:

        return text

    return (

        text[:max_chars]

        +

        "\n\n[CONTENT TRUNCATED]"

    )


# ============================================================
# EXTRACT JSON FROM MODEL RESPONSE
# ============================================================

def extract_json(
    text: str,
) -> Optional[
    Union[
        Dict[str, Any],
        List[Any],
    ]
]:

    """
    Extract JSON from:

        1. Plain JSON
        2. ```json ... ```
        3. Embedded JSON object
        4. Embedded JSON array
    """

    text = clean_text(
        text
    )

    if not text:

        return None

    # --------------------------------------------------------
    # 1. Direct JSON
    # --------------------------------------------------------

    try:

        return json.loads(
            text
        )

    except json.JSONDecodeError:

        pass

    # --------------------------------------------------------
    # 2. Markdown JSON block
    # --------------------------------------------------------

    match = re.search(

        r"```(?:json)?\s*(.*?)\s*```",

        text,

        flags=re.IGNORECASE
        |
        re.DOTALL,

    )

    if match:

        candidate = match.group(
            1
        ).strip()

        try:

            return json.loads(
                candidate
            )

        except json.JSONDecodeError:

            pass

    # --------------------------------------------------------
    # 3. JSON object
    # --------------------------------------------------------

    object_start = text.find(
        "{"
    )

    object_end = text.rfind(
        "}"
    )

    if (
        object_start >= 0
        and
        object_end > object_start
    ):

        candidate = text[
            object_start:
            object_end + 1
        ]

        try:

            return json.loads(
                candidate
            )

        except json.JSONDecodeError:

            pass

    # --------------------------------------------------------
    # 4. JSON array
    # --------------------------------------------------------

    array_start = text.find(
        "["
    )

    array_end = text.rfind(
        "]"
    )

    if (
        array_start >= 0
        and
        array_end > array_start
    ):

        candidate = text[
            array_start:
            array_end + 1
        ]

        try:

            return json.loads(
                candidate
            )

        except json.JSONDecodeError:

            pass

    return None


# ============================================================
# BUILD USER PROMPT
# ============================================================

def build_user_prompt(
    prompt: str,
    context: Optional[str] = None,
    schema: Optional[
        Mapping[str, Any]
    ] = None,
) -> str:

    parts = []

    prompt = clean_text(
        prompt
    )

    if prompt:

        parts.append(
            prompt
        )

    if context:

        parts.append(

            "RELEVANT CONTEXT\n"
            "================\n"
            +
            truncate_text(
                context
            )

        )

    if schema:

        schema_json = json.dumps(

            schema,

            indent=2,

            ensure_ascii=False,

        )

        parts.append(

            "REQUIRED JSON STRUCTURE\n"
            "=======================\n"
            +
            schema_json
            +
            "\n\n"
            "Return ONLY valid JSON. "
            "Do not use Markdown fences."

        )

    return "\n\n".join(
        parts
    )


# ============================================================
# BUILD MESSAGES
# ============================================================

def build_messages(
    prompt: str,
    system_prompt: str,
    context: Optional[str] = None,
    schema: Optional[
        Mapping[str, Any]
    ] = None,
) -> List[
    Dict[str, str]
]:

    user_prompt = build_user_prompt(

        prompt=prompt,

        context=context,

        schema=schema,

    )

    return [

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
                user_prompt,

        },

    ]


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/8
#
# GROQ SERVICE
# ============================================================


class GroqService:

    """
    Centralized Groq service.

    IMPORTANT:
        There is intentionally ONE GroqService class
        in this file.
    """

    def __init__(
        self,
        config: Optional[
            GroqConfig
        ] = None,
        client: Any = None,
    ) -> None:

        if Groq is None:

            raise ImportError(

                "Groq package is not installed. "
                "Run: pip install groq"

            )

        self.config = (

            config
            or
            GroqConfig()

        )

        if not self.config.api_key:

            raise ValueError(

                "GROQ_API_KEY is not configured. "

                "For Streamlit, add it to "
                ".streamlit/secrets.toml"

            )

        self.client = (

            client

            if client is not None

            else

            Groq(

                api_key=self.config.api_key

            )

        )

        logger.info(

            "GroqService initialized. "
            "Model=%s",

            self.config.model,

        )

    # ========================================================
    # REQUEST
    # ========================================================

    def _request(
        self,
        messages: Sequence[
            Mapping[str, str]
        ],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
    ) -> Any:

        return (

            self.client.chat.completions.create(

                model=self.config.model,

                messages=list(
                    messages
                ),

                temperature=(

                    self.config.temperature

                    if temperature is None

                    else temperature

                ),

                max_tokens=(

                    self.config.max_tokens

                    if max_tokens is None

                    else max_tokens

                ),

                top_p=(

                    self.config.top_p

                    if top_p is None

                    else top_p

                ),

            )

        )

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
    ) -> GroqResponse:

        messages = build_messages(

            prompt=prompt,

            system_prompt=(

                system_prompt

                or

                self.config.system_prompt

            ),

            context=context,

        )

        last_error = None

        for attempt in range(

            1,

            self.config.max_retries + 1,

        ):

            try:

                logger.info(

                    "Groq request attempt "
                    "%s/%s",

                    attempt,

                    self.config.max_retries,

                )

                response = self._request(

                    messages=messages,

                    temperature=temperature,

                    max_tokens=max_tokens,

                    top_p=top_p,

                )

                text = ""

                if response.choices:

                    text = (

                        response
                        .choices[0]
                        .message
                        .content

                        or
                        ""

                    )

                usage = {}

                if getattr(
                    response,
                    "usage",
                    None,
                ):

                    usage = {

                        "prompt_tokens":
                            getattr(
                                response.usage,
                                "prompt_tokens",
                                None,
                            ),

                        "completion_tokens":
                            getattr(
                                response.usage,
                                "completion_tokens",
                                None,
                            ),

                        "total_tokens":
                            getattr(
                                response.usage,
                                "total_tokens",
                                None,
                            ),

                    }

                return GroqResponse(

                    text=clean_text(
                        text
                    ),

                    model=self.config.model,

                    success=True,

                    usage=usage,

                    raw_response=response,

                    attempts=attempt,

                )

            except Exception as exc:

                last_error = str(
                    exc
                )

                logger.warning(

                    "Groq request failed: %s",

                    exc,

                )

                if attempt < (
                    self.config.max_retries
                ):

                    delay = min(

                        2 ** (
                            attempt - 1
                        ),

                        8,

                    )

                    time.sleep(
                        delay
                    )

        return GroqResponse(

            model=self.config.model,

            success=False,

            error=last_error,

            attempts=self.config.max_retries,

        )

    # ========================================================
    # COMPLETE
    # ========================================================

    def complete(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> str:

        response = self.generate(

            prompt=prompt,

            context=context,

            **kwargs,

        )

        if not response.success:

            raise RuntimeError(

                response.error
                or
                "Groq generation failed."

            )

        return response.text

    # ========================================================
    # STRUCTURED GENERATION
    # ========================================================

    def generate_structured(
        self,
        prompt: str,
        schema: Mapping[str, Any],
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = 0.1,
        max_tokens: Optional[int] = None,
    ) -> StructuredResponse:

        messages = build_messages(

            prompt=prompt,

            system_prompt=(

                system_prompt

                or

                (
                    self.config.system_prompt
                    +
                    "\n\n"
                    "You MUST return valid JSON only."
                )

            ),

            context=context,

            schema=schema,

        )

        last_error = None

        for attempt in range(

            1,

            self.config.max_retries + 1,

        ):

            response = self.generate(

                prompt=build_user_prompt(

                    prompt=prompt,

                    context=context,

                    schema=schema,

                ),

                system_prompt=(

                    system_prompt

                    or

                    (
                        self.config.system_prompt
                        +
                        "\n\n"
                        "Return valid JSON only."
                    )

                ),

                temperature=temperature,

                max_tokens=max_tokens,

            )

            if not response.success:

                last_error = response.error

                continue

            data = extract_json(
                response.text
            )

            if data is not None:

                if isinstance(
                    data,
                    list,
                ):

                    data = {

                        "items":
                            data

                    }

                return StructuredResponse(

                    data=data,

                    raw_text=response.text,

                    success=True,

                    response=response,

                )

            last_error = (

                "Model returned text that "
                "could not be parsed as JSON."

            )

            logger.warning(

                "Invalid JSON returned by Groq "
                "on structured attempt %s",

                attempt,

            )

        return StructuredResponse(

            data={},

            raw_text=(

                response.text
                if "response" in locals()
                else ""

            ),

            success=False,

            error=last_error,

            response=(

                response
                if "response" in locals()
                else None

            ),

        )


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/8
#
# CURRICULUM + INDUSTRY ANALYSIS
# ============================================================


# ============================================================
# CURRICULUM ANALYSIS SCHEMA
# ============================================================

CURRICULUM_SCHEMA = {

    "summary":
        "string",

    "modules": [],

    "topics": [],

    "skills": [],

    "tools": [],

    "technologies": [],

    "projects": [],

    "strengths": [],

    "weaknesses": [],

    "missing_areas": [],

}


# ============================================================
# ANALYZE CURRICULUM
# ============================================================

def analyze_curriculum(
    service: GroqService,
    curriculum_text: str,
) -> StructuredResponse:

    prompt = """

Analyze the supplied curriculum.

Identify:

1. Curriculum summary
2. Modules
3. Topics
4. Technical skills
5. Tools
6. Technologies
7. Projects
8. Strengths
9. Weaknesses
10. Missing areas

Evaluate:

- technical depth
- practical orientation
- industry relevance
- AI readiness
- GenAI readiness
- deployment readiness
- project readiness

Only use information supported by the supplied
curriculum.

Return valid JSON.

"""

    return service.generate_structured(

        prompt=prompt,

        schema=CURRICULUM_SCHEMA,

        context=curriculum_text,

    )


# ============================================================
# SKILL EXTRACTION SCHEMA
# ============================================================

SKILL_SCHEMA = {

    "skills": [],

    "tools": [],

    "frameworks": [],

    "technologies": [],

    "platforms": [],

    "databases": [],

}


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(
    service: GroqService,
    text: str,
) -> StructuredResponse:

    prompt = """

Extract all technical skills from the supplied text.

Categorize into:

- programming
- data science
- machine learning
- deep learning
- NLP
- Generative AI
- Agentic AI
- cloud
- DevOps
- MLOps
- databases
- frameworks
- tools
- platforms

Do not invent skills.

Return JSON.

"""

    return service.generate_structured(

        prompt=prompt,

        schema=SKILL_SCHEMA,

        context=text,

    )


# ============================================================
# INDUSTRY SCHEMA
# ============================================================

INDUSTRY_SCHEMA = {

    "required_skills": [],

    "tools": [],

    "technologies": [],

    "frameworks": [],

    "cloud_platforms": [],

    "databases": [],

    "job_roles": [],

    "experience_expectations": [],

}


# ============================================================
# ANALYZE INDUSTRY
# ============================================================

def analyze_industry(
    service: GroqService,
    job_description: str,
) -> StructuredResponse:

    prompt = """

Analyze the supplied Job Description.

Extract:

- required technical skills
- tools
- technologies
- frameworks
- cloud platforms
- databases
- job roles
- experience expectations

Separate explicit requirements from inferred
requirements.

Only include evidence-supported information.

Return JSON.

"""

    return service.generate_structured(

        prompt=prompt,

        schema=INDUSTRY_SCHEMA,

        context=job_description,

    )


# ============================================================
# INDUSTRY ALIGNMENT
# ============================================================

ALIGNMENT_SCHEMA = {

    "overall_alignment_score":
        0,

    "matching_skills": [],

    "partially_matching_skills": [],

    "missing_skills": [],

    "tools_required": [],

    "experience_expectations": [],

    "recommendations": [],

}


def analyze_industry_alignment(
    service: GroqService,
    curriculum: str,
    industry: str,
) -> StructuredResponse:

    prompt = """

Compare the curriculum against the industry
requirements.

Identify:

- matching skills
- partially matching skills
- missing skills
- missing tools
- experience gaps
- industry alignment score

Score alignment from 0 to 1.

Return JSON.

"""

    context = (

        "CURRICULUM\n"
        "==========\n"
        +
        curriculum

        +

        "\n\nINDUSTRY REQUIREMENTS\n"
        "=====================\n"
        +
        industry

    )

    return service.generate_structured(

        prompt=prompt,

        schema=ALIGNMENT_SCHEMA,

        context=context,

    )


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/8
#
# GAP + ENHANCEMENT INTELLIGENCE
# ============================================================


# ============================================================
# GAP SCHEMA
# ============================================================

GAP_SCHEMA = {

    "overall_gap_score":
        0,

    "matching_skills": [],

    "critical_gaps": [],

    "moderate_gaps": [],

    "minor_gaps": [],

    "missing_tools": [],

    "missing_projects": [],

    "missing_concepts": [],

}


# ============================================================
# GAP ANALYSIS
# ============================================================

def analyze_gaps(
    service: GroqService,
    curriculum: str,
    industry: str,
    rag_context: Optional[str] = None,
) -> StructuredResponse:

    prompt = """

Perform curriculum-to-industry skill gap analysis.

Identify:

1. Matching skills
2. Critical gaps
3. Moderate gaps
4. Minor gaps
5. Missing tools
6. Missing projects
7. Missing concepts

Use:

- curriculum evidence
- industry requirements
- retrieved RAG evidence when supplied

Score overall gap from 0 to 1 where:

0 = no meaningful gap
1 = maximum gap

Do not hallucinate requirements.

Return JSON.

"""

    context = (

        "CURRICULUM\n"
        "==========\n"
        +
        curriculum

        +

        "\n\nINDUSTRY\n"
        "========\n"
        +
        industry

    )

    if rag_context:

        context += (

            "\n\nRAG EVIDENCE\n"
            "============\n"
            +
            rag_context

        )

    return service.generate_structured(

        prompt=prompt,

        schema=GAP_SCHEMA,

        context=context,

    )


# ============================================================
# ENHANCEMENT SCHEMA
# ============================================================

ENHANCEMENT_SCHEMA = {

    "recommendations": [

        {

            "area":
                "string",

            "skill":
                "string",

            "reason":
                "string",

            "priority":
                "High",

            "recommended_change":
                "string",

            "implementation":
                "string",

            "estimated_hours":
                0,

        }

    ],

    "new_modules": [],

    "new_projects": [],

}


# ============================================================
# ENHANCEMENT GENERATION
# ============================================================

def generate_enhancements(
    service: GroqService,
    curriculum: str,
    gap_analysis: str,
    industry: Optional[str] = None,
    rag_context: Optional[str] = None,
) -> StructuredResponse:

    prompt = """

Design curriculum enhancements based on the
identified industry and skill gaps.

Prioritize:

- employability
- practical skills
- GenAI
- Agentic AI
- RAG
- LLMOps
- MLOps
- cloud
- deployment
- production engineering
- portfolio projects

For every recommendation provide:

- area
- skill
- reason
- priority
- recommended change
- implementation
- estimated hours

Also recommend new modules and projects.

Return JSON.

"""

    context = (

        "CURRICULUM\n"
        "==========\n"
        +
        curriculum

        +

        "\n\nGAP ANALYSIS\n"
        "============\n"
        +
        gap_analysis

    )

    if industry:

        context += (

            "\n\nINDUSTRY\n"
            "========\n"
            +
            industry

        )

    if rag_context:

        context += (

            "\n\nRAG EVIDENCE\n"
            "============\n"
            +
            rag_context

        )

    return service.generate_structured(

        prompt=prompt,

        schema=ENHANCEMENT_SCHEMA,

        context=context,

    )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/8
#
# LEARNING PATH + REPORT + HEALTH
# ============================================================


# ============================================================
# LEARNING PATH SCHEMA
# ============================================================

LEARNING_PATH_SCHEMA = {

    "learning_path": [

        {

            "sequence":
                1,

            "module":
                "string",

            "skills": [],

            "topics": [],

            "projects": [],

            "estimated_hours":
                0,

            "prerequisites": [],

        }

    ],

    "capstone_project":
        "",

    "career_outcomes": [],

}


# ============================================================
# LEARNING PATH
# ============================================================

def generate_learning_path(
    service: GroqService,
    current_skills: str,
    skill_gaps: str,
    target_role: str,
    duration_weeks: int = 12,
) -> StructuredResponse:

    prompt = f"""

Create a practical {duration_weeks}-week learning path
for the following target role:

{target_role}

The learner's current skills and skill gaps are supplied
in the context.

Create a sequential path containing:

- modules
- skills
- topics
- hands-on projects
- estimated hours
- prerequisites
- capstone project
- career outcomes

Move from foundational gaps toward production-ready
skills.

Return JSON.

"""

    context = (

        "CURRENT SKILLS\n"
        "==============\n"
        +
        current_skills

        +

        "\n\nSKILL GAPS\n"
        "==========\n"
        +
        skill_gaps

    )

    return service.generate_structured(

        prompt=prompt,

        schema=LEARNING_PATH_SCHEMA,

        context=context,

    )


# ============================================================
# EXECUTIVE REPORT SCHEMA
# ============================================================

EXECUTIVE_REPORT_SCHEMA = {

    "executive_summary":
        "string",

    "overall_score":
        0,

    "key_strengths": [],

    "critical_gaps": [],

    "industry_readiness":
        "string",

    "priority_actions": [],

    "recommended_modules": [],

    "recommended_projects": [],

    "conclusion":
        "string",

}


# ============================================================
# EXECUTIVE REPORT
# ============================================================

def generate_executive_report(
    service: GroqService,
    curriculum: str,
    industry: str,
    gaps: str,
    enhancements: str,
    rag_context: Optional[str] = None,
) -> StructuredResponse:

    prompt = """

Prepare an executive-level curriculum intelligence report.

Evaluate:

1. Curriculum quality
2. Industry alignment
3. Skill gaps
4. Employability readiness
5. Recommended improvements
6. Recommended modules
7. Recommended projects

Write for:

- academic leadership
- curriculum committees
- training organizations
- industry advisory boards

Be concise, evidence-driven and actionable.

Return JSON.

"""

    context = (

        "CURRICULUM\n"
        "==========\n"
        +
        curriculum

        +

        "\n\nINDUSTRY\n"
        "========\n"
        +
        industry

        +

        "\n\nGAPS\n"
        "====\n"
        +
        gaps

        +

        "\n\nENHANCEMENTS\n"
        "============\n"
        +
        enhancements

    )

    if rag_context:

        context += (

            "\n\nRAG EVIDENCE\n"
            "============\n"
            +
            rag_context

        )

    return service.generate_structured(

        prompt=prompt,

        schema=EXECUTIVE_REPORT_SCHEMA,

        context=context,

        temperature=0.15,

    )


# ============================================================
# HEALTH CHECK
# ============================================================

def health_check(
    service: Optional[
        GroqService
    ] = None,
) -> Dict[str, Any]:

    result = {

        "service":
            "Groq",

        "version":
            GROQ_SERVICE_VERSION,

        "groq_package_installed":
            Groq is not None,

        "api_key_configured":
            bool(
                resolve_api_key()
            ),

        "model":
            resolve_model(),

        "success":
            False,

        "error":
            None,

    }

    if Groq is None:

        result["error"] = (
            "groq package is not installed."
        )

        return result

    if not result[
        "api_key_configured"
    ]:

        result["error"] = (
            "GROQ_API_KEY is not configured."
        )

        return result

    try:

        service = (

            service

            or

            GroqService()

        )

        response = service.generate(

            prompt=(
                "Respond with exactly "
                "one word: OK"
            ),

            temperature=0.0,

            max_tokens=10,

        )

        result["success"] = (
            response.success
        )

        result["response"] = (
            response.text
        )

        result["error"] = (
            response.error
        )

    except Exception as exc:

        result["error"] = str(
            exc
        )

    return result


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/8
#
# CONVENIENCE FUNCTIONS + EXPORTS + SELF TEST
# ============================================================


# ============================================================
# CACHED SERVICE
# ============================================================

_default_service: Optional[
    GroqService
] = None


def get_groq_service(
    config: Optional[
        GroqConfig
    ] = None,
) -> GroqService:

    """
    Return a reusable GroqService.

    In Streamlit, app.py can additionally cache the
    service using st.cache_resource.
    """

    global _default_service

    if config is not None:

        return GroqService(
            config=config
        )

    if _default_service is None:

        _default_service = GroqService()

    return _default_service


# ============================================================
# SIMPLE GENERATE
# ============================================================

def generate(
    prompt: str,
    context: Optional[str] = None,
    **kwargs: Any,
) -> GroqResponse:

    service = get_groq_service()

    return service.generate(

        prompt=prompt,

        context=context,

        **kwargs,

    )


# ============================================================
# SIMPLE COMPLETE
# ============================================================

def complete(
    prompt: str,
    context: Optional[str] = None,
    **kwargs: Any,
) -> str:

    response = generate(

        prompt=prompt,

        context=context,

        **kwargs,

    )

    if not response.success:

        raise RuntimeError(

            response.error
            or
            "Groq request failed."

        )

    return response.text


# ============================================================
# SERVICE SUMMARY
# ============================================================

def service_summary(
    service: Optional[
        GroqService
    ] = None,
) -> Dict[str, Any]:

    service = (

        service
        or
        get_groq_service()

    )

    return {

        "version":
            GROQ_SERVICE_VERSION,

        "model":
            service.config.model,

        "temperature":
            service.config.temperature,

        "max_tokens":
            service.config.max_tokens,

        "max_retries":
            service.config.max_retries,

        "top_p":
            service.config.top_p,

        "api_key_configured":
            bool(
                service.config.api_key
            ),

    }


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [

    # Constants
    "GROQ_SERVICE_VERSION",

    "DEFAULT_MODEL",

    # Configuration
    "GroqConfig",

    # Responses
    "GroqResponse",

    "StructuredResponse",

    # Utilities
    "get_streamlit_secret",

    "resolve_api_key",

    "resolve_model",

    "clean_text",

    "truncate_text",

    "extract_json",

    "build_user_prompt",

    "build_messages",

    # Main service
    "GroqService",

    # Analysis
    "analyze_curriculum",

    "extract_skills",

    "analyze_industry",

    "analyze_industry_alignment",

    "analyze_gaps",

    "generate_enhancements",

    "generate_learning_path",

    "generate_executive_report",

    # Convenience
    "get_groq_service",

    "generate",

    "complete",

    # Diagnostics
    "health_check",

    "service_summary",

]


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "=" * 60
    )

    print(
        "PRAGYANAI GROQ SERVICE"
    )

    print(
        "=" * 60
    )

    print()

    print(
        "Version:",
        GROQ_SERVICE_VERSION,
    )

    print(
        "Groq installed:",
        Groq is not None,
    )

    print(
        "API key configured:",
        bool(
            resolve_api_key()
        ),
    )

    print(
        "Model:",
        resolve_model(),
    )

    print()

    # --------------------------------------------------------
    # Only execute API call when explicitly requested.
    # --------------------------------------------------------

    run_test = (

        os.getenv(
            "PRAGYANAI_GROQ_TEST"
        )
        ==
        "1"

    )

    if not run_test:

        print(
            "Live API test skipped."
        )

        print(
            "Set:"
        )

        print(
            "PRAGYANAI_GROQ_TEST=1"
        )

        print(
            "to execute a live API test."
        )

    else:

        print(
            "Running live API test..."
        )

        try:

            service = GroqService()

            response = service.generate(

                prompt=(
                    "Respond with exactly "
                    "'PragyanAI Groq OK'."
                ),

                temperature=0.0,

                max_tokens=20,

            )

            print()

            print(
                "Success:",
                response.success,
            )

            print(
                "Response:",
                response.text,
            )

            print(
                "Usage:",
                response.usage,
            )

            print(
                "Attempts:",
                response.attempts,
            )

        except Exception as exc:

            print(
                "ERROR:",
                exc,
            )

    print()
    print(
        "=" * 60
    )
    print(
        "TEST COMPLETE"
    )
    print(
        "=" * 60
    )


# ============================================================
# END OF llm/groq.py
# ============================================================
