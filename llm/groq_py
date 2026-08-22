# ============================================================
# llm/groq.py
# CHUNK 1/10
#
# PRAGYANAI GROQ / LLAMA LLM SERVICE
#
# Responsibilities:
#   - Groq API integration
#   - Llama model execution
#   - Structured JSON generation
#   - Text generation
#   - Prompt management
#   - Retry handling
#   - Error handling
#   - Token / temperature configuration
#   - Curriculum analysis
#   - Industry analysis
#   - Gap analysis
#   - Enhancement recommendations
#
# Installation:
#
#   pip install groq
#
# Environment:
#
#   GROQ_API_KEY=your_api_key
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

logger = logging.getLogger(__name__)


# ============================================================
# VERSION
# ============================================================

GROQ_SERVICE_VERSION = "1.0.0"


# ============================================================
# DEFAULT MODEL
# ============================================================

GROQ_MODEL = "llama-3.3-70b-versatile"

# ============================================================
# DEFAULT PARAMETERS
# ============================================================

DEFAULT_TEMPERATURE = 0.2

DEFAULT_MAX_TOKENS = 4096

DEFAULT_TIMEOUT = 120

DEFAULT_MAX_RETRIES = 3


# ============================================================
# OPTIONAL GROQ IMPORT
# ============================================================

try:

    from groq import Groq

except ImportError:

    Groq = None


# ============================================================
# LLM CONFIGURATION
# ============================================================

@dataclass
class GroqConfig:

    api_key: Optional[str] = None

    model: str = field(
        default_factory=resolve_model
    )

    temperature: float = 0.2

    max_tokens: int = 4096

    timeout: int = 120

    max_retries: int = 3

    top_p: float = 1.0

    stream: bool = False

    system_prompt: str = (
        "You are a senior AI curriculum "
        "and industry intelligence expert."
    )

# ============================================================
# LLM RESPONSE
# ============================================================

@dataclass
class GroqResponse:

    text: str = ""

    model: str = ""

    success: bool = True

    error: Optional[str] = None

    usage: Dict[str, Any] = field(
        default_factory=dict
    )

    raw_response: Any = None

    attempts: int = 1


# ============================================================
# STRUCTURED RESPONSE
# ============================================================

@dataclass
class StructuredResponse:

    data: Dict[str, Any] = field(
        default_factory=dict
    )

    raw_text: str = ""

    success: bool = True

    error: Optional[str] = None

    response: Optional[
        GroqResponse
    ] = None


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# API KEY + CLIENT
# ============================================================


# ============================================================
# API KEY RESOLUTION
# ============================================================

def resolve_api_key(
    explicit_key: Optional[str] = None,
) -> Optional[str]:

    # 1. Explicit key has highest priority
    if explicit_key:
        return explicit_key

    # 2. Streamlit Secrets
    try:
        import streamlit as st

        key = st.secrets.get(
            "GROQ_API_KEY",
            None
        )

        if key:
            return str(key)

    except Exception:
        pass

    # 3. Optional fallback for non-Streamlit usage
    return os.getenv("GROQ_API_KEY")

def resolve_model() -> str:

    try:
        import streamlit as st

        model = st.secrets.get(
            "GROQ_MODEL",
            None
        )

        if model:
            return str(model)

    except Exception:
        pass

    return os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )
# ============================================================
# CHECK GROQ INSTALLATION
# ============================================================

def is_groq_installed() -> bool:

    return Groq is not None


# ============================================================
# REQUIRE GROQ
# ============================================================

def require_groq() -> None:

    if Groq is None:

        raise ImportError(

            "The groq package is not installed. "
            "Install it using: pip install groq"

        )


# ============================================================
# REQUIRE API KEY
# ============================================================

def require_api_key(
    api_key: Optional[str] = None,
) -> str:

    key = resolve_api_key(
        api_key
    )

    if not key:

        raise ValueError(

            "GROQ_API_KEY is not configured. "
            "Set it in the environment or pass api_key."

        )

    return key


# ============================================================
# CREATE CLIENT
# ============================================================

def create_groq_client(
    api_key: Optional[str] = None,
) -> Any:

    require_groq()

    key = require_api_key(
        api_key
    )

    return Groq(
        api_key=key
    )


