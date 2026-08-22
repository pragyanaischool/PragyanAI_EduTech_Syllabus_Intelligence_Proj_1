# ============================================================
# agents/state.py
# CHUNK 1/10
#
# SHARED AGENT STATE
#
# Purpose:
#   Central state definitions for the Curriculum Intelligence
#   Agentic Pipeline.
#
# Pipeline:
#
#   JD / Curriculum
#        ↓
#   JD Parser
#        ↓
#   Skill Matcher
#        ↓
#   Gap Agent
#        ↓
#   Enhancement Agent
#        ↓
#   Curriculum Optimizer
#        ↓
#   Reports
#
# Designed to work with:
#
#   - LangGraph
#   - Streamlit
#   - Pydantic
#   - Dataclasses
#   - Plain Python
#
# LangGraph is OPTIONAL.
#
# ============================================================

from __future__ import annotations

import copy
import json
import logging

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    TypedDict,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(
    __name__
)


# ============================================================
# VERSION
# ============================================================

STATE_VERSION = "1.0.0"


# ============================================================
# WORKFLOW STATUS
# ============================================================

STATUS_IDLE = "idle"

STATUS_INITIALIZED = "initialized"

STATUS_PARSING = "parsing"

STATUS_MATCHING = "matching"

STATUS_ANALYZING_GAPS = "analyzing_gaps"

STATUS_ENHANCING = "enhancing"

STATUS_VALIDATING = "validating"

STATUS_REPORTING = "reporting"

STATUS_COMPLETED = "completed"

STATUS_FAILED = "failed"


# ============================================================
# WORKFLOW STAGES
# ============================================================

STAGE_INPUT = "input"

STAGE_JD_PARSING = "jd_parsing"

STAGE_SKILL_EXTRACTION = "skill_extraction"

STAGE_SKILL_MATCHING = "skill_matching"

STAGE_GAP_ANALYSIS = "gap_analysis"

STAGE_ENHANCEMENT = "enhancement"

STAGE_VALIDATION = "validation"

STAGE_REPORTING = "reporting"

STAGE_COMPLETED = "completed"


# ============================================================
# GENERIC STATUS MODEL
# ============================================================

@dataclass
class StageStatus:

    stage: str

    status: str = STATUS_IDLE

    started_at: Optional[str] = None

    completed_at: Optional[str] = None

    error: Optional[str] = None

    message: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# ERROR MODEL
# ============================================================

@dataclass
class AgentError:

    stage: str

    message: str

    error_type: str = "RuntimeError"

    timestamp: str = ""

    recoverable: bool = True

    details: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# INPUT STATE
# ============================================================


# ============================================================
# INPUT DATA
# ============================================================

@dataclass
class InputState:

    # --------------------------------------------------------
    # Job Description
    # --------------------------------------------------------

    jd_text: str = ""

    jd_source: str = ""

    jd_filename: str = ""

    jd_url: str = ""

    # --------------------------------------------------------
    # Curriculum
    # --------------------------------------------------------

    curriculum_text: str = ""

    curriculum_source: str = ""

    curriculum_filename: str = ""

    # --------------------------------------------------------
    # Student / Candidate
    # --------------------------------------------------------

    candidate_name: str = ""

    candidate_id: str = ""

    candidate_skills: List[str] = field(
        default_factory=list
    )

    candidate_tools: List[str] = field(
        default_factory=list
    )

    candidate_experience: List[str] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Role
    # --------------------------------------------------------

    target_role: str = ""

    target_company: str = ""

    target_domain: str = ""

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    target_readiness: float = 90.0

    minimum_match_threshold: float = 0.65

    enable_llm: bool = True

    enable_taxonomy: bool = True

    enable_project_generation: bool = True

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# DOCUMENT INPUT
# ============================================================

@dataclass
class DocumentInput:

    filename: str = ""

    file_type: str = ""

    source: str = ""

    content: str = ""

    page_count: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CURRICULUM INPUT
# ============================================================

@dataclass
class CurriculumInput:

    curriculum_id: str = ""

    title: str = ""

    description: str = ""

    modules: List[Dict[str, Any]] = field(
        default_factory=list
    )

    skills: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    concepts: List[str] = field(
        default_factory=list
    )

    projects: List[Dict[str, Any]] = field(
        default_factory=list
    )

    assessments: List[Dict[str, Any]] = field(
        default_factory=list
    )

    total_hours: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# JD + MATCHING STATE
