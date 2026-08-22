# ============================================================
# curriculum/comparator.py
# CHUNK 1/10
#
# CURRICULUM INTELLIGENCE
#
# Curriculum A
#      │
#      ├── Modules
#      ├── Topics
#      ├── Concepts
#      ├── Skills
#      ├── Tools
#      └── Technologies
#             │
#             ▼
#       COMPARISON ENGINE
#             │
#             ▼
# Curriculum B
#
# Outputs:
#   - Similarity
#   - Coverage
#   - Missing concepts
#   - Additional concepts
#   - Module comparison
#   - Skill comparison
#   - Technology comparison
#   - Gap analysis
# ============================================================


# ============================================================
# 1. STANDARD LIBRARY IMPORTS
# ============================================================

from __future__ import annotations

import json
import logging
import math
import re

from dataclasses import (
    dataclass,
    field,
)

from difflib import SequenceMatcher

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
)


# ============================================================
# 2. OPTIONAL NUMPY
# ============================================================

try:

    import numpy as np

except ImportError:

    np = None


# ============================================================
# 3. OPTIONAL RAPIDFUZZ
# ============================================================

try:

    from rapidfuzz import fuzz

except ImportError:

    fuzz = None


# ============================================================
# 4. OPTIONAL SKLEARN
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
# 5. PYDANTIC MODELS
# ============================================================

try:

    from .models import (
        Curriculum,
        Module,
        Topic,
        Concept,
        Skill,
        Tool,
        Technology,
        Project,
        CourseOutcome,
        ProgramOutcome,
        ProgramSpecificOutcome,
    )

except ImportError:

    # Allows standalone execution if required.

    from models import (
        Curriculum,
        Module,
        Topic,
        Concept,
        Skill,
        Tool,
        Technology,
        Project,
        CourseOutcome,
        ProgramOutcome,
        ProgramSpecificOutcome,
    )


# ============================================================
# 6. LOGGING
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
# 7. CONSTANTS
# ============================================================

COMPARATOR_VERSION = "1.0.0"


DEFAULT_MATCH_THRESHOLD = 0.72

DEFAULT_HIGH_MATCH_THRESHOLD = 0.85

DEFAULT_LOW_MATCH_THRESHOLD = 0.55


# ============================================================
# 8. COMPARISON WEIGHTS
# ============================================================

DEFAULT_WEIGHTS = {

    "modules": 0.20,

    "topics": 0.20,

    "concepts": 0.20,

    "skills": 0.20,

    "technologies": 0.10,

    "tools": 0.05,

    "projects": 0.05,

}


# ============================================================
# 9. NORMALIZATION ALIASES
# ============================================================

NORMALIZATION_ALIASES = {

    "ai":
        "artificial intelligence",

    "artificial intelligence":
        "artificial intelligence",

    "ml":
        "machine learning",

    "machine learning":
        "machine learning",

    "dl":
        "deep learning",

    "deep learning":
        "deep learning",

    "genai":
        "generative ai",

    "generative ai":
        "generative ai",

    "generative artificial intelligence":
        "generative ai",

    "llm":
        "large language model",

    "llms":
        "large language model",

    "large language model":
        "large language model",

    "large language models":
        "large language model",

    "nlp":
        "natural language processing",

    "natural language processing":
        "natural language processing",

    "cv":
        "computer vision",

    "computer vision":
        "computer vision",

    "sql":
        "sql",

    "structured query language":
        "sql",

    "python programming":
        "python",

    "python programming language":
        "python",

    "javascript":
        "javascript",

    "js":
        "javascript",

    "typescript":
        "typescript",

    "ts":
        "typescript",

    "k8s":
        "kubernetes",

    "kubernetes":
        "kubernetes",

    "aws":
        "amazon web services",

    "amazon web services":
        "amazon web services",

    "gcp":
        "google cloud platform",

    "google cloud platform":
        "google cloud platform",

    "azure":
        "microsoft azure",

    "microsoft azure":
        "microsoft azure",

    "rag":
        "retrieval augmented generation",

    "retrieval augmented generation":
        "retrieval augmented generation",

    "retrieval-augmented generation":
        "retrieval augmented generation",

    "peft":
        "parameter efficient fine tuning",

    "parameter efficient fine tuning":
        "parameter efficient fine tuning",

    "rlhf":
        "reinforcement learning from human feedback",

    "reinforcement learning from human feedback":
        "reinforcement learning from human feedback",

}


# ============================================================
# 10. TEXT CLEANING
# ============================================================

def clean_text(
    value: Any,
) -> str:
    """
    Convert arbitrary input into normalized text.
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
# 11. NORMALIZE TEXT
# ============================================================

def normalize_text(
    value: Any,
) -> str:
    """
    Normalize text for semantic comparison.

    Example:

        "Machine-Learning"
            →
        "machine learning"
    """

    text = clean_text(
        value
    ).lower()


    text = text.replace(
        "&",
        " and ",
    )


    text = re.sub(
        r"[_/]+",
        " ",
        text,
    )


    text = re.sub(
        r"[-]+",
        " ",
        text,
    )


    text = re.sub(
        r"[^\w\s.+#]",
        " ",
        text,
    )


    text = re.sub(
        r"\s+",
        " ",
        text,
    )


    text = text.strip()


    if text in NORMALIZATION_ALIASES:

        return NORMALIZATION_ALIASES[
            text
        ]


    return text


# ============================================================
# 12. NORMALIZE LIST
# ============================================================

def normalize_list(
    values: Any,
) -> List[str]:
    """
    Convert arbitrary iterable/list-like values into
    unique normalized strings.
    """

    if values is None:

        return []


    if isinstance(
        values,
        str,
    ):

        values = [
            values
        ]


    result = []

    seen = set()


    try:

        iterator = iter(
            values
        )

    except TypeError:

        iterator = iter(
            [values]
        )


    for value in iterator:

        normalized = normalize_text(
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
            normalized
        )


    return result


# ============================================================
# 13. SAFE FLOAT
# ============================================================

def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert value to float.
    """

    try:

        if value is None:

            return default


        number = float(
            value
        )


        if math.isnan(
            number
        ):

            return default


        if math.isinf(
            number
        ):

            return default


        return number

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# 14. CLAMP SCORE
# ============================================================

def clamp_score(
    value: Any,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    """
    Clamp a numeric score.
    """

    number = safe_float(
        value
    )


    return max(
        minimum,
        min(
            maximum,
            number,
        ),
    )


# ============================================================
# 15. SAFE DIVISION
# ============================================================

def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0,
) -> float:
    """
    Safe division.
    """

    numerator = safe_float(
        numerator
    )

    denominator = safe_float(
        denominator
    )


    if denominator == 0:

        return default


    return numerator / denominator


# ============================================================
# 16. PERCENTAGE
# ============================================================

def percentage(
    numerator: float,
    denominator: float,
) -> float:
    """
    Return percentage between 0 and 100.
    """

    return round(
        safe_divide(
            numerator,
            denominator,
            0.0,
        )
        * 100,
        2,
    )


# ============================================================
# 17. STRING SIMILARITY
# ============================================================

def string_similarity(
    text_a: Any,
    text_b: Any,
) -> float:
    """
    Calculate similarity between two strings.

    Returns:
        0.0 - 1.0
    """

    a = normalize_text(
        text_a
    )

    b = normalize_text(
        text_b
    )


    if not a or not b:

        return 0.0


    if a == b:

        return 1.0


    # --------------------------------------------------------
    # RapidFuzz
    # --------------------------------------------------------

    if fuzz is not None:

        try:

            score = fuzz.token_set_ratio(
                a,
                b,
            )


            return clamp_score(
                score,
                0,
                100,
            ) / 100.0

        except Exception:

            pass


    # --------------------------------------------------------
    # Standard library fallback
    # --------------------------------------------------------

    return SequenceMatcher(
        None,
        a,
        b,
    ).ratio()


# ============================================================
# 18. TOKEN SET
# ============================================================

def token_set(
    text: Any,
) -> Set[str]:
    """
    Convert text into a normalized token set.
    """

    normalized = normalize_text(
        text
    )


    if not normalized:

        return set()


    return set(
        normalized.split()
    )


# ============================================================
# 19. TOKEN JACCARD SIMILARITY
# ============================================================

def jaccard_similarity(
    text_a: Any,
    text_b: Any,
) -> float:
    """
    Calculate token-level Jaccard similarity.
    """

    tokens_a = token_set(
        text_a
    )

    tokens_b = token_set(
        text_b
    )


    if not tokens_a or not tokens_b:

        return 0.0


    intersection = (
        tokens_a
        &
        tokens_b
    )


    union = (
        tokens_a
        |
        tokens_b
    )


    return safe_divide(
        len(intersection),
        len(union),
        0.0,
    )


# ============================================================
# 20. HYBRID TEXT SIMILARITY
# ============================================================

def hybrid_similarity(
    text_a: Any,
    text_b: Any,
) -> float:
    """
    Combine character/token similarity.

    This is the basic comparison layer.

    Later chunks can add:
        - embeddings
        - RAG evidence
        - LLM semantic verification
    """

    sequence_score = string_similarity(
        text_a,
        text_b,
    )


    jaccard_score = jaccard_similarity(
        text_a,
        text_b,
    )


    return round(
        (
            sequence_score * 0.60
            +
            jaccard_score * 0.40
        ),
        4,
    )


# ============================================================
# 21. NORMALIZED KEY
# ============================================================

def normalized_key(
    value: Any,
) -> str:
    """
    Generate a stable comparison key.
    """

    return normalize_text(
        value
    )


# ============================================================
# 22. DEDUPLICATE VALUES
# ============================================================

def deduplicate(
    values: Iterable[Any],
) -> List[str]:
    """
    Deduplicate values while preserving order.
    """

    result = []

    seen = set()


    for value in values:

        normalized = normalize_text(
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
            normalized
        )


    return result


# ============================================================
# 23. OBJECT ATTRIBUTE
# ============================================================

def get_attr(
    obj: Any,
    name: str,
    default: Any = None,
) -> Any:
    """
    Safely get an attribute from an object or dictionary.
    """

    if obj is None:

        return default


    if isinstance(
        obj,
        dict,
    ):

        return obj.get(
            name,
            default,
        )


    return getattr(
        obj,
        name,
        default,
    )


# ============================================================
# 24. OBJECT NAME
# ============================================================

def object_name(
    obj: Any,
) -> str:
    """
    Extract a human-readable name from an arbitrary
    curriculum object.
    """

    for field_name in [

        "name",

        "title",

        "module_name",

        "topic_name",

        "course_name",

        "subject_name",

        "code",

    ]:

        value = get_attr(
            obj,
            field_name,
        )


        if value:

            return clean_text(
                value
            )


    return ""


# ============================================================
# 25. OBJECT DESCRIPTION
# ============================================================

def object_description(
    obj: Any,
) -> str:
    """
    Extract description text.
    """

    for field_name in [

        "description",

        "summary",

        "statement",

        "text",

        "objective",

    ]:

        value = get_attr(
            obj,
            field_name,
        )


        if value:

            return clean_text(
                value
            )


    return ""


# ============================================================
# 26. OBJECT TEXT
# ============================================================

def object_text(
    obj: Any,
) -> str:
    """
    Build a richer comparison representation.
    """

    name = object_name(
        obj
    )

    description = object_description(
        obj
    )


    if name and description:

        return (
            f"{name}. {description}"
        )


    return (
        name
        or
        description
    )


# ============================================================
# 27. COMPARATOR CONFIG
# ============================================================

@dataclass
class ComparatorConfig:
    """
    Configuration for curriculum comparison.
    """

    match_threshold: float = (
        DEFAULT_MATCH_THRESHOLD
    )

    high_match_threshold: float = (
        DEFAULT_HIGH_MATCH_THRESHOLD
    )

    low_match_threshold: float = (
        DEFAULT_LOW_MATCH_THRESHOLD
    )

    weights: Dict[
        str,
        float,
    ] = field(
        default_factory=lambda:
            dict(
                DEFAULT_WEIGHTS
            )
    )

    use_embeddings: bool = True

    use_llm_verification: bool = False

    use_rag_evidence: bool = False

    include_module_details: bool = True

    include_topic_details: bool = True

    include_concept_details: bool = True

    include_skill_details: bool = True

    include_technology_details: bool = True

    include_tool_details: bool = True

    include_project_details: bool = True

    max_items_per_category: int = 500


# ============================================================
# 28. MATCH RESULT
# ============================================================

@dataclass
class MatchResult:
    """
    Represents a pairwise match between two curriculum items.
    """

    source_name: str

    target_name: str

    similarity: float

    match_type: str = "semantic"

    confidence: float = 0.0

    source_index: Optional[int] = None

    target_index: Optional[int] = None

    evidence: List[str] = field(
        default_factory=list
    )

    explanation: Optional[str] = None


# ============================================================
# 29. CATEGORY RESULT
# ============================================================

@dataclass
class CategoryComparison:
    """
    Comparison result for one category.
    """

    category: str

    source_count: int

    target_count: int

    matched_count: int

    missing_count: int

    additional_count: int

    coverage_percentage: float

    similarity_percentage: float

    matched: List[
        MatchResult
    ] = field(
        default_factory=list
    )

    missing: List[str] = field(
        default_factory=list
    )

    additional: List[str] = field(
        default_factory=list
    )


# ============================================================
# 30. END OF CHUNK 1
# ============================================================
# ============================================================
# curriculum/comparator.py
# CHUNK 2/10
#
# MATCHING ENGINE
#
# Exact Match
#      ↓
# Normalized / Alias Match
#      ↓
# Fuzzy Similarity
#      ↓
# One-to-One Best Match
#      ↓
# Matched / Missing / Additional
# ============================================================


# ============================================================
# 31. ALIAS NORMALIZATION
# ============================================================

def canonical_term(
    value: Any,
) -> str:
    """
    Convert a term into its canonical comparison form.

    Examples:

        ML
            -> machine learning

        GenAI
            -> generative ai

        RAG
            -> retrieval augmented generation

        K8s
            -> kubernetes
    """

    normalized = normalize_text(
        value
    )

    if not normalized:
        return ""

    return NORMALIZATION_ALIASES.get(
        normalized,
        normalized,
    )


# ============================================================
# 32. CANONICAL TOKEN SET
# ============================================================

def canonical_tokens(
    value: Any,
) -> Set[str]:
    """
    Return canonical normalized tokens.
    """

    canonical = canonical_term(
        value
    )

    if not canonical:
        return set()

    return set(
        canonical.split()
    )


# ============================================================
# 33. CANONICAL SIMILARITY
# ============================================================

def canonical_similarity(
    value_a: Any,
    value_b: Any,
) -> float:
    """
    Compare two values after alias normalization.
    """

    a = canonical_term(
        value_a
    )

    b = canonical_term(
        value_b
    )

    if not a or not b:
        return 0.0

    if a == b:
        return 1.0

    return hybrid_similarity(
        a,
        b,
    )


# ============================================================
# 34. EXACT MATCH
# ============================================================

def exact_match(
    value_a: Any,
    value_b: Any,
) -> bool:
    """
    Case-insensitive normalized exact match.
    """

    a = normalize_text(
        value_a
    )

    b = normalize_text(
        value_b
    )

    return bool(
        a
        and b
        and a == b
    )


# ============================================================
# 35. CANONICAL MATCH
# ============================================================

def canonical_match(
    value_a: Any,
    value_b: Any,
) -> bool:
    """
    Alias-aware exact match.
    """

    a = canonical_term(
        value_a
    )

    b = canonical_term(
        value_b
    )

    return bool(
        a
        and b
        and a == b
    )


# ============================================================
# 36. TOKEN OVERLAP
# ============================================================

def token_overlap(
    value_a: Any,
    value_b: Any,
) -> float:
    """
    Calculate overlap of canonical tokens.

    This is useful for phrases such as:

        "Deep Learning Models"

        "Deep Learning"

    """

    tokens_a = canonical_tokens(
        value_a
    )

    tokens_b = canonical_tokens(
        value_b
    )

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = (
        tokens_a
        &
        tokens_b
    )

    return safe_divide(
        len(intersection),
        min(
            len(tokens_a),
            len(tokens_b),
        ),
        0.0,
    )


# ============================================================
# 37. MATCH SCORE
# ============================================================

def calculate_match_score(
    source: Any,
    target: Any,
) -> float:
    """
    Calculate robust pairwise similarity.

    Strategy:

        1. Exact match
        2. Canonical/alias match
        3. Hybrid text similarity
        4. Token overlap

    Returns:
        0.0 - 1.0
    """

    source_text = object_text(
        source
    )

    target_text = object_text(
        target
    )

    if not source_text or not target_text:
        return 0.0

    # --------------------------------------------------------
    # Exact
    # --------------------------------------------------------

    if exact_match(
        source_text,
        target_text,
    ):
        return 1.0

    # --------------------------------------------------------
    # Canonical exact
    # --------------------------------------------------------

    if canonical_match(
        source_text,
        target_text,
    ):
        return 0.98

    # --------------------------------------------------------
    # Name comparison
    # --------------------------------------------------------

    source_name = object_name(
        source
    )

    target_name = object_name(
        target
    )

    name_score = canonical_similarity(
        source_name,
        target_name,
    )

    # --------------------------------------------------------
    # Full text comparison
    # --------------------------------------------------------

    text_score = hybrid_similarity(
        source_text,
        target_text,
    )

    # --------------------------------------------------------
    # Token overlap
    # --------------------------------------------------------

    overlap_score = token_overlap(
        source_text,
        target_text,
    )

    # --------------------------------------------------------
    # Weighted result
    # --------------------------------------------------------

    score = (

        name_score * 0.55

        +

        text_score * 0.30

        +

        overlap_score * 0.15

    )

    return round(
        max(
            0.0,
            min(
                1.0,
                score,
            ),
        ),
        4,
    )


# ============================================================
# 38. MATCH TYPE
# ============================================================

def determine_match_type(
    source: Any,
    target: Any,
    score: float,
) -> str:
    """
    Determine why two items were matched.
    """

    source_name = object_name(
        source
    )

    target_name = object_name(
        target
    )

    if exact_match(
        source_name,
        target_name,
    ):
        return "exact"

    if canonical_match(
        source_name,
        target_name,
    ):
        return "alias"

    if score >= 0.90:
        return "strong_semantic"

    if score >= 0.72:
        return "semantic"

    if score >= 0.55:
        return "weak_semantic"

    return "unmatched"


# ============================================================
# 39. MATCH CONFIDENCE
# ============================================================

def match_confidence(
    score: float,
) -> float:
    """
    Convert similarity into confidence.

    Higher similarity produces higher confidence.
    """

    score = max(
        0.0,
        min(
            1.0,
            safe_float(
                score
            ),
        ),
    )

    if score >= 0.95:
        confidence = 0.98

    elif score >= 0.90:
        confidence = 0.94

    elif score >= 0.80:
        confidence = 0.88

    elif score >= 0.72:
        confidence = 0.78

    elif score >= 0.60:
        confidence = 0.62

    elif score >= 0.50:
        confidence = 0.45

    else:
        confidence = 0.20

    return round(
        confidence,
        4,
    )


# ============================================================
# 40. BUILD MATCH RESULT
# ============================================================

def build_match_result(
    source: Any,
    target: Any,
    source_index: Optional[int] = None,
    target_index: Optional[int] = None,
) -> MatchResult:
    """
    Create MatchResult for two objects.
    """

    score = calculate_match_score(
        source,
        target,
    )

    match_type = determine_match_type(
        source,
        target,
        score,
    )

    confidence = match_confidence(
        score
    )

    return MatchResult(

        source_name=object_name(
            source
        ),

        target_name=object_name(
            target
        ),

        similarity=round(
            score,
            4,
        ),

        match_type=match_type,

        confidence=confidence,

        source_index=source_index,

        target_index=target_index,

    )


# ============================================================
# 41. BUILD SIMILARITY MATRIX
# ============================================================

def build_similarity_matrix(
    source_items: Sequence[Any],
    target_items: Sequence[Any],
) -> List[List[float]]:
    """
    Build a pairwise similarity matrix.

    Matrix dimensions:

        len(source_items)
        ×
        len(target_items)
    """

    matrix = []

    for source in source_items:

        row = []

        for target in target_items:

            row.append(
                calculate_match_score(
                    source,
                    target,
                )
            )

        matrix.append(
            row
        )

    return matrix


# ============================================================
# 42. BEST TARGET INDEX
# ============================================================

def best_target_index(
    scores: Sequence[float],
    used_indices: Optional[
        Set[int]
    ] = None,
) -> Optional[int]:
    """
    Find the highest unused target index.
    """

    if not scores:
        return None

    used_indices = (
        used_indices
        or set()
    )

    best_index = None
    best_score = -1.0

    for index, score in enumerate(
        scores
    ):

        if index in used_indices:
            continue

        score = safe_float(
            score
        )

        if score > best_score:

            best_score = score

            best_index = index

    return best_index


# ============================================================
# 43. ONE-TO-ONE MATCHING
# ============================================================

def match_items(
    source_items: Sequence[Any],
    target_items: Sequence[Any],
    threshold: float = DEFAULT_MATCH_THRESHOLD,
    max_items: Optional[int] = None,
) -> CategoryComparison:
    """
    Match source items against target items.

    Each target item can be matched only once.

    Example:

        Curriculum A skills
                    ↓
                match_items
                    ↓
        Curriculum B skills

    Result:

        matched
        missing
        additional
        coverage
        similarity
    """

    source_items = list(
        source_items or []
    )

    target_items = list(
        target_items or []
    )


    if max_items is not None:

        source_items = source_items[
            :max_items
        ]

        target_items = target_items[
            :max_items
        ]


    source_count = len(
        source_items
    )

    target_count = len(
        target_items
    )


    # --------------------------------------------------------
    # Empty comparison
    # --------------------------------------------------------

    if source_count == 0:

        return CategoryComparison(

            category="unknown",

            source_count=0,

            target_count=target_count,

            matched_count=0,

            missing_count=0,

            additional_count=target_count,

            coverage_percentage=100.0,

            similarity_percentage=0.0,

            matched=[],

            missing=[],

            additional=[
                object_name(item)
                for item in target_items
            ],

        )


    if target_count == 0:

        return CategoryComparison(

            category="unknown",

            source_count=source_count,

            target_count=0,

            matched_count=0,

            missing_count=source_count,

            additional_count=0,

            coverage_percentage=0.0,

            similarity_percentage=0.0,

            matched=[],

            missing=[
                object_name(item)
                for item in source_items
            ],

            additional=[],

        )


    # --------------------------------------------------------
    # Similarity matrix
    # --------------------------------------------------------

    matrix = build_similarity_matrix(

        source_items,

        target_items,

    )


    used_targets: Set[int] = set()

    matches: List[
        MatchResult
    ] = []

    missing: List[str] = []


    # --------------------------------------------------------
    # First pass:
    # strongest candidates first
    # --------------------------------------------------------

    candidate_pairs = []


    for source_index, row in enumerate(
        matrix
    ):

        for target_index, score in enumerate(
            row
        ):

            candidate_pairs.append(

                (
                    score,
                    source_index,
                    target_index,
                )

            )


    candidate_pairs.sort(
        key=lambda item:
            item[0],
        reverse=True,
    )


    matched_sources: Set[int] = set()


    # --------------------------------------------------------
    # Greedy one-to-one assignment
    # --------------------------------------------------------

    for (
        score,
        source_index,
        target_index,
    ) in candidate_pairs:

        if score < threshold:
            break

        if source_index in matched_sources:
            continue

        if target_index in used_targets:
            continue


        match = build_match_result(

            source_items[
                source_index
            ],

            target_items[
                target_index
            ],

            source_index=source_index,

            target_index=target_index,

        )


        matches.append(
            match
        )


        matched_sources.add(
            source_index
        )


        used_targets.add(
            target_index
        )


    # --------------------------------------------------------
    # Missing source items
    # --------------------------------------------------------

    for source_index, source in enumerate(
        source_items
    ):

        if source_index in matched_sources:
            continue

        missing.append(
            object_name(
                source
            )
        )


    # --------------------------------------------------------
    # Additional target items
    # --------------------------------------------------------

    additional = []


    for target_index, target in enumerate(
        target_items
    ):

        if target_index in used_targets:
            continue

        additional.append(
            object_name(
                target
            )
        )


    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    matched_count = len(
        matches
    )

    missing_count = len(
        missing
    )

    additional_count = len(
        additional
    )


    coverage = percentage(
        matched_count,
        source_count,
    )


    if matches:

        average_similarity = (
            sum(
                match.similarity
                for match in matches
            )
            /
            len(matches)
        )

    else:

        average_similarity = 0.0


    # --------------------------------------------------------
    # Similarity percentage
    # --------------------------------------------------------

    similarity_percentage = round(

        average_similarity
        * 100,

        2,

    )


    return CategoryComparison(

        category="unknown",

        source_count=source_count,

        target_count=target_count,

        matched_count=matched_count,

        missing_count=missing_count,

        additional_count=additional_count,

        coverage_percentage=coverage,

        similarity_percentage=similarity_percentage,

        matched=matches,

        missing=missing,

        additional=additional,

    )


# ============================================================
# 44. CATEGORY MATCHING
# ============================================================

def compare_category(
    category: str,
    source_items: Sequence[Any],
    target_items: Sequence[Any],
    config: Optional[
        ComparatorConfig
    ] = None,
) -> CategoryComparison:
    """
    Compare one curriculum category.
    """

    config = (
        config
        or ComparatorConfig()
    )


    result = match_items(

        source_items=source_items,

        target_items=target_items,

        threshold=config.match_threshold,

        max_items=config.max_items_per_category,

    )


    result.category = category


    return result


# ============================================================
# 45. MATCH BY NAME
# ============================================================

def match_by_name(
    source_items: Sequence[Any],
    target_items: Sequence[Any],
) -> Dict[
    str,
    Any,
]:
    """
    Create a dictionary mapping normalized names to objects.
    """

    result = {}


    for item in target_items:

        name = object_name(
            item
        )


        key = canonical_term(
            name
        )


        if not key:
            continue


        if key not in result:

            result[key] = item


    return result


# ============================================================
# 46. EXACT INTERSECTION
# ============================================================

def exact_intersection(
    source_values: Iterable[Any],
    target_values: Iterable[Any],
) -> List[str]:
    """
    Return exact canonical intersections.
    """

    source = set(

        canonical_term(
            value
        )

        for value in source_values

        if canonical_term(
            value
        )

    )


    target = set(

        canonical_term(
            value
        )

        for value in target_values

        if canonical_term(
            value
        )

    )


    return sorted(
        source & target
    )


# ============================================================
# 47. SET DIFFERENCE
# ============================================================

def normalized_difference(
    source_values: Iterable[Any],
    target_values: Iterable[Any],
) -> List[str]:
    """
    Return source values absent from target values.
    """

    source_map = {}


    for value in source_values:

        canonical = canonical_term(
            value
        )


        if canonical:

            source_map[
                canonical
            ] = clean_text(
                value
            )


    target = {

        canonical_term(
            value
        )

        for value in target_values

        if canonical_term(
            value
        )

    }


    return [

        original

        for canonical, original
        in source_map.items()

        if canonical not in target

    ]


# ============================================================
# 48. FUZZY MISSING DETECTION
# ============================================================

def fuzzy_missing_values(
    source_values: Iterable[Any],
    target_values: Iterable[Any],
    threshold: float = DEFAULT_MATCH_THRESHOLD,
) -> List[str]:
    """
    Find source values that have no sufficiently similar
    target value.

    This is useful for concepts and skills where terminology
    differs between institutions.
    """

    source = list(
        source_values
    )

    target = list(
        target_values
    )


    missing = []


    for source_value in source:

        best_score = 0.0


        for target_value in target:

            score = canonical_similarity(

                source_value,

                target_value,

            )


            best_score = max(
                best_score,
                score,
            )


        if best_score < threshold:

            missing.append(
                clean_text(
                    source_value
                )
            )


    return deduplicate(
        missing
    )


# ============================================================
# 49. FIND STRONGEST MATCH
# ============================================================

def find_strongest_match(
    source: Any,
    candidates: Sequence[Any],
) -> Optional[
    MatchResult
]:
    """
    Find the strongest candidate for one source item.
    """

    if not candidates:
        return None


    best_candidate = None

    best_score = -1.0

    best_index = None


    for index, candidate in enumerate(
        candidates
    ):

        score = calculate_match_score(

            source,

            candidate,

        )


        if score > best_score:

            best_score = score

            best_candidate = candidate

            best_index = index


    if best_candidate is None:
        return None


    return build_match_result(

        source,

        best_candidate,

        source_index=0,

        target_index=best_index,

    )


# ============================================================
# 50. MATCH QUALITY
# ============================================================

def match_quality(
    similarity: float,
) -> str:
    """
    Convert similarity score to human-readable quality.
    """

    score = safe_float(
        similarity
    )


    if score >= 0.90:
        return "Excellent"

    if score >= 0.80:
        return "Strong"

    if score >= 0.72:
        return "Good"

    if score >= 0.60:
        return "Moderate"

    if score >= 0.50:
        return "Weak"

    return "No Match"


# ============================================================
# 51. MATCH_RESULT TO DICT
# ============================================================

def match_result_to_dict(
    result: MatchResult,
) -> Dict[str, Any]:
    """
    Convert MatchResult to serializable dictionary.
    """

    return {

        "source_name":
            result.source_name,

        "target_name":
            result.target_name,

        "similarity":
            round(
                result.similarity * 100,
                2,
            ),

        "similarity_score":
            result.similarity,

        "match_type":
            result.match_type,

        "quality":
            match_quality(
                result.similarity
            ),

        "confidence":
            round(
                result.confidence * 100,
                2,
            ),

        "source_index":
            result.source_index,

        "target_index":
            result.target_index,

        "evidence":
            list(
                result.evidence
            ),

        "explanation":
            result.explanation,

    }


# ============================================================
# 52. CATEGORY_RESULT TO DICT
# ============================================================

def category_result_to_dict(
    result: CategoryComparison,
) -> Dict[str, Any]:
    """
    Convert CategoryComparison to JSON-compatible dict.
    """

    return {

        "category":
            result.category,

        "source_count":
            result.source_count,

        "target_count":
            result.target_count,

        "matched_count":
            result.matched_count,

        "missing_count":
            result.missing_count,

        "additional_count":
            result.additional_count,

        "coverage_percentage":
            result.coverage_percentage,

        "similarity_percentage":
            result.similarity_percentage,

        "matched":
            [
                match_result_to_dict(
                    match
                )

                for match in result.matched
            ],

        "missing":
            list(
                result.missing
            ),

        "additional":
            list(
                result.additional
            ),

    }


# ============================================================
# 53. RANK MATCHES
# ============================================================

def rank_matches(
    matches: Sequence[
        MatchResult
    ],
    descending: bool = True,
) -> List[
    MatchResult
]:
    """
    Rank matches by similarity.
    """

    return sorted(

        list(
            matches
        ),

        key=lambda match:
            match.similarity,

        reverse=descending,

    )


# ============================================================
# 54. TOP_MATCHES
# ============================================================

def top_matches(
    matches: Sequence[
        MatchResult
    ],
    limit: int = 10,
) -> List[
    MatchResult
]:
    """
    Return top N matches.
    """

    return rank_matches(
        matches
    )[
        :max(
            0,
            limit,
        )
    ]


# ============================================================
# 55. LOW_CONFIDENCE_MATCHES
# ============================================================

def low_confidence_matches(
    matches: Sequence[
        MatchResult
    ],
    threshold: float = 0.70,
) -> List[
    MatchResult
]:
    """
    Return matches requiring further validation.
    """

    return [

        match

        for match in matches

        if match.confidence < threshold

    ]


# ============================================================
# 56. END OF CHUNK 2
# ============================================================
# ============================================================
# curriculum/comparator.py
# CHUNK 3/10
#
# MODULE-WISE + TOPIC-WISE COMPARISON
#
# Curriculum A
#      │
#      ├── Module 1 ─────────┐
#      │                     │
#      ├── Module 2 ───────┐ │
#      │                   │ │
#      └── Module N        │ │
#                          ▼ ▼
#                    Module Matching
#                          │
#                          ▼
#                    Topic Matching
#                          │
#              ┌───────────┼───────────┐
#              ▼           ▼           ▼
#           Matched      Missing    Additional
# ============================================================


# ============================================================
# 57. MODULE TOPIC EXTRACTION
# ============================================================

def get_module_topics(
    module: Any,
) -> List[Any]:
    """
    Safely extract topics from a Module.

    Supports both:
        - Pydantic Module
        - dictionary representation
    """

    topics = get_attr(
        module,
        "topics",
        [],
    )

    if topics is None:
        return []

    if isinstance(
        topics,
        list,
    ):
        return topics

    try:

        return list(
            topics
        )

    except TypeError:

        return []


# ============================================================
# 58. MODULE PROJECT EXTRACTION
# ============================================================

def get_module_projects(
    module: Any,
) -> List[Any]:
    """
    Safely extract projects from a Module.
    """

    projects = get_attr(
        module,
        "projects",
        [],
    )

    if projects is None:
        return []

    if isinstance(
        projects,
        list,
    ):
        return projects

    try:

        return list(
            projects
        )

    except TypeError:

        return []


