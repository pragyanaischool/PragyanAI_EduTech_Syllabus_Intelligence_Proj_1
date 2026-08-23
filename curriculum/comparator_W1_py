# ============================================================
# curriculum/comparator.py
# ============================================================
#
# PragyanAI Curriculum Intelligence
#
# Curriculum-to-Curriculum and
# Curriculum-to-Industry comparison.
#
# ============================================================

from __future__ import annotations

import logging
import re

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set


logger = logging.getLogger(
    "pragyanai.curriculum.comparator"
)


# ============================================================
# RESULT MODELS
# ============================================================

@dataclass
class ComparisonItem:

    name: str

    category: str = ""

    status: str = ""

    score: float = 0.0

    source: str = ""

    target: str = ""

    notes: str = ""


@dataclass
class ComparisonResult:

    overall_score: float = 0.0

    matching_items: List[
        ComparisonItem
    ] = field(
        default_factory=list
    )

    missing_items: List[
        ComparisonItem
    ] = field(
        default_factory=list
    )

    partial_items: List[
        ComparisonItem
    ] = field(
        default_factory=list
    )

    extra_items: List[
        ComparisonItem
    ] = field(
        default_factory=list
    )

    recommendations: List[
        str
    ] = field(
        default_factory=list
    )

    statistics: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(
    value: Any,
) -> str:

    if value is None:

        return ""

    value = str(
        value
    ).strip().lower()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def normalize_list(
    values: Any,
) -> List[str]:

    if values is None:

        return []

    if isinstance(
        values,
        str,
    ):

        values = [
            values
        ]

    if not isinstance(
        values,
        (list, tuple, set),
    ):

        return []

    result = []

    for value in values:

        text = normalize_text(
            value
        )

        if text:

            result.append(
                text
            )

    return list(
        dict.fromkeys(
            result
        )
    )


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/7
#
# CURRICULUM FIELD EXTRACTION
# ============================================================


def model_to_dict(
    obj: Any,
) -> Dict[str, Any]:

    if obj is None:

        return {}

    if isinstance(
        obj,
        dict,
    ):

        return obj

    if hasattr(
        obj,
        "model_dump",
    ):

        try:

            return obj.model_dump(
                mode="python"
            )

        except Exception:

            pass

    if hasattr(
        obj,
        "dict",
    ):

        try:

            return obj.dict()

        except Exception:

            pass

    try:

        return vars(
            obj
        )

    except Exception:

        return {}


def extract_field(
    curriculum: Any,
    field_names: Sequence[str],
) -> List[str]:

    data = model_to_dict(
        curriculum
    )

    values = []

    for field_name in field_names:

        value = data.get(
            field_name
        )

        if isinstance(
            value,
            list,
        ):

            values.extend(
                value
            )

        elif value:

            values.append(
                value
            )

    result = []

    for item in values:

        # ----------------------------------------------------
        # Strings
        # ----------------------------------------------------

        if isinstance(
            item,
            str,
        ):

            text = normalize_text(
                item
            )

            if text:

                result.append(
                    text
                )

            continue

        # ----------------------------------------------------
        # Dictionaries
        # ----------------------------------------------------

        if isinstance(
            item,
            dict,
        ):

            candidate = (

                item.get("name")

                or

                item.get("title")

                or

                item.get("skill")

                or

                item.get("topic")

                or

                item.get("code")

            )

            if candidate:

                result.append(
                    normalize_text(
                        candidate
                    )
                )

            continue

        # ----------------------------------------------------
        # Pydantic / object
        # ----------------------------------------------------

        candidate = (

            getattr(
                item,
                "name",
                None,
            )

            or

            getattr(
                item,
                "title",
                None,
            )

            or

            getattr(
                item,
                "skill",
                None,
            )

            or

            getattr(
                item,
                "topic",
                None,
            )

        )

        if candidate:

            result.append(
                normalize_text(
                    candidate
                )
            )

    return list(
        dict.fromkeys(
            result
        )
    )


# ============================================================
# EXTRACT CURRICULUM FEATURES
# ============================================================

def extract_curriculum_features(
    curriculum: Any,
) -> Dict[str, List[str]]:

    return {

        "modules": extract_field(

            curriculum,

            [
                "modules",
                "module_list",
            ],

        ),

        "topics": extract_field(

            curriculum,

            [
                "topics",
                "topic_list",
            ],

        ),

        "skills": extract_field(

            curriculum,

            [
                "skills",
                "skill_list",
                "technical_skills",
            ],

        ),

        "tools": extract_field(

            curriculum,

            [
                "tools",
                "software_tools",
            ],

        ),

        "technologies": extract_field(

            curriculum,

            [
                "technologies",
                "technology",
            ],

        ),

        "projects": extract_field(

            curriculum,

            [
                "projects",
                "project_list",
            ],

        ),

        "concepts": extract_field(

            curriculum,

            [
                "concepts",
                "concept_list",
            ],

        ),

    }


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/7
#
# ITEM MATCHING
# ============================================================


