# ============================================================
# app.py
# CHUNK 1/10
#
# PRAGYANAI CURRICULUM INTELLIGENCE PLATFORM
#
# Main Streamlit Application
#
# Features:
#   - Curriculum Intelligence
#   - Industry Alignment
#   - Skill Gap Analysis
#   - Concept Intelligence
#   - AI Curriculum Enhancement
#   - RAG-based Evidence
#   - AI Learning Path
#   - Reports
#   - Groq + Llama
#
# Secrets:
#
# .streamlit/secrets.toml
#
# GROQ_API_KEY = "gsk_xxxxxxxxx"
# GROQ_MODEL = "llama-3.3-70b-versatile"
#
# ============================================================

from __future__ import annotations

import json
import logging
import os
import re

from datetime import datetime

from pathlib import Path

from typing import Any, Dict, List, Optional


import streamlit as st


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(
    "pragyanai.app"
)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = (
    "PragyanAI Curriculum Intelligence"
)

APP_VERSION = "1.0.0"

ORGANIZATION = "PragyanAI"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(

    page_title=APP_NAME,

    page_icon="📊",

    layout="wide",

    initial_sidebar_state="expanded",

)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid #ddd;
        background: #ffffff;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }

    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background: #e8f5e9;
        border: 1px solid #81c784;
    }

    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background: #fff8e1;
        border: 1px solid #ffcc80;
    }

    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background: #e3f2fd;
        border: 1px solid #90caf9;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# PROJECT MODULE IMPORTS
# ============================================================


# ============================================================
# LLM
# ============================================================

try:

    from llm.groq import (

        GroqConfig,

        GroqService,

        health_check,

        get_groq_service,

    )

except Exception as exc:

    GroqConfig = None

    GroqService = None

    health_check = None

    get_groq_service = None

    logger.warning(

        "Groq module unavailable: %s",

        exc,

    )


# ============================================================
# REPORTS
# ============================================================

try:

    from reports.generator import (

        ReportConfig,

        ReportGenerator,

    )

except Exception as exc:

    ReportConfig = None

    ReportGenerator = None

    logger.warning(

        "Report module unavailable: %s",

        exc,

    )


# ============================================================
# CURRICULUM
# ============================================================

try:

    from curriculum.extractor import (
        CurriculumExtractor,
    )

except Exception as exc:

    CurriculumExtractor = None

    logger.warning(

        "Curriculum extractor unavailable: %s",

        exc,

    )


# ============================================================
# INDUSTRY
# ============================================================

try:

    from industry.jd_parser import (
        JDParser,
    )

except Exception as exc:

    JDParser = None

    logger.warning(

        "JD parser unavailable: %s",

        exc,

    )


# ============================================================
# AGENTS
# ============================================================

try:

    from agents.gap_agent import (
        GapAgent,
    )

except Exception as exc:

    GapAgent = None

    logger.warning(

        "Gap agent unavailable: %s",

        exc,

    )


try:

    from agents.enhancement_agent import (
        EnhancementAgent,
    )

except Exception as exc:

    EnhancementAgent = None

    logger.warning(

        "Enhancement agent unavailable: %s",

        exc,

    )


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# SESSION STATE
# ============================================================