# ============================================================
# 59. MODULE CONCEPTS
# ============================================================

def get_module_concepts(
    module: Any,
) -> List[str]:
    """
    Get concepts directly declared on a module,
    plus concepts declared inside its topics.
    """

    values = []

    values.extend(
        get_attr(
            module,
            "concepts",
            [],
        )
        or []
    )

    for topic in get_module_topics(
        module
    ):

        values.extend(
            get_attr(
                topic,
                "concepts",
                [],
            )
            or []
        )

    return deduplicate(
        values
    )


# ============================================================
# 60. MODULE SKILLS
# ============================================================

def get_module_skills(
    module: Any,
) -> List[str]:
    """
    Get skills from module and its topics.
    """

    values = []

    values.extend(
        get_attr(
            module,
            "skills",
            [],
        )
        or []
    )

    for topic in get_module_topics(
        module
    ):

        values.extend(
            get_attr(
                topic,
                "skills",
                [],
            )
            or []
        )

    return deduplicate(
        values
    )


# ============================================================
# 61. MODULE TOOLS
# ============================================================

def get_module_tools(
    module: Any,
) -> List[str]:
    """
    Get tools from module and its topics.
    """

    values = []

    values.extend(
        get_attr(
            module,
            "tools",
            [],
        )
        or []
    )

    for topic in get_module_topics(
        module
    ):

        values.extend(
            get_attr(
                topic,
                "tools",
                [],
            )
            or []
        )

    return deduplicate(
        values
    )


# ============================================================
# 62. MODULE TECHNOLOGIES
# ============================================================

def get_module_technologies(
    module: Any,
) -> List[str]:
    """
    Get technologies from module and its topics.
    """

    values = []

    values.extend(
        get_attr(
            module,
            "technologies",
            [],
        )
        or []
    )

    for topic in get_module_topics(
        module
    ):

        values.extend(
            get_attr(
                topic,
                "technologies",
                [],
            )
            or []
        )

    return deduplicate(
        values
    )


# ============================================================
# 63. MODULE HOURS
# ============================================================

def get_module_hours(
    module: Any,
) -> float:
    """
    Safely obtain module teaching hours.

    Falls back to topic hours if module hours are zero.
    """

    hours = safe_float(
        get_attr(
            module,
            "hours",
            0,
        )
    )

    if hours > 0:
        return hours

    topic_hours = 0.0

    for topic in get_module_topics(
        module
    ):

        topic_hours += safe_float(
            get_attr(
                topic,
                "hours",
                0,
            )
        )

    return topic_hours


# ============================================================
# 64. TOPIC TEXT
# ============================================================

def topic_text(
    topic: Any,
) -> str:
    """
    Return rich text representation of a topic.
    """

    name = object_name(
        topic
    )

    description = object_description(
        topic
    )

    concepts = normalize_list(
        get_attr(
            topic,
            "concepts",
            [],
        )
    )

    skills = normalize_list(
        get_attr(
            topic,
            "skills",
            [],
        )
    )

    technologies = normalize_list(
        get_attr(
            topic,
            "technologies",
            [],
        )
    )


    parts = []


    if name:
        parts.append(
            name
        )

    if description:
        parts.append(
            description
        )

    if concepts:
        parts.append(
            "Concepts: "
            + ", ".join(
                concepts
            )
        )

    if skills:
        parts.append(
            "Skills: "
            + ", ".join(
                skills
            )
        )

    if technologies:
        parts.append(
            "Technologies: "
            + ", ".join(
                technologies
            )
        )


    return ". ".join(
        parts
    )


# ============================================================
# 65. TOPIC MATCH SCORE
# ============================================================

def calculate_topic_match_score(
    topic_a: Any,
    topic_b: Any,
) -> float:
    """
    Calculate topic similarity.

    Topic comparison uses:

        name
        description
        concepts
        skills
        technologies
        tools
    """

    name_a = object_name(
        topic_a
    )

    name_b = object_name(
        topic_b
    )


    name_score = canonical_similarity(
        name_a,
        name_b,
    )


    text_score = hybrid_similarity(
        topic_text(
            topic_a
        ),
        topic_text(
            topic_b
        ),
    )


    concept_a = normalize_list(
        get_attr(
            topic_a,
            "concepts",
            [],
        )
    )

    concept_b = normalize_list(
        get_attr(
            topic_b,
            "concepts",
            [],
        )
    )


    skill_a = normalize_list(
        get_attr(
            topic_a,
            "skills",
            [],
        )
    )

    skill_b = normalize_list(
        get_attr(
            topic_b,
            "skills",
            [],
        )
    )


    tech_a = normalize_list(
        get_attr(
            topic_a,
            "technologies",
            [],
        )
    )

    tech_b = normalize_list(
        get_attr(
            topic_b,
            "technologies",
            [],
        )
    )


    concept_score = list_similarity(
        concept_a,
        concept_b,
    )


    skill_score = list_similarity(
        skill_a,
        skill_b,
    )


    technology_score = list_similarity(
        tech_a,
        tech_b,
    )


    score = (

        name_score * 0.40

        +

        text_score * 0.25

        +

        concept_score * 0.15

        +

        skill_score * 0.10

        +

        technology_score * 0.10

    )


    return round(
        max(
            0.0,
            min(
                1.0,
                score,
            ),
        ),
        4,
    )


# ============================================================
# 66. LIST SIMILARITY
# ============================================================

def list_similarity(
    values_a: Sequence[Any],
    values_b: Sequence[Any],
) -> float:
    """
    Compare two lists of concepts/skills/tools/etc.

    Uses best-match coverage rather than simple set
    intersection.

    This allows:

        ["RAG"]

    to match:

        ["Retrieval Augmented Generation"]
    """

    a = deduplicate(
        values_a
    )

    b = deduplicate(
        values_b
    )


    if not a and not b:
        return 1.0

    if not a or not b:
        return 0.0


    scores = []


    for value_a in a:

        best = 0.0


        for value_b in b:

            best = max(

                best,

                canonical_similarity(
                    value_a,
                    value_b,
                ),

            )


        scores.append(
            best
        )


    if not scores:
        return 0.0


    return round(
        sum(scores)
        /
        len(scores),
        4,
    )


# ============================================================
# 67. MODULE MATCH SCORE
# ============================================================

def calculate_module_match_score(
    module_a: Any,
    module_b: Any,
) -> float:
    """
    Calculate module-level similarity.

    Module matching considers:

        Module name
        Description
        Topics
        Concepts
        Skills
        Technologies
    """

    name_score = canonical_similarity(

        object_name(
            module_a
        ),

        object_name(
            module_b
        ),

    )


    description_score = hybrid_similarity(

        object_description(
            module_a
        ),

        object_description(
            module_b
        ),

    )


    topics_a = get_module_topics(
        module_a
    )

    topics_b = get_module_topics(
        module_b
    )


    topic_names_a = [
        object_name(
            topic
        )
        for topic in topics_a
    ]

    topic_names_b = [
        object_name(
            topic
        )
        for topic in topics_b
    ]


    topic_score = list_similarity(
        topic_names_a,
        topic_names_b,
    )


    concept_score = list_similarity(

        get_module_concepts(
            module_a
        ),

        get_module_concepts(
            module_b
        ),

    )


    skill_score = list_similarity(

        get_module_skills(
            module_a
        ),

        get_module_skills(
            module_b
        ),

    )


    technology_score = list_similarity(

        get_module_technologies(
            module_a
        ),

        get_module_technologies(
            module_b
        ),

    )


    score = (

        name_score * 0.35

        +

        description_score * 0.10

        +

        topic_score * 0.25

        +

        concept_score * 0.10

        +

        skill_score * 0.10

        +

        technology_score * 0.10

    )


    return round(
        max(
            0.0,
            min(
                1.0,
                score,
            ),
        ),
        4,
    )


# ============================================================
# 68. BUILD MODULE SIMILARITY MATRIX
# ============================================================

def build_module_similarity_matrix(
    source_modules: Sequence[Any],
    target_modules: Sequence[Any],
) -> List[List[float]]:
    """
    Build module-to-module similarity matrix.
    """

    matrix = []


    for source_module in source_modules:

        row = []


        for target_module in target_modules:

            row.append(

                calculate_module_match_score(

                    source_module,

                    target_module,

                )

            )


        matrix.append(
            row
        )


    return matrix


# ============================================================
# 69. TOPIC COMPARISON RESULT
# ============================================================

@dataclass
class TopicComparison:
    """
    Detailed comparison between two matched topics.
    """

    source_topic: str

    target_topic: str

    similarity_percentage: float

    source_hours: float

    target_hours: float

    hours_difference: float

    concepts: CategoryComparison

    skills: CategoryComparison

    tools: CategoryComparison

    technologies: CategoryComparison

    source_bloom_level: Optional[str] = None

    target_bloom_level: Optional[str] = None

    difficulty_change: Optional[str] = None

    enhancement_needed: bool = False

    enhancement_reasons: List[str] = field(
        default_factory=list
    )


# ============================================================
# 70. MODULE COMPARISON RESULT
# ============================================================

@dataclass
class ModuleComparison:
    """
    Detailed comparison between two modules.
    """

    source_module: str

    target_module: str

    similarity_percentage: float

    source_hours: float

    target_hours: float

    hours_difference: float

    topics: List[
        TopicComparison
    ] = field(
        default_factory=list
    )

    matched_topics: List[str] = field(
        default_factory=list
    )

    missing_topics: List[str] = field(
        default_factory=list
    )

    additional_topics: List[str] = field(
        default_factory=list
    )

    concepts: Optional[
        CategoryComparison
    ] = None

    skills: Optional[
        CategoryComparison
    ] = None

    tools: Optional[
        CategoryComparison
    ] = None

    technologies: Optional[
        CategoryComparison
    ] = None

    projects: Optional[
        CategoryComparison
    ] = None

    enhancement_needed: bool = False

    enhancement_reasons: List[str] = field(
        default_factory=list
    )


# ============================================================
# 71. FIND BEST MODULE MATCHES
# ============================================================

def match_modules(
    source_modules: Sequence[Any],
    target_modules: Sequence[Any],
    config: Optional[
        ComparatorConfig
    ] = None,
) -> Tuple[
    List[
        Tuple[
            int,
            int,
            float,
        ]
    ],
    List[int],
    List[int],
]:
    """
    Match source modules to target modules.

    Returns:

        matched_pairs
        unmatched_source_indices
        unmatched_target_indices

    matched_pairs contains:

        (
            source_index,
            target_index,
            similarity
        )
    """

    config = (
        config
        or ComparatorConfig()
    )


    source_modules = list(
        source_modules
        or []
    )

    target_modules = list(
        target_modules
        or []
    )


    if not source_modules:

        return (
            [],
            [],
            list(
                range(
                    len(
                        target_modules
                    )
                )
            ),
        )


    if not target_modules:

        return (
            [],
            list(
                range(
                    len(
                        source_modules
                    )
                )
            ),
            [],
        )


    matrix = (
        build_module_similarity_matrix(
            source_modules,
            target_modules,
        )
    )


    candidates = []


    for source_index, row in enumerate(
        matrix
    ):

        for target_index, score in enumerate(
            row
        ):

            candidates.append(

                (
                    score,
                    source_index,
                    target_index,
                )

            )


    candidates.sort(
        key=lambda item:
            item[0],
        reverse=True,
    )


    matched_pairs = []

    used_source = set()

    used_target = set()


    for (
        score,
        source_index,
        target_index,
    ) in candidates:

        if score < config.match_threshold:
            break


        if source_index in used_source:
            continue


        if target_index in used_target:
            continue


        matched_pairs.append(

            (
                source_index,
                target_index,
                score,
            )

        )


        used_source.add(
            source_index
        )

        used_target.add(
            target_index
        )


    unmatched_source = [

        index

        for index in range(
            len(
                source_modules
            )
        )

        if index not in used_source

    ]


    unmatched_target = [

        index

        for index in range(
            len(
                target_modules
            )
        )

        if index not in used_target

    ]


    return (

        matched_pairs,

        unmatched_source,

        unmatched_target,

    )


# ============================================================
# 72. COMPARE TOPICS INSIDE MODULE
# ============================================================

def compare_topics(
    source_topics: Sequence[Any],
    target_topics: Sequence[Any],
    config: Optional[
        ComparatorConfig
    ] = None,
) -> Tuple[
    List[
        TopicComparison
    ],
    CategoryComparison,
]:
    """
    Compare topics within two matched modules.
    """

    config = (
        config
        or ComparatorConfig()
    )


    source_topics = list(
        source_topics
        or []
    )

    target_topics = list(
        target_topics
        or []
    )


    # --------------------------------------------------------
    # Match topics
    # --------------------------------------------------------

    matrix = []


    for source_topic in source_topics:

        row = []


        for target_topic in target_topics:

            row.append(

                calculate_topic_match_score(

                    source_topic,

                    target_topic,

                )

            )


        matrix.append(
            row
        )


    candidates = []


    for source_index, row in enumerate(
        matrix
    ):

        for target_index, score in enumerate(
            row
        ):

            candidates.append(

                (
                    score,
                    source_index,
                    target_index,
                )

            )


    candidates.sort(
        key=lambda item:
            item[0],
        reverse=True,
    )


    used_source = set()

    used_target = set()

    topic_comparisons = []


    # --------------------------------------------------------
    # Pair topics
    # --------------------------------------------------------

    for (
        score,
        source_index,
        target_index,
    ) in candidates:

        if score < config.match_threshold:
            break


        if source_index in used_source:
            continue


        if target_index in used_target:
            continue


        source_topic = source_topics[
            source_index
        ]

        target_topic = target_topics[
            target_index
        ]


        topic_comparison = (
            build_topic_comparison(

                source_topic,

                target_topic,

                score,

                source_index,

                target_index,

                config,

            )
        )


        topic_comparisons.append(
            topic_comparison
        )


        used_source.add(
            source_index
        )

        used_target.add(
            target_index
        )


    # --------------------------------------------------------
    # Missing topics
    # --------------------------------------------------------

    missing_topics = [

        object_name(
            source_topics[index]
        )

        for index in range(
            len(
                source_topics
            )
        )

        if index not in used_source

    ]


    # --------------------------------------------------------
    # Additional topics
    # --------------------------------------------------------

    additional_topics = [

        object_name(
            target_topics[index]
        )

        for index in range(
            len(
                target_topics
            )
        )

        if index not in used_target

    ]


    # --------------------------------------------------------
    # Category comparison
    # --------------------------------------------------------

    topic_category = CategoryComparison(

        category="topics",

        source_count=len(
            source_topics
        ),

        target_count=len(
            target_topics
        ),

        matched_count=len(
            topic_comparisons
        ),

        missing_count=len(
            missing_topics
        ),

        additional_count=len(
            additional_topics
        ),

        coverage_percentage=percentage(

            len(
                topic_comparisons
            ),

            len(
                source_topics
            ),

        ),

        similarity_percentage=(

            round(

                (
                    sum(
                        item.similarity_percentage
                        for item in topic_comparisons
                    )
                    /
                    len(
                        topic_comparisons
                    )
                )

                if topic_comparisons

                else 0.0,

                2,

            )

        ),

        matched=[],

        missing=missing_topics,

        additional=additional_topics,

    )


    return (
        topic_comparisons,
        topic_category,
    )


# ============================================================
# 73. BUILD TOPIC COMPARISON
# ============================================================

def build_topic_comparison(
    source_topic: Any,
    target_topic: Any,
    similarity: float,
    source_index: int,
    target_index: int,
    config: ComparatorConfig,
) -> TopicComparison:
    """
    Build detailed topic comparison.
    """

    # --------------------------------------------------------
    # Concepts
    # --------------------------------------------------------

    source_concepts = normalize_list(

        get_attr(
            source_topic,
            "concepts",
            [],
        )

    )


    target_concepts = normalize_list(

        get_attr(
            target_topic,
            "concepts",
            [],
        )

    )


    concept_result = compare_category_values(

        category="concepts",

        source_values=source_concepts,

        target_values=target_concepts,

        config=config,

    )


    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    source_skills = normalize_list(

        get_attr(
            source_topic,
            "skills",
            [],
        )

    )


    target_skills = normalize_list(

        get_attr(
            target_topic,
            "skills",
            [],
        )

    )


    skill_result = compare_category_values(

        category="skills",

        source_values=source_skills,

        target_values=target_skills,

        config=config,

    )


    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    source_tools = normalize_list(

        get_attr(
            source_topic,
            "tools",
            [],
        )

    )


    target_tools = normalize_list(

        get_attr(
            target_topic,
            "tools",
            [],
        )

    )


    tool_result = compare_category_values(

        category="tools",

        source_values=source_tools,

        target_values=target_tools,

        config=config,

    )


    # --------------------------------------------------------
    # Technologies
    # --------------------------------------------------------

    source_technologies = normalize_list(

        get_attr(
            source_topic,
            "technologies",
            [],
        )

    )


    target_technologies = normalize_list(

        get_attr(
            target_topic,
            "technologies",
            [],
        )

    )


    technology_result = compare_category_values(

        category="technologies",

        source_values=source_technologies,

        target_values=target_technologies,

        config=config,

    )


    # --------------------------------------------------------
    # Hours
    # --------------------------------------------------------

    source_hours = safe_float(

        get_attr(
            source_topic,
            "hours",
            0,
        )

    )


    target_hours = safe_float(

        get_attr(
            target_topic,
            "hours",
            0,
        )

    )


    hours_difference = round(

        target_hours
        -
        source_hours,

        2,

    )


    # --------------------------------------------------------
    # Bloom level
    # --------------------------------------------------------

    source_bloom = clean_text(

        get_attr(
            source_topic,
            "bloom_level",
            "",
        )

    ) or None


    target_bloom = clean_text(

        get_attr(
            target_topic,
            "bloom_level",
            "",
        )

    ) or None


    # --------------------------------------------------------
    # Difficulty
    # --------------------------------------------------------

    source_difficulty = clean_text(

        get_attr(
            source_topic,
            "difficulty",
            "",
        )

    )


    target_difficulty = clean_text(

        get_attr(
            target_topic,
            "difficulty",
            "",
        )

    )


    difficulty_change = None


    if (
        source_difficulty
        and target_difficulty
        and
        normalize_text(
            source_difficulty
        )
        !=
        normalize_text(
            target_difficulty
        )
    ):

        difficulty_change = (

            f"{source_difficulty} → "
            f"{target_difficulty}"

        )


    # --------------------------------------------------------
    # Enhancement determination
    # --------------------------------------------------------

    enhancement_reasons = []


    if concept_result.missing_count > 0:

        enhancement_reasons.append(

            (
                f"{concept_result.missing_count} "
                "concept(s) missing"
            )

        )


    if skill_result.missing_count > 0:

        enhancement_reasons.append(

            (
                f"{skill_result.missing_count} "
                "skill(s) missing"
            )

        )


    if technology_result.missing_count > 0:

        enhancement_reasons.append(

            (
                f"{technology_result.missing_count} "
                "technology/technologies missing"
            )

        )


    if (
        source_hours > 0
        and target_hours > 0
        and target_hours < source_hours * 0.75
    ):

        enhancement_reasons.append(

            "Target curriculum allocates substantially "
            "less teaching time."

        )


    enhancement_needed = bool(
        enhancement_reasons
    )


    return TopicComparison(

        source_topic=object_name(
            source_topic
        ),

        target_topic=object_name(
            target_topic
        ),

        similarity_percentage=round(
            similarity * 100,
            2,
        ),

        source_hours=source_hours,

        target_hours=target_hours,

        hours_difference=hours_difference,

        concepts=concept_result,

        skills=skill_result,

        tools=tool_result,

        technologies=technology_result,

        source_bloom_level=source_bloom,

        target_bloom_level=target_bloom,

        difficulty_change=difficulty_change,

        enhancement_needed=enhancement_needed,

        enhancement_reasons=enhancement_reasons,

    )


# ============================================================
# 74. COMPARE CATEGORY VALUES
# ============================================================

def compare_category_values(
    category: str,
    source_values: Sequence[str],
    target_values: Sequence[str],
    config: Optional[
        ComparatorConfig
    ] = None,
) -> CategoryComparison:
    """
    Compare string-based curriculum categories.

    Used for:

        concepts
        skills
        tools
        technologies
        prerequisites
        case studies
    """

    config = (
        config
        or ComparatorConfig()
    )


    source_values = deduplicate(
        source_values
    )

    target_values = deduplicate(
        target_values
    )


    # --------------------------------------------------------
    # Empty source
    # --------------------------------------------------------

    if not source_values:

        return CategoryComparison(

            category=category,

            source_count=0,

            target_count=len(
                target_values
            ),

            matched_count=0,

            missing_count=0,

            additional_count=len(
                target_values
            ),

            coverage_percentage=100.0,

            similarity_percentage=0.0,

            matched=[],

            missing=[],

            additional=target_values,

        )


    # --------------------------------------------------------
    # Empty target
    # --------------------------------------------------------

    if not target_values:

        return CategoryComparison(

            category=category,

            source_count=len(
                source_values
            ),

            target_count=0,

            matched_count=0,

            missing_count=len(
                source_values
            ),

            additional_count=0,

            coverage_percentage=0.0,

            similarity_percentage=0.0,

            matched=[],

            missing=source_values,

            additional=[],

        )


    # --------------------------------------------------------
    # Match values
    # --------------------------------------------------------

    candidates = []


    for source_index, source_value in enumerate(
        source_values
    ):

        for target_index, target_value in enumerate(
            target_values
        ):

            score = canonical_similarity(

                source_value,

                target_value,

            )


            candidates.append(

                (
                    score,
                    source_index,
                    target_index,
                )

            )


    candidates.sort(
        key=lambda item:
            item[0],
        reverse=True,
    )


    used_source = set()

    used_target = set()

    matched = []


    for (
        score,
        source_index,
        target_index,
    ) in candidates:

        if score < config.match_threshold:
            break


        if source_index in used_source:
            continue


        if target_index in used_target:
            continue


        source_value = source_values[
            source_index
        ]

        target_value = target_values[
            target_index
        ]


        matched.append(

            MatchResult(

                source_name=source_value,

                target_name=target_value,

                similarity=score,

                match_type=(

                    "exact"

                    if canonical_match(
                        source_value,
                        target_value,
                    )

                    else "semantic"

                ),

                confidence=match_confidence(
                    score
                ),

                source_index=source_index,

                target_index=target_index,

            )

        )


        used_source.add(
            source_index
        )

        used_target.add(
            target_index
        )


    # --------------------------------------------------------
    # Missing
    # --------------------------------------------------------

    missing = [

        source_values[index]

        for index in range(
            len(
                source_values
            )
        )

        if index not in used_source

    ]


    # --------------------------------------------------------
    # Additional
    # --------------------------------------------------------

    additional = [

        target_values[index]

        for index in range(
            len(
                target_values
            )
        )

        if index not in used_target

    ]


    # --------------------------------------------------------
    # Similarity
    # --------------------------------------------------------

    if matched:

        average_similarity = (

            sum(
                item.similarity
                for item in matched
            )

            /

            len(
                matched
            )

        )

    else:

        average_similarity = 0.0


    return CategoryComparison(

        category=category,

        source_count=len(
            source_values
        ),

        target_count=len(
            target_values
        ),

        matched_count=len(
            matched
        ),

        missing_count=len(
            missing
        ),

        additional_count=len(
            additional
        ),

        coverage_percentage=percentage(

            len(
                matched
            ),

            len(
                source_values
            ),

        ),

        similarity_percentage=round(

            average_similarity * 100,

            2,

        ),

        matched=matched,

        missing=missing,

        additional=additional,

    )


# ============================================================
# 75. BUILD MODULE COMPARISON
# ============================================================

def build_module_comparison(
    source_module: Any,
    target_module: Any,
    similarity: float,
    config: Optional[
        ComparatorConfig
    ] = None,
) -> ModuleComparison:
    """
    Build detailed comparison for a pair of modules.
    """

    config = (
        config
        or ComparatorConfig()
    )


    # --------------------------------------------------------
    # Topic comparison
    # --------------------------------------------------------

    topic_comparisons, topic_category = (
        compare_topics(

            get_module_topics(
                source_module
            ),

            get_module_topics(
                target_module
            ),

            config,

        )
    )


    # --------------------------------------------------------
    # Concepts
    # --------------------------------------------------------

    concepts = compare_category_values(

        category="concepts",

        source_values=get_module_concepts(
            source_module
        ),

        target_values=get_module_concepts(
            target_module
        ),

        config=config,

    )


    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    skills = compare_category_values(

        category="skills",

        source_values=get_module_skills(
            source_module
        ),

        target_values=get_module_skills(
            target_module
        ),

        config=config,

    )


    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    tools = compare_category_values(

        category="tools",

        source_values=get_module_tools(
            source_module
        ),

        target_values=get_module_tools(
            target_module
        ),

        config=config,

    )


    # --------------------------------------------------------
    # Technologies
    # --------------------------------------------------------

    technologies = compare_category_values(

        category="technologies",

        source_values=get_module_technologies(
            source_module
        ),

        target_values=get_module_technologies(
            target_module
        ),

        config=config,

    )


    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    source_projects = [

        object_name(
            project
        )

        for project
        in get_module_projects(
            source_module
        )

    ]


    target_projects = [

        object_name(
            project
        )

        for project
        in get_module_projects(
            target_module
        )

    ]


    projects = compare_category_values(

        category="projects",

        source_values=source_projects,

        target_values=target_projects,

        config=config,

    )


    # --------------------------------------------------------
    # Hours
    # --------------------------------------------------------

    source_hours = get_module_hours(
        source_module
    )

    target_hours = get_module_hours(
        target_module
    )


    hours_difference = round(

        target_hours
        -
        source_hours,

        2,

    )


    # --------------------------------------------------------
    # Enhancement reasons
    # --------------------------------------------------------

    enhancement_reasons = []


    if topic_category.missing_count:

        enhancement_reasons.append(

            (
                f"{topic_category.missing_count} "
                "topic(s) missing"
            )

        )


    if concepts.missing_count:

        enhancement_reasons.append(

            (
                f"{concepts.missing_count} "
                "concept(s) missing"
            )

        )


    if skills.missing_count:

        enhancement_reasons.append(

            (
                f"{skills.missing_count} "
                "skill(s) missing"
            )

        )


    if technologies.missing_count:

        enhancement_reasons.append(

            (
                f"{technologies.missing_count} "
                "technology/technologies missing"
            )

        )


    if projects.missing_count:

        enhancement_reasons.append(

            (
                f"{projects.missing_count} "
                "project(s) missing"
            )

        )


    if (
        source_hours > 0
        and target_hours > 0
        and target_hours < source_hours * 0.75
    ):

        enhancement_reasons.append(

            "Target curriculum allocates "
            "significantly fewer hours."

        )


    enhancement_needed = bool(
        enhancement_reasons
    )


    return ModuleComparison(

        source_module=object_name(
            source_module
        ),

        target_module=object_name(
            target_module
        ),

        similarity_percentage=round(
            similarity * 100,
            2,
        ),

        source_hours=source_hours,

        target_hours=target_hours,

        hours_difference=hours_difference,

        topics=topic_comparisons,

        matched_topics=[
            item.source_topic
            for item in topic_comparisons
        ],

        missing_topics=topic_category.missing,

        additional_topics=topic_category.additional,

        concepts=concepts,

        skills=skills,

        tools=tools,

        technologies=technologies,

        projects=projects,

        enhancement_needed=enhancement_needed,

        enhancement_reasons=enhancement_reasons,

    )


# ============================================================
# 76. MODULE COMPARISON DICT
# ============================================================

def module_comparison_to_dict(
    comparison: ModuleComparison,
) -> Dict[str, Any]:
    """
    Convert ModuleComparison into JSON-compatible data.
    """

    return {

        "source_module":
            comparison.source_module,

        "target_module":
            comparison.target_module,

        "similarity_percentage":
            comparison.similarity_percentage,

        "source_hours":
            comparison.source_hours,

        "target_hours":
            comparison.target_hours,

        "hours_difference":
            comparison.hours_difference,

        "matched_topics":
            list(
                comparison.matched_topics
            ),

        "missing_topics":
            list(
                comparison.missing_topics
            ),

        "additional_topics":
            list(
                comparison.additional_topics
            ),

        "topics":
            [
                topic_comparison_to_dict(
                    topic
                )

                for topic
                in comparison.topics
            ],

        "concepts":
            (
                category_result_to_dict(
                    comparison.concepts
                )

                if comparison.concepts

                else None
            ),

        "skills":
            (
                category_result_to_dict(
                    comparison.skills
                )

                if comparison.skills

                else None
            ),

        "tools":
            (
                category_result_to_dict(
                    comparison.tools
                )

                if comparison.tools

                else None
            ),

        "technologies":
            (
                category_result_to_dict(
                    comparison.technologies
                )

                if comparison.technologies

                else None
            ),

        "projects":
            (
                category_result_to_dict(
                    comparison.projects
                )

                if comparison.projects

                else None
            ),

        "enhancement_needed":
            comparison.enhancement_needed,

        "enhancement_reasons":
            list(
                comparison.enhancement_reasons
            ),

    }


# ============================================================
# 77. TOPIC COMPARISON DICT
# ============================================================

def topic_comparison_to_dict(
    comparison: TopicComparison,
) -> Dict[str, Any]:
    """
    Convert TopicComparison to dictionary.
    """

    return {

        "source_topic":
            comparison.source_topic,

        "target_topic":
            comparison.target_topic,

        "similarity_percentage":
            comparison.similarity_percentage,

        "source_hours":
            comparison.source_hours,

        "target_hours":
            comparison.target_hours,

        "hours_difference":
            comparison.hours_difference,

        "concepts":
            category_result_to_dict(
                comparison.concepts
            ),

        "skills":
            category_result_to_dict(
                comparison.skills
            ),

        "tools":
            category_result_to_dict(
                comparison.tools
            ),

        "technologies":
            category_result_to_dict(
                comparison.technologies
            ),

        "source_bloom_level":
            comparison.source_bloom_level,

        "target_bloom_level":
            comparison.target_bloom_level,

        "difficulty_change":
            comparison.difficulty_change,

        "enhancement_needed":
            comparison.enhancement_needed,

        "enhancement_reasons":
            list(
                comparison.enhancement_reasons
            ),

    }


# ============================================================
# 78. END OF CHUNK 3
# ============================================================
# ============================================================
# curriculum/comparator.py
# CHUNK 4/10
#
# CURRICULUM-WIDE COMPARISON ENGINE
#
# Curriculum A
#       │
#       ├── Modules
#       ├── Topics
#       ├── Concepts
#       ├── Skills
#       ├── Tools
#       ├── Technologies
#       └── Projects
#               │
#               ▼
#        GLOBAL COMPARISON
#               │
#       ┌───────┼────────┐
#       ▼       ▼        ▼
#   Coverage Similarity  Gaps
#       │       │        │
#       └───────┼────────┘
#               ▼
#      CurriculumComparison
# ============================================================


# ============================================================
# 79. CURRICULUM MODULE EXTRACTION
# ============================================================

def get_curriculum_modules(
    curriculum: Any,
) -> List[Any]:
    """
    Safely extract modules from a Curriculum.
    """

    if curriculum is None:
        return []

    modules = get_attr(
        curriculum,
        "modules",
        [],
    )

    if modules is None:
        return []

    if isinstance(
        modules,
        list,
    ):
        return modules

    try:

        return list(
            modules
        )

    except TypeError:

        return []


# ============================================================
# 80. CURRICULUM TOPICS
# ============================================================

def get_curriculum_topics(
    curriculum: Any,
) -> List[Any]:
    """
    Extract all topics from all modules.
    """

    topics = []

    for module in get_curriculum_modules(
        curriculum
    ):

        topics.extend(
            get_module_topics(
                module
            )
        )

    return topics


# ============================================================
# 81. CURRICULUM CONCEPTS
# ============================================================

def get_curriculum_concepts(
    curriculum: Any,
) -> List[str]:
    """
    Extract all concepts from the curriculum.

    Includes:
        - curriculum-level concepts
        - module concepts
        - topic concepts
    """

    values = []


    values.extend(
        get_attr(
            curriculum,
            "concepts",
            [],
        )
        or []
    )


    for module in get_curriculum_modules(
        curriculum
    ):

        values.extend(
            get_module_concepts(
                module
            )
        )


    return deduplicate(
        values
    )


# ============================================================
# 82. CURRICULUM SKILLS
# ============================================================

def get_curriculum_skills(
    curriculum: Any,
) -> List[str]:
    """
    Extract all skills from curriculum.
    """

    values = []


    values.extend(
        get_attr(
            curriculum,
            "skills",
            [],
        )
        or []
    )


    for module in get_curriculum_modules(
        curriculum
    ):

        values.extend(
            get_module_skills(
                module
            )
        )


    return deduplicate(
        values
    )


# ============================================================
# 83. CURRICULUM TOOLS
# ============================================================

