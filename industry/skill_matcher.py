# ============================================================
# industry/skill_matcher.py
# CHUNK 1/10
#
# INDUSTRY SKILL MATCHER
#
# Purpose:
#   Compare industry/JD requirements against:
#
#       - Curriculum skills
#       - Student skills
#       - Course/module skills
#       - Resume skills
#       - Portfolio/project skills
#
# Pipeline:
#
#   JDProfile
#       ↓
#   Required / Preferred Skills
#       ↓
#   Skill Normalization
#       ↓
#   Exact Matching
#       ↓
#   Alias Matching
#       ↓
#   Fuzzy Matching
#       ↓
#   Semantic / Concept Matching
#       ↓
#   Weighted Coverage
#       ↓
#   Skill Gaps
#       ↓
#   Industry Readiness
#
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

from difflib import SequenceMatcher

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
# OPTIONAL IMPORT
# ============================================================

try:

    from .jd_parser import (
        JDProfile,
        JDSkill,
        canonicalize_skill,
        skill_aliases,
        skill_category,
        normalize_name,
    )

except ImportError:

    from jd_parser import (
        JDProfile,
        JDSkill,
        canonicalize_skill,
        skill_aliases,
        skill_category,
        normalize_name,
    )


# ============================================================
# VERSION
# ============================================================

SKILL_MATCHER_VERSION = "1.0.0"


# ============================================================
# MATCH TYPES
# ============================================================

MATCH_EXACT = "exact"

MATCH_ALIAS = "alias"

MATCH_FUZZY = "fuzzy"

MATCH_SEMANTIC = "semantic"

MATCH_CONCEPT = "concept"

MATCH_CATEGORY = "category"

MATCH_NONE = "none"


# ============================================================
# MATCH STATUS
# ============================================================

STATUS_MATCHED = "matched"

STATUS_PARTIAL = "partial"

STATUS_MISSING = "missing"

STATUS_UNKNOWN = "unknown"


# ============================================================
# REQUIREMENT TYPES
# ============================================================

REQUIRED = "required"

PREFERRED = "preferred"

OPTIONAL = "optional"

UNKNOWN = "unknown"


# ============================================================
# DEFAULT THRESHOLDS
# ============================================================

DEFAULT_EXACT_THRESHOLD = 1.0

DEFAULT_ALIAS_THRESHOLD = 0.95

DEFAULT_FUZZY_THRESHOLD = 0.82

DEFAULT_PARTIAL_THRESHOLD = 0.65

DEFAULT_SEMANTIC_THRESHOLD = 0.75


# ============================================================
# SKILL PRIORITIES
# ============================================================

DEFAULT_REQUIRED_WEIGHT = 1.0

DEFAULT_PREFERRED_WEIGHT = 0.5

DEFAULT_OPTIONAL_WEIGHT = 0.25


# ============================================================
# NORMALIZATION
# ============================================================

