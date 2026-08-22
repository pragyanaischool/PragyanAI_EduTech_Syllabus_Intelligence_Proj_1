# ============================================================
# reports/generator.py
# CHUNK 1/10
#
# PRAGYANAI CURRICULUM INTELLIGENCE
# REPORT GENERATOR
#
# Responsibilities:
#   - Generate structured reports
#   - Executive reports
#   - Curriculum analysis reports
#   - Industry alignment reports
#   - Gap analysis reports
#   - Enhancement reports
#   - Skill intelligence reports
#   - Learning path reports
#   - Comprehensive reports
#   - Markdown / HTML / JSON output
#   - Optional LLM-powered narrative generation
#
# Dependencies:
#
#   llm/groq.py
#   curriculum/models.py
#
# ============================================================

from __future__ import annotations

import html
import json
import logging
import re

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from datetime import (
    datetime,
)

from pathlib import Path

from typing import (
    Any,
    Dict,
    Iterable,
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

REPORT_GENERATOR_VERSION = "1.0.0"


# ============================================================
# OPTIONAL LLM IMPORT
# ============================================================

try:

    from llm.groq import (
        GroqService,
        StructuredResponse,
        get_groq_service,
    )

except ImportError:

    try:

        from ..llm.groq import (
            GroqService,
            StructuredResponse,
            get_groq_service,
        )

    except ImportError:

        GroqService = Any
        StructuredResponse = Any

        def get_groq_service():

            raise ImportError(
                "llm.groq could not be imported."
            )


# ============================================================
# REPORT CONFIGURATION
# ============================================================

@dataclass
class ReportConfig:

    title: str = (
        "PragyanAI Curriculum "
        "Intelligence Report"
    )

    organization: str = "PragyanAI"

    include_scores: bool = True

    include_evidence: bool = True

    include_recommendations: bool = True

    include_rag_sources: bool = True

    use_llm_narrative: bool = True

    max_context_chars: int = 30000

    output_format: str = "markdown"


# ============================================================
# REPORT SECTION
# ============================================================

@dataclass
class ReportSection:

    title: str

    content: Any = ""

    order: int = 0

    section_type: str = "text"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# REPORT
# ============================================================

@dataclass
class Report:

    title: str = ""

    report_type: str = ""

    generated_at: str = ""

    executive_summary: str = ""

    overall_score: Optional[float] = None

    sections: List[
        ReportSection
    ] = field(
        default_factory=list
    )

    recommendations: List[
        Any
    ] = field(
        default_factory=list
    )

    sources: List[
        Any
    ] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# DATA NORMALIZATION UTILITIES
# ============================================================


# ============================================================
# SAFE STRING
# ============================================================

def safe_string(
    value: Any,
) -> str:

    if value is None:

        return ""

    if isinstance(
        value,
        str,
    ):

        return value.strip()

    return str(
        value
    ).strip()


# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:

    if value is None:

        return default

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# SAFE LIST
# ============================================================

def safe_list(
    value: Any,
) -> List[Any]:

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

    if isinstance(
        value,
        set,
    ):

        return list(
            value
        )

    if isinstance(
        value,
        str,
    ):

        if not value.strip():

            return []

        return [

            item.strip()

            for item
            in value.split(",")

            if item.strip()

        ]

    return [
        value
    ]


# ============================================================
# TO DICT
# ============================================================

def to_dict(
    value: Any,
) -> Dict[str, Any]:

    if value is None:

        return {}

    if isinstance(
        value,
        dict,
    ):

        return dict(
            value
        )

    if hasattr(
        value,
        "model_dump",
    ):

        try:

            return dict(
                value.model_dump()
            )

        except Exception:

            pass

    if hasattr(
        value,
        "dict",
    ):

        try:

            return dict(
                value.dict()
            )

        except Exception:

            pass

    if hasattr(
        value,
        "__dataclass_fields__",
    ):

        try:

            return asdict(
                value
            )

        except Exception:

            pass

    if hasattr(
        value,
        "__dict__",
    ):

        try:

            return {

                key: val

                for key, val
                in vars(
                    value
                ).items()

                if not key.startswith(
                    "_"
                )

            }

        except Exception:

            pass

    return {}


# ============================================================
# NORMALIZE OBJECT
# ============================================================

def normalize_object(
    value: Any,
) -> Any:

    if value is None:

        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):

        return value

    if isinstance(
        value,
        Mapping,
    ):

        return {

            str(key):
            normalize_object(
                val
            )

            for key, val
            in value.items()

        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):

        return [

            normalize_object(
                item
            )

            for item
            in value

        ]

    return to_dict(
        value
    )


# ============================================================
# TRUNCATE
# ============================================================