def get_curriculum_tools(
    curriculum: Any,
) -> List[str]:
    """
    Extract all tools.
    """

    values = []


    values.extend(
        get_attr(
            curriculum,
            "tools",
            [],
        )
        or []
    )


    for module in get_curriculum_modules(
        curriculum
    ):

        values.extend(
            get_module_tools(
                module
            )
        )


    return deduplicate(
        values
    )


# ============================================================
# 84. CURRICULUM TECHNOLOGIES
# ============================================================

def get_curriculum_technologies(
    curriculum: Any,
) -> List[str]:
    """
    Extract all technologies.
    """

    values = []


    values.extend(
        get_attr(
            curriculum,
            "technologies",
            [],
        )
        or []
    )


    for module in get_curriculum_modules(
        curriculum
    ):

        values.extend(
            get_module_technologies(
                module
            )
        )


    return deduplicate(
        values
    )


# ============================================================
# 85. CURRICULUM PROJECTS
# ============================================================

def get_curriculum_projects(
    curriculum: Any,
) -> List[str]:
    """
    Extract project names from curriculum,
    modules and topics.
    """

    values = []


    # --------------------------------------------------------
    # Curriculum-level projects
    # --------------------------------------------------------

    for project in (
        get_attr(
            curriculum,
            "projects",
            [],
        )
        or []
    ):

        name = object_name(
            project
        )

        if name:
            values.append(
                name
            )


    # --------------------------------------------------------
    # Module projects
    # --------------------------------------------------------

    for module in get_curriculum_modules(
        curriculum
    ):

        for project in get_module_projects(
            module
        ):

            name = object_name(
                project
            )

            if name:
                values.append(
                    name
                )


        # ----------------------------------------------------
        # Topic projects
        # ----------------------------------------------------

        for topic in get_module_topics(
            module
        ):

            for project in (
                get_attr(
                    topic,
                    "projects",
                    [],
                )
                or []
            ):

                name = object_name(
                    project
                )

                if name:
                    values.append(
                        name
                    )


    return deduplicate(
        values
    )


# ============================================================
# 86. CURRICULUM OUTCOMES
# ============================================================

def get_curriculum_outcomes(
    curriculum: Any,
    outcome_type: str = "course",
) -> List[Any]:
    """
    Extract CO / PO / PSO objects.
    """

    field_map = {

        "course":
            "course_outcomes",

        "co":
            "course_outcomes",

        "program":
            "program_outcomes",

        "po":
            "program_outcomes",

        "program_specific":
            "program_specific_outcomes",

        "pso":
            "program_specific_outcomes",

    }


    field_name = field_map.get(
        normalize_text(
            outcome_type
        ),
        outcome_type,
    )


    outcomes = get_attr(
        curriculum,
        field_name,
        [],
    )


    if outcomes is None:
        return []


    if isinstance(
        outcomes,
        list,
    ):
        return outcomes


    try:

        return list(
            outcomes
        )

    except TypeError:

        return []


# ============================================================
# 87. CURRICULUM COMPARISON RESULT
# ============================================================

@dataclass
class CurriculumComparison:
    """
    Complete curriculum-vs-curriculum comparison result.
    """

    source_title: str

    target_title: str

    overall_similarity_percentage: float

    overall_coverage_percentage: float

    weighted_similarity_percentage: float

    module_comparison: Optional[
        CategoryComparison
    ] = None

    topic_comparison: Optional[
        CategoryComparison
    ] = None

    concept_comparison: Optional[
        CategoryComparison
    ] = None

    skill_comparison: Optional[
        CategoryComparison
    ] = None

    tool_comparison: Optional[
        CategoryComparison
    ] = None

    technology_comparison: Optional[
        CategoryComparison
    ] = None

    project_comparison: Optional[
        CategoryComparison
    ] = None

    course_outcome_comparison: Optional[
        CategoryComparison
    ] = None

    program_outcome_comparison: Optional[
        CategoryComparison
    ] = None

    pso_comparison: Optional[
        CategoryComparison
    ] = None

    modules: List[
        ModuleComparison
    ] = field(
        default_factory=list
    )

    missing_concepts: List[str] = field(
        default_factory=list
    )

    additional_concepts: List[str] = field(
        default_factory=list
    )

    missing_skills: List[str] = field(
        default_factory=list
    )

    additional_skills: List[str] = field(
        default_factory=list
    )

    missing_tools: List[str] = field(
        default_factory=list
    )

    additional_tools: List[str] = field(
        default_factory=list
    )

    missing_technologies: List[str] = field(
        default_factory=list
    )

    additional_technologies: List[str] = field(
        default_factory=list
    )

    missing_projects: List[str] = field(
        default_factory=list
    )

    additional_projects: List[str] = field(
        default_factory=list
    )

    strengths: List[str] = field(
        default_factory=list
    )

    gaps: List[str] = field(
        default_factory=list
    )

    recommendations: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# 88. GET CURRICULUM TITLE
# ============================================================

def get_curriculum_title(
    curriculum: Any,
) -> str:
    """
    Get curriculum title safely.
    """

    title = clean_text(
        get_attr(
            curriculum,
            "title",
            "",
        )
    )


    if title:
        return title


    metadata = get_attr(
        curriculum,
        "metadata",
        None,
    )


    for field_name in [
        "course_name",
        "subject_name",
        "name",
    ]:

        value = clean_text(
            get_attr(
                metadata,
                field_name,
                "",
            )
        )


        if value:
            return value


    return "Untitled Curriculum"


# ============================================================
# 89. COMPARE MODULES GLOBALLY
# ============================================================

def compare_curriculum_modules(
    source: Any,
    target: Any,
    config: Optional[
        ComparatorConfig
    ] = None,
) -> Tuple[
    CategoryComparison,
    List[
        ModuleComparison
    ],
]:
    """
    Perform full module-wise curriculum comparison.
    """

    config = (
        config
        or ComparatorConfig()
    )


    source_modules = get_curriculum_modules(
        source
    )

    target_modules = get_curriculum_modules(
        target
    )


    matched_pairs, unmatched_source, unmatched_target = (
        match_modules(

            source_modules,

            target_modules,

            config,

        )
    )


    detailed_modules = []


    matches = []


    # --------------------------------------------------------
    # Detailed matched modules
    # --------------------------------------------------------

    for (
        source_index,
        target_index,
        similarity,
    ) in matched_pairs:

        source_module = source_modules[
            source_index
        ]

        target_module = target_modules[
            target_index
        ]


        detailed = build_module_comparison(

            source_module,

            target_module,

            similarity,

            config,

        )


        detailed_modules.append(
            detailed
        )


        matches.append(

            MatchResult(

                source_name=object_name(
                    source_module
                ),

                target_name=object_name(
                    target_module
                ),

                similarity=similarity,

                match_type=(
                    determine_match_type(
                        source_module,
                        target_module,
                        similarity,
                    )
                ),

                confidence=match_confidence(
                    similarity
                ),

                source_index=source_index,

                target_index=target_index,

            )

        )


    # --------------------------------------------------------
    # Missing modules
    # --------------------------------------------------------

    missing_modules = [

        object_name(
            source_modules[index]
        )

        for index in unmatched_source

    ]


    # --------------------------------------------------------
    # Additional modules
    # --------------------------------------------------------

    additional_modules = [

        object_name(
            target_modules[index]
        )

        for index in unmatched_target

    ]


    # --------------------------------------------------------
    # Similarity
    # --------------------------------------------------------

    if matches:

        average_similarity = (

            sum(
                match.similarity
                for match in matches
            )

            /

            len(
                matches
            )

        )

    else:

        average_similarity = 0.0


    category = CategoryComparison(

        category="modules",

        source_count=len(
            source_modules
        ),

        target_count=len(
            target_modules
        ),

        matched_count=len(
            matched_pairs
        ),

        missing_count=len(
            unmatched_source
        ),

        additional_count=len(
            unmatched_target
        ),

        coverage_percentage=percentage(

            len(
                matched_pairs
            ),

            len(
                source_modules
            ),

        ),

        similarity_percentage=round(

            average_similarity * 100,

            2,

        ),

        matched=matches,

        missing=missing_modules,

        additional=additional_modules,

    )


    return (
        category,
        detailed_modules,
    )


# ============================================================
# 90. COMPARE GLOBAL STRING CATEGORY
# ============================================================

def compare_global_category(
    category: str,
    source_values: Sequence[str],
    target_values: Sequence[str],
    config: Optional[
        ComparatorConfig
    ] = None,
) -> CategoryComparison:
    """
    Generic global category comparison.
    """

    return compare_category_values(

        category=category,

        source_values=source_values,

        target_values=target_values,

        config=config,

    )


# ============================================================
# 91. CALCULATE WEIGHTED SIMILARITY
# ============================================================

def calculate_weighted_similarity(
    category_results: Dict[
        str,
        CategoryComparison
    ],
    weights: Optional[
        Dict[str, float]
    ] = None,
) -> float:
    """
    Calculate weighted overall similarity.

    Categories with missing data are automatically excluded
    from the denominator.

    This prevents a curriculum with no project information
    from being unfairly penalized.
    """

    weights = (
        weights
        or DEFAULT_WEIGHTS
    )


    weighted_sum = 0.0

    total_weight = 0.0


    for category, weight in weights.items():

        result = category_results.get(
            category
        )


        if result is None:
            continue


        weight = safe_float(
            weight
        )


        if weight <= 0:
            continue


        # No source items means the category is unavailable.
        if result.source_count == 0:
            continue


        weighted_sum += (

            result.similarity_percentage
            *
            weight

        )


        total_weight += weight


    if total_weight == 0:
        return 0.0


    return round(

        weighted_sum
        /
        total_weight,

        2,

    )


# ============================================================
# 92. CALCULATE OVERALL COVERAGE
# ============================================================

def calculate_overall_coverage(
    category_results: Dict[
        str,
        CategoryComparison
    ],
) -> float:
    """
    Calculate macro coverage based on source curriculum
    items.

    Categories are weighted according to their source
    item counts.
    """

    total_source = 0

    total_matched = 0


    for result in category_results.values():

        if result is None:
            continue


        total_source += (
            result.source_count
        )


        total_matched += (
            result.matched_count
        )


    return percentage(

        total_matched,

        total_source,

    )


# ============================================================
# 93. CALCULATE OVERALL SIMILARITY
# ============================================================

def calculate_overall_similarity(
    category_results: Dict[
        str,
        CategoryComparison
    ],
) -> float:
    """
    Calculate unweighted average similarity across
    available categories.
    """

    scores = []


    for result in category_results.values():

        if result is None:
            continue


        if result.source_count == 0:
            continue


        scores.append(
            result.similarity_percentage
        )


    if not scores:
        return 0.0


    return round(

        sum(scores)
        /
        len(scores),

        2,

    )


# ============================================================
# 94. BUILD GLOBAL CATEGORY RESULTS
# ============================================================

def build_global_category_results(
    source: Any,
    target: Any,
    config: Optional[
        ComparatorConfig
    ] = None,
) -> Dict[
    str,
    CategoryComparison
]:
    """
    Build all global category comparisons except modules.

    Categories:

        topics
        concepts
        skills
        tools
        technologies
        projects
        CO
        PO
        PSO
    """

    config = (
        config
        or ComparatorConfig()
    )


    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    source_topics = [
        object_name(
            topic
        )

        for topic
        in get_curriculum_topics(
            source
        )

    ]


    target_topics = [
        object_name(
            topic
        )

        for topic
        in get_curriculum_topics(
            target
        )

    ]


    topic_result = compare_global_category(

        "topics",

        source_topics,

        target_topics,

        config,

    )


    # --------------------------------------------------------
    # Concepts
    # --------------------------------------------------------

    concept_result = compare_global_category(

        "concepts",

        get_curriculum_concepts(
            source
        ),

        get_curriculum_concepts(
            target
        ),

        config,

    )


    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    skill_result = compare_global_category(

        "skills",

        get_curriculum_skills(
            source
        ),

        get_curriculum_skills(
            target
        ),

        config,

    )


    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    tool_result = compare_global_category(

        "tools",

        get_curriculum_tools(
            source
        ),

        get_curriculum_tools(
            target
        ),

        config,

    )


    # --------------------------------------------------------
    # Technologies
    # --------------------------------------------------------

    technology_result = compare_global_category(

        "technologies",

        get_curriculum_technologies(
            source
        ),

        get_curriculum_technologies(
            target
        ),

        config,

    )


    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    project_result = compare_global_category(

        "projects",

        get_curriculum_projects(
            source
        ),

        get_curriculum_projects(
            target
        ),

        config,

    )


    # --------------------------------------------------------
    # Course Outcomes
    # --------------------------------------------------------

    source_cos = [
        object_text(
            item
        )

        for item
        in get_curriculum_outcomes(
            source,
            "course",
        )

    ]


    target_cos = [
        object_text(
            item
        )

        for item
        in get_curriculum_outcomes(
            target,
            "course",
        )

    ]


    co_result = compare_global_category(

        "course_outcomes",

        source_cos,

        target_cos,

        config,

    )


    # --------------------------------------------------------
    # Program Outcomes
    # --------------------------------------------------------

    source_pos = [
        object_text(
            item
        )

        for item
        in get_curriculum_outcomes(
            source,
            "program",
        )

    ]


    target_pos = [
        object_text(
            item
        )

        for item
        in get_curriculum_outcomes(
            target,
            "program",
        )

    ]


    po_result = compare_global_category(

        "program_outcomes",

        source_pos,

        target_pos,

        config,

    )


    # --------------------------------------------------------
    # PSO
    # --------------------------------------------------------

    source_psos = [
        object_text(
            item
        )

        for item
        in get_curriculum_outcomes(
            source,
            "program_specific",
        )

    ]


    target_psos = [
        object_text(
            item
        )

        for item
        in get_curriculum_outcomes(
            target,
            "program_specific",
        )

    ]


    pso_result = compare_global_category(

        "program_specific_outcomes",

        source_psos,

        target_psos,

        config,

    )


    return {

        "topics":
            topic_result,

        "concepts":
            concept_result,

        "skills":
            skill_result,

        "tools":
            tool_result,

        "technologies":
            technology_result,

        "projects":
            project_result,

        "course_outcomes":
            co_result,

        "program_outcomes":
            po_result,

        "program_specific_outcomes":
            pso_result,

    }


# ============================================================
# 95. BUILD GLOBAL GAP LISTS
# ============================================================

def build_global_gap_lists(
    category_results: Dict[
        str,
        CategoryComparison
    ],
) -> Dict[
    str,
    List[str]
]:
    """
    Extract missing/additional items by category.
    """

    return {

        "missing_topics":
            list(
                category_results[
                    "topics"
                ].missing
            ),

        "additional_topics":
            list(
                category_results[
                    "topics"
                ].additional
            ),

        "missing_concepts":
            list(
                category_results[
                    "concepts"
                ].missing
            ),

        "additional_concepts":
            list(
                category_results[
                    "concepts"
                ].additional
            ),

        "missing_skills":
            list(
                category_results[
                    "skills"
                ].missing
            ),

        "additional_skills":
            list(
                category_results[
                    "skills"
                ].additional
            ),

        "missing_tools":
            list(
                category_results[
                    "tools"
                ].missing
            ),

        "additional_tools":
            list(
                category_results[
                    "tools"
                ].additional
            ),

        "missing_technologies":
            list(
                category_results[
                    "technologies"
                ].missing
            ),

        "additional_technologies":
            list(
                category_results[
                    "technologies"
                ].additional
            ),

        "missing_projects":
            list(
                category_results[
                    "projects"
                ].missing
            ),

        "additional_projects":
            list(
                category_results[
                    "projects"
                ].additional
            ),

    }


# ============================================================
# 96. BUILD STRENGTHS
# ============================================================

def build_comparison_strengths(
    category_results: Dict[
        str,
        CategoryComparison
    ],
) -> List[str]:
    """
    Identify strong areas in the comparison.
    """

    strengths = []


    for category, result in category_results.items():

        if result is None:
            continue


        score = (
            result.similarity_percentage
        )


        coverage = (
            result.coverage_percentage
        )


        if (
            score >= 85
            and coverage >= 80
        ):

            strengths.append(

                (
                    f"{format_category_name(category)} "
                    "shows strong alignment."
                )

            )


        elif (
            score >= 75
            and coverage >= 75
        ):

            strengths.append(

                (
                    f"{format_category_name(category)} "
                    "shows good alignment."
                )

            )


    return strengths


# ============================================================
# 97. BUILD COMPARISON GAPS
# ============================================================

def build_comparison_gaps(
    category_results: Dict[
        str,
        CategoryComparison
    ],
) -> List[str]:
    """
    Generate human-readable global gaps.
    """

    gaps = []


    for category, result in category_results.items():

        if result is None:
            continue


        if result.missing_count <= 0:
            continue


        category_name = (
            format_category_name(
                category
            )
        )


        missing_items = (
            result.missing[:5]
        )


        if missing_items:

            gaps.append(

                (
                    f"{category_name}: "
                    f"{result.missing_count} "
                    "item(s) missing. "
                    "Examples: "
                    +
                    ", ".join(
                        missing_items
                    )
                )

            )

        else:

            gaps.append(

                (
                    f"{category_name}: "
                    f"{result.missing_count} "
                    "item(s) missing."
                )

            )


    return gaps


# ============================================================
# 98. BUILD RECOMMENDATIONS
# ============================================================

def build_comparison_recommendations(
    category_results: Dict[
        str,
        CategoryComparison
    ],
) -> List[str]:
    """
    Generate basic rule-based recommendations.

    More advanced LLM/agent recommendations will be
    implemented in Gap & Enhancement modules.
    """

    recommendations = []


    # --------------------------------------------------------
    # Concepts
    # --------------------------------------------------------

    concepts = category_results.get(
        "concepts"
    )


    if concepts:

        if concepts.missing_count > 0:

            recommendations.append(

                (
                    "Review and add the missing concepts "
                    "identified in the curriculum comparison."
                )

            )


    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    skills = category_results.get(
        "skills"
    )


    if skills:

        if skills.missing_count > 0:

            recommendations.append(

                (
                    "Add missing industry-relevant skills "
                    "through modules, labs, assignments, "
                    "or projects."
                )

            )


    # --------------------------------------------------------
    # Technologies
    # --------------------------------------------------------

    technologies = category_results.get(
        "technologies"
    )


    if technologies:

        if technologies.missing_count > 0:

            recommendations.append(

                (
                    "Review missing technologies and "
                    "evaluate whether they should be "
                    "introduced into practical learning."
                )

            )


    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    projects = category_results.get(
        "projects"
    )


    if projects:

        if projects.missing_count > 0:

            recommendations.append(

                (
                    "Increase project-based learning to "
                    "cover practical competencies absent "
                    "from the curriculum."
                )

            )


    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    topics = category_results.get(
        "topics"
    )


    if topics:

        if topics.coverage_percentage < 70:

            recommendations.append(

                (
                    "The curriculum has significant topic "
                    "coverage gaps and should undergo "
                    "module-wise revision."
                )

            )


    return recommendations


# ============================================================
# 99. FORMAT CATEGORY NAME
# ============================================================

def format_category_name(
    category: str,
) -> str:
    """
    Convert internal category name to display name.
    """

    mapping = {

        "topics":
            "Topics",

        "concepts":
            "Concepts",

        "skills":
            "Skills",

        "tools":
            "Tools",

        "technologies":
            "Technologies",

        "projects":
            "Projects",

        "course_outcomes":
            "Course Outcomes",

        "program_outcomes":
            "Program Outcomes",

        "program_specific_outcomes":
            "Program Specific Outcomes",

        "modules":
            "Modules",

    }


    return mapping.get(
        category,
        category.replace(
            "_",
            " "
        ).title(),
    )


# ============================================================
# 100. BUILD CURRICULUM COMPARISON
# ============================================================

def compare_curriculums(
    source: Any,
    target: Any,
    config: Optional[
        ComparatorConfig
    ] = None,
) -> CurriculumComparison:
    """
    MAIN CURRICULUM COMPARISON API.

    Parameters
    ----------
    source:
        Reference / original curriculum.

    target:
        Curriculum being compared against the source.

    Returns
    -------
    CurriculumComparison

    Example
    -------

        result = compare_curriculums(
            curriculum_a,
            curriculum_b,
        )

        print(
            result.overall_similarity_percentage
        )

    """

    config = (
        config
        or ComparatorConfig()
    )


    logger.info(
        "Starting curriculum comparison."
    )


    # --------------------------------------------------------
    # Module comparison
    # --------------------------------------------------------

    module_result, detailed_modules = (
        compare_curriculum_modules(

            source,

            target,

            config,

        )
    )


    # --------------------------------------------------------
    # Global categories
    # --------------------------------------------------------

    category_results = (
        build_global_category_results(

            source,

            target,

            config,

        )
    )


    # --------------------------------------------------------
    # Add module result
    # --------------------------------------------------------

    category_results[
        "modules"
    ] = module_result


    # --------------------------------------------------------
    # Overall metrics
    # --------------------------------------------------------

    weighted_similarity = (
        calculate_weighted_similarity(

            category_results,

            config.weights,

        )
    )


    overall_similarity = (
        calculate_overall_similarity(

            category_results

        )
    )


    overall_coverage = (
        calculate_overall_coverage(

            category_results

        )
    )


    # --------------------------------------------------------
    # Gaps
    # --------------------------------------------------------

    gap_lists = (
        build_global_gap_lists(
            category_results
        )
    )


    strengths = (
        build_comparison_strengths(
            category_results
        )
    )


    gaps = (
        build_comparison_gaps(
            category_results
        )
    )


    recommendations = (
        build_comparison_recommendations(
            category_results
        )
    )


    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    result = CurriculumComparison(

        source_title=get_curriculum_title(
            source
        ),

        target_title=get_curriculum_title(
            target
        ),

        overall_similarity_percentage=(
            overall_similarity
        ),

        overall_coverage_percentage=(
            overall_coverage
        ),

        weighted_similarity_percentage=(
            weighted_similarity
        ),

        module_comparison=(
            category_results[
                "modules"
            ]
        ),

        topic_comparison=(
            category_results[
                "topics"
            ]
        ),

        concept_comparison=(
            category_results[
                "concepts"
            ]
        ),

        skill_comparison=(
            category_results[
                "skills"
            ]
        ),

        tool_comparison=(
            category_results[
                "tools"
            ]
        ),

        technology_comparison=(
            category_results[
                "technologies"
            ]
        ),

        project_comparison=(
            category_results[
                "projects"
            ]
        ),

        course_outcome_comparison=(
            category_results[
                "course_outcomes"
            ]
        ),

        program_outcome_comparison=(
            category_results[
                "program_outcomes"
            ]
        ),

        pso_comparison=(
            category_results[
                "program_specific_outcomes"
            ]
        ),

        modules=detailed_modules,

        missing_concepts=(
            gap_lists[
                "missing_concepts"
            ]
        ),

        additional_concepts=(
            gap_lists[
                "additional_concepts"
            ]
        ),

        missing_skills=(
            gap_lists[
                "missing_skills"
            ]
        ),

        additional_skills=(
            gap_lists[
                "additional_skills"
            ]
        ),

        missing_tools=(
            gap_lists[
                "missing_tools"
            ]
        ),

        additional_tools=(
            gap_lists[
                "additional_tools"
            ]
        ),

        missing_technologies=(
            gap_lists[
                "missing_technologies"
            ]
        ),

        additional_technologies=(
            gap_lists[
                "additional_technologies"
            ]
        ),

        missing_projects=(
            gap_lists[
                "missing_projects"
            ]
        ),

        additional_projects=(
            gap_lists[
                "additional_projects"
            ]
        ),

        strengths=strengths,

        gaps=gaps,

        recommendations=recommendations,

        metadata={

            "comparator_version":
                COMPARATOR_VERSION,

            "match_threshold":
                config.match_threshold,

            "source_modules":
                len(
                    get_curriculum_modules(
                        source
                    )
                ),

            "target_modules":
                len(
                    get_curriculum_modules(
                        target
                    )
                ),

        },

    )


    logger.info(
        (
            "Curriculum comparison completed. "
            f"Weighted similarity: "
            f"{weighted_similarity}%"
        )
    )


    return result


# ============================================================
# 101. END OF CHUNK 4
# ============================================================
# ============================================================
# curriculum/comparator.py
# CHUNK 5/10
#
# ADVANCED CONCEPT INTELLIGENCE
#
# Exact Concept
#       │
#       ▼
# Canonical Concept
#       │
#       ├── Related Concepts
#       ├── Concept Family
#       ├── Prerequisites
#       ├── Advanced Concepts
#       └── Emerging Concepts
#              │
#              ▼
#       Concept Intelligence
# ============================================================


# ============================================================
# 102. CONCEPT INTELLIGENCE RESULT
# ============================================================

@dataclass
class ConceptIntelligence:
    """
    Detailed semantic analysis of one concept.
    """

    concept: str

    canonical_concept: str

    category: str = "general"

    matched_concepts: List[str] = field(
        default_factory=list
    )

    related_concepts: List[str] = field(
        default_factory=list
    )

    prerequisite_concepts: List[str] = field(
        default_factory=list
    )

    advanced_concepts: List[str] = field(
        default_factory=list
    )

    emerging_concepts: List[str] = field(
        default_factory=list
    )

    synonyms: List[str] = field(
        default_factory=list
    )

    source_present: bool = False

    target_present: bool = False

    similarity_percentage: float = 0.0

    relevance_score: float = 0.0

    confidence: float = 0.0

    explanation: Optional[str] = None


# ============================================================
# 103. CONCEPT RELATION
# ============================================================

@dataclass
class ConceptRelation:
    """
    Represents a relationship between two concepts.
    """

    source_concept: str

    target_concept: str

    relation_type: str

    similarity_percentage: float

    confidence: float

    explanation: str = ""


# ============================================================
# 104. CONCEPT FAMILY
# ============================================================

@dataclass
class ConceptFamily:
    """
    Groups concepts belonging to the same conceptual domain.
    """

    family_name: str

    concepts: List[str] = field(
        default_factory=list
    )

    source_count: int = 0

    target_count: int = 0

    common_count: int = 0

    missing_count: int = 0

    coverage_percentage: float = 0.0


# ============================================================
# 105. CONCEPT TAXONOMY
# ============================================================

CONCEPT_TAXONOMY = {

    "artificial_intelligence": {

        "label":
            "Artificial Intelligence",

        "keywords": [

            "artificial intelligence",

            "ai",

            "intelligent systems",

            "expert systems",

            "knowledge representation",

            "reasoning",

            "search algorithms",

        ],

    },


    "machine_learning": {

        "label":
            "Machine Learning",

        "keywords": [

            "machine learning",

            "supervised learning",

            "unsupervised learning",

            "semi supervised learning",

            "reinforcement learning",

            "classification",

            "regression",

            "clustering",

            "feature engineering",

            "model evaluation",

        ],

    },


    "deep_learning": {

        "label":
            "Deep Learning",

        "keywords": [

            "deep learning",

            "neural networks",

            "cnn",

            "convolutional neural network",

            "rnn",

            "recurrent neural network",

            "lstm",

            "gru",

            "transformer",

            "attention",

            "self attention",

        ],

    },


    "generative_ai": {

        "label":
            "Generative AI",

        "keywords": [

            "generative ai",

            "genai",

            "large language model",

            "llm",

            "foundation model",

            "prompt engineering",

            "rag",

            "retrieval augmented generation",

            "fine tuning",

            "peft",

            "lora",

            "rlhf",

            "ai agents",

            "agentic ai",

        ],

    },


    "natural_language_processing": {

        "label":
            "Natural Language Processing",

        "keywords": [

            "natural language processing",

            "nlp",

            "tokenization",

            "text classification",

            "sentiment analysis",

            "named entity recognition",

            "ner",

            "language model",

            "word embeddings",

            "sentence embeddings",

            "bert",

            "transformers",

        ],

    },


    "computer_vision": {

        "label":
            "Computer Vision",

        "keywords": [

            "computer vision",

            "image classification",

            "object detection",

            "image segmentation",

            "ocr",

            "cnn",

            "yolo",

            "resnet",

            "vision transformer",

            "vit",

        ],

    },


    "data_engineering": {

        "label":
            "Data Engineering",

        "keywords": [

            "data engineering",

            "etl",

            "elt",

            "data pipeline",

            "data warehouse",

            "data lake",

            "spark",

            "kafka",

            "airflow",

            "data ingestion",

        ],

    },


    "cloud_computing": {

        "label":
            "Cloud Computing",

        "keywords": [

            "cloud computing",

            "aws",

            "amazon web services",

            "azure",

            "microsoft azure",

            "gcp",

            "google cloud platform",

            "serverless",

            "containers",

            "kubernetes",

        ],

    },


    "devops": {

        "label":
            "DevOps",

        "keywords": [

            "devops",

            "docker",

            "kubernetes",

            "ci cd",

            "continuous integration",

            "continuous deployment",

            "terraform",

            "ansible",

            "jenkins",

            "github actions",

        ],

    },


    "mlops": {

        "label":
            "MLOps",

        "keywords": [

            "mlops",

            "model deployment",

            "model monitoring",

            "model registry",

            "mlflow",

            "kubeflow",

            "feature store",

            "model serving",

        ],

    },


    "cybersecurity": {

        "label":
            "Cybersecurity",

        "keywords": [

            "cybersecurity",

            "network security",

            "application security",

            "identity management",

            "cryptography",

            "penetration testing",

            "zero trust",

            "security operations",

        ],

    },


    "database": {

        "label":
            "Database Technologies",

        "keywords": [

            "database",

            "sql",

            "mysql",

            "postgresql",

            "mongodb",

            "nosql",

            "database management",

            "query optimization",

        ],

    },


    "software_engineering": {

        "label":
            "Software Engineering",

        "keywords": [

            "software engineering",

            "object oriented programming",

            "oop",

            "design patterns",

            "software architecture",

            "api",

            "testing",

            "version control",

            "git",

        ],

    },

}


# ============================================================
# 106. CONCEPT FAMILY LOOKUP
# ============================================================

def concept_family(
    concept: Any,
) -> str:
    """
    Identify the most likely concept family.

    Returns taxonomy key.
    """

    normalized = normalize_text(
        concept
    )


    if not normalized:
        return "general"


    best_family = "general"

    best_score = 0.0


    for family_name, family_data in (
        CONCEPT_TAXONOMY.items()
    ):

        keywords = family_data.get(
            "keywords",
            [],
        )


        for keyword in keywords:

            score = canonical_similarity(

                normalized,

                keyword,

            )


            if score > best_score:

                best_score = score

                best_family = family_name


    if best_score < 0.55:

        return "general"


    return best_family


# ============================================================
# 107. CONCEPT FAMILY LABEL
# ============================================================

def concept_family_label(
    family_name: str,
) -> str:
    """
    Convert taxonomy key to display name.
    """

    if family_name in CONCEPT_TAXONOMY:

        return CONCEPT_TAXONOMY[
            family_name
        ].get(
            "label",
            family_name,
        )


    return (
        family_name
        .replace(
            "_",
            " ",
        )
        .title()
    )


# ============================================================
# 108. CLASSIFY CONCEPTS
# ============================================================

def classify_concepts(
    concepts: Sequence[str],
) -> Dict[
    str,
    List[str]
]:
    """
    Group concepts into taxonomy families.
    """

    result: Dict[
        str,
        List[str]
    ] = {}


    for concept in deduplicate(
        concepts
    ):

        family = concept_family(
            concept
        )


        result.setdefault(
            family,
            [],
        )


        result[
            family
        ].append(
            concept
        )


    return result


# ============================================================
# 109. BUILD CONCEPT FAMILIES
# ============================================================

def build_concept_families(
    source_concepts: Sequence[str],
    target_concepts: Sequence[str],
    config: Optional[
        ComparatorConfig
    ] = None,
) -> List[ConceptFamily]:
    """
    Compare concepts by conceptual family.

    Example:

        Source:
            CNN
            RNN
            Transformer

        Target:
            CNN
            Vision Transformer

    Both may belong to the Deep Learning family.
    """

    source_groups = classify_concepts(
        source_concepts
    )

    target_groups = classify_concepts(
        target_concepts
    )


    families = []


    all_families = sorted(

        set(
            source_groups.keys()
        )

        |

        set(
            target_groups.keys()
        )

    )


    for family in all_families:

        source_values = source_groups.get(
            family,
            [],
        )

        target_values = target_groups.get(
            family,
            [],
        )


        common = exact_intersection(

            source_values,

            target_values,

        )


        missing = normalized_difference(

            source_values,

            target_values,

        )


        coverage = percentage(

            len(
                source_values
            )
            -
            len(
                missing
            ),

            len(
                source_values
            ),

        )


        family_object = ConceptFamily(

            family_name=concept_family_label(
                family
            ),

            concepts=deduplicate(

                [
                    *source_values,
                    *target_values,
                ]

            ),

            source_count=len(
                source_values
            ),

            target_count=len(
                target_values
            ),

            common_count=len(
                common
            ),

            missing_count=len(
                missing
            ),

            coverage_percentage=coverage,

        )


        families.append(
            family_object
        )


    return families


# ============================================================
# 110. CONCEPT RELATION KEYWORDS
# ============================================================

