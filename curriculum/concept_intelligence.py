# ============================================================
# curriculum/concept_intelligence.py
# CHUNK 1/10
#
# CONCEPT INTELLIGENCE ENGINE
#
# Purpose:
#   Analyze curriculum concepts at a deeper level than simple
#   keyword matching.
#
# Pipeline:
#
# Curriculum
#     │
#     ▼
# Concept Extraction
#     │
#     ▼
# Concept Normalization
#     │
#     ├── Classification
#     ├── Difficulty
#     ├── Prerequisites
#     ├── Dependencies
#     ├── Relationships
#     ├── Industry Relevance
#     ├── Employability
#     └── Learning Recommendations
#              │
#              ▼
#       Concept Intelligence
#
# Designed to work with:
#   - curriculum/models.py
#   - curriculum/extractor.py
#   - curriculum/comparator.py
#   - 04_🔍_Gap_Enhancement.py
#   - 05_📊_Reports.py
#
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

from __future__ import annotations


import json

import math

import re

from dataclasses import (
    dataclass,
    field,
    asdict,
)

from pathlib import Path

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)


# ============================================================
# 2. OPTIONAL NUMPY
# ============================================================

try:

    import numpy as np

except ImportError:

    np = None


# ============================================================
# 3. OPTIONAL SKLEARN
# ============================================================

try:

    from sklearn.feature_extraction.text import (
        TfidfVectorizer,
    )

    from sklearn.metrics.pairwise import (
        cosine_similarity,
    )

except ImportError:

    TfidfVectorizer = None

    cosine_similarity = None


# ============================================================
# 4. MODULE VERSION
# ============================================================

CONCEPT_INTELLIGENCE_VERSION = "1.0.0"


# ============================================================
# 5. CONCEPT TYPES
# ============================================================

CONCEPT_TYPE_UNKNOWN = "unknown"

CONCEPT_TYPE_FOUNDATION = "foundation"

CONCEPT_TYPE_CONCEPT = "concept"

CONCEPT_TYPE_ALGORITHM = "algorithm"

CONCEPT_TYPE_MODEL = "model"

CONCEPT_TYPE_TECHNOLOGY = "technology"

CONCEPT_TYPE_TOOL = "tool"

CONCEPT_TYPE_FRAMEWORK = "framework"

CONCEPT_TYPE_LIBRARY = "library"

CONCEPT_TYPE_PLATFORM = "platform"

CONCEPT_TYPE_SKILL = "skill"

CONCEPT_TYPE_METHOD = "method"

CONCEPT_TYPE_ARCHITECTURE = "architecture"

CONCEPT_TYPE_PATTERN = "pattern"

CONCEPT_TYPE_PROJECT = "project"

CONCEPT_TYPE_DOMAIN = "domain"

CONCEPT_TYPE_SOFTWARE = "software"

CONCEPT_TYPE_CLOUD = "cloud"

CONCEPT_TYPE_DATABASE = "database"

CONCEPT_TYPE_SECURITY = "security"

CONCEPT_TYPE_EVALUATION = "evaluation"

CONCEPT_TYPE_DEPLOYMENT = "deployment"

CONCEPT_TYPE_OTHER = "other"


# ============================================================
# 6. DIFFICULTY LEVELS
# ============================================================

DIFFICULTY_BEGINNER = "Beginner"

DIFFICULTY_INTERMEDIATE = "Intermediate"

DIFFICULTY_ADVANCED = "Advanced"

DIFFICULTY_EXPERT = "Expert"


DIFFICULTY_ORDER = {

    DIFFICULTY_BEGINNER: 1,

    DIFFICULTY_INTERMEDIATE: 2,

    DIFFICULTY_ADVANCED: 3,

    DIFFICULTY_EXPERT: 4,

}


# ============================================================
# 7. CONCEPT IMPORTANCE
# ============================================================

IMPORTANCE_LOW = "Low"

IMPORTANCE_MEDIUM = "Medium"

IMPORTANCE_HIGH = "High"

IMPORTANCE_CRITICAL = "Critical"


IMPORTANCE_ORDER = {

    IMPORTANCE_LOW: 1,

    IMPORTANCE_MEDIUM: 2,

    IMPORTANCE_HIGH: 3,

    IMPORTANCE_CRITICAL: 4,

}


# ============================================================
# 8. CONCEPT STATUS
# ============================================================

STATUS_PRESENT = "present"

STATUS_MISSING = "missing"

STATUS_PARTIAL = "partial"

STATUS_DUPLICATE = "duplicate"

STATUS_OUTDATED = "outdated"

STATUS_EMERGING = "emerging"


# ============================================================
# 9. RELATIONSHIP TYPES
# ============================================================

REL_PREREQUISITE = "prerequisite"

REL_DEPENDS_ON = "depends_on"

REL_RELATED_TO = "related_to"

REL_PART_OF = "part_of"

REL_VARIANT_OF = "variant_of"

REL_EXTENDS = "extends"

REL_REQUIRES = "requires"

REL_USED_WITH = "used_with"

REL_ALTERNATIVE_TO = "alternative_to"

REL_FOLLOWED_BY = "followed_by"

REL_PRECEDES = "precedes"

REL_APPLICATION_OF = "application_of"


# ============================================================
# 10. CONCEPT DOMAIN
# ============================================================

DOMAIN_GENERAL = "General"

DOMAIN_PROGRAMMING = "Programming"

DOMAIN_DATA_SCIENCE = "Data Science"

DOMAIN_MACHINE_LEARNING = "Machine Learning"

DOMAIN_DEEP_LEARNING = "Deep Learning"

DOMAIN_NLP = "Natural Language Processing"

DOMAIN_GENERATIVE_AI = "Generative AI"

DOMAIN_AGENTIC_AI = "Agentic AI"

DOMAIN_COMPUTER_VISION = "Computer Vision"

DOMAIN_DATA_ENGINEERING = "Data Engineering"

DOMAIN_MLOPS = "MLOps"

DOMAIN_LLMOPS = "LLMOps"

DOMAIN_CLOUD = "Cloud Computing"

DOMAIN_DATABASE = "Database"

DOMAIN_DEVOPS = "DevOps"

DOMAIN_CYBERSECURITY = "Cybersecurity"

DOMAIN_SOFTWARE_ENGINEERING = "Software Engineering"

DOMAIN_BUSINESS_INTELLIGENCE = "Business Intelligence"

DOMAIN_ANALYTICS = "Analytics"


# ============================================================
# 11. NORMALIZATION
# ============================================================

def clean_text(
    value: Any,
) -> str:
    """
    Normalize arbitrary values into clean text.
    """

    if value is None:

        return ""


    text = str(
        value
    )


    text = text.replace(
        "\n",
        " ",
    )


    text = text.replace(
        "\r",
        " ",
    )


    text = re.sub(
        r"\s+",
        " ",
        text,
    )


    return text.strip()


# ============================================================
# 12. CANONICAL CONCEPT
# ============================================================

def canonical_concept(
    value: Any,
) -> str:
    """
    Generate canonical representation for concept matching.
    """

    text = clean_text(
        value
    ).lower()


    # --------------------------------------------------------
    # Common aliases
    # --------------------------------------------------------

    aliases = {

        "gen ai":
            "generative ai",

        "genai":
            "generative ai",

        "artificial intelligence":
            "ai",

        "machine-learning":
            "machine learning",

        "deep-learning":
            "deep learning",

        "natural-language-processing":
            "natural language processing",

        "large language models":
            "large language model",

        "llms":
            "large language model",

        "rag":
            "retrieval augmented generation",

        "retrieval-augmented generation":
            "retrieval augmented generation",

        "mlops":
            "machine learning operations",

        "llmops":
            "large language model operations",

        "cv":
            "computer vision",

        "nlp":
            "natural language processing",

    }


    text = aliases.get(
        text,
        text,
    )


    text = re.sub(
        r"[^a-z0-9+#./ -]",
        "",
        text,
    )


    text = re.sub(
        r"\s+",
        " ",
        text,
    )


    return text.strip()


# ============================================================
# 13. TOKENIZE CONCEPT
# ============================================================

def concept_tokens(
    value: Any,
) -> List[str]:
    """
    Tokenize concept text.
    """

    text = canonical_concept(
        value
    )


    if not text:

        return []


    return [

        token

        for token
        in re.split(
            r"[\s,;/|:_()\-]+",
            text,
        )

        if token

    ]


# ============================================================
# 14. SAFE FLOAT
# ============================================================