# ============================================================


# ============================================================
# JD STATE
# ============================================================

@dataclass
class JDState:

    title: str = ""

    company: str = ""

    role: str = ""

    location: str = ""

    experience_min: float = 0.0

    experience_max: float = 0.0

    education: List[str] = field(
        default_factory=list
    )

    required_skills: List[str] = field(
        default_factory=list
    )

    preferred_skills: List[str] = field(
        default_factory=list
    )

    technologies: List[str] = field(
        default_factory=list
    )

    domains: List[str] = field(
        default_factory=list
    )

    responsibilities: List[str] = field(
        default_factory=list
    )

    qualifications: List[str] = field(
        default_factory=list
    )

    keywords: List[str] = field(
        default_factory=list
    )

    raw_text: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# MATCH RESULT
# ============================================================

@dataclass
class MatchState:

    required_matches: List[Dict[str, Any]] = field(
        default_factory=list
    )

    preferred_matches: List[Dict[str, Any]] = field(
        default_factory=list
    )

    partial_matches: List[Dict[str, Any]] = field(
        default_factory=list
    )

    missing_matches: List[Dict[str, Any]] = field(
        default_factory=list
    )

    covered_skills: List[str] = field(
        default_factory=list
    )

    partial_skills: List[str] = field(
        default_factory=list
    )

    missing_skills: List[str] = field(
        default_factory=list
    )

    required_coverage: float = 0.0

    preferred_coverage: float = 0.0

    overall_coverage: float = 0.0

    readiness_score: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SKILL EVIDENCE
# ============================================================

@dataclass
class SkillEvidence:

    skill: str

    source: str

    evidence: str = ""

    confidence: float = 0.0

    proficiency: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# GAP + ENHANCEMENT STATE
# ============================================================


# ============================================================
# GAP STATE
# ============================================================

@dataclass
class GapState:

    # --------------------------------------------------------
    # Skill gaps
    # --------------------------------------------------------

    skill_gaps: List[Dict[str, Any]] = field(
        default_factory=list
    )

    concept_gaps: List[Dict[str, Any]] = field(
        default_factory=list
    )

    tool_gaps: List[Dict[str, Any]] = field(
        default_factory=list
    )

    category_gaps: List[Dict[str, Any]] = field(
        default_factory=list
    )

    experience_gaps: List[Dict[str, Any]] = field(
        default_factory=list
    )

    proficiency_gaps: List[Dict[str, Any]] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Priority
    # --------------------------------------------------------

    critical_gaps: List[str] = field(
        default_factory=list
    )

    high_priority_gaps: List[str] = field(
        default_factory=list
    )

    medium_priority_gaps: List[str] = field(
        default_factory=list
    )

    low_priority_gaps: List[str] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    total_gaps: int = 0

    critical_count: int = 0

    high_count: int = 0

    medium_count: int = 0

    low_count: int = 0

    readiness_score: float = 0.0

    readiness_band: str = ""

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# ENHANCEMENT STATE
# ============================================================

@dataclass
class EnhancementState:

    enhancements: List[Dict[str, Any]] = field(
        default_factory=list
    )

    modules: List[Dict[str, Any]] = field(
        default_factory=list
    )

    topics: List[Dict[str, Any]] = field(
        default_factory=list
    )

    tools: List[Dict[str, Any]] = field(
        default_factory=list
    )

    projects: List[Dict[str, Any]] = field(
        default_factory=list
    )

    case_studies: List[Dict[str, Any]] = field(
        default_factory=list
    )

    assessments: List[Dict[str, Any]] = field(
        default_factory=list
    )

    learning_outcomes: List[str] = field(
        default_factory=list
    )

    recommended_sequence: List[str] = field(
        default_factory=list
    )

    estimated_total_hours: float = 0.0

    target_readiness: float = 90.0

    projected_readiness: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# VALIDATION + REPORT STATE
# ============================================================


# ============================================================
# VALIDATION RESULT
# ============================================================

@dataclass
class ValidationState:

    valid: bool = True

    score: float = 0.0

    curriculum_quality_score: float = 0.0

    industry_alignment_score: float = 0.0

    skill_coverage_score: float = 0.0

    practical_coverage_score: float = 0.0

    project_coverage_score: float = 0.0

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    recommendations: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# REPORT STATE
# ============================================================