CONCEPT_RELATIONS = {

    "machine learning": {

        "prerequisites": [

            "python",

            "statistics",

            "probability",

            "linear algebra",

            "data preprocessing",

        ],

        "related": [

            "supervised learning",

            "unsupervised learning",

            "feature engineering",

            "model evaluation",

            "classification",

            "regression",

        ],

        "advanced": [

            "ensemble learning",

            "gradient boosting",

            "reinforcement learning",

            "meta learning",

            "federated learning",

        ],

    },


    "deep learning": {

        "prerequisites": [

            "machine learning",

            "linear algebra",

            "calculus",

            "probability",

            "python",

        ],

        "related": [

            "neural networks",

            "cnn",

            "rnn",

            "lstm",

            "transformers",

            "attention",

        ],

        "advanced": [

            "vision transformers",

            "diffusion models",

            "multimodal models",

            "neural architecture search",

        ],

    },


    "generative ai": {

        "prerequisites": [

            "machine learning",

            "deep learning",

            "natural language processing",

            "transformers",

        ],

        "related": [

            "large language models",

            "prompt engineering",

            "rag",

            "embeddings",

            "vector databases",

            "ai agents",

        ],

        "advanced": [

            "agentic ai",

            "multimodal ai",

            "model fine tuning",

            "parameter efficient fine tuning",

            "reinforcement learning from human feedback",

            "synthetic data generation",

        ],

    },


    "large language model": {

        "prerequisites": [

            "deep learning",

            "natural language processing",

            "transformers",

        ],

        "related": [

            "prompt engineering",

            "tokenization",

            "embeddings",

            "attention",

            "rag",

        ],

        "advanced": [

            "fine tuning",

            "peft",

            "lora",

            "rlhf",

            "reasoning models",

            "mixture of experts",

        ],

    },


    "retrieval augmented generation": {

        "prerequisites": [

            "large language models",

            "embeddings",

            "vector databases",

            "information retrieval",

        ],

        "related": [

            "semantic search",

            "document retrieval",

            "chunking",

            "reranking",

            "vector search",

        ],

        "advanced": [

            "agentic rag",

            "graph rag",

            "multimodal rag",

            "self correcting rag",

            "hybrid search",

        ],

    },


    "natural language processing": {

        "prerequisites": [

            "machine learning",

            "statistics",

            "linguistics",

        ],

        "related": [

            "tokenization",

            "embeddings",

            "text classification",

            "named entity recognition",

            "sentiment analysis",

        ],

        "advanced": [

            "large language models",

            "transformers",

            "multilingual models",

            "instruction tuning",

        ],

    },


    "computer vision": {

        "prerequisites": [

            "linear algebra",

            "image processing",

            "machine learning",

        ],

        "related": [

            "image classification",

            "object detection",

            "image segmentation",

            "ocr",

        ],

        "advanced": [

            "vision transformers",

            "multimodal models",

            "3d computer vision",

            "generative vision",

        ],

    },

}


# ============================================================
# 111. GET_CONCEPT_RELATIONS
# ============================================================

def get_concept_relations(
    concept: Any,
) -> Dict[
    str,
    List[str]
]:
    """
    Get known relationships for a concept.
    """

    canonical = canonical_term(
        concept
    )


    # --------------------------------------------------------
    # Direct relation
    # --------------------------------------------------------

    if canonical in CONCEPT_RELATIONS:

        return CONCEPT_RELATIONS[
            canonical
        ]


    # --------------------------------------------------------
    # Family relation
    # --------------------------------------------------------

    family = concept_family(
        canonical
    )


    family_map = {

        "machine_learning":
            "machine learning",

        "deep_learning":
            "deep learning",

        "generative_ai":
            "generative ai",

        "natural_language_processing":
            "natural language processing",

        "computer_vision":
            "computer vision",

    }


    relation_key = family_map.get(
        family
    )


    if relation_key in CONCEPT_RELATIONS:

        return CONCEPT_RELATIONS[
            relation_key
        ]


    return {

        "prerequisites": [],

        "related": [],

        "advanced": [],

    }


# ============================================================
# 112. CONCEPT SYNONYMS
# ============================================================

CONCEPT_SYNONYMS = {

    "machine learning": [

        "ml",

        "machine learning",

        "statistical learning",

    ],

    "deep learning": [

        "dl",

        "deep learning",

        "deep neural networks",

    ],

    "generative ai": [

        "genai",

        "generative ai",

        "generative artificial intelligence",

    ],

    "large language model": [

        "llm",

        "large language model",

        "large language models",

    ],

    "retrieval augmented generation": [

        "rag",

        "retrieval augmented generation",

        "retrieval-augmented generation",

    ],

    "natural language processing": [

        "nlp",

        "natural language processing",

    ],

    "computer vision": [

        "cv",

        "computer vision",

    ],

    "parameter efficient fine tuning": [

        "peft",

        "parameter efficient fine tuning",

    ],

}


# ============================================================
# 113. GET SYNONYMS
# ============================================================

def get_concept_synonyms(
    concept: Any,
) -> List[str]:
    """
    Return known synonyms.
    """

    canonical = canonical_term(
        concept
    )


    if canonical in CONCEPT_SYNONYMS:

        return list(
            CONCEPT_SYNONYMS[
                canonical
            ]
        )


    return [
        clean_text(
            concept
        )
    ]


# ============================================================
# 114. DETECT RELATED CONCEPTS
# ============================================================

def detect_related_concepts(
    concept: Any,
    candidate_concepts: Sequence[str],
    threshold: float = 0.60,
) -> List[
    Tuple[
        str,
        float,
    ]
]:
    """
    Detect semantically related concepts from a candidate list.

    Returns:
        [(concept, similarity), ...]
    """

    result = []


    concept_text_value = clean_text(
        concept
    )


    if not concept_text_value:
        return result


    for candidate in deduplicate(
        candidate_concepts
    ):

        if canonical_match(
            concept_text_value,
            candidate,
        ):
            continue


        score = canonical_similarity(

            concept_text_value,

            candidate,

        )


        if score >= threshold:

            result.append(

                (
                    candidate,
                    score,
                )

            )


    result.sort(
        key=lambda item:
            item[1],
        reverse=True,
    )


    return result


# ============================================================
# 115. CONCEPT INTELLIGENCE ANALYSIS
# ============================================================

def analyze_concept(
    concept: str,
    source_concepts: Sequence[str],
    target_concepts: Sequence[str],
    all_known_concepts: Optional[
        Sequence[str]
    ] = None,
    config: Optional[
        ComparatorConfig
    ] = None,
) -> ConceptIntelligence:
    """
    Analyze one concept across two curricula.
    """

    config = (
        config
        or ComparatorConfig()
    )


    concept = clean_text(
        concept
    )


    canonical = canonical_term(
        concept
    )


    source_canonical = {

        canonical_term(
            item
        )

        for item
        in source_concepts

        if canonical_term(
            item
        )

    }


    target_canonical = {

        canonical_term(
            item
        )

        for item
        in target_concepts

        if canonical_term(
            item
        )

    }


    # --------------------------------------------------------
    # Presence
    # --------------------------------------------------------

    source_present = (
        canonical
        in source_canonical
    )


    target_present = (
        canonical
        in target_canonical
    )


    # --------------------------------------------------------
    # Related candidates
    # --------------------------------------------------------

    candidates = (

        list(
            all_known_concepts
            or []
        )

        +

        list(
            source_concepts
        )

        +

        list(
            target_concepts
        )

    )


    candidates = deduplicate(
        candidates
    )


    related = detect_related_concepts(

        concept,

        candidates,

        threshold=0.60,

    )


    related_concepts = [

        item[0]

        for item in related[:10]

    ]


    # --------------------------------------------------------
    # Known conceptual relationships
    # --------------------------------------------------------

    relations = get_concept_relations(
        concept
    )


    prerequisites = deduplicate(

        relations.get(
            "prerequisites",
            [],
        )

    )


    advanced = deduplicate(

        relations.get(
            "advanced",
            [],
        )

    )


    # --------------------------------------------------------
    # Synonyms
    # --------------------------------------------------------

    synonyms = get_concept_synonyms(
        concept
    )


    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    family = concept_family(
        concept
    )


    # --------------------------------------------------------
    # Best source-target match
    # --------------------------------------------------------

    best_target = 0.0


    for target_concept in target_concepts:

        best_target = max(

            best_target,

            canonical_similarity(

                concept,

                target_concept,

            ),

        )


    # --------------------------------------------------------
    # Emerging concepts
    # --------------------------------------------------------

    emerging = []


    # If the concept is in target but not source,
    # it may represent curriculum evolution.

    if (
        target_present
        and not source_present
    ):

        emerging.append(
            concept
        )


    # Add advanced concepts that occur in target.
    for advanced_concept in advanced:

        if canonical_term(
            advanced_concept
        ) in target_canonical:

            emerging.append(
                advanced_concept
            )


    # --------------------------------------------------------
    # Relevance
    # --------------------------------------------------------

    relevance = best_target


    if source_present:

        relevance = max(
            relevance,
            1.0,
        )


    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = match_confidence(
        best_target
    )


    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    if (
        source_present
        and target_present
    ):

        explanation = (
            "Concept is present in both curricula."
        )

    elif source_present:

        explanation = (
            "Concept exists in the source curriculum "
            "but was not sufficiently matched in the "
            "target curriculum."
        )

    elif target_present:

        explanation = (
            "Concept appears in the target curriculum "
            "but not in the source curriculum."
        )

    else:

        explanation = (
            "Concept was analyzed as a related or "
            "potentially relevant concept."
        )


    return ConceptIntelligence(

        concept=concept,

        canonical_concept=canonical,

        category=concept_family_label(
            family
        ),

        matched_concepts=(
            [
                concept
            ]

            if (
                source_present
                and target_present
            )

            else []
        ),

        related_concepts=related_concepts,

        prerequisite_concepts=prerequisites,

        advanced_concepts=advanced,

        emerging_concepts=deduplicate(
            emerging
        ),

        synonyms=synonyms,

        source_present=source_present,

        target_present=target_present,

        similarity_percentage=round(

            best_target * 100,

            2,

        ),

        relevance_score=round(

            relevance * 100,

            2,

        ),

        confidence=round(

            confidence * 100,

            2,

        ),

        explanation=explanation,

    )


# ============================================================
# 116. ANALYZE CURRICULUM CONCEPTS
# ============================================================

def analyze_curriculum_concepts(
    source: Any,
    target: Any,
    config: Optional[
        ComparatorConfig
    ] = None,
) -> List[
    ConceptIntelligence
]:
    """
    Perform concept intelligence across two curricula.
    """

    config = (
        config
        or ComparatorConfig()
    )


    source_concepts = (
        get_curriculum_concepts(
            source
        )
    )


    target_concepts = (
        get_curriculum_concepts(
            target
        )
    )


    all_concepts = deduplicate(

        [
            *source_concepts,
            *target_concepts,
        ]

    )


    results = []


    # Analyze concepts from source.
    for concept in source_concepts:

        results.append(

            analyze_concept(

                concept,

                source_concepts,

                target_concepts,

                all_concepts,

                config,

            )

        )


    # Add target-only concepts.
    source_keys = {

        canonical_term(
            concept
        )

        for concept
        in source_concepts

    }


    for concept in target_concepts:

        if (
            canonical_term(
                concept
            )
            in source_keys
        ):

            continue


        results.append(

            analyze_concept(

                concept,

                source_concepts,

                target_concepts,

                all_concepts,

                config,

            )

        )


    return results


# ============================================================
# 117. CONCEPT RELATION GRAPH
# ============================================================

def build_concept_relation_graph(
    concepts: Sequence[str],
    threshold: float = 0.72,
) -> List[
    ConceptRelation
]:
    """
    Build a lightweight concept relationship graph.

    Each relation represents a sufficiently similar pair.

    This is useful for later visualization with:
        - NetworkX
        - Plotly
        - Streamlit
    """

    values = deduplicate(
        concepts
    )


    relations = []


    for index, source in enumerate(
        values
    ):

        for target in values[
            index + 1:
        ]:

            score = canonical_similarity(

                source,

                target,

            )


            if score < threshold:
                continue


            if canonical_match(
                source,
                target,
            ):

                relation_type = (
                    "equivalent"
                )

            else:

                relation_type = (
                    "related"
                )


            relations.append(

                ConceptRelation(

                    source_concept=source,

                    target_concept=target,

                    relation_type=relation_type,

                    similarity_percentage=round(

                        score * 100,

                        2,

                    ),

                    confidence=round(

                        match_confidence(
                            score
                        )
                        * 100,

                        2,

                    ),

                    explanation=(

                        "Concepts share strong "
                        "semantic similarity."

                    ),

                )

            )


    relations.sort(

        key=lambda item:
            item.similarity_percentage,

        reverse=True,

    )


    return relations


# ============================================================
# 118. CONCEPT INTELLIGENCE TO DICT
# ============================================================

def concept_intelligence_to_dict(
    item: ConceptIntelligence,
) -> Dict[str, Any]:
    """
    Serialize ConceptIntelligence.
    """

    return {

        "concept":
            item.concept,

        "canonical_concept":
            item.canonical_concept,

        "category":
            item.category,

        "matched_concepts":
            list(
                item.matched_concepts
            ),

        "related_concepts":
            list(
                item.related_concepts
            ),

        "prerequisite_concepts":
            list(
                item.prerequisite_concepts
            ),

        "advanced_concepts":
            list(
                item.advanced_concepts
            ),

        "emerging_concepts":
            list(
                item.emerging_concepts
            ),

        "synonyms":
            list(
                item.synonyms
            ),

        "source_present":
            item.source_present,

        "target_present":
            item.target_present,

        "similarity_percentage":
            item.similarity_percentage,

        "relevance_score":
            item.relevance_score,

        "confidence":
            item.confidence,

        "explanation":
            item.explanation,

    }


# ============================================================
# 119. CONCEPT FAMILY TO DICT
# ============================================================

def concept_family_to_dict(
    item: ConceptFamily,
) -> Dict[str, Any]:
    """
    Serialize ConceptFamily.
    """

    return {

        "family_name":
            item.family_name,

        "concepts":
            list(
                item.concepts
            ),

        "source_count":
            item.source_count,

        "target_count":
            item.target_count,

        "common_count":
            item.common_count,

        "missing_count":
            item.missing_count,

        "coverage_percentage":
            item.coverage_percentage,

    }


# ============================================================
# 120. CONCEPT RELATION TO DICT
# ============================================================

def concept_relation_to_dict(
    item: ConceptRelation,
) -> Dict[str, Any]:
    """
    Serialize ConceptRelation.
    """

    return {

        "source_concept":
            item.source_concept,

        "target_concept":
            item.target_concept,

        "relation_type":
            item.relation_type,

        "similarity_percentage":
            item.similarity_percentage,

        "confidence":
            item.confidence,

        "explanation":
            item.explanation,

    }


# ============================================================
# 121. END OF CHUNK 5
# ============================================================
# ============================================================
# curriculum/comparator.py
# CHUNK 6/10
#
# ADVANCED SEMANTIC / EMBEDDING COMPARISON
#
# Local Text Similarity
#        │
#        ├── TF-IDF / lexical similarity
#        │
#        └── Sentence Embeddings
#                 │
#                 ▼
#          Cosine Similarity
#                 │
#                 ▼
#        Semantic Match Engine
#
# Optional dependency:
#     sentence-transformers
#
# The comparator MUST continue working without it.
# ============================================================


# ============================================================
# 122. OPTIONAL SENTENCE TRANSFORMER IMPORT
# ============================================================

try:

    from sentence_transformers import (
        SentenceTransformer,
    )

    SENTENCE_TRANSFORMERS_AVAILABLE = True

except Exception:

    SentenceTransformer = None

    SENTENCE_TRANSFORMERS_AVAILABLE = False


# ============================================================
# 123. OPTIONAL NUMPY IMPORT
# ============================================================

try:

    import numpy as np

    NUMPY_AVAILABLE = True

except Exception:

    np = None

    NUMPY_AVAILABLE = False


# ============================================================
# 124. SEMANTIC MODEL CACHE
# ============================================================

_SEMANTIC_MODEL_CACHE = {}


# ============================================================
# 125. DEFAULT EMBEDDING MODEL
# ============================================================

DEFAULT_EMBEDDING_MODEL = (
    "all-MiniLM-L6-v2"
)


# ============================================================
# 126. SEMANTIC CONFIGURATION
# ============================================================

@dataclass
class SemanticConfig:
    """
    Configuration for embedding-based comparison.
    """

    enabled: bool = True

    model_name: str = (
        DEFAULT_EMBEDDING_MODEL
    )

    batch_size: int = 32

    normalize_embeddings: bool = True

    semantic_weight: float = 0.65

    lexical_weight: float = 0.35

    semantic_threshold: float = 0.70

    cache_model: bool = True


# ============================================================
# 127. SEMANTIC MODEL STATUS
# ============================================================

def semantic_model_available() -> bool:
    """
    Return True when sentence-transformers and numpy
    are available.
    """

    return bool(

        SENTENCE_TRANSFORMERS_AVAILABLE

        and

        NUMPY_AVAILABLE

    )


# ============================================================
# 128. GET SEMANTIC MODEL
# ============================================================

def get_semantic_model(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    cache_model: bool = True,
):
    """
    Load SentenceTransformer model lazily.

    The model is NOT loaded during module import.

    This is important for Streamlit applications because
    importing comparator.py should remain lightweight.
    """

    if not semantic_model_available():

        logger.warning(

            "SentenceTransformer unavailable. "
            "Falling back to lexical similarity."

        )

        return None


    if (
        cache_model
        and model_name
        in _SEMANTIC_MODEL_CACHE
    ):

        return _SEMANTIC_MODEL_CACHE[
            model_name
        ]


    try:

        model = SentenceTransformer(
            model_name
        )


        if cache_model:

            _SEMANTIC_MODEL_CACHE[
                model_name
            ] = model


        logger.info(

            "Loaded semantic model: "
            f"{model_name}"

        )


        return model


    except Exception as exc:

        logger.warning(

            "Unable to load semantic model "
            f"'{model_name}': {exc}"

        )

        return None


# ============================================================
# 129. CLEAR SEMANTIC MODEL CACHE
# ============================================================

def clear_semantic_model_cache() -> None:
    """
    Clear cached embedding models.
    """

    _SEMANTIC_MODEL_CACHE.clear()


# ============================================================
# 130. ENCODE TEXT
# ============================================================

def encode_text(
    texts: Union[
        str,
        Sequence[str],
    ],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = 32,
    normalize_embeddings: bool = True,
):
    """
    Encode one or more texts into sentence embeddings.

    Returns:
        numpy.ndarray

    Returns None if semantic dependencies are unavailable.
    """

    if not semantic_model_available():

        return None


    model = get_semantic_model(
        model_name=model_name,
        cache_model=True,
    )


    if model is None:

        return None


    if isinstance(
        texts,
        str,
    ):

        values = [
            texts
        ]

    else:

        values = [
            clean_text(
                value
            )
            for value in texts
        ]


    values = [
        value
        for value in values
        if value
    ]


    if not values:

        return None


    try:

        embeddings = model.encode(

            values,

            batch_size=batch_size,

            normalize_embeddings=(
                normalize_embeddings
            ),

            show_progress_bar=False,

        )


        return np.asarray(
            embeddings
        )


    except Exception as exc:

        logger.warning(

            "Embedding generation failed: "
            f"{exc}"

        )

        return None


# ============================================================
# 131. COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    vector_a: Any,
    vector_b: Any,
) -> float:
    """
    Calculate cosine similarity between two vectors.

    If vectors are already normalized, dot product is enough,
    but this implementation remains safe for unnormalized
    vectors.
    """

    if (
        vector_a is None
        or vector_b is None
    ):

        return 0.0


    if not NUMPY_AVAILABLE:

        return 0.0


    try:

        a = np.asarray(
            vector_a,
            dtype=float,
        )

        b = np.asarray(
            vector_b,
            dtype=float,
        )


        denominator = (

            np.linalg.norm(a)
            *
            np.linalg.norm(b)

        )


        if denominator == 0:

            return 0.0


        score = (

            np.dot(
                a,
                b,
            )
            /
            denominator

        )


        # Numerical protection.
        score = max(
            -1.0,
            min(
                1.0,
                float(
                    score
                ),
            ),
        )


        # Convert [-1, 1] to [0, 1].
        return round(

            (
                score
                + 1.0
            )
            / 2.0,

            6,

        )


    except Exception:

        return 0.0


# ============================================================
# 132. RAW COSINE SIMILARITY
# ============================================================

def raw_cosine_similarity(
    vector_a: Any,
    vector_b: Any,
) -> float:
    """
    Return standard cosine similarity in [-1, 1].
    """

    if (
        vector_a is None
        or vector_b is None
    ):

        return 0.0


    if not NUMPY_AVAILABLE:

        return 0.0


    try:

        a = np.asarray(
            vector_a,
            dtype=float,
        )

        b = np.asarray(
            vector_b,
            dtype=float,
        )


        denominator = (

            np.linalg.norm(a)
            *
            np.linalg.norm(b)

        )


        if denominator == 0:

            return 0.0


        return float(

            np.dot(
                a,
                b,
            )
            /
            denominator

        )


    except Exception:

        return 0.0


# ============================================================
# 133. SEMANTIC TEXT SIMILARITY
# ============================================================