# ============================================================
# GROQ SERVICE
# ============================================================

class GroqService:

    def __init__(
        self,
        config: Optional[
            GroqConfig
        ] = None,
        client: Any = None,
    ) -> None:

        self.config = (

            config
            or
            GroqConfig()

        )

        self.api_key = require_api_key(

            self.config.api_key

        )

        self.client = (

            client

            if client is not None

            else

            create_groq_client(

                self.api_key

            )

        )

        logger.info(

            "Groq service initialized with model: %s",

            self.config.model,

        )


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# PROMPTS + MESSAGE BUILDING
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
    text: str,
    max_chars: int = 20000,
) -> str:

    text = clean_text(
        text
    )

    if len(text) <= max_chars:

        return text

    return (

        text[
            :max_chars
        ]

        +

        "\n\n[CONTENT TRUNCATED]"

    )


# ============================================================
# BUILD SYSTEM MESSAGE
# ============================================================

def build_system_message(
    system_prompt: Optional[str] = None,
) -> str:

    return clean_text(

        system_prompt
        or
        GroqConfig().system_prompt

    )


# ============================================================
# BUILD USER PROMPT
# ============================================================

def build_user_prompt(
    prompt: str,
    context: Optional[str] = None,
    output_schema: Optional[
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

            "\n"
            "RELEVANT CONTEXT:\n"
            "-----------------\n"
            +
            truncate_text(
                context
            )

        )

    if output_schema:

        schema_text = json.dumps(

            output_schema,

            indent=2,

            ensure_ascii=False,

        )

        parts.append(

            "\n"
            "REQUIRED JSON STRUCTURE:\n"
            "------------------------\n"
            +
            schema_text
            +
            "\n\n"
            "Return valid JSON only."

        )

    return "\n\n".join(
        parts
    )


# ============================================================
# BUILD MESSAGES
# ============================================================

def build_messages(
    user_prompt: str,
    system_prompt: Optional[str] = None,
) -> List[Dict[str, str]]:

    system = build_system_message(
        system_prompt
    )

    return [

        {
            "role":
                "system",

            "content":
                system,

        },

        {
            "role":
                "user",

            "content":
                clean_text(
                    user_prompt
                ),

        },

    ]


# ============================================================
# PROMPT TEMPLATE
# ============================================================

def render_prompt(
    template: str,
    variables: Optional[
        Mapping[str, Any]
    ] = None,
) -> str:

    variables = (
        variables
        or
        {}
    )

    rendered = template

    for key, value in variables.items():

        placeholder = (
            "{"
            +
            str(key)
            +
            "}"
        )

        rendered = rendered.replace(

            placeholder,

            clean_text(
                value
            ),

        )

    return rendered


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# TEXT GENERATION
# ============================================================


class GroqService:

    def __init__(
        self,
        config: Optional[
            GroqConfig
        ] = None,
        client: Any = None,
    ) -> None:

        self.config = (

            config
            or
            GroqConfig()

        )

        self.api_key = require_api_key(

            self.config.api_key

        )

        self.client = (

            client

            if client is not None

            else

            create_groq_client(

                self.api_key

            )

        )

    # --------------------------------------------------------
    # Build request
    # --------------------------------------------------------

    def _build_request(
        self,
        messages: Sequence[
            Mapping[str, str]
        ],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
    ) -> Dict[str, Any]:

        request = {

            "model":
                self.config.model,

            "messages":
                list(
                    messages
                ),

            "temperature": (

                temperature
                if temperature is not None
                else
                self.config.temperature

            ),

            "max_tokens": (

                max_tokens
                if max_tokens is not None
                else
                self.config.max_tokens

            ),

            "top_p": (

                top_p
                if top_p is not None
                else
                self.config.top_p

            ),

        }

        return request

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
    ) -> GroqResponse:

        user_prompt = build_user_prompt(

            prompt=prompt,

            context=context,

        )

        messages = build_messages(

            user_prompt=user_prompt,

            system_prompt=(

                system_prompt
                or
                self.config.system_prompt

            ),

        )

        request = self._build_request(

            messages=messages,

            temperature=temperature,

            max_tokens=max_tokens,

            top_p=top_p,

        )

        last_error = None

        attempts = 0

        for attempt in range(

            1,

            self.config.max_retries + 1,

        ):

            attempts = attempt

            try:

                logger.debug(

                    "Groq request attempt %s/%s",

                    attempt,

                    self.config.max_retries,

                )

                response = (

                    self.client.chat.completions.create(

                        **request

                    )

                )

                text = (

                    response.choices[0]
                    .message
                    .content

                    if response.choices

                    else ""

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

                    attempts=attempts,

                )

            except Exception as exc:

                last_error = str(
                    exc
                )

                logger.warning(

                    "Groq request failed on "
                    "attempt %s: %s",

                    attempt,

                    exc,

                )

                if attempt < self.config.max_retries:

                    delay = (
                        2
                        **
                        (
                            attempt - 1
                        )
                    )

                    time.sleep(
                        delay
                    )

        return GroqResponse(

            text="",

            model=self.config.model,

            success=False,

            error=last_error,

            attempts=attempts,

        )

    # --------------------------------------------------------
    # Simple completion
    # --------------------------------------------------------

    def complete(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:

        response = self.generate(

            prompt=prompt,

            **kwargs,

        )

        if not response.success:

            raise RuntimeError(

                response.error
                or
                "Groq generation failed."

            )

        return response.text


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# STRUCTURED JSON GENERATION
# ============================================================


# ============================================================
# EXTRACT JSON
# ============================================================

def extract_json(
    text: str,
) -> Optional[
    Union[
        Dict[str, Any],
        List[Any],
    ]
]:

    text = clean_text(
        text
    )

    if not text:

        return None

    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:

        return json.loads(
            text
        )

    except json.JSONDecodeError:

        pass

    # --------------------------------------------------------
    # Markdown code block
    # --------------------------------------------------------

    fenced = re.search(

        r"```(?:json)?\s*(.*?)\s*```",

        text,

        flags=re.DOTALL
        |
        re.IGNORECASE,

    )

    if fenced:

        candidate = fenced.group(
            1
        ).strip()

        try:

            return json.loads(
                candidate
            )

        except json.JSONDecodeError:

            pass

    # --------------------------------------------------------
    # Find first JSON object
    # --------------------------------------------------------

    start_object = text.find(
        "{"
    )

    end_object = text.rfind(
        "}"
    )

    if (
        start_object >= 0
        and
        end_object > start_object
    ):

        candidate = text[
            start_object:
            end_object + 1
        ]

        try:

            return json.loads(
                candidate
            )

        except json.JSONDecodeError:

            pass

    # --------------------------------------------------------
    # Find JSON array
    # --------------------------------------------------------

    start_array = text.find(
        "["
    )

    end_array = text.rfind(
        "]"
    )

    if (
        start_array >= 0
        and
        end_array > start_array
    ):

        candidate = text[
            start_array:
            end_array + 1
        ]

        try:

            return json.loads(
                candidate
            )

        except json.JSONDecodeError:

            pass

    return None


# ============================================================
# VALIDATE JSON OBJECT
# ============================================================

def validate_json_object(
    data: Any,
) -> Dict[str, Any]:

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(

            "Expected JSON object but received "
            f"{type(data).__name__}."

        )

    return data


# ============================================================
# STRUCTURED GENERATION
# ============================================================

class GroqService:

    # Existing methods are continued here.

    def generate_structured(
        self,
        prompt: str,
        schema: Mapping[str, Any],
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = 0.1,
        max_tokens: Optional[int] = None,
    ) -> StructuredResponse:

        schema_prompt = build_user_prompt(

            prompt=prompt,

            context=context,

            output_schema=schema,

        )

        response = self.generate(

            prompt=schema_prompt,

            system_prompt=(

                system_prompt
                or
                (
                    self.config.system_prompt
                    +
                    "\n\n"
                    "You must return ONLY valid JSON. "
                    "Do not include markdown fences."
                )

            ),

            temperature=temperature,

            max_tokens=max_tokens,

        )

        if not response.success:

            return StructuredResponse(

                data={},

                raw_text=response.text,

                success=False,

                error=response.error,

                response=response,

            )

        data = extract_json(
            response.text
        )

        if data is None:

            return StructuredResponse(

                data={},

                raw_text=response.text,

                success=False,

                error=(
                    "The model response could not "
                    "be parsed as valid JSON."
                ),

                response=response,

            )

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

    # --------------------------------------------------------
    # JSON completion
    # --------------------------------------------------------

    def json(
        self,
        prompt: str,
        schema: Optional[
            Mapping[str, Any]
        ] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:

        if schema is None:

            schema = {

                "result":
                    "string"

            }

        result = self.generate_structured(

            prompt=prompt,

            schema=schema,

            context=context,

        )

        if not result.success:

            raise RuntimeError(

                result.error
                or
                "Structured generation failed."

            )

        return result.data


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# CURRICULUM ANALYSIS
# ============================================================


# ============================================================
# CURRICULUM SCHEMA
# ============================================================

CURRICULUM_ANALYSIS_SCHEMA = {

    "summary":
        "string",

    "strengths": [
        "string"
    ],

    "weaknesses": [
        "string"
    ],

    "technologies": [
        "string"
    ],

    "skills": [
        "string"
    ],

    "topics": [
        "string"
    ],

    "projects": [
        "string"
    ],

    "missing_areas": [
        "string"
    ],

    "recommendations": [
        "string"
    ],

}


# ============================================================
# CURRICULUM ANALYSIS
# ============================================================

def analyze_curriculum(
    service: GroqService,
    curriculum_text: str,
) -> StructuredResponse:

    prompt = """
Analyze the following technical curriculum.

Evaluate:

1. Overall curriculum quality
2. Technical depth
3. Industry relevance
4. AI / ML / GenAI coverage
5. Programming coverage
6. Project orientation
7. Deployment readiness
8. Missing skills
9. Emerging technology gaps
10. Recommendations for improvement

Do not invent technologies that are not supported
by the provided curriculum.

Return structured JSON.
"""

    return service.generate_structured(

        prompt=prompt,

        schema=CURRICULUM_ANALYSIS_SCHEMA,

        context=curriculum_text,

    )


# ============================================================
# INDUSTRY ALIGNMENT SCHEMA
# ============================================================

INDUSTRY_ALIGNMENT_SCHEMA = {

    "overall_alignment_score":
        0,

    "matching_skills": [
        "string"
    ],

    "missing_skills": [
        "string"
    ],

    "partially_matching_skills": [
        "string"
    ],

    "tools_required": [
        "string"
    ],

    "experience_expectations": [
        "string"
    ],

    "recommendations": [
        "string"
    ],

}


# ============================================================
# INDUSTRY ALIGNMENT
# ============================================================

def analyze_industry_alignment(
    service: GroqService,
    curriculum_text: str,
    job_description: str,
) -> StructuredResponse:

    prompt = """
Compare the curriculum against the industry job
description.

Determine:

- Skills explicitly required by the JD
- Skills covered by the curriculum
- Skills partially covered
- Skills missing
- Tools and platforms missing
- Project or experience gaps
- Overall industry alignment

Use evidence from the supplied curriculum and JD.

Return structured JSON.
"""

    context = (

        "CURRICULUM:\n"
        +
        curriculum_text
        +
        "\n\n"
        "JOB DESCRIPTION:\n"
        +
        job_description

    )

    return service.generate_structured(

        prompt=prompt,

        schema=INDUSTRY_ALIGNMENT_SCHEMA,

        context=context,

    )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# GAP ANALYSIS
# ============================================================


# ============================================================
# GAP ANALYSIS SCHEMA
# ============================================================

GAP_ANALYSIS_SCHEMA = {

    "overall_gap_score":
        0,

    "critical_gaps": [

        {

            "skill":
                "string",

            "category":
                "string",

            "severity":
                "High",

            "reason":
                "string",

            "evidence":
                "string",

        }

    ],

    "moderate_gaps": [

        {

            "skill":
                "string",

            "category":
                "string",

            "severity":
                "Medium",

            "reason":
                "string",

            "evidence":
                "string",

        }

    ],

    "minor_gaps": [

        {

            "skill":
                "string",

            "category":
                "string",

            "severity":
                "Low",

            "reason":
                "string",

            "evidence":
                "string",

        }

    ],

    "missing_tools": [
        "string"
    ],

    "missing_projects": [
        "string"
    ],

    "missing_concepts": [
        "string"
    ],

}


# ============================================================
# GAP ANALYSIS
# ============================================================

def analyze_gaps(
    service: GroqService,
    curriculum_text: str,
    industry_text: str,
    rag_context: Optional[str] = None,
) -> StructuredResponse:

    prompt = """
Perform a detailed curriculum-to-industry gap analysis.

Identify:

1. Critical technical skill gaps
2. Moderate skill gaps
3. Minor gaps
4. Missing concepts
5. Missing tools
6. Missing platforms
7. Missing project experience
8. Deployment gaps
9. Industry readiness gaps

Rank gaps by severity.

Only identify gaps supported by the supplied evidence.
Do not hallucinate requirements.

Return structured JSON.
"""

    context_parts = [

        "CURRICULUM:\n"
        +
        curriculum_text,

        "\nINDUSTRY REQUIREMENTS:\n"
        +
        industry_text,

    ]

    if rag_context:

        context_parts.append(

            "\nRETRIEVED RAG EVIDENCE:\n"
            +
            rag_context

        )

    return service.generate_structured(

        prompt=prompt,

        schema=GAP_ANALYSIS_SCHEMA,

        context="\n".join(
            context_parts
        ),

    )


# ============================================================
# SKILL EXTRACTION SCHEMA
# ============================================================

SKILL_EXTRACTION_SCHEMA = {

    "skills": [

        {

            "name":
                "string",

            "category":
                "Programming",

            "level":
                "Beginner",

            "evidence":
                "string",

        }

    ],

    "tools": [
        "string"
    ],

    "platforms": [
        "string"
    ],

    "frameworks": [
        "string"
    ],

    "databases": [
        "string"
    ],

}


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(
    service: GroqService,
    text: str,
) -> StructuredResponse:

    prompt = """
Extract technical skills from the supplied text.

Classify skills into:

- Programming
- Data Science
- Machine Learning
- Deep Learning
- NLP
- Generative AI
- Agentic AI
- Cloud
- DevOps
- MLOps
- Databases
- Data Engineering
- Visualization
- Software Engineering

Also identify tools, platforms, frameworks and databases.

Only extract skills supported by the text.
"""

    return service.generate_structured(

        prompt=prompt,

        schema=SKILL_EXTRACTION_SCHEMA,

        context=text,

    )


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# ENHANCEMENT ENGINE
# ============================================================


# ============================================================
# ENHANCEMENT SCHEMA
# ============================================================

ENHANCEMENT_SCHEMA = {

    "priority":
        "string",

    "recommendations": [

        {

            "area":
                "string",

            "skill":
                "string",

            "reason":
                "string",

            "current_state":
                "string",

            "recommended_change":
                "string",

            "implementation":
                "string",

            "priority":
                "High",

            "estimated_hours":
                0,

        }

    ],

    "new_modules": [

        {

            "module":
                "string",

            "topics": [
                "string"
            ],

            "projects": [
                "string"
            ],

        }

    ],

}


# ============================================================
# ENHANCEMENT RECOMMENDATIONS
# ============================================================

def generate_enhancements(
    service: GroqService,
    curriculum_text: str,
    gap_analysis: str,
    industry_context: Optional[str] = None,
    rag_context: Optional[str] = None,
) -> StructuredResponse:

    prompt = """
Design curriculum enhancements based on the identified
industry and skill gaps.

For every recommendation provide:

- Area
- Skill
- Reason
- Current state
- Recommended change
- Implementation approach
- Priority
- Estimated learning hours

Also propose completely new modules where appropriate.

Prioritize:

1. Industry employability
2. Practical projects
3. Modern AI skills
4. Agentic AI
5. GenAI
6. Cloud deployment
7. MLOps
8. Production engineering
9. Portfolio development

Do not recommend technologies without evidence or a clear
industry relevance.
"""

    context_parts = [

        "CURRICULUM:\n"
        +
        curriculum_text,

        "\nGAP ANALYSIS:\n"
        +
        gap_analysis,

    ]

    if industry_context:

        context_parts.append(

            "\nINDUSTRY CONTEXT:\n"
            +
            industry_context

        )

    if rag_context:

        context_parts.append(

            "\nRAG EVIDENCE:\n"
            +
            rag_context

        )

    return service.generate_structured(

        prompt=prompt,

        schema=ENHANCEMENT_SCHEMA,

        context="\n".join(
            context_parts
        ),

    )


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

            "skills":
                [],

            "topics":
                [],

            "projects":
                [],

            "estimated_hours":
                0,

            "prerequisites":
                [],

        }

    ],

    "capstone_project":
        "string",

    "career_outcomes":
        [],

}