@dataclass
class ReportState:

    report_title: str = ""

    executive_summary: str = ""

    readiness_summary: str = ""

    key_findings: List[str] = field(
        default_factory=list
    )

    critical_gaps: List[str] = field(
        default_factory=list
    )

    recommended_actions: List[str] = field(
        default_factory=list
    )

    curriculum_changes: List[str] = field(
        default_factory=list
    )

    module_recommendations: List[str] = field(
        default_factory=list
    )

    project_recommendations: List[str] = field(
        default_factory=list
    )

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    charts: List[Dict[str, Any]] = field(
        default_factory=list
    )

    tables: List[Dict[str, Any]] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# COMPLETE WORKFLOW STATE
# ============================================================


# ============================================================
# AGENT WORKFLOW STATE
# ============================================================

@dataclass
class AgentState:

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    workflow_id: str = ""

    session_id: str = ""

    user_id: str = ""

    created_at: str = ""

    updated_at: str = ""

    state_version: str = STATE_VERSION

    # --------------------------------------------------------
    # Workflow
    # --------------------------------------------------------

    status: str = STATUS_IDLE

    current_stage: str = STAGE_INPUT

    progress: float = 0.0

    iteration: int = 0

    # --------------------------------------------------------
    # Inputs
    # --------------------------------------------------------

    input: InputState = field(
        default_factory=InputState
    )

    jd: JDState = field(
        default_factory=JDState
    )

    curriculum: CurriculumInput = field(
        default_factory=CurriculumInput
    )

    # --------------------------------------------------------
    # Matching
    # --------------------------------------------------------

    match: MatchState = field(
        default_factory=MatchState
    )

    skill_evidence: List[SkillEvidence] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Gap analysis
    # --------------------------------------------------------

    gap: GapState = field(
        default_factory=GapState
    )

    # --------------------------------------------------------
    # Enhancement
    # --------------------------------------------------------

    enhancement: EnhancementState = field(
        default_factory=EnhancementState
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    validation: ValidationState = field(
        default_factory=ValidationState
    )

    # --------------------------------------------------------
    # Reporting
    # --------------------------------------------------------

    report: ReportState = field(
        default_factory=ReportState
    )

    # --------------------------------------------------------
    # Errors
    # --------------------------------------------------------

    errors: List[AgentError] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Arbitrary data
    # --------------------------------------------------------

    data: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# STATE LIFECYCLE
# ============================================================


# ============================================================
# CURRENT UTC
# ============================================================

def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# CREATE WORKFLOW STATE
# ============================================================

def create_state(
    workflow_id: str = "",
    session_id: str = "",
    user_id: str = "",
    **kwargs: Any,
) -> AgentState:

    now = utc_now()

    state = AgentState(

        workflow_id=workflow_id,

        session_id=session_id,

        user_id=user_id,

        created_at=now,

        updated_at=now,

        state_version=STATE_VERSION,

        status=STATUS_INITIALIZED,

    )

    # --------------------------------------------------------
    # Input fields
    # --------------------------------------------------------

    for key, value in kwargs.items():

        if hasattr(
            state.input,
            key,
        ):

            setattr(

                state.input,

                key,

                value,

            )

        elif hasattr(
            state,
            key,
        ):

            setattr(

                state,

                key,

                value,

            )

        else:

            state.data[
                key
            ] = value

    return state


# ============================================================
# UPDATE TIMESTAMP
# ============================================================

def touch_state(
    state: AgentState,
) -> AgentState:

    state.updated_at = utc_now()

    return state


# ============================================================
# SET STATUS
# ============================================================

def set_status(
    state: AgentState,
    status: str,
    stage: Optional[str] = None,
    message: str = "",
) -> AgentState:

    state.status = status

    if stage is not None:

        state.current_stage = stage

    if message:

        state.metadata[
            "status_message"
        ] = message

    touch_state(
        state
    )

    return state


# ============================================================
# START STAGE
# ============================================================

def start_stage(
    state: AgentState,
    stage: str,
    message: str = "",
) -> AgentState:

    set_status(

        state,

        STATUS_PARSING
        if stage == STAGE_JD_PARSING

        else STATUS_MATCHING
        if stage == STAGE_SKILL_MATCHING

        else STATUS_ANALYZING_GAPS
        if stage == STAGE_GAP_ANALYSIS

        else STATUS_ENHANCING
        if stage == STAGE_ENHANCEMENT

        else STATUS_VALIDATING
        if stage == STAGE_VALIDATION

        else STATUS_REPORTING
        if stage == STAGE_REPORTING

        else STATUS_INITIALIZED,

        stage=stage,

        message=message,

    )

    state.metadata[
        f"{stage}_started_at"
    ] = utc_now()

    return state


# ============================================================
# COMPLETE STAGE
# ============================================================

def complete_stage(
    state: AgentState,
    stage: str,
    message: str = "",
) -> AgentState:

    state.metadata[
        f"{stage}_completed_at"
    ] = utc_now()

    if message:

        state.metadata[
            f"{stage}_message"
        ] = message

    touch_state(
        state
    )

    return state


# ============================================================
# UPDATE PROGRESS
# ============================================================

def update_progress(
    state: AgentState,
    progress: float,
) -> AgentState:

    state.progress = max(

        0.0,

        min(
            100.0,
            float(
                progress
            ),
        ),

    )

    touch_state(
        state
    )

    return state


# ============================================================
# INCREMENT ITERATION
# ============================================================

def increment_iteration(
    state: AgentState,
) -> AgentState:

    state.iteration += 1

    touch_state(
        state
    )

    return state


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# ERROR HANDLING + SERIALIZATION
# ============================================================


# ============================================================
# ADD ERROR
# ============================================================

def add_error(
    state: AgentState,
    stage: str,
    error: Exception | str,
    recoverable: bool = True,
    details: Optional[
        Dict[str, Any]
    ] = None,
) -> AgentState:

    if isinstance(
        error,
        Exception,
    ):

        message = str(
            error
        )

        error_type = type(
            error
        ).__name__

    else:

        message = str(
            error
        )

        error_type = "RuntimeError"

    state.errors.append(

        AgentError(

            stage=stage,

            message=message,

            error_type=error_type,

            timestamp=utc_now(),

            recoverable=recoverable,

            details=details
            or
            {},

        )

    )

    state.status = STATUS_FAILED

    touch_state(
        state
    )

    return state


# ============================================================
# ADD WARNING
# ============================================================

def add_warning(
    state: AgentState,
    message: str,
) -> AgentState:

    message = str(
        message
    ).strip()

    if message:

        state.warnings.append(
            message
        )

    touch_state(
        state
    )

    return state


# ============================================================
# HAS ERRORS
# ============================================================

def has_errors(
    state: AgentState,
) -> bool:

    return bool(
        state.errors
    )


# ============================================================
# HAS RECOVERABLE ERRORS
# ============================================================

def has_recoverable_errors(
    state: AgentState,
) -> bool:

    return any(

        error.recoverable

        for error
        in state.errors

    )


# ============================================================
# STATE → DICT
# ============================================================

def state_to_dict(
    state: AgentState,
) -> Dict[str, Any]:

    return asdict(
        state
    )


# ============================================================
# STATE → JSON
# ============================================================

def state_to_json(
    state: AgentState,
    indent: int = 2,
) -> str:

    return json.dumps(

        state_to_dict(
            state
        ),

        indent=indent,

        ensure_ascii=False,

        default=str,

    )


# ============================================================
# COPY STATE
# ============================================================

def copy_state(
    state: AgentState,
) -> AgentState:

    return copy.deepcopy(
        state
    )


# ============================================================
# UPDATE STATE DATA
# ============================================================

def update_data(
    state: AgentState,
    **kwargs: Any,
) -> AgentState:

    state.data.update(
        kwargs
    )

    touch_state(
        state
    )

    return state


# ============================================================
# GET DATA
# ============================================================

def get_data(
    state: AgentState,
    key: str,
    default: Any = None,
) -> Any:

    return state.data.get(

        key,

        default,

    )


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# LANGGRAPH COMPATIBILITY
# ============================================================


# ============================================================
# LANGGRAPH STATE
#
# TypedDict version is useful when constructing a StateGraph.
#
# Values are intentionally broad because different nodes may
# return dataclasses, dictionaries, or plain lists.
# ============================================================

class AgentGraphState(
    TypedDict,
    total=False,
):

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    workflow_id: str

    session_id: str

    user_id: str

    # --------------------------------------------------------
    # Workflow
    # --------------------------------------------------------

    status: str

    current_stage: str

    progress: float

    iteration: int

    # --------------------------------------------------------
    # Inputs
    # --------------------------------------------------------

    jd_text: str

    curriculum_text: str

    target_role: str

    target_company: str

    candidate_skills: List[str]

    candidate_tools: List[str]

    target_readiness: float

    # --------------------------------------------------------
    # Structured data
    # --------------------------------------------------------

    jd_profile: Any

    curriculum: Any

    skill_match_report: Any

    gap_analysis: Any

    enhancement_plan: Any

    validation_result: Any

    report: Any

    # --------------------------------------------------------
    # Convenience outputs
    # --------------------------------------------------------

    skill_gaps: List[Any]

    critical_gaps: List[Any]

    curriculum_enhancements: List[Any]

    recommended_projects: List[Any]

    recommended_modules: List[Any]

    readiness_score: float

    # --------------------------------------------------------
    # Errors
    # --------------------------------------------------------

    errors: List[Any]

    warnings: List[str]

    # --------------------------------------------------------
    # Generic
    # --------------------------------------------------------

    data: Dict[str, Any]

    metadata: Dict[str, Any]


# ============================================================
# AGENT STATE → GRAPH STATE
# ============================================================

def to_graph_state(
    state: AgentState,
) -> AgentGraphState:

    return {

        "workflow_id":
            state.workflow_id,

        "session_id":
            state.session_id,

        "user_id":
            state.user_id,

        "status":
            state.status,

        "current_stage":
            state.current_stage,

        "progress":
            state.progress,

        "iteration":
            state.iteration,

        "jd_text":
            state.input.jd_text,

        "curriculum_text":
            state.input.curriculum_text,

        "target_role":
            state.input.target_role,

        "target_company":
            state.input.target_company,

        "candidate_skills":
            state.input.candidate_skills,

        "candidate_tools":
            state.input.candidate_tools,

        "target_readiness":
            state.input.target_readiness,

        "jd_profile":
            state.jd,

        "curriculum":
            state.curriculum,

        "skill_match_report":
            state.match,

        "gap_analysis":
            state.gap,

        "enhancement_plan":
            state.enhancement,

        "validation_result":
            state.validation,

        "report":
            state.report,

        "skill_gaps":
            state.gap.skill_gaps,

        "critical_gaps":
            state.gap.critical_gaps,

        "curriculum_enhancements":
            state.enhancement.enhancements,

        "recommended_projects":
            state.enhancement.projects,

        "recommended_modules":
            state.enhancement.modules,

        "readiness_score":
            state.gap.readiness_score,

        "errors": [

            asdict(
                error
            )

            for error
            in state.errors

        ],

        "warnings":
            state.warnings,

        "data":
            state.data,

        "metadata":
            state.metadata,

    }


# ============================================================
# GRAPH STATE → PARTIAL AGENT STATE
# ============================================================

def from_graph_state(
    graph_state: Mapping[str, Any],
) -> AgentState:

    state = create_state(

        workflow_id=str(

            graph_state.get(
                "workflow_id",
                "",
            )

        ),

        session_id=str(

            graph_state.get(
                "session_id",
                "",
            )

        ),

        user_id=str(

            graph_state.get(
                "user_id",
                "",
            )

        ),

    )

    # --------------------------------------------------------
    # Basic fields
    # --------------------------------------------------------

    state.status = graph_state.get(

        "status",

        STATUS_INITIALIZED,

    )

    state.current_stage = graph_state.get(

        "current_stage",

        STAGE_INPUT,

    )

    state.progress = float(

        graph_state.get(
            "progress",
            0.0,
        )

        or

        0.0

    )

    state.iteration = int(

        graph_state.get(
            "iteration",
            0,
        )

        or

        0

    )

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    state.input.jd_text = str(

        graph_state.get(
            "jd_text",
            "",
        )

        or

        ""

    )

    state.input.curriculum_text = str(

        graph_state.get(
            "curriculum_text",
            "",
        )

        or

        ""

    )

    state.input.target_role = str(

        graph_state.get(
            "target_role",
            "",
        )

        or

        ""

    )

    state.input.target_company = str(

        graph_state.get(
            "target_company",
            "",
        )

        or

        ""

    )

    state.input.candidate_skills = list(

        graph_state.get(
            "candidate_skills",
            [],
        )

        or

        []

    )

    state.input.candidate_tools = list(

        graph_state.get(
            "candidate_tools",
            [],
        )

        or

        []

    )

    state.input.target_readiness = float(

        graph_state.get(
            "target_readiness",
            90.0,
        )

        or

        90.0

    )

    # --------------------------------------------------------
    # Generic
    # --------------------------------------------------------

    state.data = dict(

        graph_state.get(
            "data",
            {},
        )

        or

        {}

    )

    state.metadata = dict(

        graph_state.get(
            "metadata",
            {},
        )

        or

        {}

    )

    state.warnings = list(

        graph_state.get(
            "warnings",
            [],
        )

        or

        []

    )

    touch_state(
        state
    )

    return state


# ============================================================
# NODE UPDATE
#
# Useful for LangGraph nodes which only need to update a few
# fields instead of returning the complete AgentState.
# ============================================================

def node_update(
    state: Mapping[str, Any],
    **updates: Any,
) -> Dict[str, Any]:

    result = dict(
        state
    )

    result.update(
        updates
    )

    result[
        "iteration"
    ] = (

        int(

            result.get(
                "iteration",
                0,
            )

        )
        +
        1

    )

    result[
        "updated_at"
    ] = utc_now()

    return result


# ============================================================
# COMPLETION UPDATE
# ============================================================

def completion_update(
    state: Mapping[str, Any],
) -> Dict[str, Any]:

    result = dict(
        state
    )

    result.update({

        "status":
            STATUS_COMPLETED,

        "current_stage":
            STAGE_COMPLETED,

        "progress":
            100.0,

        "updated_at":
            utc_now(),

    })

    return result


# ============================================================
# FAILURE UPDATE
# ============================================================

def failure_update(
    state: Mapping[str, Any],
    error: Exception | str,
    stage: str = "",
) -> Dict[str, Any]:

    if isinstance(
        error,
        Exception,
    ):

        message = str(
            error
        )

        error_type = type(
            error
        ).__name__

    else:

        message = str(
            error
        )

        error_type = "RuntimeError"

    result = dict(
        state
    )

    errors = list(

        result.get(
            "errors",
            [],
        )

        or

        []

    )

    errors.append({

        "stage":
            stage
            or
            result.get(
                "current_stage",
                "",
            ),

        "message":
            message,

        "error_type":
            error_type,

        "timestamp":
            utc_now(),

    })

    result.update({

        "status":
            STATUS_FAILED,

        "errors":
            errors,

        "updated_at":
            utc_now(),

    })

    return result


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# WORKFLOW ROUTING + VALIDATION + EXPORTS
# ============================================================


# ============================================================
# NEXT STAGE
# ============================================================

STAGE_ORDER = [

    STAGE_INPUT,

    STAGE_JD_PARSING,

    STAGE_SKILL_EXTRACTION,

    STAGE_SKILL_MATCHING,

    STAGE_GAP_ANALYSIS,

    STAGE_ENHANCEMENT,

    STAGE_VALIDATION,

    STAGE_REPORTING,

    STAGE_COMPLETED,

]


# ============================================================
# GET NEXT STAGE
# ============================================================

def next_stage(
    current_stage: str,
) -> str:

    try:

        index = STAGE_ORDER.index(
            current_stage
        )

    except ValueError:

        return STAGE_INPUT

    if index >= len(
        STAGE_ORDER
    ) - 1:

        return STAGE_COMPLETED

    return STAGE_ORDER[
        index + 1
    ]


# ============================================================
# GET PREVIOUS STAGE
# ============================================================

def previous_stage(
    current_stage: str,
) -> str:

    try:

        index = STAGE_ORDER.index(
            current_stage
        )

    except ValueError:

        return STAGE_INPUT

    if index <= 0:

        return STAGE_INPUT

    return STAGE_ORDER[
        index - 1
    ]


# ============================================================
# STAGE PROGRESS
# ============================================================

def stage_progress(
    stage: str,
) -> float:

    try:

        index = STAGE_ORDER.index(
            stage
        )

    except ValueError:

        return 0.0

    if len(
        STAGE_ORDER
    ) <= 1:

        return 100.0

    return round(

        (
            index
            /
            (
                len(
                    STAGE_ORDER
                )
                -
                1
            )
        )
        *
        100.0,

        2,

    )


# ============================================================
# VALIDATE INPUT
# ============================================================

def validate_input(
    state: AgentState,
) -> Dict[str, Any]:

    errors = []

    warnings = []

    if not state.input.jd_text.strip():

        if not state.input.jd_filename:

            errors.append(
                "Job description is missing."
            )

    if not state.input.curriculum_text.strip():

        if not state.curriculum.modules:

            if not state.curriculum.skills:

                warnings.append(

                    "Curriculum information is limited."

                )

    if not state.input.target_role:

        warnings.append(
            "Target role has not been specified."
        )

    if not state.input.candidate_skills:

        warnings.append(

            "Candidate skills have not been specified."

        )

    target = state.input.target_readiness

    if not (
        0.0
        <=
        target
        <=
        100.0
    ):

        errors.append(

            "Target readiness must be between 0 and 100."

        )

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

        "warnings":
            warnings,

    }


