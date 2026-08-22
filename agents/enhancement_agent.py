# ============================================================
# agents/enhancement_agent.py
# CHUNK 1/10
#
# CURRICULUM ENHANCEMENT AGENT
#
# Purpose:
#   Convert identified industry/JD skill gaps into
#   actionable curriculum enhancements.
#
# Pipeline:
#
#   JD
#    ↓
#   Gap Agent
#    ↓
#   Skill / Concept / Tool Gaps
#    ↓
#   Enhancement Agent
#    ↓
#   Topics
#   Modules
#   Tools
#   Projects
#   Case Studies
#   Assessments
#   Learning Outcomes
#   Priority
#    ↓
#   Enhanced Curriculum
#
# Designed for:
#
#   - Streamlit
#   - LangGraph
#   - Curriculum Intelligence
#   - Industry Skill Mapping
#   - Gap Analysis
#   - Training Program Design
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
    Tuple,
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

    from .gap_agent import (
        GapItem,
        GapAnalysisResult,
        PRIORITY_CRITICAL,
        PRIORITY_HIGH,
        PRIORITY_MEDIUM,
        PRIORITY_LOW,
        GAP_SKILL,
        GAP_CONCEPT,
        GAP_TOOL,
        GAP_CATEGORY,
    )

except ImportError:

    try:

        from agents.gap_agent import (
            GapItem,
            GapAnalysisResult,
            PRIORITY_CRITICAL,
            PRIORITY_HIGH,
            PRIORITY_MEDIUM,
            PRIORITY_LOW,
            GAP_SKILL,
            GAP_CONCEPT,
            GAP_TOOL,
            GAP_CATEGORY,
        )

    except ImportError:

        GapItem = Any
        GapAnalysisResult = Any

        PRIORITY_CRITICAL = "critical"
        PRIORITY_HIGH = "high"
        PRIORITY_MEDIUM = "medium"
        PRIORITY_LOW = "low"

        GAP_SKILL = "skill"
        GAP_CONCEPT = "concept"
        GAP_TOOL = "tool"
        GAP_CATEGORY = "category"


try:

    from ..industry.taxonomy import (
        get_skill_definition,
        get_skill_aliases,
        get_skill_concepts,
        get_skill_tools,
        get_related_skills,
        get_parent_skills,
        get_skill_category,
        get_role_definition,
        get_role_skills,
    )

except ImportError:

    try:

        from industry.taxonomy import (
            get_skill_definition,
            get_skill_aliases,
            get_skill_concepts,
            get_skill_tools,
            get_related_skills,
            get_parent_skills,
            get_skill_category,
            get_role_definition,
            get_role_skills,
        )

    except ImportError:

        get_skill_definition = None
        get_skill_aliases = None
        get_skill_concepts = None
        get_skill_tools = None
        get_related_skills = None
        get_parent_skills = None
        get_skill_category = None
        get_role_definition = None
        get_role_skills = None


# ============================================================
# VERSION
# ============================================================

ENHANCEMENT_AGENT_VERSION = "1.0.0"


# ============================================================
# ENHANCEMENT TYPES
# ============================================================

ENHANCEMENT_TOPIC = "topic"

ENHANCEMENT_MODULE = "module"

ENHANCEMENT_TOOL = "tool"

ENHANCEMENT_PROJECT = "project"

ENHANCEMENT_CASE_STUDY = "case_study"

ENHANCEMENT_ASSESSMENT = "assessment"

ENHANCEMENT_LEARNING_OUTCOME = "learning_outcome"

ENHANCEMENT_CONTENT = "content"


# ============================================================
# DELIVERY TYPES
# ============================================================

DELIVERY_THEORY = "theory"

DELIVERY_HANDS_ON = "hands_on"

DELIVERY_PROJECT = "project"

DELIVERY_CASE_STUDY = "case_study"

DELIVERY_LAB = "lab"

DELIVERY_ASSESSMENT = "assessment"


# ============================================================
# DIFFICULTY LEVELS
# ============================================================

LEVEL_BEGINNER = "beginner"

LEVEL_INTERMEDIATE = "intermediate"

LEVEL_ADVANCED = "advanced"

LEVEL_EXPERT = "expert"


# ============================================================
# ENHANCEMENT ITEM
# ============================================================