def initialize_session_state() -> None:

    defaults = {

        "curriculum_text":
            "",

        "curriculum_data":
            {},

        "industry_text":
            "",

        "industry_data":
            {},

        "skill_data":
            {},

        "gap_data":
            {},

        "enhancement_data":
            {},

        "learning_path_data":
            {},

        "report":
            None,

        "rag_context":
            "",

        "uploaded_files":
            [],

        "analysis_complete":
            False,

        "active_tab":
            "Dashboard",

        "processing":
            False,

        "last_analysis_time":
            None,

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[
                key
            ] = value


initialize_session_state()


# ============================================================
# RESET APPLICATION
# ============================================================

def reset_application() -> None:

    keys = [

        "curriculum_text",

        "curriculum_data",

        "industry_text",

        "industry_data",

        "skill_data",

        "gap_data",

        "enhancement_data",

        "learning_path_data",

        "report",

        "rag_context",

        "uploaded_files",

        "analysis_complete",

        "processing",

        "last_analysis_time",

    ]

    for key in keys:

        if key in st.session_state:

            del st.session_state[
                key
            ]

    initialize_session_state()


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# STREAMLIT SECRETS
# ============================================================


def get_secret(
    key: str,
    default: Optional[str] = None,
) -> Optional[str]:

    # --------------------------------------------------------
    # Streamlit Secrets
    # --------------------------------------------------------

    try:

        value = st.secrets.get(
            key,
            None,
        )

        if value:

            return str(
                value
            )

    except Exception:

        pass

    # --------------------------------------------------------
    # Fallback environment variable
    #
    # Useful when running outside Streamlit.
    # --------------------------------------------------------

    value = os.getenv(
        key
    )

    if value:

        return value

    return default


# ============================================================
# GROQ CONFIGURATION
# ============================================================

def get_groq_config():

    if GroqConfig is None:

        return None

    api_key = get_secret(
        "GROQ_API_KEY"
    )

    model = get_secret(

        "GROQ_MODEL",

        "llama-3.3-70b-versatile",

    )

    return GroqConfig(

        api_key=api_key,

        model=model,

        temperature=0.2,

        max_tokens=4096,

        timeout=120,

        max_retries=3,

        top_p=1.0,

    )


# ============================================================
# GROQ SERVICE
# ============================================================

@st.cache_resource(
    show_spinner=False
)
def get_llm_service():

    if GroqService is None:

        return None

    try:

        config = get_groq_config()

        if config is None:

            return None

        return GroqService(

            config=config

        )

    except Exception as exc:

        logger.error(

            "Unable to initialize Groq: %s",

            exc,

        )

        return None


# ============================================================
# REPORT GENERATOR
# ============================================================

@st.cache_resource(
    show_spinner=False
)
def get_report_generator():

    if ReportGenerator is None:

        return None

    llm = get_llm_service()

    config = ReportConfig(

        title=(
            "PragyanAI Curriculum "
            "Intelligence Report"
        ),

        organization=ORGANIZATION,

        include_scores=True,

        include_evidence=True,

        include_recommendations=True,

        include_rag_sources=True,

        use_llm_narrative=(
            llm is not None
        ),

        max_context_chars=30000,

        output_format="markdown",

    )

    return ReportGenerator(

        config=config,

        llm_service=llm,

    )


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# FILE READING
# ============================================================


def extract_text_from_file(
    uploaded_file,
) -> str:

    if uploaded_file is None:

        return ""

    filename = (
        uploaded_file.name
        .lower()
    )

    suffix = (
        Path(filename)
        .suffix
        .lower()
    )

    try:

        # ----------------------------------------------------
        # TXT / MD
        # ----------------------------------------------------

        if suffix in {

            ".txt",
            ".md",
            ".csv",

        }:

            raw = uploaded_file.read()

            return raw.decode(

                "utf-8",

                errors="ignore",

            )

        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        if suffix == ".pdf":

            import fitz

            raw = uploaded_file.read()

            document = fitz.open(

                stream=raw,

                filetype="pdf",

            )

            pages = []

            for page in document:

                pages.append(

                    page.get_text()

                )

            document.close()

            return "\n\n".join(
                pages
            )

        # ----------------------------------------------------
        # DOCX
        # ----------------------------------------------------

        if suffix == ".docx":

            from docx import Document

            raw = uploaded_file.read()

            import io

            document = Document(

                io.BytesIO(
                    raw
                )

            )

            paragraphs = [

                paragraph.text

                for paragraph
                in document.paragraphs

                if paragraph.text.strip()

            ]

            return "\n".join(
                paragraphs
            )

        # ----------------------------------------------------
        # JSON
        # ----------------------------------------------------

        if suffix == ".json":

            raw = uploaded_file.read()

            text = raw.decode(

                "utf-8",

                errors="ignore",

            )

            try:

                data = json.loads(
                    text
                )

                return json.dumps(

                    data,

                    indent=2,

                    ensure_ascii=False,

                )

            except Exception:

                return text

        # ----------------------------------------------------
        # Images
        # ----------------------------------------------------

        if suffix in {

            ".png",
            ".jpg",
            ".jpeg",
            ".webp",

        }:

            try:

                import pytesseract

                from PIL import Image

                import io

                image = Image.open(

                    io.BytesIO(
                        uploaded_file.read()
                    )

                )

                return pytesseract.image_to_string(

                    image

                )

            except Exception as exc:

                logger.warning(

                    "OCR failed: %s",

                    exc,

                )

                return ""

    except Exception as exc:

        logger.exception(
            "File extraction failed"
        )

        st.error(

            f"Unable to read "
            f"{uploaded_file.name}: "
            f"{exc}"

        )

        return ""

    return ""


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# SIDEBAR + INPUT
# ============================================================


def render_sidebar():

    with st.sidebar:

        st.markdown(
            "## 📊 PragyanAI"
        )

        st.caption(
            "Curriculum Intelligence Platform"
        )

        st.divider()

        # ----------------------------------------------------
        # Navigation
        # ----------------------------------------------------

        st.markdown(
            "### Navigation"
        )

        page = st.radio(

            "Select Module",

            [

                "🏠 Dashboard",

                "📄 Curriculum",

                "🏢 Industry",

                "🧠 Concept Intelligence",

                "🔍 Gap Analysis",

                "🚀 Enhancements",

                "📊 Reports",

            ],

            label_visibility="collapsed",

        )

        st.session_state[
            "active_tab"
        ] = page

        st.divider()

        # ----------------------------------------------------
        # System status
        # ----------------------------------------------------

        st.markdown(
            "### System Status"
        )

        api_key = get_secret(
            "GROQ_API_KEY"
        )

        if api_key:

            st.success(
                "Groq API configured"
            )

        else:

            st.error(
                "Groq API not configured"
            )

        model = get_secret(

            "GROQ_MODEL",

            "llama-3.3-70b-versatile",

        )

        st.caption(
            f"Model: `{model}`"
        )

        st.divider()

        # ----------------------------------------------------
        # Reset
        # ----------------------------------------------------

        if st.button(

            "🔄 Reset Analysis",

            use_container_width=True,

        ):

            reset_application()

            st.rerun()

        st.divider()

        st.caption(
            f"Version {APP_VERSION}"
        )

        st.caption(
            "© PragyanAI"
        )


# ============================================================
# CURRICULUM UPLOAD
# ============================================================

def render_curriculum_input():

    st.markdown(
        "## 📄 Curriculum Input"
    )

    st.write(

        "Upload your curriculum document "
        "or paste the curriculum text."

    )

    uploaded = st.file_uploader(

        "Upload Curriculum",

        type=[

            "pdf",

            "docx",

            "txt",

            "md",

            "json",

        ],

        accept_multiple_files=False,

    )

    if uploaded:

        text = extract_text_from_file(
            uploaded
        )

        if text:

            st.session_state[
                "curriculum_text"
            ] = text

            st.session_state[
                "uploaded_files"
            ] = [

                uploaded.name

            ]

            st.success(

                f"Loaded {uploaded.name}"

            )

    text = st.text_area(

        "Curriculum Text",

        value=st.session_state[
            "curriculum_text"
        ],

        height=350,

        placeholder=(

            "Paste curriculum content here..."

        ),

    )

    st.session_state[
        "curriculum_text"
    ] = text

    return text


# ============================================================
# INDUSTRY INPUT
# ============================================================

def render_industry_input():

    st.markdown(
        "## 🏢 Industry Requirements"
    )

    st.write(

        "Paste one or more Job Descriptions, "
        "industry skill requirements or "
        "technology requirements."

    )

    industry_text = st.text_area(

        "Job Description / Industry Requirements",

        value=st.session_state[
            "industry_text"
        ],

        height=350,

        placeholder=(

            "Example:\n"
            "Python\n"
            "Machine Learning\n"
            "LLM\n"
            "RAG\n"
            "LangChain\n"
            "AWS\n"
            "Docker\n"
            "Kubernetes"

        ),

    )

    st.session_state[
        "industry_text"
    ] = industry_text

    return industry_text


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# ANALYSIS ENGINE
# ============================================================


def run_ai_analysis():

    curriculum_text = (
        st.session_state[
            "curriculum_text"
        ]
    )

    industry_text = (
        st.session_state[
            "industry_text"
        ]
    )

    if not curriculum_text.strip():

        st.error(
            "Please provide curriculum content."
        )

        return False

    llm = get_llm_service()

    if llm is None:

        st.error(

            "Groq LLM service is not available. "
            "Please configure GROQ_API_KEY "
            "in Streamlit Secrets."

        )

        return False

    progress = st.progress(
        0
    )

    status = st.empty()

    try:

        # ----------------------------------------------------
        # STEP 1 — Curriculum intelligence
        # ----------------------------------------------------

        status.info(

            "Step 1/6 — Analyzing curriculum..."

        )

        curriculum_prompt = """

Analyze this curriculum and extract:

- curriculum summary
- modules
- topics
- skills
- tools
- technologies
- projects
- strengths
- weaknesses
- missing areas

Return structured JSON.

"""

        curriculum_schema = {

            "summary":
                "string",

            "modules": [
                "string"
            ],

            "topics": [
                "string"
            ],

            "skills": [
                "string"
            ],

            "tools": [
                "string"
            ],

            "technologies": [
                "string"
            ],

            "projects": [
                "string"
            ],

            "strengths": [
                "string"
            ],

            "weaknesses": [
                "string"
            ],

            "missing_areas": [
                "string"
            ],

        }

        curriculum_result = (

            llm.generate_structured(

                prompt=curriculum_prompt,

                schema=curriculum_schema,

                context=curriculum_text,

            )

        )

        curriculum_data = (

            curriculum_result.data

            if curriculum_result.success

            else {}

        )

        st.session_state[
            "curriculum_data"
        ] = curriculum_data

        progress.progress(
            16
        )

        # ----------------------------------------------------
        # STEP 2 — Industry skills
        # ----------------------------------------------------

        status.info(

            "Step 2/6 — Analyzing industry requirements..."

        )

        industry_schema = {

            "required_skills": [
                "string"
            ],

            "tools": [
                "string"
            ],

            "technologies": [
                "string"
            ],

            "frameworks": [
                "string"
            ],

            "cloud_platforms": [
                "string"
            ],

            "job_roles": [
                "string"
            ],

        }

        industry_result = (

            llm.generate_structured(

                prompt="""

Extract industry requirements from the
provided job descriptions.

Identify:

- technical skills
- tools
- technologies
- frameworks
- cloud platforms
- job roles

Only extract information supported by
the supplied text.

""",

                schema=industry_schema,

                context=industry_text,

            )

        )

        industry_data = (

            industry_result.data

            if industry_result.success

            else {}

        )

        st.session_state[
            "industry_data"
        ] = industry_data

        progress.progress(
            32
        )

        # ----------------------------------------------------
        # STEP 3 — Skill gap
        # ----------------------------------------------------

        status.info(

            "Step 3/6 — Calculating skill gaps..."

        )

        gap_schema = {

            "overall_gap_score":
                0,

            "critical_gaps": [],

            "moderate_gaps": [],

            "minor_gaps": [],

            "matching_skills": [],

            "missing_tools": [],

            "missing_projects": [],

            "missing_concepts": [],

        }

        gap_context = (

            "CURRICULUM:\n"
            +
            json.dumps(

                curriculum_data,

                indent=2,

                ensure_ascii=False,

            )

            +

            "\n\nINDUSTRY:\n"
            +

            json.dumps(

                industry_data,

                indent=2,

                ensure_ascii=False,

            )

        )

        gap_result = (

            llm.generate_structured(

                prompt="""

Compare the curriculum against the
industry requirements.

Identify:

- matching skills
- critical gaps
- moderate gaps
- minor gaps
- missing tools
- missing projects
- missing concepts

Calculate an overall gap score between
0 and 1 where 1 means maximum gap.

""",

                schema=gap_schema,

                context=gap_context,

            )

        )

        gap_data = (

            gap_result.data

            if gap_result.success

            else {}

        )

        st.session_state[
            "gap_data"
        ] = gap_data

        progress.progress(
            50
        )

        # ----------------------------------------------------
        # STEP 4 — Enhancements
        # ----------------------------------------------------

        status.info(

            "Step 4/6 — Generating enhancements..."

        )

        enhancement_schema = {

            "recommendations": [],

            "new_modules": [],

            "new_projects": [],

        }

        enhancement_context = (

            "CURRICULUM:\n"
            +
            json.dumps(

                curriculum_data,

                indent=2,

                ensure_ascii=False,

            )

            +

            "\n\nGAPS:\n"
            +

            json.dumps(

                gap_data,

                indent=2,

                ensure_ascii=False,

            )

            +

            "\n\nINDUSTRY:\n"
            +

            json.dumps(

                industry_data,

                indent=2,

                ensure_ascii=False,

            )

        )

        enhancement_result = (

            llm.generate_structured(

                prompt="""

Recommend curriculum enhancements
based on industry requirements.

Prioritize:

- employability
- GenAI
- Agentic AI
- RAG
- LLMOps
- MLOps
- cloud
- deployment
- projects
- production engineering

Return actionable recommendations.

""",

                schema=enhancement_schema,

                context=enhancement_context,

            )

        )

        enhancement_data = (

            enhancement_result.data

            if enhancement_result.success

            else {}

        )

        st.session_state[
            "enhancement_data"
        ] = enhancement_data

        progress.progress(
            66
        )

        # ----------------------------------------------------
        # STEP 5 — Learning path
        # ----------------------------------------------------

        status.info(

            "Step 5/6 — Creating learning path..."

        )

        learning_schema = {

            "learning_path": [],

            "capstone_project":
                "",

            "career_outcomes": [],

        }

        learning_context = (

            "CURRENT CURRICULUM:\n"
            +
            json.dumps(

                curriculum_data,

                indent=2,

                ensure_ascii=False,

            )

            +

            "\n\nSKILL GAPS:\n"
            +

            json.dumps(

                gap_data,

                indent=2,

                ensure_ascii=False,

            )

        )

        learning_result = (

            llm.generate_structured(

                prompt="""

Create a practical learning path
to close the identified skill gaps.

Include:

- sequence
- modules
- skills
- topics
- projects
- estimated hours
- prerequisites
- capstone
- career outcomes

""",

                schema=learning_schema,

                context=learning_context,

            )

        )

        learning_data = (

            learning_result.data

            if learning_result.success

            else {}

        )

        st.session_state[
            "learning_path_data"
        ] = learning_data

        progress.progress(
            83
        )

        # ----------------------------------------------------
        # STEP 6 — Comprehensive report
        # ----------------------------------------------------

        status.info(

            "Step 6/6 — Generating final report..."

        )

        generator = (
            get_report_generator()
        )

        if generator:

            report = (

                generator
                .generate_comprehensive_report(

                    curriculum=curriculum_data,

                    industry=industry_data,

                    gaps=gap_data,

                    enhancements=enhancement_data,

                    learning_path=learning_data,

                    rag_context=(
                        st.session_state[
                            "rag_context"
                        ]
                    ),

                )

            )

            st.session_state[
                "report"
            ] = report

        progress.progress(
            100
        )

        st.session_state[
            "analysis_complete"
        ] = True

        st.session_state[
            "last_analysis_time"
        ] = datetime.now()

        status.success(

            "Analysis completed successfully."

        )

        return True

    except Exception as exc:

        logger.exception(
            "Analysis failed"
        )

        status.error(

            f"Analysis failed: {exc}"

        )

        return False


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# DASHBOARD
# ============================================================


def count_items(
    data: Any,
    key: str,
) -> int:

    if not isinstance(
        data,
        dict,
    ):

        return 0

    value = data.get(
        key,
        []
    )

    if isinstance(
        value,
        list,
    ):

        return len(
            value
        )

    return 0


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():

    st.markdown(

        '<div class="main-title">'
        '📊 PragyanAI Curriculum Intelligence'
        '</div>',

        unsafe_allow_html=True,

    )

    st.markdown(

        '<div class="subtitle">'
        'AI-powered curriculum analysis, '
        'industry alignment and skill-gap '
        'intelligence platform'
        '</div>',

        unsafe_allow_html=True,

    )

    # --------------------------------------------------------
    # Introduction
    # --------------------------------------------------------

    st.info(

        """
        Upload a curriculum and provide industry
        requirements to automatically identify
        skill gaps, analyze employability,
        recommend curriculum enhancements and
        generate an AI-powered intelligence report.
        """

    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    curriculum = st.session_state[
        "curriculum_data"
    ]

    industry = st.session_state[
        "industry_data"
    ]

    gaps = st.session_state[
        "gap_data"
    ]

    enhancements = st.session_state[
        "enhancement_data"
    ]

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        st.metric(

            "Curriculum Skills",

            count_items(
                curriculum,
                "skills",
            ),

        )

    with col2:

        st.metric(

            "Industry Skills",

            count_items(
                industry,
                "required_skills",
            ),

        )

    with col3:

        st.metric(

            "Critical Gaps",

            count_items(
                gaps,
                "critical_gaps",
            ),

        )

    with col4:

        st.metric(

            "Enhancements",

            count_items(
                enhancements,
                "recommendations",
            ),

        )

    # --------------------------------------------------------
    # Main action
    # --------------------------------------------------------

    st.divider()

    col1, col2 = st.columns(
        2
    )

    with col1:

        if st.button(

            "🚀 Run Complete AI Analysis",

            type="primary",

            use_container_width=True,

        ):

            run_ai_analysis()

    with col2:

        if st.button(

            "📄 Start with Curriculum",

            use_container_width=True,

        ):

            st.session_state[
                "active_tab"
            ] = "📄 Curriculum"

            st.rerun()

    # --------------------------------------------------------
    # Recent analysis
    # --------------------------------------------------------

    if st.session_state[
        "last_analysis_time"
    ]:

        st.success(

            "Last analysis completed at "
            +
            str(

                st.session_state[
                    "last_analysis_time"
                ]

            )

        )

    # --------------------------------------------------------
    # Workflow
    # --------------------------------------------------------

    st.markdown(
        "## 🔄 Analysis Workflow"
    )

    cols = st.columns(
        6
    )

    workflow = [

        ("1", "📄", "Curriculum"),

        ("2", "🏢", "Industry"),

        ("3", "🔍", "Gap Analysis"),

        ("4", "🚀", "Enhancement"),

        ("5", "🧠", "Learning Path"),

        ("6", "📊", "Report"),

    ]

    for column, item in zip(
        cols,
        workflow,
    ):

        number, icon, title = item

        with column:

            st.markdown(

                f"""
                <div class="metric-card">
                    <h3>{icon}</h3>
                    <strong>{number}. {title}</strong>
                </div>
                """,

                unsafe_allow_html=True,

            )


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# MODULE PAGES
# ============================================================


def render_gap_page():

    st.markdown(
        "## 🔍 Skill Gap Analysis"
    )

    data = st.session_state[
        "gap_data"
    ]

    if not data:

        st.warning(

            "Run the AI analysis first."

        )

        return

    score = data.get(
        "overall_gap_score"
    )

    if score is not None:

        if isinstance(
            score,
            (int, float),
        ):

            if score <= 1:

                gap_percentage = score * 100

            else:

                gap_percentage = score

            st.metric(

                "Overall Gap Score",

                f"{gap_percentage:.1f}%",

            )

    col1, col2 = st.columns(
        2
    )

    with col1:

        st.markdown(
            "### 🔴 Critical Gaps"
        )

        for item in data.get(
            "critical_gaps",
            [],
        ):

            if isinstance(
                item,
                dict,
            ):

                st.error(

                    json.dumps(
                        item,
                        indent=2,
                        ensure_ascii=False,
                    )

                )

            else:

                st.error(
                    str(item)
                )

    with col2:

        st.markdown(
            "### 🟡 Moderate Gaps"
        )

        for item in data.get(
            "moderate_gaps",
            [],
        ):

            st.warning(

                json.dumps(
                    item,
                    indent=2,
                    ensure_ascii=False,
                )

                if isinstance(
                    item,
                    dict,
                )

                else
                str(item)

            )

    st.markdown(
        "### 🛠 Missing Tools"
    )

    st.write(

        data.get(
            "missing_tools",
            [],
        )

    )

    st.markdown(
        "### 📚 Missing Concepts"
    )

    st.write(

        data.get(
            "missing_concepts",
            [],
        )

    )

    st.markdown(
        "### 🧪 Missing Projects"
    )

    st.write(

        data.get(
            "missing_projects",
            [],
        )

    )


# ============================================================
# ENHANCEMENTS
# ============================================================

def render_enhancement_page():

    st.markdown(
        "## 🚀 Curriculum Enhancements"
    )

    data = st.session_state[
        "enhancement_data"
    ]

    if not data:

        st.warning(

            "Run the AI analysis first."

        )

        return

    recommendations = data.get(
        "recommendations",
        [],
    )

    st.markdown(
        "### Priority Recommendations"
    )

    for index, item in enumerate(

        recommendations,

        start=1,

    ):

        if isinstance(
            item,
            dict,
        ):

            with st.expander(

                f"{index}. "
                +
                str(

                    item.get(
                        "skill",
                        item.get(
                            "area",
                            "Recommendation",
                        ),
                    )

                )

            ):

                st.json(
                    item
                )

        else:

            st.write(
                f"{index}. {item}"
            )

    modules = data.get(
        "new_modules",
        [],
    )

    if modules:

        st.markdown(
            "### 📚 Recommended New Modules"
        )

        st.json(
            modules
        )

    projects = data.get(
        "new_projects",
        [],
    )

    if projects:

        st.markdown(
            "### 🧪 Recommended Projects"
        )

        st.json(
            projects
        )


# ============================================================
# INDUSTRY PAGE
# ============================================================

def render_industry_page():

    st.markdown(
        "## 🏢 Industry Intelligence"
    )

    industry = st.session_state[
        "industry_data"
    ]

    if not industry:

        st.warning(

            "Run the AI analysis first."

        )

        return

    cols = st.columns(
        3
    )

    with cols[0]:

        st.metric(

            "Required Skills",

            len(

                industry.get(
                    "required_skills",
                    [],
                )

            ),

        )

    with cols[1]:

        st.metric(

            "Tools",

            len(

                industry.get(
                    "tools",
                    [],
                )

            ),

        )

    with cols[2]:

        st.metric(

            "Frameworks",

            len(

                industry.get(
                    "frameworks",
                    [],
                )

            ),

        )

    st.markdown(
        "### Required Skills"
    )

    st.write(

        industry.get(
            "required_skills",
            [],
        )

    )

    st.markdown(
        "### Technologies"
    )

    st.write(

        industry.get(
            "technologies",
            [],
        )

    )

    st.markdown(
        "### Cloud Platforms"
    )

    st.write(

        industry.get(
            "cloud_platforms",
            [],
        )

    )


# ============================================================
# CURRICULUM PAGE
# ============================================================

def render_curriculum_page():

    text = render_curriculum_input()

    if text:

        data = st.session_state[
            "curriculum_data"
        ]

        if data:

            st.divider()

            st.markdown(
                "### Curriculum Intelligence"
            )

            st.write(

                data.get(
                    "summary",
                    "",
                )

            )

            col1, col2, col3 = st.columns(
                3
            )

            with col1:

                st.metric(

                    "Skills",

                    len(

                        data.get(
                            "skills",
                            [],
                        )

                    ),

                )

            with col2:

                st.metric(

                    "Topics",

                    len(

                        data.get(
                            "topics",
                            [],
                        )

                    ),

                )

            with col3:

                st.metric(

                    "Projects",

                    len(

                        data.get(
                            "projects",
                            [],
                        )

                    ),

                )


# ============================================================
# CONCEPT INTELLIGENCE
# ============================================================

def render_concept_page():

    st.markdown(
        "## 🧠 Concept Intelligence"
    )

    curriculum = st.session_state[
        "curriculum_data"
    ]

    if not curriculum:

        st.warning(

            "Analyze the curriculum first."

        )

        return

    concepts = (

        curriculum.get(
            "topics",
            []
        )

    )

    if concepts:

        st.markdown(
            "### Detected Concepts"
        )

        for concept in concepts:

            st.write(
                f"• {concept}"
            )

    else:

        st.info(
            "No concepts extracted yet."
        )


# ============================================================
# REPORT PAGE
# ============================================================

def render_reports_page():

    st.markdown(
        "## 📊 Reports"
    )

    report = st.session_state[
        "report"
    ]

    if report is None:

        st.warning(

            "Run the complete AI analysis "
            "to generate a report."

        )

        return

    generator = (
        get_report_generator()
    )

    if generator is None:

        st.error(
            "Report generator unavailable."
        )

        return

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    if report.overall_score is not None:

        score = report.overall_score

        if 0 <= score <= 1:

            score_display = score * 100

        else:

            score_display = score

        st.metric(

            "Overall Score",

            f"{score_display:.1f}%",

        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if report.executive_summary:

        st.markdown(
            "### Executive Summary"
        )

        st.info(
            report.executive_summary
        )

    # --------------------------------------------------------
    # Downloads
    # --------------------------------------------------------

    markdown = generator.to_markdown(
        report
    )

    json_data = generator.to_json(
        report
    )

    col1, col2 = st.columns(
        2
    )

    with col1:

        st.download_button(

            "⬇️ Download Markdown",

            data=markdown,

            file_name=(
                "curriculum_intelligence_report.md"
            ),

            mime="text/markdown",

            use_container_width=True,

        )

    with col2:

        st.download_button(

            "⬇️ Download JSON",

            data=json_data,

            file_name=(
                "curriculum_intelligence_report.json"
            ),

            mime="application/json",

            use_container_width=True,

        )

    st.divider()

    st.markdown(
        markdown
    )


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# MAIN APPLICATION
# ============================================================


def render_header():

    st.markdown(

        f"""
        <div class="main-title">
            📊 {APP_NAME}
        </div>

        <div class="subtitle">
            AI-powered Curriculum Intelligence,
            Industry Alignment & Skill Gap Analysis
        </div>
        """,

        unsafe_allow_html=True,

    )


# ============================================================
# SYSTEM HEALTH
# ============================================================

def render_system_health():

    api_key = get_secret(
        "GROQ_API_KEY"
    )

    if not api_key:

        st.warning(

            """
            ⚠️ Groq API key is not configured.

            Add it to:

            `.streamlit/secrets.toml`

            Example:

            GROQ_API_KEY = "gsk_xxxxxxxxx"
            GROQ_MODEL = "llama-3.3-70b-versatile"
            """

        )

        return False

    return True


# ============================================================
# ROUTER
# ============================================================

def route_page(
    page: str,
):

    if page == "🏠 Dashboard":

        render_dashboard()

    elif page == "📄 Curriculum":

        render_curriculum_page()

    elif page == "🏢 Industry":

        render_industry_page()

    elif page == "🧠 Concept Intelligence":

        render_concept_page()

    elif page == "🔍 Gap Analysis":

        render_gap_page()

    elif page == "🚀 Enhancements":

        render_enhancement_page()

    elif page == "📊 Reports":

        render_reports_page()

    else:

        render_dashboard()


# ============================================================
# APPLICATION ENTRYPOINT
# ============================================================

def main():

    render_sidebar()

    render_header()

    render_system_health()

    page = st.session_state[
        "active_tab"
    ]

    route_page(
        page
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()


# ============================================================
# END OF app.py
# ============================================================