# ============================================================
# VALIDATE STATE
# ============================================================

def validate_state(
    state: AgentState,
) -> Dict[str, Any]:

    errors = []

    warnings = []

    # --------------------------------------------------------
    # Workflow identity
    # --------------------------------------------------------

    if not state.workflow_id:

        warnings.append(

            "workflow_id is empty."

        )

    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if not (
        0.0
        <=
        state.progress
        <=
        100.0
    ):

        errors.append(

            "Progress must be between 0 and 100."

        )

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    input_validation = validate_input(
        state
    )

    errors.extend(
        input_validation[
            "errors"
        ]
    )

    warnings.extend(
        input_validation[
            "warnings"
        ]
    )

    # --------------------------------------------------------
    # Error consistency
    # --------------------------------------------------------

    if state.errors and state.status != STATUS_FAILED:

        warnings.append(

            "State contains errors but status is not failed."

        )

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

        "warnings":
            warnings,

    }


# ============================================================
# MARK COMPLETED
# ============================================================

def mark_completed(
    state: AgentState,
) -> AgentState:

    state.status = STATUS_COMPLETED

    state.current_stage = STAGE_COMPLETED

    state.progress = 100.0

    touch_state(
        state
    )

    return state


# ============================================================
# RESET WORKFLOW
# ============================================================