@dataclass
class EnhancementItem:

    title: str

    enhancement_type: str

    priority: str = PRIORITY_MEDIUM

    priority_score: float = 0.0

    source_gap: str = ""

    source_gap_type: str = GAP_SKILL

    category: str = "technical"

    difficulty: str = LEVEL_INTERMEDIATE

    delivery_mode: str = DELIVERY_HANDS_ON

    description: str = ""

    rationale: str = ""

    learning_outcomes: List[str] = field(
        default_factory=list
    )

    topics: List[str] = field(
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

    project_ideas: List[str] = field(
        default_factory=list
    )

    case_studies: List[str] = field(
        default_factory=list
    )

    assessments: List[str] = field(
        default_factory=list
    )

    prerequisites: List[str] = field(
        default_factory=list
    )

    estimated_hours: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# ENHANCEMENT PLAN
# ============================================================

@dataclass
class EnhancementPlan:

    role: str = ""

    jd_title: str = ""

    company: str = ""

    current_readiness: float = 0.0

    target_readiness: float = 90.0

    enhancements: List[EnhancementItem] = field(
        default_factory=list
    )

    priority_items: List[EnhancementItem] = field(
        default_factory=list
    )

    modules: List[EnhancementItem] = field(
        default_factory=list
    )

    projects: List[EnhancementItem] = field(
        default_factory=list
    )

    case_studies: List[EnhancementItem] = field(
        default_factory=list
    )

    assessments: List[EnhancementItem] = field(
        default_factory=list
    )

    learning_outcomes: List[str] = field(
        default_factory=list
    )

    recommended_sequence: List[str] = field(
        default_factory=list
    )

    estimated_total_hours: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# NORMALIZATION + UTILITY FUNCTIONS
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
# NORMALIZE KEY
# ============================================================

def normalize_key(
    value: Any,
) -> str:

    text = clean_text(
        value
    ).lower()

    text = text.replace(
        "&",
        "and",
    )

    text = re.sub(
        r"[^a-z0-9+#./ -]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# SLUGIFY
# ============================================================

def slugify(
    value: Any,
) -> str:

    text = normalize_key(
        value
    )

    text = text.replace(
        "+",
        "plus",
    )

    text = text.replace(
        "#",
        "sharp",
    )

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text,
    )

    return text.strip(
        "_"
    )


# ============================================================
# DEDUPLICATE
# ============================================================

def deduplicate(
    values: Iterable[Any],
) -> List[str]:

    result = []

    seen = set()

    for value in values:

        text = clean_text(
            value
        )

        if not text:

            continue

        key = normalize_key(
            text
        )

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
# SAFE TAXONOMY CALL
# ============================================================

def safe_taxonomy_call(
    function: Any,
    value: str,
    default: Any = None,
) -> Any:

    if function is None:

        return default

    try:

        return function(
            value
        )

    except Exception as exc:

        logger.debug(
            "Taxonomy lookup failed for %s: %s",
            value,
            exc,
        )

        return default


# ============================================================
# TAXONOMY SKILL INFO
# ============================================================

def skill_info(
    skill: str,
) -> Dict[str, Any]:

    return {

        "category":
            safe_taxonomy_call(
                get_skill_category,
                skill,
                "technical",
            ),

        "concepts":
            deduplicate(

                safe_taxonomy_call(
                    get_skill_concepts,
                    skill,
                    [],
                )
                or
                []

            ),

        "tools":
            deduplicate(

                safe_taxonomy_call(
                    get_skill_tools,
                    skill,
                    [],
                )
                or
                []

            ),

        "related_skills":
            deduplicate(

                safe_taxonomy_call(
                    get_related_skills,
                    skill,
                    [],
                )
                or
                []

            ),

        "parent_skills":
            deduplicate(

                safe_taxonomy_call(
                    get_parent_skills,
                    skill,
                    [],
                )
                or
                []

            ),

        "aliases":
            deduplicate(

                safe_taxonomy_call(
                    get_skill_aliases,
                    skill,
                    [],
                )
                or
                []

            ),

    }


# ============================================================
# GET GAP ATTRIBUTE
# ============================================================

def gap_value(
    gap: Any,
    attribute: str,
    default: Any = None,
) -> Any:

    if isinstance(
        gap,
        Mapping,
    ):

        return gap.get(
            attribute,
            default,
        )

    return getattr(

        gap,

        attribute,

        default,

    )


# ============================================================
# GAP TO DICT
# ============================================================

def gap_to_dict(
    gap: Any,
) -> Dict[str, Any]:

    if isinstance(
        gap,
        Mapping,
    ):

        return dict(
            gap
        )

    return {

        "skill":
            gap_value(
                gap,
                "skill",
                "",
            ),

        "gap_type":
            gap_value(
                gap,
                "gap_type",
                GAP_SKILL,
            ),

        "priority":
            gap_value(
                gap,
                "priority",
                PRIORITY_MEDIUM,
            ),

        "priority_score":
            gap_value(
                gap,
                "priority_score",
                0.0,
            ),

        "category":
            gap_value(
                gap,
                "category",
                "technical",
            ),

        "importance":
            gap_value(
                gap,
                "importance",
                0.0,
            ),

        "status":
            gap_value(
                gap,
                "status",
                "missing",
            ),

    }


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# ENHANCEMENT KNOWLEDGE BASE
# ============================================================


# ============================================================
# DEFAULT HOURS
# ============================================================

DEFAULT_HOURS = {

    ENHANCEMENT_TOPIC:
        3.0,

    ENHANCEMENT_MODULE:
        8.0,

    ENHANCEMENT_TOOL:
        4.0,

    ENHANCEMENT_PROJECT:
        20.0,

    ENHANCEMENT_CASE_STUDY:
        5.0,

    ENHANCEMENT_ASSESSMENT:
        2.0,

    ENHANCEMENT_LEARNING_OUTCOME:
        1.0,

    ENHANCEMENT_CONTENT:
        4.0,

}


# ============================================================
# CATEGORY → DELIVERY
# ============================================================

CATEGORY_DELIVERY = {

    "programming":
        DELIVERY_LAB,

    "machine_learning":
        DELIVERY_HANDS_ON,

    "deep_learning":
        DELIVERY_LAB,

    "generative_ai":
        DELIVERY_LAB,

    "agentic_ai":
        DELIVERY_PROJECT,

    "data_engineering":
        DELIVERY_LAB,

    "cloud":
        DELIVERY_LAB,

    "devops":
        DELIVERY_LAB,

    "mlops":
        DELIVERY_LAB,

    "database":
        DELIVERY_HANDS_ON,

    "business_intelligence":
        DELIVERY_HANDS_ON,

    "cybersecurity":
        DELIVERY_LAB,

    "computer_vision":
        DELIVERY_PROJECT,

    "finance":
        DELIVERY_CASE_STUDY,

    "industrial_ai":
        DELIVERY_PROJECT,

}


# ============================================================
# CATEGORY → DIFFICULTY
# ============================================================

CATEGORY_DIFFICULTY = {

    "programming":
        LEVEL_INTERMEDIATE,

    "machine_learning":
        LEVEL_INTERMEDIATE,

    "deep_learning":
        LEVEL_ADVANCED,

    "generative_ai":
        LEVEL_ADVANCED,

    "agentic_ai":
        LEVEL_ADVANCED,

    "data_engineering":
        LEVEL_INTERMEDIATE,

    "cloud":
        LEVEL_INTERMEDIATE,

    "devops":
        LEVEL_INTERMEDIATE,

    "mlops":
        LEVEL_ADVANCED,

    "database":
        LEVEL_BEGINNER,

    "business_intelligence":
        LEVEL_BEGINNER,

    "cybersecurity":
        LEVEL_ADVANCED,

    "computer_vision":
        LEVEL_ADVANCED,

    "finance":
        LEVEL_INTERMEDIATE,

    "industrial_ai":
        LEVEL_ADVANCED,

}


# ============================================================
# SKILL-SPECIFIC PROJECT TEMPLATES
# ============================================================

PROJECT_TEMPLATES = {

    "python": [

        "Build a production-ready Python data processing application.",

        "Develop a Python REST API with validation, logging, and testing.",

    ],

    "machine learning": [

        "Build an end-to-end machine learning prediction system.",

        "Develop a model training and evaluation pipeline.",

    ],

    "large language models": [

        "Build an LLM-powered enterprise assistant.",

        "Develop an LLM evaluation and monitoring pipeline.",

    ],

    "retrieval augmented generation": [

        "Build a production-style document RAG assistant.",

        "Develop a domain-specific knowledge retrieval system.",

    ],

    "langchain": [

        "Build a tool-enabled LLM application using LangChain.",

        "Develop a structured agent workflow using LangChain.",

    ],

    "langgraph": [

        "Build a stateful multi-step AI workflow using LangGraph.",

        "Develop a checkpointed human-in-the-loop agent.",

    ],

    "agentic ai": [

        "Build a multi-agent enterprise automation workflow.",

        "Develop a planning-and-tool-use AI agent.",

    ],

    "computer vision": [

        "Build an image classification or object detection system.",

        "Develop an automated visual inspection pipeline.",

    ],

    "data engineering": [

        "Build an end-to-end ETL data pipeline.",

        "Develop a batch and streaming data processing workflow.",

    ],

    "apache spark": [

        "Build a distributed data processing pipeline with Spark.",

    ],

    "docker": [

        "Containerize and deploy an AI application.",

    ],

    "kubernetes": [

        "Deploy and scale a machine learning service on Kubernetes.",

    ],

    "aws": [

        "Deploy an AI application using AWS cloud services.",

    ],

    "power bi": [

        "Build an executive business intelligence dashboard.",

    ],

    "cybersecurity": [

        "Build an AI-assisted security monitoring workflow.",

    ],

}


# ============================================================
# CASE STUDY TEMPLATES
# ============================================================

CASE_STUDY_TEMPLATES = {

    "machine learning": [

        "Customer churn prediction",

        "Credit risk prediction",

        "Demand forecasting",

    ],

    "generative ai": [

        "Enterprise knowledge assistant",

        "Customer support copilot",

        "Document intelligence",

    ],

    "retrieval augmented generation": [

        "Enterprise policy knowledge assistant",

        "Technical documentation assistant",

        "Research paper assistant",

    ],

    "agentic ai": [

        "Multi-agent business process automation",

        "AI research assistant",

        "Autonomous support workflow",

    ],

    "computer vision": [

        "Manufacturing defect detection",

        "Medical image classification",

        "Retail shelf monitoring",

    ],

    "data engineering": [

        "Real-time transaction analytics",

        "Customer data pipeline",

        "IoT event processing",

    ],

    "cybersecurity": [

        "Threat detection",

        "Security incident triage",

        "AI-assisted SOC workflow",

    ],

    "business intelligence": [

        "Executive KPI analytics",

        "Sales performance dashboard",

        "Customer analytics dashboard",

    ],

    "industrial_ai": [

        "Predictive maintenance",

        "Visual quality inspection",

        "Production optimization",

    ],

}


# ============================================================
# ASSESSMENT TEMPLATES
# ============================================================

ASSESSMENT_TEMPLATES = {

    "programming":
        "Implement a practical coding assignment.",

    "machine_learning":
        "Build, evaluate, and explain a machine learning model.",

    "deep_learning":
        "Train and evaluate a deep learning model.",

    "generative_ai":
        "Develop and evaluate a generative AI application.",

    "agentic_ai":
        "Build an agent capable of tool use and workflow execution.",

    "data_engineering":
        "Design and implement a data pipeline.",

    "cloud":
        "Deploy a production-style application in the cloud.",

    "devops":
        "Create a CI/CD pipeline and containerized deployment.",

    "mlops":
        "Deploy and monitor a machine learning model.",

    "cybersecurity":
        "Analyze a security scenario and propose an automated response.",

    "computer_vision":
        "Build and evaluate a computer vision application.",

    "business_intelligence":
        "Create an interactive dashboard and derive business insights.",

}


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# TOPIC + LEARNING OUTCOME GENERATION
# ============================================================


# ============================================================
# GENERATE TOPICS
# ============================================================

def generate_topics(
    skill: str,
    concepts: Sequence[str],
    tools: Sequence[str],
) -> List[str]:

    topics = [

        f"{skill} fundamentals",

        f"{skill} architecture",

        f"{skill} implementation",

        f"{skill} best practices",

        f"{skill} production applications",

    ]

    for concept in concepts:

        topics.append(
            concept
        )

    for tool in tools:

        topics.append(

            f"{skill} with {tool}"

        )

    return deduplicate(
        topics
    )


# ============================================================
# GENERATE LEARNING OUTCOMES
# ============================================================

def generate_learning_outcomes(
    skill: str,
    concepts: Sequence[str],
    tools: Sequence[str],
    difficulty: str,
) -> List[str]:

    outcomes = [

        (
            f"Explain the core principles "
            f"of {skill}."
        ),

        (
            f"Implement {skill} in a "
            "practical application."
        ),

        (
            f"Evaluate solutions built "
            f"using {skill}."
        ),

    ]

    if concepts:

        outcomes.append(

            (
                f"Apply key {skill} concepts "
                "to an industry problem."
            )

        )

    if tools:

        outcomes.append(

            (
                f"Use relevant tools such as "
                f"{', '.join(tools[:3])} "
                f"to implement {skill}."
            )

        )

    if difficulty in {

        LEVEL_ADVANCED,

        LEVEL_EXPERT,

    }:

        outcomes.extend([

            (
                f"Design a production-oriented "
                f"{skill} solution."
            ),

            (
                f"Identify performance, "
                "scalability, reliability, "
                "and security considerations."
            ),

        ])

    return deduplicate(
        outcomes
    )


# ============================================================
# GENERATE PREREQUISITES
# ============================================================

def generate_prerequisites(
    skill: str,
    parent_skills: Sequence[str],
) -> List[str]:

    prerequisites = []

    for parent in parent_skills:

        if normalize_key(
            parent
        ) != normalize_key(
            skill
        ):

            prerequisites.append(
                parent
            )

    return deduplicate(
        prerequisites
    )


# ============================================================
# SELECT DELIVERY MODE
# ============================================================

def select_delivery_mode(
    category: str,
    enhancement_type: str,
) -> str:

    if enhancement_type == ENHANCEMENT_PROJECT:

        return DELIVERY_PROJECT

    if enhancement_type == ENHANCEMENT_CASE_STUDY:

        return DELIVERY_CASE_STUDY

    if enhancement_type == ENHANCEMENT_ASSESSMENT:

        return DELIVERY_ASSESSMENT

    return CATEGORY_DELIVERY.get(

        category,

        DELIVERY_HANDS_ON,

    )


# ============================================================
# SELECT DIFFICULTY
# ============================================================

def select_difficulty(
    category: str,
    priority: str,
) -> str:

    base = CATEGORY_DIFFICULTY.get(

        category,

        LEVEL_INTERMEDIATE,

    )

    if priority == PRIORITY_CRITICAL:

        if base == LEVEL_BEGINNER:

            return LEVEL_INTERMEDIATE

        if base == LEVEL_INTERMEDIATE:

            return LEVEL_ADVANCED

    return base


# ============================================================
# ESTIMATE HOURS
# ============================================================

def estimate_hours(
    enhancement_type: str,
    priority: str,
    concepts: int = 0,
    tools: int = 0,
) -> float:

    hours = DEFAULT_HOURS.get(

        enhancement_type,

        4.0,

    )

    if priority == PRIORITY_CRITICAL:

        hours *= 1.5

    elif priority == PRIORITY_HIGH:

        hours *= 1.25

    hours += concepts * 0.5

    hours += tools * 0.5

    return round(
        hours,
        1,
    )


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# TOPIC + MODULE ENHANCEMENTS
# ============================================================


# ============================================================
# CREATE TOPIC ENHANCEMENT
# ============================================================

def create_topic_enhancement(
    gap: Any,
) -> EnhancementItem:

    data = gap_to_dict(
        gap
    )

    skill = clean_text(
        data.get(
            "skill",
            "",
        )
    )

    priority = data.get(
        "priority",
        PRIORITY_MEDIUM,
    )

    score = float(

        data.get(
            "priority_score",
            0.0,
        )
        or
        0.0

    )

    category = clean_text(

        data.get(
            "category",
            "technical",
        )

    )

    info = skill_info(
        skill
    )

    concepts = info[
        "concepts"
    ]

    tools = info[
        "tools"
    ]

    difficulty = select_difficulty(

        category,

        priority,

    )

    return EnhancementItem(

        title=f"{skill} Enhancement",

        enhancement_type=ENHANCEMENT_TOPIC,

        priority=priority,

        priority_score=score,

        source_gap=skill,

        source_gap_type=data.get(
            "gap_type",
            GAP_SKILL,
        ),

        category=category,

        difficulty=difficulty,

        delivery_mode=select_delivery_mode(

            category,

            ENHANCEMENT_TOPIC,

        ),

        description=(

            f"Add focused curriculum coverage "
            f"for {skill}."

        ),

        rationale=(

            f"The curriculum should strengthen "
            f"{skill} based on the identified "
            "industry requirement."

        ),

        learning_outcomes=
            generate_learning_outcomes(

                skill,

                concepts,

                tools,

                difficulty,

            ),

        topics=
            generate_topics(

                skill,

                concepts,

                tools,

            ),

        skills=[

            skill

        ],

        tools=tools,

        concepts=concepts,

        prerequisites=
            generate_prerequisites(

                skill,

                info[
                    "parent_skills"
                ],

            ),

        estimated_hours=
            estimate_hours(

                ENHANCEMENT_TOPIC,

                priority,

                len(
                    concepts
                ),

                len(
                    tools
                ),

            ),

    )


# ============================================================
# CREATE MODULE ENHANCEMENT
# ============================================================

def create_module_enhancement(
    gap: Any,
) -> EnhancementItem:

    data = gap_to_dict(
        gap
    )

    skill = clean_text(
        data.get(
            "skill",
            "",
        )
    )

    priority = data.get(
        "priority",
        PRIORITY_MEDIUM,
    )

    score = float(

        data.get(
            "priority_score",
            0.0,
        )
        or
        0.0

    )

    category = clean_text(

        data.get(
            "category",
            "technical",
        )

    )

    info = skill_info(
        skill
    )

    concepts = info[
        "concepts"
    ]

    tools = info[
        "tools"
    ]

    difficulty = select_difficulty(

        category,

        priority,

    )

    topics = generate_topics(

        skill,

        concepts,

        tools,

    )

    outcomes = generate_learning_outcomes(

        skill,

        concepts,

        tools,

        difficulty,

    )

    return EnhancementItem(

        title=f"Industry-Aligned {skill} Module",

        enhancement_type=ENHANCEMENT_MODULE,

        priority=priority,

        priority_score=score,

        source_gap=skill,

        source_gap_type=data.get(
            "gap_type",
            GAP_SKILL,
        ),

        category=category,

        difficulty=difficulty,

        delivery_mode=select_delivery_mode(

            category,

            ENHANCEMENT_MODULE,

        ),

        description=(

            f"Create a structured module "
            f"covering {skill} from "
            "fundamentals through practical "
            "industry implementation."

        ),

        rationale=(

            f"{skill} represents an identified "
            "curriculum-to-industry gap and "
            "should receive structured module "
            "coverage."

        ),

        learning_outcomes=outcomes,

        topics=topics,

        skills=[

            skill

        ],

        tools=tools,

        concepts=concepts,

        prerequisites=
            generate_prerequisites(

                skill,

                info[
                    "parent_skills"
                ],

            ),

        estimated_hours=
            estimate_hours(

                ENHANCEMENT_MODULE,

                priority,

                len(
                    concepts
                ),

                len(
                    tools
                ),

            ),

    )


# ============================================================
# CREATE TOOL ENHANCEMENT
# ============================================================

def create_tool_enhancement(
    gap: Any,
) -> EnhancementItem:

    data = gap_to_dict(
        gap
    )

    tool = clean_text(

        data.get(
            "skill",
            "",
        )

    )

    priority = data.get(
        "priority",
        PRIORITY_MEDIUM,
    )

    score = float(

        data.get(
            "priority_score",
            0.0,
        )
        or
        0.0

    )

    category = clean_text(

        data.get(
            "category",
            "technical",
        )

    )

    return EnhancementItem(

        title=f"{tool} Practical Lab",

        enhancement_type=ENHANCEMENT_TOOL,

        priority=priority,

        priority_score=score,

        source_gap=tool,

        source_gap_type=GAP_TOOL,

        category=category,

        difficulty=select_difficulty(

            category,

            priority,

        ),

        delivery_mode=DELIVERY_LAB,

        description=(

            f"Introduce practical hands-on "
            f"training using {tool}."

        ),

        rationale=(

            f"{tool} provides practical "
            "implementation capability "
            "associated with the identified "
            "industry requirement."

        ),

        learning_outcomes=[

            (
                f"Explain the purpose and "
                f"architecture of {tool}."
            ),

            (
                f"Use {tool} in a practical "
                "industry workflow."
            ),

            (
                f"Troubleshoot common "
                f"{tool} implementation issues."
            ),

        ],

        topics=[

            f"{tool} fundamentals",

            f"{tool} architecture",

            f"{tool} hands-on lab",

            f"{tool} production usage",

        ],

        tools=[

            tool

        ],

        estimated_hours=
            estimate_hours(

                ENHANCEMENT_TOOL,

                priority,

            ),

    )


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# PROJECT + CASE STUDY + ASSESSMENT GENERATION
# ============================================================


# ============================================================
# PROJECT IDEAS
# ============================================================

def project_ideas_for_skill(
    skill: str,
) -> List[str]:

    key = normalize_key(
        skill
    )

    for template_key, ideas in (
        PROJECT_TEMPLATES.items()
    ):

        if key == normalize_key(
            template_key
        ):

            return list(
                ideas
            )

    # --------------------------------------------------------
    # Generic project templates
    # --------------------------------------------------------

    return [

        (
            f"Build an end-to-end "
            f"{skill} solution for an "
            "industry problem."
        ),

        (
            f"Develop a production-oriented "
            f"{skill} application with "
            "documentation and testing."
        ),

    ]


# ============================================================
# CASE STUDY IDEAS
# ============================================================

def case_study_ideas_for_skill(
    skill: str,
) -> List[str]:

    key = normalize_key(
        skill
    )

    for template_key, ideas in (
        CASE_STUDY_TEMPLATES.items()
    ):

        if key == normalize_key(
            template_key
        ):

            return list(
                ideas
            )

    return [

        (
            f"Analyze an enterprise "
            f"use case involving {skill}."
        ),

        (
            f"Compare multiple approaches "
            f"to implementing {skill}."
        ),

    ]


# ============================================================
# ASSESSMENT FOR CATEGORY
# ============================================================

def assessment_for_category(
    skill: str,
    category: str,
) -> str:

    template = ASSESSMENT_TEMPLATES.get(

        category,

        (
            "Complete a practical assignment "
            f"demonstrating {skill}."
        ),

    )

    return template


# ============================================================
# CREATE PROJECT ENHANCEMENT
# ============================================================

def create_project_enhancement(
    gap: Any,
) -> EnhancementItem:

    data = gap_to_dict(
        gap
    )

    skill = clean_text(

        data.get(
            "skill",
            "",
        )

    )

    priority = data.get(
        "priority",
        PRIORITY_MEDIUM,
    )

    score = float(

        data.get(
            "priority_score",
            0.0,
        )
        or
        0.0

    )

    category = clean_text(

        data.get(
            "category",
            "technical",
        )

    )

    info = skill_info(
        skill
    )

    projects = project_ideas_for_skill(
        skill
    )

    return EnhancementItem(

        title=f"{skill} Industry Project",

        enhancement_type=ENHANCEMENT_PROJECT,

        priority=priority,

        priority_score=score,

        source_gap=skill,

        source_gap_type=data.get(
            "gap_type",
            GAP_SKILL,
        ),

        category=category,

        difficulty=select_difficulty(

            category,

            priority,

        ),

        delivery_mode=DELIVERY_PROJECT,

        description=(

            f"Add a practical industry project "
            f"focused on {skill}."

        ),

        rationale=(

            f"Project-based learning will "
            f"validate practical proficiency "
            f"in {skill}."

        ),

        learning_outcomes=[

            (
                f"Apply {skill} to solve a "
                "realistic business problem."
            ),

            (
                f"Build an end-to-end "
                f"{skill} solution."
            ),

            (
                f"Document and present the "
                f"{skill} implementation."
            ),

        ],

        topics=generate_topics(

            skill,

            info[
                "concepts"
            ],

            info[
                "tools"
            ],

        ),

        skills=[

            skill

        ],

        tools=info[
            "tools"
        ],

        concepts=info[
            "concepts"
        ],

        project_ideas=projects,

        prerequisites=info[
            "parent_skills"
        ],

        estimated_hours=
            estimate_hours(

                ENHANCEMENT_PROJECT,

                priority,

                len(
                    info["concepts"]
                ),

                len(
                    info["tools"]
                ),

            ),

    )


# ============================================================
# CREATE CASE STUDY
# ============================================================

def create_case_study_enhancement(
    gap: Any,
) -> EnhancementItem:

    data = gap_to_dict(
        gap
    )

    skill = clean_text(

        data.get(
            "skill",
            "",
        )

    )

    priority = data.get(
        "priority",
        PRIORITY_MEDIUM,
    )

    score = float(

        data.get(
            "priority_score",
            0.0,
        )
        or
        0.0

    )

    category = clean_text(

        data.get(
            "category",
            "technical",
        )

    )

    cases = case_study_ideas_for_skill(
        skill
    )

    return EnhancementItem(

        title=f"{skill} Industry Case Study",

        enhancement_type=ENHANCEMENT_CASE_STUDY,

        priority=priority,

        priority_score=score,

        source_gap=skill,

        source_gap_type=data.get(
            "gap_type",
            GAP_SKILL,
        ),

        category=category,

        difficulty=LEVEL_INTERMEDIATE,

        delivery_mode=DELIVERY_CASE_STUDY,

        description=(

            f"Add industry case studies "
            f"illustrating how {skill} is "
            "used in real organizations."

        ),

        rationale=(

            f"Industry context helps learners "
            f"connect {skill} with business "
            "problems and production decisions."

        ),

        learning_outcomes=[

            (
                f"Analyze a real-world "
                f"{skill} use case."
            ),

            (
                "Identify technical and "
                "business trade-offs."
            ),

            (
                "Recommend an appropriate "
                "implementation approach."
            ),

        ],

        skills=[

            skill

        ],

        concepts=skill_info(
            skill
        )[
            "concepts"
        ],

        tools=skill_info(
            skill
        )[
            "tools"
        ],

        case_studies=cases,

        assessments=[

            (
                f"Prepare a solution "
                f"recommendation for the "
                f"{skill} case."
            )

        ],

        estimated_hours=
            estimate_hours(

                ENHANCEMENT_CASE_STUDY,

                priority,

            ),

    )


# ============================================================
# CREATE ASSESSMENT
# ============================================================

def create_assessment_enhancement(
    gap: Any,
) -> EnhancementItem:

    data = gap_to_dict(
        gap
    )

    skill = clean_text(

        data.get(
            "skill",
            "",
        )

    )

    priority = data.get(
        "priority",
        PRIORITY_MEDIUM,
    )

    score = float(

        data.get(
            "priority_score",
            0.0,
        )
        or
        0.0

    )

    category = clean_text(

        data.get(
            "category",
            "technical",
        )

    )

    assessment = assessment_for_category(

        skill,

        category,

    )

    return EnhancementItem(

        title=f"{skill} Competency Assessment",

        enhancement_type=ENHANCEMENT_ASSESSMENT,

        priority=priority,

        priority_score=score,

        source_gap=skill,

        source_gap_type=data.get(
            "gap_type",
            GAP_SKILL,
        ),

        category=category,

        difficulty=select_difficulty(

            category,

            priority,

        ),

        delivery_mode=DELIVERY_ASSESSMENT,

        description=(

            f"Assess practical competency "
            f"in {skill}."

        ),

        rationale=(

            "Assessment should verify that "
            "the identified skill gap has "
            "actually been closed."

        ),

        learning_outcomes=[

            (
                f"Demonstrate practical "
                f"competency in {skill}."
            )

        ],

        skills=[

            skill

        ],

        assessments=[

            assessment

        ],

        estimated_hours=
            estimate_hours(

                ENHANCEMENT_ASSESSMENT,

                priority,

            ),

    )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# ENHANCEMENT PLAN GENERATION
# ============================================================


# ============================================================
# SELECT GAP ENHANCEMENTS
# ============================================================

def create_enhancements_for_gap(
    gap: Any,
) -> List[EnhancementItem]:

    data = gap_to_dict(
        gap
    )

    gap_type = data.get(
        "gap_type",
        GAP_SKILL,
    )

    enhancements = []

    # --------------------------------------------------------
    # Skill gap
    # --------------------------------------------------------

    if gap_type == GAP_SKILL:

        enhancements.append(

            create_topic_enhancement(
                gap
            )

        )

        enhancements.append(

            create_module_enhancement(
                gap
            )

        )

        enhancements.append(

            create_project_enhancement(
                gap
            )

        )

        enhancements.append(

            create_case_study_enhancement(
                gap
            )

        )

        enhancements.append(

            create_assessment_enhancement(
                gap
            )

        )

    # --------------------------------------------------------
    # Concept gap
    # --------------------------------------------------------

    elif gap_type == GAP_CONCEPT:

        enhancements.append(

            create_topic_enhancement(
                gap
            )

        )

        enhancements.append(

            create_case_study_enhancement(
                gap
            )

        )

        enhancements.append(

            create_assessment_enhancement(
                gap
            )

        )

    # --------------------------------------------------------
    # Tool gap
    # --------------------------------------------------------

    elif gap_type == GAP_TOOL:

        enhancements.append(

            create_tool_enhancement(
                gap
            )

        )

        enhancements.append(

            create_project_enhancement(
                gap
            )

        )

        enhancements.append(

            create_assessment_enhancement(
                gap
            )

        )

    # --------------------------------------------------------
    # Category gap
    # --------------------------------------------------------

    elif gap_type == GAP_CATEGORY:

        enhancements.append(

            create_module_enhancement(
                gap
            )

        )

        enhancements.append(

            create_project_enhancement(
                gap
            )

        )

    else:

        enhancements.append(

            create_topic_enhancement(
                gap
            )

        )

    return enhancements


# ============================================================
# DEDUPLICATE ENHANCEMENTS
# ============================================================

def deduplicate_enhancements(
    enhancements: Sequence[
        EnhancementItem
    ],
) -> List[EnhancementItem]:

    result = []

    seen = set()

    for item in enhancements:

        key = (

            normalize_key(
                item.title
            ),

            item.enhancement_type,

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
# SORT ENHANCEMENTS
# ============================================================

def sort_enhancements(
    enhancements: Sequence[
        EnhancementItem
    ],
) -> List[EnhancementItem]:

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

    type_order = {

        ENHANCEMENT_MODULE:
            0,

        ENHANCEMENT_TOPIC:
            1,

        ENHANCEMENT_TOOL:
            2,

        ENHANCEMENT_PROJECT:
            3,

        ENHANCEMENT_CASE_STUDY:
            4,

        ENHANCEMENT_ASSESSMENT:
            5,

    }

    return sorted(

        enhancements,

        key=lambda item: (

            priority_order.get(

                item.priority,

                99,

            ),

            -item.priority_score,

            type_order.get(

                item.enhancement_type,

                99,

            ),

            item.title.lower(),

        ),

    )


# ============================================================
# BUILD RECOMMENDED SEQUENCE
# ============================================================

def build_learning_sequence(
    enhancements: Sequence[
        EnhancementItem
    ],
) -> List[str]:

    sequence = []

    # --------------------------------------------------------
    # Modules first
    # --------------------------------------------------------

    modules = [

        item

        for item
        in enhancements

        if item.enhancement_type
        == ENHANCEMENT_MODULE

    ]

    for item in modules:

        sequence.append(

            f"1. Learn: {item.title}"

        )

    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    tools = [

        item

        for item
        in enhancements

        if item.enhancement_type
        == ENHANCEMENT_TOOL

    ]

    for item in tools:

        sequence.append(

            f"2. Practice: {item.title}"

        )

    # --------------------------------------------------------
    # Case studies
    # --------------------------------------------------------

    cases = [

        item

        for item
        in enhancements

        if item.enhancement_type
        == ENHANCEMENT_CASE_STUDY

    ]

    for item in cases:

        sequence.append(

            f"3. Analyze: {item.title}"

        )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    projects = [

        item

        for item
        in enhancements

        if item.enhancement_type
        == ENHANCEMENT_PROJECT

    ]

    for item in projects:

        sequence.append(

            f"4. Build: {item.title}"

        )

    # --------------------------------------------------------
    # Assessments
    # --------------------------------------------------------

    assessments = [

        item

        for item
        in enhancements

        if item.enhancement_type
        == ENHANCEMENT_ASSESSMENT

    ]

    for item in assessments:

        sequence.append(

            f"5. Validate: {item.title}"

        )

    return sequence


# ============================================================
# BUILD PLAN
# ============================================================

def build_enhancement_plan(
    gap_result: Any,
) -> EnhancementPlan:

    skill_gaps = (

        getattr(
            gap_result,
            "skill_gaps",
            [],
        )

        or

        []

    )

    concept_gaps = (

        getattr(
            gap_result,
            "concept_gaps",
            [],
        )

        or

        []

    )

    tool_gaps = (

        getattr(
            gap_result,
            "tool_gaps",
            [],
        )

        or

        []

    )

    category_gaps = (

        getattr(
            gap_result,
            "category_gaps",
            [],
        )

        or

        []

    )

    all_gaps = (

        list(skill_gaps)

        +

        list(concept_gaps)

        +

        list(tool_gaps)

        +

        list(category_gaps)

    )

    enhancements = []

    for gap in all_gaps:

        enhancements.extend(

            create_enhancements_for_gap(
                gap
            )

        )

    enhancements = deduplicate_enhancements(

        enhancements

    )

    enhancements = sort_enhancements(

        enhancements

    )

    modules = [

        item

        for item
        in enhancements

        if item.enhancement_type
        == ENHANCEMENT_MODULE

    ]

    projects = [

        item

        for item
        in enhancements

        if item.enhancement_type
        == ENHANCEMENT_PROJECT

    ]

    cases = [

        item

        for item
        in enhancements

        if item.enhancement_type
        == ENHANCEMENT_CASE_STUDY

    ]

    assessments = [

        item

        for item
        in enhancements

        if item.enhancement_type
        == ENHANCEMENT_ASSESSMENT

    ]

    priority_items = [

        item

        for item
        in enhancements

        if item.priority
        in {

            PRIORITY_CRITICAL,

            PRIORITY_HIGH,

        }

    ]

    outcomes = []

    for item in enhancements:

        outcomes.extend(
            item.learning_outcomes
        )

    outcomes = deduplicate(
        outcomes
    )

    sequence = build_learning_sequence(

        enhancements

    )

    total_hours = sum(

        item.estimated_hours

        for item
        in enhancements

    )

    summary = getattr(

        gap_result,

        "summary",

        None,

    )

    readiness = float(

        getattr(
            summary,
            "readiness_score",
            0.0,
        )

        or

        0.0

    )

    return EnhancementPlan(

        role=clean_text(

            getattr(
                gap_result,
                "role",
                "",
            )

        ),

        jd_title=clean_text(

            getattr(
                gap_result,
                "jd_title",
                "",
            )

        ),

        company=clean_text(

            getattr(
                gap_result,
                "company",
                "",
            )

        ),

        current_readiness=readiness,

        enhancements=enhancements,

        priority_items=priority_items,

        modules=modules,

        projects=projects,

        case_studies=cases,

        assessments=assessments,

        learning_outcomes=outcomes,

        recommended_sequence=sequence,

        estimated_total_hours=round(

            total_hours,

            1,

        ),

        metadata={

            "agent_version":
                ENHANCEMENT_AGENT_VERSION,

            "gap_count":
                len(
                    all_gaps
                ),

            "enhancement_count":
                len(
                    enhancements
                ),

        },

    )


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# MAIN ENHANCEMENT AGENT
# ============================================================


class EnhancementAgent:

    """
    Converts GapAnalysisResult into a structured
    curriculum enhancement plan.
    """

    def __init__(
        self,
        target_readiness: float = 90.0,
    ):

        self.target_readiness = max(

            0.0,

            min(
                100.0,
                float(
                    target_readiness
                ),
            ),

        )


    # ========================================================
    # GENERATE
    # ========================================================

    def generate(
        self,
        gap_result: Any,
    ) -> EnhancementPlan:

        logger.info(

            "Generating curriculum enhancements"

        )

        plan = build_enhancement_plan(

            gap_result

        )

        plan.target_readiness = (

            self.target_readiness

        )

        return plan


    # ========================================================
    # ENHANCE
    # ========================================================

    def enhance(
        self,
        gap_result: Any,
    ) -> EnhancementPlan:

        return self.generate(
            gap_result
        )


    # ========================================================
    # TOP PRIORITIES
    # ========================================================

    def top_priorities(
        self,
        plan: EnhancementPlan,
        limit: int = 10,
    ) -> List[EnhancementItem]:

        return plan.priority_items[
            :limit
        ]


    # ========================================================
    # CRITICAL ENHANCEMENTS
    # ========================================================

    def critical_enhancements(
        self,
        plan: EnhancementPlan,
    ) -> List[EnhancementItem]:

        return [

            item

            for item
            in plan.enhancements

            if item.priority
            == PRIORITY_CRITICAL

        ]


    # ========================================================
    # PROJECT RECOMMENDATIONS
    # ========================================================

    def project_recommendations(
        self,
        plan: EnhancementPlan,
        limit: int = 10,
    ) -> List[EnhancementItem]:

        return plan.projects[
            :limit
        ]


    # ========================================================
    # MODULE RECOMMENDATIONS
    # ========================================================

    def module_recommendations(
        self,
        plan: EnhancementPlan,
        limit: int = 10,
    ) -> List[EnhancementItem]:

        return plan.modules[
            :limit
        ]


    # ========================================================
    # SUMMARY
    # ========================================================

    def summary(
        self,
        plan: EnhancementPlan,
    ) -> Dict[str, Any]:

        readiness_gap = max(

            0.0,

            plan.target_readiness
            -
            plan.current_readiness,

        )

        return {

            "role":
                plan.role,

            "current_readiness":
                plan.current_readiness,

            "target_readiness":
                plan.target_readiness,

            "readiness_gap":
                round(
                    readiness_gap,
                    2,
                ),

            "enhancement_count":
                len(
                    plan.enhancements
                ),

            "priority_count":
                len(
                    plan.priority_items
                ),

            "module_count":
                len(
                    plan.modules
                ),

            "project_count":
                len(
                    plan.projects
                ),

            "case_study_count":
                len(
                    plan.case_studies
                ),

            "assessment_count":
                len(
                    plan.assessments
                ),

            "estimated_hours":
                plan.estimated_total_hours,

        }


# ============================================================
# GLOBAL AGENT
# ============================================================

enhancement_agent = EnhancementAgent()


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# FUNCTIONAL API + LANGGRAPH NODE
# ============================================================


# ============================================================
# GENERATE ENHANCEMENTS
# ============================================================

def generate_enhancements(
    gap_result: Any,
    target_readiness: float = 90.0,
) -> EnhancementPlan:

    agent = EnhancementAgent(

        target_readiness=target_readiness

    )

    return agent.generate(
        gap_result
    )


# ============================================================
# ENHANCE CURRICULUM
# ============================================================

def enhance_curriculum(
    gap_result: Any,
    target_readiness: float = 90.0,
) -> EnhancementPlan:

    return generate_enhancements(

        gap_result,

        target_readiness,

    )


# ============================================================
# PLAN → DICT
# ============================================================

def enhancement_plan_to_dict(
    plan: EnhancementPlan,
) -> Dict[str, Any]:

    return {

        "role":
            plan.role,

        "jd_title":
            plan.jd_title,

        "company":
            plan.company,

        "current_readiness":
            plan.current_readiness,

        "target_readiness":
            plan.target_readiness,

        "enhancements": [

            asdict(
                item
            )

            for item
            in plan.enhancements

        ],

        "priority_items": [

            asdict(
                item
            )

            for item
            in plan.priority_items

        ],

        "modules": [

            asdict(
                item
            )

            for item
            in plan.modules

        ],

        "projects": [

            asdict(
                item
            )

            for item
            in plan.projects

        ],

        "case_studies": [

            asdict(
                item
            )

            for item
            in plan.case_studies

        ],

        "assessments": [

            asdict(
                item
            )

            for item
            in plan.assessments

        ],

        "learning_outcomes":
            plan.learning_outcomes,

        "recommended_sequence":
            plan.recommended_sequence,

        "estimated_total_hours":
            plan.estimated_total_hours,

        "metadata":
            plan.metadata,

    }


# ============================================================
# PLAN → JSON
# ============================================================

def enhancement_plan_to_json(
    plan: EnhancementPlan,
    indent: int = 2,
) -> str:

    return json.dumps(

        enhancement_plan_to_dict(
            plan
        ),

        indent=indent,

        ensure_ascii=False,

    )


# ============================================================
# LANGGRAPH NODE
#
# Expected input state:
#
# {
#     "gap_analysis": GapAnalysisResult
# }
#
# Output:
#
# {
#     "enhancement_plan": EnhancementPlan,
#     "enhancement_plan_dict": {...}
# }
#
# ============================================================

def enhancement_agent_node(
    state: Mapping[str, Any],
) -> Dict[str, Any]:

    gap_result = (

        state.get(
            "gap_analysis"
        )

        or

        state.get(
            "gap_result"
        )

    )

    if gap_result is None:

        raise ValueError(

            "enhancement_agent_node requires "
            "'gap_analysis' or 'gap_result'."

        )

    target_readiness = state.get(

        "target_readiness",

        90.0,

    )

    plan = generate_enhancements(

        gap_result,

        target_readiness=float(
            target_readiness
        ),

    )

    return {

        "enhancement_plan":
            plan,

        "enhancement_plan_dict":
            enhancement_plan_to_dict(
                plan
            ),

        "curriculum_enhancements":
            plan.enhancements,

        "recommended_projects":
            plan.projects,

        "recommended_modules":
            plan.modules,

        "estimated_enhancement_hours":
            plan.estimated_total_hours,

    }


# ============================================================
# TOP ENHANCEMENT TITLES
# ============================================================

def top_enhancement_titles(
    plan: EnhancementPlan,
    limit: int = 10,
) -> List[str]:

    return [

        item.title

        for item
        in plan.enhancements[
            :limit
        ]

    ]


# ============================================================
# TOP PROJECT TITLES
# ============================================================

def top_project_titles(
    plan: EnhancementPlan,
    limit: int = 10,
) -> List[str]:

    return [

        item.title

        for item
        in plan.projects[
            :limit
        ]

    ]


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# VALIDATION + STATISTICS + PUBLIC API
# ============================================================


# ============================================================
# VALIDATE ENHANCEMENT
# ============================================================

def validate_enhancement(
    item: EnhancementItem,
) -> Dict[str, Any]:

    errors = []

    if not clean_text(
        item.title
    ):

        errors.append(
            "Enhancement title is required."
        )

    if not clean_text(
        item.enhancement_type
    ):

        errors.append(
            "Enhancement type is required."
        )

    if not (
        0.0
        <=
        item.priority_score
        <=
        100.0
    ):

        errors.append(
            "Priority score must be between 0 and 100."
        )

    if item.estimated_hours < 0:

        errors.append(
            "Estimated hours cannot be negative."
        )

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

    }


# ============================================================
# VALIDATE PLAN
# ============================================================

def validate_enhancement_plan(
    plan: EnhancementPlan,
) -> Dict[str, Any]:

    errors = []

    if not isinstance(
        plan,
        EnhancementPlan,
    ):

        errors.append(
            "Invalid enhancement plan type."
        )

        return {

            "valid":
                False,

            "errors":
                errors,

        }

    for item in plan.enhancements:

        validation = validate_enhancement(
            item
        )

        errors.extend(

            validation[
                "errors"
            ]

        )

    if plan.estimated_total_hours < 0:

        errors.append(
            "Total hours cannot be negative."
        )

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

    }