def truncate(
    text: Any,
    max_chars: int,
) -> str:

    text = safe_string(
        text
    )

    if len(text) <= max_chars:

        return text

    return (

        text[
            :max_chars
        ]

        +
        "\n\n[TRUNCATED]"

    )


# ============================================================
# FORMAT SCORE
# ============================================================

def format_score(
    score: Any,
) -> str:

    value = safe_float(
        score
    )

    if value is None:

        return "N/A"

    # Convert 0-1 score to percentage.
    if 0 <= value <= 1:

        return f"{value * 100:.1f}%"

    return f"{value:.1f}"


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# REPORT GENERATOR CORE
# ============================================================


class ReportGenerator:

    def __init__(
        self,
        config: Optional[
            ReportConfig
        ] = None,
        llm_service: Optional[
            GroqService
        ] = None,
    ) -> None:

        self.config = (

            config
            or
            ReportConfig()

        )

        self.llm_service = (
            llm_service
        )

        if (
            self.config.use_llm_narrative
            and
            self.llm_service is None
        ):

            try:

                self.llm_service = (
                    get_groq_service()
                )

            except Exception as exc:

                logger.warning(

                    "LLM service unavailable: %s",

                    exc,

                )

                self.llm_service = None

    # --------------------------------------------------------
    # Current timestamp
    # --------------------------------------------------------

    @staticmethod
    def timestamp() -> str:

        return datetime.now().isoformat(
            timespec="seconds"
        )

    # --------------------------------------------------------
    # Create report
    # --------------------------------------------------------

    def create_report(
        self,
        report_type: str,
        title: Optional[str] = None,
    ) -> Report:

        return Report(

            title=(

                title
                or
                self.config.title

            ),

            report_type=report_type,

            generated_at=self.timestamp(),

            metadata={

                "generator_version":
                    REPORT_GENERATOR_VERSION,

                "organization":
                    self.config.organization,

            },

        )

    # --------------------------------------------------------
    # Add section
    # --------------------------------------------------------

    @staticmethod
    def add_section(
        report: Report,
        title: str,
        content: Any,
        order: Optional[int] = None,
        section_type: str = "text",
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> Report:

        if order is None:

            order = len(
                report.sections
            ) + 1

        report.sections.append(

            ReportSection(

                title=title,

                content=content,

                order=order,

                section_type=section_type,

                metadata=dict(

                    metadata
                    or
                    {}

                ),

            )

        )

        report.sections.sort(

            key=lambda item:
            item.order

        )

        return report

    # --------------------------------------------------------
    # Set summary
    # --------------------------------------------------------

    @staticmethod
    def set_summary(
        report: Report,
        summary: str,
    ) -> Report:

        report.executive_summary = (
            safe_string(
                summary
            )
        )

        return report

    # --------------------------------------------------------
    # Set score
    # --------------------------------------------------------

    @staticmethod
    def set_score(
        report: Report,
        score: Any,
    ) -> Report:

        report.overall_score = safe_float(
            score
        )

        return report

    # --------------------------------------------------------
    # Add recommendation
    # --------------------------------------------------------

    @staticmethod
    def add_recommendation(
        report: Report,
        recommendation: Any,
    ) -> Report:

        report.recommendations.append(

            normalize_object(
                recommendation
            )

        )

        return report

    # --------------------------------------------------------
    # Add source
    # --------------------------------------------------------

    @staticmethod
    def add_source(
        report: Report,
        source: Any,
    ) -> Report:

        report.sources.append(

            normalize_object(
                source
            )

        )

        return report


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# EXECUTIVE REPORT
# ============================================================


EXECUTIVE_SCHEMA = {

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

    "conclusion":
        "string",

}


def _extract_llm_data(
    response: Any,
) -> Dict[str, Any]:

    if response is None:

        return {}

    data = getattr(
        response,
        "data",
        None,
    )

    if isinstance(
        data,
        dict,
    ):

        return data

    if isinstance(
        response,
        dict,
    ):

        return dict(
            response
        )

    return {}


class ReportGenerator(ReportGenerator):

    def generate_executive_report(
        self,
        curriculum: Any,
        industry: Any = None,
        gap_analysis: Any = None,
        enhancements: Any = None,
        rag_context: Optional[str] = None,
    ) -> Report:

        report = self.create_report(

            report_type="executive",

            title=(
                "Executive Curriculum "
                "Intelligence Report"
            ),

        )

        curriculum_data = normalize_object(
            curriculum
        )

        industry_data = normalize_object(
            industry
        )

        gap_data = normalize_object(
            gap_analysis
        )

        enhancement_data = normalize_object(
            enhancements
        )

        context = self._build_context(

            curriculum_data,

            industry_data,

            gap_data,

            enhancement_data,

            rag_context,

        )

        llm_data = {}

        if (
            self.config.use_llm_narrative
            and
            self.llm_service
        ):

            try:

                response = (
                    self.llm_service
                    .generate_structured(

                        prompt="""
Prepare an executive curriculum
intelligence report.

Summarize the curriculum,
industry alignment, skill gaps,
enhancements and career readiness.

Be evidence-driven and actionable.
""",

                        schema=EXECUTIVE_SCHEMA,

                        context=context,

                        temperature=0.15,

                    )
                )

                llm_data = _extract_llm_data(
                    response
                )

            except Exception as exc:

                logger.warning(

                    "Executive LLM report failed: %s",

                    exc,

                )

        summary = safe_string(

            llm_data.get(
                "executive_summary"
            )

            or

            self._fallback_summary(
                gap_data,
                industry_data,
            )

        )

        score = (

            llm_data.get(
                "overall_score"
            )

            or

            self._calculate_overall_score(
                industry_data,
                gap_data,
            )

        )

        report.executive_summary = summary

        report.overall_score = safe_float(
            score
        )

        self.add_section(

            report,

            "Key Strengths",

            safe_list(

                llm_data.get(
                    "key_strengths"
                )

            ),

            section_type="list",

        )

        self.add_section(

            report,

            "Critical Gaps",

            safe_list(

                llm_data.get(
                    "critical_gaps"
                )

            ),

            section_type="list",

        )

        self.add_section(

            report,

            "Industry Readiness",

            llm_data.get(
                "industry_readiness",
                "Analysis pending.",
            ),

            section_type="text",

        )

        self.add_section(

            report,

            "Priority Actions",

            safe_list(

                llm_data.get(
                    "priority_actions"
                )

            ),

            section_type="table",

        )

        self.add_section(

            report,

            "Conclusion",

            llm_data.get(
                "conclusion",
                "",
            ),

            section_type="text",

        )

        for item in safe_list(

            llm_data.get(
                "priority_actions"
            )

        ):

            self.add_recommendation(

                report,

                item,

            )

        if rag_context:

            self.add_source(

                report,

                {
                    "type":
                        "rag",

                    "description":
                        "Retrieved RAG evidence",

                },

            )

        return report


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# GAP ANALYSIS REPORT
# ============================================================


class ReportGenerator(ReportGenerator):

    def generate_gap_report(
        self,
        gap_analysis: Any,
        curriculum: Any = None,
        industry: Any = None,
    ) -> Report:

        report = self.create_report(

            report_type="gap_analysis",

            title=(
                "Curriculum Skill Gap "
                "Analysis Report"
            ),

        )

        data = normalize_object(
            gap_analysis
        )

        critical = safe_list(

            data.get(
                "critical_gaps"
            )

        )

        moderate = safe_list(

            data.get(
                "moderate_gaps"
            )

        )

        minor = safe_list(

            data.get(
                "minor_gaps"
            )

        )

        missing_tools = safe_list(

            data.get(
                "missing_tools"
            )

        )

        missing_projects = safe_list(

            data.get(
                "missing_projects"
            )

        )

        missing_concepts = safe_list(

            data.get(
                "missing_concepts"
            )

        )

        score = data.get(
            "overall_gap_score"
        )

        report.overall_score = (
            safe_float(
                score
            )
        )

        report.executive_summary = (

            f"The analysis identified "
            f"{len(critical)} critical, "
            f"{len(moderate)} moderate and "
            f"{len(minor)} minor gaps."

        )

        self.add_section(

            report,

            "Critical Skill Gaps",

            critical,

            section_type="table",

        )

        self.add_section(

            report,

            "Moderate Skill Gaps",

            moderate,

            section_type="table",

        )

        self.add_section(

            report,

            "Minor Skill Gaps",

            minor,

            section_type="table",

        )

        self.add_section(

            report,

            "Missing Concepts",

            missing_concepts,

            section_type="list",

        )

        self.add_section(

            report,

            "Missing Tools & Platforms",

            missing_tools,

            section_type="list",

        )

        self.add_section(

            report,

            "Missing Projects",

            missing_projects,

            section_type="list",

        )

        # ----------------------------------------------------
        # Priority recommendations
        # ----------------------------------------------------

        for item in (

            critical
            +
            moderate

        ):

            self.add_recommendation(

                report,

                item,

            )

        return report


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# INDUSTRY ALIGNMENT REPORT
# ============================================================


class ReportGenerator(ReportGenerator):

    def generate_industry_report(
        self,
        alignment: Any,
        curriculum: Any = None,
        job_description: Any = None,
    ) -> Report:

        report = self.create_report(

            report_type="industry_alignment",

            title=(
                "Industry Alignment "
                "Assessment Report"
            ),

        )

        data = normalize_object(
            alignment
        )

        score = (

            data.get(
                "overall_alignment_score"
            )

            or

            data.get(
                "alignment_score"
            )

        )

        report.overall_score = (
            safe_float(
                score
            )
        )

        report.executive_summary = (

            "The curriculum was evaluated "
            "against identified industry "
            "requirements."

        )

        self.add_section(

            report,

            "Matching Skills",

            safe_list(

                data.get(
                    "matching_skills"
                )

            ),

            section_type="list",

        )

        self.add_section(

            report,

            "Partially Matching Skills",

            safe_list(

                data.get(
                    "partially_matching_skills"
                )

            ),

            section_type="list",

        )

        self.add_section(

            report,

            "Missing Skills",

            safe_list(

                data.get(
                    "missing_skills"
                )

            ),

            section_type="list",

        )

        self.add_section(

            report,

            "Required Tools",

            safe_list(

                data.get(
                    "tools_required"
                )

            ),

            section_type="list",

        )

        self.add_section(

            report,

            "Experience Expectations",

            safe_list(

                data.get(
                    "experience_expectations"
                )

            ),

            section_type="list",

        )

        self.add_section(

            report,

            "Recommendations",

            safe_list(

                data.get(
                    "recommendations"
                )

            ),

            section_type="list",

        )

        for recommendation in safe_list(

            data.get(
                "recommendations"
            )

        ):

            self.add_recommendation(

                report,

                recommendation,

            )

        return report


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# ENHANCEMENT + LEARNING PATH REPORTS
# ============================================================


class ReportGenerator(ReportGenerator):

    def generate_enhancement_report(
        self,
        enhancements: Any,
    ) -> Report:

        report = self.create_report(

            report_type="enhancement",

            title=(
                "Curriculum Enhancement "
                "Recommendation Report"
            ),

        )

        data = normalize_object(
            enhancements
        )

        recommendations = safe_list(

            data.get(
                "recommendations"
            )

        )

        modules = safe_list(

            data.get(
                "new_modules"
            )

        )

        report.executive_summary = (

            f"{len(recommendations)} "
            "enhancement recommendations "
            "and "
            f"{len(modules)} new modules "
            "were identified."

        )

        self.add_section(

            report,

            "Enhancement Recommendations",

            recommendations,

            section_type="table",

        )

        self.add_section(

            report,

            "Recommended New Modules",

            modules,

            section_type="table",

        )

        priority_order = {

            "critical": 0,

            "high": 1,

            "medium": 2,

            "low": 3,

        }

        sorted_recommendations = sorted(

            recommendations,

            key=lambda item:

                priority_order.get(

                    safe_string(

                        to_dict(
                            item
                        ).get(
                            "priority",
                            "medium",
                        )

                    ).lower(),

                    99,

                )

        )

        for recommendation in (

            sorted_recommendations

        ):

            self.add_recommendation(

                report,

                recommendation,

            )

        return report

    # --------------------------------------------------------
    # Learning path
    # --------------------------------------------------------

    def generate_learning_path_report(
        self,
        learning_path: Any,
    ) -> Report:

        report = self.create_report(

            report_type="learning_path",

            title=(
                "AI Engineering "
                "Learning Path"
            ),

        )

        data = normalize_object(
            learning_path
        )

        path = safe_list(

            data.get(
                "learning_path"
            )

        )

        report.executive_summary = (

            f"The proposed learning path "
            f"contains {len(path)} stages."

        )

        self.add_section(

            report,

            "Learning Sequence",

            path,

            section_type="table",

        )

        self.add_section(

            report,

            "Capstone Project",

            data.get(
                "capstone_project",
                "",
            ),

            section_type="text",

        )

        self.add_section(

            report,

            "Career Outcomes",

            safe_list(

                data.get(
                    "career_outcomes"
                )

            ),

            section_type="list",

        )

        return report


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# SKILL INTELLIGENCE + COMPREHENSIVE REPORT
# ============================================================


class ReportGenerator(ReportGenerator):

    def generate_skill_report(
        self,
        skill_data: Any,
    ) -> Report:

        report = self.create_report(

            report_type="skill_intelligence",

            title=(
                "Skill Intelligence Report"
            ),

        )

        data = normalize_object(
            skill_data
        )

        skills = safe_list(

            data.get(
                "skills"
            )

        )

        tools = safe_list(

            data.get(
                "tools"
            )

        )

        platforms = safe_list(

            data.get(
                "platforms"
            )

        )

        frameworks = safe_list(

            data.get(
                "frameworks"
            )

        )

        databases = safe_list(

            data.get(
                "databases"
            )

        )

        report.executive_summary = (

            f"{len(skills)} skills, "
            f"{len(tools)} tools, "
            f"{len(frameworks)} frameworks "
            "and "
            f"{len(platforms)} platforms "
            "were identified."

        )

        self.add_section(

            report,

            "Skills",

            skills,

            section_type="table",

        )

        self.add_section(

            report,

            "Tools",

            tools,

            section_type="list",

        )

        self.add_section(

            report,

            "Platforms",

            platforms,

            section_type="list",

        )

        self.add_section(

            report,

            "Frameworks",

            frameworks,

            section_type="list",

        )

        self.add_section(

            report,

            "Databases",

            databases,

            section_type="list",

        )

        return report

    # --------------------------------------------------------
    # Comprehensive report
    # --------------------------------------------------------

    def generate_comprehensive_report(
        self,
        curriculum: Any,
        industry: Any = None,
        gaps: Any = None,
        enhancements: Any = None,
        skills: Any = None,
        learning_path: Any = None,
        rag_context: Optional[str] = None,
    ) -> Report:

        report = self.create_report(

            report_type="comprehensive",

            title=(
                "PragyanAI Comprehensive "
                "Curriculum Intelligence Report"
            ),

        )

        curriculum_data = normalize_object(
            curriculum
        )

        industry_data = normalize_object(
            industry
        )

        gaps_data = normalize_object(
            gaps
        )

        enhancement_data = normalize_object(
            enhancements
        )

        skill_data = normalize_object(
            skills
        )

        learning_data = normalize_object(
            learning_path
        )

        # ----------------------------------------------------
        # Curriculum
        # ----------------------------------------------------

        self.add_section(

            report,

            "Curriculum Overview",

            curriculum_data,

            section_type="object",

        )

        # ----------------------------------------------------
        # Industry
        # ----------------------------------------------------

        if industry_data:

            self.add_section(

                report,

                "Industry Alignment",

                industry_data,

                section_type="object",

            )

        # ----------------------------------------------------
        # Gaps
        # ----------------------------------------------------

        if gaps_data:

            self.add_section(

                report,

                "Skill Gap Analysis",

                gaps_data,

                section_type="object",

            )

        # ----------------------------------------------------
        # Enhancements
        # ----------------------------------------------------

        if enhancement_data:

            self.add_section(

                report,

                "Recommended Enhancements",

                enhancement_data,

                section_type="object",

            )

        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        if skill_data:

            self.add_section(

                report,

                "Skill Intelligence",

                skill_data,

                section_type="object",

            )

        # ----------------------------------------------------
        # Learning path
        # ----------------------------------------------------

        if learning_data:

            self.add_section(

                report,

                "Recommended Learning Path",

                learning_data,

                section_type="object",

            )

        # ----------------------------------------------------
        # RAG
        # ----------------------------------------------------

        if rag_context:

            self.add_section(

                report,

                "Retrieved Evidence",

                truncate(

                    rag_context,

                    self.config.max_context_chars,

                ),

                section_type="text",

            )

        report.executive_summary = (

            "This comprehensive report combines "
            "curriculum intelligence, industry "
            "alignment, skill-gap analysis, "
            "enhancement recommendations and "
            "learning-path recommendations."

        )

        report.overall_score = (

            self._calculate_overall_score(

                industry_data,

                gaps_data,

            )

        )

        return report


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# CONTEXT + SCORING + SERIALIZATION
# ============================================================


class ReportGenerator(ReportGenerator):

    # --------------------------------------------------------
    # Build LLM context
    # --------------------------------------------------------

    def _build_context(
        self,
        *objects: Any,
    ) -> str:

        parts = []

        remaining = (
            self.config.max_context_chars
        )

        for index, obj in enumerate(
            objects,
            start=1,
        ):

            if obj is None:

                continue

            if isinstance(
                obj,
                str,
            ):

                text = obj

            else:

                try:

                    text = json.dumps(

                        normalize_object(
                            obj
                        ),

                        indent=2,

                        ensure_ascii=False,

                    )

                except Exception:

                    text = safe_string(
                        obj
                    )

            if not text:

                continue

            text = truncate(

                text,

                min(
                    remaining,
                    10000,
                ),

            )

            parts.append(

                f"DATASET {index}\n"
                f"----------------\n"
                +
                text

            )

            remaining -= len(
                text
            )

            if remaining <= 0:

                break

        return "\n\n".join(
            parts
        )

    # --------------------------------------------------------
    # Fallback summary
    # --------------------------------------------------------

    @staticmethod
    def _fallback_summary(
        gap_data: Mapping[str, Any],
        industry_data: Mapping[str, Any],
    ) -> str:

        missing = len(

            safe_list(

                gap_data.get(
                    "critical_gaps"
                )

            )

        )

        alignment = (

            industry_data.get(
                "overall_alignment_score"
            )

            or

            industry_data.get(
                "alignment_score"
            )

        )

        if alignment is not None:

            return (

                "The curriculum has an industry "
                f"alignment score of "
                f"{format_score(alignment)} "
                f"with {missing} critical skill gaps."

            )

        return (

            f"The analysis identified "
            f"{missing} critical curriculum gaps."

        )

    # --------------------------------------------------------
    # Calculate score
    # --------------------------------------------------------

    @staticmethod
    def _calculate_overall_score(
        industry_data: Mapping[str, Any],
        gap_data: Mapping[str, Any],
    ) -> Optional[float]:

        alignment = (

            industry_data.get(
                "overall_alignment_score"
            )

            or

            industry_data.get(
                "alignment_score"
            )

        )

        if alignment is not None:

            value = safe_float(
                alignment
            )

            if value is not None:

                return value

        gap_score = safe_float(

            gap_data.get(
                "overall_gap_score"
            )

        )

        if gap_score is not None:

            # A gap score is generally interpreted
            # as "higher gap = worse".
            if 0 <= gap_score <= 1:

                return 1.0 - gap_score

            if 0 <= gap_score <= 100:

                return 100.0 - gap_score

        return None

    # --------------------------------------------------------
    # To dictionary
    # --------------------------------------------------------

    @staticmethod
    def to_dict(
        report: Report,
    ) -> Dict[str, Any]:

        return {

            "title":
                report.title,

            "report_type":
                report.report_type,

            "generated_at":
                report.generated_at,

            "executive_summary":
                report.executive_summary,

            "overall_score":
                report.overall_score,

            "sections": [

                {

                    "title":
                        section.title,

                    "content":
                        normalize_object(
                            section.content
                        ),

                    "order":
                        section.order,

                    "section_type":
                        section.section_type,

                    "metadata":
                        section.metadata,

                }

                for section
                in report.sections

            ],

            "recommendations":
                normalize_object(

                    report.recommendations

                ),

            "sources":
                normalize_object(
                    report.sources
                ),

            "metadata":
                normalize_object(
                    report.metadata
                ),

        }

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    def to_json(
        self,
        report: Report,
        indent: int = 2,
    ) -> str:

        return json.dumps(

            self.to_dict(
                report
            ),

            indent=indent,

            ensure_ascii=False,

        )

    # --------------------------------------------------------
    # Markdown
    # --------------------------------------------------------

    def to_markdown(
        self,
        report: Report,
    ) -> str:

        lines = []

        lines.append(

            f"# {report.title}"

        )

        lines.append("")

        lines.append(

            f"**Report Type:** "
            f"{report.report_type}"

        )

        lines.append(

            f"**Generated:** "
            f"{report.generated_at}"

        )

        if (
            self.config.include_scores
            and
            report.overall_score is not None
        ):

            lines.append(

                f"**Overall Score:** "
                f"{format_score(report.overall_score)}"

            )

        lines.append("")

        if report.executive_summary:

            lines.append(

                "## Executive Summary"

            )

            lines.append("")

            lines.append(

                report.executive_summary

            )

            lines.append("")

        for section in report.sections:

            lines.append(

                f"## {section.title}"

            )

            lines.append("")

            content = section.content

            if section.section_type == "list":

                for item in safe_list(
                    content
                ):

                    if isinstance(
                        item,
                        Mapping,
                    ):

                        lines.append(

                            "- "
                            +
                            self._format_mapping(
                                item
                            )

                        )

                    else:

                        lines.append(

                            "- "
                            +
                            safe_string(
                                item
                            )

                        )

            elif section.section_type == "table":

                lines.extend(

                    self._markdown_table(
                        content
                    )

                )

            elif section.section_type == "object":

                lines.append(

                    "```json"

                )

                lines.append(

                    json.dumps(

                        normalize_object(
                            content
                        ),

                        indent=2,

                        ensure_ascii=False,

                    )

                )

                lines.append(
                    "```"
                )

            else:

                lines.append(

                    safe_string(
                        content
                    )

                )

            lines.append("")

        if (
            self.config.include_recommendations
            and
            report.recommendations
        ):

            lines.append(

                "## Priority Recommendations"

            )

            lines.append("")

            for item in report.recommendations:

                if isinstance(
                    item,
                    Mapping,
                ):

                    lines.append(

                        "- "
                        +
                        self._format_mapping(
                            item
                        )

                    )

                else:

                    lines.append(

                        "- "
                        +
                        safe_string(
                            item
                        )

                    )

            lines.append("")

        if (
            self.config.include_rag_sources
            and
            report.sources
        ):

            lines.append(
                "## Sources"
            )

            lines.append("")

            for source in report.sources:

                lines.append(

                    "- "
                    +
                    self._format_mapping(
                        source
                    )

                )

        return "\n".join(
            lines
        )

    # --------------------------------------------------------
    # Format mapping
    # --------------------------------------------------------

    @staticmethod
    def _format_mapping(
        value: Mapping[str, Any],
    ) -> str:

        parts = []

        for key, val in value.items():

            if isinstance(
                val,
                (
                    list,
                    dict,
                ),
            ):

                val = json.dumps(

                    val,

                    ensure_ascii=False,

                )

            parts.append(

                f"**{key}:** {val}"

            )

        return "; ".join(
            parts
        )

    # --------------------------------------------------------
    # Markdown table
    # --------------------------------------------------------

    def _markdown_table(
        self,
        content: Any,
    ) -> List[str]:

        rows = safe_list(
            content
        )

        if not rows:

            return [
                "No data available."
            ]

        normalized = []

        for row in rows:

            if isinstance(
                row,
                Mapping,
            ):

                normalized.append(
                    dict(row)
                )

            else:

                normalized.append({

                    "Value":
                        safe_string(
                            row
                        )

                })

        columns = []

        for row in normalized:

            for key in row.keys():

                if key not in columns:

                    columns.append(
                        key
                    )

        if not columns:

            return [
                "No data available."
            ]

        lines = []

        lines.append(

            "| "
            +
            " | ".join(
                columns
            )
            +
            " |"

        )

        lines.append(

            "| "
            +
            " | ".join(
                "---"
                for _
                in columns
            )
            +
            " |"

        )

        for row in normalized:

            values = []

            for column in columns:

                value = row.get(
                    column,
                    "",
                )

                value = safe_string(
                    value
                ).replace(
                    "|",
                    "\\|"
                )

                values.append(
                    value
                )

            lines.append(

                "| "
                +
                " | ".join(
                    values
                )
                +
                " |"

            )

        return lines

    # --------------------------------------------------------
    # HTML
    # --------------------------------------------------------

    def to_html(
        self,
        report: Report,
    ) -> str:

        markdown = self.to_markdown(
            report
        )

        escaped = html.escape(
            markdown
        )

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(report.title)}</title>
<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 1100px;
    margin: 40px auto;
    padding: 0 24px;
    line-height: 1.6;
}}
pre {{
    white-space: pre-wrap;
}}
h1 {{
    margin-bottom: 8px;
}}
</style>
</head>
<body>
<pre>{escaped}</pre>
</body>
</html>
"""

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    def save(
        self,
        report: Report,
        path: Union[
            str,
            Path,
        ],
        format: Optional[str] = None,
    ) -> Path:

        path = Path(
            path
        )

        output_format = (

            format
            or
            path.suffix
            .lower()
            .lstrip(".")

            or
            self.config.output_format

        )

        path.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        if output_format == "json":

            content = self.to_json(
                report
            )

        elif output_format in {

            "html",
            "htm",

        }:

            content = self.to_html(
                report
            )

        else:

            content = self.to_markdown(
                report
            )

        path.write_text(

            content,

            encoding="utf-8",

        )

        return path


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# FACTORIES + PUBLIC API + SELF TEST
# ============================================================


# ============================================================
# CREATE GENERATOR
# ============================================================

def create_report_generator(
    config: Optional[
        ReportConfig
    ] = None,
    llm_service: Optional[
        GroqService
    ] = None,
) -> ReportGenerator:

    return ReportGenerator(

        config=config,

        llm_service=llm_service,

    )


# ============================================================
# GENERATE EXECUTIVE REPORT
# ============================================================

def generate_executive_report(
    curriculum: Any,
    industry: Any = None,
    gaps: Any = None,
    enhancements: Any = None,
    rag_context: Optional[str] = None,
    generator: Optional[
        ReportGenerator
    ] = None,
) -> Report:

    generator = (

        generator
        or
        create_report_generator()

    )

    return generator.generate_executive_report(

        curriculum=curriculum,

        industry=industry,

        gap_analysis=gaps,

        enhancements=enhancements,

        rag_context=rag_context,

    )


# ============================================================
# GENERATE GAP REPORT
# ============================================================

def generate_gap_report(
    gaps: Any,
    curriculum: Any = None,
    industry: Any = None,
    generator: Optional[
        ReportGenerator
    ] = None,
) -> Report:

    generator = (

        generator
        or
        create_report_generator()

    )

    return generator.generate_gap_report(

        gap_analysis=gaps,

        curriculum=curriculum,

        industry=industry,

    )


# ============================================================
# GENERATE INDUSTRY REPORT
# ============================================================

def generate_industry_report(
    alignment: Any,
    curriculum: Any = None,
    job_description: Any = None,
    generator: Optional[
        ReportGenerator
    ] = None,
) -> Report:

    generator = (

        generator
        or
        create_report_generator()

    )

    return generator.generate_industry_report(

        alignment=alignment,

        curriculum=curriculum,

        job_description=job_description,

    )


# ============================================================
# GENERATE ENHANCEMENT REPORT
# ============================================================

def generate_enhancement_report(
    enhancements: Any,
    generator: Optional[
        ReportGenerator
    ] = None,
) -> Report:

    generator = (

        generator
        or
        create_report_generator()

    )

    return generator.generate_enhancement_report(

        enhancements=enhancements

    )


# ============================================================
# GENERATE LEARNING PATH REPORT
# ============================================================

def generate_learning_path_report(
    learning_path: Any,
    generator: Optional[
        ReportGenerator
    ] = None,
) -> Report:

    generator = (

        generator
        or
        create_report_generator()

    )

    return generator.generate_learning_path_report(

        learning_path=learning_path

    )


# ============================================================
# GENERATE COMPREHENSIVE REPORT
# ============================================================

def generate_comprehensive_report(
    curriculum: Any,
    industry: Any = None,
    gaps: Any = None,
    enhancements: Any = None,
    skills: Any = None,
    learning_path: Any = None,
    rag_context: Optional[str] = None,
    generator: Optional[
        ReportGenerator
    ] = None,
) -> Report:

    generator = (

        generator
        or
        create_report_generator()

    )

    return generator.generate_comprehensive_report(

        curriculum=curriculum,

        industry=industry,

        gaps=gaps,

        enhancements=enhancements,

        skills=skills,

        learning_path=learning_path,

        rag_context=rag_context,

    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "REPORT_GENERATOR_VERSION",

    "ReportConfig",

    "ReportSection",

    "Report",

    "ReportGenerator",

    "create_report_generator",

    "generate_executive_report",

    "generate_gap_report",

    "generate_industry_report",

    "generate_enhancement_report",

    "generate_learning_path_report",

    "generate_comprehensive_report",

    "safe_string",

    "safe_float",

    "safe_list",

    "to_dict",

    "normalize_object",

    "truncate",

    "format_score",

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
        "PRAGYANAI REPORT GENERATOR SELF TEST"
    )

    print(
        "============================================"
    )

    # --------------------------------------------------------
    # Demo data
    # --------------------------------------------------------

    curriculum = {

        "name":
            "AI Engineering Curriculum",

        "duration":
            "12 Months",

        "skills": [

            "Python",

            "Machine Learning",

            "Deep Learning",

            "Generative AI",

            "LangChain",

        ],

    }

    industry = {

        "overall_alignment_score":
            0.78,

        "matching_skills": [

            "Python",

            "Machine Learning",

            "Generative AI",

        ],

        "missing_skills": [

            "Kubernetes",

            "MLOps",

            "Production Monitoring",

        ],

    }

    gaps = {

        "overall_gap_score":
            0.22,

        "critical_gaps": [

            {

                "skill":
                    "MLOps",

                "category":
                    "Production AI",

                "severity":
                    "High",

                "reason":
                    "Limited production deployment coverage",

            }

        ],

        "moderate_gaps": [

            {

                "skill":
                    "Kubernetes",

                "category":
                    "Cloud",

                "severity":
                    "Medium",

            }

        ],

        "minor_gaps": [],

        "missing_tools": [

            "MLflow",

            "Kubernetes",

        ],

        "missing_projects": [

            "Production RAG Application",

        ],

        "missing_concepts": [

            "LLMOps",

        ],

    }

    enhancements = {

        "recommendations": [

            {

                "area":
                    "MLOps",

                "skill":
                    "MLflow",

                "priority":
                    "High",

                "recommended_change":
                    "Add an end-to-end MLOps module",

            }

        ],

        "new_modules": [

            {

                "module":
                    "Production GenAI",

                "topics": [

                    "LLMOps",

                    "Evaluation",

                    "Monitoring",

                ],

                "projects": [

                    "Enterprise RAG System",

                ],

            }

        ],

    }

    # --------------------------------------------------------
    # Create generator without requiring live LLM
    # --------------------------------------------------------

    config = ReportConfig(

        use_llm_narrative=False,

        output_format="markdown",

    )

    generator = ReportGenerator(

        config=config,

        llm_service=None,

    )

    # --------------------------------------------------------
    # Generate comprehensive report
    # --------------------------------------------------------

    report = generator.generate_comprehensive_report(

        curriculum=curriculum,

        industry=industry,

        gaps=gaps,

        enhancements=enhancements,

    )

    # --------------------------------------------------------
    # Print Markdown
    # --------------------------------------------------------

    print(
        "\n"
        "GENERATED REPORT"
    )

    print(
        "--------------------------------------------"
    )

    print(

        generator.to_markdown(
            report
        )

    )

    # --------------------------------------------------------
    # Print JSON
    # --------------------------------------------------------

    print(
        "\n"
        "REPORT JSON"
    )

    print(
        "--------------------------------------------"
    )

    print(

        generator.to_json(
            report
        )

    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\n"
        "============================================"
    )

    print(
        "REPORT GENERATOR TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF reports/generator.py
# ============================================================