def reset_state(
    state: AgentState,
) -> AgentState:

    workflow_id = state.workflow_id

    session_id = state.session_id

    user_id = state.user_id

    new_state = create_state(

        workflow_id=workflow_id,

        session_id=session_id,

        user_id=user_id,

    )

    return new_state


# ============================================================
# STATE SUMMARY
# ============================================================

def state_summary(
    state: AgentState,
) -> Dict[str, Any]:

    return {

        "workflow_id":
            state.workflow_id,

        "status":
            state.status,

        "stage":
            state.current_stage,

        "progress":
            state.progress,

        "iteration":
            state.iteration,

        "target_role":
            state.input.target_role,

        "target_company":
            state.input.target_company,

        "candidate_skill_count":
            len(
                state.input.candidate_skills
            ),

        "required_skill_count":
            len(
                state.jd.required_skills
            ),

        "skill_gap_count":
            len(
                state.gap.skill_gaps
            ),

        "critical_gap_count":
            len(
                state.gap.critical_gaps
            ),

        "enhancement_count":
            len(
                state.enhancement.enhancements
            ),

        "project_count":
            len(
                state.enhancement.projects
            ),

        "readiness_score":
            state.gap.readiness_score,

        "projected_readiness":
            state.enhancement.projected_readiness,

        "estimated_hours":
            state.enhancement.estimated_total_hours,

        "errors":
            len(
                state.errors
            ),

        "warnings":
            len(
                state.warnings
            ),

    }