def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert value to float.
    """

    try:

        result = float(
            value
        )


        if math.isnan(
            result
        ):

            return default


        if math.isinf(
            result
        ):

            return default


        return result

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# 15. CLAMP
# ============================================================

def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    """
    Clamp numerical value.
    """

    return max(

        minimum,

        min(
            maximum,
            safe_float(
                value
            ),
        ),

    )


# ============================================================
# 16. DEDUPLICATE
# ============================================================

def deduplicate(
    values: Iterable[Any],
) -> List[Any]:
    """
    Preserve order while removing duplicates.
    """

    result = []

    seen = set()


    for value in values:

        key = canonical_concept(
            value
        )


        if not key:

            continue


        if key in seen:

            continue


        seen.add(
            key
        )


        result.append(
            value
        )


    return result


# ============================================================
# 17. PERCENTAGE
# ============================================================

def percentage(
    numerator: float,
    denominator: float,
) -> float:
    """
    Calculate percentage safely.
    """

    denominator = safe_float(
        denominator
    )


    if denominator <= 0:

        return 0.0


    return round(

        clamp(

            (
                safe_float(
                    numerator
                )
                /
                denominator
            )
            *
            100.0

        ),

        0.0,

        100.0,

        ),

        2,

    )


# ============================================================
# 18. CONCEPT INTELLIGENCE CONFIG
# ============================================================

@dataclass
class ConceptIntelligenceConfig:
    """
    Configuration for concept intelligence analysis.
    """

    similarity_threshold: float = 0.70

    partial_similarity_threshold: float = 0.45

    important_concept_threshold: float = 0.70

    emerging_concept_threshold: float = 0.65

    max_prerequisites: int = 10

    max_related_concepts: int = 15

    max_recommendations: int = 20

    include_tools: bool = True

    include_projects: bool = True

    include_prerequisites: bool = True

    include_industry_analysis: bool = True

    include_employability_analysis: bool = True


# ============================================================
# 19. CONCEPT RELATIONSHIP
# ============================================================

@dataclass
class ConceptRelationship:
    """
    Relationship between two concepts.
    """

    source: str

    target: str

    relationship_type: str

    confidence: float = 0.0

    strength: float = 0.0

    rationale: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# 20. CONCEPT PROFILE
# ============================================================

@dataclass
class ConceptProfile:
    """
    Deep intelligence profile for one concept.
    """

    concept_id: str

    name: str

    canonical_name: str

    concept_type: str = CONCEPT_TYPE_UNKNOWN

    domain: str = DOMAIN_GENERAL

    difficulty: str = DIFFICULTY_BEGINNER

    importance: str = IMPORTANCE_MEDIUM

    description: str = ""

    keywords: List[str] = field(
        default_factory=list
    )

    aliases: List[str] = field(
        default_factory=list
    )

    prerequisites: List[str] = field(
        default_factory=list
    )

    dependencies: List[str] = field(
        default_factory=list
    )

    related_concepts: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    technologies: List[str] = field(
        default_factory=list
    )

    frameworks: List[str] = field(
        default_factory=list
    )

    skills: List[str] = field(
        default_factory=list
    )

    applications: List[str] = field(
        default_factory=list
    )

    projects: List[str] = field(
        default_factory=list
    )

    industry_relevance: float = 0.0

    employability_impact: float = 0.0

    learning_impact: float = 0.0

    prerequisite_impact: float = 0.0

    emerging_score: float = 0.0

    maturity_score: float = 0.0

    confidence_score: float = 0.0

    occurrence_count: int = 1

    module_names: List[str] = field(
        default_factory=list
    )

    topic_names: List[str] = field(
        default_factory=list
    )

    status: str = STATUS_PRESENT

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# 21. CONCEPT MATCH
# ============================================================

@dataclass
class ConceptMatch:
    """
    Represents a match between two concepts.
    """

    source_concept: str

    target_concept: str

    similarity: float = 0.0

    lexical_similarity: float = 0.0

    semantic_similarity: float = 0.0

    token_overlap: float = 0.0

    status: str = STATUS_PARTIAL

    confidence: float = 0.0

    rationale: str = ""


# ============================================================
# 22. CONCEPT GAP
# ============================================================

@dataclass
class ConceptGap:
    """
    Represents a missing or weak concept.
    """

    concept: str

    gap_type: str = STATUS_MISSING

    severity: str = IMPORTANCE_MEDIUM

    priority_score: float = 0.0

    source_present: bool = True

    target_present: bool = False

    best_match: Optional[str] = None

    similarity: float = 0.0

    industry_relevance: float = 0.0

    employability_impact: float = 0.0

    learning_impact: float = 0.0

    prerequisite_impact: float = 0.0

    prerequisites: List[str] = field(
        default_factory=list
    )

    recommended_topics: List[str] = field(
        default_factory=list
    )

    recommended_tools: List[str] = field(
        default_factory=list
    )

    recommended_project: Optional[str] = None

    rationale: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# 23. CONCEPT RECOMMENDATION
# ============================================================

@dataclass
class ConceptRecommendation:
    """
    Learning recommendation generated from concept
    intelligence.
    """

    concept: str

    recommendation_type: str

    title: str

    description: str = ""

    priority: str = IMPORTANCE_MEDIUM

    estimated_hours: float = 0.0

    prerequisites: List[str] = field(
        default_factory=list
    )

    topics: List[str] = field(
        default_factory=list
    )

    activities: List[str] = field(
        default_factory=list
    )

    assessment_methods: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    project: Optional[str] = None

    expected_impact: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# 24. CONCEPT INTELLIGENCE RESULT
# ============================================================

@dataclass
class ConceptIntelligenceResult:
    """
    Complete concept intelligence analysis.
    """

    concepts: List[
        ConceptProfile
    ] = field(
        default_factory=list
    )

    relationships: List[
        ConceptRelationship
    ] = field(
        default_factory=list
    )

    matches: List[
        ConceptMatch
    ] = field(
        default_factory=list
    )

    gaps: List[
        ConceptGap
    ] = field(
        default_factory=list
    )

    recommendations: List[
        ConceptRecommendation
    ] = field(
        default_factory=list
    )

    summary: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# 25. END OF CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# CONCEPT EXTRACTION ENGINE
# ============================================================


# ============================================================
# 26. CONCEPT ID
# ============================================================

def generate_concept_id(
    name: str,
) -> str:
    """
    Generate stable concept identifier.
    """

    canonical = canonical_concept(
        name
    )


    canonical = canonical.replace(
        " ",
        "_",
    )


    canonical = re.sub(
        r"[^a-z0-9_+#./-]",
        "",
        canonical,
    )


    return (
        f"concept_{canonical}"
    )


# ============================================================
# 27. TEXT CONCEPT PATTERNS
# ============================================================

CONCEPT_PATTERNS = [

    r"\bmachine learning\b",

    r"\bdeep learning\b",

    r"\bgenerative ai\b",

    r"\bartificial intelligence\b",

    r"\bnatural language processing\b",

    r"\bcomputer vision\b",

    r"\blarge language models?\b",

    r"\bretrieval augmented generation\b",

    r"\brag\b",

    r"\bai agents?\b",

    r"\bagentic ai\b",

    r"\bprompt engineering\b",

    r"\bembeddings?\b",

    r"\bvector databases?\b",

    r"\btransformers?\b",

    r"\battention mechanisms?\b",

    r"\bneural networks?\b",

    r"\bconvolutional neural networks?\b",

    r"\brecurrent neural networks?\b",

    r"\bclassification\b",

    r"\bregression\b",

    r"\bclustering\b",

    r"\brecommendation systems?\b",

    r"\btime series\b",

    r"\banomaly detection\b",

    r"\bdata visualization\b",

    r"\bstatistics\b",

    r"\bprobability\b",

    r"\bsql\b",

    r"\bpython\b",

    r"\bjava\b",

    r"\bc\+\+\b",

    r"\bjavascript\b",

    r"\bdocker\b",

    r"\bkubernetes\b",

    r"\bmlops\b",

    r"\bllmops\b",

    r"\bdevops\b",

    r"\baws\b",

    r"\bazure\b",

    r"\bgcp\b",

    r"\bfastapi\b",

    r"\bstreamlit\b",

    r"\blangchain\b",

    r"\blanggraph\b",

    r"\bhugging face\b",

    r"\bpytorch\b",

    r"\btensorflow\b",

    r"\bscikit[- ]learn\b",

    r"\bopencv\b",

]


# ============================================================
# 28. EXTRACT CONCEPTS FROM TEXT
# ============================================================

def extract_concepts_from_text(
    text: str,
) -> List[str]:
    """
    Extract known concepts from arbitrary text.
    """

    text = clean_text(
        text
    )


    if not text:

        return []


    concepts = []


    for pattern in CONCEPT_PATTERNS:

        matches = re.findall(

            pattern,

            text,

            flags=re.IGNORECASE,

        )


        concepts.extend(
            matches
        )


    return deduplicate(
        concepts
    )


# ============================================================
# 29. EXTRACT CANDIDATE PHRASES
# ============================================================

def extract_candidate_phrases(
    text: str,
    min_words: int = 1,
    max_words: int = 5,
) -> List[str]:
    """
    Extract noun-like candidate phrases.

    This intentionally uses lightweight NLP so the module
    remains usable without spaCy.
    """

    text = clean_text(
        text
    )


    if not text:

        return []


    sentences = re.split(

        r"[.;,\n]",

        text,

    )


    candidates = []


    stopwords = {

        "the",
        "and",
        "or",
        "of",
        "to",
        "in",
        "for",
        "with",
        "using",
        "use",
        "from",
        "on",
        "by",
        "a",
        "an",
        "is",
        "are",
        "into",
        "through",
        "this",
        "that",
        "will",
        "can",
        "basic",
        "advanced",

    }


    for sentence in sentences:

        tokens = re.findall(

            r"[A-Za-z0-9+#./-]+",

            sentence,

        )


        if not tokens:

            continue


        for size in range(

            min_words,

            min(
                max_words,
                len(tokens),
            ) + 1,

        ):

            for index in range(

                0,

                len(tokens) - size + 1,

            ):

                phrase_tokens = (
                    tokens[
                        index:
                        index + size
                    ]
                )


                normalized = [

                    token.lower()

                    for token
                    in phrase_tokens

                ]


                if all(

                    token in stopwords

                    for token
                    in normalized

                ):

                    continue


                meaningful = [

                    token

                    for token
                    in normalized

                    if token not in stopwords

                ]


                if not meaningful:

                    continue


                phrase = " ".join(
                    meaningful
                )


                if len(phrase) < 3:

                    continue


                candidates.append(
                    phrase
                )


    return deduplicate(
        candidates
    )


# ============================================================
# 30. EXTRACT CONCEPTS FROM LIST
# ============================================================

def extract_concepts_from_items(
    items: Sequence[Any],
) -> List[str]:
    """
    Extract concepts from list-like curriculum items.
    """

    concepts = []


    for item in items:

        if item is None:

            continue


        if isinstance(
            item,
            str,
        ):

            concepts.extend(

                extract_concepts_from_text(
                    item
                )

            )

            # Also preserve short curriculum labels.
            if len(
                item.split()
            ) <= 8:

                concepts.append(
                    item
                )


            continue


        if isinstance(
            item,
            dict,
        ):

            for key in (

                "name",
                "title",
                "topic",
                "concept",
                "description",
                "content",

            ):

                if key in item:

                    value = item.get(
                        key
                    )


                    if value:

                        concepts.extend(

                            extract_concepts_from_text(
                                str(value)
                            )

                        )


                        if isinstance(
                            value,
                            str,
                        ) and len(
                            value.split()
                        ) <= 8:

                            concepts.append(
                                value
                            )


    return deduplicate(
        concepts
    )


# ============================================================
# 31. EXTRACT CONCEPTS FROM CURRICULUM OBJECT
# ============================================================

def extract_concepts_from_curriculum(
    curriculum: Any,
) -> List[str]:
    """
    Extract concepts from a flexible curriculum object.

    Supports:
        dict
        dataclass
        pydantic-like object
        list
        plain text
    """

    if curriculum is None:

        return []


    if isinstance(
        curriculum,
        str,
    ):

        return extract_concepts_from_text(
            curriculum
        )


    if isinstance(
        curriculum,
        (list, tuple, set),
    ):

        return extract_concepts_from_items(
            list(
                curriculum
            )
        )


    concepts = []


    # --------------------------------------------------------
    # Dictionary curriculum
    # --------------------------------------------------------

    if isinstance(
        curriculum,
        dict,
    ):

        preferred_fields = [

            "modules",

            "topics",

            "concepts",

            "skills",

            "technologies",

            "tools",

            "projects",

            "course_outcomes",

            "program_outcomes",

            "description",

            "content",

        ]


        for field_name in preferred_fields:

            if field_name not in curriculum:

                continue


            value = curriculum.get(
                field_name
            )


            if isinstance(
                value,
                str,
            ):

                concepts.extend(

                    extract_concepts_from_text(
                        value
                    )

                )


            elif isinstance(
                value,
                (list, tuple, set),
            ):

                concepts.extend(

                    extract_concepts_from_items(
                        list(value)
                    )

                )


            elif isinstance(
                value,
                dict,
            ):

                concepts.extend(

                    extract_concepts_from_curriculum(
                        value
                    )

                )


        return deduplicate(
            concepts
        )


    # --------------------------------------------------------
    # Object/dataclass curriculum
    # --------------------------------------------------------

    for field_name in (

        "modules",
        "topics",
        "concepts",
        "skills",
        "technologies",
        "tools",
        "projects",
        "course_outcomes",
        "program_outcomes",
        "description",
        "content",

    ):

        if not hasattr(
            curriculum,
            field_name,
        ):

            continue


        try:

            value = getattr(

                curriculum,

                field_name,

            )

        except Exception:

            continue


        if value is None:

            continue


        if isinstance(
            value,
            str,
        ):

            concepts.extend(

                extract_concepts_from_text(
                    value
                )

            )


        elif isinstance(
            value,
            (list, tuple, set),
        ):

            concepts.extend(

                extract_concepts_from_items(
                    list(value)
                )

            )


        elif isinstance(
            value,
            dict,
        ):

            concepts.extend(

                extract_concepts_from_curriculum(
                    value
                )

            )


    return deduplicate(
        concepts
    )


# ============================================================
# 32. EXTRACT MODULE NAMES
# ============================================================

def extract_module_names(
    curriculum: Any,
) -> List[str]:
    """
    Extract module names from curriculum.
    """

    if curriculum is None:

        return []


    if isinstance(
        curriculum,
        dict,
    ):

        modules = curriculum.get(
            "modules",
            [],
        )

    else:

        modules = getattr(

            curriculum,

            "modules",

            [],

        )


    result = []


    if isinstance(
        modules,
        dict,
    ):

        modules = list(
            modules.values()
        )


    for module in modules or []:

        if isinstance(
            module,
            str,
        ):

            result.append(
                module
            )

        elif isinstance(
            module,
            dict,
        ):

            value = (

                module.get(
                    "name"
                )

                or

                module.get(
                    "title"
                )

            )


            if value:

                result.append(
                    str(value)
                )

        else:

            value = (

                getattr(
                    module,
                    "name",
                    None,
                )

                or

                getattr(
                    module,
                    "title",
                    None,
                )

            )


            if value:

                result.append(
                    str(value)
                )


    return deduplicate(
        result
    )


# ============================================================
# 33. EXTRACT TOPIC NAMES
# ============================================================

def extract_topic_names(
    curriculum: Any,
) -> List[str]:
    """
    Extract topic names.
    """

    if curriculum is None:

        return []


    if isinstance(
        curriculum,
        dict,
    ):

        topics = curriculum.get(
            "topics",
            [],
        )

    else:

        topics = getattr(

            curriculum,

            "topics",

            [],

        )


    result = []


    if isinstance(
        topics,
        dict,
    ):

        topics = list(
            topics.values()
        )


    for topic in topics or []:

        if isinstance(
            topic,
            str,
        ):

            result.append(
                topic
            )

        elif isinstance(
            topic,
            dict,
        ):

            value = (

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


            if value:

                result.append(
                    str(value)
                )


        else:

            value = (

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

            )


            if value:

                result.append(
                    str(value)
                )


    return deduplicate(
        result
    )


# ============================================================
# 34. BUILD CONCEPT OCCURRENCES
# ============================================================

def build_concept_occurrences(
    concepts: Sequence[str],
) -> Dict[str, int]:
    """
    Count normalized concept occurrences.
    """

    occurrences = {}


    for concept in concepts:

        key = canonical_concept(
            concept
        )


        if not key:

            continue


        occurrences[key] = (

            occurrences.get(
                key,
                0,
            )
            +
            1

        )


    return occurrences


# ============================================================
# 35. END OF CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# CONCEPT CLASSIFICATION ENGINE
# ============================================================

# ============================================================
# 36. CLASSIFICATION KEYWORDS
# ============================================================

CONCEPT_CLASSIFICATION_RULES = {

    CONCEPT_TYPE_ALGORITHM: [

        "algorithm",

        "gradient descent",

        "random forest",

        "decision tree",

        "k means",

        "k-means",

        "knn",

        "support vector",

        "naive bayes",

        "xgboost",

        "lightgbm",

        "backpropagation",

    ],

    CONCEPT_TYPE_MODEL: [

        "model",

        "bert",

        "gpt",

        "llama",

        "resnet",

        "vgg",

        "inception",

        "yolo",

        "transformer",

        "cnn",

        "rnn",

        "lstm",

        "gru",

        "autoencoder",

        "gan",

        "diffusion",

    ],

    CONCEPT_TYPE_TECHNOLOGY: [

        "machine learning",

        "deep learning",

        "generative ai",

        "artificial intelligence",

        "computer vision",

        "natural language processing",

        "rag",

        "retrieval augmented generation",

        "agentic ai",

        "mlops",

        "llmops",

        "cloud computing",

    ],

    CONCEPT_TYPE_TOOL: [

        "jupyter",

        "postman",

        "git",

        "docker",

        "kubectl",

        "mlflow",

        "tableau",

        "power bi",

    ],

    CONCEPT_TYPE_FRAMEWORK: [

        "langchain",

        "langgraph",

        "tensorflow",

        "pytorch",

        "streamlit",

        "fastapi",

        "django",

        "flask",

        "react",

        "spring",

    ],

    CONCEPT_TYPE_LIBRARY: [

        "numpy",

        "pandas",

        "scikit-learn",

        "opencv",

        "spacy",

        "nltk",

        "matplotlib",

        "plotly",

        "transformers",

    ],

    CONCEPT_TYPE_CLOUD: [

        "aws",

        "azure",

        "gcp",

        "cloud",

        "ec2",

        "s3",

        "lambda",

        "cloud run",

    ],

    CONCEPT_TYPE_DATABASE: [

        "sql",

        "mysql",

        "postgresql",

        "postgres",

        "mongodb",

        "redis",

        "database",

        "vector database",

        "faiss",

        "chroma",

        "pinecone",

    ],

    CONCEPT_TYPE_SECURITY: [

        "cybersecurity",

        "security",

        "authentication",

        "authorization",

        "encryption",

        "prompt injection",

        "llm security",

        "zero trust",

    ],

    CONCEPT_TYPE_DEPLOYMENT: [

        "deployment",

        "production",

        "serving",

        "monitoring",

        "ci/cd",

        "continuous integration",

        "continuous deployment",

    ],

    CONCEPT_TYPE_SKILL: [

        "programming",

        "debugging",

        "problem solving",

        "communication",

        "data analysis",

        "model development",

        "deployment",

        "testing",

        "documentation",

    ],

    CONCEPT_TYPE_PROJECT: [

        "project",

        "capstone",

        "application",

        "system",

        "platform",

        "solution",

    ],

}


# ============================================================
# 37. DOMAIN KEYWORDS
# ============================================================

DOMAIN_RULES = {

    DOMAIN_PROGRAMMING: [

        "python",

        "java",

        "c++",

        "javascript",

        "programming",

        "object oriented",

        "data structures",

        "algorithms",

    ],

    DOMAIN_DATA_SCIENCE: [

        "data science",

        "pandas",

        "numpy",

        "statistics",

        "data analysis",

    ],

    DOMAIN_MACHINE_LEARNING: [

        "machine learning",

        "classification",

        "regression",

        "clustering",

        "feature engineering",

        "model selection",

    ],

    DOMAIN_DEEP_LEARNING: [

        "deep learning",

        "neural network",

        "cnn",

        "rnn",

        "lstm",

        "transformer",

        "pytorch",

        "tensorflow",

    ],

    DOMAIN_NLP: [

        "nlp",

        "natural language processing",

        "text classification",

        "named entity recognition",

        "sentiment analysis",

        "language model",

    ],

    DOMAIN_GENERATIVE_AI: [

        "generative ai",

        "genai",

        "llm",

        "large language model",

        "prompt engineering",

        "rag",

        "retrieval augmented",

    ],

    DOMAIN_AGENTIC_AI: [

        "agentic ai",

        "ai agent",

        "agents",

        "tool calling",

        "function calling",

        "multi agent",

        "langgraph",

    ],

    DOMAIN_COMPUTER_VISION: [

        "computer vision",

        "image classification",

        "object detection",

        "segmentation",

        "opencv",

        "yolo",

        "cnn",

    ],

    DOMAIN_DATA_ENGINEERING: [

        "data engineering",

        "etl",

        "elt",

        "spark",

        "kafka",

        "airflow",

        "data pipeline",

    ],

    DOMAIN_MLOPS: [

        "mlops",

        "model deployment",

        "model serving",

        "model monitoring",

        "mlflow",

        "kubeflow",

    ],

    DOMAIN_LLMOPS: [

        "llmops",

        "llm deployment",

        "llm monitoring",

        "llm evaluation",

        "prompt monitoring",

    ],

    DOMAIN_CLOUD: [

        "aws",

        "azure",

        "gcp",

        "cloud",

        "ec2",

        "s3",

        "lambda",

    ],

    DOMAIN_DATABASE: [

        "sql",

        "database",

        "mysql",

        "postgresql",

        "mongodb",

        "redis",

        "vector database",

    ],

    DOMAIN_DEVOPS: [

        "devops",

        "docker",

        "kubernetes",

        "terraform",

        "jenkins",

        "github actions",

        "ci/cd",

    ],

    DOMAIN_CYBERSECURITY: [

        "cybersecurity",

        "security",

        "authentication",

        "encryption",

        "zero trust",

        "soc",

    ],

    DOMAIN_SOFTWARE_ENGINEERING: [

        "software engineering",

        "system design",

        "architecture",

        "testing",

        "api",

        "version control",

    ],

    DOMAIN_BUSINESS_INTELLIGENCE: [

        "business intelligence",

        "power bi",

        "tableau",

        "dashboard",

        "reporting",

    ],

    DOMAIN_ANALYTICS: [

        "analytics",

        "data visualization",

        "business analytics",

        "predictive analytics",

    ],

}


# ============================================================
# 38. CLASSIFY CONCEPT TYPE
# ============================================================

def classify_concept_type(
    concept: str,
) -> str:
    """
    Classify concept into a high-level type.
    """

    text = canonical_concept(
        concept
    )


    if not text:

        return CONCEPT_TYPE_UNKNOWN


    scores = {}


    for concept_type, keywords in (
        CONCEPT_CLASSIFICATION_RULES.items()
    ):

        score = 0


        for keyword in keywords:

            if keyword in text:

                score += 1


                # Exact concept matches get extra weight.
                if keyword == text:

                    score += 3


        if score:

            scores[
                concept_type
            ] = score


    if not scores:

        return CONCEPT_TYPE_UNKNOWN


    return max(

        scores,

        key=scores.get,

    )


# ============================================================
# 39. CLASSIFY DOMAIN
# ============================================================

def classify_domain(
    concept: str,
) -> str:
    """
    Identify primary concept domain.
    """

    text = canonical_concept(
        concept
    )


    if not text:

        return DOMAIN_GENERAL


    scores = {}


    for domain, keywords in (
        DOMAIN_RULES.items()
    ):

        score = 0


        for keyword in keywords:

            if keyword in text:

                score += 1


                if keyword == text:

                    score += 3


        if score:

            scores[
                domain
            ] = score


    if not scores:

        return DOMAIN_GENERAL


    return max(

        scores,

        key=scores.get,

    )


# ============================================================
# 40. DIFFICULTY KEYWORDS
# ============================================================

DIFFICULTY_RULES = {

    DIFFICULTY_BEGINNER: [

        "introduction",

        "intro",

        "fundamentals",

        "basic",

        "basics",

        "getting started",

        "syntax",

        "overview",

    ],

    DIFFICULTY_INTERMEDIATE: [

        "implementation",

        "practical",

        "application",

        "intermediate",

        "feature engineering",

        "model development",

        "api",

    ],

    DIFFICULTY_ADVANCED: [

        "advanced",

        "architecture",

        "optimization",

        "fine tuning",

        "rag",

        "agents",

        "distributed",

        "deployment",

        "mlops",

        "llmops",

    ],

    DIFFICULTY_EXPERT: [

        "research",

        "reinforcement learning",

        "distributed training",

        "model architecture",

        "large scale",

        "optimization at scale",

        "multi-agent",

        "agentic architecture",

    ],

}


# ============================================================
# 41. CLASSIFY DIFFICULTY
# ============================================================

def classify_difficulty(
    concept: str,
) -> str:
    """
    Estimate concept difficulty.
    """

    text = canonical_concept(
        concept
    )


    scores = {

        level: 0

        for level
        in DIFFICULTY_RULES

    }


    for level, keywords in (
        DIFFICULTY_RULES.items()
    ):

        for keyword in keywords:

            if keyword in text:

                scores[
                    level
                ] += 1


    if max(
        scores.values()
    ) == 0:

        # Default based on concept complexity.
        token_count = len(
            concept_tokens(
                concept
            )
        )


        if token_count <= 2:

            return DIFFICULTY_BEGINNER


        if token_count <= 4:

            return DIFFICULTY_INTERMEDIATE


        return DIFFICULTY_ADVANCED


    return max(

        scores,

        key=scores.get,

    )


# ============================================================
# 42. IMPORTANCE KEYWORDS
# ============================================================

CRITICAL_CONCEPTS = {

    "python",

    "sql",

    "machine learning",

    "deep learning",

    "generative ai",

    "large language model",

    "rag",

    "retrieval augmented generation",

    "data structures",

    "algorithms",

    "statistics",

    "cloud",

    "docker",

    "kubernetes",

    "mlops",

}


HIGH_IMPORTANCE_CONCEPTS = {

    "computer vision",

    "natural language processing",

    "data engineering",

    "prompt engineering",

    "ai agents",

    "agentic ai",

    "embeddings",

    "vector database",

    "api",

    "git",

    "testing",

    "deployment",

}


# ============================================================
# 43. CLASSIFY IMPORTANCE
# ============================================================

def classify_importance(
    concept: str,
    industry_relevance: float = 0.0,
) -> str:
    """
    Estimate concept importance.
    """

    canonical = canonical_concept(
        concept
    )


    if canonical in CRITICAL_CONCEPTS:

        return IMPORTANCE_CRITICAL


    if canonical in HIGH_IMPORTANCE_CONCEPTS:

        return IMPORTANCE_HIGH


    industry_relevance = clamp(
        industry_relevance
    )


    if industry_relevance >= 85:

        return IMPORTANCE_HIGH


    if industry_relevance >= 70:

        return IMPORTANCE_MEDIUM


    return IMPORTANCE_LOW


# ============================================================
# 44. EXTRACT KEYWORDS
# ============================================================

def extract_concept_keywords(
    concept: str,
) -> List[str]:
    """
    Generate useful keywords for concept search/matching.
    """

    tokens = concept_tokens(
        concept
    )


    keywords = list(
        tokens
    )


    # Include canonical phrase.
    canonical = canonical_concept(
        concept
    )


    if canonical:

        keywords.append(
            canonical
        )


    # Domain.
    domain = classify_domain(
        concept
    )


    if domain != DOMAIN_GENERAL:

        keywords.append(
            domain
        )


    return deduplicate(
        keywords
    )


# ============================================================
# 45. BUILD CONCEPT PROFILE
# ============================================================

def build_concept_profile(
    concept: str,
    occurrence_count: int = 1,
    module_names: Optional[
        Sequence[str]
    ] = None,
    topic_names: Optional[
        Sequence[str]
    ] = None,
) -> ConceptProfile:
    """
    Build initial concept intelligence profile.
    """

    concept = clean_text(
        concept
    )


    canonical = canonical_concept(
        concept
    )


    concept_type = classify_concept_type(
        concept
    )


    domain = classify_domain(
        concept
    )


    difficulty = classify_difficulty(
        concept
    )


    # Initial industry score is refined later.
    industry = estimate_concept_industry_relevance(
        concept,
        domain,
        concept_type,
    )


    importance = classify_importance(

        concept,

        industry,

    )


    return ConceptProfile(

        concept_id=generate_concept_id(
            concept
        ),

        name=concept,

        canonical_name=canonical,

        concept_type=concept_type,

        domain=domain,

        difficulty=difficulty,

        importance=importance,

        description=(

            f"{concept} is a "
            f"{concept_type.replace('_', ' ')} "
            f"concept in the "
            f"{domain} domain."

        ),

        keywords=extract_concept_keywords(
            concept
        ),

        module_names=deduplicate(

            module_names
            or []

        ),

        topic_names=deduplicate(

            topic_names
            or []

        ),

        occurrence_count=max(

            1,

            int(
                occurrence_count
            ),

        ),

        industry_relevance=industry,

    )


# ============================================================
# 46. BUILD CONCEPT PROFILES
# ============================================================

def build_concept_profiles(
    concepts: Sequence[str],
    module_names: Optional[
        Sequence[str]
    ] = None,
    topic_names: Optional[
        Sequence[str]
    ] = None,
) -> List[ConceptProfile]:
    """
    Build profiles for a collection of concepts.
    """

    occurrences = build_concept_occurrences(
        concepts
    )


    result = []


    for canonical, count in (
        occurrences.items()
    ):

        profile = build_concept_profile(

            canonical,

            occurrence_count=count,

            module_names=module_names,

            topic_names=topic_names,

        )


        result.append(
            profile
        )


    return result


# ============================================================
# 47. END OF CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# PREREQUISITE + DEPENDENCY INTELLIGENCE
# ============================================================


# ============================================================
# 48. PREREQUISITE KNOWLEDGE GRAPH
# ============================================================

PREREQUISITE_RULES = {

    "machine learning": [

        "python",

        "statistics",

        "probability",

        "linear algebra",

    ],

    "deep learning": [

        "machine learning",

        "python",

        "linear algebra",

        "calculus",

    ],

    "generative ai": [

        "machine learning",

        "deep learning",

        "natural language processing",

        "large language model",

    ],

    "large language model": [

        "deep learning",

        "natural language processing",

        "transformers",

        "attention mechanisms",

    ],

    "retrieval augmented generation": [

        "large language model",

        "embeddings",

        "vector database",

        "information retrieval",

    ],

    "rag": [

        "large language model",

        "embeddings",

        "vector database",

        "information retrieval",

    ],

    "ai agents": [

        "large language model",

        "prompt engineering",

        "tool calling",

        "api",

    ],

    "agentic ai": [

        "large language model",

        "ai agents",

        "tool calling",

        "memory",

    ],

    "computer vision": [

        "python",

        "linear algebra",

        "image processing",

        "machine learning",

    ],

    "natural language processing": [

        "python",

        "statistics",

        "machine learning",

    ],

    "machine learning operations": [

        "machine learning",

        "python",

        "git",

        "docker",

        "cloud",

    ],

    "mlops": [

        "machine learning",

        "python",

        "git",

        "docker",

        "cloud",

    ],

    "llmops": [

        "large language model",

        "generative ai",

        "docker",

        "cloud",

    ],

    "kubernetes": [

        "docker",

        "linux",

        "networking",

        "cloud",

    ],

    "docker": [

        "linux",

        "operating systems",

        "networking",

    ],

    "sql": [

        "database fundamentals",

        "relational database",

    ],

    "data engineering": [

        "python",

        "sql",

        "database",

        "data structures",

    ],

}


# ============================================================
# 49. RELATED CONCEPT KNOWLEDGE
# ============================================================

RELATED_CONCEPT_RULES = {

    "machine learning": [

        "supervised learning",

        "unsupervised learning",

        "feature engineering",

        "model evaluation",

        "cross validation",

        "hyperparameter tuning",

    ],

    "deep learning": [

        "neural networks",

        "cnn",

        "rnn",

        "lstm",

        "transformers",

        "backpropagation",

    ],

    "generative ai": [

        "large language model",

        "prompt engineering",

        "rag",

        "ai agents",

        "fine tuning",

        "embeddings",

    ],

    "large language model": [

        "transformers",

        "attention mechanisms",

        "tokenization",

        "embeddings",

        "fine tuning",

        "prompt engineering",

    ],

    "rag": [

        "embeddings",

        "vector database",

        "retrieval",

        "reranking",

        "chunking",

        "hybrid search",

    ],

    "computer vision": [

        "image classification",

        "object detection",

        "image segmentation",

        "opencv",

        "cnn",

    ],

    "mlops": [

        "model deployment",

        "model monitoring",

        "model registry",

        "ci/cd",

        "docker",

        "kubernetes",

    ],

}


# ============================================================
# 50. GET PREREQUISITES
# ============================================================

def get_prerequisites(
    concept: str,
    max_items: int = 10,
) -> List[str]:
    """
    Retrieve direct prerequisites.
    """

    canonical = canonical_concept(
        concept
    )


    prerequisites = (
        PREREQUISITE_RULES.get(
            canonical,
            [],
        )
    )


    return deduplicate(
        prerequisites
    )[:max_items]


# ============================================================
# 51. GET RELATED CONCEPTS
# ============================================================

def get_related_concepts(
    concept: str,
    max_items: int = 15,
) -> List[str]:
    """
    Retrieve related concepts.
    """

    canonical = canonical_concept(
        concept
    )


    related = (
        RELATED_CONCEPT_RULES.get(
            canonical,
            [],
        )
    )


    return deduplicate(
        related
    )[:max_items]


# ============================================================
# 52. BUILD PREREQUISITE GRAPH
# ============================================================

def build_prerequisite_graph(
    concepts: Sequence[str],
) -> Dict[str, List[str]]:
    """
    Build prerequisite graph for supplied concepts.
    """

    graph = {}


    normalized = {

        canonical_concept(
            concept
        )

        for concept
        in concepts

        if canonical_concept(
            concept
        )

    }


    for concept in normalized:

        prerequisites = get_prerequisites(
            concept
        )


        graph[
            concept
        ] = [

            prerequisite

            for prerequisite
            in prerequisites

            if canonical_concept(
                prerequisite
            ) != concept

        ]


    return graph


# ============================================================
# 53. TRANSITIVE PREREQUISITES
# ============================================================

def get_transitive_prerequisites(
    concept: str,
    max_depth: int = 3,
) -> List[str]:
    """
    Recursively discover prerequisite concepts.
    """

    result = []

    visited = set()


    def visit(
        current: str,
        depth: int,
    ):

        if depth > max_depth:

            return


        canonical = canonical_concept(
            current
        )


        if canonical in visited:

            return


        visited.add(
            canonical
        )


        prerequisites = get_prerequisites(
            canonical
        )


        for prerequisite in prerequisites:

            prerequisite_canonical = (
                canonical_concept(
                    prerequisite
                )
            )


            if (
                prerequisite_canonical
                ==
                canonical
            ):

                continue


            result.append(
                prerequisite
            )


            visit(

                prerequisite,

                depth + 1,

            )


    visit(
        concept,
        0,
    )


    return deduplicate(
        result
    )


# ============================================================
# 54. DEPENDENCY DEPTH
# ============================================================

def calculate_dependency_depth(
    concept: str,
    max_depth: int = 10,
) -> int:
    """
    Calculate prerequisite depth.
    """

    visited = set()


    def depth(
        current: str,
        current_depth: int,
    ) -> int:

        if current_depth >= max_depth:

            return current_depth


        canonical = canonical_concept(
            current
        )


        if canonical in visited:

            return current_depth


        visited.add(
            canonical
        )


        prerequisites = get_prerequisites(
            canonical
        )


        if not prerequisites:

            return current_depth


        depths = [

            depth(

                prerequisite,

                current_depth + 1,

            )

            for prerequisite
            in prerequisites

        ]


        return max(
            depths
        )


    return depth(
        concept,
        0,
    )


# ============================================================
# 55. PREREQUISITE IMPACT
# ============================================================

def calculate_prerequisite_impact(
    concept: str,
) -> float:
    """
    Estimate importance of prerequisites.
    """

    prerequisites = get_prerequisites(
        concept
    )


    transitive = get_transitive_prerequisites(
        concept
    )


    direct_score = min(

        60.0,

        len(
            prerequisites
        )
        *
        15.0,

    )


    transitive_score = min(

        40.0,

        len(
            transitive
        )
        *
        5.0,

    )


    return round(

        min(

            100.0,

            direct_score
            +
            transitive_score,

        ),

        2,

    )


# ============================================================
# 56. MISSING PREREQUISITES
# ============================================================

def find_missing_prerequisites(
    concept: str,
    available_concepts: Sequence[str],
) -> List[str]:
    """
    Identify prerequisites absent from curriculum.
    """

    available = {

        canonical_concept(
            item
        )

        for item
        in available_concepts

    }


    prerequisites = get_transitive_prerequisites(
        concept
    )


    return [

        prerequisite

        for prerequisite
        in prerequisites

        if canonical_concept(
            prerequisite
        )
        not in available

    ]


# ============================================================
# 57. DEPENDENCY RISK
# ============================================================

def calculate_dependency_risk(
    concept: str,
    available_concepts: Sequence[str],
) -> float:
    """
    Calculate risk of teaching a concept when prerequisites
    are absent.
    """

    prerequisites = get_transitive_prerequisites(
        concept
    )


    if not prerequisites:

        return 0.0


    missing = find_missing_prerequisites(

        concept,

        available_concepts,

    )


    return percentage(

        len(
            missing
        ),

        len(
            prerequisites
        ),

    )


# ============================================================
# 58. ENRICH PROFILE WITH DEPENDENCIES
# ============================================================

def enrich_profile_dependencies(
    profile: ConceptProfile,
    available_concepts: Sequence[str],
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> ConceptProfile:
    """
    Add dependency information to a profile.
    """

    config = (
        config
        or
        ConceptIntelligenceConfig()
    )


    prerequisites = get_prerequisites(

        profile.name,

        config.max_prerequisites,

    )


    profile.prerequisites = (
        deduplicate(
            prerequisites
        )
    )


    profile.dependencies = (
        deduplicate(

            get_transitive_prerequisites(

                profile.name,

                max_depth=3,

            )

        )
    )


    profile.prerequisite_impact = (
        calculate_prerequisite_impact(
            profile.name
        )
    )


    profile.metadata[
        "missing_prerequisites"
    ] = find_missing_prerequisites(

        profile.name,

        available_concepts,

    )


    profile.metadata[
        "dependency_risk"
    ] = calculate_dependency_risk(

        profile.name,

        available_concepts,

    )


    return profile


# ============================================================
# 59. END OF CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# CONCEPT RELATIONSHIPS + KNOWLEDGE GRAPH
# ============================================================


# ============================================================
# 60. RELATIONSHIP CONFIDENCE
# ============================================================

def relationship_confidence(
    source: str,
    target: str,
    relationship_type: str,
) -> float:
    """
    Estimate relationship confidence.
    """

    source_canonical = canonical_concept(
        source
    )


    target_canonical = canonical_concept(
        target
    )


    if not source_canonical or not target_canonical:

        return 0.0


    if (
        source_canonical
        ==
        target_canonical
    ):

        return 100.0


    if relationship_type == REL_PREREQUISITE:

        prerequisites = get_prerequisites(
            source
        )


        if canonical_concept(
            target
        ) in {

            canonical_concept(
                item
            )

            for item
            in prerequisites

        }:

            return 95.0


    if relationship_type == REL_RELATED_TO:

        related = get_related_concepts(
            source
        )


        if canonical_concept(
            target
        ) in {

            canonical_concept(
                item
            )

            for item
            in related

        }:

            return 85.0


    source_tokens = set(
        concept_tokens(
            source
        )
    )


    target_tokens = set(
        concept_tokens(
            target
        )
    )


    if source_tokens and target_tokens:

        overlap = percentage(

            len(
                source_tokens
                &
                target_tokens
            ),

            len(
                source_tokens
                |
                target_tokens
            ),

        )


        return overlap


    return 0.0


# ============================================================
# 61. CREATE RELATIONSHIP
# ============================================================

def create_relationship(
    source: str,
    target: str,
    relationship_type: str,
    rationale: str = "",
) -> ConceptRelationship:
    """
    Create concept relationship.
    """

    confidence = relationship_confidence(

        source,

        target,

        relationship_type,

    )


    return ConceptRelationship(

        source=source,

        target=target,

        relationship_type=relationship_type,

        confidence=confidence,

        strength=confidence,

        rationale=rationale,

    )


# ============================================================
# 62. BUILD RELATIONSHIPS FOR CONCEPT
# ============================================================

def build_relationships_for_concept(
    concept: str,
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> List[ConceptRelationship]:
    """
    Build relationships around one concept.
    """

    config = (
        config
        or
        ConceptIntelligenceConfig()
    )


    relationships = []


    # --------------------------------------------------------
    # Prerequisites
    # --------------------------------------------------------

    if config.include_prerequisites:

        for prerequisite in get_prerequisites(

            concept,

            config.max_prerequisites,

        ):

            relationships.append(

                create_relationship(

                    concept,

                    prerequisite,

                    REL_PREREQUISITE,

                    (
                        f"{prerequisite} is a prerequisite "
                        f"for {concept}."
                    ),

                )

            )


    # --------------------------------------------------------
    # Related concepts
    # --------------------------------------------------------

    for related in get_related_concepts(

        concept,

        config.max_related_concepts,

    ):

        relationships.append(

            create_relationship(

                concept,

                related,

                REL_RELATED_TO,

                (
                    f"{related} is conceptually related "
                    f"to {concept}."
                ),

            )

        )


    return relationships


# ============================================================
# 63. BUILD CONCEPT GRAPH
# ============================================================

def build_concept_graph(
    concepts: Sequence[str],
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> List[ConceptRelationship]:
    """
    Build complete concept relationship graph.
    """

    concepts = deduplicate(
        concepts
    )


    relationships = []


    for concept in concepts:

        relationships.extend(

            build_relationships_for_concept(

                concept,

                config,

            )

        )


    return relationships


# ============================================================
# 64. GRAPH ADJACENCY
# ============================================================

def build_graph_adjacency(
    relationships: Sequence[
        ConceptRelationship
    ],
) -> Dict[str, List[str]]:
    """
    Convert relationships into adjacency map.
    """

    graph = {}


    for relationship in relationships:

        source = canonical_concept(
            relationship.source
        )


        target = canonical_concept(
            relationship.target
        )


        if not source or not target:

            continue


        graph.setdefault(
            source,
            [],
        )


        graph[
            source
        ].append(
            target
        )


    for source in graph:

        graph[
            source
        ] = deduplicate(

            graph[
                source
            ]

        )


    return graph


# ============================================================
# 65. GRAPH REVERSE ADJACENCY
# ============================================================

def build_reverse_graph(
    relationships: Sequence[
        ConceptRelationship
    ],
) -> Dict[str, List[str]]:
    """
    Build reverse dependency graph.
    """

    graph = {}


    for relationship in relationships:

        source = canonical_concept(
            relationship.source
        )


        target = canonical_concept(
            relationship.target
        )


        if not source or not target:

            continue


        graph.setdefault(
            target,
            [],
        )


        graph[
            target
        ].append(
            source
        )


    for target in graph:

        graph[
            target
        ] = deduplicate(

            graph[
                target
            ]

        )


    return graph


# ============================================================
# 66. FIND DEPENDENT CONCEPTS
# ============================================================

def find_dependent_concepts(
    concept: str,
    relationships: Sequence[
        ConceptRelationship
    ],
) -> List[str]:
    """
    Find concepts depending on the supplied concept.
    """

    reverse_graph = build_reverse_graph(
        relationships
    )


    canonical = canonical_concept(
        concept
    )


    return reverse_graph.get(

        canonical,

        [],

    )


# ============================================================
# 67. FIND RELATED NETWORK
# ============================================================

def find_related_network(
    concept: str,
    relationships: Sequence[
        ConceptRelationship
    ],
    max_depth: int = 2,
) -> List[str]:
    """
    Discover nearby concepts in graph.
    """

    graph = build_graph_adjacency(
        relationships
    )


    start = canonical_concept(
        concept
    )


    visited = set()


    queue = [

        (
            start,
            0,
        )

    ]


    result = []


    while queue:

        current, depth = queue.pop(
            0
        )


        if current in visited:

            continue


        visited.add(
            current
        )


        if (
            current != start
        ):

            result.append(
                current
            )


        if depth >= max_depth:

            continue


        for neighbor in graph.get(

            current,

            [],

        ):

            queue.append(

                (
                    neighbor,
                    depth + 1,
                )

            )


    return result


# ============================================================
# 68. CONCEPT CENTRALITY
# ============================================================

def calculate_concept_centrality(
    concept: str,
    relationships: Sequence[
        ConceptRelationship
    ],
) -> float:
    """
    Estimate concept importance based on graph connectivity.
    """

    canonical = canonical_concept(
        concept
    )


    if not canonical:

        return 0.0


    incoming = 0

    outgoing = 0


    for relationship in relationships:

        source = canonical_concept(
            relationship.source
        )


        target = canonical_concept(
            relationship.target
        )


        if source == canonical:

            outgoing += 1


        if target == canonical:

            incoming += 1


    score = (

        incoming * 8.0

        +

        outgoing * 5.0

    )


    return clamp(
        score
    )


# ============================================================
# 69. ENRICH PROFILES WITH RELATIONSHIPS
# ============================================================

def enrich_profiles_with_relationships(
    profiles: Sequence[
        ConceptProfile
    ],
    relationships: Sequence[
        ConceptRelationship
    ],
) -> List[ConceptProfile]:
    """
    Add graph relationships to concept profiles.
    """

    for profile in profiles:

        canonical = canonical_concept(
            profile.name
        )


        related = []

        dependencies = []


        for relationship in relationships:

            source = canonical_concept(
                relationship.source
            )


            target = canonical_concept(
                relationship.target
            )


            if source != canonical:

                continue


            if relationship.relationship_type == (
                REL_PREREQUISITE
            ):

                dependencies.append(
                    target
                )


            elif relationship.relationship_type == (
                REL_RELATED_TO
            ):

                related.append(
                    target
                )


        profile.dependencies = deduplicate(

            profile.dependencies
            +
            dependencies

        )


        profile.related_concepts = deduplicate(

            profile.related_concepts
            +
            related

        )


        profile.metadata[
            "centrality"
        ] = calculate_concept_centrality(

            profile.name,

            relationships,

        )


    return list(
        profiles
    )


# ============================================================
# 70. END OF CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# CONCEPT MATURITY + INDUSTRY INTELLIGENCE
# ============================================================


# ============================================================
# 71. INDUSTRY KEYWORDS
# ============================================================

HIGH_INDUSTRY_RELEVANCE = {

    "python",

    "sql",

    "machine learning",

    "deep learning",

    "generative ai",

    "large language model",

    "rag",

    "retrieval augmented generation",

    "ai agents",

    "agentic ai",

    "cloud",

    "aws",

    "azure",

    "gcp",

    "docker",

    "kubernetes",

    "mlops",

    "llmops",

    "data engineering",

    "cybersecurity",

    "computer vision",

    "natural language processing",

    "api",

    "git",

}


EMERGING_TECHNOLOGIES = {

    "generative ai",

    "large language model",

    "rag",

    "retrieval augmented generation",

    "ai agents",

    "agentic ai",

    "llmops",

    "multimodal ai",

    "vision language model",

    "small language model",

    "ai evaluation",

    "prompt engineering",

    "synthetic data",

    "vector database",

}


# ============================================================
# 72. INDUSTRY RELEVANCE
# ============================================================

def estimate_concept_industry_relevance(
    concept: str,
    domain: Optional[str] = None,
    concept_type: Optional[str] = None,
) -> float:
    """
    Estimate industry relevance from concept/domain.
    """

    canonical = canonical_concept(
        concept
    )


    if not canonical:

        return 0.0


    if canonical in HIGH_INDUSTRY_RELEVANCE:

        return 95.0


    score = 50.0


    if domain in (

        DOMAIN_MACHINE_LEARNING,

        DOMAIN_DEEP_LEARNING,

        DOMAIN_GENERATIVE_AI,

        DOMAIN_AGENTIC_AI,

        DOMAIN_DATA_ENGINEERING,

        DOMAIN_MLOPS,

        DOMAIN_LLMOPS,

        DOMAIN_CLOUD,

        DOMAIN_CYBERSECURITY,

    ):

        score += 20.0


    if concept_type in (

        CONCEPT_TYPE_TECHNOLOGY,

        CONCEPT_TYPE_FRAMEWORK,

        CONCEPT_TYPE_TOOL,

        CONCEPT_TYPE_PLATFORM,

        CONCEPT_TYPE_DEPLOYMENT,

    ):

        score += 10.0


    if canonical in EMERGING_TECHNOLOGIES:

        score += 15.0


    return clamp(
        score
    )


# ============================================================
# 73. EMPLOYABILITY KEYWORDS
# ============================================================

HIGH_EMPLOYABILITY_CONCEPTS = {

    "python",

    "sql",

    "machine learning",

    "deep learning",

    "generative ai",

    "large language model",

    "rag",

    "ai agents",

    "agentic ai",

    "data engineering",

    "cloud",

    "docker",

    "kubernetes",

    "mlops",

    "api",

    "git",

    "data analysis",

    "computer vision",

    "natural language processing",

}


# ============================================================
# 74. EMPLOYABILITY IMPACT
# ============================================================

def estimate_concept_employability(
    concept: str,
    concept_type: Optional[str] = None,
    domain: Optional[str] = None,
) -> float:
    """
    Estimate employability impact.
    """

    canonical = canonical_concept(
        concept
    )


    if canonical in HIGH_EMPLOYABILITY_CONCEPTS:

        return 95.0


    score = 50.0


    if concept_type in (

        CONCEPT_TYPE_SKILL,

        CONCEPT_TYPE_TECHNOLOGY,

        CONCEPT_TYPE_TOOL,

        CONCEPT_TYPE_FRAMEWORK,

        CONCEPT_TYPE_PROJECT,

    ):

        score += 20.0


    if domain in (

        DOMAIN_GENERATIVE_AI,

        DOMAIN_AGENTIC_AI,

        DOMAIN_MLOPS,

        DOMAIN_DATA_ENGINEERING,

        DOMAIN_CLOUD,

        DOMAIN_CYBERSECURITY,

    ):

        score += 15.0


    return clamp(
        score
    )


# ============================================================
# 75. LEARNING IMPACT
# ============================================================

def estimate_learning_impact(
    concept: str,
    difficulty: str,
    prerequisite_count: int,
    related_count: int,
) -> float:
    """
    Estimate learning impact.
    """

    score = 40.0


    score += min(

        25.0,

        prerequisite_count * 5.0,

    )


    score += min(

        20.0,

        related_count * 2.5,

    )


    if difficulty == DIFFICULTY_ADVANCED:

        score += 10.0


    elif difficulty == DIFFICULTY_EXPERT:

        score += 15.0


    elif difficulty == DIFFICULTY_INTERMEDIATE:

        score += 5.0


    return clamp(
        score
    )


# ============================================================
# 76. EMERGING SCORE
# ============================================================

def calculate_emerging_score(
    concept: str,
) -> float:
    """
    Estimate how emerging a concept is.
    """

    canonical = canonical_concept(
        concept
    )


    if canonical in EMERGING_TECHNOLOGIES:

        return 95.0


    text = canonical


    emerging_keywords = [

        "agent",

        "generative",

        "multimodal",

        "vector",

        "llm",

        "foundation model",

        "synthetic data",

        "ai evaluation",

        "fine tuning",

        "rag",

    ]


    matches = sum(

        1

        for keyword
        in emerging_keywords

        if keyword in text

    )


    return clamp(

        40.0
        +
        (
            matches
            *
            10.0
        )

    )


# ============================================================
# 77. CONCEPT MATURITY
# ============================================================

def calculate_concept_maturity(
    profile: ConceptProfile,
) -> float:
    """
    Estimate maturity based on curriculum exposure and
    concept ecosystem.
    """

    score = 30.0


    score += min(

        20.0,

        profile.occurrence_count * 5.0,

    )


    score += min(

        20.0,

        len(
            profile.prerequisites
        )
        *
        3.0,

    )


    score += min(

        15.0,

        len(
            profile.related_concepts
        )
        *
        2.0,

    )


    if profile.industry_relevance >= 80:

        score += 10.0


    if profile.employability_impact >= 80:

        score += 5.0


    return clamp(
        score
    )


# ============================================================
# 78. ENRICH INDUSTRY INTELLIGENCE
# ============================================================

def enrich_profile_industry(
    profile: ConceptProfile,
) -> ConceptProfile:
    """
    Add industry and employability intelligence.
    """

    profile.industry_relevance = (
        estimate_concept_industry_relevance(

            profile.name,

            profile.domain,

            profile.concept_type,

        )
    )


    profile.employability_impact = (
        estimate_concept_employability(

            profile.name,

            profile.concept_type,

            profile.domain,

        )
    )


    profile.emerging_score = (
        calculate_emerging_score(
            profile.name
        )
    )


    profile.learning_impact = (
        estimate_learning_impact(

            profile.name,

            profile.difficulty,

            len(
                profile.prerequisites
            ),

            len(
                profile.related_concepts
            ),

        )
    )


    profile.maturity_score = (
        calculate_concept_maturity(
            profile
        )
    )


    profile.importance = classify_importance(

        profile.name,

        profile.industry_relevance,

    )


    return profile


# ============================================================
# 79. DIFFICULTY SCORE
# ============================================================

def difficulty_score(
    difficulty: str,
) -> float:
    """
    Convert difficulty to numeric score.
    """

    mapping = {

        DIFFICULTY_BEGINNER:
            25.0,

        DIFFICULTY_INTERMEDIATE:
            50.0,

        DIFFICULTY_ADVANCED:
            75.0,

        DIFFICULTY_EXPERT:
            95.0,

    }


    return mapping.get(
        difficulty,
        50.0,
    )


# ============================================================
# 80. END OF CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# CONCEPT MATCHING ENGINE
# ============================================================


# ============================================================
# 81. TOKEN OVERLAP
# ============================================================

def calculate_token_overlap(
    source: str,
    target: str,
) -> float:
    """
    Calculate Jaccard token overlap.
    """

    source_tokens = set(
        concept_tokens(
            source
        )
    )


    target_tokens = set(
        concept_tokens(
            target
        )
    )


    if not source_tokens or not target_tokens:

        return 0.0


    intersection = (
        source_tokens
        &
        target_tokens
    )


    union = (
        source_tokens
        |
        target_tokens
    )


    if not union:

        return 0.0


    return round(

        len(
            intersection
        )
        /
        len(
            union
        ),

        4,

    )


# ============================================================
# 82. LEXICAL SIMILARITY
# ============================================================

def calculate_lexical_similarity(
    source: str,
    target: str,
) -> float:
    """
    Calculate lightweight lexical similarity.
    """

    source_canonical = canonical_concept(
        source
    )


    target_canonical = canonical_concept(
        target
    )


    if not source_canonical or not target_canonical:

        return 0.0


    if source_canonical == target_canonical:

        return 1.0


    token_score = calculate_token_overlap(

        source,

        target,

    )


    # Character-level similarity approximation.
    source_chars = set(
        source_canonical
    )


    target_chars = set(
        target_canonical
    )


    if source_chars and target_chars:

        char_score = (

            len(
                source_chars
                &
                target_chars
            )

            /

            len(
                source_chars
                |
                target_chars
            )

        )

    else:

        char_score = 0.0


    return round(

        (
            token_score * 0.7
            +
            char_score * 0.3
        ),

        4,

    )


# ============================================================
# 83. TF-IDF SIMILARITY
# ============================================================

def calculate_tfidf_similarity(
    source: str,
    target: str,
) -> float:
    """
    Calculate TF-IDF similarity when sklearn is available.
    """

    if (
        TfidfVectorizer is None
        or
        cosine_similarity is None
    ):

        return 0.0


    try:

        vectorizer = TfidfVectorizer(
            lowercase=True
        )


        matrix = vectorizer.fit_transform([

            source,

            target,

        ])


        score = cosine_similarity(

            matrix[0:1],

            matrix[1:2],

        )[0][0]


        return clamp(
            score * 100.0,
            0.0,
            100.0,
        ) / 100.0

    except Exception:

        return 0.0


# ============================================================
# 84. CONCEPT SIMILARITY
# ============================================================

def concept_similarity(
    source: str,
    target: str,
) -> float:
    """
    Hybrid concept similarity.

    Combines:
        lexical similarity
        token overlap
        TF-IDF similarity
    """

    lexical = calculate_lexical_similarity(

        source,

        target,

    )


    overlap = calculate_token_overlap(

        source,

        target,

    )


    tfidf = calculate_tfidf_similarity(

        source,

        target,

    )


    if tfidf <= 0:

        score = (

            lexical * 0.70

            +

            overlap * 0.30

        )

    else:

        score = (

            lexical * 0.40

            +

            overlap * 0.20

            +

            tfidf * 0.40

        )


    # Exact canonical match.
    if (

        canonical_concept(
            source
        )
        ==
        canonical_concept(
            target
        )

    ):

        return 1.0


    return round(

        min(
            1.0,
            score,
        ),

        4,

    )


# ============================================================
# 85. MATCH STATUS
# ============================================================

def determine_match_status(
    similarity: float,
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> str:
    """
    Determine match state.
    """

    config = (
        config
        or
        ConceptIntelligenceConfig()
    )


    similarity = safe_float(
        similarity
    )


    if similarity >= config.similarity_threshold:

        return STATUS_PRESENT


    if similarity >= config.partial_similarity_threshold:

        return STATUS_PARTIAL


    return STATUS_MISSING


# ============================================================
# 86. MATCH RATIONALE
# ============================================================

def build_match_rationale(
    source: str,
    target: str,
    similarity: float,
    status: str,
) -> str:
    """
    Human-readable matching explanation.
    """

    percentage_score = (
        similarity
        *
        100.0
    )


    if status == STATUS_PRESENT:

        return (

            f"'{source}' closely matches "
            f"'{target}' with "
            f"{percentage_score:.1f}% similarity."

        )


    if status == STATUS_PARTIAL:

        return (

            f"'{source}' partially matches "
            f"'{target}' with "
            f"{percentage_score:.1f}% similarity."

        )


    return (

        f"'{source}' has no sufficiently strong "
        f"match with '{target}'."

    )


# ============================================================
# 87. BUILD CONCEPT MATCH
# ============================================================

def build_concept_match(
    source: str,
    target: str,
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> ConceptMatch:
    """
    Build detailed concept match.
    """

    config = (
        config
        or
        ConceptIntelligenceConfig()
    )


    lexical = calculate_lexical_similarity(

        source,

        target,

    )


    overlap = calculate_token_overlap(

        source,

        target,

    )


    semantic = calculate_tfidf_similarity(

        source,

        target,

    )


    similarity = concept_similarity(

        source,

        target,

    )


    status = determine_match_status(

        similarity,

        config,

    )


    confidence = (

        similarity
        *
        100.0

    )


    return ConceptMatch(

        source_concept=source,

        target_concept=target,

        similarity=round(

            similarity * 100.0,

            2,

        ),

        lexical_similarity=round(

            lexical * 100.0,

            2,

        ),

        semantic_similarity=round(

            semantic * 100.0,

            2,

        ),

        token_overlap=round(

            overlap * 100.0,

            2,

        ),

        status=status,

        confidence=round(

            confidence,

            2,

        ),

        rationale=build_match_rationale(

            source,

            target,

            similarity,

            status,

        ),

    )


# ============================================================
# 88. BEST CONCEPT MATCH
# ============================================================

def find_best_concept_match(
    concept: str,
    candidates: Sequence[str],
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> Optional[ConceptMatch]:
    """
    Find best matching target concept.
    """

    if not candidates:

        return None


    best = None


    best_score = -1.0


    for candidate in candidates:

        match = build_concept_match(

            concept,

            candidate,

            config,

        )


        if match.similarity > best_score:

            best_score = (
                match.similarity
            )

            best = match


    return best


# ============================================================
# 89. MATCH CONCEPT COLLECTIONS
# ============================================================

def match_concept_collections(
    source_concepts: Sequence[str],
    target_concepts: Sequence[str],
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> List[ConceptMatch]:
    """
    Match every source concept against target concepts.
    """

    source_concepts = deduplicate(
        source_concepts
    )


    target_concepts = deduplicate(
        target_concepts
    )


    matches = []


    for source in source_concepts:

        best = find_best_concept_match(

            source,

            target_concepts,

            config,

        )


        if best is not None:

            matches.append(
                best
            )


    return matches


# ============================================================
# 90. END OF CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# CONCEPT GAP INTELLIGENCE
# ============================================================


# ============================================================
# 91. GAP SEVERITY
# ============================================================

def concept_gap_severity(
    priority_score: float,
) -> str:
    """
    Convert concept priority to severity.
    """

    score = clamp(
        priority_score
    )


    if score >= 80:

        return IMPORTANCE_CRITICAL


    if score >= 65:

        return IMPORTANCE_HIGH


    if score >= 40:

        return IMPORTANCE_MEDIUM


    return IMPORTANCE_LOW


# ============================================================
# 92. CONCEPT GAP PRIORITY
# ============================================================

def calculate_concept_gap_priority(
    concept: str,
    similarity: float,
    industry_relevance: float,
    employability_impact: float,
    learning_impact: float,
    prerequisite_impact: float,
    dependency_risk: float = 0.0,
) -> float:
    """
    Calculate concept gap priority.
    """

    similarity = clamp(
        similarity
    )


    industry = clamp(
        industry_relevance
    )


    employability = clamp(
        employability_impact
    )


    learning = clamp(
        learning_impact
    )


    prerequisite = clamp(
        prerequisite_impact
    )


    dependency = clamp(
        dependency_risk
    )


    # Similarity is represented as coverage.
    semantic_gap = (

        100.0
        -
        similarity

    )


    score = (

        semantic_gap * 0.20

        +

        industry * 0.25

        +

        employability * 0.25

        +

        learning * 0.15

        +

        prerequisite * 0.10

        +

        dependency * 0.05

    )


    return round(

        clamp(
            score
        ),

        2,

    )


# ============================================================
# 93. GAP TOPICS
# ============================================================

def recommend_gap_topics(
    concept: str,
) -> List[str]:
    """
    Generate topics needed to teach a missing concept.
    """

    domain = classify_domain(
        concept
    )


    topics = [

        f"{concept} fundamentals",

        f"{concept} architecture",

        f"{concept} implementation",

    ]


    if domain in (

        DOMAIN_GENERATIVE_AI,

        DOMAIN_AGENTIC_AI,

    ):

        topics.extend([

            f"{concept} prompting",

            f"{concept} evaluation",

            f"{concept} deployment",

        ])


    if domain in (

        DOMAIN_MACHINE_LEARNING,

        DOMAIN_DEEP_LEARNING,

    ):

        topics.extend([

            f"{concept} model training",

            f"{concept} evaluation",

            f"{concept} optimization",

        ])


    if domain == DOMAIN_MLOPS:

        topics.extend([

            f"{concept} deployment",

            f"{concept} monitoring",

            f"{concept} CI/CD",

        ])


    return deduplicate(
        topics
    )


# ============================================================
# 94. GAP TOOLS
# ============================================================

def recommend_gap_tools(
    concept: str,
) -> List[str]:
    """
    Recommend tools for missing concept.
    """

    text = canonical_concept(
        concept
    )


    tools = []


    if "rag" in text:

        tools.extend([

            "LangChain",

            "LlamaIndex",

            "FAISS",

            "Chroma",

        ])


    elif (
        "generative ai" in text
        or
        "large language model" in text
    ):

        tools.extend([

            "Hugging Face",

            "LangChain",

            "Ollama",

        ])


    elif "agent" in text:

        tools.extend([

            "LangGraph",

            "LangChain",

        ])


    elif "machine learning" in text:

        tools.extend([

            "Python",

            "scikit-learn",

            "Jupyter",

        ])


    elif "deep learning" in text:

        tools.extend([

            "PyTorch",

            "TensorFlow",

        ])


    elif "computer vision" in text:

        tools.extend([

            "OpenCV",

            "PyTorch",

            "YOLO",

        ])


    elif "mlops" in text:

        tools.extend([

            "MLflow",

            "Docker",

            "Kubernetes",

        ])


    elif "cloud" in text:

        tools.extend([

            "AWS",

            "Azure",

            "GCP",

        ])


    return deduplicate(
        tools
    )


# ============================================================
# 95. GAP PROJECT
# ============================================================

def recommend_gap_project(
    concept: str,
) -> Optional[str]:
    """
    Generate practical project recommendation.
    """

    text = canonical_concept(
        concept
    )


    if (
        "rag" in text
        or
        "retrieval augmented" in text
    ):

        return (
            "Enterprise Document RAG "
            "Question Answering System"
        )


    if (
        "agentic ai" in text
        or
        "ai agent" in text
    ):

        return (
            "Multi-Agent AI Business Automation System"
        )


    if (
        "generative ai" in text
        or
        "large language model" in text
    ):

        return (
            "Domain-Specific Generative AI Assistant"
        )


    if "machine learning" in text:

        return (
            "End-to-End Machine Learning "
            "Prediction Platform"
        )


    if "computer vision" in text:

        return (
            "Real-Time Computer Vision "
            "Detection System"
        )


    if "natural language processing" in text:

        return (
            "NLP Text Intelligence Application"
        )


    if "mlops" in text:

        return (
            "Production ML Model Monitoring "
            "and Deployment Platform"
        )


    return (
        f"Industry Application using {concept}"
    )


# ============================================================
# 96. BUILD CONCEPT GAP
# ============================================================

def build_concept_gap(
    concept: str,
    target_concepts: Sequence[str],
    available_concepts: Sequence[str],
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> ConceptGap:
    """
    Build complete concept gap object.
    """

    config = (
        config
        or
        ConceptIntelligenceConfig()
    )


    profile = build_concept_profile(
        concept
    )


    profile = enrich_profile_industry(
        profile
    )


    profile = enrich_profile_dependencies(

        profile,

        available_concepts,

        config,

    )


    best_match = find_best_concept_match(

        concept,

        target_concepts,

        config,

    )


    similarity = (

        best_match.similarity

        if best_match

        else 0.0

    )


    priority = calculate_concept_gap_priority(

        concept,

        similarity,

        profile.industry_relevance,

        profile.employability_impact,

        profile.learning_impact,

        profile.prerequisite_impact,

        safe_float(

            profile.metadata.get(
                "dependency_risk",
                0.0,
            )

        ),

    )


    severity = concept_gap_severity(
        priority
    )


    gap_type = STATUS_MISSING


    if best_match is not None:

        if best_match.status == STATUS_PARTIAL:

            gap_type = STATUS_PARTIAL

        elif best_match.status == STATUS_PRESENT:

            # Strongly matched concepts are not gaps.
            gap_type = STATUS_PRESENT


    return ConceptGap(

        concept=concept,

        gap_type=gap_type,

        severity=severity,

        priority_score=priority,

        source_present=True,

        target_present=(

            best_match is not None
            and
            best_match.status
            ==
            STATUS_PRESENT

        ),

        best_match=(

            best_match.target_concept

            if best_match

            else None

        ),

        similarity=similarity,

        industry_relevance=(
            profile.industry_relevance
        ),

        employability_impact=(
            profile.employability_impact
        ),

        learning_impact=(
            profile.learning_impact
        ),

        prerequisite_impact=(
            profile.prerequisite_impact
        ),

        prerequisites=(
            profile.prerequisites
        ),

        recommended_topics=(
            recommend_gap_topics(
                concept
            )
        ),

        recommended_tools=(
            recommend_gap_tools(
                concept
            )
        ),

        recommended_project=(
            recommend_gap_project(
                concept
            )
        ),

        rationale=(

            f"'{concept}' has a priority score "
            f"of {priority:.1f}/100 based on "
            f"industry relevance, employability, "
            f"learning impact and prerequisite "
            f"dependencies."

        ),

        metadata={

            "dependency_risk":
                profile.metadata.get(
                    "dependency_risk",
                    0.0,
                ),

            "missing_prerequisites":
                profile.metadata.get(
                    "missing_prerequisites",
                    [],
                ),

        },

    )


# ============================================================
# 97. IDENTIFY CONCEPT GAPS
# ============================================================

def identify_concept_gaps(
    source_concepts: Sequence[str],
    target_concepts: Sequence[str],
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> List[ConceptGap]:
    """
    Identify missing and partial concepts.
    """

    config = (
        config
        or
        ConceptIntelligenceConfig()
    )


    source_concepts = deduplicate(
        source_concepts
    )


    target_concepts = deduplicate(
        target_concepts
    )


    gaps = []


    for concept in source_concepts:

        gap = build_concept_gap(

            concept,

            target_concepts,

            source_concepts,

            config,

        )


        if gap.gap_type == STATUS_PRESENT:

            continue


        gaps.append(
            gap
        )


    return sorted(

        gaps,

        key=lambda item: (

            item.priority_score,

            item.industry_relevance,

            item.employability_impact,

        ),

        reverse=True,

    )


# ============================================================
# 98. IDENTIFY EMERGING CONCEPTS
# ============================================================

def identify_emerging_concepts(
    concepts: Sequence[str],
    threshold: float = 65.0,
) -> List[Tuple[str, float]]:
    """
    Identify emerging concepts.
    """

    result = []


    for concept in deduplicate(
        concepts
    ):

        score = calculate_emerging_score(
            concept
        )


        if score >= threshold:

            result.append(

                (
                    concept,

                    score,

                )

            )


    return sorted(

        result,

        key=lambda item: item[1],

        reverse=True,

    )


# ============================================================
# 99. END OF CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# CONCEPT-BASED LEARNING RECOMMENDATION ENGINE
# ============================================================


# ============================================================
# 100. RECOMMENDATION TYPE
# ============================================================

REC_TEACH = "teach"

REC_REINFORCE = "reinforce"

REC_PRACTICE = "practice"

REC_PROJECT = "project"

REC_PREREQUISITE = "prerequisite"

REC_ADVANCE = "advance"

REC_REPLACE = "replace"

REC_UPDATE = "update"


# ============================================================
# 101. LEARNING ACTIVITIES
# ============================================================

def recommend_learning_activities_for_concept(
    profile: ConceptProfile,
) -> List[str]:
    """
    Generate learning activities.
    """

    activities = []


    if profile.difficulty == DIFFICULTY_BEGINNER:

        activities.extend([

            "Instructor-led explanation",

            "Worked examples",

            "Guided exercises",

            "Concept quiz",

        ])


    elif profile.difficulty == DIFFICULTY_INTERMEDIATE:

        activities.extend([

            "Hands-on laboratory",

            "Implementation exercise",

            "Debugging exercise",

            "Case study",

        ])


    elif profile.difficulty == DIFFICULTY_ADVANCED:

        activities.extend([

            "Architecture exercise",

            "Advanced implementation",

            "Optimization exercise",

            "Industry case study",

        ])


    else:

        activities.extend([

            "Research-oriented problem",

            "System architecture exercise",

            "Independent implementation",

            "Technical presentation",

        ])


    if profile.concept_type in (

        CONCEPT_TYPE_TOOL,

        CONCEPT_TYPE_FRAMEWORK,

        CONCEPT_TYPE_TECHNOLOGY,

    ):

        activities.append(
            "Tool-based practical lab"
        )


    if profile.employability_impact >= 80:

        activities.append(
            "Industry-oriented assignment"
        )


    return deduplicate(
        activities
    )


# ============================================================
# 102. ASSESSMENT METHODS
# ============================================================

def recommend_assessment_methods(
    profile: ConceptProfile,
) -> List[str]:
    """
    Generate assessments based on concept type.
    """

    assessments = [

        "Conceptual quiz",

    ]


    if profile.concept_type in (

        CONCEPT_TYPE_CONCEPT,

        CONCEPT_TYPE_FOUNDATION,

        CONCEPT_TYPE_ALGORITHM,

    ):

        assessments.extend([

            "Problem-solving assessment",

            "Short-answer assessment",

        ])


    if profile.concept_type in (

        CONCEPT_TYPE_TOOL,

        CONCEPT_TYPE_FRAMEWORK,

        CONCEPT_TYPE_LIBRARY,

        CONCEPT_TYPE_TECHNOLOGY,

        CONCEPT_TYPE_SKILL,

    ):

        assessments.extend([

            "Hands-on practical assessment",

            "Implementation assignment",

        ])


    if profile.concept_type in (

        CONCEPT_TYPE_PROJECT,

        CONCEPT_TYPE_ARCHITECTURE,

        CONCEPT_TYPE_DEPLOYMENT,

    ):

        assessments.extend([

            "Project evaluation",

            "Architecture review",

            "Technical presentation",

        ])


    return deduplicate(
        assessments
    )


# ============================================================
# 103. ESTIMATE LEARNING HOURS
# ============================================================

def estimate_concept_learning_hours(
    profile: ConceptProfile,
) -> float:
    """
    Estimate required instructional hours.
    """

    base = {

        DIFFICULTY_BEGINNER:
            3.0,

        DIFFICULTY_INTERMEDIATE:
            5.0,

        DIFFICULTY_ADVANCED:
            8.0,

        DIFFICULTY_EXPERT:
            12.0,

    }.get(

        profile.difficulty,

        5.0,

    )


    if profile.concept_type in (

        CONCEPT_TYPE_TECHNOLOGY,

        CONCEPT_TYPE_TOOL,

        CONCEPT_TYPE_FRAMEWORK,

        CONCEPT_TYPE_LIBRARY,

    ):

        base += 2.0


    if profile.concept_type in (

        CONCEPT_TYPE_PROJECT,

        CONCEPT_TYPE_ARCHITECTURE,

        CONCEPT_TYPE_DEPLOYMENT,

    ):

        base += 8.0


    if profile.prerequisite_impact >= 70:

        base += 2.0


    return round(
        base,
        1,
    )


# ============================================================
# 104. RECOMMEND CONCEPT PROJECT
# ============================================================

def recommend_concept_project(
    profile: ConceptProfile,
) -> Optional[str]:
    """
    Generate project for concept.
    """

    return recommend_gap_project(
        profile.name
    )


# ============================================================
# 105. BUILD CONCEPT RECOMMENDATION
# ============================================================

def build_concept_recommendation(
    profile: ConceptProfile,
    recommendation_type: str = REC_TEACH,
) -> ConceptRecommendation:
    """
    Build learning recommendation.
    """

    hours = estimate_concept_learning_hours(
        profile
    )


    priority = profile.importance


    title = (

        f"Learn and Apply {profile.name}"

    )


    description = (

        f"Develop practical and conceptual "
        f"competency in {profile.name}, "
        f"including its prerequisites, "
        f"implementation and industry applications."

    )


    expected_impact = (

        profile.industry_relevance * 0.30

        +

        profile.employability_impact * 0.35

        +

        profile.learning_impact * 0.20

        +

        profile.emerging_score * 0.15

    )


    return ConceptRecommendation(

        concept=profile.name,

        recommendation_type=recommendation_type,

        title=title,

        description=description,

        priority=priority,

        estimated_hours=hours,

        prerequisites=profile.prerequisites,

        topics=(

            recommend_gap_topics(
                profile.name
            )

        ),

        activities=(

            recommend_learning_activities_for_concept(
                profile
            )

        ),

        assessment_methods=(

            recommend_assessment_methods(
                profile
            )

        ),

        tools=profile.tools
        or
        recommend_gap_tools(
            profile.name
        ),

        project=(

            recommend_concept_project(
                profile
            )

        ),

        expected_impact=round(

            clamp(
                expected_impact
            ),

            2,

        ),

        metadata={

            "domain":
                profile.domain,

            "difficulty":
                profile.difficulty,

            "industry_relevance":
                profile.industry_relevance,

            "employability_impact":
                profile.employability_impact,

        },

    )


# ============================================================
# 106. BUILD RECOMMENDATIONS
# ============================================================

def build_concept_recommendations(
    profiles: Sequence[
        ConceptProfile
    ],
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> List[ConceptRecommendation]:
    """
    Generate recommendations for concept profiles.
    """

    config = (
        config
        or
        ConceptIntelligenceConfig()
    )


    recommendations = []


    profiles = sorted(

        profiles,

        key=lambda profile: (

            profile.industry_relevance,

            profile.employability_impact,

            profile.importance,

        ),

        reverse=True,

    )


    for profile in profiles[

        :config.max_recommendations

    ]:

        recommendations.append(

            build_concept_recommendation(
                profile
            )

        )


    return recommendations


# ============================================================
# 107. RECOMMEND MISSING PREREQUISITES
# ============================================================

def build_prerequisite_recommendations(
    profiles: Sequence[
        ConceptProfile
    ],
    available_concepts: Sequence[str],
) -> List[ConceptRecommendation]:
    """
    Build recommendations for missing prerequisites.
    """

    recommendations = []


    for profile in profiles:

        missing = find_missing_prerequisites(

            profile.name,

            available_concepts,

        )


        for prerequisite in missing:

            prerequisite_profile = (
                build_concept_profile(
                    prerequisite
                )
            )


            prerequisite_profile = (
                enrich_profile_industry(
                    prerequisite_profile
                )
            )


            recommendations.append(

                build_concept_recommendation(

                    prerequisite_profile,

                    REC_PREREQUISITE,

                )

            )


    # Deduplicate.
    seen = set()

    result = []


    for item in recommendations:

        key = canonical_concept(
            item.concept
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
# 108. END OF CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# COMPLETE CONCEPT INTELLIGENCE PIPELINE
# SERIALIZATION
# VALIDATION
# REPORTING
# PUBLIC API
# ============================================================


# ============================================================
# 109. ENRICH PROFILE
# ============================================================

def enrich_concept_profile(
    profile: ConceptProfile,
    available_concepts: Sequence[str],
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> ConceptProfile:
    """
    Run complete intelligence enrichment for one concept.
    """

    profile = enrich_profile_dependencies(

        profile,

        available_concepts,

        config,

    )


    profile.related_concepts = deduplicate(

        profile.related_concepts
        +
        get_related_concepts(
            profile.name
        )

    )


    profile.tools = deduplicate(

        profile.tools
        +
        recommend_gap_tools(
            profile.name
        )

    )


    profile.technologies = deduplicate(

        profile.technologies
        +
        recommend_gap_tools(
            profile.name
        )

    )


    profile.skills = deduplicate(

        profile.skills
        +
        [

            f"{profile.name} implementation",

            f"{profile.name} problem solving",

        ]

    )


    profile.applications = deduplicate(

        profile.applications
        +
        [

            f"{profile.name} industry application",

        ]

    )


    profile.projects = deduplicate(

        profile.projects
        +
        [

            recommend_gap_project(
                profile.name
            )

        ]

    )


    profile = enrich_profile_industry(
        profile
    )


    profile.confidence_score = min(

        100.0,

        (
            profile.industry_relevance
            +
            profile.employability_impact
            +
            profile.learning_impact
        )
        /
        3.0,

    )


    return profile


# ============================================================
# 110. BUILD INTELLIGENCE RESULT
# ============================================================

def build_concept_intelligence(
    concepts: Sequence[str],
    target_concepts: Optional[
        Sequence[str]
    ] = None,
    module_names: Optional[
        Sequence[str]
    ] = None,
    topic_names: Optional[
        Sequence[str]
    ] = None,
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> ConceptIntelligenceResult:
    """
    Main concept intelligence engine.

    Performs:

        Extraction/profile
        ↓
        Classification
        ↓
        Prerequisites
        ↓
        Relationships
        ↓
        Industry analysis
        ↓
        Concept matching
        ↓
        Gap analysis
        ↓
        Recommendations
    """

    config = (
        config
        or
        ConceptIntelligenceConfig()
    )


    concepts = deduplicate(
        concepts
    )


    target_concepts = deduplicate(

        target_concepts
        or
        []

    )


    # --------------------------------------------------------
    # Profiles
    # --------------------------------------------------------

    profiles = build_concept_profiles(

        concepts,

        module_names=module_names,

        topic_names=topic_names,

    )


    # --------------------------------------------------------
    # Enrich profiles
    # --------------------------------------------------------

    profiles = [

        enrich_concept_profile(

            profile,

            concepts,

            config,

        )

        for profile
        in profiles

    ]


    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    relationships = build_concept_graph(

        concepts,

        config,

    )


    profiles = enrich_profiles_with_relationships(

        profiles,

        relationships,

    )


    # Recalculate maturity after relationships.
    for profile in profiles:

        profile.maturity_score = (
            calculate_concept_maturity(
                profile
            )
        )


    # --------------------------------------------------------
    # Target matching
    # --------------------------------------------------------

    matches = []


    if target_concepts:

        matches = match_concept_collections(

            concepts,

            target_concepts,

            config,

        )


    # --------------------------------------------------------
    # Gap detection
    # --------------------------------------------------------

    gaps = []


    if target_concepts:

        gaps = identify_concept_gaps(

            concepts,

            target_concepts,

            config,

        )


    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = build_concept_recommendations(

        profiles,

        config,

    )


    # Add prerequisite recommendations.
    prerequisite_recommendations = (
        build_prerequisite_recommendations(

            profiles,

            concepts,

        )
    )


    recommendations.extend(

        prerequisite_recommendations

    )


    # Deduplicate recommendations.
    recommendation_seen = set()

    unique_recommendations = []


    for recommendation in recommendations:

        key = (

            canonical_concept(
                recommendation.concept
            ),

            recommendation.recommendation_type,

        )


        if key in recommendation_seen:

            continue


        recommendation_seen.add(
            key
        )


        unique_recommendations.append(
            recommendation
        )


    recommendations = unique_recommendations[

        :config.max_recommendations

    ]


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = build_concept_summary(

        profiles,

        matches,

        gaps,

        recommendations,

    )


    return ConceptIntelligenceResult(

        concepts=profiles,

        relationships=relationships,

        matches=matches,

        gaps=gaps,

        recommendations=recommendations,

        summary=summary,

        metadata={

            "version":
                CONCEPT_INTELLIGENCE_VERSION,

            "concept_count":
                len(profiles),

            "relationship_count":
                len(relationships),

            "match_count":
                len(matches),

            "gap_count":
                len(gaps),

            "recommendation_count":
                len(recommendations),

        },

    )


# ============================================================
# 111. CURRICULUM-LEVEL PIPELINE
# ============================================================

def analyze_curriculum_concepts(
    curriculum: Any,
    target_curriculum: Any = None,
    config: Optional[
        ConceptIntelligenceConfig
    ] = None,
) -> ConceptIntelligenceResult:
    """
    Analyze concepts directly from curriculum objects.
    """

    concepts = extract_concepts_from_curriculum(

        curriculum

    )


    target_concepts = []


    if target_curriculum is not None:

        target_concepts = (
            extract_concepts_from_curriculum(

                target_curriculum

            )
        )


    modules = extract_module_names(
        curriculum
    )


    topics = extract_topic_names(
        curriculum
    )


    return build_concept_intelligence(

        concepts,

        target_concepts=target_concepts,

        module_names=modules,

        topic_names=topics,

        config=config,

    )


# ============================================================
# 112. CONCEPT SUMMARY
# ============================================================

def build_concept_summary(
    profiles: Sequence[
        ConceptProfile
    ],
    matches: Sequence[
        ConceptMatch
    ],
    gaps: Sequence[
        ConceptGap
    ],
    recommendations: Sequence[
        ConceptRecommendation
    ],
) -> Dict[str, Any]:
    """
    Build aggregate concept intelligence summary.
    """

    total = len(
        profiles
    )


    domains = {}


    types = {}


    difficulties = {}


    emerging = 0


    high_industry = 0


    high_employability = 0


    for profile in profiles:

        domains[
            profile.domain
        ] = (

            domains.get(
                profile.domain,
                0,
            )
            +
            1

        )


        types[
            profile.concept_type
        ] = (

            types.get(
                profile.concept_type,
                0,
            )
            +
            1

        )


        difficulties[
            profile.difficulty
        ] = (

            difficulties.get(
                profile.difficulty,
                0,
            )
            +
            1

        )


        if profile.emerging_score >= 65:

            emerging += 1


        if profile.industry_relevance >= 80:

            high_industry += 1


        if profile.employability_impact >= 80:

            high_employability += 1


    present_matches = sum(

        1

        for match
        in matches

        if match.status
        ==
        STATUS_PRESENT

    )


    partial_matches = sum(

        1

        for match
        in matches

        if match.status
        ==
        STATUS_PARTIAL

    )


    return {

        "total_concepts":
            total,

        "domains":
            domains,

        "concept_types":
            types,

        "difficulty_distribution":
            difficulties,

        "emerging_concepts":
            emerging,

        "high_industry_relevance":
            high_industry,

        "high_employability":
            high_employability,

        "matched_concepts":
            present_matches,

        "partial_concepts":
            partial_matches,

        "gap_count":
            len(
                gaps
            ),

        "recommendation_count":
            len(
                recommendations
            ),

        "average_industry_relevance": round(

            (
                sum(

                    profile.industry_relevance

                    for profile
                    in profiles

                )
                /
                total

            )

            if total

            else 0.0,

            2,

        ),

        "average_employability": round(

            (
                sum(

                    profile.employability_impact

                    for profile
                    in profiles

                )
                /
                total

            )

            if total

            else 0.0,

            2,

        ),

        "average_maturity": round(

            (
                sum(

                    profile.maturity_score

                    for profile
                    in profiles

                )
                /
                total

            )

            if total

            else 0.0,

            2,

        ),

    }


# ============================================================
# 113. PROFILE TO DICT
# ============================================================

def concept_profile_to_dict(
    profile: ConceptProfile,
) -> Dict[str, Any]:
    """
    Serialize concept profile.
    """

    return asdict(
        profile
    )


# ============================================================
# 114. RELATIONSHIP TO DICT
# ============================================================

def concept_relationship_to_dict(
    relationship: ConceptRelationship,
) -> Dict[str, Any]:
    """
    Serialize relationship.
    """

    return asdict(
        relationship
    )


# ============================================================
# 115. MATCH TO DICT
# ============================================================

def concept_match_to_dict(
    match: ConceptMatch,
) -> Dict[str, Any]:
    """
    Serialize concept match.
    """

    return asdict(
        match
    )


# ============================================================
# 116. GAP TO DICT
# ============================================================

def concept_gap_to_dict(
    gap: ConceptGap,
) -> Dict[str, Any]:
    """
    Serialize concept gap.
    """

    return asdict(
        gap
    )


# ============================================================
# 117. RECOMMENDATION TO DICT
# ============================================================

def concept_recommendation_to_dict(
    recommendation: ConceptRecommendation,
) -> Dict[str, Any]:
    """
    Serialize recommendation.
    """

    return asdict(
        recommendation
    )


# ============================================================
# 118. RESULT TO DICT
# ============================================================

def concept_intelligence_to_dict(
    result: ConceptIntelligenceResult,
) -> Dict[str, Any]:
    """
    Serialize complete result.
    """

    return {

        "concepts": [

            concept_profile_to_dict(
                profile
            )

            for profile
            in result.concepts

        ],

        "relationships": [

            concept_relationship_to_dict(
                relationship
            )

            for relationship
            in result.relationships

        ],

        "matches": [

            concept_match_to_dict(
                match
            )

            for match
            in result.matches

        ],

        "gaps": [

            concept_gap_to_dict(
                gap
            )

            for gap
            in result.gaps

        ],

        "recommendations": [

            concept_recommendation_to_dict(
                recommendation
            )

            for recommendation
            in result.recommendations

        ],

        "summary":
            dict(
                result.summary
            ),

        "metadata":
            dict(
                result.metadata
            ),

    }


# ============================================================
# 119. JSON EXPORT
# ============================================================

def concept_intelligence_to_json(
    result: ConceptIntelligenceResult,
    indent: int = 2,
) -> str:
    """
    Convert concept intelligence result to JSON.
    """

    return json.dumps(

        concept_intelligence_to_dict(
            result
        ),

        indent=indent,

        ensure_ascii=False,

        default=str,

    )


# ============================================================
# 120. SAVE JSON
# ============================================================

def save_concept_intelligence_json(
    result: ConceptIntelligenceResult,
    file_path: Union[
        str,
        Path,
    ],
) -> Path:
    """
    Save concept intelligence to JSON.
    """

    path = Path(
        file_path
    )


    path.parent.mkdir(

        parents=True,

        exist_ok=True,

    )


    path.write_text(

        concept_intelligence_to_json(
            result
        ),

        encoding="utf-8",

    )


    return path


# ============================================================
# 121. VALIDATE PROFILE
# ============================================================

def validate_concept_profile(
    profile: ConceptProfile,
) -> List[str]:
    """
    Validate concept profile.
    """

    errors = []


    if not profile.name:

        errors.append(
            "Concept name is missing."
        )


    if not profile.concept_id:

        errors.append(
            "Concept ID is missing."
        )


    if not (
        0
        <=
        profile.industry_relevance
        <=
        100
    ):

        errors.append(
            "Industry relevance must be 0-100."
        )


    if not (
        0
        <=
        profile.employability_impact
        <=
        100
    ):

        errors.append(
            "Employability impact must be 0-100."
        )


    if not (
        0
        <=
        profile.maturity_score
        <=
        100
    ):

        errors.append(
            "Maturity score must be 0-100."
        )


    return errors


# ============================================================
# 122. VALIDATE RESULT
# ============================================================

def validate_concept_intelligence(
    result: ConceptIntelligenceResult,
) -> Dict[str, List[str]]:
    """
    Validate complete concept intelligence result.
    """

    errors = {

        "profiles": [],

        "relationships": [],

        "matches": [],

        "gaps": [],

        "recommendations": [],

    }


    for profile in result.concepts:

        errors[
            "profiles"
        ].extend(

            validate_concept_profile(
                profile
            )

        )


    for relationship in result.relationships:

        if not relationship.source:

            errors[
                "relationships"
            ].append(

                "Relationship source is missing."

            )


        if not relationship.target:

            errors[
                "relationships"
            ].append(

                "Relationship target is missing."

            )


    for match in result.matches:

        if not match.source_concept:

            errors[
                "matches"
            ].append(

                "Match source concept is missing."

            )


        if not (

            0
            <=
            match.similarity
            <=
            100

        ):

            errors[
                "matches"
            ].append(

                (
                    f"Invalid similarity for "
                    f"{match.source_concept}."
                )

            )


    for gap in result.gaps:

        if not gap.concept:

            errors[
                "gaps"
            ].append(

                "Gap concept is missing."

            )


        if not (

            0
            <=
            gap.priority_score
            <=
            100

        ):

            errors[
                "gaps"
            ].append(

                (
                    f"Invalid priority for "
                    f"{gap.concept}."
                )

            )


    for recommendation in result.recommendations:

        if not recommendation.concept:

            errors[
                "recommendations"
            ].append(

                "Recommendation concept is missing."

            )


    return errors


# ============================================================
# 123. CONCEPT DASHBOARD DATA
# ============================================================

def build_concept_dashboard_data(
    result: ConceptIntelligenceResult,
) -> Dict[str, Any]:
    """
    Build Streamlit/Plotly-ready data.
    """

    profile_data = []


    for profile in result.concepts:

        profile_data.append({

            "concept":
                profile.name,

            "domain":
                profile.domain,

            "type":
                profile.concept_type,

            "difficulty":
                profile.difficulty,

            "importance":
                profile.importance,

            "industry_relevance":
                profile.industry_relevance,

            "employability":
                profile.employability_impact,

            "learning_impact":
                profile.learning_impact,

            "maturity":
                profile.maturity_score,

            "emerging_score":
                profile.emerging_score,

            "prerequisite_impact":
                profile.prerequisite_impact,

            "occurrences":
                profile.occurrence_count,

        })


    gap_data = [

        {

            "concept":
                gap.concept,

            "severity":
                gap.severity,

            "priority":
                gap.priority_score,

            "industry_relevance":
                gap.industry_relevance,

            "employability":
                gap.employability_impact,

            "learning_impact":
                gap.learning_impact,

            "similarity":
                gap.similarity,

        }

        for gap
        in result.gaps

    ]


    domain_distribution = {}


    for profile in result.concepts:

        domain = profile.domain


        domain_distribution[
            domain
        ] = (

            domain_distribution.get(
                domain,
                0,
            )
            +
            1

        )


    return {

        "profiles":
            profile_data,

        "gaps":
            gap_data,

        "domain_distribution":
            domain_distribution,

        "summary":
            result.summary,

    }


# ============================================================
# 124. TOP CONCEPTS
# ============================================================

def get_top_concepts(
    result: ConceptIntelligenceResult,
    limit: int = 10,
) -> List[ConceptProfile]:
    """
    Return highest-value concepts.
    """

    return sorted(

        result.concepts,

        key=lambda profile: (

            profile.industry_relevance,

            profile.employability_impact,

            profile.maturity_score,

        ),

        reverse=True,

    )[:max(
        1,
        limit,
    )]


# ============================================================
# 125. TOP CONCEPT GAPS
# ============================================================

def get_top_concept_gaps(
    result: ConceptIntelligenceResult,
    limit: int = 10,
) -> List[ConceptGap]:
    """
    Return highest-priority concept gaps.
    """

    return sorted(

        result.gaps,

        key=lambda gap: (

            gap.priority_score,

            gap.industry_relevance,

            gap.employability_impact,

        ),

        reverse=True,

    )[:max(
        1,
        limit,
    )]


# ============================================================
# 126. EMERGING CONCEPT PROFILES
# ============================================================

def get_emerging_concept_profiles(
    result: ConceptIntelligenceResult,
    threshold: float = 65.0,
) -> List[ConceptProfile]:
    """
    Return emerging concepts.
    """

    return [

        profile

        for profile
        in result.concepts

        if profile.emerging_score >= threshold

    ]


# ============================================================
# 127. HIGH EMPLOYABILITY CONCEPTS
# ============================================================

def get_high_employability_concepts(
    result: ConceptIntelligenceResult,
    threshold: float = 80.0,
) -> List[ConceptProfile]:
    """
    Return concepts with high employability impact.
    """

    return [

        profile

        for profile
        in result.concepts

        if profile.employability_impact
        >=
        threshold

    ]


# ============================================================
# 128. HIGH INDUSTRY RELEVANCE CONCEPTS
# ============================================================

def get_high_industry_concepts(
    result: ConceptIntelligenceResult,
    threshold: float = 80.0,
) -> List[ConceptProfile]:
    """
    Return highly industry-relevant concepts.
    """

    return [

        profile

        for profile
        in result.concepts

        if profile.industry_relevance
        >=
        threshold

    ]


# ============================================================
# 129. QUICK SUMMARY
# ============================================================

def concept_quick_summary(
    result: ConceptIntelligenceResult,
) -> Dict[str, Any]:
    """
    Return compact dashboard metrics.
    """

    summary = result.summary


    return {

        "concepts":
            summary.get(
                "total_concepts",
                0,
            ),

        "gaps":
            summary.get(
                "gap_count",
                0,
            ),

        "emerging":
            summary.get(
                "emerging_concepts",
                0,
            ),

        "high_industry":
            summary.get(
                "high_industry_relevance",
                0,
            ),

        "high_employability":
            summary.get(
                "high_employability",
                0,
            ),

        "average_maturity":
            summary.get(
                "average_maturity",
                0.0,
            ),

        "average_industry_relevance":
            summary.get(
                "average_industry_relevance",
                0.0,
            ),

        "average_employability":
            summary.get(
                "average_employability",
                0.0,
            ),

    }


# ============================================================
# 130. PUBLIC API ALIASES
# ============================================================

extract_concepts = (
    extract_concepts_from_curriculum
)


build_profiles = (
    build_concept_profiles
)


analyze_concepts = (
    analyze_curriculum_concepts
)


concept_match = (
    build_concept_match
)


find_best_match = (
    find_best_concept_match
)


find_gaps = (
    identify_concept_gaps
)


build_graph = (
    build_concept_graph
)


build_recommendations = (
    build_concept_recommendations
)


# ============================================================
# 131. CAPABILITIES
# ============================================================

CONCEPT_INTELLIGENCE_CAPABILITIES = [

    "concept_extraction",

    "concept_normalization",

    "concept_classification",

    "domain_classification",

    "difficulty_estimation",

    "importance_estimation",

    "prerequisite_detection",

    "dependency_analysis",

    "knowledge_graph",

    "concept_relationships",

    "concept_similarity",

    "concept_matching",

    "concept_gap_detection",

    "gap_prioritization",

    "industry_relevance",

    "employability_analysis",

    "emerging_technology_detection",

    "concept_maturity",

    "learning_recommendations",

    "project_recommendations",

    "assessment_recommendations",

    "dashboard_data",

    "json_export",

    "validation",

]


# ============================================================
# 132. PUBLIC EXPORTS
# ============================================================

__all__ = [

    # --------------------------------------------------------
    # Config
    # --------------------------------------------------------

    "ConceptIntelligenceConfig",

    # --------------------------------------------------------
    # Core models
    # --------------------------------------------------------

    "ConceptProfile",

    "ConceptRelationship",

    "ConceptMatch",

    "ConceptGap",

    "ConceptRecommendation",

    "ConceptIntelligenceResult",

    # --------------------------------------------------------
    # Extraction
    # --------------------------------------------------------

    "extract_concepts",

    "extract_concepts_from_text",

    "extract_concepts_from_curriculum",

    "extract_candidate_phrases",

    "extract_module_names",

    "extract_topic_names",

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    "classify_concept_type",

    "classify_domain",

    "classify_difficulty",

    "classify_importance",

    "extract_concept_keywords",

    # --------------------------------------------------------
    # Profiles
    # --------------------------------------------------------

    "build_concept_profile",

    "build_concept_profiles",

    "build_profiles",

    "enrich_concept_profile",

    # --------------------------------------------------------
    # Prerequisites
    # --------------------------------------------------------

    "get_prerequisites",

    "get_related_concepts",

    "get_transitive_prerequisites",

    "calculate_dependency_depth",

    "calculate_prerequisite_impact",

    "find_missing_prerequisites",

    "calculate_dependency_risk",

    # --------------------------------------------------------
    # Knowledge graph
    # --------------------------------------------------------

    "create_relationship",

    "build_relationships_for_concept",

    "build_concept_graph",

    "build_graph",

    "build_graph_adjacency",

    "build_reverse_graph",

    "find_dependent_concepts",

    "find_related_network",

    "calculate_concept_centrality",

    # --------------------------------------------------------
    # Industry intelligence
    # --------------------------------------------------------

    "estimate_concept_industry_relevance",

    "estimate_concept_employability",

    "estimate_learning_impact",

    "calculate_emerging_score",

    "calculate_concept_maturity",

    # --------------------------------------------------------
    # Matching
    # --------------------------------------------------------

    "calculate_token_overlap",

    "calculate_lexical_similarity",

    "calculate_tfidf_similarity",

    "concept_similarity",

    "build_concept_match",

    "concept_match",

    "find_best_concept_match",

    "find_best_match",

    "match_concept_collections",

    # --------------------------------------------------------
    # Gaps
    # --------------------------------------------------------

    "calculate_concept_gap_priority",

    "build_concept_gap",

    "identify_concept_gaps",

    "find_gaps",

    "get_top_concept_gaps",

    "identify_emerging_concepts",

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    "recommend_learning_activities_for_concept",

    "recommend_assessment_methods",

    "estimate_concept_learning_hours",

    "recommend_concept_project",

    "build_concept_recommendation",

    "build_concept_recommendations",

    "build_recommendations",

    "build_prerequisite_recommendations",

    # --------------------------------------------------------
    # Main pipeline
    # --------------------------------------------------------

    "build_concept_intelligence",

    "analyze_curriculum_concepts",

    "analyze_concepts",

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    "concept_profile_to_dict",

    "concept_relationship_to_dict",

    "concept_match_to_dict",

    "concept_gap_to_dict",

    "concept_recommendation_to_dict",

    "concept_intelligence_to_dict",

    "concept_intelligence_to_json",

    "save_concept_intelligence_json",

    # --------------------------------------------------------
    # Reporting
    # --------------------------------------------------------

    "build_concept_dashboard_data",

    "get_top_concepts",

    "get_top_concept_gaps",

    "get_emerging_concept_profiles",

    "get_high_employability_concepts",

    "get_high_industry_concepts",

    "concept_quick_summary",

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    "validate_concept_profile",

    "validate_concept_intelligence",

    # --------------------------------------------------------
    # Constants
    # --------------------------------------------------------

    "CONCEPT_TYPE_UNKNOWN",

    "CONCEPT_TYPE_FOUNDATION",

    "CONCEPT_TYPE_CONCEPT",

    "CONCEPT_TYPE_ALGORITHM",

    "CONCEPT_TYPE_MODEL",

    "CONCEPT_TYPE_TECHNOLOGY",

    "CONCEPT_TYPE_TOOL",

    "CONCEPT_TYPE_FRAMEWORK",

    "CONCEPT_TYPE_LIBRARY",

    "CONCEPT_TYPE_PLATFORM",

    "CONCEPT_TYPE_SKILL",

    "CONCEPT_TYPE_METHOD",

    "CONCEPT_TYPE_ARCHITECTURE",

    "CONCEPT_TYPE_PATTERN",

    "CONCEPT_TYPE_PROJECT",

    "CONCEPT_TYPE_DOMAIN",

    "CONCEPT_TYPE_SOFTWARE",

    "CONCEPT_TYPE_CLOUD",

    "CONCEPT_TYPE_DATABASE",

    "CONCEPT_TYPE_SECURITY",

    "CONCEPT_TYPE_EVALUATION",

    "CONCEPT_TYPE_DEPLOYMENT",

    "CONCEPT_TYPE_OTHER",

    # Difficulty
    "DIFFICULTY_BEGINNER",

    "DIFFICULTY_INTERMEDIATE",

    "DIFFICULTY_ADVANCED",

    "DIFFICULTY_EXPERT",

    # Importance
    "IMPORTANCE_LOW",

    "IMPORTANCE_MEDIUM",

    "IMPORTANCE_HIGH",

    "IMPORTANCE_CRITICAL",

    # Status
    "STATUS_PRESENT",

    "STATUS_MISSING",

    "STATUS_PARTIAL",

    "STATUS_DUPLICATE",

    "STATUS_OUTDATED",

    "STATUS_EMERGING",

    # Relationships
    "REL_PREREQUISITE",

    "REL_DEPENDS_ON",

    "REL_RELATED_TO",

    "REL_PART_OF",

    "REL_VARIANT_OF",

    "REL_EXTENDS",

    "REL_REQUIRES",

    "REL_USED_WITH",

    "REL_ALTERNATIVE_TO",

    "REL_FOLLOWED_BY",

    "REL_PRECEDES",

    "REL_APPLICATION_OF",

    # Version
    "CONCEPT_INTELLIGENCE_VERSION",

    "CONCEPT_INTELLIGENCE_CAPABILITIES",

]


# ============================================================
# 133. END OF FILE
# ============================================================