def clean_skill_text(
    value: Any,
) -> str:

    if value is None:
        return ""

    text = str(value)

    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def normalize_skill(
    value: Any,
) -> str:

    text = clean_skill_text(
        value
    )

    if not text:
        return ""

    try:

        return canonicalize_skill(
            text
        )

    except Exception:

        normalized = normalize_name(
            text
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized


def deduplicate_skills(
    skills: Iterable[str],
) -> List[str]:

    result = []

    seen = set()

    for skill in skills:

        cleaned = clean_skill_text(
            skill
        )

        if not cleaned:
            continue

        normalized = normalize_skill(
            cleaned
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
# INPUT SKILL
# ============================================================

@dataclass
class InputSkill:

    name: str

    normalized_name: str = ""

    category: str = "technical"

    proficiency: Optional[
        Union[
            float,
            int,
            str,
        ]
    ] = None

    years_experience: Optional[
        float
    ] = None

    source: str = "unknown"

    evidence: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        if not self.normalized_name:

            self.normalized_name = (
                normalize_skill(
                    self.name
                )
            )

        if self.category == "technical":

            try:

                self.category = skill_category(
                    self.name
                )

            except Exception:

                pass


# ============================================================
# MATCH RESULT
# ============================================================

@dataclass
class SkillMatch:

    required_skill: str

    candidate_skill: Optional[str] = None

    normalized_required: str = ""

    normalized_candidate: str = ""

    match_type: str = MATCH_NONE

    status: str = STATUS_MISSING

    similarity: float = 0.0

    confidence: float = 0.0

    requirement_type: str = REQUIRED

    category: str = "technical"

    importance: float = 0.0

    evidence: List[str] = field(
        default_factory=list
    )

    explanation: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# MATCHER CONFIGURATION
# ============================================================

@dataclass
class SkillMatcherConfig:

    exact_threshold: float = (
        DEFAULT_EXACT_THRESHOLD
    )

    alias_threshold: float = (
        DEFAULT_ALIAS_THRESHOLD
    )

    fuzzy_threshold: float = (
        DEFAULT_FUZZY_THRESHOLD
    )

    partial_threshold: float = (
        DEFAULT_PARTIAL_THRESHOLD
    )

    semantic_threshold: float = (
        DEFAULT_SEMANTIC_THRESHOLD
    )

    required_weight: float = (
        DEFAULT_REQUIRED_WEIGHT
    )

    preferred_weight: float = (
        DEFAULT_PREFERRED_WEIGHT
    )

    optional_weight: float = (
        DEFAULT_OPTIONAL_WEIGHT
    )

    enable_fuzzy: bool = True

    enable_semantic: bool = True

    enable_concept_matching: bool = True

    category_match_enabled: bool = True

    use_proficiency: bool = True

    use_experience: bool = True

    top_k_candidates: int = 5


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# SKILL RELATIONSHIPS
# ============================================================


# ============================================================
# RELATED SKILLS
#
# These relationships are deliberately conservative.
# A related skill does NOT automatically mean the candidate
# fully possesses the JD skill.
# ============================================================

RELATED_SKILLS: Dict[str, Set[str]] = {

    "machine learning": {

        "scikit-learn",

        "deep learning",

        "feature engineering",

        "model evaluation",

        "statistics",

    },

    "deep learning": {

        "machine learning",

        "pytorch",

        "tensorflow",

        "keras",

        "transformers",

    },

    "generative ai": {

        "large language models",

        "prompt engineering",

        "retrieval augmented generation",

        "embeddings",

        "transformers",

        "langchain",

        "hugging face",

    },

    "large language models": {

        "generative ai",

        "transformers",

        "prompt engineering",

        "fine tuning",

        "embeddings",

        "retrieval augmented generation",

    },

    "retrieval augmented generation": {

        "large language models",

        "embeddings",

        "vector databases",

        "langchain",

        "llamaindex",

    },

    "vector databases": {

        "embeddings",

        "retrieval augmented generation",

        "pinecone",

        "weaviate",

        "chroma",

        "faiss",

    },

    "langchain": {

        "large language models",

        "retrieval augmented generation",

        "generative ai",

    },

    "langgraph": {

        "langchain",

        "agentic ai",

        "generative ai",

    },

    "pytorch": {

        "deep learning",

        "machine learning",

    },

    "tensorflow": {

        "deep learning",

        "machine learning",

    },

    "pandas": {

        "python",

        "data analysis",

    },

    "numpy": {

        "python",

        "data analysis",

    },

    "apache spark": {

        "python",

        "sql",

        "data engineering",

    },

    "apache kafka": {

        "data engineering",

        "distributed systems",

    },

    "docker": {

        "kubernetes",

        "devops",

        "ci/cd",

    },

    "kubernetes": {

        "docker",

        "devops",

        "cloud",

    },

    "terraform": {

        "devops",

        "cloud",

        "infrastructure as code",

    },

    "aws": {

        "cloud",

        "docker",

        "kubernetes",

    },

    "azure": {

        "cloud",

        "docker",

        "kubernetes",

    },

    "gcp": {

        "cloud",

        "docker",

        "kubernetes",

    },

}


# ============================================================
# PARENT SKILLS
# ============================================================

PARENT_SKILLS: Dict[str, str] = {

    "scikit-learn":
        "machine learning",

    "pytorch":
        "deep learning",

    "tensorflow":
        "deep learning",

    "keras":
        "deep learning",

    "transformers":
        "large language models",

    "prompt engineering":
        "generative ai",

    "embeddings":
        "generative ai",

    "retrieval augmented generation":
        "generative ai",

    "langchain":
        "generative ai",

    "langgraph":
        "agentic ai",

    "docker":
        "devops",

    "kubernetes":
        "devops",

    "terraform":
        "devops",

    "apache spark":
        "data engineering",

    "apache kafka":
        "data engineering",

    "pandas":
        "data analysis",

    "numpy":
        "data analysis",

    "power bi":
        "business intelligence",

    "tableau":
        "business intelligence",

}


# ============================================================
# SKILL FAMILY
# ============================================================

SKILL_FAMILIES: Dict[str, Set[str]] = {

    "python_ecosystem": {

        "python",

        "pandas",

        "numpy",

        "scikit-learn",

        "pytorch",

        "tensorflow",

        "keras",

    },

    "machine_learning": {

        "machine learning",

        "scikit-learn",

        "deep learning",

        "feature engineering",

        "model evaluation",

        "statistics",

    },

    "generative_ai": {

        "generative ai",

        "large language models",

        "transformers",

        "prompt engineering",

        "embeddings",

        "retrieval augmented generation",

        "vector databases",

        "fine tuning",

        "langchain",

        "langgraph",

        "llamaindex",

        "hugging face",

    },

    "cloud": {

        "aws",

        "azure",

        "gcp",

        "cloud",

    },

    "devops": {

        "git",

        "docker",

        "kubernetes",

        "terraform",

        "ci/cd",

    },

    "data_engineering": {

        "apache spark",

        "apache kafka",

        "apache airflow",

        "sql",

        "data engineering",

    },

    "business_intelligence": {

        "excel",

        "power bi",

        "tableau",

        "business intelligence",

    },

}


# ============================================================
# GET RELATED SKILLS
# ============================================================

def get_related_skills(
    skill: str,
) -> Set[str]:

    normalized = normalize_skill(
        skill
    )

    related = set(
        RELATED_SKILLS.get(
            normalized,
            set(),
        )
    )

    parent = PARENT_SKILLS.get(
        normalized
    )

    if parent:
        related.add(
            parent
        )

    return related


# ============================================================
# GET SKILL FAMILY
# ============================================================

def get_skill_family(
    skill: str,
) -> Optional[str]:

    normalized = normalize_skill(
        skill
    )

    for family, members in (
        SKILL_FAMILIES.items()
    ):

        if normalized in members:

            return family

    return None


# ============================================================
# GET SKILL ALIAS SET
# ============================================================

def get_skill_alias_set(
    skill: str,
) -> Set[str]:

    normalized = normalize_skill(
        skill
    )

    aliases = set()

    aliases.add(
        normalized
    )

    try:

        aliases.update(

            normalize_skill(
                alias
            )

            for alias
            in skill_aliases(
                normalized
            )

        )

    except Exception:

        pass

    return {

        alias

        for alias
        in aliases

        if alias

    }


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# SIMILARITY ENGINE
# ============================================================


# ============================================================
# TOKENIZATION
# ============================================================

def skill_tokens(
    value: str,
) -> Set[str]:

    normalized = normalize_skill(
        value
    )

    if not normalized:
        return set()

    tokens = re.findall(
        r"[a-z0-9+#.]+",
        normalized,
    )

    return set(
        tokens
    )


# ============================================================
# TOKEN SIMILARITY
# ============================================================

def token_similarity(
    left: str,
    right: str,
) -> float:

    left_tokens = skill_tokens(
        left
    )

    right_tokens = skill_tokens(
        right
    )

    if not left_tokens or not right_tokens:

        return 0.0

    intersection = (
        left_tokens
        &
        right_tokens
    )

    union = (
        left_tokens
        |
        right_tokens
    )

    if not union:

        return 0.0

    return (

        len(intersection)
        /
        len(union)

    )


# ============================================================
# CHARACTER SIMILARITY
# ============================================================

def character_similarity(
    left: str,
    right: str,
) -> float:

    left = normalize_skill(
        left
    )

    right = normalize_skill(
        right
    )

    if not left or not right:

        return 0.0

    return SequenceMatcher(

        None,

        left,

        right,

    ).ratio()


# ============================================================
# COMBINED FUZZY SIMILARITY
# ============================================================

def fuzzy_similarity(
    left: str,
    right: str,
) -> float:

    left = normalize_skill(
        left
    )

    right = normalize_skill(
        right
    )

    if not left or not right:

        return 0.0

    if left == right:

        return 1.0

    char_score = character_similarity(
        left,
        right,
    )

    token_score = token_similarity(
        left,
        right,
    )

    return round(

        (
            char_score * 0.65
            +
            token_score * 0.35
        ),

        4,

    )


# ============================================================
# ALIAS SIMILARITY
# ============================================================

def alias_similarity(
    required: str,
    candidate: str,
) -> float:

    required_aliases = get_skill_alias_set(
        required
    )

    candidate_aliases = get_skill_alias_set(
        candidate
    )

    if (
        required_aliases
        &
        candidate_aliases
    ):

        return 1.0

    return 0.0


# ============================================================
# CONCEPT SIMILARITY
# ============================================================

def concept_similarity(
    required: str,
    candidate: str,
) -> float:

    required_normalized = normalize_skill(
        required
    )

    candidate_normalized = normalize_skill(
        candidate
    )

    if not required_normalized or not candidate_normalized:

        return 0.0

    if candidate_normalized in get_related_skills(
        required_normalized
    ):

        return 0.78

    if required_normalized in get_related_skills(
        candidate_normalized
    ):

        return 0.78

    required_family = get_skill_family(
        required_normalized
    )

    candidate_family = get_skill_family(
        candidate_normalized
    )

    if (

        required_family

        and

        required_family == candidate_family

    ):

        return 0.68

    return 0.0


# ============================================================
# CATEGORY SIMILARITY
# ============================================================

def category_similarity(
    required: str,
    candidate: str,
) -> float:

    try:

        required_category = skill_category(
            required
        )

        candidate_category = skill_category(
            candidate
        )

    except Exception:

        return 0.0

    if (

        required_category
        and
        candidate_category
        and
        required_category
        == candidate_category

    ):

        return 0.55

    return 0.0


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# INDIVIDUAL SKILL MATCHING
# ============================================================


def determine_match_type(
    required: str,
    candidate: str,
    config: SkillMatcherConfig,
) -> Tuple[str, float]:

    required_normalized = normalize_skill(
        required
    )

    candidate_normalized = normalize_skill(
        candidate
    )

    # --------------------------------------------------------
    # Exact
    # --------------------------------------------------------

    if (

        required_normalized
        ==
        candidate_normalized

    ):

        return MATCH_EXACT, 1.0

    # --------------------------------------------------------
    # Alias
    # --------------------------------------------------------

    alias_score = alias_similarity(

        required_normalized,

        candidate_normalized,

    )

    if (

        alias_score
        >=
        config.alias_threshold

    ):

        return MATCH_ALIAS, alias_score

    # --------------------------------------------------------
    # Fuzzy
    # --------------------------------------------------------

    if config.enable_fuzzy:

        fuzzy_score = fuzzy_similarity(

            required_normalized,

            candidate_normalized,

        )

        if (

            fuzzy_score
            >=
            config.fuzzy_threshold

        ):

            return MATCH_FUZZY, fuzzy_score

    # --------------------------------------------------------
    # Concept
    # --------------------------------------------------------

    if config.enable_concept_matching:

        concept_score = concept_similarity(

            required_normalized,

            candidate_normalized,

        )

        if (

            concept_score
            >=
            config.semantic_threshold

        ):

            return MATCH_CONCEPT, concept_score

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    if config.category_match_enabled:

        category_score = category_similarity(

            required_normalized,

            candidate_normalized,

        )

        if (

            category_score
            >=
            config.partial_threshold

        ):

            return MATCH_CATEGORY, category_score

    # --------------------------------------------------------
    # No match
    # --------------------------------------------------------

    if config.enable_fuzzy:

        score = fuzzy_similarity(

            required_normalized,

            candidate_normalized,

        )

    else:

        score = 0.0

    return MATCH_NONE, score


# ============================================================
# MATCH STATUS
# ============================================================

def determine_status(
    match_type: str,
    similarity: float,
    config: SkillMatcherConfig,
) -> str:

    if match_type in {

        MATCH_EXACT,

        MATCH_ALIAS,

    }:

        return STATUS_MATCHED

    if (

        similarity
        >=
        config.fuzzy_threshold

    ):

        return STATUS_MATCHED

    if (

        similarity
        >=
        config.partial_threshold

    ):

        return STATUS_PARTIAL

    return STATUS_MISSING


# ============================================================
# MATCH ONE SKILL
# ============================================================

def match_skill_pair(
    required_skill: str,
    candidate_skill: str,
    requirement_type: str = REQUIRED,
    importance: float = 0.0,
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> SkillMatch:

    config = (

        config

        or

        SkillMatcherConfig()

    )

    required_normalized = normalize_skill(
        required_skill
    )

    candidate_normalized = normalize_skill(
        candidate_skill
    )

    match_type, similarity = determine_match_type(

        required_normalized,

        candidate_normalized,

        config,

    )

    status = determine_status(

        match_type,

        similarity,

        config,

    )

    confidence = min(

        100.0,

        similarity * 100.0,

    )

    category = skill_category(
        required_normalized
    )

    explanation = ""

    if match_type == MATCH_EXACT:

        explanation = (
            "Exact skill match."
        )

    elif match_type == MATCH_ALIAS:

        explanation = (
            "Matched using a known skill alias."
        )

    elif match_type == MATCH_FUZZY:

        explanation = (
            "Matched using fuzzy similarity."
        )

    elif match_type == MATCH_CONCEPT:

        explanation = (
            "Related concept detected; "
            "this should be treated as a "
            "partial conceptual match."
        )

    elif match_type == MATCH_CATEGORY:

        explanation = (
            "Skills belong to the same "
            "technical category."
        )

    else:

        explanation = (
            "No sufficiently strong match found."
        )

    return SkillMatch(

        required_skill=required_skill,

        candidate_skill=candidate_skill,

        normalized_required=required_normalized,

        normalized_candidate=candidate_normalized,

        match_type=match_type,

        status=status,

        similarity=round(
            similarity,
            4,
        ),

        confidence=round(
            confidence,
            2,
        ),

        requirement_type=requirement_type,

        category=category,

        importance=importance,

        evidence=[

            f"{required_skill} ↔ {candidate_skill}"

        ],

        explanation=explanation,

    )


# ============================================================
# FIND BEST CANDIDATE
# ============================================================

def find_best_candidate(
    required_skill: str,
    candidate_skills: Sequence[
        Union[
            str,
            InputSkill,
        ]
    ],
    requirement_type: str = REQUIRED,
    importance: float = 0.0,
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> SkillMatch:

    config = (

        config

        or

        SkillMatcherConfig()

    )

    if not candidate_skills:

        return SkillMatch(

            required_skill=required_skill,

            normalized_required=normalize_skill(
                required_skill
            ),

            match_type=MATCH_NONE,

            status=STATUS_MISSING,

            similarity=0.0,

            confidence=0.0,

            requirement_type=requirement_type,

            importance=importance,

            explanation=(
                "No candidate skills were supplied."
            ),

        )

    best_match = None

    for candidate in candidate_skills:

        if isinstance(
            candidate,
            InputSkill,
        ):

            candidate_name = candidate.name

        else:

            candidate_name = str(
                candidate
            )

        result = match_skill_pair(

            required_skill,

            candidate_name,

            requirement_type,

            importance,

            config,

        )

        if (

            best_match is None

            or

            result.similarity
            >
            best_match.similarity

        ):

            best_match = result

    return best_match


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# INPUT PREPARATION
# ============================================================


# ============================================================
# CONVERT INPUT TO InputSkill
# ============================================================

def to_input_skill(
    value: Union[
        str,
        Mapping[str, Any],
        InputSkill,
    ],
    source: str = "unknown",
) -> InputSkill:

    if isinstance(
        value,
        InputSkill,
    ):

        return value

    if isinstance(
        value,
        Mapping,
    ):

        name = (

            value.get(
                "name"
            )

            or

            value.get(
                "skill"
            )

            or

            value.get(
                "title"
            )

            or

            ""

        )

        return InputSkill(

            name=str(
                name
            ),

            normalized_name=str(

                value.get(
                    "normalized_name",
                    "",
                )

            ),

            category=str(

                value.get(
                    "category",
                    "technical",
                )

            ),

            proficiency=value.get(
                "proficiency"
            ),

            years_experience=value.get(
                "years_experience"
            ),

            source=str(

                value.get(
                    "source",
                    source,
                )

            ),

            evidence=list(

                value.get(
                    "evidence",
                    [],
                )

                or

                []

            ),

            metadata=dict(

                value.get(
                    "metadata",
                    {},
                )

                or

                {}

            ),

        )

    return InputSkill(

        name=str(
            value
        ),

        source=source,

    )


# ============================================================
# PREPARE CANDIDATE SKILLS
# ============================================================

def prepare_candidate_skills(
    skills: Sequence[
        Union[
            str,
            Mapping[str, Any],
            InputSkill,
        ]
    ],
    source: str = "candidate",
) -> List[InputSkill]:

    result = []

    seen = set()

    for value in skills:

        item = to_input_skill(

            value,

            source,

        )

        if not item.name:
            continue

        key = normalize_skill(
            item.name
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
# EXTRACT JD REQUIREMENTS
# ============================================================

def extract_jd_requirements(
    profile: JDProfile,
) -> List[JDSkill]:

    skills = []

    skills.extend(

        profile.required_skills

    )

    skills.extend(

        profile.preferred_skills

    )

    # Avoid duplicate technologies.
    existing = {

        normalize_skill(
            skill.name
        )

        for skill
        in skills

    }

    for technology in profile.technologies:

        key = normalize_skill(
            technology.name
        )

        if key in existing:
            continue

        skills.append(
            technology
        )

        existing.add(
            key
        )

    return skills


# ============================================================
# GET REQUIREMENT WEIGHT
# ============================================================

def requirement_weight(
    requirement_type: str,
    config: SkillMatcherConfig,
) -> float:

    if requirement_type == REQUIRED:

        return config.required_weight

    if requirement_type == PREFERRED:

        return config.preferred_weight

    if requirement_type == OPTIONAL:

        return config.optional_weight

    return config.preferred_weight


# ============================================================
# NORMALIZE JD SKILL
# ============================================================

def normalize_jd_skill(
    skill: JDSkill,
) -> JDSkill:

    normalized = normalize_skill(
        skill.name
    )

    skill.name = (

        normalized

        or

        skill.name

    )

    skill.normalized_name = normalized

    return skill


# ============================================================
# PREPARE JD SKILLS
# ============================================================

def prepare_jd_skills(
    profile: JDProfile,
) -> List[JDSkill]:

    skills = extract_jd_requirements(
        profile
    )

    result = []

    seen = set()

    for skill in skills:

        normalized = normalize_skill(
            skill.name
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(
            normalized
        )

        skill.normalized_name = normalized

        result.append(
            skill
        )

    return result


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# JD → CANDIDATE SKILL MATCHING
# ============================================================


@dataclass
class SkillMatchReport:

    total_required: int = 0

    total_preferred: int = 0

    total_candidate_skills: int = 0

    matched_required: int = 0

    matched_preferred: int = 0

    partial_required: int = 0

    partial_preferred: int = 0

    missing_required: int = 0

    missing_preferred: int = 0

    required_coverage: float = 0.0

    preferred_coverage: float = 0.0

    overall_coverage: float = 0.0

    readiness_score: float = 0.0

    matches: List[SkillMatch] = field(
        default_factory=list
    )

    matched_skills: List[str] = field(
        default_factory=list
    )

    partial_skills: List[str] = field(
        default_factory=list
    )

    missing_skills: List[str] = field(
        default_factory=list
    )

    critical_gaps: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# MATCH JD AGAINST CANDIDATE
# ============================================================

def match_jd_to_candidate(
    profile: JDProfile,
    candidate_skills: Sequence[
        Union[
            str,
            Mapping[str, Any],
            InputSkill,
        ]
    ],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> SkillMatchReport:

    config = (

        config

        or

        SkillMatcherConfig()

    )

    candidates = prepare_candidate_skills(

        candidate_skills,

        source="candidate",

    )

    jd_skills = prepare_jd_skills(
        profile
    )

    matches = []

    for required_skill in jd_skills:

        requirement_type = (

            required_skill.requirement_type

            if required_skill.requirement_type
            != UNKNOWN

            else REQUIRED

        )

        weight = (

            required_skill.importance

            *
            requirement_weight(

                requirement_type,

                config,

            )

        )

        match = find_best_candidate(

            required_skill.name,

            candidates,

            requirement_type,

            weight,

            config,

        )

        matches.append(
            match
        )

    report = SkillMatchReport(

        total_candidate_skills=len(
            candidates
        ),

        matches=matches,

    )

    report.total_required = sum(

        1

        for match
        in matches

        if match.requirement_type
        == REQUIRED

    )

    report.total_preferred = sum(

        1

        for match
        in matches

        if match.requirement_type
        == PREFERRED

    )

    for match in matches:

        if match.status == STATUS_MATCHED:

            report.matched_skills.append(

                match.required_skill

            )

            if match.requirement_type == REQUIRED:

                report.matched_required += 1

            elif match.requirement_type == PREFERRED:

                report.matched_preferred += 1

        elif match.status == STATUS_PARTIAL:

            report.partial_skills.append(

                match.required_skill

            )

            if match.requirement_type == REQUIRED:

                report.partial_required += 1

            elif match.requirement_type == PREFERRED:

                report.partial_preferred += 1

        else:

            report.missing_skills.append(

                match.required_skill

            )

            if match.requirement_type == REQUIRED:

                report.missing_required += 1

            elif match.requirement_type == PREFERRED:

                report.missing_preferred += 1

    report.required_coverage = calculate_requirement_coverage(

        matches,

        REQUIRED,

    )

    report.preferred_coverage = calculate_requirement_coverage(

        matches,

        PREFERRED,

    )

    report.overall_coverage = calculate_overall_coverage(

        matches,

        config,

    )

    report.readiness_score = calculate_readiness_score(

        report,

        profile,

        config,

    )

    report.critical_gaps = identify_critical_gaps(

        matches,

        profile,

    )

    report.metadata = {

        "matcher_version":
            SKILL_MATCHER_VERSION,

        "candidate_skill_count":
            len(candidates),

        "jd_skill_count":
            len(jd_skills),

    }

    return report


# ============================================================
# REQUIREMENT COVERAGE
# ============================================================

def calculate_requirement_coverage(
    matches: Sequence[SkillMatch],
    requirement_type: str,
) -> float:

    relevant = [

        match

        for match
        in matches

        if match.requirement_type
        == requirement_type

    ]

    if not relevant:
        return 100.0

    total = 0.0

    for match in relevant:

        if match.status == STATUS_MATCHED:

            score = 1.0

        elif match.status == STATUS_PARTIAL:

            score = min(

                1.0,

                match.similarity,

            )

        else:

            score = 0.0

        total += score

    return round(

        (
            total
            /
            len(relevant)
        )
        *
        100.0,

        2,

    )


# ============================================================
# OVERALL COVERAGE
# ============================================================

def calculate_overall_coverage(
    matches: Sequence[SkillMatch],
    config: SkillMatcherConfig,
) -> float:

    if not matches:
        return 0.0

    weighted_total = 0.0

    weighted_possible = 0.0

    for match in matches:

        weight = requirement_weight(

            match.requirement_type,

            config,

        )

        weighted_possible += weight

        if match.status == STATUS_MATCHED:

            score = 1.0

        elif match.status == STATUS_PARTIAL:

            score = match.similarity

        else:

            score = 0.0

        weighted_total += (

            score
            *
            weight

        )

    if weighted_possible <= 0:
        return 0.0

    return round(

        (
            weighted_total
            /
            weighted_possible
        )
        *
        100.0,

        2,

    )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# READINESS + GAP ANALYSIS
# ============================================================


# ============================================================
# READINESS SCORE
# ============================================================

def calculate_readiness_score(
    report: SkillMatchReport,
    profile: JDProfile,
    config: SkillMatcherConfig,
) -> float:

    required_component = (

        report.required_coverage
        *
        0.65

    )

    preferred_component = (

        report.preferred_coverage
        *
        0.15

    )

    overall_component = (

        report.overall_coverage
        *
        0.20

    )

    score = (

        required_component
        +
        preferred_component
        +
        overall_component

    )

    # Strong penalty for critical missing skills.
    critical_count = len(
        report.critical_gaps
    )

    if critical_count:

        penalty = min(

            25.0,

            critical_count
            *
            3.0,

        )

        score -= penalty

    return round(

        max(
            0.0,
            min(
                100.0,
                score,
            )
        ),

        2,

    )


# ============================================================
# IDENTIFY CRITICAL GAPS
# ============================================================

def identify_critical_gaps(
    matches: Sequence[SkillMatch],
    profile: JDProfile,
) -> List[str]:

    critical = []

    for match in matches:

        if match.requirement_type != REQUIRED:
            continue

        if match.status != STATUS_MISSING:
            continue

        critical.append(
            match.required_skill
        )

    return deduplicate_skills(
        critical
    )


# ============================================================
# GAP SEVERITY
# ============================================================

def gap_severity(
    match: SkillMatch,
) -> str:

    if match.status == STATUS_MATCHED:

        return "none"

    if match.status == STATUS_PARTIAL:

        if match.requirement_type == REQUIRED:

            return "medium"

        return "low"

    if match.requirement_type == REQUIRED:

        if match.importance >= 80:

            return "critical"

        return "high"

    if match.requirement_type == PREFERRED:

        return "medium"

    return "low"


# ============================================================
# GAP RECORD
# ============================================================

@dataclass
class SkillGap:

    skill: str

    requirement_type: str

    severity: str

    category: str

    similarity: float

    importance: float

    recommended_action: str

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# BUILD GAP LIST
# ============================================================

def build_skill_gaps(
    report: SkillMatchReport,
) -> List[SkillGap]:

    gaps = []

    for match in report.matches:

        if match.status == STATUS_MATCHED:

            continue

        severity = gap_severity(
            match
        )

        if match.status == STATUS_PARTIAL:

            action = (

                "Strengthen the existing skill "
                "through hands-on projects and "
                "industry-level practice."

            )

        else:

            action = (

                "Add the skill to the learning "
                "plan and complete a practical "
                "industry project."

            )

        rationale = (

            f"{match.required_skill} is "
            f"{match.requirement_type} and "
            f"currently has a similarity score "
            f"of {match.similarity:.2f}."

        )

        gaps.append(

            SkillGap(

                skill=match.required_skill,

                requirement_type=match.requirement_type,

                severity=severity,

                category=match.category,

                similarity=match.similarity,

                importance=match.importance,

                recommended_action=action,

                rationale=rationale,

            )

        )

    severity_order = {

        "critical": 0,

        "high": 1,

        "medium": 2,

        "low": 3,

        "none": 4,

    }

    gaps.sort(

        key=lambda gap: (

            severity_order.get(
                gap.severity,
                99,
            ),

            -gap.importance,

            gap.skill,

        )

    )

    return gaps


# ============================================================
# CATEGORY COVERAGE
# ============================================================

def category_coverage(
    report: SkillMatchReport,
) -> Dict[str, Dict[str, Any]]:

    grouped = {}

    for match in report.matches:

        category = (

            match.category
            or
            "technical"

        )

        if category not in grouped:

            grouped[category] = {

                "total": 0,

                "matched": 0,

                "partial": 0,

                "missing": 0,

                "coverage": 0.0,

            }

        grouped[
            category
        ][
            "total"
        ] += 1

        if match.status == STATUS_MATCHED:

            grouped[
                category
            ][
                "matched"
            ] += 1

        elif match.status == STATUS_PARTIAL:

            grouped[
                category
            ][
                "partial"
            ] += 1

        else:

            grouped[
                category
            ][
                "missing"
            ] += 1

    for category, data in grouped.items():

        total = data[
            "total"
        ]

        if total:

            score = (

                data["matched"]

                +

                data["partial"] * 0.5

            )

            data[
                "coverage"
            ] = round(

                (
                    score
                    /
                    total
                )
                *
                100.0,

                2,

            )

    return grouped


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# CURRICULUM / STUDENT / JD COMPARISON
# ============================================================


@dataclass
class CurriculumMatchReport:

    jd_title: str = ""

    candidate_skill_count: int = 0

    jd_skill_count: int = 0

    coverage: float = 0.0

    readiness: float = 0.0

    matched_skills: List[str] = field(
        default_factory=list
    )

    partial_skills: List[str] = field(
        default_factory=list
    )

    missing_skills: List[str] = field(
        default_factory=list
    )

    critical_gaps: List[str] = field(
        default_factory=list
    )

    gaps: List[SkillGap] = field(
        default_factory=list
    )

    categories: Dict[
        str,
        Dict[str, Any]
    ] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# MATCH CURRICULUM TO JD
# ============================================================

def match_curriculum_to_jd(
    profile: JDProfile,
    curriculum_skills: Sequence[
        Union[
            str,
            Mapping[str, Any],
            InputSkill,
        ]
    ],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> CurriculumMatchReport:

    report = match_jd_to_candidate(

        profile,

        curriculum_skills,

        config,

    )

    gaps = build_skill_gaps(
        report
    )

    return CurriculumMatchReport(

        jd_title=profile.title,

        candidate_skill_count=(
            report.total_candidate_skills
        ),

        jd_skill_count=(
            report.total_required
            +
            report.total_preferred
        ),

        coverage=(
            report.overall_coverage
        ),

        readiness=(
            report.readiness_score
        ),

        matched_skills=(
            report.matched_skills
        ),

        partial_skills=(
            report.partial_skills
        ),

        missing_skills=(
            report.missing_skills
        ),

        critical_gaps=(
            report.critical_gaps
        ),

        gaps=gaps,

        categories=category_coverage(
            report
        ),

        metadata=report.metadata,

    )


# ============================================================
# REVERSE MATCH
#
# Given one candidate skill, identify which JD skills
# it can potentially satisfy.
# ============================================================

def reverse_match_skill(
    candidate_skill: str,
    jd_skills: Sequence[
        Union[
            str,
            JDSkill,
        ]
    ],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> List[SkillMatch]:

    config = (

        config

        or

        SkillMatcherConfig()

    )

    results = []

    for jd_skill in jd_skills:

        if isinstance(
            jd_skill,
            JDSkill,
        ):

            name = jd_skill.name

            requirement_type = (

                jd_skill.requirement_type

                if jd_skill.requirement_type
                != UNKNOWN

                else REQUIRED

            )

            importance = jd_skill.importance

        else:

            name = str(
                jd_skill
            )

            requirement_type = REQUIRED

            importance = 0.0

        result = match_skill_pair(

            name,

            candidate_skill,

            requirement_type,

            importance,

            config,

        )

        if result.status != STATUS_MISSING:

            results.append(
                result
            )

    results.sort(

        key=lambda item:
            item.similarity,

        reverse=True,

    )

    return results


# ============================================================
# FIND TRANSFERABLE SKILLS
# ============================================================

def find_transferable_skills(
    candidate_skills: Sequence[str],
    target_skills: Sequence[str],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> List[SkillMatch]:

    config = (

        config

        or

        SkillMatcherConfig()

    )

    results = []

    for target in target_skills:

        best = find_best_candidate(

            target,

            candidate_skills,

            REQUIRED,

            0.0,

            config,

        )

        if (

            best.status
            in {

                STATUS_MATCHED,

                STATUS_PARTIAL,

            }

        ):

            results.append(
                best
            )

    return results


# ============================================================
# SKILL TRANSFER SCORE
# ============================================================

def skill_transfer_score(
    candidate_skills: Sequence[str],
    target_skills: Sequence[str],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> float:

    matches = find_transferable_skills(

        candidate_skills,

        target_skills,

        config,

    )

    if not target_skills:
        return 0.0

    score = sum(

        match.similarity

        for match
        in matches

    )

    return round(

        (
            score
            /
            len(target_skills)
        )
        *
        100.0,

        2,

    )


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# SERIALIZATION + BATCH ANALYSIS
# ============================================================


# ============================================================
# SERIALIZATION
# ============================================================

def match_to_dict(
    match: SkillMatch,
) -> Dict[str, Any]:

    return asdict(
        match
    )


def gap_to_dict(
    gap: SkillGap,
) -> Dict[str, Any]:

    return asdict(
        gap
    )


def report_to_dict(
    report: SkillMatchReport,
) -> Dict[str, Any]:

    return {

        "total_required":
            report.total_required,

        "total_preferred":
            report.total_preferred,

        "total_candidate_skills":
            report.total_candidate_skills,

        "matched_required":
            report.matched_required,

        "matched_preferred":
            report.matched_preferred,

        "partial_required":
            report.partial_required,

        "partial_preferred":
            report.partial_preferred,

        "missing_required":
            report.missing_required,

        "missing_preferred":
            report.missing_preferred,

        "required_coverage":
            report.required_coverage,

        "preferred_coverage":
            report.preferred_coverage,

        "overall_coverage":
            report.overall_coverage,

        "readiness_score":
            report.readiness_score,

        "matches": [

            match_to_dict(
                match
            )

            for match
            in report.matches

        ],

        "matched_skills":
            report.matched_skills,

        "partial_skills":
            report.partial_skills,

        "missing_skills":
            report.missing_skills,

        "critical_gaps":
            report.critical_gaps,

        "metadata":
            report.metadata,

    }


# ============================================================
# CURRICULUM REPORT DICT
# ============================================================

def curriculum_report_to_dict(
    report: CurriculumMatchReport,
) -> Dict[str, Any]:

    return {

        "jd_title":
            report.jd_title,

        "candidate_skill_count":
            report.candidate_skill_count,

        "jd_skill_count":
            report.jd_skill_count,

        "coverage":
            report.coverage,

        "readiness":
            report.readiness,

        "matched_skills":
            report.matched_skills,

        "partial_skills":
            report.partial_skills,

        "missing_skills":
            report.missing_skills,

        "critical_gaps":
            report.critical_gaps,

        "gaps": [

            gap_to_dict(
                gap
            )

            for gap
            in report.gaps

        ],

        "categories":
            report.categories,

        "metadata":
            report.metadata,

    }


# ============================================================
# JSON EXPORT
# ============================================================

def report_to_json(
    report: SkillMatchReport,
    indent: int = 2,
) -> str:

    return json.dumps(

        report_to_dict(
            report
        ),

        indent=indent,

        ensure_ascii=False,

    )


# ============================================================
# BATCH JD MATCHING
# ============================================================

def match_multiple_jds(
    profiles: Sequence[JDProfile],
    candidate_skills: Sequence[
        Union[
            str,
            Mapping[str, Any],
            InputSkill,
        ]
    ],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> List[SkillMatchReport]:

    return [

        match_jd_to_candidate(

            profile,

            candidate_skills,

            config,

        )

        for profile
        in profiles

    ]


# ============================================================
# RANK JDS BY FIT
# ============================================================

def rank_jds(
    profiles: Sequence[JDProfile],
    candidate_skills: Sequence[
        Union[
            str,
            Mapping[str, Any],
            InputSkill,
        ]
    ],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> List[
    Tuple[
        JDProfile,
        SkillMatchReport,
    ]
]:

    results = []

    for profile in profiles:

        report = match_jd_to_candidate(

            profile,

            candidate_skills,

            config,

        )

        results.append(

            (
                profile,

                report,

            )

        )

    results.sort(

        key=lambda item:
            item[1].readiness_score,

        reverse=True,

    )

    return results


# ============================================================
# TOP GAPS
# ============================================================

def top_gaps(
    report: SkillMatchReport,
    limit: int = 10,
) -> List[SkillMatch]:

    missing = [

        match

        for match
        in report.matches

        if match.status
        in {

            STATUS_MISSING,

            STATUS_PARTIAL,

        }

    ]

    missing.sort(

        key=lambda match: (

            -match.importance,

            match.similarity,

        )

    )

    return missing[
        :limit
    ]


# ============================================================
# TOP MATCHES
# ============================================================

def top_matches(
    report: SkillMatchReport,
    limit: int = 10,
) -> List[SkillMatch]:

    matches = [

        match

        for match
        in report.matches

        if match.status
        == STATUS_MATCHED

    ]

    matches.sort(

        key=lambda match:
            match.similarity,

        reverse=True,

    )

    return matches[
        :limit
    ]


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# PUBLIC API
# ============================================================


# ============================================================
# SIMPLE MATCH API
# ============================================================

def match_skills(
    required_skills: Sequence[str],
    candidate_skills: Sequence[str],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> List[SkillMatch]:

    config = (

        config

        or

        SkillMatcherConfig()

    )

    results = []

    for required in required_skills:

        result = find_best_candidate(

            required,

            candidate_skills,

            REQUIRED,

            0.0,

            config,

        )

        results.append(
            result
        )

    return results


# ============================================================
# COVERAGE API
# ============================================================

def calculate_skill_coverage(
    required_skills: Sequence[str],
    candidate_skills: Sequence[str],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> float:

    matches = match_skills(

        required_skills,

        candidate_skills,

        config,

    )

    return calculate_requirement_coverage(

        matches,

        REQUIRED,

    )


# ============================================================
# MISSING SKILLS API
# ============================================================

def find_missing_skills(
    required_skills: Sequence[str],
    candidate_skills: Sequence[str],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> List[str]:

    matches = match_skills(

        required_skills,

        candidate_skills,

        config,

    )

    return [

        match.required_skill

        for match
        in matches

        if match.status
        == STATUS_MISSING

    ]


# ============================================================
# MATCHED SKILLS API
# ============================================================

def find_matched_skills(
    required_skills: Sequence[str],
    candidate_skills: Sequence[str],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> List[str]:

    matches = match_skills(

        required_skills,

        candidate_skills,

        config,

    )

    return [

        match.required_skill

        for match
        in matches

        if match.status
        == STATUS_MATCHED

    ]


# ============================================================
# PARTIAL SKILLS API
# ============================================================

def find_partial_skills(
    required_skills: Sequence[str],
    candidate_skills: Sequence[str],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> List[str]:

    matches = match_skills(

        required_skills,

        candidate_skills,

        config,

    )

    return [

        match.required_skill

        for match
        in matches

        if match.status
        == STATUS_PARTIAL

    ]


# ============================================================
# BUILD COMPLETE INDUSTRY REPORT
# ============================================================

def analyze_industry_fit(
    profile: JDProfile,
    candidate_skills: Sequence[
        Union[
            str,
            Mapping[str, Any],
            InputSkill,
        ]
    ],
    config: Optional[
        SkillMatcherConfig
    ] = None,
) -> Dict[str, Any]:

    report = match_jd_to_candidate(

        profile,

        candidate_skills,

        config,

    )

    gaps = build_skill_gaps(
        report
    )

    return {

        "jd": {

            "title":
                profile.title,

            "company":
                profile.company,

            "domain":
                profile.domain,

            "job_family":
                profile.job_family,

            "seniority":
                profile.seniority,

        },

        "fit": {

            "required_coverage":
                report.required_coverage,

            "preferred_coverage":
                report.preferred_coverage,

            "overall_coverage":
                report.overall_coverage,

            "readiness_score":
                report.readiness_score,

        },

        "skills": {

            "matched":
                report.matched_skills,

            "partial":
                report.partial_skills,

            "missing":
                report.missing_skills,

        },

        "critical_gaps":
            report.critical_gaps,

        "gaps": [

            gap_to_dict(
                gap
            )

            for gap
            in gaps

        ],

        "categories":
            category_coverage(
                report
            ),

        "matches": [

            match_to_dict(
                match
            )

            for match
            in report.matches

        ],

        "metadata": {

            "matcher_version":
                SKILL_MATCHER_VERSION,

        },

    }


# ============================================================
# PUBLIC CAPABILITIES
# ============================================================

SKILL_MATCHER_CAPABILITIES = [

    "exact_skill_matching",

    "alias_skill_matching",

    "fuzzy_skill_matching",

    "concept_skill_matching",

    "category_skill_matching",

    "required_skill_matching",

    "preferred_skill_matching",

    "curriculum_to_jd_matching",

    "candidate_to_jd_matching",

    "reverse_skill_matching",

    "transferable_skill_detection",

    "skill_gap_detection",

    "critical_gap_detection",

    "category_gap_analysis",

    "weighted_skill_coverage",

    "industry_readiness_score",

    "jd_ranking",

    "batch_jd_matching",

    "skill_statistics",

    "json_reporting",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "SKILL_MATCHER_VERSION",

    # Constants
    "MATCH_EXACT",

    "MATCH_ALIAS",

    "MATCH_FUZZY",

    "MATCH_SEMANTIC",

    "MATCH_CONCEPT",

    "MATCH_CATEGORY",

    "MATCH_NONE",

    "STATUS_MATCHED",

    "STATUS_PARTIAL",

    "STATUS_MISSING",

    "STATUS_UNKNOWN",

    "REQUIRED",

    "PREFERRED",

    "OPTIONAL",

    "UNKNOWN",

    # Models
    "InputSkill",

    "SkillMatch",

    "SkillMatcherConfig",

    "SkillMatchReport",

    "SkillGap",

    "CurriculumMatchReport",

    # Relationships
    "RELATED_SKILLS",

    "PARENT_SKILLS",

    "SKILL_FAMILIES",

    "get_related_skills",

    "get_skill_family",

    "get_skill_alias_set",

    # Similarity
    "skill_tokens",

    "token_similarity",

    "character_similarity",

    "fuzzy_similarity",

    "alias_similarity",

    "concept_similarity",

    "category_similarity",

    "determine_match_type",

    "determine_status",

    # Matching
    "match_skill_pair",

    "find_best_candidate",

    "match_skills",

    "match_jd_to_candidate",

    "match_curriculum_to_jd",

    "reverse_match_skill",

    "find_transferable_skills",

    "skill_transfer_score",

    # Analysis
    "calculate_requirement_coverage",

    "calculate_overall_coverage",

    "calculate_readiness_score",

    "identify_critical_gaps",

    "gap_severity",

    "build_skill_gaps",

    "category_coverage",

    "find_missing_skills",

    "find_matched_skills",

    "find_partial_skills",

    "calculate_skill_coverage",

    # Reporting
    "match_to_dict",

    "gap_to_dict",

    "report_to_dict",

    "curriculum_report_to_dict",

    "report_to_json",

    "top_gaps",

    "top_matches",

    "match_multiple_jds",

    "rank_jds",

    "analyze_industry_fit",

    "SKILL_MATCHER_CAPABILITIES",

]


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    try:

        from .jd_parser import analyze_jd

    except ImportError:

        from jd_parser import analyze_jd


    sample_jd = """

    Senior Generative AI Engineer

    About the Role

    We are looking for a Senior Generative AI Engineer.

    Responsibilities

    - Build LLM applications.
    - Develop RAG pipelines.
    - Create AI agents.
    - Deploy applications on AWS.

    Requirements

    - 5+ years of experience.
    - Strong Python programming.
    - Experience with machine learning.
    - Experience with large language models.
    - Experience with LangChain.
    - Experience with vector databases.
    - Experience with Docker.

    Preferred Skills

    - PyTorch.
    - Hugging Face.
    - Kubernetes.

    """

    profile = analyze_jd(
        sample_jd
    )

    candidate_skills = [

        "Python",

        "Machine Learning",

        "LLM",

        "LangChain",

        "Docker",

        "Pandas",

        "AWS",

    ]

    report = match_jd_to_candidate(

        profile,

        candidate_skills,

    )

    print(
        "\n"
        "============================================"
    )

    print(
        "INDUSTRY SKILL MATCHER TEST"
    )

    print(
        "============================================"
    )

    print(
        f"JD: {profile.title}"
    )

    print(
        f"Required Coverage: "
        f"{report.required_coverage}%"
    )

    print(
        f"Preferred Coverage: "
        f"{report.preferred_coverage}%"
    )

    print(
        f"Overall Coverage: "
        f"{report.overall_coverage}%"
    )

    print(
        f"Readiness Score: "
        f"{report.readiness_score}%"
    )

    print(
        "\nMatched:"
    )

    for skill in report.matched_skills:

        print(
            f"  ✓ {skill}"
        )

    print(
        "\nPartial:"
    )

    for skill in report.partial_skills:

        print(
            f"  ~ {skill}"
        )

    print(
        "\nMissing:"
    )

    for skill in report.missing_skills:

        print(
            f"  ✗ {skill}"
        )

    print(
        "\nCritical Gaps:"
    )

    for skill in report.critical_gaps:

        print(
            f"  ! {skill}"
        )

    print(
        "============================================"
    )


# ============================================================
# END OF industry/skill_matcher.py
# ============================================================