# ============================================================
# GENERATE LEARNING PATH
# ============================================================

def generate_learning_path(
    service: GroqService,
    current_skills: str,
    target_role: str,
    skill_gaps: str,
    duration_weeks: int = 12,
) -> StructuredResponse:

    prompt = f"""
Create a practical learning path for the target role:

{target_role}

Duration:
{duration_weeks} weeks

The learner's current skills and identified gaps are supplied
below.

Design a sequential curriculum.

The path must include:

- Prerequisites
- Skills
- Topics
- Hands-on projects
- Estimated hours
- Final capstone
- Career outcomes

Avoid unnecessary duplication.

The sequence should move from foundational gaps to advanced
production-level skills.
"""

    context = (

        "CURRENT SKILLS:\n"
        +
        current_skills
        +
        "\n\n"
        "SKILL GAPS:\n"
        +
        skill_gaps

    )

    return service.generate_structured(

        prompt=prompt,

        schema=LEARNING_PATH_SCHEMA,

        context=context,

    )


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# REPORT + GENERIC ANALYSIS
# ============================================================


# ============================================================
# EXECUTIVE REPORT SCHEMA
# ============================================================

EXECUTIVE_REPORT_SCHEMA = {

    "title":
        "string",

    "executive_summary":
        "string",

    "overall_score":
        0,

    "key_strengths": [
        "string"
    ],

    "critical_gaps": [
        "string"
    ],

    "industry_readiness":
        "string",

    "priority_actions": [

        {

            "action":
                "string",

            "priority":
                "High",

            "timeline":
                "string",

        }

    ],

    "recommended_modules": [
        "string"
    ],

    "recommended_projects": [
        "string"
    ],

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
    gap_analysis: str,
    enhancements: str,
    rag_context: Optional[str] = None,
) -> StructuredResponse:

    prompt = """
Prepare an executive-level curriculum intelligence report.

The report should answer:

1. How strong is the curriculum?
2. How industry aligned is it?
3. What are the most important skill gaps?
4. What should be changed immediately?
5. Which modules should be added?
6. Which projects should be introduced?
7. What is the expected employability impact?

Write for:

- Academic leadership
- Training organizations
- Curriculum committees
- Industry advisory boards

Be concise, evidence-driven and actionable.
"""

    context_parts = [

        "CURRICULUM:\n"
        +
        curriculum,

        "\nINDUSTRY:\n"
        +
        industry,

        "\nGAP ANALYSIS:\n"
        +
        gap_analysis,

        "\nENHANCEMENTS:\n"
        +
        enhancements,

    ]

    if rag_context:

        context_parts.append(

            "\nRAG EVIDENCE:\n"
            +
            rag_context

        )

    return service.generate_structured(

        prompt=prompt,

        schema=EXECUTIVE_REPORT_SCHEMA,

        context="\n".join(
            context_parts
        ),

        temperature=0.15,

    )


