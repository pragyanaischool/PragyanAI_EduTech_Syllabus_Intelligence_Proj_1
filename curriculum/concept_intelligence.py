# ============================================================
# curriculum/concept_intelligence.py
# ============================================================
#
# PragyanAI Curriculum Intelligence
#
# Concept Intelligence Engine
#
# Responsibilities:
#   - Topic enrichment
#   - Concept extraction
#   - Prerequisite identification
#   - Difficulty estimation
#   - Bloom taxonomy
#   - Learning objectives
#   - Industry relevance
#   - Skill mapping
#
# ============================================================

from __future__ import annotations

import logging
import re

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


logger = logging.getLogger(
    "pragyanai.curriculum.concept_intelligence"
)


# ============================================================
# RESULT MODELS
# ============================================================

@dataclass
class Concept:

    name: str

    description: str = ""

    category: str = ""

    difficulty: str = "Intermediate"

    bloom_level: str = "Understand"

    prerequisites: List[str] = field(
        default_factory=list
    )

    skills: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    technologies: List[str] = field(
        default_factory=list
    )

    industry_relevance: str = ""

    learning_objectives: List[str] = field(
        default_factory=list
    )


@dataclass
class TopicEnrichment:

    topic: str

    concepts: List[Concept] = field(
        default_factory=list
    )

    prerequisites: List[str] = field(
        default_factory=list
    )

    skills: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    technologies: List[str] = field(
        default_factory=list
    )

    difficulty: str = "Intermediate"

    bloom_level: str = "Understand"

    industry_relevance: str = ""

    learning_objectives: List[str] = field(
        default_factory=list
    )


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/6
#
# NORMALIZATION
# ============================================================


def normalize_text(
    value: Any,
) -> str:

    if value is None:

        return ""

    text = str(
        value
    ).strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def normalize_key(
    value: Any,
) -> str:

    return normalize_text(
        value
    ).lower()