# ============================================================
# ENHANCEMENT STATISTICS
# ============================================================

def enhancement_statistics(
    plan: EnhancementPlan,
) -> Dict[str, Any]:

    by_type = {}

    by_priority = {}

    by_category = {}

    for item in plan.enhancements:

        by_type[
            item.enhancement_type
        ] = (

            by_type.get(
                item.enhancement_type,
                0,
            )
            +
            1

        )

        by_priority[
            item.priority
        ] = (

            by_priority.get(
                item.priority,
                0,
            )
            +
            1

        )

        by_category[
            item.category
        ] = (

            by_category.get(
                item.category,
                0,
            )
            +
            1

        )

    return {

        "total_enhancements":
            len(
                plan.enhancements
            ),

        "by_type":
            by_type,

        "by_priority":
            by_priority,

        "by_category":
            by_category,

        "modules":
            len(
                plan.modules
            ),

        "projects":
            len(
                plan.projects
            ),

        "case_studies":
            len(
                plan.case_studies
            ),

        "assessments":
            len(
                plan.assessments
            ),

        "estimated_total_hours":
            plan.estimated_total_hours,

        "current_readiness":
            plan.current_readiness,

        "target_readiness":
            plan.target_readiness,

    }


# ============================================================
# PUBLIC CAPABILITIES
# ============================================================