def token_set(
    value: str,
) -> Set[str]:

    return set(
        re.findall(
            r"[a-z0-9+#.-]+",
            normalize_text(
                value
            ),
        )
    )


def similarity_score(
    source: str,
    target: str,
) -> float:

    source = normalize_text(
        source
    )

    target = normalize_text(
        target
    )

    if not source or not target:

        return 0.0

    if source == target:

        return 1.0

    if (
        source in target
        or
        target in source
    ):

        return 0.9

    source_tokens = token_set(
        source
    )

    target_tokens = token_set(
        target
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

    return len(
        intersection
    ) / len(
        union
    )


def match_items(
    source_items: Sequence[str],
    target_items: Sequence[str],
    category: str,
    threshold: float = 0.6,
) -> List[ComparisonItem]:

    results = []

    used_targets = set()

    for source in source_items:

        best_target = None

        best_score = 0.0

        for index, target in enumerate(
            target_items
        ):

            if index in used_targets:

                continue

            score = similarity_score(

                source,

                target,

            )

            if score > best_score:

                best_score = score

                best_target = (
                    target
                )

                best_index = index

        if best_target is None:

            results.append(

                ComparisonItem(

                    name=source,

                    category=category,

                    status="missing",

                    score=0.0,

                    source=source,

                )

            )

            continue

        used_targets.add(
            best_index
        )

        if best_score >= 0.85:

            status = "match"

        elif best_score >= threshold:

            status = "partial"

        else:

            status = "missing"

        results.append(

            ComparisonItem(

                name=source,

                category=category,

                status=status,

                score=best_score,

                source=source,

                target=best_target,

            )

        )

    return results


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/7
#
# CURRICULUM VS CURRICULUM
# ============================================================


def compare_curricula(
    curriculum_a: Any,
    curriculum_b: Any,
    threshold: float = 0.6,
) -> ComparisonResult:

    """
    Compare two curriculum objects.

    Works with:

        - Pydantic models
        - dataclasses
        - dictionaries
        - compatible Python objects
    """

    features_a = (
        extract_curriculum_features(
            curriculum_a
        )
    )

    features_b = (
        extract_curriculum_features(
            curriculum_b
        )
    )

    all_matches = []

    statistics = {}

    for category in features_a:

        source_items = (
            features_a[
                category
            ]
        )

        target_items = (
            features_b.get(
                category,
                [],
            )
        )

        matches = match_items(

            source_items,

            target_items,

            category,

            threshold,

        )

        all_matches.extend(
            matches
        )

        statistics[
            category
        ] = {

            "source_count":
                len(
                    source_items
                ),

            "target_count":
                len(
                    target_items
                ),

            "matches":
                sum(

                    1

                    for item
                    in matches

                    if item.status
                    ==
                    "match"

                ),

            "partial":
                sum(

                    1

                    for item
                    in matches

                    if item.status
                    ==
                    "partial"

                ),

            "missing":
                sum(

                    1

                    for item
                    in matches

                    if item.status
                    ==
                    "missing"

                ),

        }

    # --------------------------------------------------------
    # Overall score
    # --------------------------------------------------------

    if all_matches:

        overall_score = (

            sum(
                item.score
                for item
                in all_matches
            )
            /
            len(
                all_matches
            )

        )

    else:

        overall_score = 0.0

    matching = [

        item

        for item
        in all_matches

        if item.status
        ==
        "match"

    ]

    partial = [

        item

        for item
        in all_matches

        if item.status
        ==
        "partial"

    ]

    missing = [

        item

        for item
        in all_matches

        if item.status
        ==
        "missing"

    ]

    recommendations = []

    for item in missing:

        recommendations.append(

            f"Consider adding "
            f"{item.name} "
            f"under {item.category}."

        )

    return ComparisonResult(

        overall_score=round(

            overall_score,

            4,

        ),

        matching_items=matching,

        partial_items=partial,

        missing_items=missing,

        recommendations=recommendations,

        statistics=statistics,

    )


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/7
#
# CURRICULUM VS INDUSTRY
# ============================================================


def compare_curriculum_to_industry(
    curriculum: Any,
    industry: Any,
    threshold: float = 0.6,
) -> ComparisonResult:

    """
    Compare curriculum against an industry/JD object.

    Industry can be:

        - dictionary
        - JDProfile
        - skill list
        - normalized industry data
    """

    curriculum_features = (
        extract_curriculum_features(
            curriculum
        )
    )

    industry_data = model_to_dict(
        industry
    )

    industry_features = {

        "skills": extract_field(

            industry,

            [
                "skills",
                "required_skills",
                "technical_skills",
            ],

        ),

        "tools": extract_field(

            industry,

            [
                "tools",
                "required_tools",
            ],

        ),

        "technologies": extract_field(

            industry,

            [
                "technologies",
                "required_technologies",
            ],

        ),

        "frameworks": extract_field(

            industry,

            [
                "frameworks",
                "required_frameworks",
            ],

        ),

        "projects": extract_field(

            industry,

            [
                "projects",
                "required_projects",
            ],

        ),

    }

    comparisons = []

    for category in industry_features:

        industry_items = (
            industry_features[
                category
            ]
        )

        curriculum_items = (

            curriculum_features.get(

                category,

                [],

            )

        )

        # ----------------------------------------------------
        # Also consider technologies/frameworks as skills
        # ----------------------------------------------------

        if category == "frameworks":

            curriculum_items = (

                curriculum_items

                +

                curriculum_features.get(

                    "technologies",

                    [],

                )

            )

        comparisons.extend(

            match_items(

                source_items=industry_items,

                target_items=curriculum_items,

                category=category,

                threshold=threshold,

            )

        )

    # --------------------------------------------------------
    # Scores
    # --------------------------------------------------------

    if comparisons:

        overall_score = (

            sum(

                item.score

                for item
                in comparisons

            )

            /

            len(
                comparisons
            )

        )

    else:

        overall_score = 0.0

    matching = [

        item

        for item
        in comparisons

        if item.status
        ==
        "match"

    ]

    partial = [

        item

        for item
        in comparisons

        if item.status
        ==
        "partial"

    ]

    missing = [

        item

        for item
        in comparisons

        if item.status
        ==
        "missing"

    ]

    recommendations = []

    for item in missing:

        recommendations.append(

            "Add industry requirement: "
            +
            item.name
            +
            " ("
            +
            item.category
            +
            ")."

        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    statistics = {

        "industry_requirements":
            len(
                comparisons
            ),

        "matching":
            len(
                matching
            ),

        "partial":
            len(
                partial
            ),

        "missing":
            len(
                missing
            ),

        "alignment_percentage":
            round(
                overall_score * 100,
                2,
            ),

    }

    return ComparisonResult(

        overall_score=round(

            overall_score,

            4,

        ),

        matching_items=matching,

        partial_items=partial,

        missing_items=missing,

        recommendations=recommendations,

        statistics=statistics,

    )


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/7
#
# OUTPUT HELPERS
# ============================================================


def comparison_item_to_dict(
    item: ComparisonItem,
) -> Dict[str, Any]:

    return {

        "name":
            item.name,

        "category":
            item.category,

        "status":
            item.status,

        "score":
            round(
                item.score,
                4,
            ),

        "source":
            item.source,

        "target":
            item.target,

        "notes":
            item.notes,

    }


def comparison_result_to_dict(
    result: ComparisonResult,
) -> Dict[str, Any]:

    return {

        "overall_score":
            result.overall_score,

        "overall_percentage":
            round(

                result.overall_score
                *
                100,

                2,

            ),

        "matching_items": [

            comparison_item_to_dict(
                item
            )

            for item
            in result.matching_items

        ],

        "partial_items": [

            comparison_item_to_dict(
                item
            )

            for item
            in result.partial_items

        ],

        "missing_items": [

            comparison_item_to_dict(
                item
            )

            for item
            in result.missing_items

        ],

        "extra_items": [

            comparison_item_to_dict(
                item
            )

            for item
            in result.extra_items

        ],

        "recommendations":
            result.recommendations,

        "statistics":
            result.statistics,

    }


# ============================================================
# SUMMARY
# ============================================================


def generate_comparison_summary(
    result: ComparisonResult,
) -> str:

    score = (

        result.overall_score
        *
        100

    )

    return (

        f"Overall curriculum alignment: "
        f"{score:.1f}%. "

        f"{len(result.matching_items)} "
        f"items match, "

        f"{len(result.partial_items)} "
        f"items partially match, and "

        f"{len(result.missing_items)} "
        f"items are missing."

    )


# ============================================================
# EXPORT
# ============================================================

__all__ = [

    "ComparisonItem",

    "ComparisonResult",

    "normalize_text",

    "normalize_list",

    "model_to_dict",

    "extract_field",

    "extract_curriculum_features",

    "similarity_score",

    "match_items",

    "compare_curricula",

    "compare_curriculum_to_industry",

    "comparison_item_to_dict",

    "comparison_result_to_dict",

    "generate_comparison_summary",

]


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/7
#
# COMPATIBILITY HELPERS
# ============================================================


def compare_curriculum(
    curriculum_a: Any,
    curriculum_b: Any,
    **kwargs: Any,
) -> ComparisonResult:

    """
    Backward-compatible singular alias.
    """

    return compare_curricula(

        curriculum_a,

        curriculum_b,

        **kwargs,

    )


def compare_with_industry(
    curriculum: Any,
    industry: Any,
    **kwargs: Any,
) -> ComparisonResult:

    """
    Backward-compatible industry alias.
    """

    return compare_curriculum_to_industry(

        curriculum,

        industry,

        **kwargs,

    )


# ============================================================
# UPDATE PUBLIC API
# ============================================================

__all__ += [

    "compare_curriculum",

    "compare_with_industry",

]


# ============================================================
# END OF comparator.py
# ============================================================
