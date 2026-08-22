# ============================================================
# agents/gap_agent.py
# CHUNK 1/10
#
# GAP ANALYSIS AGENT
#
# Purpose:
#   Analyze the gap between:
#
#       Industry Job Description
#                    +
#       Current Curriculum / Student Skills
#                    ↓
#              Gap Analysis
#
# Outputs:
#
#   - Required skill gaps
#   - Preferred skill gaps
#   - Partial skill gaps
#   - Critical gaps
#   - Concept gaps
#   - Tool gaps
#   - Category gaps
#   - Priority scores
#   - Recommended learning actions
#
# Designed for:
#
#   Streamlit
#   LangGraph
#   LangChain
#   REST APIs
#   Batch processing
#   Curriculum intelligence
#
# ============================================================

from __future__ import annotations

import json
import logging
import re

from dataclasses import (
    dataclass,
    field,
    asdict,
)

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(
    __name__
)


# ============================================================
# OPTIONAL PROJECT IMPORTS
# ============================================================

try:

    from ..industry.jd_parser import (
        JDProfile,
        JDSkill,
    )

except ImportError:

    try:

        from industry.jd_parser import (
            JDProfile,
            JDSkill,
        )

    except ImportError:

        JDProfile = Any

        JDSkill = Any


try:

    from ..industry.skill_matcher import (
        SkillMatch,
        SkillMatchReport,
        SkillMatcherConfig,
        SkillGap,
        match_jd_to_candidate,
        build_skill_gaps,
        category_coverage,
        normalize_skill,
    )

except ImportError:

    try:

        from industry.skill_matcher import (
            SkillMatch,
            SkillMatchReport,
            SkillMatcherConfig,
            SkillGap,
            match_jd_to_candidate,
            build_skill_gaps,
            category_coverage,
            normalize_skill,
        )

    except ImportError:

        SkillMatch = Any

        SkillMatchReport = Any

        SkillMatcherConfig = Any

        SkillGap = Any

        match_jd_to_candidate = None

        build_skill_gaps = None

        category_coverage = None

        def normalize_skill(
            value: Any,
        ) -> str:

            return str(
                value
            ).strip().lower()


try:

    from ..industry.taxonomy import (
        get_skill_definition,
        get_skill_aliases,
        get_parent_skills,
        get_related_skills,
        get_skill_tools,
        get_skill_concepts,
        get_skill_category,
        get_role_definition,
        get_role_skills,
        get_role_core_skills,
        get_role_supporting_skills,
        search_taxonomy,
        classify_skill,
    )

except ImportError:

    try:

        from industry.taxonomy import (
            get_skill_definition,
            get_skill_aliases,
            get_parent_skills,
            get_related_skills,
            get_skill_tools,
            get_skill_concepts,
            get_skill_category,
            get_role_definition,
            get_role_skills,
            get_role_core_skills,
            get_role_supporting_skills,
            search_taxonomy,
            classify_skill,
        )

    except ImportError:

        get_skill_definition = None
        get_skill_aliases = None
        get_parent_skills = None
        get_related_skills = None
        get_skill_tools = None
        get_skill_concepts = None
        get_skill_category = None
        get_role_definition = None
        get_role_skills = None
        get_role_core_skills = None
        get_role_supporting_skills = None
        search_taxonomy = None
        classify_skill = None


# ============================================================
# VERSION
# ============================================================

GAP_AGENT_VERSION = "1.0.0"


# ============================================================
# GAP TYPES
# ============================================================

GAP_SKILL = "skill"

GAP_CONCEPT = "concept"

GAP_TOOL = "tool"

GAP_CATEGORY = "category"

GAP_EXPERIENCE = "experience"

GAP_PROFICIENCY = "proficiency"


# ============================================================
# GAP STATUS
# ============================================================

GAP_MISSING = "missing"

GAP_PARTIAL = "partial"

GAP_COVERED = "covered"


# ============================================================
# PRIORITY LEVELS
# ============================================================

PRIORITY_CRITICAL = "critical"

PRIORITY_HIGH = "high"

PRIORITY_MEDIUM = "medium"

PRIORITY_LOW = "low"


# ============================================================
# DEFAULT WEIGHTS
# ============================================================

DEFAULT_REQUIRED_WEIGHT = 1.00

DEFAULT_PREFERRED_WEIGHT = 0.60

DEFAULT_OPTIONAL_WEIGHT = 0.30

DEFAULT_CONCEPT_WEIGHT = 0.65

DEFAULT_TOOL_WEIGHT = 0.55

DEFAULT_EXPERIENCE_WEIGHT = 0.75


# ============================================================
# GAP ITEM
# ============================================================

@dataclass
class GapItem:

    skill: str

    gap_type: str = GAP_SKILL

    status: str = GAP_MISSING

    requirement_type: str = "required"

    category: str = "technical"

    similarity: float = 0.0

    importance: float = 0.0

    priority_score: float = 0.0

    priority: str = PRIORITY_MEDIUM

    candidate_evidence: List[str] = field(
        default_factory=list
    )

    related_skills: List[str] = field(
        default_factory=list
    )

    parent_skills: List[str] = field(
        default_factory=list
    )

    related_concepts: List[str] = field(
        default_factory=list
    )

    related_tools: List[str] = field(
        default_factory=list
    )

    rationale: str = ""

    recommended_action: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# GAP SUMMARY
# ============================================================