# ============================================================
# GENERIC ANALYSIS
# ============================================================

def analyze(
    service: GroqService,
    instruction: str,
    context: Optional[str] = None,
    schema: Optional[
        Mapping[str, Any]
    ] = None,
) -> Union[
    GroqResponse,
    StructuredResponse,
]:

    if schema:

        return service.generate_structured(

            prompt=instruction,

            schema=schema,

            context=context,

        )

    return service.generate(

        prompt=instruction,

        context=context,

    )


# ============================================================
# DEFAULT SERVICE
# ============================================================

_default_service: Optional[
    GroqService
] = None


# ============================================================
# GET SERVICE
# ============================================================

def get_groq_service(
    config: Optional[
        GroqConfig
    ] = None,
) -> GroqService:

    global _default_service

    if config is not None:

        return GroqService(
            config=config
        )

    if _default_service is None:

        _default_service = GroqService()

    return _default_service


# ============================================================
# SIMPLE GENERATE FUNCTION
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
# SIMPLE COMPLETE FUNCTION
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
            "Groq completion failed."

        )

    return response.text


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# HEALTH CHECK + PUBLIC API + SELF TEST
# ============================================================


# ============================================================
# HEALTH CHECK
# ============================================================

def health_check(
    service: Optional[
        GroqService
    ] = None,
) -> Dict[str, Any]:

    result = {

        "installed":
            is_groq_installed(),

        "api_key_configured":
            bool(
                resolve_api_key()
            ),

        "model":
            DEFAULT_GROQ_MODEL,

        "success":
            False,

        "error":
            None,

    }

    if not result["installed"]:

        result["error"] = (
            "groq package is not installed."
        )

        return result

    if not result["api_key_configured"]:

        result["error"] = (
            "GROQ_API_KEY is not configured."
        )

        return result

    try:

        service = (

            service
            or
            get_groq_service()

        )

        response = service.generate(

            prompt=(
                "Respond with exactly one word: OK"
            ),

            temperature=0.0,

            max_tokens=10,

        )

        result["success"] = (
            response.success
        )

        result["error"] = (
            response.error
        )

        result["response"] = (
            response.text
        )

    except Exception as exc:

        result["error"] = str(
            exc
        )

    return result