def semantic_text_similarity(
    text_a: Any,
    text_b: Any,
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> float:
    """
    Calculate embedding-based semantic similarity.

    Returns:
        0.0 - 1.0

    Falls back to hybrid_similarity() when embeddings
    are unavailable.
    """

    semantic_config = (
        semantic_config
        or SemanticConfig()
    )


    text_a = clean_text(
        text_a
    )

    text_b = clean_text(
        text_b
    )


    if not text_a or not text_b:

        return 0.0


    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    if canonical_match(
        text_a,
        text_b,
    ):

        return 1.0


    # --------------------------------------------------------
    # Disabled semantic mode
    # --------------------------------------------------------

    if not semantic_config.enabled:

        return hybrid_similarity(

            text_a,

            text_b,

        )


    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    embeddings = encode_text(

        [
            text_a,
            text_b,
        ],

        model_name=(
            semantic_config.model_name
        ),

        batch_size=(
            semantic_config.batch_size
        ),

        normalize_embeddings=(
            semantic_config.normalize_embeddings
        ),

    )


    if embeddings is None:

        return hybrid_similarity(

            text_a,

            text_b,

        )


    if len(
        embeddings
    ) < 2:

        return hybrid_similarity(

            text_a,

            text_b,

        )


    # SentenceTransformer embeddings are usually
    # normalized, but cosine_similarity remains safe.
    score = cosine_similarity(

        embeddings[0],

        embeddings[1],

    )


    return round(
        score,
        4,
    )


# ============================================================
# 134. HYBRID SEMANTIC SIMILARITY
# ============================================================

def hybrid_semantic_similarity(
    text_a: Any,
    text_b: Any,
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> float:
    """
    Combine lexical and embedding similarity.

    Formula:

        semantic_score * semantic_weight
        +
        lexical_score * lexical_weight
    """

    semantic_config = (
        semantic_config
        or SemanticConfig()
    )


    lexical_score = hybrid_similarity(

        text_a,

        text_b,

    )


    semantic_score = semantic_text_similarity(

        text_a,

        text_b,

        semantic_config,

    )


    total_weight = (

        semantic_config.semantic_weight

        +

        semantic_config.lexical_weight

    )


    if total_weight <= 0:

        return lexical_score


    score = (

        semantic_score
        *
        semantic_config.semantic_weight

        +

        lexical_score
        *
        semantic_config.lexical_weight

    ) / total_weight


    return round(

        max(
            0.0,
            min(
                1.0,
                score,
            ),
        ),

        4,

    )


# ============================================================
# 135. SEMANTIC BATCH SIMILARITY
# ============================================================

def semantic_batch_similarity(
    source_texts: Sequence[str],
    target_texts: Sequence[str],
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> List[List[float]]:
    """
    Calculate all-pairs semantic similarity.

    Returns:

        [
            [score, score, score],
            [score, score, score],
            ...
        ]

    Uses one embedding operation for efficiency.
    """

    semantic_config = (
        semantic_config
        or SemanticConfig()
    )


    source_texts = [

        clean_text(
            value
        )

        for value
        in source_texts

    ]


    target_texts = [

        clean_text(
            value
        )

        for value
        in target_texts

    ]


    source_texts = [
        value
        for value in source_texts
        if value
    ]


    target_texts = [
        value
        for value in target_texts
        if value
    ]


    if (
        not source_texts
        or not target_texts
    ):

        return []


    # --------------------------------------------------------
    # Try embedding approach
    # --------------------------------------------------------

    if semantic_config.enabled:

        all_texts = [

            *source_texts,

            *target_texts,

        ]


        embeddings = encode_text(

            all_texts,

            model_name=(
                semantic_config.model_name
            ),

            batch_size=(
                semantic_config.batch_size
            ),

            normalize_embeddings=(
                semantic_config.normalize_embeddings
            ),

        )


        if embeddings is not None:

            source_count = len(
                source_texts
            )

            target_count = len(
                target_texts
            )


            source_embeddings = (
                embeddings[
                    :source_count
                ]
            )


            target_embeddings = (
                embeddings[
                    source_count:
                    source_count
                    +
                    target_count
                ]
            )


            matrix = []


            for source_vector in (
                source_embeddings
            ):

                row = []


                for target_vector in (
                    target_embeddings
                ):

                    semantic_score = (
                        cosine_similarity(

                            source_vector,

                            target_vector,

                        )
                    )


                    lexical_score = (
                        hybrid_similarity(

                            source_texts[
                                len(row)
                            ]
                            if False
                            else source_texts[
                                len(matrix)
                            ],

                            target_texts[
                                len(row)
                            ],

                        )
                    )


                    score = (

                        semantic_score
                        *
                        semantic_config.semantic_weight

                        +

                        lexical_score
                        *
                        semantic_config.lexical_weight

                    ) / (

                        semantic_config.semantic_weight
                        +
                        semantic_config.lexical_weight

                    )


                    row.append(
                        round(
                            score,
                            4,
                        )
                    )


                matrix.append(
                    row
                )


            return matrix


    # --------------------------------------------------------
    # Fallback lexical matrix
    # --------------------------------------------------------

    matrix = []


    for source in source_texts:

        row = []


        for target in target_texts:

            row.append(

                hybrid_similarity(

                    source,

                    target,

                )

            )


        matrix.append(
            row
        )


    return matrix


# ============================================================
# 136. SEMANTIC BEST MATCH
# ============================================================

def semantic_best_match(
    source_text: str,
    target_texts: Sequence[str],
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> Optional[
    Tuple[
        str,
        float,
        int,
    ]
]:
    """
    Find the best semantic target.

    Returns:

        (
            target_text,
            similarity,
            target_index
        )

    """

    target_texts = list(
        target_texts
        or []
    )


    if not target_texts:

        return None


    matrix = semantic_batch_similarity(

        [
            source_text
        ],

        target_texts,

        semantic_config,

    )


    if not matrix:

        return None


    scores = matrix[0]


    if not scores:

        return None


    best_index = max(

        range(
            len(
                scores
            )
        ),

        key=lambda index:
            scores[index],

    )


    return (

        target_texts[
            best_index
        ],

        scores[
            best_index
        ],

        best_index,

    )


# ============================================================
# 137. SEMANTIC MATCH RESULT
# ============================================================

@dataclass
class SemanticMatchResult:
    """
    Result of an embedding-based semantic match.
    """

    source: str

    target: Optional[str]

    similarity_percentage: float

    confidence_percentage: float

    matched: bool

    target_index: Optional[int] = None

    explanation: str = ""


# ============================================================
# 138. BUILD SEMANTIC MATCH
# ============================================================

def build_semantic_match(
    source: str,
    target_candidates: Sequence[str],
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> SemanticMatchResult:
    """
    Match one source item against target candidates.
    """

    semantic_config = (
        semantic_config
        or SemanticConfig()
    )


    best = semantic_best_match(

        source,

        target_candidates,

        semantic_config,

    )


    if best is None:

        return SemanticMatchResult(

            source=source,

            target=None,

            similarity_percentage=0.0,

            confidence_percentage=0.0,

            matched=False,

            target_index=None,

            explanation=(
                "No candidate target item was available."
            ),

        )


    target, score, target_index = best


    matched = (

        score
        >=
        semantic_config.semantic_threshold

    )


    confidence = match_confidence(
        score
    )


    if matched:

        explanation = (

            "The target item is semantically "
            "similar to the source item."

        )

    else:

        explanation = (

            "No target item exceeded the configured "
            "semantic similarity threshold."

        )


    return SemanticMatchResult(

        source=source,

        target=target,

        similarity_percentage=round(

            score * 100,

            2,

        ),

        confidence_percentage=round(

            confidence * 100,

            2,

        ),

        matched=matched,

        target_index=target_index,

        explanation=explanation,

    )


# ============================================================
# 139. SEMANTIC MATCH MANY
# ============================================================

def semantic_match_many(
    source_items: Sequence[str],
    target_items: Sequence[str],
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> List[
    SemanticMatchResult
]:
    """
    Perform one-to-one semantic matching for lists.
    """

    semantic_config = (
        semantic_config
        or SemanticConfig()
    )


    source_items = list(
        source_items
        or []
    )

    target_items = list(
        target_items
        or []
    )


    if not source_items:

        return []


    if not target_items:

        return [

            SemanticMatchResult(

                source=source,

                target=None,

                similarity_percentage=0.0,

                confidence_percentage=0.0,

                matched=False,

                target_index=None,

                explanation=(
                    "Target list is empty."
                ),

            )

            for source
            in source_items

        ]


    matrix = semantic_batch_similarity(

        source_items,

        target_items,

        semantic_config,

    )


    candidates = []


    for source_index, row in enumerate(
        matrix
    ):

        for target_index, score in enumerate(
            row
        ):

            candidates.append(

                (
                    score,
                    source_index,
                    target_index,
                )

            )


    candidates.sort(

        key=lambda item:
            item[0],

        reverse=True,

    )


    used_source = set()

    used_target = set()

    assignments = {}


    # --------------------------------------------------------
    # Greedy one-to-one assignment
    # --------------------------------------------------------

    for (
        score,
        source_index,
        target_index,
    ) in candidates:

        if source_index in used_source:
            continue


        if target_index in used_target:
            continue


        if (
            score
            <
            semantic_config.semantic_threshold
        ):

            continue


        assignments[
            source_index
        ] = (

            target_index,

            score,

        )


        used_source.add(
            source_index
        )

        used_target.add(
            target_index
        )


    results = []


    for source_index, source in enumerate(
        source_items
    ):

        assignment = assignments.get(
            source_index
        )


        if assignment is None:

            # Find best candidate even if below threshold.
            best_index = max(

                range(
                    len(
                        matrix[
                            source_index
                        ]
                    )
                ),

                key=lambda index:
                    matrix[
                        source_index
                    ][
                        index
                    ],

            )


            best_score = matrix[
                source_index
            ][
                best_index
            ]


            results.append(

                SemanticMatchResult(

                    source=source,

                    target=target_items[
                        best_index
                    ],

                    similarity_percentage=round(

                        best_score * 100,

                        2,

                    ),

                    confidence_percentage=round(

                        match_confidence(
                            best_score
                        )
                        * 100,

                        2,

                    ),

                    matched=False,

                    target_index=best_index,

                    explanation=(

                        "Best semantic candidate did not "
                        "reach the configured threshold."

                    ),

                )

            )


            continue


        target_index, score = assignment


        results.append(

            SemanticMatchResult(

                source=source,

                target=target_items[
                    target_index
                ],

                similarity_percentage=round(

                    score * 100,

                    2,

                ),

                confidence_percentage=round(

                    match_confidence(
                        score
                    )
                    * 100,

                    2,

                ),

                matched=True,

                target_index=target_index,

                explanation=(

                    "Successfully matched using "
                    "semantic similarity."

                ),

            )

        )


    return results


# ============================================================
# 140. SEMANTIC GAP DETECTION
# ============================================================

def semantic_gap_detection(
    source_items: Sequence[str],
    target_items: Sequence[str],
    threshold: float = 0.70,
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> Dict[str, Any]:
    """
    Detect semantic gaps between two lists.

    Returns:

        matched
        missing
        additional
        weak_matches
    """

    semantic_config = (
        semantic_config
        or SemanticConfig(
            semantic_threshold=threshold
        )
    )


    results = semantic_match_many(

        source_items,

        target_items,

        semantic_config,

    )


    matched = []

    missing = []

    weak_matches = []


    used_target = set()


    for result in results:

        if result.target_index is not None:

            used_target.add(
                result.target_index
            )


        if result.matched:

            matched.append(
                result
            )

        elif (
            result.similarity_percentage
            >=
            threshold * 100 * 0.80
        ):

            weak_matches.append(
                result
            )

        else:

            missing.append(
                result
            )


    additional = [

        target_items[index]

        for index in range(
            len(
                target_items
            )
        )

        if index not in used_target

    ]


    return {

        "matched":
            matched,

        "missing":
            missing,

        "additional":
            additional,

        "weak_matches":
            weak_matches,

        "source_count":
            len(
                source_items
            ),

        "target_count":
            len(
                target_items
            ),

        "matched_count":
            len(
                matched
            ),

        "missing_count":
            len(
                missing
            ),

        "additional_count":
            len(
                additional
            ),

    }


# ============================================================
# 141. SEMANTIC MODULE MATCHING
# ============================================================

def semantic_match_modules(
    source_modules: Sequence[Any],
    target_modules: Sequence[Any],
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> List[
    SemanticMatchResult
]:
    """
    Semantic matching specifically for curriculum modules.

    Rich module text is constructed from:

        name
        description
        topics
        concepts
        skills
        technologies
    """

    source_texts = [

        module_comparison_text(
            module
        )

        for module
        in source_modules

    ]


    target_texts = [

        module_comparison_text(
            module
        )

        for module
        in target_modules

    ]


    return semantic_match_many(

        source_texts,

        target_texts,

        semantic_config,

    )


# ============================================================
# 142. MODULE COMPARISON TEXT
# ============================================================

def module_comparison_text(
    module: Any,
) -> str:
    """
    Build rich semantic text for a module.
    """

    parts = []


    name = object_name(
        module
    )


    description = object_description(
        module
    )


    if name:

        parts.append(
            name
        )


    if description:

        parts.append(
            description
        )


    topics = get_module_topics(
        module
    )


    topic_names = [

        object_name(
            topic
        )

        for topic
        in topics

    ]


    if topic_names:

        parts.append(

            "Topics: "
            +
            ", ".join(
                topic_names
            )

        )


    concepts = get_module_concepts(
        module
    )


    if concepts:

        parts.append(

            "Concepts: "
            +
            ", ".join(
                concepts
            )

        )


    skills = get_module_skills(
        module
    )


    if skills:

        parts.append(

            "Skills: "
            +
            ", ".join(
                skills
            )

        )


    technologies = (
        get_module_technologies(
            module
        )
    )


    if technologies:

        parts.append(

            "Technologies: "
            +
            ", ".join(
                technologies
            )

        )


    return ". ".join(
        parts
    )


# ============================================================
# 143. SEMANTIC TOPIC MATCHING
# ============================================================

def semantic_match_topics(
    source_topics: Sequence[Any],
    target_topics: Sequence[Any],
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> List[
    SemanticMatchResult
]:
    """
    Semantic matching for curriculum topics.
    """

    source_texts = [

        topic_text(
            topic
        )

        for topic
        in source_topics

    ]


    target_texts = [

        topic_text(
            topic
        )

        for topic
        in target_topics

    ]


    return semantic_match_many(

        source_texts,

        target_texts,

        semantic_config,

    )


# ============================================================
# 144. SEMANTIC CONCEPT MATCHING
# ============================================================

def semantic_match_concepts(
    source_concepts: Sequence[str],
    target_concepts: Sequence[str],
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> List[
    SemanticMatchResult
]:
    """
    Semantic concept matching.
    """

    return semantic_match_many(

        source_concepts,

        target_concepts,

        semantic_config,

    )


# ============================================================
# 145. SEMANTIC SKILL MATCHING
# ============================================================

def semantic_match_skills(
    source_skills: Sequence[str],
    target_skills: Sequence[str],
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> List[
    SemanticMatchResult
]:
    """
    Semantic skill matching.
    """

    return semantic_match_many(

        source_skills,

        target_skills,

        semantic_config,

    )


# ============================================================
# 146. SEMANTIC TECHNOLOGY MATCHING
# ============================================================

def semantic_match_technologies(
    source_technologies: Sequence[str],
    target_technologies: Sequence[str],
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> List[
    SemanticMatchResult
]:
    """
    Semantic technology matching.
    """

    return semantic_match_many(

        source_technologies,

        target_technologies,

        semantic_config,

    )


# ============================================================
# 147. SEMANTIC RESULT TO DICT
# ============================================================

def semantic_match_to_dict(
    result: SemanticMatchResult,
) -> Dict[str, Any]:
    """
    Serialize SemanticMatchResult.
    """

    return {

        "source":
            result.source,

        "target":
            result.target,

        "similarity_percentage":
            result.similarity_percentage,

        "confidence_percentage":
            result.confidence_percentage,

        "matched":
            result.matched,

        "target_index":
            result.target_index,

        "explanation":
            result.explanation,

    }


# ============================================================
# 148. SEMANTIC GAP RESULT TO DICT
# ============================================================

def semantic_gap_to_dict(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Serialize semantic gap detection result.
    """

    return {

        "matched": [

            semantic_match_to_dict(
                item
            )

            for item
            in result.get(
                "matched",
                [],
            )

        ],

        "missing": [

            semantic_match_to_dict(
                item
            )

            for item
            in result.get(
                "missing",
                [],
            )

        ],

        "weak_matches": [

            semantic_match_to_dict(
                item
            )

            for item
            in result.get(
                "weak_matches",
                [],
            )

        ],

        "additional":
            list(
                result.get(
                    "additional",
                    [],
                )
            ),

        "source_count":
            result.get(
                "source_count",
                0,
            ),

        "target_count":
            result.get(
                "target_count",
                0,
            ),

        "matched_count":
            result.get(
                "matched_count",
                0,
            ),

        "missing_count":
            result.get(
                "missing_count",
                0,
            ),

        "additional_count":
            result.get(
                "additional_count",
                0,
            ),

    }


# ============================================================
# 149. EMBEDDING MODEL INFORMATION
# ============================================================

def semantic_model_info(
    semantic_config: Optional[
        SemanticConfig
    ] = None,
) -> Dict[str, Any]:
    """
    Return semantic engine status.
    """

    semantic_config = (
        semantic_config
        or SemanticConfig()
    )


    model_loaded = (

        semantic_config.model_name
        in _SEMANTIC_MODEL_CACHE

    )


    return {

        "enabled":
            semantic_config.enabled,

        "available":
            semantic_model_available(),

        "sentence_transformers_available":
            SENTENCE_TRANSFORMERS_AVAILABLE,

        "numpy_available":
            NUMPY_AVAILABLE,

        "model_name":
            semantic_config.model_name,

        "model_loaded":
            model_loaded,

        "semantic_weight":
            semantic_config.semantic_weight,

        "lexical_weight":
            semantic_config.lexical_weight,

        "semantic_threshold":
            semantic_config.semantic_threshold,

    }


# ============================================================
# 150. CLEAR SEMANTIC CACHE
# ============================================================

def reset_semantic_engine() -> None:
    """
    Reset all cached semantic models.
    """

    clear_semantic_model_cache()


# ============================================================
# 151. END OF CHUNK 6
# ============================================================
# ============================================================
# curriculum/comparator.py
# CHUNK 7/10
#
# INDUSTRY ALIGNMENT + CURRICULUM MATURITY SCORING
#
# Curriculum Comparison
#          │
#          ├── Content Coverage
#          ├── Skill Coverage
#          ├── Technology Coverage
#          ├── Project Depth
#          ├── Practical Learning
#          ├── Industry Relevance
#          └── Emerging Technology
#                    │
#                    ▼
#             READINESS SCORE
# ============================================================


# ============================================================
# 152. INDUSTRY SCORING CONFIGURATION
# ============================================================

@dataclass
class IndustryScoringConfig:
    """
    Configuration for curriculum maturity and
    industry-readiness scoring.
    """

    content_weight: float = 0.20

    topic_weight: float = 0.15

    skill_weight: float = 0.20

    technology_weight: float = 0.15

    project_weight: float = 0.15

    tool_weight: float = 0.05

    emerging_technology_weight: float = 0.10

    minimum_project_count: int = 2

    minimum_skill_count: int = 5

    minimum_technology_count: int = 5

    minimum_tool_count: int = 3


# ============================================================
# 153. CURRICULUM MATURITY SCORE
# ============================================================

@dataclass
class CurriculumMaturityScore:
    """
    Overall maturity assessment.
    """

    overall_score: float = 0.0

    content_score: float = 0.0

    topic_score: float = 0.0

    skill_score: float = 0.0

    technology_score: float = 0.0

    project_score: float = 0.0

    tool_score: float = 0.0

    emerging_technology_score: float = 0.0

    practical_score: float = 0.0

    employability_score: float = 0.0

    industry_alignment_score: float = 0.0

    maturity_level: str = "Basic"

    strengths: List[str] = field(
        default_factory=list
    )

    weaknesses: List[str] = field(
        default_factory=list
    )

    recommendations: List[str] = field(
        default_factory=list
    )


# ============================================================
# 154. SCORE NORMALIZATION
# ============================================================

def normalize_score(
    score: Any,
) -> float:
    """
    Normalize score to 0-100.
    """

    value = safe_float(
        score
    )


    if value <= 1.0:

        value *= 100.0


    return round(

        max(
            0.0,
            min(
                100.0,
                value,
            ),
        ),

        2,

    )


# ============================================================
# 155. CATEGORY SCORE
# ============================================================

def category_score(
    result: Optional[
        CategoryComparison
    ],
) -> float:
    """
    Extract a usable category score.

    Uses a combination of coverage and similarity.

    Formula:

        60% coverage
        40% similarity
    """

    if result is None:
        return 0.0


    coverage = safe_float(
        result.coverage_percentage
    )


    similarity = safe_float(
        result.similarity_percentage
    )


    score = (

        coverage * 0.60

        +

        similarity * 0.40

    )


    return round(
        score,
        2,
    )


# ============================================================
# 156. COVERAGE SCORE
# ============================================================

def coverage_score(
    result: Optional[
        CategoryComparison
    ],
) -> float:
    """
    Return category coverage as 0-100.
    """

    if result is None:
        return 0.0


    return normalize_score(

        result.coverage_percentage

    )


# ============================================================
# 157. SIMILARITY SCORE
# ============================================================

def similarity_score(
    result: Optional[
        CategoryComparison
    ],
) -> float:
    """
    Return similarity as 0-100.
    """

    if result is None:
        return 0.0


    return normalize_score(

        result.similarity_percentage

    )


# ============================================================
# 158. MODULE DEPTH SCORE
# ============================================================

def module_depth_score(
    modules: Sequence[
        ModuleComparison
    ],
) -> float:
    """
    Calculate module depth from module-level comparison.
    """

    if not modules:
        return 0.0


    scores = []


    for module in modules:

        score = safe_float(

            module.similarity_percentage

        )


        topic_count = len(
            module.topics
        )


        topic_bonus = min(

            10.0,

            topic_count * 1.5,

        )


        final_score = min(

            100.0,

            score
            +
            topic_bonus,

        )


        scores.append(
            final_score
        )


    return round(

        sum(scores)
        /
        len(scores),

        2,

    )


# ============================================================
# 159. PROJECT DEPTH SCORE
# ============================================================

def project_depth_score(
    curriculum: Any,
    minimum_projects: int = 2,
) -> float:
    """
    Estimate project depth.

    Project quantity is only one signal. The function also
    looks for descriptions, tools and technologies where
    available.
    """

    projects = get_curriculum_projects(
        curriculum
    )


    count = len(
        projects
    )


    if count == 0:
        return 0.0


    quantity_score = min(

        70.0,

        (
            count
            /
            max(
                minimum_projects,
                1,
            )
        )
        *
        70.0,

    )


    # --------------------------------------------------------
    # Look for project metadata
    # --------------------------------------------------------

    detailed_count = 0


    for module in get_curriculum_modules(
        curriculum
    ):

        for project in get_module_projects(
            module
        ):

            description = object_description(
                project
            )

            technologies = normalize_list(

                get_attr(
                    project,
                    "technologies",
                    [],
                )

            )

            tools = normalize_list(

                get_attr(
                    project,
                    "tools",
                    [],
                )

            )


            if (
                description
                or technologies
                or tools
            ):

                detailed_count += 1


    quality_ratio = safe_divide(

        detailed_count,

        count,

        0.0,

    )


    quality_score = (
        quality_ratio * 30.0
    )


    return round(

        min(

            100.0,

            quantity_score
            +
            quality_score,

        ),

        2,

    )


# ============================================================
# 160. SKILL DEPTH SCORE
# ============================================================

def skill_depth_score(
    curriculum: Any,
    minimum_skills: int = 5,
) -> float:
    """
    Calculate curriculum skill depth.
    """

    skills = get_curriculum_skills(
        curriculum
    )


    count = len(
        skills
    )


    if count == 0:
        return 0.0


    score = min(

        100.0,

        (
            count
            /
            max(
                minimum_skills,
                1,
            )
        )
        *
        100.0,

    )


    return round(
        score,
        2,
    )


# ============================================================
# 161. TECHNOLOGY BREADTH SCORE
# ============================================================

def technology_breadth_score(
    curriculum: Any,
    minimum_technologies: int = 5,
) -> float:
    """
    Calculate technology breadth.
    """

    technologies = (
        get_curriculum_technologies(
            curriculum
        )
    )


    count = len(
        technologies
    )


    if count == 0:
        return 0.0


    score = min(

        100.0,

        (
            count
            /
            max(
                minimum_technologies,
                1,
            )
        )
        *
        100.0,

    )


    return round(
        score,
        2,
    )


# ============================================================
# 162. TOOL BREADTH SCORE
# ============================================================

def tool_breadth_score(
    curriculum: Any,
    minimum_tools: int = 3,
) -> float:
    """
    Calculate practical tool exposure.
    """

    tools = get_curriculum_tools(
        curriculum
    )


    count = len(
        tools
    )


    if count == 0:
        return 0.0


    score = min(

        100.0,

        (
            count
            /
            max(
                minimum_tools,
                1,
            )
        )
        *
        100.0,

    )


    return round(
        score,
        2,
    )


# ============================================================
# 163. PRACTICAL LEARNING SCORE
# ============================================================

def practical_learning_score(
    curriculum: Any,
) -> float:
    """
    Estimate practical-learning maturity.

    Signals:

        Projects
        Tools
        Technologies
        Skills
        Hands-on / lab keywords
    """

    projects = get_curriculum_projects(
        curriculum
    )

    tools = get_curriculum_tools(
        curriculum
    )

    technologies = (
        get_curriculum_technologies(
            curriculum
        )
    )

    skills = get_curriculum_skills(
        curriculum
    )


    project_score = min(

        100.0,

        len(projects) * 12.5,

    )


    tool_score = min(

        100.0,

        len(tools) * 8.0,

    )


    technology_score = min(

        100.0,

        len(technologies) * 6.0,

    )


    skill_score = min(

        100.0,

        len(skills) * 6.0,

    )


    # --------------------------------------------------------
    # Search curriculum text for practical signals
    # --------------------------------------------------------

    text = curriculum_comparison_text(
        curriculum
    )


    practical_keywords = [

        "hands on",

        "lab",

        "laboratory",

        "assignment",

        "project",

        "case study",

        "implementation",

        "deployment",

        "practical",

        "workshop",

        "hackathon",

        "capstone",

        "internship",

    ]


    keyword_hits = 0


    for keyword in practical_keywords:

        if keyword in normalize_text(
            text
        ):

            keyword_hits += 1


    keyword_score = min(

        100.0,

        keyword_hits
        /
        len(
            practical_keywords
        )
        *
        100.0,

    )


    score = (

        project_score * 0.30

        +

        tool_score * 0.15

        +

        technology_score * 0.15

        +

        skill_score * 0.15

        +

        keyword_score * 0.25

    )


    return round(
        min(
            100.0,
            score,
        ),
        2,
    )


# ============================================================
# 164. CURRICULUM COMPARISON TEXT
# ============================================================

def curriculum_comparison_text(
    curriculum: Any,
) -> str:
    """
    Build rich text representation of an entire curriculum.
    """

    parts = []


    title = get_curriculum_title(
        curriculum
    )


    if title:

        parts.append(
            title
        )


    description = object_description(
        curriculum
    )


    if description:

        parts.append(
            description
        )


    modules = get_curriculum_modules(
        curriculum
    )


    for module in modules:

        parts.append(

            module_comparison_text(
                module
            )

        )


    concepts = get_curriculum_concepts(
        curriculum
    )


    if concepts:

        parts.append(

            "Concepts: "
            +
            ", ".join(
                concepts
            )

        )


    skills = get_curriculum_skills(
        curriculum
    )


    if skills:

        parts.append(

            "Skills: "
            +
            ", ".join(
                skills
            )

        )


    tools = get_curriculum_tools(
        curriculum
    )


    if tools:

        parts.append(

            "Tools: "
            +
            ", ".join(
                tools
            )

        )


    technologies = (
        get_curriculum_technologies(
            curriculum
        )
    )


    if technologies:

        parts.append(

            "Technologies: "
            +
            ", ".join(
                technologies
            )

        )


    projects = get_curriculum_projects(
        curriculum
    )


    if projects:

        parts.append(

            "Projects: "
            +
            ", ".join(
                projects
            )

        )


    return ". ".join(
        parts
    )


# ============================================================
# 165. EMPLOYABILITY SCORE
# ============================================================

def employability_score(
    curriculum: Any,
) -> float:
    """
    Estimate employability orientation.

    This is a heuristic score, not a labor-market prediction.

    Signals include:

        skills
        technologies
        projects
        deployment
        APIs
        Git
        cloud
        testing
        communication
        interview
        internship
    """

    text = normalize_text(

        curriculum_comparison_text(
            curriculum
        )

    )


    skill_score = min(

        100.0,

        len(
            get_curriculum_skills(
                curriculum
            )
        )
        * 8.0,

    )


    technology_score = min(

        100.0,

        len(
            get_curriculum_technologies(
                curriculum
            )
        )
        * 6.0,

    )


    project_score = min(

        100.0,

        len(
            get_curriculum_projects(
                curriculum
            )
        )
        * 12.5,

    )


    employability_keywords = [

        "deployment",

        "api",

        "git",

        "github",

        "cloud",

        "aws",

        "azure",

        "gcp",

        "testing",

        "debugging",

        "software engineering",

        "interview",

        "resume",

        "internship",

        "industry",

        "capstone",

        "hackathon",

    ]


    hits = sum(

        1

        for keyword
        in employability_keywords

        if keyword in text

    )


    keyword_score = min(

        100.0,

        hits
        /
        len(
            employability_keywords
        )
        *
        100.0,

    )


    score = (

        skill_score * 0.25

        +

        technology_score * 0.20

        +

        project_score * 0.30

        +

        keyword_score * 0.25

    )


    return round(
        min(
            100.0,
            score,
        ),
        2,
    )


# ============================================================
# 166. INDUSTRY TECHNOLOGY KEYWORDS
# ============================================================

INDUSTRY_TECHNOLOGY_KEYWORDS = {

    "python",

    "java",

    "javascript",

    "typescript",

    "sql",

    "git",

    "github",

    "docker",

    "kubernetes",

    "aws",

    "azure",

    "gcp",

    "tensorflow",

    "pytorch",

    "scikit learn",

    "hugging face",

    "langchain",

    "langgraph",

    "llamaindex",

    "streamlit",

    "fastapi",

    "flask",

    "django",

    "spark",

    "kafka",

    "airflow",

    "mlflow",

    "kubeflow",

    "terraform",

    "jenkins",

}


# ============================================================
# 167. INDUSTRY TECHNOLOGY SCORE
# ============================================================

def industry_technology_score(
    curriculum: Any,
) -> float:
    """
    Estimate exposure to commonly used engineering /
    AI / data technologies.

    This is intentionally a configurable heuristic.
    """

    technologies = [

        normalize_text(
            item
        )

        for item
        in get_curriculum_technologies(
            curriculum
        )

    ]


    tools = [

        normalize_text(
            item
        )

        for item
        in get_curriculum_tools(
            curriculum
        )

    ]


    combined = set(

        [
            *technologies,
            *tools,
        ]

    )


    if not combined:

        return 0.0


    matched = 0


    for item in combined:

        for industry_item
        in INDUSTRY_TECHNOLOGY_KEYWORDS:

            if (

                canonical_similarity(

                    item,

                    industry_item,

                )
                >=
                0.80

            ):

                matched += 1

                break


    score = (

        matched
        /
        len(
            INDUSTRY_TECHNOLOGY_KEYWORDS
        )

    ) * 100.0


    # Avoid over-penalizing small curricula.
    exposure_score = min(
        100.0,
        matched * 8.0,
    )


    return round(

        max(
            score,
            exposure_score,
        ),

        2,

    )


# ============================================================
# 168. EMERGING TECHNOLOGY SCORE
# ============================================================

def emerging_technology_score(
    curriculum: Any,
) -> float:
    """
    Estimate exposure to newer AI/data technologies.
    """

    text = normalize_text(

        curriculum_comparison_text(
            curriculum
        )

    )


    emerging_keywords = [

        "generative ai",

        "genai",

        "large language model",

        "llm",

        "rag",

        "retrieval augmented generation",

        "agentic ai",

        "ai agents",

        "langgraph",

        "langchain",

        "vector database",

        "embeddings",

        "multimodal ai",

        "vision language model",

        "fine tuning",

        "peft",

        "lora",

        "mlops",

        "llmops",

        "prompt engineering",

        "diffusion models",

        "transformers",

    ]


    hits = 0


    for keyword in emerging_keywords:

        if keyword in text:

            hits += 1


    return round(

        min(

            100.0,

            (
                hits
                /
                len(
                    emerging_keywords
                )
            )
            *
            100.0,

        ),

        2,

    )


# ============================================================
# 169. CONTENT MATURITY SCORE
# ============================================================

def content_maturity_score(
    curriculum: Any,
) -> float:
    """
    Estimate content maturity using:

        modules
        topics
        concepts
        outcomes
    """

    modules = get_curriculum_modules(
        curriculum
    )

    topics = get_curriculum_topics(
        curriculum
    )

    concepts = get_curriculum_concepts(
        curriculum
    )

    outcomes = (

        get_curriculum_outcomes(
            curriculum,
            "course",
        )

    )


    module_score = min(

        100.0,

        len(modules) * 10.0,

    )


    topic_score = min(

        100.0,

        len(topics) * 4.0,

    )


    concept_score = min(

        100.0,

        len(concepts) * 3.0,

    )


    outcome_score = min(

        100.0,

        len(outcomes) * 10.0,

    )


    score = (

        module_score * 0.25

        +

        topic_score * 0.30

        +

        concept_score * 0.30

        +

        outcome_score * 0.15

    )


    return round(
        min(
            100.0,
            score,
        ),
        2,
    )


# ============================================================
# 170. MATURITY LEVEL
# ============================================================

def maturity_level(
    score: float,
) -> str:
    """
    Convert maturity score to a label.
    """

    score = normalize_score(
        score
    )


    if score >= 90:

        return "Industry Leading"


    if score >= 80:

        return "Advanced"


    if score >= 70:

        return "Industry Ready"


    if score >= 60:

        return "Intermediate"


    if score >= 45:

        return "Developing"


    return "Basic"


# ============================================================
# 171. BUILD MATURITY STRENGTHS
# ============================================================

def build_maturity_strengths(
    scores: Dict[str, float],
) -> List[str]:
    """
    Identify high-scoring maturity dimensions.
    """

    labels = {

        "content":
            "content coverage",

        "topic":
            "topic coverage",

        "skill":
            "skill development",

        "technology":
            "technology breadth",

        "project":
            "project-based learning",

        "tool":
            "tool exposure",

        "emerging_technology":
            "emerging technology exposure",

        "practical":
            "practical learning",

        "employability":
            "employability orientation",

        "industry_alignment":
            "industry alignment",

    }


    strengths = []


    for key, score in scores.items():

        if score >= 80:

            label = labels.get(
                key,
                key.replace(
                    "_",
                    " ",
                ),
            )


            strengths.append(

                (
                    f"Strong {label} "
                    f"({score:.1f}/100)."
                )

            )


    return strengths


# ============================================================
# 172. BUILD MATURITY WEAKNESSES
# ============================================================

def build_maturity_weaknesses(
    scores: Dict[str, float],
) -> List[str]:
    """
    Identify low-scoring maturity dimensions.
    """

    labels = {

        "content":
            "content coverage",

        "topic":
            "topic coverage",

        "skill":
            "skill development",

        "technology":
            "technology breadth",

        "project":
            "project-based learning",

        "tool":
            "tool exposure",

        "emerging_technology":
            "emerging technology exposure",

        "practical":
            "practical learning",

        "employability":
            "employability orientation",

        "industry_alignment":
            "industry alignment",

    }


    weaknesses = []


    for key, score in scores.items():

        if score < 50:

            label = labels.get(
                key,
                key.replace(
                    "_",
                    " ",
                ),
            )


            weaknesses.append(

                (
                    f"Low {label} "
                    f"({score:.1f}/100)."
                )

            )


    return weaknesses


# ============================================================
# 173. BUILD MATURITY RECOMMENDATIONS
# ============================================================

def build_maturity_recommendations(
    scores: Dict[str, float],
) -> List[str]:
    """
    Generate practical curriculum improvement actions.
    """

    recommendations = []


    if scores.get(
        "skill",
        0,
    ) < 60:

        recommendations.append(

            (
                "Increase explicit skill outcomes and "
                "hands-on skill-building activities."
            )

        )


    if scores.get(
        "technology",
        0,
    ) < 60:

        recommendations.append(

            (
                "Expand technology coverage with "
                "current industry tools and platforms."
            )

        )


    if scores.get(
        "project",
        0,
    ) < 60:

        recommendations.append(

            (
                "Introduce more end-to-end projects, "
                "capstones, and production-oriented assignments."
            )

        )


    if scores.get(
        "practical",
        0,
    ) < 60:

        recommendations.append(

            (
                "Increase labs, implementation exercises, "
                "deployment activities, and case studies."
            )

        )


    if scores.get(
        "emerging_technology",
        0,
    ) < 60:

        recommendations.append(

            (
                "Add emerging technologies such as "
                "Generative AI, LLMs, RAG, AI Agents, "
                "MLOps, or other domain-relevant technologies."
            )

        )


    if scores.get(
        "employability",
        0,
    ) < 60:

        recommendations.append(

            (
                "Strengthen employability components through "
                "industry projects, deployment, Git, APIs, "
                "cloud, testing, internships, and technical "
                "interview preparation."
            )

        )


    if scores.get(
        "industry_alignment",
        0,
    ) < 60:

        recommendations.append(

            (
                "Increase alignment between curriculum "
                "technologies, skills, projects, and "
                "real-world engineering workflows."
            )

        )


    return recommendations


# ============================================================
# 174. CALCULATE INDUSTRY ALIGNMENT
# ============================================================

def calculate_industry_alignment(
    curriculum: Any,
    scoring_config: Optional[
        IndustryScoringConfig
    ] = None,
) -> float:
    """
    Calculate industry alignment for one curriculum.
    """

    scoring_config = (
        scoring_config
        or IndustryScoringConfig()
    )


    skill_score = skill_depth_score(

        curriculum,

        scoring_config.minimum_skill_count,

    )


    technology_score = technology_breadth_score(

        curriculum,

        scoring_config.minimum_technology_count,

    )


    project_score = project_depth_score(

        curriculum,

        scoring_config.minimum_project_count,

    )


    tool_score = tool_breadth_score(

        curriculum,

        scoring_config.minimum_tool_count,

    )


    industry_tech_score = (
        industry_technology_score(
            curriculum
        )
    )


    practical_score = (
        practical_learning_score(
            curriculum
        )
    )


    score = (

        skill_score * 0.20

        +

        technology_score * 0.20

        +

        project_score * 0.20

        +

        tool_score * 0.10

        +

        industry_tech_score * 0.15

        +

        practical_score * 0.15

    )


    return round(

        min(
            100.0,
            score,
        ),

        2,

    )


# ============================================================
# 175. BUILD CURRICULUM MATURITY SCORE
# ============================================================

def calculate_curriculum_maturity(
    curriculum: Any,
    scoring_config: Optional[
        IndustryScoringConfig
    ] = None,
) -> CurriculumMaturityScore:
    """
    Calculate comprehensive curriculum maturity.
    """

    scoring_config = (
        scoring_config
        or IndustryScoringConfig()
    )


    # --------------------------------------------------------
    # Individual scores
    # --------------------------------------------------------

    content = content_maturity_score(
        curriculum
    )


    topics = min(

        100.0,

        len(
            get_curriculum_topics(
                curriculum
            )
        )
        * 4.0,

    )


    skills = skill_depth_score(

        curriculum,

        scoring_config.minimum_skill_count,

    )


    technologies = technology_breadth_score(

        curriculum,

        scoring_config.minimum_technology_count,

    )


    projects = project_depth_score(

        curriculum,

        scoring_config.minimum_project_count,

    )


    tools = tool_breadth_score(

        curriculum,

        scoring_config.minimum_tool_count,

    )


    emerging = emerging_technology_score(
        curriculum
    )


    practical = practical_learning_score(
        curriculum
    )


    employability = employability_score(
        curriculum
    )


    industry_alignment = (
        calculate_industry_alignment(

            curriculum,

            scoring_config,

        )
    )


    # --------------------------------------------------------
    # Weighted overall score
    # --------------------------------------------------------

    weights = {

        "content":
            scoring_config.content_weight,

        "topic":
            scoring_config.topic_weight,

        "skill":
            scoring_config.skill_weight,

        "technology":
            scoring_config.technology_weight,

        "project":
            scoring_config.project_weight,

        "tool":
            scoring_config.tool_weight,

        "emerging_technology":
            scoring_config.emerging_technology_weight,

    }


    values = {

        "content":
            content,

        "topic":
            topics,

        "skill":
            skills,

        "technology":
            technologies,

        "project":
            projects,

        "tool":
            tools,

        "emerging_technology":
            emerging,

    }


    weighted_sum = 0.0

    total_weight = 0.0


    for key, weight in weights.items():

        if weight <= 0:
            continue


        weighted_sum += (

            values[key]
            *
            weight

        )


        total_weight += weight


    if total_weight > 0:

        overall = (

            weighted_sum
            /
            total_weight

        )

    else:

        overall = 0.0


    # --------------------------------------------------------
    # Strengths / weaknesses
    # --------------------------------------------------------

    dimension_scores = {

        **values,

        "practical":
            practical,

        "employability":
            employability,

        "industry_alignment":
            industry_alignment,

    }


    strengths = build_maturity_strengths(
        dimension_scores
    )


    weaknesses = build_maturity_weaknesses(
        dimension_scores
    )


    recommendations = (
        build_maturity_recommendations(
            dimension_scores
        )
    )


    return CurriculumMaturityScore(

        overall_score=round(
            overall,
            2,
        ),

        content_score=content,

        topic_score=topics,

        skill_score=skills,

        technology_score=technologies,

        project_score=projects,

        tool_score=tools,

        emerging_technology_score=emerging,

        practical_score=practical,

        employability_score=employability,

        industry_alignment_score=(
            industry_alignment
        ),

        maturity_level=maturity_level(
            overall
        ),

        strengths=strengths,

        weaknesses=weaknesses,

        recommendations=recommendations,

    )


# ============================================================
# 176. COMPARE MATURITY
# ============================================================

def compare_curriculum_maturity(
    source: Any,
    target: Any,
    scoring_config: Optional[
        IndustryScoringConfig
    ] = None,
) -> Dict[str, Any]:
    """
    Compare maturity scores of source and target curricula.
    """

    source_score = (
        calculate_curriculum_maturity(

            source,

            scoring_config,

        )
    )


    target_score = (
        calculate_curriculum_maturity(

            target,

            scoring_config,

        )
    )


    differences = {

        "overall_score":
            round(

                target_score.overall_score
                -
                source_score.overall_score,

                2,

            ),

        "content_score":
            round(

                target_score.content_score
                -
                source_score.content_score,

                2,

            ),

        "topic_score":
            round(

                target_score.topic_score
                -
                source_score.topic_score,

                2,

            ),

        "skill_score":
            round(

                target_score.skill_score
                -
                source_score.skill_score,

                2,

            ),

        "technology_score":
            round(

                target_score.technology_score
                -
                source_score.technology_score,

                2,

            ),

        "project_score":
            round(

                target_score.project_score
                -
                source_score.project_score,

                2,

            ),

        "tool_score":
            round(

                target_score.tool_score
                -
                source_score.tool_score,

                2,

            ),

        "emerging_technology_score":
            round(

                target_score.emerging_technology_score
                -
                source_score.emerging_technology_score,

                2,

            ),

        "practical_score":
            round(

                target_score.practical_score
                -
                source_score.practical_score,

                2,

            ),

        "employability_score":
            round(

                target_score.employability_score
                -
                source_score.employability_score,

                2,

            ),

        "industry_alignment_score":
            round(

                target_score.industry_alignment_score
                -
                source_score.industry_alignment_score,

                2,

            ),

    }


    return {

        "source":
            source_score,

        "target":
            target_score,

        "differences":
            differences,

    }


# ============================================================
# 177. MATURITY SCORE TO DICT
# ============================================================

def maturity_score_to_dict(
    score: CurriculumMaturityScore,
) -> Dict[str, Any]:
    """
    Serialize CurriculumMaturityScore.
    """

    return {

        "overall_score":
            score.overall_score,

        "content_score":
            score.content_score,

        "topic_score":
            score.topic_score,

        "skill_score":
            score.skill_score,

        "technology_score":
            score.technology_score,

        "project_score":
            score.project_score,

        "tool_score":
            score.tool_score,

        "emerging_technology_score":
            score.emerging_technology_score,

        "practical_score":
            score.practical_score,

        "employability_score":
            score.employability_score,

        "industry_alignment_score":
            score.industry_alignment_score,

        "maturity_level":
            score.maturity_level,

        "strengths":
            list(
                score.strengths
            ),

        "weaknesses":
            list(
                score.weaknesses
            ),

        "recommendations":
            list(
                score.recommendations
            ),

    }


# ============================================================
# 178. MATURITY COMPARISON TO DICT
# ============================================================

def maturity_comparison_to_dict(
    comparison: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Serialize maturity comparison.
    """

    return {

        "source":
            maturity_score_to_dict(
                comparison[
                    "source"
                ]
            ),

        "target":
            maturity_score_to_dict(
                comparison[
                    "target"
                ]
            ),

        "differences":
            dict(
                comparison[
                    "differences"
                ]
            ),

    }


# ============================================================
# 179. END OF CHUNK 7
# ============================================================
# ============================================================
# curriculum/comparator.py
# CHUNK 8/10
#
# GAP SEVERITY + PRIORITIZATION ENGINE
#
# Gap Detection
#      │
#      ├── Missing Concept
#      ├── Missing Skill
#      ├── Missing Technology
#      ├── Missing Tool
#      ├── Missing Project
#      ├── Missing Topic
#      └── Missing Outcome
#               │
#               ▼
#       Severity Calculation
#               │
#       ┌───────┼────────┐
#       ▼       ▼        ▼
#    Critical  High    Medium/Low
#               │
#               ▼
#        Priority Ranking
# ============================================================


# ============================================================
# 180. GAP SEVERITY ENUM-LIKE CONSTANTS
# ============================================================

GAP_CRITICAL = "Critical"

GAP_HIGH = "High"

GAP_MEDIUM = "Medium"

GAP_LOW = "Low"


GAP_SEVERITY_ORDER = {

    GAP_CRITICAL: 4,

    GAP_HIGH: 3,

    GAP_MEDIUM: 2,

    GAP_LOW: 1,

}


# ============================================================
# 181. GAP TYPE CONSTANTS
# ============================================================

GAP_MODULE = "module"

GAP_TOPIC = "topic"

GAP_CONCEPT = "concept"

GAP_SKILL = "skill"

GAP_TOOL = "tool"

GAP_TECHNOLOGY = "technology"

GAP_PROJECT = "project"

GAP_COURSE_OUTCOME = "course_outcome"

GAP_PROGRAM_OUTCOME = "program_outcome"

GAP_PSO = "program_specific_outcome"


# ============================================================
# 182. GAP PRIORITY WEIGHTS
# ============================================================

DEFAULT_GAP_WEIGHTS = {

    GAP_MODULE: 0.90,

    GAP_TOPIC: 0.80,

    GAP_CONCEPT: 0.75,

    GAP_SKILL: 1.00,

    GAP_TOOL: 0.65,

    GAP_TECHNOLOGY: 0.95,

    GAP_PROJECT: 1.00,

    GAP_COURSE_OUTCOME: 0.90,

    GAP_PROGRAM_OUTCOME: 0.85,

    GAP_PSO: 0.85,

}


# ============================================================
# 183. GAP ITEM
# ============================================================

@dataclass
class GapItem:
    """
    Represents one prioritized curriculum gap.
    """

    gap_id: str

    gap_type: str

    name: str

    description: str = ""

    severity: str = GAP_MEDIUM

    priority_score: float = 0.0

    priority_rank: int = 0

    source_present: bool = True

    target_present: bool = False

    semantic_similarity_percentage: float = 0.0

    confidence_percentage: float = 0.0

    industry_relevance_percentage: float = 0.0

    learning_impact_percentage: float = 0.0

    prerequisite_impact_percentage: float = 0.0

    employability_impact_percentage: float = 0.0

    frequency: int = 1

    affected_modules: List[str] = field(
        default_factory=list
    )

    related_concepts: List[str] = field(
        default_factory=list
    )

    prerequisite_concepts: List[str] = field(
        default_factory=list
    )

    recommended_action: str = ""

    rationale: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# 184. GAP SUMMARY
# ============================================================

@dataclass
class GapSummary:
    """
    Summary of all curriculum gaps.
    """

    total_gaps: int = 0

    critical_gaps: int = 0

    high_gaps: int = 0

    medium_gaps: int = 0

    low_gaps: int = 0

    total_priority_score: float = 0.0

    average_priority_score: float = 0.0

    coverage_percentage: float = 0.0

    gap_percentage: float = 0.0

    top_gaps: List[GapItem] = field(
        default_factory=list
    )

    recommendations: List[str] = field(
        default_factory=list
    )


# ============================================================
# 185. GAP ANALYSIS RESULT
# ============================================================

@dataclass
class GapAnalysisResult:
    """
    Complete structured gap-analysis output.
    """

    gaps: List[GapItem] = field(
        default_factory=list
    )

    summary: Optional[
        GapSummary
    ] = None

    by_type: Dict[
        str,
        List[GapItem]
    ] = field(
        default_factory=dict
    )

    by_severity: Dict[
        str,
        List[GapItem]
    ] = field(
        default_factory=dict
    )

    critical_actions: List[str] = field(
        default_factory=list
    )

    high_priority_actions: List[str] = field(
        default_factory=list
    )


# ============================================================
# 186. GENERATE GAP ID
# ============================================================

def generate_gap_id(
    gap_type: str,
    name: str,
) -> str:
    """
    Generate deterministic gap identifier.
    """

    gap_type = normalize_text(
        gap_type
    ).replace(
        " ",
        "_",
    )


    canonical = canonical_term(
        name
    ).replace(
        " ",
        "_",
    )


    return (
        f"{gap_type}_{canonical}"
    )


# ============================================================
# 187. GAP SEVERITY FROM SCORE
# ============================================================

def severity_from_score(
    score: float,
) -> str:
    """
    Convert priority score into severity.

    Score range:
        0-100
    """

    score = normalize_score(
        score
    )


    if score >= 80:

        return GAP_CRITICAL


    if score >= 65:

        return GAP_HIGH


    if score >= 40:

        return GAP_MEDIUM


    return GAP_LOW


# ============================================================
# 188. GAP TYPE DISPLAY NAME
# ============================================================

def gap_type_display_name(
    gap_type: str,
) -> str:
    """
    Convert gap type to user-facing name.
    """

    mapping = {

        GAP_MODULE:
            "Module",

        GAP_TOPIC:
            "Topic",

        GAP_CONCEPT:
            "Concept",

        GAP_SKILL:
            "Skill",

        GAP_TOOL:
            "Tool",

        GAP_TECHNOLOGY:
            "Technology",

        GAP_PROJECT:
            "Project",

        GAP_COURSE_OUTCOME:
            "Course Outcome",

        GAP_PROGRAM_OUTCOME:
            "Program Outcome",

        GAP_PSO:
            "Program Specific Outcome",

    }


    return mapping.get(

        gap_type,

        gap_type.replace(
            "_",
            " ",
        ).title(),

    )


# ============================================================
# 189. INDUSTRY RELEVANCE ESTIMATION
# ============================================================

def estimate_industry_relevance(
    name: str,
    gap_type: str,
) -> float:
    """
    Estimate industry relevance of a missing item.

    This is intentionally heuristic and configurable.
    """

    text = normalize_text(
        name
    )


    if not text:

        return 0.0


    high_relevance_keywords = [

        "machine learning",

        "deep learning",

        "generative ai",

        "genai",

        "large language model",

        "llm",

        "rag",

        "retrieval augmented generation",

        "agentic ai",

        "ai agent",

        "python",

        "sql",

        "cloud",

        "aws",

        "azure",

        "gcp",

        "docker",

        "kubernetes",

        "mlops",

        "llmops",

        "data engineering",

        "data science",

        "computer vision",

        "natural language processing",

        "cybersecurity",

        "api",

        "fastapi",

        "git",

    ]


    medium_relevance_keywords = [

        "statistics",

        "database",

        "algorithm",

        "data structure",

        "software engineering",

        "testing",

        "deployment",

        "visualization",

        "analytics",

        "optimization",

    ]


    for keyword in high_relevance_keywords:

        if keyword in text:

            return 95.0


    for keyword in medium_relevance_keywords:

        if keyword in text:

            return 75.0


    # Technology gaps tend to be more directly actionable.
    if gap_type == GAP_TECHNOLOGY:

        return 70.0


    if gap_type == GAP_SKILL:

        return 70.0


    if gap_type == GAP_PROJECT:

        return 80.0


    return 55.0


# ============================================================
# 190. LEARNING IMPACT ESTIMATION
# ============================================================

def estimate_learning_impact(
    gap_type: str,
    name: str,
    related_count: int = 0,
) -> float:
    """
    Estimate learning impact of a gap.
    """

    base_scores = {

        GAP_MODULE:
            90.0,

        GAP_TOPIC:
            80.0,

        GAP_CONCEPT:
            70.0,

        GAP_SKILL:
            90.0,

        GAP_TOOL:
            60.0,

        GAP_TECHNOLOGY:
            85.0,

        GAP_PROJECT:
            95.0,

        GAP_COURSE_OUTCOME:
            85.0,

        GAP_PROGRAM_OUTCOME:
            80.0,

        GAP_PSO:
            80.0,

    }


    base = base_scores.get(
        gap_type,
        60.0,
    )


    # Related concepts indicate broader impact.
    related_bonus = min(

        10.0,

        related_count * 2.0,

    )


    return round(

        min(

            100.0,

            base
            +
            related_bonus,

        ),

        2,

    )


# ============================================================
# 191. EMPLOYABILITY IMPACT
# ============================================================

def estimate_employability_impact(
    name: str,
    gap_type: str,
) -> float:
    """
    Estimate employability impact.
    """

    text = normalize_text(
        name
    )


    very_high = [

        "project",

        "deployment",

        "api",

        "cloud",

        "docker",

        "kubernetes",

        "git",

        "python",

        "sql",

        "machine learning",

        "deep learning",

        "generative ai",

        "llm",

        "rag",

        "agentic ai",

        "data engineering",

        "mlops",

    ]


    high = [

        "testing",

        "debugging",

        "software engineering",

        "database",

        "data visualization",

        "statistics",

        "computer vision",

        "nlp",

    ]


    for keyword in very_high:

        if keyword in text:

            return 95.0


    for keyword in high:

        if keyword in text:

            return 80.0


    if gap_type == GAP_SKILL:

        return 75.0


    if gap_type == GAP_PROJECT:

        return 95.0


    if gap_type == GAP_TECHNOLOGY:

        return 80.0


    return 55.0


# ============================================================
# 192. PREREQUISITE IMPACT
# ============================================================

def estimate_prerequisite_impact(
    name: str,
    source_concepts: Optional[
        Sequence[str]
    ] = None,
) -> Tuple[
    float,
    List[str]
]:
    """
    Estimate whether a missing concept is foundational.

    Returns:

        impact score
        prerequisite concepts
    """

    relations = get_concept_relations(
        name
    )


    prerequisites = deduplicate(

        relations.get(
            "prerequisites",
            [],
        )

    )


    if not prerequisites:

        return (
            30.0,
            [],
        )


    existing = {

        canonical_term(
            item
        )

        for item
        in (
            source_concepts
            or []
        )

    }


    missing_prerequisites = [

        item

        for item
        in prerequisites

        if canonical_term(
            item
        )
        not in existing

    ]


    if missing_prerequisites:

        return (

            95.0,

            missing_prerequisites,

        )


    return (

        min(

            80.0,

            40.0
            +
            (
                len(
                    prerequisites
                )
                *
                5.0
            ),

        ),

        prerequisites,

    )


# ============================================================
# 193. CALCULATE GAP PRIORITY
# ============================================================

def calculate_gap_priority(
    gap_type: str,
    name: str,
    semantic_similarity: float = 0.0,
    frequency: int = 1,
    related_count: int = 0,
    source_concepts: Optional[
        Sequence[str]
    ] = None,
    custom_weight: Optional[
        float
    ] = None,
) -> Dict[str, float]:
    """
    Calculate multi-dimensional gap priority.

    Components:

        Industry relevance
        Learning impact
        Prerequisite impact
        Employability impact
        Frequency
        Semantic mismatch
    """

    industry = estimate_industry_relevance(

        name,

        gap_type,

    )


    learning = estimate_learning_impact(

        gap_type,

        name,

        related_count,

    )


    employability = (
        estimate_employability_impact(

            name,

            gap_type,

        )
    )


    prerequisite, _ = (
        estimate_prerequisite_impact(

            name,

            source_concepts,

        )
    )


    # --------------------------------------------------------
    # Frequency score
    # --------------------------------------------------------

    frequency_score = min(

        100.0,

        50.0
        +
        (
            max(
                0,
                frequency - 1,
            )
            *
            10.0
        ),

    )


    # --------------------------------------------------------
    # Semantic gap score
    # --------------------------------------------------------

    semantic_gap = (

        100.0
        -
        normalize_score(
            semantic_similarity
        )

    )


    # --------------------------------------------------------
    # Weighted priority
    # --------------------------------------------------------

    score = (

        industry * 0.25

        +

        learning * 0.20

        +

        prerequisite * 0.15

        +

        employability * 0.25

        +

        frequency_score * 0.05

        +

        semantic_gap * 0.10

    )


    if custom_weight is not None:

        score *= safe_float(
            custom_weight
        )


    return {

        "priority_score":
            round(
                min(
                    100.0,
                    score,
                ),
                2,
            ),

        "industry_relevance":
            round(
                industry,
                2,
            ),

        "learning_impact":
            round(
                learning,
                2,
            ),

        "prerequisite_impact":
            round(
                prerequisite,
                2,
            ),

        "employability_impact":
            round(
                employability,
                2,
            ),

        "frequency_score":
            round(
                frequency_score,
                2,
            ),

        "semantic_gap":
            round(
                semantic_gap,
                2,
            ),

    }


# ============================================================
# 194. RECOMMENDED GAP ACTION
# ============================================================

def recommended_gap_action(
    gap_type: str,
    severity: str,
    name: str,
) -> str:
    """
    Generate an action based on gap type/severity.
    """

    prefix = ""

    if severity == GAP_CRITICAL:

        prefix = "Immediately "

    elif severity == GAP_HIGH:

        prefix = "Prioritize "

    elif severity == GAP_MEDIUM:

        prefix = "Consider "

    else:

        prefix = "Evaluate "


    actions = {

        GAP_MODULE:
            (
                "add or redesign a module "
                f"covering '{name}'."
            ),

        GAP_TOPIC:
            (
                "add the topic "
                f"'{name}' to an appropriate module."
            ),

        GAP_CONCEPT:
            (
                "introduce the concept "
                f"'{name}' through theory and practical exercises."
            ),

        GAP_SKILL:
            (
                "add hands-on activities to develop "
                f"the skill '{name}'."
            ),

        GAP_TOOL:
            (
                "provide practical exposure to "
                f"the tool '{name}'."
            ),

        GAP_TECHNOLOGY:
            (
                "introduce "
                f"'{name}' through labs and an implementation project."
            ),

        GAP_PROJECT:
            (
                "add an end-to-end project involving "
                f"'{name}'."
            ),

        GAP_COURSE_OUTCOME:
            (
                "review course outcomes to include "
                f"'{name}' where academically appropriate."
            ),

        GAP_PROGRAM_OUTCOME:
            (
                "map the curriculum against the program outcome "
                f"'{name}'."
            ),

        GAP_PSO:
            (
                "strengthen program-specific outcome mapping "
                f"for '{name}'."
            ),

    }


    action = actions.get(

        gap_type,

        (
            "review and address the gap "
            f"'{name}'."
        ),

    )


    return prefix + action


# ============================================================
# 195. GAP RATIONALE
# ============================================================

def build_gap_rationale(
    gap_type: str,
    name: str,
    severity: str,
    priority_score: float,
    industry_relevance: float,
    employability_impact: float,
) -> str:
    """
    Generate human-readable rationale.
    """

    type_name = (
        gap_type_display_name(
            gap_type
        )
    )


    return (

        f"{type_name} '{name}' is classified as "
        f"{severity} priority with a score of "
        f"{priority_score:.1f}/100. "
        f"Industry relevance is "
        f"{industry_relevance:.1f}/100 and "
        f"employability impact is "
        f"{employability_impact:.1f}/100."

    )


# ============================================================
# 196. BUILD GAP ITEM
# ============================================================

def build_gap_item(
    gap_type: str,
    name: str,
    source_concepts: Optional[
        Sequence[str]
    ] = None,
    target_concepts: Optional[
        Sequence[str]
    ] = None,
    semantic_similarity: float = 0.0,
    frequency: int = 1,
    affected_modules: Optional[
        Sequence[str]
    ] = None,
    related_concepts: Optional[
        Sequence[str]
    ] = None,
    custom_weight: Optional[
        float
    ] = None,
) -> GapItem:
    """
    Build a complete prioritized GapItem.
    """

    name = clean_text(
        name
    )


    source_concepts = (
        list(
            source_concepts
            or []
        )
    )


    target_concepts = (
        list(
            target_concepts
            or []
        )
    )


    related_concepts = (
        list(
            related_concepts
            or []
        )
    )


    affected_modules = (
        list(
            affected_modules
            or []
        )
    )


    # --------------------------------------------------------
    # Priority
    # --------------------------------------------------------

    priority = calculate_gap_priority(

        gap_type,

        name,

        semantic_similarity,

        frequency,

        len(
            related_concepts
        ),

        source_concepts,

        custom_weight,

    )


    priority_score = priority[
        "priority_score"
    ]


    severity = severity_from_score(
        priority_score
    )


    # --------------------------------------------------------
    # Prerequisites
    # --------------------------------------------------------

    prerequisite_score, prerequisites = (
        estimate_prerequisite_impact(

            name,

            source_concepts,

        )
    )


    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    action = recommended_gap_action(

        gap_type,

        severity,

        name,

    )


    rationale = build_gap_rationale(

        gap_type,

        name,

        severity,

        priority_score,

        priority[
            "industry_relevance"
        ],

        priority[
            "employability_impact"
        ],

    )


    return GapItem(

        gap_id=generate_gap_id(

            gap_type,

            name,

        ),

        gap_type=gap_type,

        name=name,

        description=(

            f"Missing {gap_type_display_name(gap_type).lower()} "
            f"identified during curriculum comparison."

        ),

        severity=severity,

        priority_score=priority_score,

        source_present=True,

        target_present=False,

        semantic_similarity_percentage=(

            normalize_score(
                semantic_similarity
            )

        ),

        confidence_percentage=(

            round(

                match_confidence(
                    semantic_similarity
                )
                * 100,

                2,

            )

        ),

        industry_relevance_percentage=(

            priority[
                "industry_relevance"
            ]

        ),

        learning_impact_percentage=(

            priority[
                "learning_impact"
            ]

        ),

        prerequisite_impact_percentage=(

            prerequisite_score

        ),

        employability_impact_percentage=(

            priority[
                "employability_impact"
            ]

        ),

        frequency=max(
            1,
            frequency,
        ),

        affected_modules=deduplicate(

            affected_modules

        ),

        related_concepts=deduplicate(

            related_concepts

        ),

        prerequisite_concepts=deduplicate(

            prerequisites

        ),

        recommended_action=action,

        rationale=rationale,

        metadata={

            "semantic_gap":
                priority[
                    "semantic_gap"
                ],

            "frequency_score":
                priority[
                    "frequency_score"
                ],

        },

    )


# ============================================================
# 197. BUILD GAPS FROM CATEGORY
# ============================================================

def build_gaps_from_category(
    gap_type: str,
    category_result: Optional[
        CategoryComparison
    ],
    source_concepts: Optional[
        Sequence[str]
    ] = None,
    target_concepts: Optional[
        Sequence[str]
    ] = None,
    semantic_config: Optional[
        SemanticConfig
    ] = None,
    custom_weight: Optional[
        float
    ] = None,
) -> List[GapItem]:
    """
    Convert CategoryComparison missing items into GapItems.
    """

    if category_result is None:

        return []


    gaps = []


    missing_items = (

        category_result.missing
        or []

    )


    for item in missing_items:

        item = clean_text(
            item
        )


        if not item:
            continue


        # ----------------------------------------------------
        # Find semantic similarity against target
        # ----------------------------------------------------

        similarity = 0.0

        if target_concepts:

            best = semantic_best_match(

                item,

                target_concepts,

                semantic_config,

            )


            if best is not None:

                similarity = best[1]


        gap = build_gap_item(

            gap_type=gap_type,

            name=item,

            source_concepts=source_concepts,

            target_concepts=target_concepts,

            semantic_similarity=similarity,

            frequency=1,

            custom_weight=custom_weight,

        )


        gaps.append(
            gap
        )


    return gaps


# ============================================================
# 198. BUILD ALL GAP ITEMS
# ============================================================

def build_all_gap_items(
    comparison: CurriculumComparison,
    source: Any = None,
    target: Any = None,
    semantic_config: Optional[
        SemanticConfig
    ] = None,
    gap_weights: Optional[
        Dict[str, float]
    ] = None,
) -> List[GapItem]:
    """
    Convert CurriculumComparison into prioritized GapItems.
    """

    gap_weights = (

        gap_weights
        or DEFAULT_GAP_WEIGHTS

    )


    source_concepts = []


    target_concepts = []


    if source is not None:

        source_concepts = (
            get_curriculum_concepts(
                source
            )
        )


    if target is not None:

        target_concepts = (
            get_curriculum_concepts(
                target
            )
        )


    all_gaps = []


    # --------------------------------------------------------
    # Category mapping
    # --------------------------------------------------------

    category_mapping = [

        (
            GAP_MODULE,
            comparison.module_comparison,
        ),

        (
            GAP_TOPIC,
            comparison.topic_comparison,
        ),

        (
            GAP_CONCEPT,
            comparison.concept_comparison,
        ),

        (
            GAP_SKILL,
            comparison.skill_comparison,
        ),

        (
            GAP_TOOL,
            comparison.tool_comparison,
        ),

        (
            GAP_TECHNOLOGY,
            comparison.technology_comparison,
        ),

        (
            GAP_PROJECT,
            comparison.project_comparison,
        ),

        (
            GAP_COURSE_OUTCOME,
            comparison.course_outcome_comparison,
        ),

        (
            GAP_PROGRAM_OUTCOME,
            comparison.program_outcome_comparison,
        ),

        (
            GAP_PSO,
            comparison.pso_comparison,
        ),

    ]


    for (
        gap_type,
        category_result,
    ) in category_mapping:

        if category_result is None:
            continue


        gaps = build_gaps_from_category(

            gap_type=gap_type,

            category_result=category_result,

            source_concepts=source_concepts,

            target_concepts=target_concepts,

            semantic_config=semantic_config,

            custom_weight=gap_weights.get(
                gap_type
            ),

        )


        all_gaps.extend(
            gaps
        )


    return all_gaps


# ============================================================
# 199. DEDUPLICATE GAPS
# ============================================================

def deduplicate_gap_items(
    gaps: Sequence[GapItem],
) -> List[GapItem]:
    """
    Deduplicate gaps using:
        gap type + canonical name
    """

    seen = set()

    result = []


    for gap in gaps:

        key = (

            gap.gap_type,

            canonical_term(
                gap.name
            ),

        )


        if key in seen:

            continue


        seen.add(
            key
        )


        result.append(
            gap
        )


    return result


# ============================================================
# 200. SORT GAPS
# ============================================================

def sort_gap_items(
    gaps: Sequence[GapItem],
) -> List[GapItem]:
    """
    Sort gaps by:

        severity
        priority score
        industry relevance
        employability impact
    """

    return sorted(

        list(
            gaps
        ),

        key=lambda gap: (

            GAP_SEVERITY_ORDER.get(

                gap.severity,

                0,

            ),

            gap.priority_score,

            gap.industry_relevance_percentage,

            gap.employability_impact_percentage,

        ),

        reverse=True,

    )


# ============================================================
# 201. ASSIGN GAP RANKS
# ============================================================

def assign_gap_ranks(
    gaps: Sequence[GapItem],
) -> List[GapItem]:
    """
    Assign sequential priority ranks.
    """

    sorted_gaps = sort_gap_items(
        gaps
    )


    result = []


    for rank, gap in enumerate(

        sorted_gaps,

        start=1,

    ):

        gap.priority_rank = rank

        result.append(
            gap
        )


    return result


# ============================================================
# 202. GROUP GAPS BY TYPE
# ============================================================

def group_gaps_by_type(
    gaps: Sequence[GapItem],
) -> Dict[
    str,
    List[GapItem]
]:
    """
    Group gap items by type.
    """

    result = {}


    for gap in gaps:

        result.setdefault(

            gap.gap_type,

            [],

        )


        result[
            gap.gap_type
        ].append(
            gap
        )


    return result


# ============================================================
# 203. GROUP GAPS BY SEVERITY
# ============================================================

def group_gaps_by_severity(
    gaps: Sequence[GapItem],
) -> Dict[
    str,
    List[GapItem]
]:
    """
    Group gaps by severity.
    """

    result = {

        GAP_CRITICAL: [],

        GAP_HIGH: [],

        GAP_MEDIUM: [],

        GAP_LOW: [],

    }


    for gap in gaps:

        result.setdefault(

            gap.severity,

            [],

        )


        result[
            gap.severity
        ].append(
            gap
        )


    return result


# ============================================================
# 204. BUILD GAP SUMMARY
# ============================================================

def build_gap_summary(
    gaps: Sequence[GapItem],
    source_item_count: int = 0,
    matched_item_count: int = 0,
) -> GapSummary:
    """
    Build aggregate gap statistics.
    """

    gaps = list(
        gaps
    )


    total = len(
        gaps
    )


    critical = sum(

        1

        for gap
        in gaps

        if gap.severity
        ==
        GAP_CRITICAL

    )


    high = sum(

        1

        for gap
        in gaps

        if gap.severity
        ==
        GAP_HIGH

    )


    medium = sum(

        1

        for gap
        in gaps

        if gap.severity
        ==
        GAP_MEDIUM

    )


    low = sum(

        1

        for gap
        in gaps

        if gap.severity
        ==
        GAP_LOW

    )


    total_priority = sum(

        gap.priority_score

        for gap
        in gaps

    )


    average_priority = (

        safe_divide(

            total_priority,

            total,

            0.0,

        )

    )


    coverage = percentage(

        matched_item_count,

        source_item_count,

    )


    gap_percentage = (

        100.0
        -
        coverage

    )


    top_gaps = (

        sort_gap_items(
            gaps
        )[:10]

    )


    recommendations = []


    if critical > 0:

        recommendations.append(

            (
                f"Address {critical} critical "
                "curriculum gap(s) immediately."
            )

        )


    if high > 0:

        recommendations.append(

            (
                f"Prioritize {high} high-impact "
                "gap(s) in the next curriculum revision."
            )

        )


    if medium > 0:

        recommendations.append(

            (
                f"Review {medium} medium-priority "
                "gap(s) during the next enhancement cycle."
            )

        )


    return GapSummary(

        total_gaps=total,

        critical_gaps=critical,

        high_gaps=high,

        medium_gaps=medium,

        low_gaps=low,

        total_priority_score=round(

            total_priority,

            2,

        ),

        average_priority_score=round(

            average_priority,

            2,

        ),

        coverage_percentage=round(

            coverage,

            2,

        ),

        gap_percentage=round(

            max(
                0.0,
                gap_percentage,
            ),

            2,

        ),

        top_gaps=top_gaps,

        recommendations=recommendations,

    )


# ============================================================
# 205. BUILD GAP ANALYSIS
# ============================================================

def analyze_curriculum_gaps(
    comparison: CurriculumComparison,
    source: Any = None,
    target: Any = None,
    semantic_config: Optional[
        SemanticConfig
    ] = None,
    gap_weights: Optional[
        Dict[str, float]
    ] = None,
) -> GapAnalysisResult:
    """
    Main gap-analysis API.

    Example:

        comparison = compare_curriculums(
            source,
            target,
        )

        gaps = analyze_curriculum_gaps(
            comparison,
            source,
            target,
        )
    """

    gaps = build_all_gap_items(

        comparison,

        source=source,

        target=target,

        semantic_config=semantic_config,

        gap_weights=gap_weights,

    )


    gaps = deduplicate_gap_items(
        gaps
    )


    gaps = assign_gap_ranks(
        gaps
    )


    by_type = group_gaps_by_type(
        gaps
    )


    by_severity = group_gaps_by_severity(
        gaps
    )


    source_count = 0

    matched_count = 0


    # Use module/topic/concept counts as a broad
    # curriculum content measure.
    category_results = [

        comparison.module_comparison,

        comparison.topic_comparison,

        comparison.concept_comparison,

        comparison.skill_comparison,

        comparison.tool_comparison,

        comparison.technology_comparison,

        comparison.project_comparison,

    ]


    for result in category_results:

        if result is None:
            continue


        source_count += (
            result.source_count
        )


        matched_count += (
            result.matched_count
        )


    summary = build_gap_summary(

        gaps,

        source_item_count=source_count,

        matched_item_count=matched_count,

    )


    critical_actions = [

        gap.recommended_action

        for gap
        in by_severity.get(
            GAP_CRITICAL,
            [],
        )

    ]


    high_priority_actions = [

        gap.recommended_action

        for gap
        in by_severity.get(
            GAP_HIGH,
            [],
        )

    ]


    return GapAnalysisResult(

        gaps=gaps,

        summary=summary,

        by_type=by_type,

        by_severity=by_severity,

        critical_actions=critical_actions,

        high_priority_actions=high_priority_actions,

    )


# ============================================================
# 206. GAP ITEM TO DICT
# ============================================================

def gap_item_to_dict(
    gap: GapItem,
) -> Dict[str, Any]:
    """
    Serialize GapItem.
    """

    return {

        "gap_id":
            gap.gap_id,

        "gap_type":
            gap.gap_type,

        "gap_type_name":
            gap_type_display_name(
                gap.gap_type
            ),

        "name":
            gap.name,

        "description":
            gap.description,

        "severity":
            gap.severity,

        "priority_score":
            gap.priority_score,

        "priority_rank":
            gap.priority_rank,

        "source_present":
            gap.source_present,

        "target_present":
            gap.target_present,

        "semantic_similarity_percentage":
            gap.semantic_similarity_percentage,

        "confidence_percentage":
            gap.confidence_percentage,

        "industry_relevance_percentage":
            gap.industry_relevance_percentage,

        "learning_impact_percentage":
            gap.learning_impact_percentage,

        "prerequisite_impact_percentage":
            gap.prerequisite_impact_percentage,

        "employability_impact_percentage":
            gap.employability_impact_percentage,

        "frequency":
            gap.frequency,

        "affected_modules":
            list(
                gap.affected_modules
            ),

        "related_concepts":
            list(
                gap.related_concepts
            ),

        "prerequisite_concepts":
            list(
                gap.prerequisite_concepts
            ),

        "recommended_action":
            gap.recommended_action,

        "rationale":
            gap.rationale,

        "metadata":
            dict(
                gap.metadata
            ),

    }


# ============================================================
# 207. GAP SUMMARY TO DICT
# ============================================================

def gap_summary_to_dict(
    summary: GapSummary,
) -> Dict[str, Any]:
    """
    Serialize GapSummary.
    """

    return {

        "total_gaps":
            summary.total_gaps,

        "critical_gaps":
            summary.critical_gaps,

        "high_gaps":
            summary.high_gaps,

        "medium_gaps":
            summary.medium_gaps,

        "low_gaps":
            summary.low_gaps,

        "total_priority_score":
            summary.total_priority_score,

        "average_priority_score":
            summary.average_priority_score,

        "coverage_percentage":
            summary.coverage_percentage,

        "gap_percentage":
            summary.gap_percentage,

        "top_gaps": [

            gap_item_to_dict(
                gap
            )

            for gap
            in summary.top_gaps

        ],

        "recommendations":
            list(
                summary.recommendations
            ),

    }


# ============================================================
# 208. GAP ANALYSIS TO DICT
# ============================================================

def gap_analysis_to_dict(
    analysis: GapAnalysisResult,
) -> Dict[str, Any]:
    """
    Serialize complete gap analysis.
    """

    return {

        "gaps": [

            gap_item_to_dict(
                gap
            )

            for gap
            in analysis.gaps

        ],

        "summary": (

            gap_summary_to_dict(
                analysis.summary
            )

            if analysis.summary

            else None

        ),

        "by_type": {

            key: [

                gap_item_to_dict(
                    gap
                )

                for gap
                in values

            ]

            for key, values
            in analysis.by_type.items()

        },

        "by_severity": {

            key: [

                gap_item_to_dict(
                    gap
                )

                for gap
                in values

            ]

            for key, values
            in analysis.by_severity.items()

        },

        "critical_actions":
            list(
                analysis.critical_actions
            ),

        "high_priority_actions":
            list(
                analysis.high_priority_actions
            ),

    }


# ============================================================
# 209. GET TOP GAPS
# ============================================================

def get_top_gaps(
    analysis: GapAnalysisResult,
    limit: int = 10,
) -> List[GapItem]:
    """
    Return highest-priority gaps.
    """

    limit = max(
        1,
        int(
            limit
        ),
    )


    return list(
        analysis.gaps[:limit]
    )


# ============================================================
# 210. GET CRITICAL GAPS
# ============================================================

def get_critical_gaps(
    analysis: GapAnalysisResult,
) -> List[GapItem]:
    """
    Return critical gaps.
    """

    return list(

        analysis.by_severity.get(

            GAP_CRITICAL,

            [],

        )

    )


# ============================================================
# 211. GET HIGH PRIORITY GAPS
# ============================================================

def get_high_priority_gaps(
    analysis: GapAnalysisResult,
) -> List[GapItem]:
    """
    Return high-priority gaps.
    """

    return list(

        analysis.by_severity.get(

            GAP_HIGH,

            [],

        )

    )


# ============================================================
# 212. END OF CHUNK 8
# ============================================================
# ============================================================
# curriculum/comparator.py
# CHUNK 9/10
#
# CURRICULUM ENHANCEMENT RECOMMENDATION ENGINE
#
# Gap Analysis
#      │
#      ▼
# Gap Prioritization
#      │
#      ├── Module Enhancement
#      ├── Topic Enhancement
#      ├── Skill Enhancement
#      ├── Technology Lab
#      ├── Project Enhancement
#      └── Outcome Enhancement
#              │
#              ▼
#      Enhancement Plan
# ============================================================


# ============================================================
# 213. ENHANCEMENT TYPE CONSTANTS
# ============================================================

ENHANCEMENT_MODULE = "module_addition"

ENHANCEMENT_TOPIC = "topic_addition"

ENHANCEMENT_CONCEPT = "concept_addition"

ENHANCEMENT_SKILL = "skill_enhancement"

ENHANCEMENT_TOOL = "tool_exposure"

ENHANCEMENT_TECHNOLOGY = "technology_lab"

ENHANCEMENT_PROJECT = "project_enhancement"

ENHANCEMENT_OUTCOME = "outcome_alignment"

ENHANCEMENT_PREREQUISITE = "prerequisite_enhancement"

ENHANCEMENT_PRACTICAL = "practical_enhancement"


# ============================================================
# 214. ENHANCEMENT PRIORITY
# ============================================================

ENHANCEMENT_PRIORITY_CRITICAL = "Critical"

ENHANCEMENT_PRIORITY_HIGH = "High"

ENHANCEMENT_PRIORITY_MEDIUM = "Medium"

ENHANCEMENT_PRIORITY_LOW = "Low"


# ============================================================
# 215. ENHANCEMENT ITEM
# ============================================================

@dataclass
class EnhancementItem:
    """
    Represents one recommended curriculum enhancement.
    """

    enhancement_id: str

    enhancement_type: str

    title: str

    description: str = ""

    priority: str = ENHANCEMENT_PRIORITY_MEDIUM

    priority_score: float = 0.0

    target_gap_id: Optional[str] = None

    target_gap_type: Optional[str] = None

    target_gap_name: Optional[str] = None

    recommended_module: Optional[str] = None

    recommended_topics: List[str] = field(
        default_factory=list
    )

    recommended_concepts: List[str] = field(
        default_factory=list
    )

    recommended_skills: List[str] = field(
        default_factory=list
    )

    recommended_tools: List[str] = field(
        default_factory=list
    )

    recommended_technologies: List[str] = field(
        default_factory=list
    )

    recommended_project: Optional[str] = None

    prerequisites: List[str] = field(
        default_factory=list
    )

    learning_activities: List[str] = field(
        default_factory=list
    )

    assessment_methods: List[str] = field(
        default_factory=list
    )

    estimated_hours: float = 0.0

    industry_relevance: float = 0.0

    employability_impact: float = 0.0

    implementation_effort: float = 0.0

    expected_impact: float = 0.0

    rationale: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# 216. ENHANCEMENT PLAN
# ============================================================

@dataclass
class EnhancementPlan:
    """
    Complete curriculum enhancement roadmap.
    """

    curriculum_title: str

    total_enhancements: int = 0

    critical_enhancements: int = 0

    high_enhancements: int = 0

    medium_enhancements: int = 0

    low_enhancements: int = 0

    estimated_total_hours: float = 0.0

    estimated_impact_score: float = 0.0

    enhancements: List[
        EnhancementItem
    ] = field(
        default_factory=list
    )

    phase_1_immediate: List[
        EnhancementItem
    ] = field(
        default_factory=list
    )

    phase_2_short_term: List[
        EnhancementItem
    ] = field(
        default_factory=list
    )

    phase_3_medium_term: List[
        EnhancementItem
    ] = field(
        default_factory=list
    )

    strategic_recommendations: List[str] = field(
        default_factory=list
    )


# ============================================================
# 217. ENHANCEMENT CONFIG
# ============================================================

@dataclass
class EnhancementConfig:
    """
    Controls recommendation generation.
    """

    default_topic_hours: float = 4.0

    default_skill_hours: float = 6.0

    default_technology_lab_hours: float = 8.0

    default_project_hours: float = 24.0

    default_module_hours: float = 20.0

    maximum_recommendations: int = 50

    include_low_priority: bool = True

    generate_projects: bool = True

    generate_prerequisites: bool = True

    generate_assessment: bool = True


# ============================================================
# 218. ENHANCEMENT ID
# ============================================================

def generate_enhancement_id(
    enhancement_type: str,
    title: str,
) -> str:
    """
    Generate deterministic enhancement ID.
    """

    type_part = normalize_text(
        enhancement_type
    ).replace(
        " ",
        "_",
    )


    title_part = canonical_term(
        title
    ).replace(
        " ",
        "_",
    )


    return (
        f"{type_part}_{title_part}"
    )


# ============================================================
# 219. ENHANCEMENT PRIORITY FROM GAP
# ============================================================

def enhancement_priority_from_gap(
    gap: GapItem,
) -> str:
    """
    Convert gap severity to enhancement priority.
    """

    mapping = {

        GAP_CRITICAL:
            ENHANCEMENT_PRIORITY_CRITICAL,

        GAP_HIGH:
            ENHANCEMENT_PRIORITY_HIGH,

        GAP_MEDIUM:
            ENHANCEMENT_PRIORITY_MEDIUM,

        GAP_LOW:
            ENHANCEMENT_PRIORITY_LOW,

    }


    return mapping.get(

        gap.severity,

        ENHANCEMENT_PRIORITY_MEDIUM,

    )


# ============================================================
# 220. RECOMMENDED MODULE NAME
# ============================================================

def recommend_module_name(
    gap: GapItem,
) -> str:
    """
    Generate an appropriate module title.
    """

    name = clean_text(
        gap.name
    )


    mapping = {

        GAP_MODULE:
            name,

        GAP_TOPIC:
            f"Advanced {name}",

        GAP_CONCEPT:
            f"{name} Fundamentals",

        GAP_SKILL:
            f"Practical {name}",

        GAP_TOOL:
            f"{name} Tools & Workflow",

        GAP_TECHNOLOGY:
            f"{name} Technology & Applications",

        GAP_PROJECT:
            f"{name} Capstone Project",

        GAP_COURSE_OUTCOME:
            "Course Outcome Enhancement",

        GAP_PROGRAM_OUTCOME:
            "Program Outcome Enhancement",

        GAP_PSO:
            "Program Specific Outcome Enhancement",

    }


    return mapping.get(

        gap.gap_type,

        f"{name} Enhancement",

    )


# ============================================================
# 221. RECOMMENDED TOPICS
# ============================================================

def recommend_topics_for_gap(
    gap: GapItem,
) -> List[str]:
    """
    Generate suggested topics for the gap.
    """

    name = clean_text(
        gap.name
    )


    relations = get_concept_relations(
        name
    )


    topics = []


    if gap.gap_type == GAP_CONCEPT:

        topics.extend([

            f"{name} Fundamentals",

            f"{name} Architecture",

            f"{name} Implementation",

            f"{name} Applications",

        ])


    elif gap.gap_type == GAP_SKILL:

        topics.extend([

            f"{name} Fundamentals",

            f"{name} Hands-on Practice",

            f"{name} Real-world Application",

        ])


    elif gap.gap_type == GAP_TECHNOLOGY:

        topics.extend([

            f"{name} Overview",

            f"{name} Installation & Setup",

            f"{name} Core APIs",

            f"{name} Hands-on Lab",

            f"{name} Production Deployment",

        ])


    elif gap.gap_type == GAP_PROJECT:

        topics.extend([

            f"{name} Requirements",

            f"{name} Architecture",

            f"{name} Implementation",

            f"{name} Testing",

            f"{name} Deployment",

        ])


    else:

        topics.append(
            name
        )


    # Add known related concepts.
    topics.extend(

        relations.get(
            "related",
            [],
        )[:5]

    )


    return deduplicate(
        topics
    )


# ============================================================
# 222. RECOMMENDED SKILLS
# ============================================================

def recommend_skills_for_gap(
    gap: GapItem,
) -> List[str]:
    """
    Generate skills associated with the gap.
    """

    name = clean_text(
        gap.name
    )


    if gap.gap_type == GAP_SKILL:

        return [
            name,
            f"{name} implementation",
            f"{name} problem solving",
        ]


    if gap.gap_type == GAP_TECHNOLOGY:

        return [

            f"{name} implementation",

            f"{name} integration",

            f"{name} troubleshooting",

            f"{name} deployment",

        ]


    if gap.gap_type == GAP_PROJECT:

        return [

            "requirements analysis",

            "solution architecture",

            "implementation",

            "testing",

            "deployment",

            "documentation",

        ]


    if gap.gap_type == GAP_CONCEPT:

        return [

            f"{name} conceptual understanding",

            f"{name} implementation",

            f"{name} problem solving",

        ]


    return []


# ============================================================
# 223. RECOMMENDED TOOLS
# ============================================================

def recommend_tools_for_gap(
    gap: GapItem,
) -> List[str]:
    """
    Recommend tools based on gap terminology.
    """

    text = normalize_text(
        gap.name
    )


    recommendations = []


    tool_map = {

        "machine learning": [

            "Python",

            "scikit-learn",

            "Jupyter",

        ],

        "deep learning": [

            "Python",

            "PyTorch",

            "TensorFlow",

            "Jupyter",

        ],

        "generative ai": [

            "Python",

            "Hugging Face",

            "LangChain",

            "LangGraph",

        ],

        "large language model": [

            "Hugging Face",

            "Ollama",

            "LangChain",

        ],

        "rag": [

            "LangChain",

            "LlamaIndex",

            "FAISS",

            "Chroma",

        ],

        "retrieval augmented generation": [

            "LangChain",

            "LlamaIndex",

            "FAISS",

            "Chroma",

        ],

        "computer vision": [

            "OpenCV",

            "PyTorch",

            "TensorFlow",

        ],

        "natural language processing": [

            "Hugging Face",

            "spaCy",

            "NLTK",

        ],

        "mlops": [

            "MLflow",

            "Docker",

            "Kubernetes",

            "Kubeflow",

        ],

        "data engineering": [

            "Apache Spark",

            "Apache Kafka",

            "Airflow",

        ],

    }


    for keyword, tools in tool_map.items():

        if keyword in text:

            recommendations.extend(
                tools
            )


    return deduplicate(
        recommendations
    )


# ============================================================
# 224. RECOMMENDED TECHNOLOGIES
# ============================================================

def recommend_technologies_for_gap(
    gap: GapItem,
) -> List[str]:
    """
    Recommend technologies related to the gap.
    """

    text = normalize_text(
        gap.name
    )


    recommendations = []


    technology_map = {

        "machine learning": [

            "Python",

            "scikit-learn",

        ],

        "deep learning": [

            "PyTorch",

            "TensorFlow",

        ],

        "generative ai": [

            "LLMs",

            "Transformers",

            "RAG",

            "AI Agents",

        ],

        "large language model": [

            "Transformers",

            "LLM Fine-tuning",

            "PEFT",

        ],

        "rag": [

            "Embeddings",

            "Vector Databases",

            "Hybrid Search",

            "Reranking",

        ],

        "retrieval augmented generation": [

            "Embeddings",

            "Vector Databases",

            "Hybrid Search",

            "Reranking",

        ],

        "computer vision": [

            "CNN",

            "YOLO",

            "Vision Transformers",

        ],

        "natural language processing": [

            "Transformers",

            "BERT",

            "Sentence Embeddings",

        ],

        "mlops": [

            "Model Registry",

            "Model Serving",

            "Model Monitoring",

            "CI/CD",

        ],

        "cloud": [

            "AWS",

            "Azure",

            "GCP",

            "Docker",

            "Kubernetes",

        ],

    }


    for keyword, technologies in (
        technology_map.items()
    ):

        if keyword in text:

            recommendations.extend(
                technologies
            )


    return deduplicate(
        recommendations
    )


# ============================================================
# 225. RECOMMENDED PROJECT
# ============================================================

def recommend_project_for_gap(
    gap: GapItem,
) -> Optional[str]:
    """
    Generate an end-to-end project recommendation.
    """

    name = clean_text(
        gap.name
    )


    if gap.gap_type not in [

        GAP_SKILL,

        GAP_TECHNOLOGY,

        GAP_CONCEPT,

        GAP_PROJECT,

    ]:

        return None


    text = normalize_text(
        name
    )


    if (
        "rag" in text
        or
        "retrieval augmented" in text
    ):

        return (
            "Enterprise Document Intelligence "
            "RAG Assistant"
        )


    if (
        "large language model" in text
        or
        "llm" in text
    ):

        return (
            "Domain-Specific LLM Application"
        )


    if (
        "generative ai" in text
        or
        "genai" in text
    ):

        return (
            "Generative AI Business Application"
        )


    if (
        "machine learning" in text
        or
        "classification" in text
    ):

        return (
            "End-to-End Machine Learning "
            "Prediction System"
        )


    if (
        "computer vision" in text
        or
        "object detection" in text
    ):

        return (
            "Real-Time Computer Vision "
            "Detection Application"
        )


    if (
        "natural language processing" in text
        or
        "nlp" in text
    ):

        return (
            "NLP Text Intelligence Platform"
        )


    if "mlops" in text:

        return (
            "Production ML Model Deployment "
            "and Monitoring Platform"
        )


    if "data engineering" in text:

        return (
            "End-to-End Data Engineering Pipeline"
        )


    return (
        f"End-to-End {name} "
        "Industry Application"
    )


# ============================================================
# 226. RECOMMENDED PREREQUISITES
# ============================================================

def recommend_prerequisites(
    gap: GapItem,
) -> List[str]:
    """
    Determine prerequisite learning required before
    implementing the enhancement.
    """

    prerequisites = list(

        gap.prerequisite_concepts
        or []

    )


    if gap.gap_type == GAP_TECHNOLOGY:

        prerequisites.extend([

            "Programming fundamentals",

            "Basic system understanding",

        ])


    elif gap.gap_type == GAP_PROJECT:

        prerequisites.extend([

            "Problem definition",

            "Requirements analysis",

            "Version control",

        ])


    elif gap.gap_type == GAP_SKILL:

        prerequisites.extend([

            "Conceptual understanding",

            "Basic implementation practice",

        ])


    return deduplicate(
        prerequisites
    )


# ============================================================
# 227. LEARNING ACTIVITIES
# ============================================================

def recommend_learning_activities(
    gap: GapItem,
) -> List[str]:
    """
    Generate practical learning activities.
    """

    activities = []


    if gap.gap_type == GAP_CONCEPT:

        activities.extend([

            "Instructor-led concept session",

            "Worked examples",

            "Concept quiz",

            "Mini implementation",

        ])


    elif gap.gap_type == GAP_SKILL:

        activities.extend([

            "Guided hands-on lab",

            "Practice exercises",

            "Debugging exercise",

            "Independent implementation",

        ])


    elif gap.gap_type == GAP_TECHNOLOGY:

        activities.extend([

            "Environment setup",

            "Tool/API walkthrough",

            "Hands-on laboratory",

            "Integration exercise",

            "Deployment exercise",

        ])


    elif gap.gap_type == GAP_PROJECT:

        activities.extend([

            "Problem definition",

            "Architecture design",

            "Implementation",

            "Testing",

            "Deployment",

            "Project presentation",

        ])


    elif gap.gap_type == GAP_TOPIC:

        activities.extend([

            "Theory session",

            "Demonstration",

            "Hands-on exercise",

            "Assessment",

        ])


    else:

        activities.extend([

            "Concept session",

            "Hands-on activity",

            "Assessment",

        ])


    return activities


# ============================================================
# 228. ASSESSMENT METHODS
# ============================================================

def recommend_assessments(
    gap: GapItem,
) -> List[str]:
    """
    Generate assessment strategy.
    """

    assessments = [

        "Conceptual quiz",

    ]


    if gap.gap_type in [

        GAP_SKILL,

        GAP_TOOL,

        GAP_TECHNOLOGY,

    ]:

        assessments.extend([

            "Hands-on practical assessment",

            "Implementation assignment",

        ])


    if gap.gap_type in [

        GAP_PROJECT,

        GAP_TECHNOLOGY,

    ]:

        assessments.extend([

            "Project evaluation",

            "Code review",

            "Technical presentation",

        ])


    if gap.severity in [

        GAP_CRITICAL,

        GAP_HIGH,

    ]:

        assessments.append(

            "Industry-oriented capstone evaluation"

        )


    return deduplicate(
        assessments
    )


# ============================================================
# 229. ESTIMATE ENHANCEMENT HOURS
# ============================================================

def estimate_enhancement_hours(
    gap: GapItem,
    config: Optional[
        EnhancementConfig
    ] = None,
) -> float:
    """
    Estimate instructional hours.
    """

    config = (
        config
        or EnhancementConfig()
    )


    if gap.gap_type == GAP_MODULE:

        hours = (
            config.default_module_hours
        )


    elif gap.gap_type == GAP_TOPIC:

        hours = (
            config.default_topic_hours
        )


    elif gap.gap_type == GAP_CONCEPT:

        hours = (
            config.default_topic_hours
        )


    elif gap.gap_type == GAP_SKILL:

        hours = (
            config.default_skill_hours
        )


    elif gap.gap_type == GAP_TOOL:

        hours = (
            config.default_skill_hours
        )


    elif gap.gap_type == GAP_TECHNOLOGY:

        hours = (
            config.default_technology_lab_hours
        )


    elif gap.gap_type == GAP_PROJECT:

        hours = (
            config.default_project_hours
        )


    elif gap.gap_type in [

        GAP_COURSE_OUTCOME,

        GAP_PROGRAM_OUTCOME,

        GAP_PSO,

    ]:

        hours = 2.0


    else:

        hours = 4.0


    if gap.severity == GAP_CRITICAL:

        hours *= 1.25


    elif gap.severity == GAP_HIGH:

        hours *= 1.15


    return round(
        hours,
        1,
    )


# ============================================================
# 230. ESTIMATE IMPLEMENTATION EFFORT
# ============================================================

def estimate_implementation_effort(
    gap: GapItem,
) -> float:
    """
    Estimate implementation effort on 0-100.

    Higher means harder to implement.
    """

    effort_map = {

        GAP_MODULE:
            80.0,

        GAP_TOPIC:
            35.0,

        GAP_CONCEPT:
            25.0,

        GAP_SKILL:
            45.0,

        GAP_TOOL:
            40.0,

        GAP_TECHNOLOGY:
            60.0,

        GAP_PROJECT:
            85.0,

        GAP_COURSE_OUTCOME:
            20.0,

        GAP_PROGRAM_OUTCOME:
            25.0,

        GAP_PSO:
            25.0,

    }


    return effort_map.get(

        gap.gap_type,

        50.0,

    )


# ============================================================
# 231. EXPECTED IMPACT
# ============================================================

def calculate_expected_impact(
    gap: GapItem,
) -> float:
    """
    Calculate expected impact of enhancement.

    High relevance + high employability + high learning
    impact = high expected impact.
    """

    impact = (

        gap.industry_relevance_percentage
        * 0.35

        +

        gap.learning_impact_percentage
        * 0.25

        +

        gap.employability_impact_percentage
        * 0.30

        +

        gap.prerequisite_impact_percentage
        * 0.10

    )


    return round(

        min(
            100.0,
            impact,
        ),

        2,

    )


# ============================================================
# 232. BUILD ENHANCEMENT ITEM
# ============================================================

def build_enhancement_item(
    gap: GapItem,
    config: Optional[
        EnhancementConfig
    ] = None,
) -> EnhancementItem:
    """
    Convert a GapItem into a complete enhancement
    recommendation.
    """

    config = (
        config
        or EnhancementConfig()
    )


    module_name = recommend_module_name(
        gap
    )


    topics = recommend_topics_for_gap(
        gap
    )


    skills = recommend_skills_for_gap(
        gap
    )


    tools = recommend_tools_for_gap(
        gap
    )


    technologies = (
        recommend_technologies_for_gap(
            gap
        )
    )


    project = None


    if config.generate_projects:

        project = recommend_project_for_gap(
            gap
        )


    prerequisites = []


    if config.generate_prerequisites:

        prerequisites = (
            recommend_prerequisites(
                gap
            )
        )


    activities = (
        recommend_learning_activities(
            gap
        )
    )


    assessments = []


    if config.generate_assessment:

        assessments = recommend_assessments(
            gap
        )


    hours = estimate_enhancement_hours(

        gap,

        config,

    )


    effort = estimate_implementation_effort(
        gap
    )


    expected_impact = (
        calculate_expected_impact(
            gap
        )
    )


    priority = (
        enhancement_priority_from_gap(
            gap
        )
    )


    title = (

        f"Enhance {gap.name}"

    )


    description = (

        f"Address the {gap.severity.lower()}-priority "
        f"{gap_type_display_name(gap.gap_type).lower()} "
        f"gap '{gap.name}' through structured learning, "
        "hands-on practice, and assessment."

    )


    rationale = (

        f"This enhancement addresses a {gap.severity.lower()} "
        f"gap with priority score {gap.priority_score:.1f}/100. "
        f"Industry relevance is "
        f"{gap.industry_relevance_percentage:.1f}/100 "
        f"and employability impact is "
        f"{gap.employability_impact_percentage:.1f}/100."

    )


    return EnhancementItem(

        enhancement_id=generate_enhancement_id(

            gap.gap_type,

            title,

        ),

        enhancement_type=enhancement_type_for_gap(
            gap
        ),

        title=title,

        description=description,

        priority=priority,

        priority_score=gap.priority_score,

        target_gap_id=gap.gap_id,

        target_gap_type=gap.gap_type,

        target_gap_name=gap.name,

        recommended_module=module_name,

        recommended_topics=topics,

        recommended_concepts=[

            gap.name

        ],

        recommended_skills=skills,

        recommended_tools=tools,

        recommended_technologies=technologies,

        recommended_project=project,

        prerequisites=prerequisites,

        learning_activities=activities,

        assessment_methods=assessments,

        estimated_hours=hours,

        industry_relevance=(

            gap.industry_relevance_percentage

        ),

        employability_impact=(

            gap.employability_impact_percentage

        ),

        implementation_effort=effort,

        expected_impact=expected_impact,

        rationale=rationale,

        metadata={

            "source_gap_priority":
                gap.priority_score,

            "source_gap_severity":
                gap.severity,

        },

    )


# ============================================================
# 233. ENHANCEMENT TYPE FOR GAP
# ============================================================

def enhancement_type_for_gap(
    gap: GapItem,
) -> str:
    """
    Map gap type to enhancement type.
    """

    mapping = {

        GAP_MODULE:
            ENHANCEMENT_MODULE,

        GAP_TOPIC:
            ENHANCEMENT_TOPIC,

        GAP_CONCEPT:
            ENHANCEMENT_CONCEPT,

        GAP_SKILL:
            ENHANCEMENT_SKILL,

        GAP_TOOL:
            ENHANCEMENT_TOOL,

        GAP_TECHNOLOGY:
            ENHANCEMENT_TECHNOLOGY,

        GAP_PROJECT:
            ENHANCEMENT_PROJECT,

        GAP_COURSE_OUTCOME:
            ENHANCEMENT_OUTCOME,

        GAP_PROGRAM_OUTCOME:
            ENHANCEMENT_OUTCOME,

        GAP_PSO:
            ENHANCEMENT_OUTCOME,

    }


    return mapping.get(

        gap.gap_type,

        ENHANCEMENT_CONCEPT,

    )


# ============================================================
# 234. SORT ENHANCEMENTS
# ============================================================

def sort_enhancements(
    enhancements: Sequence[
        EnhancementItem
    ],
) -> List[
    EnhancementItem
]:
    """
    Sort by expected impact and priority.
    """

    priority_order = {

        ENHANCEMENT_PRIORITY_CRITICAL:
            4,

        ENHANCEMENT_PRIORITY_HIGH:
            3,

        ENHANCEMENT_PRIORITY_MEDIUM:
            2,

        ENHANCEMENT_PRIORITY_LOW:
            1,

    }


    return sorted(

        list(
            enhancements
        ),

        key=lambda item: (

            priority_order.get(

                item.priority,

                0,

            ),

            item.expected_impact,

            item.priority_score,

        ),

        reverse=True,

    )


# ============================================================
# 235. BUILD ENHANCEMENT PLAN
# ============================================================

def build_enhancement_plan(
    gap_analysis: GapAnalysisResult,
    curriculum_title: str = "Curriculum",
    config: Optional[
        EnhancementConfig
    ] = None,
) -> EnhancementPlan:
    """
    Generate complete enhancement roadmap from gap analysis.
    """

    config = (
        config
        or EnhancementConfig()
    )


    gaps = list(

        gap_analysis.gaps

    )


    if not config.include_low_priority:

        gaps = [

            gap

            for gap
            in gaps

            if gap.severity
            !=
            GAP_LOW

        ]


    # --------------------------------------------------------
    # Limit recommendations
    # --------------------------------------------------------

    gaps = gaps[
        :max(
            1,
            config.maximum_recommendations,
        )
    ]


    enhancements = [

        build_enhancement_item(

            gap,

            config,

        )

        for gap
        in gaps

    ]


    enhancements = sort_enhancements(
        enhancements
    )


    # --------------------------------------------------------
    # Counts
    # --------------------------------------------------------

    critical = sum(

        1

        for item
        in enhancements

        if item.priority
        ==
        ENHANCEMENT_PRIORITY_CRITICAL

    )


    high = sum(

        1

        for item
        in enhancements

        if item.priority
        ==
        ENHANCEMENT_PRIORITY_HIGH

    )


    medium = sum(

        1

        for item
        in enhancements

        if item.priority
        ==
        ENHANCEMENT_PRIORITY_MEDIUM

    )


    low = sum(

        1

        for item
        in enhancements

        if item.priority
        ==
        ENHANCEMENT_PRIORITY_LOW

    )


    # --------------------------------------------------------
    # Total hours
    # --------------------------------------------------------

    total_hours = sum(

        item.estimated_hours

        for item
        in enhancements

    )


    # --------------------------------------------------------
    # Average impact
    # --------------------------------------------------------

    if enhancements:

        impact = (

            sum(

                item.expected_impact

                for item
                in enhancements

            )

            /

            len(
                enhancements
            )

        )

    else:

        impact = 0.0


    # --------------------------------------------------------
    # Implementation phases
    # --------------------------------------------------------

    phase_1 = [

        item

        for item
        in enhancements

        if item.priority
        ==
        ENHANCEMENT_PRIORITY_CRITICAL

    ]


    phase_2 = [

        item

        for item
        in enhancements

        if item.priority
        ==
        ENHANCEMENT_PRIORITY_HIGH

    ]


    phase_3 = [

        item

        for item
        in enhancements

        if item.priority
        in [

            ENHANCEMENT_PRIORITY_MEDIUM,

            ENHANCEMENT_PRIORITY_LOW,

        ]

    ]


    strategic_recommendations = []


    if critical:

        strategic_recommendations.append(

            (
                f"Phase 1 should address {critical} "
                "critical enhancement(s)."
            )

        )


    if high:

        strategic_recommendations.append(

            (
                f"Phase 2 should address {high} "
                "high-priority enhancement(s)."
            )

        )


    if total_hours > 100:

        strategic_recommendations.append(

            (
                "The enhancement roadmap exceeds 100 "
                "hours. Consider phased curriculum redesign "
                "rather than adding all content at once."
            )

        )


    if impact >= 80:

        strategic_recommendations.append(

            (
                "The proposed enhancements have high "
                "expected industry and employability impact."
            )

        )


    return EnhancementPlan(

        curriculum_title=curriculum_title,

        total_enhancements=len(
            enhancements
        ),

        critical_enhancements=critical,

        high_enhancements=high,

        medium_enhancements=medium,

        low_enhancements=low,

        estimated_total_hours=round(
            total_hours,
            1,
        ),

        estimated_impact_score=round(
            impact,
            2,
        ),

        enhancements=enhancements,

        phase_1_immediate=phase_1,

        phase_2_short_term=phase_2,

        phase_3_medium_term=phase_3,

        strategic_recommendations=(
            strategic_recommendations
        ),

    )


# ============================================================
# 236. ONE-STEP ENHANCEMENT ANALYSIS
# ============================================================

def generate_enhancement_plan(
    comparison: CurriculumComparison,
    source: Any = None,
    target: Any = None,
    semantic_config: Optional[
        SemanticConfig
    ] = None,
    gap_weights: Optional[
        Dict[str, float]
    ] = None,
    enhancement_config: Optional[
        EnhancementConfig
    ] = None,
) -> EnhancementPlan:
    """
    Convenience API.

    Performs:

        Comparison
          ↓
        Gap analysis
          ↓
        Prioritization
          ↓
        Enhancement recommendations
    """

    gap_analysis = analyze_curriculum_gaps(

        comparison,

        source=source,

        target=target,

        semantic_config=semantic_config,

        gap_weights=gap_weights,

    )


    title = comparison.target_title


    return build_enhancement_plan(

        gap_analysis,

        curriculum_title=title,

        config=enhancement_config,

    )


# ============================================================
# 237. ENHANCEMENT ITEM TO DICT
# ============================================================

def enhancement_item_to_dict(
    item: EnhancementItem,
) -> Dict[str, Any]:
    """
    Serialize EnhancementItem.
    """

    return {

        "enhancement_id":
            item.enhancement_id,

        "enhancement_type":
            item.enhancement_type,

        "title":
            item.title,

        "description":
            item.description,

        "priority":
            item.priority,

        "priority_score":
            item.priority_score,

        "target_gap_id":
            item.target_gap_id,

        "target_gap_type":
            item.target_gap_type,

        "target_gap_name":
            item.target_gap_name,

        "recommended_module":
            item.recommended_module,

        "recommended_topics":
            list(
                item.recommended_topics
            ),

        "recommended_concepts":
            list(
                item.recommended_concepts
            ),

        "recommended_skills":
            list(
                item.recommended_skills
            ),

        "recommended_tools":
            list(
                item.recommended_tools
            ),

        "recommended_technologies":
            list(
                item.recommended_technologies
            ),

        "recommended_project":
            item.recommended_project,

        "prerequisites":
            list(
                item.prerequisites
            ),

        "learning_activities":
            list(
                item.learning_activities
            ),

        "assessment_methods":
            list(
                item.assessment_methods
            ),

        "estimated_hours":
            item.estimated_hours,

        "industry_relevance":
            item.industry_relevance,

        "employability_impact":
            item.employability_impact,

        "implementation_effort":
            item.implementation_effort,

        "expected_impact":
            item.expected_impact,

        "rationale":
            item.rationale,

        "metadata":
            dict(
                item.metadata
            ),

    }


# ============================================================
# 238. ENHANCEMENT PLAN TO DICT
# ============================================================

def enhancement_plan_to_dict(
    plan: EnhancementPlan,
) -> Dict[str, Any]:
    """
    Serialize EnhancementPlan.
    """

    return {

        "curriculum_title":
            plan.curriculum_title,

        "total_enhancements":
            plan.total_enhancements,

        "critical_enhancements":
            plan.critical_enhancements,

        "high_enhancements":
            plan.high_enhancements,

        "medium_enhancements":
            plan.medium_enhancements,

        "low_enhancements":
            plan.low_enhancements,

        "estimated_total_hours":
            plan.estimated_total_hours,

        "estimated_impact_score":
            plan.estimated_impact_score,

        "enhancements": [

            enhancement_item_to_dict(
                item
            )

            for item
            in plan.enhancements

        ],

        "phase_1_immediate": [

            enhancement_item_to_dict(
                item
            )

            for item
            in plan.phase_1_immediate

        ],

        "phase_2_short_term": [

            enhancement_item_to_dict(
                item
            )

            for item
            in plan.phase_2_short_term

        ],

        "phase_3_medium_term": [

            enhancement_item_to_dict(
                item
            )

            for item
            in plan.phase_3_medium_term

        ],

        "strategic_recommendations":
            list(
                plan.strategic_recommendations
            ),

    }


# ============================================================
# 239. GET IMMEDIATE ENHANCEMENTS
# ============================================================

def get_immediate_enhancements(
    plan: EnhancementPlan,
) -> List[
    EnhancementItem
]:
    """
    Return critical enhancements.
    """

    return list(
        plan.phase_1_immediate
    )


# ============================================================
# 240. GET HIGH PRIORITY ENHANCEMENTS
# ============================================================

def get_high_priority_enhancements(
    plan: EnhancementPlan,
) -> List[
    EnhancementItem
]:
    """
    Return high-priority enhancements.
    """

    return list(
        plan.phase_2_short_term
    )


# ============================================================
# 241. GET PROJECT ENHANCEMENTS
# ============================================================

def get_project_enhancements(
    plan: EnhancementPlan,
) -> List[
    EnhancementItem
]:
    """
    Return project-oriented recommendations.
    """

    return [

        item

        for item
        in plan.enhancements

        if item.enhancement_type
        ==
        ENHANCEMENT_PROJECT

        or
        item.recommended_project

    ]


# ============================================================
# 242. GET TECHNOLOGY ENHANCEMENTS
# ============================================================

def get_technology_enhancements(
    plan: EnhancementPlan,
) -> List[
    EnhancementItem
]:
    """
    Return technology-oriented recommendations.
    """

    return [

        item

        for item
        in plan.enhancements

        if item.enhancement_type
        ==
        ENHANCEMENT_TECHNOLOGY

    ]


# ============================================================
# 243. GET SKILL ENHANCEMENTS
# ============================================================

def get_skill_enhancements(
    plan: EnhancementPlan,
) -> List[
    EnhancementItem
]:
    """
    Return skill-oriented recommendations.
    """

    return [

        item

        for item
        in plan.enhancements

        if item.enhancement_type
        ==
        ENHANCEMENT_SKILL

    ]


# ============================================================
# 244. END OF CHUNK 9
# ============================================================
# ============================================================
# curriculum/comparator.py
# CHUNK 10/10
#
# REPORT / DASHBOARD / EXPORT / VALIDATION / PUBLIC API
#
# This is the FINAL chunk of comparator.py
#
# Pipeline:
#
# Curriculum A
#      │
# Curriculum B
#      │
#      ▼
# Comparison
#      │
#      ├── Similarity
#      ├── Coverage
#      ├── Missing Items
#      ├── Extra Items
#      ├── Maturity
#      ├── Gap Analysis
#      └── Enhancement Plan
#               │
#               ▼
#       Dashboard / Reports
# ============================================================


# ============================================================
# 245. COMPARISON DASHBOARD DATA
# ============================================================

def build_comparison_dashboard_data(
    comparison: CurriculumComparison,
    source: Any = None,
    target: Any = None,
    maturity_comparison: Optional[
        Dict[str, Any]
    ] = None,
    gap_analysis: Optional[
        GapAnalysisResult
    ] = None,
    enhancement_plan: Optional[
        EnhancementPlan
    ] = None,
) -> Dict[str, Any]:
    """
    Build a report/dashboard-friendly dictionary.

    Designed for Streamlit, Plotly, Pandas,
    JSON APIs and reporting modules.
    """

    data = {

        "source_title":
            comparison.source_title,

        "target_title":
            comparison.target_title,

        "overall_similarity":
            comparison.overall_similarity_percentage,

        "category_scores": {},

        "maturity": None,

        "gap_summary": None,

        "enhancement_summary": None,

    }


    # --------------------------------------------------------
    # Category scores
    # --------------------------------------------------------

    category_mapping = {

        "Modules":
            comparison.module_comparison,

        "Topics":
            comparison.topic_comparison,

        "Concepts":
            comparison.concept_comparison,

        "Skills":
            comparison.skill_comparison,

        "Tools":
            comparison.tool_comparison,

        "Technologies":
            comparison.technology_comparison,

        "Projects":
            comparison.project_comparison,

        "Course Outcomes":
            comparison.course_outcome_comparison,

        "Program Outcomes":
            comparison.program_outcome_comparison,

        "PSOs":
            comparison.pso_comparison,

    }


    for name, result in category_mapping.items():

        if result is None:

            data[
                "category_scores"
            ][name] = {

                "coverage": 0.0,

                "similarity": 0.0,

                "source_count": 0,

                "target_count": 0,

                "matched_count": 0,

                "missing_count": 0,

                "extra_count": 0,

            }

            continue


        data[
            "category_scores"
        ][name] = {

            "coverage":
                round(

                    safe_float(
                        result.coverage_percentage
                    ),

                    2,

                ),

            "similarity":
                round(

                    safe_float(
                        result.similarity_percentage
                    ),

                    2,

                ),

            "source_count":
                result.source_count,

            "target_count":
                result.target_count,

            "matched_count":
                result.matched_count,

            "missing_count":
                len(
                    result.missing
                ),

            "extra_count":
                len(
                    result.extra
                ),

        }


    # --------------------------------------------------------
    # Maturity
    # --------------------------------------------------------

    if maturity_comparison is not None:

        data[
            "maturity"
        ] = maturity_comparison_to_dict(

            maturity_comparison

        )


    # --------------------------------------------------------
    # Gap summary
    # --------------------------------------------------------

    if gap_analysis is not None:

        data[
            "gap_summary"
        ] = gap_analysis_to_dict(

            gap_analysis

        )[
            "summary"
        ]


    # --------------------------------------------------------
    # Enhancement summary
    # --------------------------------------------------------

    if enhancement_plan is not None:

        data[
            "enhancement_summary"
        ] = {

            "total":
                enhancement_plan.total_enhancements,

            "critical":
                enhancement_plan.critical_enhancements,

            "high":
                enhancement_plan.high_enhancements,

            "medium":
                enhancement_plan.medium_enhancements,

            "low":
                enhancement_plan.low_enhancements,

            "estimated_hours":
                enhancement_plan.estimated_total_hours,

            "expected_impact":
                enhancement_plan.estimated_impact_score,

        }


    return data


# ============================================================
# 246. CATEGORY RADAR DATA
# ============================================================

def build_category_radar_data(
    comparison: CurriculumComparison,
) -> Dict[str, List[float]]:
    """
    Build values suitable for radar charts.

    Returns source and target values across major
    curriculum dimensions.
    """

    categories = [

        (
            "Modules",
            comparison.module_comparison,
        ),

        (
            "Topics",
            comparison.topic_comparison,
        ),

        (
            "Concepts",
            comparison.concept_comparison,
        ),

        (
            "Skills",
            comparison.skill_comparison,
        ),

        (
            "Technologies",
            comparison.technology_comparison,
        ),

        (
            "Tools",
            comparison.tool_comparison,
        ),

        (
            "Projects",
            comparison.project_comparison,
        ),

    ]


    labels = []

    source_values = []

    target_values = []


    for label, result in categories:

        labels.append(
            label
        )


        if result is None:

            source_values.append(
                0.0
            )

            target_values.append(
                0.0
            )

            continue


        # Coverage is based on source curriculum
        # being represented in target.
        source_values.append(
            100.0
        )


        target_values.append(

            normalize_score(

                result.coverage_percentage

            )

        )


    return {

        "categories":
            labels,

        "source":
            source_values,

        "target":
            target_values,

    }


# ============================================================
# 247. CATEGORY BAR DATA
# ============================================================

def build_category_bar_data(
    comparison: CurriculumComparison,
) -> List[Dict[str, Any]]:
    """
    Build flat records for bar charts / DataFrames.
    """

    records = []


    categories = {

        "Modules":
            comparison.module_comparison,

        "Topics":
            comparison.topic_comparison,

        "Concepts":
            comparison.concept_comparison,

        "Skills":
            comparison.skill_comparison,

        "Tools":
            comparison.tool_comparison,

        "Technologies":
            comparison.technology_comparison,

        "Projects":
            comparison.project_comparison,

        "Course Outcomes":
            comparison.course_outcome_comparison,

        "Program Outcomes":
            comparison.program_outcome_comparison,

        "PSOs":
            comparison.pso_comparison,

    }


    for category, result in categories.items():

        if result is None:

            records.append({

                "category":
                    category,

                "coverage":
                    0.0,

                "similarity":
                    0.0,

                "missing":
                    0,

                "extra":
                    0,

                "source_count":
                    0,

                "target_count":
                    0,

            })

            continue


        records.append({

            "category":
                category,

            "coverage":
                round(

                    safe_float(
                        result.coverage_percentage
                    ),

                    2,

                ),

            "similarity":
                round(

                    safe_float(
                        result.similarity_percentage
                    ),

                    2,

                ),

            "missing":
                len(
                    result.missing
                ),

            "extra":
                len(
                    result.extra
                ),

            "source_count":
                result.source_count,

            "target_count":
                result.target_count,

        })


    return records


# ============================================================
# 248. GAP CHART DATA
# ============================================================

def build_gap_chart_data(
    analysis: GapAnalysisResult,
) -> List[Dict[str, Any]]:
    """
    Build gap records for visualizations.
    """

    records = []


    for gap in analysis.gaps:

        records.append({

            "rank":
                gap.priority_rank,

            "gap":
                gap.name,

            "type":
                gap_type_display_name(
                    gap.gap_type
                ),

            "severity":
                gap.severity,

            "priority_score":
                gap.priority_score,

            "industry_relevance":
                gap.industry_relevance_percentage,

            "learning_impact":
                gap.learning_impact_percentage,

            "employability_impact":
                gap.employability_impact_percentage,

            "prerequisite_impact":
                gap.prerequisite_impact_percentage,

            "estimated_action":
                gap.recommended_action,

        })


    return records


# ============================================================
# 249. ENHANCEMENT CHART DATA
# ============================================================

def build_enhancement_chart_data(
    plan: EnhancementPlan,
) -> List[Dict[str, Any]]:
    """
    Build enhancement records for dashboard/reporting.
    """

    records = []


    for item in plan.enhancements:

        records.append({

            "rank":
                len(records) + 1,

            "title":
                item.title,

            "type":
                item.enhancement_type,

            "priority":
                item.priority,

            "priority_score":
                item.priority_score,

            "expected_impact":
                item.expected_impact,

            "industry_relevance":
                item.industry_relevance,

            "employability_impact":
                item.employability_impact,

            "implementation_effort":
                item.implementation_effort,

            "estimated_hours":
                item.estimated_hours,

            "recommended_module":
                item.recommended_module,

            "project":
                item.recommended_project,

        })


    return records


# ============================================================
# 250. EXECUTIVE SUMMARY
# ============================================================

def generate_executive_summary(
    comparison: CurriculumComparison,
    maturity: Optional[
        Dict[str, Any]
    ] = None,
    gap_analysis: Optional[
        GapAnalysisResult
    ] = None,
    enhancement_plan: Optional[
        EnhancementPlan
    ] = None,
) -> str:
    """
    Generate concise executive summary.
    """

    source_title = (
        comparison.source_title
        or
        "Reference Curriculum"
    )


    target_title = (
        comparison.target_title
        or
        "Target Curriculum"
    )


    similarity = (
        comparison.overall_similarity_percentage
    )


    lines = []


    lines.append(

        (
            f"The comparison between "
            f"'{source_title}' and "
            f"'{target_title}' shows an overall "
            f"curriculum similarity of "
            f"{similarity:.1f}%."
        )

    )


    if maturity is not None:

        source_maturity = maturity.get(
            "source",
            {},
        )


        target_maturity = maturity.get(
            "target",
            {},
        )


        if isinstance(
            source_maturity,
            CurriculumMaturityScore,
        ):

            source_score = (
                source_maturity.overall_score
            )

            source_level = (
                source_maturity.maturity_level
            )

        else:

            source_score = safe_float(

                source_maturity.get(
                    "overall_score",
                    0.0,
                )

            )

            source_level = (
                source_maturity.get(
                    "maturity_level",
                    "Unknown",
                )
            )


        if isinstance(
            target_maturity,
            CurriculumMaturityScore,
        ):

            target_score = (
                target_maturity.overall_score
            )

            target_level = (
                target_maturity.maturity_level
            )

        else:

            target_score = safe_float(

                target_maturity.get(
                    "overall_score",
                    0.0,
                )

            )

            target_level = (
                target_maturity.get(
                    "maturity_level",
                    "Unknown",
                )
            )


        lines.append(

            (
                f"The reference curriculum has a "
                f"maturity score of {source_score:.1f}/100 "
                f"({source_level}), while the target curriculum "
                f"has {target_score:.1f}/100 "
                f"({target_level})."
            )

        )


    if gap_analysis is not None:

        summary = gap_analysis.summary


        if summary is not None:

            lines.append(

                (
                    f"The analysis identifies "
                    f"{summary.total_gaps} total gaps, "
                    f"including {summary.critical_gaps} critical "
                    f"and {summary.high_gaps} high-priority gaps."
                )

            )


    if enhancement_plan is not None:

        lines.append(

            (
                f"The recommended enhancement roadmap contains "
                f"{enhancement_plan.total_enhancements} actions "
                f"requiring approximately "
                f"{enhancement_plan.estimated_total_hours:.0f} "
                f"instructional hours."
            )

        )


        if (
            enhancement_plan.estimated_impact_score
            >=
            80
        ):

            lines.append(

                (
                    "The recommended changes are expected to "
                    "have strong industry and employability impact."
                )

            )


    return " ".join(
        lines
    )


# ============================================================
# 251. TOP STRENGTHS
# ============================================================

def extract_top_strengths(
    comparison: CurriculumComparison,
    limit: int = 5,
) -> List[str]:
    """
    Identify categories where target coverage is strong.
    """

    records = build_category_bar_data(
        comparison
    )


    records = sorted(

        records,

        key=lambda item: (

            item[
                "coverage"
            ],

            item[
                "similarity"
            ],

        ),

        reverse=True,

    )


    strengths = []


    for record in records:

        coverage = record[
            "coverage"
        ]


        if coverage < 70:

            continue


        strengths.append(

            (
                f"{record['category']} coverage is "
                f"{coverage:.1f}%."
            )

        )


        if len(strengths) >= limit:

            break


    return strengths


# ============================================================
# 252. TOP WEAKNESSES
# ============================================================

def extract_top_weaknesses(
    comparison: CurriculumComparison,
    limit: int = 5,
) -> List[str]:
    """
    Identify categories with weak target coverage.
    """

    records = build_category_bar_data(
        comparison
    )


    records = sorted(

        records,

        key=lambda item: (

            item[
                "coverage"
            ],

            item[
                "similarity"
            ],

        ),

    )


    weaknesses = []


    for record in records:

        coverage = record[
            "coverage"
        ]


        if coverage >= 70:

            continue


        weaknesses.append(

            (
                f"{record['category']} coverage is "
                f"only {coverage:.1f}%, with "
                f"{record['missing']} missing item(s)."
            )

        )


        if len(weaknesses) >= limit:

            break


    return weaknesses


# ============================================================
# 253. FULL ANALYSIS PIPELINE
# ============================================================

def run_full_curriculum_analysis(
    source: Any,
    target: Any,
    semantic_config: Optional[
        SemanticConfig
    ] = None,
    scoring_config: Optional[
        IndustryScoringConfig
    ] = None,
    enhancement_config: Optional[
        EnhancementConfig
    ] = None,
    gap_weights: Optional[
        Dict[str, float]
    ] = None,
) -> Dict[str, Any]:
    """
    Run the complete curriculum intelligence pipeline.

    Steps:

        1. Compare curricula
        2. Calculate maturity
        3. Detect and prioritize gaps
        4. Generate enhancements
        5. Build dashboard data
        6. Generate executive summary
    """

    # --------------------------------------------------------
    # 1. Curriculum comparison
    # --------------------------------------------------------

    comparison = compare_curriculums(

        source,

        target,

        semantic_config=semantic_config,

    )


    # --------------------------------------------------------
    # 2. Maturity
    # --------------------------------------------------------

    maturity = compare_curriculum_maturity(

        source,

        target,

        scoring_config=scoring_config,

    )


    # --------------------------------------------------------
    # 3. Gap analysis
    # --------------------------------------------------------

    gap_analysis = analyze_curriculum_gaps(

        comparison,

        source=source,

        target=target,

        semantic_config=semantic_config,

        gap_weights=gap_weights,

    )


    # --------------------------------------------------------
    # 4. Enhancement plan
    # --------------------------------------------------------

    enhancement_plan = build_enhancement_plan(

        gap_analysis,

        curriculum_title=(
            comparison.target_title
            or
            "Target Curriculum"
        ),

        config=enhancement_config,

    )


    # --------------------------------------------------------
    # 5. Dashboard data
    # --------------------------------------------------------

    dashboard = (
        build_comparison_dashboard_data(

            comparison,

            source=source,

            target=target,

            maturity_comparison=maturity,

            gap_analysis=gap_analysis,

            enhancement_plan=enhancement_plan,

        )
    )


    # --------------------------------------------------------
    # 6. Executive summary
    # --------------------------------------------------------

    summary = generate_executive_summary(

        comparison,

        maturity=maturity,

        gap_analysis=gap_analysis,

        enhancement_plan=enhancement_plan,

    )


    return {

        "comparison":
            comparison,

        "maturity":
            maturity,

        "gap_analysis":
            gap_analysis,

        "enhancement_plan":
            enhancement_plan,

        "dashboard":
            dashboard,

        "executive_summary":
            summary,

        "strengths":
            extract_top_strengths(
                comparison
            ),

        "weaknesses":
            extract_top_weaknesses(
                comparison
            ),

        "radar_data":
            build_category_radar_data(
                comparison
            ),

        "category_data":
            build_category_bar_data(
                comparison
            ),

        "gap_chart_data":
            build_gap_chart_data(
                gap_analysis
            ),

        "enhancement_chart_data":
            build_enhancement_chart_data(
                enhancement_plan
            ),

    }


# ============================================================
# 254. SERIALIZE FULL ANALYSIS
# ============================================================

def serialize_full_curriculum_analysis(
    analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert the result of run_full_curriculum_analysis()
    into JSON-compatible dictionaries.
    """

    comparison = analysis.get(
        "comparison"
    )


    maturity = analysis.get(
        "maturity"
    )


    gap_analysis = analysis.get(
        "gap_analysis"
    )


    enhancement_plan = analysis.get(
        "enhancement_plan"
    )


    result = {

        "executive_summary":
            analysis.get(
                "executive_summary",
                "",
            ),

        "strengths":
            list(
                analysis.get(
                    "strengths",
                    [],
                )
            ),

        "weaknesses":
            list(
                analysis.get(
                    "weaknesses",
                    [],
                )
            ),

        "dashboard":
            analysis.get(
                "dashboard",
                {},
            ),

        "radar_data":
            analysis.get(
                "radar_data",
                {},
            ),

        "category_data":
            analysis.get(
                "category_data",
                [],
            ),

        "gap_chart_data":
            analysis.get(
                "gap_chart_data",
                [],
            ),

        "enhancement_chart_data":
            analysis.get(
                "enhancement_chart_data",
                [],
            ),

    }


    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    if comparison is not None:

        result[
            "comparison"
        ] = curriculum_comparison_to_dict(
            comparison
        )


    # --------------------------------------------------------
    # Maturity
    # --------------------------------------------------------

    if maturity is not None:

        result[
            "maturity"
        ] = maturity_comparison_to_dict(
            maturity
        )


    # --------------------------------------------------------
    # Gaps
    # --------------------------------------------------------

    if gap_analysis is not None:

        result[
            "gap_analysis"
        ] = gap_analysis_to_dict(
            gap_analysis
        )


    # --------------------------------------------------------
    # Enhancements
    # --------------------------------------------------------

    if enhancement_plan is not None:

        result[
            "enhancement_plan"
        ] = enhancement_plan_to_dict(
            enhancement_plan
        )


    return result


# ============================================================
# 255. JSON STRING EXPORT
# ============================================================

def analysis_to_json(
    analysis: Dict[str, Any],
    indent: int = 2,
) -> str:
    """
    Convert full analysis to JSON string.
    """

    serialized = (
        serialize_full_curriculum_analysis(
            analysis
        )
    )


    return json.dumps(

        serialized,

        indent=indent,

        ensure_ascii=False,

        default=str,

    )


# ============================================================
# 256. SAVE ANALYSIS JSON
# ============================================================

def save_analysis_json(
    analysis: Dict[str, Any],
    file_path: Union[
        str,
        Path,
    ],
    indent: int = 2,
) -> Path:
    """
    Save analysis to JSON file.
    """

    path = Path(
        file_path
    )


    path.parent.mkdir(

        parents=True,

        exist_ok=True,

    )


    path.write_text(

        analysis_to_json(

            analysis,

            indent=indent,

        ),

        encoding="utf-8",

    )


    return path


# ============================================================
# 257. LOAD ANALYSIS JSON
# ============================================================

def load_analysis_json(
    file_path: Union[
        str,
        Path,
    ],
) -> Dict[str, Any]:
    """
    Load previously exported analysis JSON.
    """

    path = Path(
        file_path
    )


    if not path.exists():

        raise FileNotFoundError(

            f"Analysis file not found: {path}"

        )


    text = path.read_text(

        encoding="utf-8"

    )


    return json.loads(
        text
    )


# ============================================================
# 258. VALIDATE COMPARISON
# ============================================================

def validate_curriculum_comparison(
    comparison: CurriculumComparison,
) -> List[str]:
    """
    Validate a CurriculumComparison object.

    Returns a list of validation errors.
    """

    errors = []


    if not isinstance(
        comparison,
        CurriculumComparison,
    ):

        errors.append(

            "Object is not a CurriculumComparison."

        )

        return errors


    if not comparison.source_title:

        errors.append(

            "Source curriculum title is missing."

        )


    if not comparison.target_title:

        errors.append(

            "Target curriculum title is missing."

        )


    similarity = safe_float(

        comparison.overall_similarity_percentage

    )


    if similarity < 0 or similarity > 100:

        errors.append(

            "Overall similarity must be between 0 and 100."

        )


    category_results = [

        comparison.module_comparison,

        comparison.topic_comparison,

        comparison.concept_comparison,

        comparison.skill_comparison,

        comparison.tool_comparison,

        comparison.technology_comparison,

        comparison.project_comparison,

        comparison.course_outcome_comparison,

        comparison.program_outcome_comparison,

        comparison.pso_comparison,

    ]


    for result in category_results:

        if result is None:

            continue


        coverage = safe_float(

            result.coverage_percentage

        )


        similarity_value = safe_float(

            result.similarity_percentage

        )


        if coverage < 0 or coverage > 100:

            errors.append(

                (
                    "Category coverage must be "
                    "between 0 and 100."
                )

            )


        if (
            similarity_value < 0
            or
            similarity_value > 100
        ):

            errors.append(

                (
                    "Category similarity must be "
                    "between 0 and 100."
                )

            )


    return errors


# ============================================================
# 259. VALIDATE GAP ANALYSIS
# ============================================================

def validate_gap_analysis(
    analysis: GapAnalysisResult,
) -> List[str]:
    """
    Validate gap analysis.
    """

    errors = []


    if not isinstance(
        analysis,
        GapAnalysisResult,
    ):

        return [

            "Object is not a GapAnalysisResult."

        ]


    for gap in analysis.gaps:

        if not gap.gap_id:

            errors.append(

                "Gap ID is missing."

            )


        if not gap.name:

            errors.append(

                f"Gap {gap.gap_id} has no name."

            )


        if gap.severity not in (

            GAP_CRITICAL,

            GAP_HIGH,

            GAP_MEDIUM,

            GAP_LOW,

        ):

            errors.append(

                (
                    f"Invalid severity for "
                    f"gap '{gap.name}'."
                )

            )


        if (
            gap.priority_score < 0
            or
            gap.priority_score > 100
        ):

            errors.append(

                (
                    f"Priority score for "
                    f"'{gap.name}' must be "
                    "between 0 and 100."
                )

            )


    return errors


# ============================================================
# 260. VALIDATE ENHANCEMENT PLAN
# ============================================================

def validate_enhancement_plan(
    plan: EnhancementPlan,
) -> List[str]:
    """
    Validate enhancement plan.
    """

    errors = []


    if not isinstance(
        plan,
        EnhancementPlan,
    ):

        return [

            "Object is not an EnhancementPlan."

        ]


    if plan.total_enhancements != len(

        plan.enhancements

    ):

        errors.append(

            (
                "total_enhancements does not "
                "match enhancements length."
            )

        )


    for item in plan.enhancements:

        if not item.enhancement_id:

            errors.append(

                "Enhancement ID is missing."

            )


        if not item.title:

            errors.append(

                "Enhancement title is missing."

            )


        if (
            item.priority_score < 0
            or
            item.priority_score > 100
        ):

            errors.append(

                (
                    f"Invalid priority score "
                    f"for '{item.title}'."
                )

            )


        if item.estimated_hours < 0:

            errors.append(

                (
                    f"Negative estimated hours "
                    f"for '{item.title}'."
                )

            )


    return errors


# ============================================================
# 261. FULL VALIDATION
# ============================================================

def validate_full_analysis(
    analysis: Dict[str, Any],
) -> Dict[str, List[str]]:
    """
    Validate every major result in a full analysis.
    """

    errors = {

        "comparison": [],

        "gap_analysis": [],

        "enhancement_plan": [],

    }


    comparison = analysis.get(
        "comparison"
    )


    if comparison is not None:

        errors[
            "comparison"
        ] = validate_curriculum_comparison(

            comparison

        )


    gap_analysis = analysis.get(
        "gap_analysis"
    )


    if gap_analysis is not None:

        errors[
            "gap_analysis"
        ] = validate_gap_analysis(

            gap_analysis

        )


    enhancement_plan = analysis.get(
        "enhancement_plan"
    )


    if enhancement_plan is not None:

        errors[
            "enhancement_plan"
        ] = validate_enhancement_plan(

            enhancement_plan

        )


    return errors


# ============================================================
# 262. HAS VALIDATION ERRORS
# ============================================================

def has_validation_errors(
    validation_result: Dict[
        str,
        List[str]
    ],
) -> bool:
    """
    Return True if any validation errors exist.
    """

    return any(

        bool(
            errors
        )

        for errors
        in validation_result.values()

    )


# ============================================================
# 263. COMPARISON QUICK SUMMARY
# ============================================================

def comparison_quick_summary(
    comparison: CurriculumComparison,
) -> Dict[str, Any]:
    """
    Return a compact summary suitable for cards.
    """

    category_data = build_category_bar_data(
        comparison
    )


    total_missing = sum(

        item[
            "missing"
        ]

        for item
        in category_data

    )


    total_extra = sum(

        item[
            "extra"
        ]

        for item
        in category_data

    )


    return {

        "source":
            comparison.source_title,

        "target":
            comparison.target_title,

        "similarity":
            comparison.overall_similarity_percentage,

        "total_missing":
            total_missing,

        "total_extra":
            total_extra,

        "categories":
            len(
                category_data
            ),

    }


# ============================================================
# 264. GAP QUICK SUMMARY
# ============================================================

def gap_quick_summary(
    analysis: GapAnalysisResult,
) -> Dict[str, Any]:
    """
    Return compact gap metrics.
    """

    summary = analysis.summary


    if summary is None:

        return {

            "total":
                0,

            "critical":
                0,

            "high":
                0,

            "medium":
                0,

            "low":
                0,

            "average_priority":
                0.0,

        }


    return {

        "total":
            summary.total_gaps,

        "critical":
            summary.critical_gaps,

        "high":
            summary.high_gaps,

        "medium":
            summary.medium_gaps,

        "low":
            summary.low_gaps,

        "average_priority":
            summary.average_priority_score,

        "coverage":
            summary.coverage_percentage,

    }


# ============================================================
# 265. ENHANCEMENT QUICK SUMMARY
# ============================================================

def enhancement_quick_summary(
    plan: EnhancementPlan,
) -> Dict[str, Any]:
    """
    Return compact enhancement metrics.
    """

    return {

        "total":
            plan.total_enhancements,

        "critical":
            plan.critical_enhancements,

        "high":
            plan.high_enhancements,

        "medium":
            plan.medium_enhancements,

        "low":
            plan.low_enhancements,

        "estimated_hours":
            plan.estimated_total_hours,

        "expected_impact":
            plan.estimated_impact_score,

    }


# ============================================================
# 266. PUBLIC API ALIASES
# ============================================================

# These aliases make the module easier to use from
# Streamlit pages and other application modules.


compare = compare_curriculums


compare_maturity = (
    compare_curriculum_maturity
)


analyze_gaps = (
    analyze_curriculum_gaps
)


build_enhancements = (
    build_enhancement_plan
)


full_analysis = (
    run_full_curriculum_analysis
)


export_json = (
    analysis_to_json
)


# ============================================================
# 267. MODULE CAPABILITIES
# ============================================================

COMPARATOR_CAPABILITIES = [

    "curriculum_comparison",

    "semantic_similarity",

    "category_coverage",

    "missing_item_detection",

    "extra_item_detection",

    "curriculum_maturity",

    "industry_alignment",

    "practical_learning_analysis",

    "employability_analysis",

    "technology_breadth_analysis",

    "emerging_technology_analysis",

    "gap_detection",

    "gap_severity",

    "gap_prioritization",

    "prerequisite_analysis",

    "enhancement_recommendations",

    "module_recommendations",

    "topic_recommendations",

    "skill_recommendations",

    "technology_lab_recommendations",

    "tool_recommendations",

    "project_recommendations",

    "assessment_recommendations",

    "learning_activity_recommendations",

    "implementation_roadmap",

    "dashboard_data",

    "chart_data",

    "executive_summary",

    "json_export",

    "analysis_validation",

]


# ============================================================
# 268. MODULE VERSION
# ============================================================

COMPARATOR_VERSION = "1.0.0"


# ============================================================
# 269. PUBLIC EXPORTS
# ============================================================

__all__ = [

    # --------------------------------------------------------
    # Core comparison
    # --------------------------------------------------------

    "compare_curriculums",

    "compare",

    "CurriculumComparison",

    "CategoryComparison",

    # --------------------------------------------------------
    # Semantic matching
    # --------------------------------------------------------

    "SemanticConfig",

    "semantic_similarity",

    "semantic_best_match",

    "canonical_similarity",

    # --------------------------------------------------------
    # Maturity
    # --------------------------------------------------------

    "IndustryScoringConfig",

    "CurriculumMaturityScore",

    "calculate_curriculum_maturity",

    "compare_curriculum_maturity",

    "compare_maturity",

    "calculate_industry_alignment",

    "practical_learning_score",

    "employability_score",

    "emerging_technology_score",

    "industry_technology_score",

    # --------------------------------------------------------
    # Gap analysis
    # --------------------------------------------------------

    "GapItem",

    "GapSummary",

    "GapAnalysisResult",

    "analyze_curriculum_gaps",

    "analyze_gaps",

    "calculate_gap_priority",

    "severity_from_score",

    "get_top_gaps",

    "get_critical_gaps",

    "get_high_priority_gaps",

    # --------------------------------------------------------
    # Enhancements
    # --------------------------------------------------------

    "EnhancementItem",

    "EnhancementPlan",

    "EnhancementConfig",

    "build_enhancement_plan",

    "build_enhancements",

    "generate_enhancement_plan",

    "get_immediate_enhancements",

    "get_high_priority_enhancements",

    "get_project_enhancements",

    "get_technology_enhancements",

    "get_skill_enhancements",

    # --------------------------------------------------------
    # Reporting
    # --------------------------------------------------------

    "build_comparison_dashboard_data",

    "build_category_radar_data",

    "build_category_bar_data",

    "build_gap_chart_data",

    "build_enhancement_chart_data",

    "generate_executive_summary",

    "extract_top_strengths",

    "extract_top_weaknesses",

    # --------------------------------------------------------
    # Full pipeline
    # --------------------------------------------------------

    "run_full_curriculum_analysis",

    "full_analysis",

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    "curriculum_comparison_to_dict",

    "maturity_score_to_dict",

    "maturity_comparison_to_dict",

    "gap_item_to_dict",

    "gap_summary_to_dict",

    "gap_analysis_to_dict",

    "enhancement_item_to_dict",

    "enhancement_plan_to_dict",

    "serialize_full_curriculum_analysis",

    "analysis_to_json",

    "export_json",

    "save_analysis_json",

    "load_analysis_json",

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    "validate_curriculum_comparison",

    "validate_gap_analysis",

    "validate_enhancement_plan",

    "validate_full_analysis",

    "has_validation_errors",

    # --------------------------------------------------------
    # Quick summaries
    # --------------------------------------------------------

    "comparison_quick_summary",

    "gap_quick_summary",

    "enhancement_quick_summary",

    # --------------------------------------------------------
    # Constants
    # --------------------------------------------------------

    "GAP_CRITICAL",

    "GAP_HIGH",

    "GAP_MEDIUM",

    "GAP_LOW",

    "GAP_MODULE",

    "GAP_TOPIC",

    "GAP_CONCEPT",

    "GAP_SKILL",

    "GAP_TOOL",

    "GAP_TECHNOLOGY",

    "GAP_PROJECT",

    "GAP_COURSE_OUTCOME",

    "GAP_PROGRAM_OUTCOME",

    "GAP_PSO",

    "COMPARATOR_CAPABILITIES",

    "COMPARATOR_VERSION",

]


# ============================================================
# 270. END OF FILE
# ============================================================