def unique_strings(
    values: Sequence[Any],
) -> List[str]:

    result = []

    seen = set()

    for value in values:

        text = normalize_text(
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
# TOKENIZATION
# ============================================================

def tokenize(
    text: str,
) -> List[str]:

    return re.findall(

        r"[A-Za-z0-9+#.-]+",

        normalize_text(
            text
        ).lower(),

    )


# ============================================================
# SIMILARITY
# ============================================================

def concept_similarity(
    topic_a: str,
    topic_b: str,
) -> float:

    a = normalize_key(
        topic_a
    )

    b = normalize_key(
        topic_b
    )

    if not a or not b:

        return 0.0

    if a == b:

        return 1.0

    if (
        a in b
        or
        b in a
    ):

        return 0.9

    a_tokens = set(
        tokenize(a)
    )

    b_tokens = set(
        tokenize(b)
    )

    if not a_tokens or not b_tokens:

        return 0.0

    intersection = (
        a_tokens
        &
        b_tokens
    )

    union = (
        a_tokens
        |
        b_tokens
    )

    return len(
        intersection
    ) / len(
        union
    )


# ============================================================
# CONCEPT EXTRACTION
# ============================================================

def extract_concepts(
    topic: str,
) -> List[Concept]:

    """
    Lightweight deterministic concept extraction.

    This does not require an LLM and is intentionally
    safe as a fallback when Groq is unavailable.
    """

    topic_clean = normalize_text(
        topic
    )

    if not topic_clean:

        return []

    concepts = []

    concepts.append(

        Concept(

            name=topic_clean,

            description=(

                f"Core concepts and practical "
                f"applications related to "
                f"{topic_clean}."

            ),

            category="Core",

            difficulty="Intermediate",

            bloom_level="Understand",

            learning_objectives=[

                (
                    f"Explain the fundamentals "
                    f"of {topic_clean}."
                ),

                (
                    f"Apply {topic_clean} "
                    f"to practical problems."
                ),

            ],

        )

    )

    return concepts


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/6
#
# RULE-BASED CONCEPT INTELLIGENCE
# ============================================================


DIFFICULTY_KEYWORDS = {

    "beginner": [

        "introduction",

        "basic",

        "fundamentals",

        "overview",

        "getting started",

    ],

    "intermediate": [

        "classification",

        "regression",

        "clustering",

        "optimization",

        "deployment",

        "api",

        "database",

    ],

    "advanced": [

        "transformer",

        "fine tuning",

        "fine-tuning",

        "reinforcement learning",

        "distributed",

        "multi agent",

        "agentic",

        "llmops",

        "rag",

        "architecture",

    ],

}


BLOOM_KEYWORDS = {

    "Remember": [

        "define",

        "list",

        "identify",

        "recall",

    ],

    "Understand": [

        "explain",

        "describe",

        "understand",

        "overview",

    ],

    "Apply": [

        "implement",

        "use",

        "apply",

        "build",

        "develop",

    ],

    "Analyze": [

        "analyze",

        "compare",

        "evaluate",

        "debug",

    ],

    "Create": [

        "design",

        "create",

        "develop",

        "architect",

        "build",

    ],

}


INDUSTRY_KEYWORDS = {

    "High": [

        "deployment",

        "production",

        "api",

        "cloud",

        "docker",

        "kubernetes",

        "rag",

        "llm",

        "agentic",

        "machine learning",

        "deep learning",

    ],

    "Medium": [

        "python",

        "sql",

        "statistics",

        "pandas",

        "numpy",

        "scikit",

    ],

}


def infer_difficulty(
    topic: str,
) -> str:

    text = normalize_key(
        topic
    )

    for level in [

        "advanced",

        "intermediate",

        "beginner",

    ]:

        for keyword in (
            DIFFICULTY_KEYWORDS[
                level
            ]
        ):

            if keyword in text:

                return level.title()

    return "Intermediate"


def infer_bloom_level(
    topic: str,
) -> str:

    text = normalize_key(
        topic
    )

    for level in [

        "Create",

        "Analyze",

        "Apply",

        "Understand",

        "Remember",

    ]:

        for keyword in (
            BLOOM_KEYWORDS[
                level
            ]
        ):

            if keyword in text:

                return level

    return "Understand"


def infer_industry_relevance(
    topic: str,
) -> str:

    text = normalize_key(
        topic
    )

    for relevance in [

        "High",

        "Medium",

    ]:

        for keyword in (
            INDUSTRY_KEYWORDS[
                relevance
            ]
        ):

            if keyword in text:

                return relevance

    return "Medium"


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/6
#
# PREREQUISITES + SKILLS
# ============================================================


PREREQUISITE_MAP = {

    "machine learning": [

        "Python",

        "NumPy",

        "Pandas",

        "Statistics",

    ],

    "deep learning": [

        "Python",

        "Machine Learning",

        "Linear Algebra",

        "Probability",

    ],

    "natural language processing": [

        "Python",

        "Machine Learning",

        "Text Processing",

    ],

    "nlp": [

        "Python",

        "Machine Learning",

        "Text Processing",

    ],

    "generative ai": [

        "Python",

        "Machine Learning",

        "Deep Learning",

        "NLP",

    ],

    "rag": [

        "Python",

        "Embeddings",

        "Vector Databases",

        "LLMs",

    ],

    "agentic ai": [

        "Python",

        "LLMs",

        "Prompt Engineering",

        "APIs",

    ],

    "llmops": [

        "Python",

        "LLMs",

        "Docker",

        "Cloud",

    ],

    "computer vision": [

        "Python",

        "NumPy",

        "Deep Learning",

        "Image Processing",

    ],

}


SKILL_MAP = {

    "python": [

        "Python Programming",

    ],

    "machine learning": [

        "Machine Learning",

        "Model Development",

    ],

    "deep learning": [

        "Deep Learning",

        "Neural Networks",

    ],

    "natural language processing": [

        "NLP",

        "Text Processing",

    ],

    "nlp": [

        "NLP",

        "Text Processing",

    ],

    "generative ai": [

        "Generative AI",

        "LLM Engineering",

    ],

    "rag": [

        "Retrieval Augmented Generation",

        "Vector Search",

    ],

    "agentic ai": [

        "Agentic AI",

        "AI Agents",

    ],

    "computer vision": [

        "Computer Vision",

        "Image Processing",

    ],

    "docker": [

        "Containerization",

    ],

    "kubernetes": [

        "Container Orchestration",

    ],

    "sql": [

        "SQL",

        "Database Management",

    ],

}


TOOL_MAP = {

    "python": [

        "Python",

    ],

    "machine learning": [

        "scikit-learn",

    ],

    "deep learning": [

        "PyTorch",

        "TensorFlow",

    ],

    "generative ai": [

        "Hugging Face",

        "Groq",

    ],

    "rag": [

        "FAISS",

        "Chroma",

    ],

    "docker": [

        "Docker",

    ],

    "kubernetes": [

        "Kubernetes",

    ],

}


def infer_prerequisites(
    topic: str,
) -> List[str]:

    text = normalize_key(
        topic
    )

    results = []

    for key, values in (
        PREREQUISITE_MAP.items()
    ):

        if key in text:

            results.extend(
                values
            )

    return unique_strings(
        results
    )


def infer_skills(
    topic: str,
) -> List[str]:

    text = normalize_key(
        topic
    )

    results = []

    for key, values in (
        SKILL_MAP.items()
    ):

        if key in text:

            results.extend(
                values
            )

    if not results:

        results.append(
            topic
        )

    return unique_strings(
        results
    )


def infer_tools(
    topic: str,
) -> List[str]:

    text = normalize_key(
        topic
    )

    results = []

    for key, values in (
        TOOL_MAP.items()
    ):

        if key in text:

            results.extend(
                values
            )

    return unique_strings(
        results
    )


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/6
#
# TOPIC ENRICHMENT
# ============================================================


def create_learning_objectives(
    topic: str,
    bloom_level: str,
) -> List[str]:

    topic = normalize_text(
        topic
    )

    if bloom_level == "Remember":

        return [

            f"Identify the key concepts "
            f"of {topic}.",

            f"Recall important terminology "
            f"used in {topic}.",

        ]

    if bloom_level == "Understand":

        return [

            f"Explain the core principles "
            f"of {topic}.",

            f"Describe practical applications "
            f"of {topic}.",

        ]

    if bloom_level == "Apply":

        return [

            f"Implement {topic} "
            f"in a practical exercise.",

            f"Apply {topic} to "
            f"a real-world problem.",

        ]

    if bloom_level == "Analyze":

        return [

            f"Analyze approaches used "
            f"in {topic}.",

            f"Compare alternative solutions "
            f"for {topic}.",

        ]

    return [

        f"Design a practical solution "
        f"using {topic}.",

        f"Build a project demonstrating "
        f"mastery of {topic}.",

    ]


def enrich_topic(
    topic: str,
) -> TopicEnrichment:

    topic = normalize_text(
        topic
    )

    difficulty = infer_difficulty(
        topic
    )

    bloom_level = infer_bloom_level(
        topic
    )

    industry_relevance = (
        infer_industry_relevance(
            topic
        )
    )

    prerequisites = (
        infer_prerequisites(
            topic
        )
    )

    skills = infer_skills(
        topic
    )

    tools = infer_tools(
        topic
    )

    concepts = extract_concepts(
        topic
    )

    learning_objectives = (
        create_learning_objectives(

            topic,

            bloom_level,

        )
    )

    # --------------------------------------------------------
    # Update concepts
    # --------------------------------------------------------

    for concept in concepts:

        concept.difficulty = (
            difficulty
        )

        concept.bloom_level = (
            bloom_level
        )

        concept.prerequisites = (
            prerequisites.copy()
        )

        concept.skills = (
            skills.copy()
        )

        concept.tools = (
            tools.copy()
        )

        concept.industry_relevance = (
            industry_relevance
        )

        concept.learning_objectives = (
            learning_objectives.copy()
        )

    return TopicEnrichment(

        topic=topic,

        concepts=concepts,

        prerequisites=prerequisites,

        skills=skills,

        tools=tools,

        difficulty=difficulty,

        bloom_level=bloom_level,

        industry_relevance=(
            industry_relevance
        ),

        learning_objectives=(
            learning_objectives
        ),

    )


def enrich_topics(
    topics: Sequence[Any],
) -> List[TopicEnrichment]:

    """
    Enrich multiple curriculum topics.

    Compatible with:

        enrich_topics(["Python", "RAG"])

    and:

        enrich_topics(
            [
                {"name": "Python"},
                {"name": "RAG"}
            ]
        )
    """

    results = []

    for topic in topics:

        if isinstance(
            topic,
            dict,
        ):

            topic_name = (

                topic.get(
                    "name"
                )

                or

                topic.get(
                    "title"
                )

                or

                topic.get(
                    "topic"
                )

            )

        else:

            topic_name = (

                getattr(
                    topic,
                    "name",
                    None,
                )

                or

                getattr(
                    topic,
                    "title",
                    None,
                )

                or

                getattr(
                    topic,
                    "topic",
                    None,
                )

                or

                topic

            )

        topic_name = normalize_text(
            topic_name
        )

        if not topic_name:

            continue

        results.append(

            enrich_topic(
                topic_name
            )

        )

    return results


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/6
#
# SERIALIZATION + PUBLIC API
# ============================================================


def concept_to_dict(
    concept: Concept,
) -> Dict[str, Any]:

    return {

        "name":
            concept.name,

        "description":
            concept.description,

        "category":
            concept.category,

        "difficulty":
            concept.difficulty,

        "bloom_level":
            concept.bloom_level,

        "prerequisites":
            concept.prerequisites,

        "skills":
            concept.skills,

        "tools":
            concept.tools,

        "technologies":
            concept.technologies,

        "industry_relevance":
            concept.industry_relevance,

        "learning_objectives":
            concept.learning_objectives,

    }


def enrichment_to_dict(
    enrichment: TopicEnrichment,
) -> Dict[str, Any]:

    return {

        "topic":
            enrichment.topic,

        "concepts": [

            concept_to_dict(
                concept
            )

            for concept
            in enrichment.concepts

        ],

        "prerequisites":
            enrichment.prerequisites,

        "skills":
            enrichment.skills,

        "tools":
            enrichment.tools,

        "technologies":
            enrichment.technologies,

        "difficulty":
            enrichment.difficulty,

        "bloom_level":
            enrichment.bloom_level,

        "industry_relevance":
            enrichment.industry_relevance,

        "learning_objectives":
            enrichment.learning_objectives,

    }


def enrich_topics_as_dict(
    topics: Sequence[Any],
) -> List[Dict[str, Any]]:

    enrichments = enrich_topics(
        topics
    )

    return [

        enrichment_to_dict(
            enrichment
        )

        for enrichment
        in enrichments

    ]


# ============================================================
# SINGLE TOPIC ALIAS
# ============================================================


def enrich_single_topic(
    topic: Any,
) -> TopicEnrichment:

    return enrich_topic(
        topic
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [

    "Concept",

    "TopicEnrichment",

    "normalize_text",

    "normalize_key",

    "unique_strings",

    "concept_similarity",

    "extract_concepts",

    "infer_difficulty",

    "infer_bloom_level",

    "infer_industry_relevance",

    "infer_prerequisites",

    "infer_skills",

    "infer_tools",

    "create_learning_objectives",

    "enrich_topic",

    "enrich_topics",

    "enrich_topics_as_dict",

    "enrich_single_topic",

    "concept_to_dict",

    "enrichment_to_dict",

]


# ============================================================
# END OF FILE
# ============================================================