# ============================================================
# SERVICE SUMMARY
# ============================================================

def service_summary(
    service: GroqService,
) -> Dict[str, Any]:

    return {

        "version":
            GROQ_SERVICE_VERSION,

        "model":
            service.config.model,

        "temperature":
            service.config.temperature,

        "max_tokens":
            service.config.max_tokens,

        "timeout":
            service.config.timeout,

        "max_retries":
            service.config.max_retries,

        "top_p":
            service.config.top_p,

        "api_key_configured":
            bool(
                service.api_key
            ),

    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "GROQ_SERVICE_VERSION",

    # Config
    "GroqConfig",

    # Responses
    "GroqResponse",

    "StructuredResponse",

    # Utility
    "resolve_api_key",

    "is_groq_installed",

    "require_groq",

    "require_api_key",

    "create_groq_client",

    "clean_text",

    "truncate_text",

    "build_system_message",

    "build_user_prompt",

    "build_messages",

    "render_prompt",

    # Service
    "GroqService",

    # JSON
    "extract_json",

    "validate_json_object",

    # Curriculum
    "analyze_curriculum",

    "analyze_industry_alignment",

    "analyze_gaps",

    "extract_skills",

    "generate_enhancements",

    "generate_learning_path",

    "generate_executive_report",

    # Generic
    "analyze",

    "get_groq_service",

    "generate",

    "complete",

    # Health
    "health_check",

    "service_summary",

]


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n"
        "============================================"
    )

    print(
        "PRAGYANAI GROQ SERVICE SELF TEST"
    )

    print(
        "============================================"
    )

    print(
        "\nGroq package installed:"
    )

    print(
        is_groq_installed()
    )

    print(
        "\nAPI key configured:"
    )

    print(
        bool(
            resolve_api_key()
        )
    )

    print(
        "\nConfigured model:"
    )

    print(
        DEFAULT_GROQ_MODEL
    )

    # --------------------------------------------------------
    # Do not make an API request unless explicitly enabled.
    # --------------------------------------------------------

    run_api_test = (

        os.getenv(
            "PRAGYANAI_GROQ_TEST"
        )
        ==
        "1"

    )

    if run_api_test:

        print(
            "\nRunning live Groq API test..."
        )

        try:

            service = GroqService()

            response = service.generate(

                prompt=(
                    "Respond with exactly: "
                    "PragyanAI Groq OK"
                ),

                temperature=0.0,

                max_tokens=20,

            )

            print(
                "\nSuccess:"
            )

            print(
                response.success
            )

            print(
                "\nResponse:"
            )

            print(
                response.text
            )

            print(
                "\nUsage:"
            )

            print(
                response.usage
            )

        except Exception as exc:

            print(
                "\nAPI test failed:"
            )

            print(
                exc
            )

    else:

        print(
            "\nLive API test skipped."
        )

        print(
            "Set PRAGYANAI_GROQ_TEST=1 "
            "to run it."
        )

    print(
        "\n============================================"
    )

    print(
        "GROQ SERVICE TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF llm/groq.py
# ============================================================
