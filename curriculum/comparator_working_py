# ============================================================
# curriculum/comparator.py
# ============================================================
"""
PragyanAI Curriculum Intelligence
Curriculum-to-Curriculum and Curriculum-to-Industry comparison.

IMPORTANT:
Page 02 (Curriculum Intelligence) expects compare_curricula()
to return a DICTIONARY, not a ComparisonResult dataclass.

This version keeps the dataclasses for industry/legacy use, but
compare_curricula() returns the Page-02-compatible dictionary.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


logger = logging.getLogger("pragyanai.curriculum.comparator")


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
    matching_items: List[ComparisonItem] = field(default_factory=list)
    missing_items: List[ComparisonItem] = field(default_factory=list)
    partial_items: List[ComparisonItem] = field(default_factory=list)
    extra_items: List[ComparisonItem] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)

    # Normalize common separators without destroying terms such as
    # C++, C#, .NET, RAG, LLM, etc.
    value = value.replace("–", "-").replace("—", "-")

    return value.strip()


def normalize_list(values: Any) -> List[str]:
    if values is None:
        return []

    if isinstance(values, str):
        values = [values]

    if isinstance(values, dict):
        values = [values]

    if not isinstance(values, (list, tuple, set)):
        return []

    result: List[str] = []

    for value in values:
        if isinstance(value, dict):
            candidate = (
                value.get("name")
                or value.get("title")
                or value.get("topic")
                or value.get("skill")
                or value.get("code")
                or value.get("description")
            )
            if candidate is not None:
                value = candidate

        text = normalize_text(value)

        if text:
            result.append(text)

    return list(dict.fromkeys(result))


# ============================================================
# OBJECT / MODEL HELPERS
# ============================================================

def model_to_dict(obj: Any) -> Dict[str, Any]:
    if obj is None:
        return {}

    if isinstance(obj, dict):
        return obj

    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump(mode="python")
        except Exception:
            pass

    if hasattr(obj, "dict"):
        try:
            return obj.dict()
        except Exception:
            pass

    try:
        return vars(obj)
    except Exception:
        return {}


def _first_value(data: Dict[str, Any], names: Sequence[str]) -> Any:
    for name in names:
        value = data.get(name)
        if value is not None and value != "":
            return value
    return None


def _item_name(item: Any) -> str:
    if isinstance(item, str):
        return normalize_text(item)

    if isinstance(item, dict):
        value = _first_value(
            item,
            (
                "name",
                "title",
                "topic",
                "module",
                "module_name",
                "subject",
                "skill",
                "technology",
                "tool",
                "project",
                "concept",
                "code",
            ),
        )
        return normalize_text(value)

    value = _first_value(
        model_to_dict(item),
        (
            "name",
            "title",
            "topic",
            "module",
            "module_name",
            "subject",
            "skill",
            "technology",
            "tool",
            "project",
            "concept",
            "code",
        ),
    )

    if value is not None:
        return normalize_text(value)

    for attr in (
        "name",
        "title",
        "topic",
        "module",
        "module_name",
        "subject",
        "skill",
    ):
        value = getattr(item, attr, None)
        if value:
            return normalize_text(value)

    return ""


def extract_field(
    curriculum: Any,
    field_names: Sequence[str],
) -> List[str]:
    """
    Extract a flat list from curriculum fields.

    Supports:
      - strings
      - lists
      - dictionaries
      - Pydantic models
      - nested topic/module objects
    """

    data = model_to_dict(curriculum)
    values: List[Any] = []

    for field_name in field_names:
        value = data.get(field_name)

        if value is None:
            continue

        if isinstance(value, (list, tuple, set)):
            values.extend(value)
        else:
            values.append(value)

    result: List[str] = []

    for item in values:
        name = _item_name(item)

        if name:
            result.append(name)

    return list(dict.fromkeys(result))


# ============================================================
# NESTED MODULE / TOPIC EXTRACTION
# ============================================================

MODULE_KEYS = (
    "modules",
    "module_list",
    "units",
    "unit_list",
    "chapters",
    "sections",
)

TOPIC_KEYS = (
    "topics",
    "topic_list",
    "subtopics",
    "concepts",
    "concept_list",
    "contents",
)


def _children_from_object(
    obj: Any,
    keys: Sequence[str],
) -> List[Any]:
    data = model_to_dict(obj)

    children: List[Any] = []

    for key in keys:
        value = data.get(key)

        if value is None:
            continue

        if isinstance(value, (list, tuple, set)):
            children.extend(value)
        else:
            children.append(value)

    return children


def extract_module_records(
    curriculum: Any,
) -> List[Dict[str, Any]]:
    data = model_to_dict(curriculum)

    raw_modules: List[Any] = []

    for key in MODULE_KEYS:
        value = data.get(key)

        if value is None:
            continue

        if isinstance(value, (list, tuple, set)):
            raw_modules.extend(value)
        else:
            raw_modules.append(value)

    records: List[Dict[str, Any]] = []

    for index, raw_module in enumerate(raw_modules, start=1):
        module_data = model_to_dict(raw_module)

        module_name = _item_name(raw_module)

        if not module_name:
            module_name = f"module {index}"

        topics: List[str] = []

        for key in TOPIC_KEYS:
            value = module_data.get(key)

            if value is None:
                continue

            if isinstance(value, (list, tuple, set)):
                values = value
            else:
                values = [value]

            for topic in values:
                topic_name = _item_name(topic)

                if topic_name:
                    topics.append(topic_name)

        # Some extractor outputs use "topic" singular.
        singular_topic = module_data.get("topic")

        if singular_topic:
            topic_name = _item_name(singular_topic)
            if topic_name:
                topics.append(topic_name)

        topics = list(dict.fromkeys(topics))

        records.append(
            {
                "name": module_name,
                "topics": topics,
                "raw": module_data,
            }
        )

    return records


def get_all_topics(
    curriculum: Any,
) -> List[str]:
    """
    Get topics from nested modules first, then top-level topic fields.
    """

    records = extract_module_records(curriculum)

    topics: List[str] = []

    for module in records:
        topics.extend(module.get("topics", []))

    if not topics:
        topics.extend(
            extract_field(
                curriculum,
                TOPIC_KEYS,
            )
        )

    return list(dict.fromkeys(topics))


def extract_curriculum_features(
    curriculum: Any,
) -> Dict[str, List[str]]:
    """
    Backward-compatible flat curriculum feature extraction.
    """

    return {
        "modules": extract_field(
            curriculum,
            MODULE_KEYS,
        ),
        "topics": get_all_topics(curriculum),
        "skills": extract_field(
            curriculum,
            (
                "skills",
                "skill_list",
                "technical_skills",
            ),
        ),
        "tools": extract_field(
            curriculum,
            (
                "tools",
                "software_tools",
                "technologies_used",
            ),
        ),
        "technologies": extract_field(
            curriculum,
            (
                "technologies",
                "technology",
                "frameworks",
            ),
        ),
        "projects": extract_field(
            curriculum,
            (
                "projects",
                "project_list",
            ),
        ),
        "concepts": extract_field(
            curriculum,
            (
                "concepts",
                "concept_list",
            ),
        ),
    }


# ============================================================
# ITEM MATCHING
# ============================================================

def token_set(value: str) -> Set[str]:
    return set(
        re.findall(
            r"[a-z0-9+#.-]+",
            normalize_text(value),
        )
    )


def similarity_score(
    source: str,
    target: str,
) -> float:
    source = normalize_text(source)
    target = normalize_text(target)

    if not source or not target:
        return 0.0

    if source == target:
        return 1.0

    if source in target or target in source:
        return 0.90

    source_tokens = token_set(source)
    target_tokens = token_set(target)

    if not source_tokens or not target_tokens:
        return 0.0

    intersection = source_tokens & target_tokens
    union = source_tokens | target_tokens

    if not union:
        return 0.0

    return len(intersection) / len(union)


def match_items(
    source_items: Sequence[str],
    target_items: Sequence[str],
    category: str,
    threshold: float = 0.60,
) -> List[ComparisonItem]:

    results: List[ComparisonItem] = []
    used_targets: Set[int] = set()

    source_items = normalize_list(source_items)
    target_items = normalize_list(target_items)

    for source in source_items:
        best_target: Optional[str] = None
        best_score = 0.0
        best_index: Optional[int] = None

        for index, target in enumerate(target_items):
            if index in used_targets:
                continue

            score = similarity_score(source, target)

            if score > best_score:
                best_score = score
                best_target = target
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

        if best_index is not None:
            used_targets.add(best_index)

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


def _unmatched_target_items(
    source_items: Sequence[str],
    target_items: Sequence[str],
    threshold: float = 0.60,
) -> List[str]:
    """
    Find benchmark items that have no sufficiently similar primary item.
    """

    source_items = normalize_list(source_items)
    target_items = normalize_list(target_items)

    extras: List[str] = []

    for target in target_items:
        best = 0.0

        for source in source_items:
            best = max(
                best,
                similarity_score(source, target),
            )

        if best < threshold:
            extras.append(target)

    return list(dict.fromkeys(extras))


# ============================================================
# MODULE COMPARISON
# ============================================================

def _compare_modules(
    primary: Any,
    benchmark: Any,
    threshold: float,
) -> List[Dict[str, Any]]:

    primary_modules = extract_module_records(primary)
    benchmark_modules = extract_module_records(benchmark)

    results: List[Dict[str, Any]] = []
    used_benchmark: Set[int] = set()

    # If no nested modules exist, create a synthetic module from topics.
    if not primary_modules:
        primary_topics = get_all_topics(primary)

        if primary_topics:
            primary_modules = [
                {
                    "name": "Primary Curriculum Topics",
                    "topics": primary_topics,
                    "raw": {},
                }
            ]

    if not benchmark_modules:
        benchmark_topics = get_all_topics(benchmark)

        if benchmark_topics:
            benchmark_modules = [
                {
                    "name": "Benchmark Curriculum Topics",
                    "topics": benchmark_topics,
                    "raw": {},
                }
            ]

    for primary_module in primary_modules:
        primary_name = primary_module["name"]
        primary_topics = primary_module.get("topics", [])

        best_index: Optional[int] = None
        best_score = 0.0

        for index, benchmark_module in enumerate(
            benchmark_modules
        ):
            if index in used_benchmark:
                continue

            benchmark_name = benchmark_module["name"]
            benchmark_topics = benchmark_module.get(
                "topics",
                [],
            )

            # Module name similarity.
            name_score = similarity_score(
                primary_name,
                benchmark_name,
            )

            # Topic similarity.
            topic_score = 0.0

            if primary_topics and benchmark_topics:
                topic_matches = match_items(
                    primary_topics,
                    benchmark_topics,
                    "topic",
                    threshold,
                )

                topic_score = (
                    sum(
                        item.score
                        for item in topic_matches
                    )
                    / len(topic_matches)
                    if topic_matches
                    else 0.0
                )

            # Name carries more weight, but topics stabilize the match.
            if primary_topics and benchmark_topics:
                combined_score = (
                    0.45 * name_score
                    + 0.55 * topic_score
                )
            else:
                combined_score = name_score

            if combined_score > best_score:
                best_score = combined_score
                best_index = index

        if best_index is None:
            results.append(
                {
                    "primary_module": primary_name,
                    "benchmark_module": "No Matching Module",
                    "similarity_pct": 0.0,
                    "similar_concepts": [],
                    "primary_only": primary_topics,
                    "benchmark_only": [],
                }
            )
            continue

        used_benchmark.add(best_index)

        benchmark_module = benchmark_modules[
            best_index
        ]

        benchmark_name = benchmark_module["name"]
        benchmark_topics = benchmark_module.get(
            "topics",
            [],
        )

        topic_matches = match_items(
            primary_topics,
            benchmark_topics,
            "topic",
            threshold,
        )

        similar_concepts = [
            item.source
            for item in topic_matches
            if item.status == "match"
        ]

        partial_topics = [
            item.source
            for item in topic_matches
            if item.status == "partial"
        ]

        primary_only = [
            item.source
            for item in topic_matches
            if item.status == "missing"
        ]

        benchmark_only = _unmatched_target_items(
            primary_topics,
            benchmark_topics,
            threshold,
        )

        # Include partial matches in "similar concepts" because the
        # UI needs a useful topic-level comparison, while preserving
        # partial information in a separate field.
        all_similar = list(
            dict.fromkeys(
                similar_concepts
                + partial_topics
            )
        )

        topic_scores = [
            item.score
            for item in topic_matches
        ]

        topic_similarity = (
            sum(topic_scores)
            / len(topic_scores)
            if topic_scores
            else 0.0
        )

        if primary_topics and benchmark_topics:
            module_similarity = (
                0.45 * similarity_score(
                    primary_name,
                    benchmark_name,
                )
                + 0.55 * topic_similarity
            )
        else:
            module_similarity = similarity_score(
                primary_name,
                benchmark_name,
            )

        results.append(
            {
                "primary_module": primary_name,
                "benchmark_module": benchmark_name,
                "similarity_pct": round(
                    max(
                        0.0,
                        min(
                            100.0,
                            module_similarity * 100,
                        ),
                    ),
                    2,
                ),
                "similar_concepts": all_similar,
                "primary_only": primary_only,
                "benchmark_only": benchmark_only,
                "partial_concepts": partial_topics,
            }
        )

    # Benchmark modules that were not used by any primary module.
    for index, benchmark_module in enumerate(
        benchmark_modules
    ):
        if index in used_benchmark:
            continue

        results.append(
            {
                "primary_module": "No Matching Primary Module",
                "benchmark_module": benchmark_module["name"],
                "similarity_pct": 0.0,
                "similar_concepts": [],
                "primary_only": [],
                "benchmark_only": benchmark_module.get(
                    "topics",
                    [],
                ),
                "partial_concepts": [],
            }
        )

    return results


# ============================================================
# TOPIC COMPARISON
# ============================================================

def _build_topic_comparison(
    primary: Any,
    benchmark: Any,
    threshold: float,
) -> Tuple[
    List[Dict[str, Any]],
    List[str],
    List[str],
    List[str],
]:
    primary_topics = get_all_topics(primary)
    benchmark_topics = get_all_topics(benchmark)

    matches = match_items(
        primary_topics,
        benchmark_topics,
        "topic",
        threshold,
    )

    rows: List[Dict[str, Any]] = []

    similar_topics: List[str] = []
    primary_only_topics: List[str] = []
    benchmark_only_topics: List[str] = []

    for item in matches:
        if item.status == "match":
            status = "Similar"
            similar_topics.append(item.source)

        elif item.status == "partial":
            status = "Partial"
            similar_topics.append(item.source)

        else:
            status = "Primary Only"
            primary_only_topics.append(item.source)

        rows.append(
            {
                "Module": "",
                "Benchmark Module": "",
                "Topic": item.source,
                "Status": status,
                "Similarity %": round(
                    item.score * 100,
                    2,
                ),
                "Benchmark Topic": item.target,
            }
        )

    benchmark_only_topics = _unmatched_target_items(
        primary_topics,
        benchmark_topics,
        threshold,
    )

    # Add benchmark-only rows without mutating the list while
    # iterating over it.
    for topic in list(benchmark_only_topics):
        rows.append(
            {
                "Module": "",
                "Benchmark Module": "",
                "Topic": topic,
                "Status": "Benchmark Only",
                "Similarity %": 0.0,
                "Benchmark Topic": topic,
            }
        )

    benchmark_only_topics = list(
        dict.fromkeys(benchmark_only_topics)
    )

    return (
        rows,
        list(dict.fromkeys(similar_topics)),
        list(dict.fromkeys(primary_only_topics)),
        benchmark_only_topics,
    )


# ============================================================
# PAGE-02 SUMMARY
# ============================================================

def _comparison_summary(
    primary: Any,
    benchmark: Any,
    module_comparisons: List[Dict[str, Any]],
    topic_rows: List[Dict[str, Any]],
    similar_topics: List[str],
    primary_only_topics: List[str],
    benchmark_only_topics: List[str],
) -> Dict[str, Any]:

    module_scores = [
        float(item.get("similarity_pct", 0) or 0)
        for item in module_comparisons
    ]

    if module_scores:
        module_similarity = (
            sum(module_scores)
            / len(module_scores)
        )
    else:
        module_similarity = 0.0

    primary_topics = get_all_topics(primary)
    benchmark_topics = get_all_topics(benchmark)

    topic_scores = [
        float(
            row.get(
                "Similarity %",
                0,
            )
            or 0
        )
        for row in topic_rows
        if row.get("Status") != "Benchmark Only"
    ]

    if topic_scores:
        topic_similarity = (
            sum(topic_scores)
            / len(topic_scores)
        )
    elif not primary_topics and not benchmark_topics:
        topic_similarity = 0.0
    else:
        topic_similarity = 0.0

    # When topic data exists it is more informative than module-name
    # similarity. Combine both where possible.
    if module_scores and topic_scores:
        overall_similarity = (
            0.40 * module_similarity
            + 0.60 * topic_similarity
        )
    elif module_scores:
        overall_similarity = module_similarity
    else:
        overall_similarity = topic_similarity

    return {
        "similarity_pct": round(
            max(
                0.0,
                min(
                    100.0,
                    overall_similarity,
                ),
            ),
            2,
        ),
        "modules_compared": len(
            module_comparisons
        ),
        "similar_topics": len(
            similar_topics
        ),
        "different_topics": (
            len(primary_only_topics)
            + len(benchmark_only_topics)
        ),
        "primary_topic_count": len(primary_topics),
        "benchmark_topic_count": len(benchmark_topics),
    }


# ============================================================
# MAIN CURRICULUM VS CURRICULUM API
# ============================================================

def compare_curricula(
    curriculum_a: Any,
    curriculum_b: Any,
    threshold: float = 0.60,
) -> Dict[str, Any]:
    """
    Compare two curricula.

    IMPORTANT:
    This function intentionally returns a DICT because Page 02
    accesses the result with:
        comparison.get(...)
        comparison["..."]

    The previous implementation returned ComparisonResult, which
    caused:
        ValueError: Curriculum comparator returned an invalid result.
    """

    primary = model_to_dict(curriculum_a)
    benchmark = model_to_dict(curriculum_b)

    if not primary:
        logger.warning(
            "Primary curriculum converted to empty dictionary."
        )

    if not benchmark:
        logger.warning(
            "Benchmark curriculum converted to empty dictionary."
        )

    # --------------------------------------------------------
    # Module comparison
    # --------------------------------------------------------

    module_comparisons = _compare_modules(
        primary,
        benchmark,
        threshold,
    )

    # --------------------------------------------------------
    # Topic comparison
    # --------------------------------------------------------

    (
        topic_comparison,
        similar_topics,
        primary_only_topics,
        benchmark_only_topics,
    ) = _build_topic_comparison(
        primary,
        benchmark,
        threshold,
    )

    # --------------------------------------------------------
    # Overall summary
    # --------------------------------------------------------

    summary = _comparison_summary(
        primary,
        benchmark,
        module_comparisons,
        topic_comparison,
        similar_topics,
        primary_only_topics,
        benchmark_only_topics,
    )

    # --------------------------------------------------------
    # Legacy flat matching information
    # --------------------------------------------------------

    all_features_a = extract_curriculum_features(
        primary
    )
    all_features_b = extract_curriculum_features(
        benchmark
    )

    matching_items: List[Dict[str, Any]] = []
    partial_items: List[Dict[str, Any]] = []
    missing_items: List[Dict[str, Any]] = []
    extra_items: List[Dict[str, Any]] = []

    for category, source_items in all_features_a.items():
        target_items = all_features_b.get(
            category,
            [],
        )

        matches = match_items(
            source_items,
            target_items,
            category,
            threshold,
        )

        for item in matches:
            item_dict = comparison_item_to_dict(item)

            if item.status == "match":
                matching_items.append(item_dict)
            elif item.status == "partial":
                partial_items.append(item_dict)
            else:
                missing_items.append(item_dict)

        extra_items.extend(
            {
                "name": item,
                "category": category,
                "status": "extra",
                "score": 0.0,
                "source": "",
                "target": item,
                "notes": "Present in benchmark only.",
            }
            for item in _unmatched_target_items(
                source_items,
                target_items,
                threshold,
            )
        )

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = [
        f"Consider adding {topic} from the benchmark curriculum."
        for topic in benchmark_only_topics
    ]

    # --------------------------------------------------------
    # Page-02-compatible response
    # --------------------------------------------------------

    result: Dict[str, Any] = {
        # Page 02 primary keys
        "primary_subject": (
            primary.get("subject_name")
            or primary.get("subject")
            or ""
        ),
        "benchmark_subject": (
            benchmark.get("subject_name")
            or benchmark.get("subject")
            or ""
        ),

        "overall_comparison": {
            "similarity_pct": summary[
                "similarity_pct"
            ],
            "modules_compared": summary[
                "modules_compared"
            ],
            "similar_topics": summary[
                "similar_topics"
            ],
            "different_topics": summary[
                "different_topics"
            ],
        },

        "module_comparisons": module_comparisons,

        "topic_comparison": topic_comparison,

        "topic_categories": {
            "similar": similar_topics,
            "primary_only": primary_only_topics,
            "benchmark_only": benchmark_only_topics,
        },

        # Common aliases used by report/handoff code
        "module_comparison": module_comparisons,

        "topic_comparisons": topic_comparison,

        "similar_topics": similar_topics,

        "primary_only_topics": primary_only_topics,

        "benchmark_only_topics": benchmark_only_topics,

        "summary": summary,

        "matching_items": matching_items,

        "partial_items": partial_items,

        "missing_items": missing_items,

        "extra_items": extra_items,

        "recommendations": recommendations,

        "statistics": {
            **summary,
            "matching_items": len(
                matching_items
            ),
            "partial_items": len(
                partial_items
            ),
            "missing_items": len(
                missing_items
            ),
            "extra_items": len(
                extra_items
            ),
        },
    }

    # Final defensive validation.
    if not isinstance(result, dict):
        raise TypeError(
            "compare_curricula() must return a dictionary."
        )

    return result


# ============================================================
# CURRICULUM VS INDUSTRY
# ============================================================

def compare_curriculum_to_industry(
    curriculum: Any,
    industry: Any,
    threshold: float = 0.60,
) -> ComparisonResult:

    curriculum_features = (
        extract_curriculum_features(
            curriculum
        )
    )

    industry_features = {
        "skills": extract_field(
            industry,
            (
                "skills",
                "required_skills",
                "technical_skills",
            ),
        ),
        "tools": extract_field(
            industry,
            (
                "tools",
                "required_tools",
            ),
        ),
        "technologies": extract_field(
            industry,
            (
                "technologies",
                "required_technologies",
            ),
        ),
        "frameworks": extract_field(
            industry,
            (
                "frameworks",
                "required_frameworks",
            ),
        ),
        "projects": extract_field(
            industry,
            (
                "projects",
                "required_projects",
            ),
        ),
    }

    comparisons: List[ComparisonItem] = []

    for category, industry_items in industry_features.items():

        curriculum_items = (
            curriculum_features.get(
                category,
                [],
            )
        )

        if category == "frameworks":
            curriculum_items = list(
                dict.fromkeys(
                    curriculum_items
                    + curriculum_features.get(
                        "technologies",
                        [],
                    )
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

    if comparisons:
        overall_score = (
            sum(
                item.score
                for item in comparisons
            )
            / len(comparisons)
        )
    else:
        overall_score = 0.0

    matching = [
        item
        for item in comparisons
        if item.status == "match"
    ]

    partial = [
        item
        for item in comparisons
        if item.status == "partial"
    ]

    missing = [
        item
        for item in comparisons
        if item.status == "missing"
    ]

    recommendations = [
        (
            f"Add industry requirement: "
            f"{item.name} ({item.category})."
        )
        for item in missing
    ]

    statistics = {
        "industry_requirements": len(
            comparisons
        ),
        "matching": len(matching),
        "partial": len(partial),
        "missing": len(missing),
        "alignment_percentage": round(
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
# OUTPUT HELPERS
# ============================================================

def comparison_item_to_dict(
    item: ComparisonItem,
) -> Dict[str, Any]:

    return {
        "name": item.name,
        "category": item.category,
        "status": item.status,
        "score": round(
            item.score,
            4,
        ),
        "source": item.source,
        "target": item.target,
        "notes": item.notes,
    }


def comparison_result_to_dict(
    result: ComparisonResult,
) -> Dict[str, Any]:

    return {
        "overall_score": result.overall_score,
        "overall_percentage": round(
            result.overall_score * 100,
            2,
        ),
        "matching_items": [
            comparison_item_to_dict(item)
            for item in result.matching_items
        ],
        "partial_items": [
            comparison_item_to_dict(item)
            for item in result.partial_items
        ],
        "missing_items": [
            comparison_item_to_dict(item)
            for item in result.missing_items
        ],
        "extra_items": [
            comparison_item_to_dict(item)
            for item in result.extra_items
        ],
        "recommendations": result.recommendations,
        "statistics": result.statistics,
    }


def generate_comparison_summary(
    result: ComparisonResult,
) -> str:

    score = result.overall_score * 100

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
# BACKWARD COMPATIBILITY
# ============================================================

def compare_curriculum(
    curriculum_a: Any,
    curriculum_b: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
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
    return compare_curriculum_to_industry(
        curriculum,
        industry,
        **kwargs,
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "ComparisonItem",
    "ComparisonResult",
    "normalize_text",
    "normalize_list",
    "model_to_dict",
    "extract_field",
    "extract_module_records",
    "get_all_topics",
    "extract_curriculum_features",
    "similarity_score",
    "match_items",
    "compare_curricula",
    "compare_curriculum_to_industry",
    "comparison_item_to_dict",
    "comparison_result_to_dict",
    "generate_comparison_summary",
    "compare_curriculum",
    "compare_with_industry",
]