@dataclass
class GapSummary:

    total_requirements: int = 0

    covered_requirements: int = 0

    partial_requirements: int = 0

    missing_requirements: int = 0

    critical_gaps: int = 0

    high_priority_gaps: int = 0

    medium_priority_gaps: int = 0

    low_priority_gaps: int = 0

    required_coverage: float = 0.0

    preferred_coverage: float = 0.0

    overall_coverage: float = 0.0

    readiness_score: float = 0.0

    category_coverage: Dict[
        str,
        Dict[str, Any]
    ] = field(
        default_factory=dict
    )


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# INPUT NORMALIZATION
# ============================================================


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(
    value: Any,
) -> str:

    if value is None:

        return ""

    text = str(
        value
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# NORMALIZE SKILL LIST
# ============================================================

def normalize_skill_list(
    skills: Optional[
        Sequence[Any]
    ],
) -> List[str]:

    if not skills:

        return []

    result = []

    seen = set()

    for skill in skills:

        if isinstance(
            skill,
            Mapping,
        ):

            value = (

                skill.get(
                    "name"
                )

                or

                skill.get(
                    "skill"
                )

                or

                skill.get(
                    "title"
                )

                or

                ""

            )

        elif hasattr(
            skill,
            "name",
        ):

            value = skill.name

        else:

            value = skill

        value = clean_text(
            value
        )

        if not value:

            continue

        normalized = normalize_skill(
            value
        )

        if not normalized:

            continue

        if normalized in seen:

            continue

        seen.add(
            normalized
        )

        result.append(
            value
        )

    return result


# ============================================================
# CONVERT JD SKILL TO DICT
# ============================================================

def jd_skill_to_dict(
    skill: Any,
) -> Dict[str, Any]:

    if isinstance(
        skill,
        Mapping,
    ):

        return dict(
            skill
        )

    result = {

        "name":
            getattr(
                skill,
                "name",
                "",
            ),

        "normalized_name":
            getattr(
                skill,
                "normalized_name",
                "",
            ),

        "requirement_type":
            getattr(
                skill,
                "requirement_type",
                "required",
            ),

        "importance":
            getattr(
                skill,
                "importance",
                0.0,
            ),

        "category":
            getattr(
                skill,
                "category",
                "technical",
            ),

    }

    return result


# ============================================================
# EXTRACT JD SKILLS
# ============================================================

def extract_required_jd_skills(
    profile: JDProfile,
) -> List[Any]:

    skills = getattr(
        profile,
        "required_skills",
        [],
    )

    return list(
        skills
        or
        []
    )


# ============================================================
# EXTRACT PREFERRED JD SKILLS
# ============================================================

def extract_preferred_jd_skills(
    profile: JDProfile,
) -> List[Any]:

    skills = getattr(
        profile,
        "preferred_skills",
        [],
    )

    return list(
        skills
        or
        []
    )


# ============================================================
# EXTRACT TECHNOLOGIES
# ============================================================

def extract_jd_technologies(
    profile: JDProfile,
) -> List[Any]:

    technologies = getattr(
        profile,
        "technologies",
        [],
    )

    return list(
        technologies
        or
        []
    )


# ============================================================
# ALL JD REQUIREMENTS
# ============================================================

def extract_all_requirements(
    profile: JDProfile,
) -> List[Any]:

    result = []

    result.extend(
        extract_required_jd_skills(
            profile
        )
    )

    result.extend(
        extract_preferred_jd_skills(
            profile
        )
    )

    result.extend(
        extract_jd_technologies(
            profile
        )
    )

    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    output = []

    seen = set()

    for item in result:

        data = jd_skill_to_dict(
            item
        )

        name = clean_text(
            data.get(
                "name",
                "",
            )
        )

        if not name:

            continue

        key = normalize_skill(
            name
        )

        if key in seen:

            continue

        seen.add(
            key
        )

        output.append(
            item
        )

    return output


# ============================================================
# CANDIDATE SKILLS
# ============================================================

def extract_candidate_skills(
    candidate_skills: Any,
) -> List[str]:

    if candidate_skills is None:

        return []

    if isinstance(
        candidate_skills,
        Mapping,
    ):

        for key in (

            "skills",

            "candidate_skills",

            "technical_skills",

            "curriculum_skills",

        ):

            if key in candidate_skills:

                return normalize_skill_list(

                    candidate_skills[
                        key
                    ]

                )

        return []

    return normalize_skill_list(
        candidate_skills
    )


# ============================================================
# CURRICULUM MODULE SKILLS
# ============================================================

def extract_curriculum_skills(
    curriculum: Any,
) -> List[str]:

    if curriculum is None:

        return []

    if isinstance(
        curriculum,
        Mapping,
    ):

        result = []

        for key in (

            "skills",

            "skills_covered",

            "technical_skills",

            "learning_outcomes",

        ):

            result.extend(

                normalize_skill_list(

                    curriculum.get(
                        key,
                        [],
                    )

                )

            )

        return normalize_skill_list(
            result
        )

    return normalize_skill_list(
        curriculum
    )


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# TAXONOMY INTELLIGENCE
# ============================================================


# ============================================================
# SAFE CALL
# ============================================================

def safe_call(
    function: Any,
    *args: Any,
    default: Any = None,
    **kwargs: Any,
) -> Any:

    if function is None:

        return default

    try:

        return function(
            *args,
            **kwargs,
        )

    except Exception as exc:

        logger.debug(
            "Taxonomy lookup failed: %s",
            exc,
        )

        return default


# ============================================================
# SKILL CATEGORY
# ============================================================

def resolve_skill_category(
    skill: str,
) -> str:

    category = safe_call(

        get_skill_category,

        skill,

        default="technical",

    )

    return (

        clean_text(
            category
        )

        or

        "technical"

    )


# ============================================================
# SKILL RELATED SKILLS
# ============================================================

def resolve_related_skills(
    skill: str,
) -> List[str]:

    values = safe_call(

        get_related_skills,

        skill,

        default=[],

    )

    return normalize_skill_list(
        values
    )


# ============================================================
# PARENT SKILLS
# ============================================================

def resolve_parent_skills(
    skill: str,
) -> List[str]:

    values = safe_call(

        get_parent_skills,

        skill,

        default=[],

    )

    return normalize_skill_list(
        values
    )


# ============================================================
# SKILL TOOLS
# ============================================================

def resolve_skill_tools(
    skill: str,
) -> List[str]:

    values = safe_call(

        get_skill_tools,

        skill,

        default=[],

    )

    return normalize_skill_list(
        values
    )


# ============================================================
# SKILL CONCEPTS
# ============================================================

def resolve_skill_concepts(
    skill: str,
) -> List[str]:

    values = safe_call(

        get_skill_concepts,

        skill,

        default=[],

    )

    return normalize_skill_list(
        values
    )


# ============================================================
# SKILL ALIASES
# ============================================================

def resolve_skill_aliases(
    skill: str,
) -> List[str]:

    values = safe_call(

        get_skill_aliases,

        skill,

        default=[],

    )

    return normalize_skill_list(
        values
    )


# ============================================================
# SKILL INTELLIGENCE
# ============================================================

def get_skill_intelligence(
    skill: str,
) -> Dict[str, Any]:

    return {

        "skill":
            skill,

        "normalized":
            normalize_skill(
                skill
            ),

        "category":
            resolve_skill_category(
                skill
            ),

        "aliases":
            resolve_skill_aliases(
                skill
            ),

        "parent_skills":
            resolve_parent_skills(
                skill
            ),

        "related_skills":
            resolve_related_skills(
                skill
            ),

        "tools":
            resolve_skill_tools(
                skill
            ),

        "concepts":
            resolve_skill_concepts(
                skill
            ),

    }


# ============================================================
# IS RELATED
# ============================================================

def is_related_skill(
    required_skill: str,
    candidate_skill: str,
) -> bool:

    required = normalize_skill(
        required_skill
    )

    candidate = normalize_skill(
        candidate_skill
    )

    if required == candidate:

        return True

    related = {

        normalize_skill(
            item
        )

        for item
        in resolve_related_skills(
            required_skill
        )

    }

    parents = {

        normalize_skill(
            item
        )

        for item
        in resolve_parent_skills(
            required_skill
        )

    }

    return (

        candidate in related

        or

        candidate in parents

    )


# ============================================================
# FIND RELATED CANDIDATE EVIDENCE
# ============================================================

def find_related_evidence(
    required_skill: str,
    candidate_skills: Sequence[str],
) -> List[str]:

    evidence = []

    required_normalized = normalize_skill(
        required_skill
    )

    related = {

        normalize_skill(
            skill
        )

        for skill
        in (

            resolve_related_skills(
                required_skill
            )

            +

            resolve_parent_skills(
                required_skill
            )

        )

    }

    for candidate in candidate_skills:

        candidate_normalized = normalize_skill(
            candidate
        )

        if candidate_normalized == required_normalized:

            evidence.append(
                candidate
            )

        elif candidate_normalized in related:

            evidence.append(
                candidate
            )

    return evidence


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# GAP PRIORITY ENGINE
# ============================================================


# ============================================================
# REQUIREMENT WEIGHT
# ============================================================

def requirement_weight(
    requirement_type: str,
) -> float:

    requirement_type = normalize_skill(
        requirement_type
    )

    if requirement_type == "required":

        return DEFAULT_REQUIRED_WEIGHT

    if requirement_type == "preferred":

        return DEFAULT_PREFERRED_WEIGHT

    if requirement_type == "optional":

        return DEFAULT_OPTIONAL_WEIGHT

    return DEFAULT_PREFERRED_WEIGHT


# ============================================================
# STATUS SCORE
# ============================================================

def status_gap_score(
    status: str,
) -> float:

    status = normalize_skill(
        status
    )

    if status == GAP_MISSING:

        return 1.0

    if status == GAP_PARTIAL:

        return 0.5

    return 0.0


# ============================================================
# CATEGORY IMPORTANCE
# ============================================================

CATEGORY_WEIGHTS = {

    "technical":
        1.00,

    "programming":
        1.00,

    "machine_learning":
        1.00,

    "deep_learning":
        1.00,

    "generative_ai":
        1.00,

    "agentic_ai":
        1.00,

    "data_engineering":
        0.95,

    "cloud":
        0.90,

    "devops":
        0.90,

    "mlops":
        0.95,

    "database":
        0.85,

    "business_intelligence":
        0.75,

    "communication":
        0.55,

    "management":
        0.50,

    "domain":
        0.80,

}


# ============================================================
# CATEGORY WEIGHT
# ============================================================

def category_weight(
    category: str,
) -> float:

    category = normalize_skill(
        category
    )

    return CATEGORY_WEIGHTS.get(

        category,

        0.75,

    )


# ============================================================
# IMPORTANCE NORMALIZATION
# ============================================================

def normalize_importance(
    value: Any,
) -> float:

    try:

        score = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        score = 50.0

    # Support both 0–1 and 0–100.
    if 0.0 <= score <= 1.0:

        score *= 100.0

    return max(

        0.0,

        min(
            100.0,
            score,
        ),

    )


# ============================================================
# PRIORITY SCORE
# ============================================================

def calculate_priority_score(
    requirement_type: str,
    status: str,
    importance: float,
    category: str,
) -> float:

    req_weight = requirement_weight(
        requirement_type
    )

    gap_weight = status_gap_score(
        status
    )

    importance_weight = (

        normalize_importance(
            importance
        )
        /
        100.0

    )

    cat_weight = category_weight(
        category
    )

    score = (

        req_weight
        *
        gap_weight
        *
        (
            0.60
            +
            0.40
            *
            importance_weight
        )
        *
        cat_weight

    )

    return round(

        score
        *
        100.0,

        2,

    )


# ============================================================
# PRIORITY LABEL
# ============================================================

def priority_label(
    score: float,
    requirement_type: str,
    status: str,
) -> str:

    if status == GAP_COVERED:

        return PRIORITY_LOW

    if (

        requirement_type == "required"

        and

        score >= 70

    ):

        return PRIORITY_CRITICAL

    if score >= 60:

        return PRIORITY_HIGH

    if score >= 35:

        return PRIORITY_MEDIUM

    return PRIORITY_LOW


# ============================================================
# RECOMMENDED ACTION
# ============================================================

def recommended_action(
    status: str,
    skill: str,
    priority: str,
) -> str:

    if status == GAP_PARTIAL:

        return (

            f"Strengthen {skill} through "
            "hands-on practice, an industry "
            "case study, and a project."

        )

    if priority == PRIORITY_CRITICAL:

        return (

            f"Immediately add {skill} to the "
            "learning plan and complete a "
            "production-oriented project."

        )

    if priority == PRIORITY_HIGH:

        return (

            f"Add focused training for {skill} "
            "and validate it through a practical "
            "industry assignment."

        )

    if priority == PRIORITY_MEDIUM:

        return (

            f"Include {skill} as a targeted "
            "enhancement in the curriculum."

        )

    return (

        f"Consider {skill} as an optional "
        "learning enhancement."

    )


# ============================================================
# GAP RATIONALE
# ============================================================

def build_gap_rationale(
    skill: str,
    requirement_type: str,
    status: str,
    similarity: float,
    importance: float,
) -> str:

    if status == GAP_MISSING:

        return (

            f"{skill} is a {requirement_type} "
            "requirement and no sufficiently "
            f"strong evidence was found. "
            f"Requirement importance is "
            f"{normalize_importance(importance):.0f}/100."

        )

    if status == GAP_PARTIAL:

        return (

            f"{skill} is partially covered. "
            f"Current similarity is "
            f"{similarity:.2f}. Additional "
            "hands-on depth is recommended."

        )

    return (

        f"{skill} is adequately covered "
        "by the current skill set."

    )


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# GAP ITEM GENERATION
# ============================================================


# ============================================================
# GET MATCH ATTRIBUTE
# ============================================================

def get_match_value(
    match: Any,
    attribute: str,
    default: Any = None,
) -> Any:

    if isinstance(
        match,
        Mapping,
    ):

        return match.get(
            attribute,
            default,
        )

    return getattr(

        match,

        attribute,

        default,

    )


# ============================================================
# MATCH → GAP ITEM
# ============================================================

def match_to_gap_item(
    match: Any,
) -> GapItem:

    skill = clean_text(

        get_match_value(
            match,
            "required_skill",
            "",
        )

    )

    status = clean_text(

        get_match_value(
            match,
            "status",
            GAP_MISSING,
        )

    )

    requirement_type = clean_text(

        get_match_value(
            match,
            "requirement_type",
            "required",
        )

    )

    category = clean_text(

        get_match_value(
            match,
            "category",
            "technical",
        )

    )

    similarity = float(

        get_match_value(
            match,
            "similarity",
            0.0,
        )

        or

        0.0

    )

    importance = float(

        get_match_value(
            match,
            "importance",
            0.0,
        )

        or

        0.0

    )

    candidate_skill = clean_text(

        get_match_value(
            match,
            "candidate_skill",
            "",
        )

    )

    evidence = []

    if candidate_skill:

        evidence.append(
            candidate_skill
        )

    priority_score = calculate_priority_score(

        requirement_type,

        status,

        importance,

        category,

    )

    priority = priority_label(

        priority_score,

        requirement_type,

        status,

    )

    related_skills = resolve_related_skills(
        skill
    )

    parent_skills = resolve_parent_skills(
        skill
    )

    related_concepts = resolve_skill_concepts(
        skill
    )

    related_tools = resolve_skill_tools(
        skill
    )

    rationale = build_gap_rationale(

        skill,

        requirement_type,

        status,

        similarity,

        importance,

    )

    action = recommended_action(

        status,

        skill,

        priority,

    )

    return GapItem(

        skill=skill,

        gap_type=GAP_SKILL,

        status=status,

        requirement_type=requirement_type,

        category=category,

        similarity=similarity,

        importance=importance,

        priority_score=priority_score,

        priority=priority,

        candidate_evidence=evidence,

        related_skills=related_skills,

        parent_skills=parent_skills,

        related_concepts=related_concepts,

        related_tools=related_tools,

        rationale=rationale,

        recommended_action=action,

        metadata={

            "candidate_skill":
                candidate_skill,

            "match_type":
                get_match_value(
                    match,
                    "match_type",
                    "",
                ),

            "confidence":
                get_match_value(
                    match,
                    "confidence",
                    0.0,
                ),

        },

    )


# ============================================================
# FILTER ACTUAL GAPS
# ============================================================

def filter_gaps(
    gaps: Sequence[GapItem],
) -> List[GapItem]:

    return [

        gap

        for gap
        in gaps

        if gap.status
        != GAP_COVERED

    ]


# ============================================================
# SORT GAPS
# ============================================================

def sort_gaps(
    gaps: Sequence[GapItem],
) -> List[GapItem]:

    priority_order = {

        PRIORITY_CRITICAL:
            0,

        PRIORITY_HIGH:
            1,

        PRIORITY_MEDIUM:
            2,

        PRIORITY_LOW:
            3,

    }

    return sorted(

        gaps,

        key=lambda gap: (

            priority_order.get(
                gap.priority,
                99,
            ),

            -gap.priority_score,

            -gap.importance,

            gap.skill.lower(),

        ),

    )


# ============================================================
# BUILD GAP ITEMS FROM MATCH REPORT
# ============================================================

def build_gap_items(
    report: Any,
) -> List[GapItem]:

    matches = getattr(

        report,

        "matches",

        [],

    )

    gaps = [

        match_to_gap_item(
            match
        )

        for match
        in matches

    ]

    gaps = filter_gaps(
        gaps
    )

    return sort_gaps(
        gaps
    )


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# SECONDARY GAP ANALYSIS
# ============================================================


# ============================================================
# CONCEPT GAP
# ============================================================

def build_concept_gaps(
    skill_gaps: Sequence[GapItem],
) -> List[GapItem]:

    result = []

    seen = set()

    for gap in skill_gaps:

        if gap.status == GAP_COVERED:

            continue

        for concept in gap.related_concepts:

            key = normalize_skill(
                concept
            )

            if not key:

                continue

            if key in seen:

                continue

            seen.add(
                key
            )

            result.append(

                GapItem(

                    skill=concept,

                    gap_type=GAP_CONCEPT,

                    status=GAP_MISSING,

                    requirement_type=gap.requirement_type,

                    category=gap.category,

                    similarity=gap.similarity,

                    importance=gap.importance,

                    priority_score=round(

                        gap.priority_score
                        *
                        DEFAULT_CONCEPT_WEIGHT,

                        2,

                    ),

                    priority=gap.priority,

                    candidate_evidence=[],

                    related_skills=[

                        gap.skill

                    ],

                    related_concepts=[],

                    related_tools=[],

                    rationale=(

                        f"The concept '{concept}' "
                        f"is associated with the "
                        f"required skill '{gap.skill}'."

                    ),

                    recommended_action=(

                        f"Teach {concept} while "
                        f"strengthening {gap.skill}."

                    ),

                )

            )

    return sort_gaps(
        result
    )


# ============================================================
# TOOL GAP
# ============================================================

def build_tool_gaps(
    skill_gaps: Sequence[GapItem],
    candidate_tools: Optional[
        Sequence[str]
    ] = None,
) -> List[GapItem]:

    candidate_tool_keys = {

        normalize_skill(
            tool
        )

        for tool
        in (

            candidate_tools
            or
            []

        )

    }

    result = []

    seen = set()

    for gap in skill_gaps:

        if gap.status == GAP_COVERED:

            continue

        for tool in gap.related_tools:

            key = normalize_skill(
                tool
            )

            if not key:

                continue

            if key in candidate_tool_keys:

                continue

            if key in seen:

                continue

            seen.add(
                key
            )

            score = (

                gap.priority_score
                *
                DEFAULT_TOOL_WEIGHT

            )

            result.append(

                GapItem(

                    skill=tool,

                    gap_type=GAP_TOOL,

                    status=GAP_MISSING,

                    requirement_type=gap.requirement_type,

                    category=gap.category,

                    similarity=0.0,

                    importance=gap.importance,

                    priority_score=round(
                        score,
                        2,
                    ),

                    priority=priority_label(

                        score,

                        gap.requirement_type,

                        GAP_MISSING,

                    ),

                    related_skills=[

                        gap.skill

                    ],

                    rationale=(

                        f"{tool} is a relevant "
                        f"tool associated with "
                        f"{gap.skill}."

                    ),

                    recommended_action=(

                        f"Add practical exposure "
                        f"to {tool} while learning "
                        f"{gap.skill}."

                    ),

                )

            )

    return sort_gaps(
        result
    )


# ============================================================
# CATEGORY GAPS
# ============================================================

def build_category_gaps(
    report: Any,
) -> List[GapItem]:

    coverage = getattr(

        report,

        "matches",

        [],

    )

    grouped = {}

    for match in coverage:

        category = clean_text(

            get_match_value(
                match,
                "category",
                "technical",
            )

        )

        if category not in grouped:

            grouped[category] = {

                "total":
                    0,

                "missing":
                    0,

                "partial":
                    0,

                "importance":
                    0.0,

            }

        grouped[
            category
        ][
            "total"
        ] += 1

        status = get_match_value(

            match,

            "status",

            GAP_MISSING,

        )

        if status == GAP_MISSING:

            grouped[
                category
            ][
                "missing"
            ] += 1

        elif status == GAP_PARTIAL:

            grouped[
                category
            ][
                "partial"
            ] += 1

        grouped[
            category
        ][
            "importance"
        ] += normalize_importance(

            get_match_value(
                match,
                "importance",
                0.0,
            )

        )

    result = []

    for category, data in grouped.items():

        total = data[
            "total"
        ]

        missing = data[
            "missing"
        ]

        partial = data[
            "partial"
        ]

        if total <= 0:

            continue

        gap_ratio = (

            (
                missing
                +
                partial * 0.5
            )
            /
            total

        )

        if gap_ratio <= 0:

            continue

        importance = (

            data[
                "importance"
            ]
            /
            total

        )

        score = round(

            gap_ratio
            *
            100.0
            *
            category_weight(
                category
            ),

            2,

        )

        result.append(

            GapItem(

                skill=category,

                gap_type=GAP_CATEGORY,

                status=GAP_MISSING,

                requirement_type="required",

                category=category,

                similarity=1.0 - gap_ratio,

                importance=importance,

                priority_score=score,

                priority=priority_label(

                    score,

                    "required",

                    GAP_MISSING,

                ),

                rationale=(

                    f"The {category} category "
                    f"has {missing} missing and "
                    f"{partial} partial "
                    "requirements."

                ),

                recommended_action=(

                    f"Increase curriculum "
                    f"coverage in {category}."

                ),

            )

        )

    return sort_gaps(
        result
    )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# GAP SUMMARY + READINESS
# ============================================================


# ============================================================
# BUILD SUMMARY
# ============================================================

def build_gap_summary(
    report: Any,
) -> GapSummary:

    total = int(

        getattr(
            report,
            "total_required",
            0,
        )

    ) + int(

        getattr(
            report,
            "total_preferred",
            0,
        )

    )

    gaps = build_gap_items(
        report
    )

    critical = sum(

        1

        for gap
        in gaps

        if gap.priority
        == PRIORITY_CRITICAL

    )

    high = sum(

        1

        for gap
        in gaps

        if gap.priority
        == PRIORITY_HIGH

    )

    medium = sum(

        1

        for gap
        in gaps

        if gap.priority
        == PRIORITY_MEDIUM

    )

    low = sum(

        1

        for gap
        in gaps

        if gap.priority
        == PRIORITY_LOW

    )

    covered = (

        int(

            getattr(
                report,
                "matched_required",
                0,
            )

        )

        +

        int(

            getattr(
                report,
                "matched_preferred",
                0,
            )

        )

    )

    partial = (

        int(

            getattr(
                report,
                "partial_required",
                0,
            )

        )

        +

        int(

            getattr(
                report,
                "partial_preferred",
                0,
            )

        )

    )

    missing = (

        int(

            getattr(
                report,
                "missing_required",
                0,
            )

        )

        +

        int(

            getattr(
                report,
                "missing_preferred",
                0,
            )

        )

    )

    return GapSummary(

        total_requirements=total,

        covered_requirements=covered,

        partial_requirements=partial,

        missing_requirements=missing,

        critical_gaps=critical,

        high_priority_gaps=high,

        medium_priority_gaps=medium,

        low_priority_gaps=low,

        required_coverage=float(

            getattr(
                report,
                "required_coverage",
                0.0,
            )

            or

            0.0

        ),

        preferred_coverage=float(

            getattr(
                report,
                "preferred_coverage",
                0.0,
            )

            or

            0.0

        ),

        overall_coverage=float(

            getattr(
                report,
                "overall_coverage",
                0.0,
            )

            or

            0.0

        ),

        readiness_score=float(

            getattr(
                report,
                "readiness_score",
                0.0,
            )

            or

            0.0

        ),

    )


# ============================================================
# READINESS BAND
# ============================================================

def readiness_band(
    score: float,
) -> str:

    score = max(

        0.0,

        min(
            100.0,
            float(score),
        ),

    )

    if score >= 85:

        return "job_ready"

    if score >= 70:

        return "near_ready"

    if score >= 50:

        return "developing"

    if score >= 30:

        return "significant_gap"

    return "major_gap"


# ============================================================
# READINESS MESSAGE
# ============================================================

def readiness_message(
    score: float,
) -> str:

    band = readiness_band(
        score
    )

    messages = {

        "job_ready":
            "The current skill profile is strongly aligned with the target role.",

        "near_ready":
            "The current skill profile is close to the target role, with focused gaps to address.",

        "developing":
            "The candidate has a useful foundation but requires targeted skill development.",

        "significant_gap":
            "Several important requirements are not sufficiently covered.",

        "major_gap":
            "The current profile has substantial gaps against the target role.",

    }

    return messages[
        band
    ]


# ============================================================
# CRITICAL GAP FILTER
# ============================================================

def get_critical_gaps(
    gaps: Sequence[GapItem],
) -> List[GapItem]:

    return [

        gap

        for gap
        in gaps

        if gap.priority
        == PRIORITY_CRITICAL

    ]


# ============================================================
# HIGH PRIORITY GAP FILTER
# ============================================================

def get_high_priority_gaps(
    gaps: Sequence[GapItem],
) -> List[GapItem]:

    return [

        gap

        for gap
        in gaps

        if gap.priority
        in {

            PRIORITY_CRITICAL,

            PRIORITY_HIGH,

        }

    ]


# ============================================================
# GAP DISTRIBUTION
# ============================================================

def gap_distribution(
    gaps: Sequence[GapItem],
) -> Dict[str, int]:

    distribution = {

        PRIORITY_CRITICAL:
            0,

        PRIORITY_HIGH:
            0,

        PRIORITY_MEDIUM:
            0,

        PRIORITY_LOW:
            0,

    }

    for gap in gaps:

        if gap.priority in distribution:

            distribution[
                gap.priority
            ] += 1

    return distribution


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# MAIN GAP AGENT
# ============================================================


@dataclass
class GapAnalysisResult:

    jd_title: str = ""

    company: str = ""

    role: str = ""

    summary: GapSummary = field(
        default_factory=GapSummary
    )

    skill_gaps: List[GapItem] = field(
        default_factory=list
    )

    concept_gaps: List[GapItem] = field(
        default_factory=list
    )

    tool_gaps: List[GapItem] = field(
        default_factory=list
    )

    category_gaps: List[GapItem] = field(
        default_factory=list
    )

    critical_gaps: List[GapItem] = field(
        default_factory=list
    )

    recommendations: List[str] = field(
        default_factory=list
    )

    readiness_band: str = ""

    readiness_message: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# GAP AGENT
# ============================================================

class GapAgent:

    def __init__(
        self,
        config: Optional[
            SkillMatcherConfig
        ] = None,
    ):

        if config is None:

            try:

                config = SkillMatcherConfig()

            except Exception:

                config = None

        self.config = config


    # ========================================================
    # MATCH
    # ========================================================

    def match(
        self,
        profile: JDProfile,
        candidate_skills: Sequence[Any],
    ) -> Any:

        if match_jd_to_candidate is None:

            raise RuntimeError(

                "industry.skill_matcher could not "
                "be imported. Ensure the industry "
                "package is available."

            )

        return match_jd_to_candidate(

            profile,

            candidate_skills,

            self.config,

        )


    # ========================================================
    # ANALYZE
    # ========================================================

    def analyze(
        self,
        profile: JDProfile,
        candidate_skills: Sequence[Any],
        candidate_tools: Optional[
            Sequence[str]
        ] = None,
    ) -> GapAnalysisResult:

        logger.info(
            "Starting gap analysis"
        )

        normalized_candidate_skills = (
            extract_candidate_skills(
                candidate_skills
            )
        )

        report = self.match(

            profile,

            normalized_candidate_skills,

        )

        skill_gaps = build_gap_items(
            report
        )

        concept_gaps = build_concept_gaps(
            skill_gaps
        )

        tool_gaps = build_tool_gaps(

            skill_gaps,

            candidate_tools,

        )

        category_gaps = build_category_gaps(
            report
        )

        summary = build_gap_summary(
            report
        )

        critical = get_critical_gaps(
            skill_gaps
        )

        recommendations = self.generate_recommendations(

            skill_gaps,

            concept_gaps,

            tool_gaps,

            category_gaps,

        )

        score = summary.readiness_score

        return GapAnalysisResult(

            jd_title=clean_text(

                getattr(
                    profile,
                    "title",
                    "",
                )

            ),

            company=clean_text(

                getattr(
                    profile,
                    "company",
                    "",
                )

            ),

            role=clean_text(

                getattr(
                    profile,
                    "role",
                    "",
                )

                or

                getattr(
                    profile,
                    "job_title",
                    "",
                )

            ),

            summary=summary,

            skill_gaps=skill_gaps,

            concept_gaps=concept_gaps,

            tool_gaps=tool_gaps,

            category_gaps=category_gaps,

            critical_gaps=critical,

            recommendations=recommendations,

            readiness_band=readiness_band(
                score
            ),

            readiness_message=readiness_message(
                score
            ),

            metadata={

                "agent_version":
                    GAP_AGENT_VERSION,

                "candidate_skill_count":
                    len(
                        normalized_candidate_skills
                    ),

                "gap_count":
                    len(
                        skill_gaps
                    ),

            },

        )


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    def generate_recommendations(
        self,
        skill_gaps: Sequence[GapItem],
        concept_gaps: Sequence[GapItem],
        tool_gaps: Sequence[GapItem],
        category_gaps: Sequence[GapItem],
    ) -> List[str]:

        recommendations = []

        # ----------------------------------------------------
        # Critical
        # ----------------------------------------------------

        critical = get_critical_gaps(
            skill_gaps
        )

        for gap in critical[:5]:

            recommendations.append(

                f"Priority 1: Build {gap.skill} "
                "because it is a critical "
                "requirement for the target role."

            )

        # ----------------------------------------------------
        # High
        # ----------------------------------------------------

        high = [

            gap

            for gap
            in skill_gaps

            if gap.priority
            == PRIORITY_HIGH

        ]

        for gap in high[:5]:

            recommendations.append(

                f"Strengthen {gap.skill} with "
                "hands-on implementation and "
                "an industry-relevant project."

            )

        # ----------------------------------------------------
        # Concepts
        # ----------------------------------------------------

        for gap in concept_gaps[:5]:

            recommendations.append(

                f"Add conceptual depth in "
                f"{gap.skill}."

            )

        # ----------------------------------------------------
        # Tools
        # ----------------------------------------------------

        for gap in tool_gaps[:5]:

            recommendations.append(

                f"Provide practical exposure "
                f"to {gap.skill}."

            )

        # ----------------------------------------------------
        # Categories
        # ----------------------------------------------------

        for gap in category_gaps[:3]:

            recommendations.append(

                f"Increase curriculum coverage "
                f"for the {gap.category} category."

            )

        # ----------------------------------------------------
        # Deduplicate
        # ----------------------------------------------------

        output = []

        seen = set()

        for item in recommendations:

            key = normalize_skill(
                item
            )

            if key in seen:

                continue

            seen.add(
                key
            )

            output.append(
                item
            )

        return output


# ============================================================
# GLOBAL AGENT
# ============================================================

gap_agent = GapAgent()


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# FUNCTIONAL API + LANGGRAPH COMPATIBILITY
# ============================================================


# ============================================================
# ANALYZE GAP
# ============================================================

def analyze_gap(
    profile: JDProfile,
    candidate_skills: Sequence[Any],
    candidate_tools: Optional[
        Sequence[str]
    ] = None,
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> GapAnalysisResult:

    agent = GapAgent(
        config
    )

    return agent.analyze(

        profile,

        candidate_skills,

        candidate_tools,

    )


# ============================================================
# ANALYZE CURRICULUM AGAINST JD
# ============================================================

def analyze_curriculum_gap(
    profile: JDProfile,
    curriculum: Any,
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> GapAnalysisResult:

    skills = extract_curriculum_skills(
        curriculum
    )

    return analyze_gap(

        profile,

        skills,

        config=config,

    )


# ============================================================
# RESULT TO DICT
# ============================================================

def gap_result_to_dict(
    result: GapAnalysisResult,
) -> Dict[str, Any]:

    return {

        "jd_title":
            result.jd_title,

        "company":
            result.company,

        "role":
            result.role,

        "summary":
            asdict(
                result.summary
            ),

        "skill_gaps": [

            asdict(
                gap
            )

            for gap
            in result.skill_gaps

        ],

        "concept_gaps": [

            asdict(
                gap
            )

            for gap
            in result.concept_gaps

        ],

        "tool_gaps": [

            asdict(
                gap
            )

            for gap
            in result.tool_gaps

        ],

        "category_gaps": [

            asdict(
                gap
            )

            for gap
            in result.category_gaps

        ],

        "critical_gaps": [

            asdict(
                gap
            )

            for gap
            in result.critical_gaps

        ],

        "recommendations":
            result.recommendations,

        "readiness_band":
            result.readiness_band,

        "readiness_message":
            result.readiness_message,

        "metadata":
            result.metadata,

    }


# ============================================================
# JSON
# ============================================================

def gap_result_to_json(
    result: GapAnalysisResult,
    indent: int = 2,
) -> str:

    return json.dumps(

        gap_result_to_dict(
            result
        ),

        indent=indent,

        ensure_ascii=False,

    )


# ============================================================
# LANGGRAPH NODE
#
# This function deliberately does not import LangGraph.
# Therefore the project can run without LangGraph installed.
#
# Expected state:
#
# {
#     "jd_profile": JDProfile,
#     "candidate_skills": [...],
#     "candidate_tools": [...]
# }
#
# Output:
#
# {
#     "gap_analysis": GapAnalysisResult,
#     "gap_analysis_dict": {...},
# }
# ============================================================

def gap_agent_node(
    state: Mapping[str, Any],
) -> Dict[str, Any]:

    profile = (

        state.get(
            "jd_profile"
        )

        or

        state.get(
            "profile"
        )

    )

    if profile is None:

        raise ValueError(

            "gap_agent_node requires "
            "'jd_profile' or 'profile'."

        )

    candidate_skills = (

        state.get(
            "candidate_skills"
        )

        or

        state.get(
            "skills"
        )

        or

        state.get(
            "curriculum_skills"
        )

        or

        []

    )

    candidate_tools = (

        state.get(
            "candidate_tools"
        )

        or

        state.get(
            "tools"
        )

        or

        []

    )

    result = gap_agent.analyze(

        profile,

        candidate_skills,

        candidate_tools,

    )

    return {

        "gap_analysis":
            result,

        "gap_analysis_dict":
            gap_result_to_dict(
                result
            ),

        "skill_gaps":
            result.skill_gaps,

        "critical_gaps":
            result.critical_gaps,

        "readiness_score":
            result.summary.readiness_score,

    }


# ============================================================
# TOP GAP NAMES
# ============================================================

def top_gap_names(
    result: GapAnalysisResult,
    limit: int = 10,
) -> List[str]:

    return [

        gap.skill

        for gap
        in result.skill_gaps[
            :limit
        ]

    ]


# ============================================================
# TOP CRITICAL GAP NAMES
# ============================================================

def critical_gap_names(
    result: GapAnalysisResult,
) -> List[str]:

    return [

        gap.skill

        for gap
        in result.critical_gaps

    ]


# ============================================================
# GAP COUNT
# ============================================================

def gap_count(
    result: GapAnalysisResult,
) -> int:

    return len(
        result.skill_gaps
    )


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# VALIDATION + PUBLIC API + SELF TEST
# ============================================================


# ============================================================
# VALIDATE RESULT
# ============================================================

def validate_gap_result(
    result: GapAnalysisResult,
) -> Dict[str, Any]:

    errors = []

    if not isinstance(
        result,
        GapAnalysisResult,
    ):

        errors.append(
            "Result is not GapAnalysisResult."
        )

    if result.summary.total_requirements < 0:

        errors.append(
            "total_requirements cannot be negative."
        )

    if not (
        0.0
        <=
        result.summary.readiness_score
        <=
        100.0
    ):

        errors.append(
            "readiness_score must be between 0 and 100."
        )

    if not (
        0.0
        <=
        result.summary.required_coverage
        <=
        100.0
    ):

        errors.append(
            "required_coverage must be between 0 and 100."
        )

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

    }


# ============================================================
# GAP STATISTICS
# ============================================================

def gap_statistics(
    result: GapAnalysisResult,
) -> Dict[str, Any]:

    distribution = gap_distribution(

        result.skill_gaps

    )

    return {

        "total_skill_gaps":
            len(
                result.skill_gaps
            ),

        "total_concept_gaps":
            len(
                result.concept_gaps
            ),

        "total_tool_gaps":
            len(
                result.tool_gaps
            ),

        "total_category_gaps":
            len(
                result.category_gaps
            ),

        "critical_gaps":
            len(
                result.critical_gaps
            ),

        "distribution":
            distribution,

        "readiness_score":
            result.summary.readiness_score,

        "readiness_band":
            result.readiness_band,

        "required_coverage":
            result.summary.required_coverage,

        "preferred_coverage":
            result.summary.preferred_coverage,

        "overall_coverage":
            result.summary.overall_coverage,

    }


# ============================================================
# PUBLIC CAPABILITIES
# ============================================================

GAP_AGENT_CAPABILITIES = [

    "jd_to_curriculum_gap_analysis",

    "jd_to_candidate_gap_analysis",

    "required_skill_gap_detection",

    "preferred_skill_gap_detection",

    "partial_skill_detection",

    "critical_gap_detection",

    "concept_gap_detection",

    "tool_gap_detection",

    "category_gap_detection",

    "gap_priority_scoring",

    "gap_severity_classification",

    "readiness_scoring",

    "readiness_band_classification",

    "learning_recommendations",

    "langgraph_node",

    "json_serialization",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "GAP_AGENT_VERSION",

    # Constants
    "GAP_SKILL",

    "GAP_CONCEPT",

    "GAP_TOOL",

    "GAP_CATEGORY",

    "GAP_EXPERIENCE",

    "GAP_PROFICIENCY",

    "GAP_MISSING",

    "GAP_PARTIAL",

    "GAP_COVERED",

    "PRIORITY_CRITICAL",

    "PRIORITY_HIGH",

    "PRIORITY_MEDIUM",

    "PRIORITY_LOW",

    # Models
    "GapItem",

    "GapSummary",

    "GapAnalysisResult",

    # Agent
    "GapAgent",

    "gap_agent",

    # Input
    "normalize_skill_list",

    "extract_candidate_skills",

    "extract_curriculum_skills",

    "extract_all_requirements",

    # Taxonomy
    "get_skill_intelligence",

    "resolve_related_skills",

    "resolve_parent_skills",

    "resolve_skill_tools",

    "resolve_skill_concepts",

    "resolve_skill_aliases",

    # Priority
    "calculate_priority_score",

    "priority_label",

    "recommended_action",

    # Gap analysis
    "match_to_gap_item",

    "build_gap_items",

    "build_concept_gaps",

    "build_tool_gaps",

    "build_category_gaps",

    "build_gap_summary",

    "get_critical_gaps",

    "get_high_priority_gaps",

    "gap_distribution",

    # Main API
    "analyze_gap",

    "analyze_curriculum_gap",

    "gap_agent_node",

    # Reporting
    "gap_result_to_dict",

    "gap_result_to_json",

    "top_gap_names",

    "critical_gap_names",

    "gap_count",

    "gap_statistics",

    "validate_gap_result",

    "GAP_AGENT_CAPABILITIES",

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
        "GAP AGENT SELF TEST"
    )

    print(
        "============================================"
    )

    # --------------------------------------------------------
    # Try importing JD parser
    # --------------------------------------------------------

    try:

        from ..industry.jd_parser import (
            analyze_jd,
        )

    except ImportError:

        try:

            from industry.jd_parser import (
                analyze_jd,
            )

        except ImportError:

            analyze_jd = None


    if analyze_jd is None:

        print(
            "JD parser unavailable."
        )

        print(
            "Gap agent module import test passed."
        )

    else:

        sample_jd = """

        Senior Generative AI Engineer

        Requirements:

        - Strong Python programming.
        - Machine learning experience.
        - Large language models.
        - Retrieval augmented generation.
        - LangChain.
        - Vector databases.
        - Docker.

        Preferred:

        - AWS.
        - Kubernetes.
        - Hugging Face.
        - PyTorch.

        """

        try:

            profile = analyze_jd(
                sample_jd
            )

            candidate_skills = [

                "Python",

                "Machine Learning",

                "LLM",

                "LangChain",

                "Docker",

            ]

            result = analyze_gap(

                profile,

                candidate_skills,

            )

            print(
                "\nJD:"
            )

            print(
                result.jd_title
            )

            print(
                "\nReadiness:"
            )

            print(
                result.summary.readiness_score
            )

            print(
                result.readiness_band
            )

            print(
                "\nCritical Gaps:"
            )

            for gap in result.critical_gaps:

                print(
                    f"  ! {gap.skill}"
                )

            print(
                "\nAll Skill Gaps:"
            )

            for gap in result.skill_gaps:

                print(

                    f"  [{gap.priority}] "
                    f"{gap.skill} "
                    f"({gap.status})"

                )

            print(
                "\nRecommendations:"
            )

            for item in result.recommendations:

                print(
                    f"  - {item}"
                )

            print(
                "\nValidation:"
            )

            print(

                json.dumps(

                    validate_gap_result(
                        result
                    ),

                    indent=2,

                )

            )

            print(
                "\nStatistics:"
            )

            print(

                json.dumps(

                    gap_statistics(
                        result
                    ),

                    indent=2,

                )

            )

        except Exception as exc:

            print(
                "Self-test execution error:"
            )

            print(
                exc
            )

    print(
        "\n============================================"
    )

    print(
        "GAP AGENT TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF agents/gap_agent.py
# ============================================================