# ============================================================
# STATE CAPABILITIES
# ============================================================

STATE_CAPABILITIES = [

    "shared_workflow_state",

    "jd_state",

    "curriculum_state",

    "skill_matching_state",

    "gap_analysis_state",

    "enhancement_state",

    "validation_state",

    "report_state",

    "workflow_status",

    "stage_tracking",

    "progress_tracking",

    "error_tracking",

    "warning_tracking",

    "state_serialization",

    "state_copying",

    "langgraph_compatibility",

    "workflow_routing",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "STATE_VERSION",

    # Status
    "STATUS_IDLE",

    "STATUS_INITIALIZED",

    "STATUS_PARSING",

    "STATUS_MATCHING",

    "STATUS_ANALYZING_GAPS",

    "STATUS_ENHANCING",

    "STATUS_VALIDATING",

    "STATUS_REPORTING",

    "STATUS_COMPLETED",

    "STATUS_FAILED",

    # Stages
    "STAGE_INPUT",

    "STAGE_JD_PARSING",

    "STAGE_SKILL_EXTRACTION",

    "STAGE_SKILL_MATCHING",

    "STAGE_GAP_ANALYSIS",

    "STAGE_ENHANCEMENT",

    "STAGE_VALIDATION",

    "STAGE_REPORTING",

    "STAGE_COMPLETED",

    # Models
    "StageStatus",

    "AgentError",

    "InputState",

    "DocumentInput",

    "CurriculumInput",

    "JDState",

    "MatchState",

    "SkillEvidence",

    "GapState",

    "EnhancementState",

    "ValidationState",

    "ReportState",

    "AgentState",

    "AgentGraphState",

    # State lifecycle
    "create_state",

    "touch_state",

    "set_status",

    "start_stage",

    "complete_stage",

    "update_progress",

    "increment_iteration",

    # Error handling
    "add_error",

    "add_warning",

    "has_errors",

    "has_recoverable_errors",

    # Serialization
    "state_to_dict",

    "state_to_json",

    "copy_state",

    "update_data",

    "get_data",

    # LangGraph
    "to_graph_state",

    "from_graph_state",

    "node_update",

    "completion_update",

    "failure_update",

    # Routing
    "next_stage",

    "previous_stage",

    "stage_progress",

    "mark_completed",

    "reset_state",

    # Validation
    "validate_input",

    "validate_state",

    "state_summary",

    "STATE_CAPABILITIES",

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
        "AGENT STATE SELF TEST"
    )

    print(
        "============================================"
    )

    # --------------------------------------------------------
    # Create state
    # --------------------------------------------------------

    state = create_state(

        workflow_id="demo-workflow-001",

        session_id="demo-session-001",

        target_role="Generative AI Engineer",

        target_company="Demo Company",

    )

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    state.input.jd_text = """

    Generative AI Engineer

    Requirements:
    Python
    Machine Learning
    LLM
    RAG
    LangChain
    Docker

    """

    state.input.candidate_skills = [

        "Python",

        "Machine Learning",

        "LLM",

    ]

    # --------------------------------------------------------
    # Stage progression
    # --------------------------------------------------------

    start_stage(

        state,

        STAGE_JD_PARSING,

        "Parsing job description.",

    )

    update_progress(
        state,
        stage_progress(
            STAGE_JD_PARSING
        ),
    )

    complete_stage(

        state,

        STAGE_JD_PARSING,

        "JD parsing completed.",

    )

    start_stage(

        state,

        STAGE_SKILL_MATCHING,

        "Matching skills.",

    )

    update_progress(
        state,
        stage_progress(
            STAGE_SKILL_MATCHING
        ),
    )

    complete_stage(

        state,

        STAGE_SKILL_MATCHING,

        "Skill matching completed.",

    )

    # --------------------------------------------------------
    # Add warning
    # --------------------------------------------------------

    add_warning(

        state,

        "Demo state does not contain a parsed curriculum.",

    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    validation = validate_state(
        state
    )

    print(
        "\nValidation:"
    )

    print(

        json.dumps(

            validation,

            indent=2,

        )

    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\nSummary:"
    )

    print(

        json.dumps(

            state_summary(
                state
            ),

            indent=2,

        )

    )

    # --------------------------------------------------------
    # Graph state
    # --------------------------------------------------------

    graph_state = to_graph_state(
        state
    )

    print(
        "\nGraph State Keys:"
    )

    print(
        list(
            graph_state.keys()
        )
    )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    print(
        "\nSerialized State:"
    )

    print(

        state_to_json(
            state
        )[:1000]

    )

    print(
        "\nNext Stage:"
    )

    print(
        next_stage(
            state.current_stage
        )
    )

    print(
        "\n============================================"
    )

    print(
        "AGENT STATE TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF agents/state.py
# ============================================================