ENHANCEMENT_AGENT_CAPABILITIES = [

    "skill_gap_to_topic",

    "skill_gap_to_module",

    "skill_gap_to_project",

    "skill_gap_to_case_study",

    "skill_gap_to_assessment",

    "tool_gap_to_lab",

    "concept_gap_to_learning_content",

    "category_gap_to_curriculum_module",

    "learning_outcome_generation",

    "project_generation",

    "case_study_generation",

    "assessment_generation",

    "learning_sequence_generation",

    "curriculum_enhancement_plan",

    "priority_based_enhancement",

    "langgraph_node",

    "json_serialization",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "ENHANCEMENT_AGENT_VERSION",

    # Constants
    "ENHANCEMENT_TOPIC",

    "ENHANCEMENT_MODULE",

    "ENHANCEMENT_TOOL",

    "ENHANCEMENT_PROJECT",

    "ENHANCEMENT_CASE_STUDY",

    "ENHANCEMENT_ASSESSMENT",

    "ENHANCEMENT_LEARNING_OUTCOME",

    "ENHANCEMENT_CONTENT",

    "DELIVERY_THEORY",

    "DELIVERY_HANDS_ON",

    "DELIVERY_PROJECT",

    "DELIVERY_CASE_STUDY",

    "DELIVERY_LAB",

    "DELIVERY_ASSESSMENT",

    "LEVEL_BEGINNER",

    "LEVEL_INTERMEDIATE",

    "LEVEL_ADVANCED",

    "LEVEL_EXPERT",

    # Models
    "EnhancementItem",

    "EnhancementPlan",

    # Agent
    "EnhancementAgent",

    "enhancement_agent",

    # Generators
    "generate_topics",

    "generate_learning_outcomes",

    "generate_prerequisites",

    "project_ideas_for_skill",

    "case_study_ideas_for_skill",

    "create_topic_enhancement",

    "create_module_enhancement",

    "create_tool_enhancement",

    "create_project_enhancement",

    "create_case_study_enhancement",

    "create_assessment_enhancement",

    "create_enhancements_for_gap",

    # Planning
    "build_learning_sequence",

    "build_enhancement_plan",

    "generate_enhancements",

    "enhance_curriculum",

    # Serialization
    "enhancement_plan_to_dict",

    "enhancement_plan_to_json",

    # LangGraph
    "enhancement_agent_node",

    # Reporting
    "top_enhancement_titles",

    "top_project_titles",

    "enhancement_statistics",

    "validate_enhancement",

    "validate_enhancement_plan",

    "ENHANCEMENT_AGENT_CAPABILITIES",

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
        "ENHANCEMENT AGENT SELF TEST"
    )

    print(
        "============================================"
    )

    # --------------------------------------------------------
    # Create lightweight mock gap objects
    # --------------------------------------------------------

    mock_gaps = [

        {

            "skill":
                "Retrieval Augmented Generation",

            "gap_type":
                GAP_SKILL,

            "priority":
                PRIORITY_CRITICAL,

            "priority_score":
                92.0,

            "category":
                "generative_ai",

            "importance":
                95.0,

            "status":
                "missing",

        },

        {

            "skill":
                "LangGraph",

            "gap_type":
                GAP_SKILL,

            "priority":
                PRIORITY_HIGH,

            "priority_score":
                78.0,

            "category":
                "agentic_ai",

            "importance":
                85.0,

            "status":
                "missing",

        },

        {

            "skill":
                "Docker",

            "gap_type":
                GAP_TOOL,

            "priority":
                PRIORITY_MEDIUM,

            "priority_score":
                55.0,

            "category":
                "devops",

            "importance":
                60.0,

            "status":
                "missing",

        },

    ]

    # --------------------------------------------------------
    # Mock result
    # --------------------------------------------------------

    mock_result = {

        "role":
            "Generative AI Engineer",

        "jd_title":
            "Generative AI Engineer",

        "company":
            "Demo Company",

        "summary": {

            "readiness_score":
                58.0,

        },

        "skill_gaps":
            mock_gaps[
                :2
            ],

        "concept_gaps":
            [],

        "tool_gaps":
            mock_gaps[
                2:
            ],

        "category_gaps":
            [],

    }

    # --------------------------------------------------------
    # Convert mock mapping to lightweight object
    # --------------------------------------------------------

    class MockResult:

        role = mock_result[
            "role"
        ]

        jd_title = mock_result[
            "jd_title"
        ]

        company = mock_result[
            "company"
        ]

        skill_gaps = mock_result[
            "skill_gaps"
        ]

        concept_gaps = mock_result[
            "concept_gaps"
        ]

        tool_gaps = mock_result[
            "tool_gaps"
        ]

        category_gaps = mock_result[
            "category_gaps"
        ]

        summary = type(

            "Summary",
            (),
            {

                "readiness_score":
                    58.0,

            },

        )()

    result = MockResult()

    # --------------------------------------------------------
    # Generate plan
    # --------------------------------------------------------

    plan = generate_enhancements(
        result
    )

    print(
        "\nRole:"
    )

    print(
        plan.role
    )

    print(
        "\nCurrent Readiness:"
    )

    print(
        plan.current_readiness
    )

    print(
        "\nEnhancements:"
    )

    for item in plan.enhancements[

        :10

    ]:

        print(

            f"  [{item.priority}] "
            f"{item.enhancement_type}: "
            f"{item.title}"

        )

    print(
        "\nProjects:"
    )

    for item in plan.projects[:5]:

        print(
            f"  - {item.title}"
        )

    print(
        "\nRecommended Sequence:"
    )

    for item in plan.recommended_sequence[:10]:

        print(
            f"  {item}"
        )

    print(
        "\nStatistics:"
    )

    print(

        json.dumps(

            enhancement_statistics(
                plan
            ),

            indent=2,

        )

    )

    print(
        "\nValidation:"
    )

    print(

        json.dumps(

            validate_enhancement_plan(
                plan
            ),

            indent=2,

        )

    )

    print(
        "\n============================================"
    )

    print(
        "ENHANCEMENT AGENT TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF agents/enhancement_agent.py
# ============================================================
