# ============================================================
# curriculum/skill_extractor.py
# CHUNK 1/10
#
# SKILL EXTRACTION + SKILL INTELLIGENCE ENGINE
#
# Purpose:
#   Extract and analyze skills from:
#       - Curriculum
#       - Course descriptions
#       - Topics
#       - Projects
#       - Industry Job Descriptions
#       - Resumes / profiles
#       - Learning outcomes
#
# Pipeline:
#
#   Raw Curriculum / JD / Resume
#              │
#              ▼
#       Text Normalization
#              │
#              ▼
#       Skill Detection
#              │
#       ┌──────┼────────┐
#       ▼      ▼        ▼
#   Technical Tools  Soft Skills
#   Skills     &      & Domain
#              │
#              ▼
#       Skill Normalization
#              │
#              ▼
#       Skill Classification
#              │
#              ▼
#       Proficiency Detection
#              │
#              ▼
#       Evidence Extraction
#              │
#              ▼
#       Skill Intelligence
#              │
#       ┌──────┼──────────────┐
#       ▼      ▼              ▼
#      Gaps   Priority    Recommendations
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
# OPTIONAL SKLEARN
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
# VERSION
# ============================================================

SKILL_EXTRACTOR_VERSION = "1.0.0"


# ============================================================
# SKILL CATEGORIES
# ============================================================

SKILL_TECHNICAL = "technical"

SKILL_PROGRAMMING = "programming"

SKILL_MACHINE_LEARNING = "machine_learning"

SKILL_DEEP_LEARNING = "deep_learning"

SKILL_GENERATIVE_AI = "generative_ai"

SKILL_AGENTIC_AI = "agentic_ai"

SKILL_NLP = "nlp"

SKILL_COMPUTER_VISION = "computer_vision"

SKILL_DATA_SCIENCE = "data_science"

SKILL_DATA_ENGINEERING = "data_engineering"

SKILL_MLOPS = "mlops"

SKILL_LLMOPS = "llmops"

SKILL_CLOUD = "cloud"

SKILL_DATABASE = "database"

SKILL_DEVOPS = "devops"

SKILL_CYBERSECURITY = "cybersecurity"

SKILL_SOFTWARE_ENGINEERING = "software_engineering"

SKILL_BUSINESS_INTELLIGENCE = "business_intelligence"

SKILL_ANALYTICS = "analytics"

SKILL_TOOL = "tool"

SKILL_FRAMEWORK = "framework"

SKILL_LIBRARY = "library"

SKILL_PLATFORM = "platform"

SKILL_DOMAIN = "domain"

SKILL_SOFT = "soft_skill"

SKILL_COMMUNICATION = "communication"

SKILL_LEADERSHIP = "leadership"

SKILL_MANAGEMENT = "management"

SKILL_PROBLEM_SOLVING = "problem_solving"

SKILL_OTHER = "other"


# ============================================================
# PROFICIENCY LEVELS
# ============================================================

PROFICIENCY_UNKNOWN = "Unknown"

PROFICIENCY_AWARENESS = "Awareness"

PROFICIENCY_BEGINNER = "Beginner"

PROFICIENCY_INTERMEDIATE = "Intermediate"

PROFICIENCY_ADVANCED = "Advanced"

PROFICIENCY_EXPERT = "Expert"


PROFICIENCY_ORDER = {

    PROFICIENCY_UNKNOWN: 0,

    PROFICIENCY_AWARENESS: 1,

    PROFICIENCY_BEGINNER: 2,

    PROFICIENCY_INTERMEDIATE: 3,

    PROFICIENCY_ADVANCED: 4,

    PROFICIENCY_EXPERT: 5,

}


# ============================================================
# SKILL STATUS
# ============================================================

SKILL_PRESENT = "present"

SKILL_MISSING = "missing"

SKILL_PARTIAL = "partial"

SKILL_WEAK = "weak"

SKILL_STRONG = "strong"

SKILL_EMERGING = "emerging"

SKILL_OUTDATED = "outdated"


# ============================================================
# EVIDENCE TYPES
# ============================================================

EVIDENCE_EXPLICIT = "explicit"

EVIDENCE_CONTEXTUAL = "contextual"

EVIDENCE_PROJECT = "project"

EVIDENCE_TOOL = "tool"

EVIDENCE_OUTCOME = "outcome"

EVIDENCE_EXPERIENCE = "experience"

EVIDENCE_CERTIFICATION = "certification"


# ============================================================
# IMPORTANCE
# ============================================================

IMPORTANCE_LOW = "Low"

IMPORTANCE_MEDIUM = "Medium"

IMPORTANCE_HIGH = "High"

IMPORTANCE_CRITICAL = "Critical"


# ============================================================
# RECOMMENDATION TYPES
# ============================================================

REC_LEARN = "learn"

REC_PRACTICE = "practice"

REC_PROJECT = "project"

REC_ADVANCE = "advance"

REC_PREREQUISITE = "prerequisite"

REC_UPDATE = "update"

REC_SPECIALIZE = "specialize"


# ============================================================
# TEXT UTILITIES
# ============================================================

def clean_text(
    value: Any,
) -> str:

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


def canonical_skill(
    value: Any,
) -> str:

    text = clean_text(
        value
    ).lower()

    aliases = {

        "ml":
            "machine learning",

        "machine-learning":
            "machine learning",

        "dl":
            "deep learning",

        "deep-learning":
            "deep learning",

        "genai":
            "generative ai",

        "gen ai":
            "generative ai",

        "llm":
            "large language model",

        "llms":
            "large language model",

        "rag":
            "retrieval augmented generation",

        "retrieval-augmented generation":
            "retrieval augmented generation",

        "nlp":
            "natural language processing",

        "cv":
            "computer vision",

        "mlops":
            "machine learning operations",

        "llmops":
            "large language model operations",

        "k8s":
            "kubernetes",

        "powerbi":
            "power bi",

        "scikit learn":
            "scikit-learn",

        "sklearn":
            "scikit-learn",

    }

    text = aliases.get(
        text,
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

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


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:

    return max(

        minimum,

        min(
            maximum,
            safe_float(
                value
            ),
        ),

    )


def percentage(
    numerator: float,
    denominator: float,
) -> float:

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
            * 100.0

        ),

        0.0,

        100.0,

    ),

    2)


def deduplicate(
    values: Iterable[Any],
) -> List[Any]:

    result = []

    seen = set()

    for value in values:

        key = canonical_skill(
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
# CONFIGURATION
# ============================================================

@dataclass
class SkillExtractorConfig:

    similarity_threshold: float = 0.70

    partial_similarity_threshold: float = 0.45

    minimum_confidence: float = 50.0

    emerging_threshold: float = 65.0

    high_priority_threshold: float = 70.0

    critical_priority_threshold: float = 85.0

    max_skills: int = 500

    max_evidence_per_skill: int = 10

    max_recommendations: int = 50

    include_soft_skills: bool = True

    include_tools: bool = True

    include_projects: bool = True

    include_emerging_skills: bool = True

    infer_skills_from_tools: bool = True


# ============================================================
# SKILL EVIDENCE
# ============================================================

@dataclass
class SkillEvidence:

    skill: str

    evidence_text: str

    evidence_type: str = EVIDENCE_EXPLICIT

    confidence: float = 0.0

    source: str = ""

    context: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SKILL PROFILE
# ============================================================

@dataclass
class SkillProfile:

    skill_id: str

    name: str

    canonical_name: str

    category: str = SKILL_OTHER

    subcategory: str = ""

    description: str = ""

    aliases: List[str] = field(
        default_factory=list
    )

    keywords: List[str] = field(
        default_factory=list
    )

    related_skills: List[str] = field(
        default_factory=list
    )

    prerequisite_skills: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    frameworks: List[str] = field(
        default_factory=list
    )

    technologies: List[str] = field(
        default_factory=list
    )

    projects: List[str] = field(
        default_factory=list
    )

    proficiency: str = PROFICIENCY_UNKNOWN

    proficiency_score: float = 0.0

    confidence_score: float = 0.0

    industry_relevance: float = 0.0

    employability_impact: float = 0.0

    emerging_score: float = 0.0

    learning_impact: float = 0.0

    occurrence_count: int = 1

    evidence_count: int = 0

    status: str = SKILL_PRESENT

    importance: str = IMPORTANCE_MEDIUM

    evidence: List[
        SkillEvidence
    ] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SKILL MATCH
# ============================================================

@dataclass
class SkillMatch:

    source_skill: str

    target_skill: str

    similarity: float = 0.0

    lexical_similarity: float = 0.0

    token_overlap: float = 0.0

    semantic_similarity: float = 0.0

    status: str = SKILL_PARTIAL

    confidence: float = 0.0

    rationale: str = ""


# ============================================================
# SKILL GAP
# ============================================================

@dataclass
class SkillGap:

    skill: str

    category: str = SKILL_OTHER

    gap_type: str = SKILL_MISSING

    severity: str = IMPORTANCE_MEDIUM

    priority_score: float = 0.0

    similarity: float = 0.0

    industry_relevance: float = 0.0

    employability_impact: float = 0.0

    learning_impact: float = 0.0

    prerequisite_impact: float = 0.0

    best_match: Optional[str] = None

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
# SKILL RECOMMENDATION
# ============================================================

@dataclass
class SkillRecommendation:

    skill: str

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

    tools: List[str] = field(
        default_factory=list
    )

    project: Optional[str] = None

    expected_impact: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# COMPLETE RESULT
# ============================================================

@dataclass
class SkillExtractionResult:

    skills: List[
        SkillProfile
    ] = field(
        default_factory=list
    )

    evidence: List[
        SkillEvidence
    ] = field(
        default_factory=list
    )

    matches: List[
        SkillMatch
    ] = field(
        default_factory=list
    )

    gaps: List[
        SkillGap
    ] = field(
        default_factory=list
    )

    recommendations: List[
        SkillRecommendation
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
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# SKILL KNOWLEDGE BASE
# ============================================================


# ============================================================
# PROGRAMMING SKILLS
# ============================================================

PROGRAMMING_SKILLS = {

    "python": [
        "python",
        "python programming",
    ],

    "java": [
        "java",
        "java programming",
    ],

    "c++": [
        "c++",
        "cpp",
        "c plus plus",
    ],

    "c": [
        "c programming",
        "c language",
    ],

    "javascript": [
        "javascript",
        "js",
    ],

    "typescript": [
        "typescript",
        "ts",
    ],

    "go": [
        "golang",
        "go programming",
    ],

    "rust": [
        "rust programming",
    ],

    "scala": [
        "scala",
    ],

    "r": [
        "r programming",
        "r language",
    ],

    "sql": [
        "sql",
        "structured query language",
    ],

    "bash": [
        "bash",
        "shell scripting",
    ],

}


# ============================================================
# DATA SCIENCE
# ============================================================

DATA_SCIENCE_SKILLS = {

    "data analysis": [
        "data analysis",
        "data analytics",
    ],

    "statistics": [
        "statistics",
        "statistical analysis",
    ],

    "probability": [
        "probability",
        "probability theory",
    ],

    "linear algebra": [
        "linear algebra",
    ],

    "calculus": [
        "calculus",
        "differential calculus",
    ],

    "feature engineering": [
        "feature engineering",
        "feature extraction",
    ],

    "exploratory data analysis": [
        "exploratory data analysis",
        "eda",
    ],

    "data visualization": [
        "data visualization",
        "data visualisation",
    ],

}


# ============================================================
# MACHINE LEARNING
# ============================================================

MACHINE_LEARNING_SKILLS = {

    "machine learning": [
        "machine learning",
        "machine-learning",
        "ml",
    ],

    "supervised learning": [
        "supervised learning",
    ],

    "unsupervised learning": [
        "unsupervised learning",
    ],

    "classification": [
        "classification",
        "classification algorithms",
    ],

    "regression": [
        "regression",
        "regression algorithms",
    ],

    "clustering": [
        "clustering",
        "cluster analysis",
    ],

    "decision trees": [
        "decision tree",
        "decision trees",
    ],

    "random forest": [
        "random forest",
    ],

    "xgboost": [
        "xgboost",
    ],

    "lightgbm": [
        "lightgbm",
        "light gbm",
    ],

    "support vector machines": [
        "support vector machine",
        "support vector machines",
        "svm",
    ],

    "k nearest neighbors": [
        "k nearest neighbors",
        "knn",
    ],

    "naive bayes": [
        "naive bayes",
    ],

    "recommender systems": [
        "recommendation system",
        "recommendation systems",
        "recommender systems",
    ],

    "time series forecasting": [
        "time series forecasting",
        "time-series forecasting",
    ],

    "anomaly detection": [
        "anomaly detection",
    ],

    "model evaluation": [
        "model evaluation",
        "model validation",
    ],

    "hyperparameter tuning": [
        "hyperparameter tuning",
        "hyperparameter optimization",
    ],

}


# ============================================================
# DEEP LEARNING
# ============================================================

DEEP_LEARNING_SKILLS = {

    "deep learning": [
        "deep learning",
        "deep-learning",
        "dl",
    ],

    "neural networks": [
        "neural networks",
        "neural network",
    ],

    "cnn": [
        "cnn",
        "convolutional neural network",
        "convolutional neural networks",
    ],

    "rnn": [
        "rnn",
        "recurrent neural network",
    ],

    "lstm": [
        "lstm",
        "long short term memory",
    ],

    "gru": [
        "gru",
        "gated recurrent unit",
    ],

    "transformers": [
        "transformer",
        "transformers",
        "transformer architecture",
    ],

    "attention mechanisms": [
        "attention mechanism",
        "attention mechanisms",
        "self attention",
    ],

    "backpropagation": [
        "backpropagation",
        "back propagation",
    ],

    "transfer learning": [
        "transfer learning",
    ],

    "fine tuning": [
        "fine tuning",
        "fine-tuning",
    ],

    "reinforcement learning": [
        "reinforcement learning",
        "rl",
    ],

}


# ============================================================
# GENERATIVE AI
# ============================================================

GENERATIVE_AI_SKILLS = {

    "generative ai": [
        "generative ai",
        "generative artificial intelligence",
        "genai",
        "gen ai",
    ],

    "large language models": [
        "large language model",
        "large language models",
        "llm",
        "llms",
    ],

    "prompt engineering": [
        "prompt engineering",
        "prompt design",
        "prompting",
    ],

    "retrieval augmented generation": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
        "rag",
    ],

    "embeddings": [
        "embeddings",
        "embedding models",
    ],

    "vector databases": [
        "vector database",
        "vector databases",
        "vector db",
    ],

    "fine tuning": [
        "fine tuning",
        "fine-tuning",
    ],

    "llm evaluation": [
        "llm evaluation",
        "large language model evaluation",
    ],

    "multimodal ai": [
        "multimodal ai",
        "multimodal artificial intelligence",
    ],

    "synthetic data": [
        "synthetic data",
        "synthetic dataset",
    ],

}


# ============================================================
# AGENTIC AI
# ============================================================

AGENTIC_AI_SKILLS = {

    "agentic ai": [
        "agentic ai",
        "agentic artificial intelligence",
    ],

    "ai agents": [
        "ai agents",
        "ai agent",
        "intelligent agents",
    ],

    "tool calling": [
        "tool calling",
        "tool use",
        "tool usage",
    ],

    "function calling": [
        "function calling",
        "function-calling",
    ],

    "multi agent systems": [
        "multi agent",
        "multi-agent",
        "multi agent systems",
    ],

    "agent memory": [
        "agent memory",
        "memory systems",
        "long term memory",
        "short term memory",
    ],

    "agent orchestration": [
        "agent orchestration",
        "agent workflow",
    ],

}


# ============================================================
# NLP
# ============================================================

NLP_SKILLS = {

    "natural language processing": [
        "natural language processing",
        "nlp",
    ],

    "text classification": [
        "text classification",
    ],

    "sentiment analysis": [
        "sentiment analysis",
    ],

    "named entity recognition": [
        "named entity recognition",
        "ner",
    ],

    "tokenization": [
        "tokenization",
        "tokenisation",
    ],

    "text summarization": [
        "text summarization",
        "text summarisation",
    ],

    "machine translation": [
        "machine translation",
    ],

}


# ============================================================
# COMPUTER VISION
# ============================================================

COMPUTER_VISION_SKILLS = {

    "computer vision": [
        "computer vision",
    ],

    "image classification": [
        "image classification",
    ],

    "object detection": [
        "object detection",
    ],

    "image segmentation": [
        "image segmentation",
        "semantic segmentation",
        "instance segmentation",
    ],

    "opencv": [
        "opencv",
        "open cv",
    ],

    "yolo": [
        "yolo",
        "yolov5",
        "yolov8",
        "yolov9",
        "yolov10",
    ],

    "image processing": [
        "image processing",
    ],

}


# ============================================================
# DATA ENGINEERING
# ============================================================

DATA_ENGINEERING_SKILLS = {

    "data engineering": [
        "data engineering",
    ],

    "etl": [
        "etl",
        "extract transform load",
    ],

    "data pipelines": [
        "data pipeline",
        "data pipelines",
    ],

    "apache spark": [
        "apache spark",
        "spark",
        "pyspark",
    ],

    "apache kafka": [
        "apache kafka",
        "kafka",
    ],

    "apache airflow": [
        "apache airflow",
        "airflow",
    ],

    "data warehousing": [
        "data warehouse",
        "data warehousing",
    ],

}


# ============================================================
# MLOPS / LLMOPS
# ============================================================

MLOPS_SKILLS = {

    "mlops": [
        "mlops",
        "machine learning operations",
    ],

    "model deployment": [
        "model deployment",
        "ml model deployment",
    ],

    "model monitoring": [
        "model monitoring",
    ],

    "model registry": [
        "model registry",
    ],

    "mlflow": [
        "mlflow",
    ],

    "kubeflow": [
        "kubeflow",
    ],

    "llmops": [
        "llmops",
        "large language model operations",
    ],

}


# ============================================================
# CLOUD
# ============================================================

CLOUD_SKILLS = {

    "aws": [
        "aws",
        "amazon web services",
    ],

    "azure": [
        "azure",
        "microsoft azure",
    ],

    "gcp": [
        "gcp",
        "google cloud platform",
    ],

    "ec2": [
        "ec2",
        "amazon ec2",
    ],

    "s3": [
        "s3",
        "amazon s3",
    ],

    "lambda": [
        "aws lambda",
        "lambda functions",
    ],

    "cloud architecture": [
        "cloud architecture",
        "cloud infrastructure",
    ],

}


# ============================================================
# TOOLS / FRAMEWORKS
# ============================================================

TOOLS_AND_FRAMEWORKS = {

    "pandas": [
        "pandas",
    ],

    "numpy": [
        "numpy",
    ],

    "scikit-learn": [
        "scikit-learn",
        "sklearn",
        "scikit learn",
    ],

    "pytorch": [
        "pytorch",
        "torch",
    ],

    "tensorflow": [
        "tensorflow",
    ],

    "keras": [
        "keras",
    ],

    "hugging face": [
        "hugging face",
        "huggingface",
    ],

    "transformers": [
        "transformers",
        "huggingface transformers",
    ],

    "langchain": [
        "langchain",
    ],

    "langgraph": [
        "langgraph",
    ],

    "llamaindex": [
        "llamaindex",
        "llama index",
    ],

    "streamlit": [
        "streamlit",
    ],

    "gradio": [
        "gradio",
    ],

    "fastapi": [
        "fastapi",
    ],

    "flask": [
        "flask",
    ],

    "django": [
        "django",
    ],

    "docker": [
        "docker",
    ],

    "kubernetes": [
        "kubernetes",
        "k8s",
    ],

    "terraform": [
        "terraform",
    ],

    "git": [
        "git",
        "git version control",
    ],

    "github actions": [
        "github actions",
    ],

}


# ============================================================
# DATABASE
# ============================================================

DATABASE_SKILLS = {

    "mysql": [
        "mysql",
    ],

    "postgresql": [
        "postgresql",
        "postgres",
    ],

    "mongodb": [
        "mongodb",
        "mongo db",
    ],

    "redis": [
        "redis",
    ],

    "faiss": [
        "faiss",
    ],

    "chroma": [
        "chroma",
        "chromadb",
    ],

    "pinecone": [
        "pinecone",
    ],

    "vector databases": [
        "vector database",
        "vector databases",
        "vector db",
    ],

}


# ============================================================
# SOFT SKILLS
# ============================================================

SOFT_SKILLS = {

    "communication": [
        "communication",
        "communication skills",
        "verbal communication",
        "written communication",
    ],

    "leadership": [
        "leadership",
        "leadership skills",
    ],

    "teamwork": [
        "teamwork",
        "team work",
        "collaboration",
        "collaborative skills",
    ],

    "problem solving": [
        "problem solving",
        "problem-solving",
    ],

    "critical thinking": [
        "critical thinking",
    ],

    "analytical thinking": [
        "analytical thinking",
    ],

    "time management": [
        "time management",
    ],

    "adaptability": [
        "adaptability",
        "adaptable",
    ],

    "presentation": [
        "presentation skills",
        "presentations",
    ],

    "negotiation": [
        "negotiation",
        "negotiation skills",
    ],

}


# ============================================================
# MASTER DICTIONARY
# ============================================================

SKILL_DICTIONARIES = {

    SKILL_PROGRAMMING:
        PROGRAMMING_SKILLS,

    SKILL_DATA_SCIENCE:
        DATA_SCIENCE_SKILLS,

    SKILL_MACHINE_LEARNING:
        MACHINE_LEARNING_SKILLS,

    SKILL_DEEP_LEARNING:
        DEEP_LEARNING_SKILLS,

    SKILL_GENERATIVE_AI:
        GENERATIVE_AI_SKILLS,

    SKILL_AGENTIC_AI:
        AGENTIC_AI_SKILLS,

    SKILL_NLP:
        NLP_SKILLS,

    SKILL_COMPUTER_VISION:
        COMPUTER_VISION_SKILLS,

    SKILL_DATA_ENGINEERING:
        DATA_ENGINEERING_SKILLS,

    SKILL_MLOPS:
        MLOPS_SKILLS,

    SKILL_CLOUD:
        CLOUD_SKILLS,

    SKILL_DATABASE:
        DATABASE_SKILLS,

    SKILL_TOOL:
        TOOLS_AND_FRAMEWORKS,

    SKILL_SOFT:
        SOFT_SKILLS,

}


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# SKILL DETECTION + EXTRACTION
# ============================================================


# ============================================================
# 1. GENERATE SKILL ID
# ============================================================

def generate_skill_id(
    skill: str,
) -> str:

    canonical = canonical_skill(
        skill
    )

    canonical = canonical.replace(
        " ",
        "_",
    )

    canonical = re.sub(
        r"[^a-z0-9_+#.-]",
        "",
        canonical,
    )

    return (
        f"skill_{canonical}"
    )


# ============================================================
# 2. MATCH PHRASE
# ============================================================

def phrase_present(
    text: str,
    phrase: str,
) -> bool:

    text = clean_text(
        text
    ).lower()

    phrase = clean_text(
        phrase
    ).lower()

    if not text or not phrase:

        return False

    escaped = re.escape(
        phrase
    )

    pattern = (
        r"(?<![a-z0-9+#])"
        + escaped
        + r"(?![a-z0-9+#])"
    )

    return bool(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
    )


# ============================================================
# 3. FIND SKILL EVIDENCE
# ============================================================

def find_skill_evidence_in_text(
    text: str,
    skill: str,
    aliases: Sequence[str],
    source: str = "",
    max_items: int = 10,
) -> List[SkillEvidence]:

    text = clean_text(
        text
    )

    if not text:

        return []

    phrases = deduplicate(
        [skill] + list(
            aliases
        )
    )

    evidence = []

    for phrase in phrases:

        if not phrase_present(
            text,
            phrase,
        ):

            continue

        match = re.search(

            re.escape(
                phrase
            ),

            text,

            flags=re.IGNORECASE,

        )

        if not match:

            continue

        start = max(
            0,
            match.start() - 120,
        )

        end = min(
            len(text),
            match.end() + 180,
        )

        context = text[
            start:end
        ]

        evidence.append(

            SkillEvidence(

                skill=skill,

                evidence_text=phrase,

                evidence_type=EVIDENCE_EXPLICIT,

                confidence=95.0,

                source=source,

                context=context,

            )

        )

        if len(
            evidence
        ) >= max_items:

            break

    return evidence


# ============================================================
# 4. FIND ALL DICTIONARY SKILLS
# ============================================================

def extract_dictionary_skills(
    text: str,
    include_soft_skills: bool = True,
    include_tools: bool = True,
    max_skills: int = 500,
) -> Tuple[
    List[str],
    List[SkillEvidence],
]:

    text = clean_text(
        text
    )

    if not text:

        return [], []

    skills = []

    evidence = []

    for category, dictionary in (
        SKILL_DICTIONARIES.items()
    ):

        if (
            category == SKILL_SOFT
            and
            not include_soft_skills
        ):

            continue

        if (
            category == SKILL_TOOL
            and
            not include_tools
        ):

            continue

        for skill, aliases in (
            dictionary.items()
        ):

            skill_evidence = (
                find_skill_evidence_in_text(

                    text,

                    skill,

                    aliases,

                )
            )

            if not skill_evidence:

                continue

            skills.append(
                skill
            )

            evidence.extend(
                skill_evidence
            )

            if len(
                skills
            ) >= max_skills:

                break

        if len(
            skills
        ) >= max_skills:

            break

    return (

        deduplicate(
            skills
        ),

        evidence,

    )


# ============================================================
# 5. EXTRACT CANDIDATE SKILLS
# ============================================================

def extract_candidate_skills(
    text: str,
) -> List[str]:

    text = clean_text(
        text
    )

    if not text:

        return []

    candidates = []

    patterns = [

        r"\b[A-Z][A-Za-z0-9+#.-]{1,30}\b",

        r"\b[A-Za-z]+(?:\s+[A-Za-z]+){1,4}\s+(?:skills?|development|engineering|analysis|programming|deployment|architecture)\b",

    ]

    for pattern in patterns:

        candidates.extend(

            re.findall(

                pattern,

                text,

                flags=re.IGNORECASE,

            )

        )

    stopwords = {

        "this",

        "that",

        "with",

        "from",

        "using",

        "skills",

        "experience",

        "years",

        "candidate",

        "responsibilities",

        "requirements",

        "knowledge",

        "strong",

        "good",

        "working",

        "ability",

    }

    result = []

    for candidate in candidates:

        candidate = clean_text(
            candidate
        )

        if not candidate:

            continue

        normalized = canonical_skill(
            candidate
        )

        if normalized in stopwords:

            continue

        if len(
            normalized
        ) < 2:

            continue

        result.append(
            candidate
        )

    return deduplicate(
        result
    )


# ============================================================
# 6. EXTRACT SKILLS FROM TEXT
# ============================================================

def extract_skills_from_text(
    text: str,
    config: Optional[
        SkillExtractorConfig
    ] = None,
    source: str = "",
) -> Tuple[
    List[str],
    List[SkillEvidence],
]:

    config = (
        config
        or
        SkillExtractorConfig()
    )

    dictionary_skills, evidence = (
        extract_dictionary_skills(

            text,

            include_soft_skills=(
                config.include_soft_skills
            ),

            include_tools=(
                config.include_tools
            ),

            max_skills=(
                config.max_skills
            ),

        )
    )

    # Add candidate phrases only when
    # they can be mapped to known categories.
    candidates = extract_candidate_skills(
        text
    )

    known = set(
        canonical_skill(
            skill
        )
        for skill
        in dictionary_skills
    )

    for candidate in candidates:

        canonical = canonical_skill(
            candidate
        )

        if canonical in known:

            continue

        # Only accept candidate if it has
        # meaningful skill-related wording.
        candidate_lower = canonical.lower()

        skill_words = (

            "programming",
            "engineering",
            "development",
            "analytics",
            "analysis",
            "deployment",
            "architecture",
            "automation",
            "security",
            "management",

        )

        if not any(

            word in candidate_lower

            for word in skill_words

        ):

            continue

        dictionary_skills.append(
            candidate
        )

        known.add(
            canonical
        )

        evidence.append(

            SkillEvidence(

                skill=candidate,

                evidence_text=candidate,

                evidence_type=EVIDENCE_CONTEXTUAL,

                confidence=60.0,

                source=source,

                context=text[:500],

            )

        )

    return (

        deduplicate(
            dictionary_skills
        )[
            :config.max_skills
        ],

        evidence,

    )


# ============================================================
# 7. EXTRACT FROM ITEMS
# ============================================================

def extract_skills_from_items(
    items: Sequence[Any],
    config: Optional[
        SkillExtractorConfig
    ] = None,
    source: str = "",
) -> Tuple[
    List[str],
    List[SkillEvidence],
]:

    skills = []

    evidence = []

    for item in items:

        if item is None:

            continue

        if isinstance(
            item,
            str,
        ):

            item_skills, item_evidence = (
                extract_skills_from_text(

                    item,

                    config,

                    source,

                )
            )

            skills.extend(
                item_skills
            )

            evidence.extend(
                item_evidence
            )

            continue

        if isinstance(
            item,
            dict,
        ):

            for key in (

                "name",
                "title",
                "skill",
                "skills",
                "topic",
                "description",
                "content",
                "technology",
                "tools",
                "technologies",
                "requirements",
                "responsibilities",

            ):

                if key not in item:

                    continue

                value = item.get(
                    key
                )

                if isinstance(
                    value,
                    (list, tuple, set),
                ):

                    nested_skills, nested_evidence = (
                        extract_skills_from_items(

                            list(value),

                            config,

                            source,

                        )
                    )

                else:

                    nested_skills, nested_evidence = (
                        extract_skills_from_text(

                            str(value),

                            config,

                            source,

                        )
                    )

                skills.extend(
                    nested_skills
                )

                evidence.extend(
                    nested_evidence
                )

    return (

        deduplicate(
            skills
        ),

        evidence,

    )


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# SKILL CLASSIFICATION
# ============================================================


# ============================================================
# 1. CATEGORY CLASSIFICATION
# ============================================================

def classify_skill_category(
    skill: str,
) -> str:

    canonical = canonical_skill(
        skill
    )

    if not canonical:

        return SKILL_OTHER

    for category, dictionary in (
        SKILL_DICTIONARIES.items()
    ):

        if canonical in {

            canonical_skill(
                item
            )

            for item
            in dictionary.keys()

        }:

            return category

        for aliases in dictionary.values():

            if canonical in {

                canonical_skill(
                    alias
                )

                for alias
                in aliases

            }:

                return category

    # Domain-based fallback.
    text = canonical

    if "machine learning" in text:

        return SKILL_MACHINE_LEARNING

    if "deep learning" in text:

        return SKILL_DEEP_LEARNING

    if "generative ai" in text:

        return SKILL_GENERATIVE_AI

    if "agent" in text:

        return SKILL_AGENTIC_AI

    if "cloud" in text:

        return SKILL_CLOUD

    if "database" in text:

        return SKILL_DATABASE

    if "security" in text:

        return SKILL_CYBERSECURITY

    if "analytics" in text:

        return SKILL_ANALYTICS

    return SKILL_OTHER


# ============================================================
# 2. SUBCATEGORY
# ============================================================

def classify_skill_subcategory(
    skill: str,
    category: str,
) -> str:

    canonical = canonical_skill(
        skill
    )

    if category == SKILL_PROGRAMMING:

        return "Programming Language"

    if category == SKILL_TOOL:

        return "Tool"

    if category == SKILL_FRAMEWORK:

        return "Framework"

    if category == SKILL_MACHINE_LEARNING:

        if "classification" in canonical:

            return "Supervised Learning"

        if "regression" in canonical:

            return "Supervised Learning"

        if "clustering" in canonical:

            return "Unsupervised Learning"

        return "Machine Learning"

    if category == SKILL_GENERATIVE_AI:

        if "rag" in canonical:

            return "Retrieval"

        if "prompt" in canonical:

            return "Prompt Engineering"

        if "embedding" in canonical:

            return "Representation"

        return "Generative AI"

    if category == SKILL_AGENTIC_AI:

        if "memory" in canonical:

            return "Agent Memory"

        if "tool" in canonical:

            return "Tool Calling"

        return "Agent Systems"

    if category == SKILL_CLOUD:

        return "Cloud Computing"

    if category == SKILL_DATABASE:

        return "Database"

    if category == SKILL_SOFT:

        return "Soft Skills"

    return category.replace(
        "_",
        " ",
    ).title()


# ============================================================
# 3. ALIASES
# ============================================================

def get_skill_aliases(
    skill: str,
) -> List[str]:

    canonical = canonical_skill(
        skill
    )

    aliases = []

    for dictionary in (
        SKILL_DICTIONARIES.values()
    ):

        if canonical in {

            canonical_skill(
                key
            )

            for key
            in dictionary.keys()

        }:

            for key, values in (
                dictionary.items()
            ):

                if canonical_skill(
                    key
                ) == canonical:

                    aliases.extend(
                        values
                    )

    return deduplicate(
        aliases
    )


# ============================================================
# 4. KEYWORDS
# ============================================================

def get_skill_keywords(
    skill: str,
) -> List[str]:

    aliases = get_skill_aliases(
        skill
    )

    tokens = re.split(
        r"[\s,;/|:+#.-]+",
        canonical_skill(
            skill
        ),
    )

    return deduplicate(

        list(aliases)

        +

        [

            token

            for token
            in tokens

            if token

        ]

    )


# ============================================================
# 5. IMPORTANCE
# ============================================================

CRITICAL_SKILLS = {

    "python",

    "sql",

    "machine learning",

    "deep learning",

    "generative ai",

    "large language models",

    "retrieval augmented generation",

    "cloud",

    "git",

}


HIGH_IMPORTANCE_SKILLS = {

    "data analysis",

    "statistics",

    "natural language processing",

    "computer vision",

    "ai agents",

    "agentic ai",

    "docker",

    "kubernetes",

    "mlops",

    "data engineering",

    "api",

}


def classify_skill_importance(
    skill: str,
    industry_relevance: float = 0.0,
    employability: float = 0.0,
) -> str:

    canonical = canonical_skill(
        skill
    )

    if canonical in CRITICAL_SKILLS:

        return IMPORTANCE_CRITICAL

    if canonical in HIGH_IMPORTANCE_SKILLS:

        return IMPORTANCE_HIGH

    if (
        industry_relevance >= 85
        or
        employability >= 85
    ):

        return IMPORTANCE_HIGH

    if (
        industry_relevance >= 65
        or
        employability >= 65
    ):

        return IMPORTANCE_MEDIUM

    return IMPORTANCE_LOW


# ============================================================
# 6. NORMALIZE SKILL COLLECTION
# ============================================================

def normalize_skills(
    skills: Sequence[str],
) -> List[str]:

    normalized = []

    for skill in skills:

        canonical = canonical_skill(
            skill
        )

        if not canonical:

            continue

        normalized.append(
            canonical
        )

    return deduplicate(
        normalized
    )


# ============================================================
# 7. BUILD SKILL PROFILE
# ============================================================

def build_skill_profile(
    skill: str,
    occurrence_count: int = 1,
    evidence: Optional[
        Sequence[SkillEvidence]
    ] = None,
) -> SkillProfile:

    canonical = canonical_skill(
        skill
    )

    category = classify_skill_category(
        canonical
    )

    subcategory = classify_skill_subcategory(
        canonical,
        category,
    )

    industry = estimate_skill_industry_relevance(
        canonical,
        category,
    )

    employability = estimate_skill_employability(
        canonical,
        category,
    )

    importance = classify_skill_importance(

        canonical,

        industry,

        employability,

    )

    return SkillProfile(

        skill_id=generate_skill_id(
            canonical
        ),

        name=canonical,

        canonical_name=canonical,

        category=category,

        subcategory=subcategory,

        description=(

            f"{canonical} is a "
            f"{subcategory.lower()} skill."

        ),

        aliases=get_skill_aliases(
            canonical
        ),

        keywords=get_skill_keywords(
            canonical
        ),

        proficiency=(
            PROFICIENCY_UNKNOWN
        ),

        occurrence_count=max(

            1,

            int(
                occurrence_count
            ),

        ),

        evidence_count=len(
            evidence
            or []
        ),

        industry_relevance=industry,

        employability_impact=employability,

        importance=importance,

        evidence=list(
            evidence
            or []
        ),

    )


# ============================================================
# 8. BUILD PROFILES
# ============================================================

def build_skill_profiles(
    skills: Sequence[str],
    evidence: Optional[
        Sequence[SkillEvidence]
    ] = None,
) -> List[SkillProfile]:

    normalized = normalize_skills(
        skills
    )

    evidence = list(
        evidence
        or []
    )

    occurrences = {}

    for skill in skills:

        canonical = canonical_skill(
            skill
        )

        if not canonical:

            continue

        occurrences[
            canonical
        ] = (

            occurrences.get(
                canonical,
                0,
            )
            +
            1

        )

    profiles = []

    for skill in normalized:

        skill_evidence = [

            item

            for item
            in evidence

            if canonical_skill(
                item.skill
            ) == skill

        ]

        profile = build_skill_profile(

            skill,

            occurrence_count=(
                occurrences.get(
                    skill,
                    1,
                )
            ),

            evidence=skill_evidence,

        )

        profiles.append(
            profile
        )

    return profiles


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# PROFICIENCY + EVIDENCE INTELLIGENCE
# ============================================================


# ============================================================
# PROFICIENCY SIGNALS
# ============================================================

PROFICIENCY_SIGNALS = {

    PROFICIENCY_AWARENESS: [

        "awareness",
        "familiarity",
        "familiar with",
        "exposure",
        "understanding",
        "knowledge of",
    ],

    PROFICIENCY_BEGINNER: [

        "basic",
        "beginner",
        "fundamentals",
        "introduction",
        "introductory",
        "learned",
        "learning",
    ],

    PROFICIENCY_INTERMEDIATE: [

        "intermediate",
        "practical",
        "hands-on",
        "implementation",
        "developed",
        "built",
        "used",
        "working knowledge",
    ],

    PROFICIENCY_ADVANCED: [

        "advanced",
        "advanced knowledge",
        "expertise",
        "designed",
        "architected",
        "deployed",
        "optimized",
        "production",
    ],

    PROFICIENCY_EXPERT: [

        "expert",
        "expertise",
        "lead",
        "led",
        "architect",
        "research",
        "specialist",
        "deep expertise",
    ],

}


# ============================================================
# SCORE PROFICIENCY
# ============================================================

def estimate_proficiency_from_text(
    skill: str,
    text: str,
) -> Tuple[
    str,
    float,
]:

    text = clean_text(
        text
    ).lower()

    canonical = canonical_skill(
        skill
    )

    if not text or not canonical:

        return (
            PROFICIENCY_UNKNOWN,
            0.0,
        )

    positions = []

    for phrase in (
        [canonical]
        +
        get_skill_aliases(
            canonical
        )
    ):

        match = re.search(

            re.escape(
                phrase
            ),

            text,

            flags=re.IGNORECASE,

        )

        if match:

            positions.append(
                match.start()
            )

    if not positions:

        return (
            PROFICIENCY_UNKNOWN,
            0.0,
        )

    scores = {

        level: 0

        for level
        in PROFICIENCY_SIGNALS
    }

    for position in positions:

        context = text[
            max(
                0,
                position - 150,
            ):
            min(
                len(text),
                position + 250,
            )
        ]

        for level, signals in (
            PROFICIENCY_SIGNALS.items()
        ):

            for signal in signals:

                if signal in context:

                    scores[
                        level
                    ] += 1

    if max(
        scores.values()
    ) == 0:

        # Presence itself is evidence of
        # at least awareness.
        return (
            PROFICIENCY_AWARENESS,
            45.0,
        )

    level = max(
        scores,
        key=scores.get,
    )

    raw_score = {

        PROFICIENCY_AWARENESS:
            35.0,

        PROFICIENCY_BEGINNER:
            50.0,

        PROFICIENCY_INTERMEDIATE:
            70.0,

        PROFICIENCY_ADVANCED:
            85.0,

        PROFICIENCY_EXPERT:
            95.0,

    }.get(
        level,
        0.0,
    )

    confidence = min(
        100.0,
        raw_score
        +
        (
            scores[level]
            *
            3.0
        ),
    )

    return (
        level,
        round(
            confidence,
            2,
        ),
    )


# ============================================================
# INFER PROFICIENCY FROM EVIDENCE
# ============================================================

def infer_skill_proficiency(
    profile: SkillProfile,
    text: str = "",
) -> SkillProfile:

    if text:

        level, score = (
            estimate_proficiency_from_text(

                profile.name,

                text,

            )
        )

    else:

        if profile.occurrence_count >= 5:

            level = PROFICIENCY_ADVANCED

            score = 85.0

        elif profile.occurrence_count >= 3:

            level = PROFICIENCY_INTERMEDIATE

            score = 70.0

        elif profile.occurrence_count >= 2:

            level = PROFICIENCY_BEGINNER

            score = 55.0

        else:

            level = PROFICIENCY_AWARENESS

            score = 40.0

    profile.proficiency = level

    profile.proficiency_score = score

    profile.confidence_score = max(

        profile.confidence_score,

        score,

    )

    return profile


# ============================================================
# PROJECT EVIDENCE
# ============================================================

def infer_project_evidence(
    skill: str,
    projects: Sequence[Any],
) -> List[SkillEvidence]:

    evidence = []

    for project in projects:

        if isinstance(
            project,
            str,
        ):

            text = project

        elif isinstance(
            project,
            dict,
        ):

            text = " ".join(

                str(
                    project.get(
                        key,
                        ""
                    )
                )

                for key in (

                    "name",
                    "title",
                    "description",
                    "technologies",
                    "tools",
                    "skills",

                )

            )

        else:

            text = str(
                project
            )

        if not phrase_present(
            text,
            skill,
        ):

            continue

        evidence.append(

            SkillEvidence(

                skill=skill,

                evidence_text=skill,

                evidence_type=EVIDENCE_PROJECT,

                confidence=90.0,

                source="project",

                context=text[:500],

            )

        )

    return evidence


# ============================================================
# TOOL EVIDENCE
# ============================================================

def infer_tool_evidence(
    skill: str,
    text: str,
) -> List[SkillEvidence]:

    canonical = canonical_skill(
        skill
    )

    evidence = []

    for tool in (
        get_skill_aliases(
            canonical
        )
    ):

        if not phrase_present(
            text,
            tool,
        ):

            continue

        evidence.append(

            SkillEvidence(

                skill=skill,

                evidence_text=tool,

                evidence_type=EVIDENCE_TOOL,

                confidence=88.0,

                source="tool",

                context=text[:500],

            )

        )

    return evidence


# ============================================================
# MERGE EVIDENCE
# ============================================================

def merge_skill_evidence(
    profile: SkillProfile,
    evidence: Sequence[SkillEvidence],
    max_items: int = 10,
) -> SkillProfile:

    existing = [

        item.evidence_text.lower()

        for item
        in profile.evidence

    ]

    for item in evidence:

        if (
            item.evidence_text.lower()
            in existing
        ):

            continue

        profile.evidence.append(
            item
        )

        existing.append(
            item.evidence_text.lower()
        )

    profile.evidence = profile.evidence[
        :max_items
    ]

    profile.evidence_count = len(
        profile.evidence
    )

    if profile.evidence_count:

        profile.confidence_score = max(

            profile.confidence_score,

            min(

                100.0,

                sum(

                    item.confidence

                    for item
                    in profile.evidence

                )
                /
                profile.evidence_count,

            ),

        )

    return profile


# ============================================================
# ENRICH PROFICIENCY
# ============================================================

def enrich_skill_proficiency(
    profile: SkillProfile,
    source_text: str = "",
) -> SkillProfile:

    profile = infer_skill_proficiency(

        profile,

        source_text,

    )

    if profile.proficiency_score >= 85:

        profile.status = SKILL_STRONG

    elif profile.proficiency_score >= 65:

        profile.status = SKILL_PRESENT

    elif profile.proficiency_score >= 45:

        profile.status = SKILL_WEAK

    else:

        profile.status = SKILL_PRESENT

    return profile


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# INDUSTRY + EMPLOYABILITY + EMERGING SKILLS
# ============================================================


# ============================================================
# HIGH INDUSTRY SKILLS
# ============================================================

HIGH_INDUSTRY_SKILLS = {

    "python",
    "sql",
    "machine learning",
    "deep learning",
    "generative ai",
    "large language models",
    "retrieval augmented generation",
    "ai agents",
    "agentic ai",
    "data engineering",
    "cloud architecture",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "mlops",
    "llmops",
    "cybersecurity",
    "computer vision",
    "natural language processing",
}


# ============================================================
# EMERGING SKILLS
# ============================================================

EMERGING_SKILLS = {

    "generative ai",
    "large language models",
    "retrieval augmented generation",
    "prompt engineering",
    "ai agents",
    "agentic ai",
    "multi agent systems",
    "llmops",
    "multimodal ai",
    "synthetic data",
    "vector databases",
    "llm evaluation",
    "ai evaluation",
    "vision language models",
    "small language models",
}


# ============================================================
# EMPLOYABILITY SKILLS
# ============================================================

HIGH_EMPLOYABILITY_SKILLS = {

    "python",
    "sql",
    "machine learning",
    "deep learning",
    "generative ai",
    "large language models",
    "rag",
    "retrieval augmented generation",
    "data analysis",
    "data engineering",
    "cloud",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "mlops",
    "api",
    "git",
    "computer vision",
    "natural language processing",
}


# ============================================================
# INDUSTRY RELEVANCE
# ============================================================

def estimate_skill_industry_relevance(
    skill: str,
    category: str = SKILL_OTHER,
) -> float:

    canonical = canonical_skill(
        skill
    )

    if canonical in HIGH_INDUSTRY_SKILLS:

        return 95.0

    score = 50.0

    high_categories = {

        SKILL_MACHINE_LEARNING,

        SKILL_DEEP_LEARNING,

        SKILL_GENERATIVE_AI,

        SKILL_AGENTIC_AI,

        SKILL_DATA_ENGINEERING,

        SKILL_MLOPS,

        SKILL_LLMOPS,

        SKILL_CLOUD,

        SKILL_CYBERSECURITY,

        SKILL_PROGRAMMING,

    }

    if category in high_categories:

        score += 20.0

    if category in {

        SKILL_TOOL,

        SKILL_FRAMEWORK,

        SKILL_LIBRARY,

        SKILL_PLATFORM,

    }:

        score += 10.0

    if canonical in EMERGING_SKILLS:

        score += 15.0

    return clamp(
        score
    )


# ============================================================
# EMPLOYABILITY
# ============================================================

def estimate_skill_employability(
    skill: str,
    category: str = SKILL_OTHER,
) -> float:

    canonical = canonical_skill(
        skill
    )

    if canonical in HIGH_EMPLOYABILITY_SKILLS:

        return 95.0

    score = 45.0

    if category in {

        SKILL_PROGRAMMING,

        SKILL_TECHNICAL,

        SKILL_TOOL,

        SKILL_FRAMEWORK,

        SKILL_MACHINE_LEARNING,

        SKILL_GENERATIVE_AI,

        SKILL_AGENTIC_AI,

        SKILL_DATA_ENGINEERING,

        SKILL_CLOUD,

        SKILL_MLOPS,

    }:

        score += 25.0

    if canonical in EMERGING_SKILLS:

        score += 15.0

    if category == SKILL_SOFT:

        score += 5.0

    return clamp(
        score
    )


# ============================================================
# EMERGING SCORE
# ============================================================

def calculate_skill_emerging_score(
    skill: str,
) -> float:

    canonical = canonical_skill(
        skill
    )

    if canonical in EMERGING_SKILLS:

        return 95.0

    emerging_terms = [

        "generative",

        "llm",

        "agent",

        "rag",

        "vector",

        "multimodal",

        "synthetic",

        "foundation model",

        "evaluation",

    ]

    matches = sum(

        1

        for term
        in emerging_terms

        if term in canonical

    )

    return clamp(

        35.0
        +
        matches * 12.0

    )


# ============================================================
# LEARNING IMPACT
# ============================================================

def estimate_skill_learning_impact(
    profile: SkillProfile,
) -> float:

    score = 40.0

    score += min(

        20.0,

        profile.industry_relevance
        *
        0.20,

    )

    score += min(

        20.0,

        profile.employability_impact
        *
        0.20,

    )

    score += min(

        15.0,

        profile.occurrence_count
        *
        3.0,

    )

    if profile.proficiency_score < 50:

        score += 10.0

    return clamp(
        score
    )


# ============================================================
# ENRICH INDUSTRY PROFILE
# ============================================================

def enrich_skill_industry(
    profile: SkillProfile,
) -> SkillProfile:

    profile.industry_relevance = (
        estimate_skill_industry_relevance(

            profile.name,

            profile.category,

        )
    )

    profile.employability_impact = (
        estimate_skill_employability(

            profile.name,

            profile.category,

        )
    )

    profile.emerging_score = (
        calculate_skill_emerging_score(
            profile.name
        )
    )

    profile.learning_impact = (
        estimate_skill_learning_impact(
            profile
        )
    )

    profile.importance = (
        classify_skill_importance(

            profile.name,

            profile.industry_relevance,

            profile.employability_impact,

        )
    )

    return profile


# ============================================================
# RELATED SKILLS
# ============================================================

RELATED_SKILLS = {

    "python": [

        "numpy",
        "pandas",
        "scikit-learn",
        "data analysis",
    ],

    "machine learning": [

        "statistics",
        "python",
        "feature engineering",
        "model evaluation",
    ],

    "deep learning": [

        "pytorch",
        "tensorflow",
        "neural networks",
        "transformers",
    ],

    "generative ai": [

        "large language models",
        "prompt engineering",
        "rag",
        "embeddings",
        "ai agents",
    ],

    "rag": [

        "embeddings",
        "vector databases",
        "large language models",
        "retrieval",
    ],

    "ai agents": [

        "tool calling",
        "function calling",
        "agent memory",
        "large language models",
    ],

    "mlops": [

        "docker",
        "kubernetes",
        "mlflow",
        "model deployment",
    ],

}


# ============================================================
# PREREQUISITES
# ============================================================

SKILL_PREREQUISITES = {

    "machine learning": [

        "python",
        "statistics",
        "probability",
        "linear algebra",
    ],

    "deep learning": [

        "python",
        "machine learning",
        "linear algebra",
    ],

    "generative ai": [

        "machine learning",
        "deep learning",
        "natural language processing",
    ],

    "large language models": [

        "deep learning",
        "transformers",
        "natural language processing",
    ],

    "retrieval augmented generation": [

        "large language models",
        "embeddings",
        "vector databases",
    ],

    "ai agents": [

        "large language models",
        "prompt engineering",
        "tool calling",
        "api",
    ],

    "agentic ai": [

        "large language models",
        "ai agents",
        "tool calling",
        "agent memory",
    ],

    "mlops": [

        "machine learning",
        "python",
        "git",
        "docker",
    ],

    "llmops": [

        "large language models",
        "generative ai",
        "docker",
        "cloud",
    ],

    "kubernetes": [

        "docker",
        "linux",
        "networking",
    ],

}


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# SKILL MATCHING ENGINE
# ============================================================


# ============================================================
# TOKEN OVERLAP
# ============================================================

def skill_token_overlap(
    source: str,
    target: str,
) -> float:

    source_tokens = set(

        re.split(

            r"[\s,;/|:+#.-]+",

            canonical_skill(
                source
            ),

        )

    )

    target_tokens = set(

        re.split(

            r"[\s,;/|:+#.-]+",

            canonical_skill(
                target
            ),

        )

    )

    source_tokens.discard("")
    target_tokens.discard("")

    if not source_tokens or not target_tokens:

        return 0.0

    union = (
        source_tokens
        |
        target_tokens
    )

    intersection = (
        source_tokens
        &
        target_tokens
    )

    return (
        len(intersection)
        /
        len(union)
    )


# ============================================================
# LEXICAL SIMILARITY
# ============================================================

def skill_lexical_similarity(
    source: str,
    target: str,
) -> float:

    source = canonical_skill(
        source
    )

    target = canonical_skill(
        target
    )

    if source == target:

        return 1.0

    if not source or not target:

        return 0.0

    token_score = skill_token_overlap(

        source,

        target,

    )

    source_chars = set(
        source
    )

    target_chars = set(
        target
    )

    if not source_chars or not target_chars:

        char_score = 0.0

    else:

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

    return (

        token_score * 0.7

        +

        char_score * 0.3

    )


# ============================================================
# TF-IDF SIMILARITY
# ============================================================

def skill_semantic_similarity(
    source: str,
    target: str,
) -> float:

    if (
        TfidfVectorizer is None
        or
        cosine_similarity is None
    ):

        return 0.0

    try:

        vectorizer = TfidfVectorizer()

        matrix = vectorizer.fit_transform([

            source,

            target,

        ])

        score = cosine_similarity(

            matrix[0:1],

            matrix[1:2],

        )[0][0]

        return float(
            score
        )

    except Exception:

        return 0.0


# ============================================================
# HYBRID SIMILARITY
# ============================================================

def skill_similarity(
    source: str,
    target: str,
) -> float:

    source_canonical = canonical_skill(
        source
    )

    target_canonical = canonical_skill(
        target
    )

    if (
        source_canonical
        ==
        target_canonical
    ):

        return 1.0

    lexical = skill_lexical_similarity(

        source,

        target,

    )

    overlap = skill_token_overlap(

        source,

        target,

    )

    semantic = skill_semantic_similarity(

        source,

        target,

    )

    if semantic <= 0:

        return round(

            lexical * 0.70
            +
            overlap * 0.30,

            4,

        )

    return round(

        lexical * 0.35
        +
        overlap * 0.20
        +
        semantic * 0.45,

        4,

    )


# ============================================================
# MATCH STATUS
# ============================================================

def determine_skill_match_status(
    similarity: float,
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> str:

    config = (
        config
        or
        SkillExtractorConfig()
    )

    if similarity >= config.similarity_threshold:

        return SKILL_PRESENT

    if similarity >= config.partial_similarity_threshold:

        return SKILL_PARTIAL

    return SKILL_MISSING


# ============================================================
# MATCH RATIONALE
# ============================================================

def build_skill_match_rationale(
    source: str,
    target: str,
    similarity: float,
    status: str,
) -> str:

    score = (
        similarity * 100.0
    )

    if status == SKILL_PRESENT:

        return (

            f"{source} strongly matches "
            f"{target} ({score:.1f}%)."

        )

    if status == SKILL_PARTIAL:

        return (

            f"{source} partially matches "
            f"{target} ({score:.1f}%)."

        )

    return (

        f"{source} does not sufficiently "
        f"match {target} ({score:.1f}%)."

    )


# ============================================================
# BUILD MATCH
# ============================================================

def build_skill_match(
    source: str,
    target: str,
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> SkillMatch:

    lexical = skill_lexical_similarity(

        source,

        target,

    )

    overlap = skill_token_overlap(

        source,

        target,

    )

    semantic = skill_semantic_similarity(

        source,

        target,

    )

    similarity = skill_similarity(

        source,

        target,

    )

    status = determine_skill_match_status(

        similarity,

        config,

    )

    return SkillMatch(

        source_skill=source,

        target_skill=target,

        similarity=round(

            similarity * 100.0,

            2,

        ),

        lexical_similarity=round(

            lexical * 100.0,

            2,

        ),

        token_overlap=round(

            overlap * 100.0,

            2,

        ),

        semantic_similarity=round(

            semantic * 100.0,

            2,

        ),

        status=status,

        confidence=round(

            similarity * 100.0,

            2,

        ),

        rationale=build_skill_match_rationale(

            source,

            target,

            similarity,

            status,

        ),

    )


# ============================================================
# BEST MATCH
# ============================================================

def find_best_skill_match(
    skill: str,
    candidates: Sequence[str],
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> Optional[SkillMatch]:

    if not candidates:

        return None

    best = None

    best_score = -1.0

    for candidate in deduplicate(
        candidates
    ):

        match = build_skill_match(

            skill,

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
# MATCH COLLECTIONS
# ============================================================

def match_skill_collections(
    source_skills: Sequence[str],
    target_skills: Sequence[str],
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> List[SkillMatch]:

    matches = []

    source_skills = normalize_skills(
        source_skills
    )

    target_skills = normalize_skills(
        target_skills
    )

    for skill in source_skills:

        best = find_best_skill_match(

            skill,

            target_skills,

            config,

        )

        if best is not None:

            matches.append(
                best
            )

    return matches


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# SKILL GAP ANALYSIS
# ============================================================


# ============================================================
# GAP PRIORITY
# ============================================================

def calculate_skill_gap_priority(
    skill: str,
    similarity: float,
    industry_relevance: float,
    employability_impact: float,
    learning_impact: float,
    prerequisite_impact: float,
) -> float:

    semantic_gap = (
        100.0
        -
        clamp(
            similarity
        )
    )

    score = (

        semantic_gap * 0.20

        +

        clamp(
            industry_relevance
        )
        * 0.30

        +

        clamp(
            employability_impact
        )
        * 0.30

        +

        clamp(
            learning_impact
        )
        * 0.10

        +

        clamp(
            prerequisite_impact
        )
        * 0.10

    )

    return round(
        clamp(
            score
        ),
        2,
    )


# ============================================================
# SEVERITY
# ============================================================

def determine_gap_severity(
    priority: float,
) -> str:

    if priority >= 85:

        return IMPORTANCE_CRITICAL

    if priority >= 70:

        return IMPORTANCE_HIGH

    if priority >= 45:

        return IMPORTANCE_MEDIUM

    return IMPORTANCE_LOW


# ============================================================
# PREREQUISITES
# ============================================================

def get_skill_prerequisites(
    skill: str,
) -> List[str]:

    canonical = canonical_skill(
        skill
    )

    prerequisites = (
        SKILL_PREREQUISITES.get(
            canonical,
            [],
        )
    )

    return deduplicate(
        prerequisites
    )


# ============================================================
# TRANSITIVE PREREQUISITES
# ============================================================

def get_transitive_skill_prerequisites(
    skill: str,
    max_depth: int = 3,
) -> List[str]:

    result = []

    visited = set()

    def visit(
        current: str,
        depth: int,
    ):

        if depth > max_depth:

            return

        canonical = canonical_skill(
            current
        )

        if canonical in visited:

            return

        visited.add(
            canonical
        )

        for prerequisite in (
            get_skill_prerequisites(
                canonical
            )
        ):

            result.append(
                prerequisite
            )

            visit(

                prerequisite,

                depth + 1,

            )

    visit(
        skill,
        0,
    )

    return deduplicate(
        result
    )


# ============================================================
# PREREQUISITE IMPACT
# ============================================================

def calculate_skill_prerequisite_impact(
    skill: str,
) -> float:

    direct = get_skill_prerequisites(
        skill
    )

    transitive = (
        get_transitive_skill_prerequisites(
            skill
        )
    )

    return clamp(

        min(
            60.0,
            len(
                direct
            ) * 15.0,
        )
        +
        min(
            40.0,
            len(
                transitive
            ) * 5.0,
        )

    )


# ============================================================
# RECOMMENDED TOPICS
# ============================================================

def recommend_skill_topics(
    skill: str,
) -> List[str]:

    canonical = canonical_skill(
        skill
    )

    topics = [

        f"{canonical} fundamentals",

        f"{canonical} implementation",

        f"{canonical} best practices",

    ]

    if canonical in {

        "machine learning",
        "deep learning",

    }:

        topics.extend([

            f"{canonical} model training",

            f"{canonical} evaluation",

            f"{canonical} optimization",

        ])

    if (
        "generative ai" in canonical
        or
        "large language" in canonical
    ):

        topics.extend([

            f"{canonical} prompting",

            f"{canonical} evaluation",

            f"{canonical} deployment",

        ])

    if (
        "agent" in canonical
    ):

        topics.extend([

            "tool calling",

            "agent memory",

            "agent orchestration",

        ])

    return deduplicate(
        topics
    )


# ============================================================
# RECOMMENDED TOOLS
# ============================================================

def recommend_skill_tools(
    skill: str,
) -> List[str]:

    canonical = canonical_skill(
        skill
    )

    mapping = {

        "python": [
            "Jupyter",
            "VS Code",
        ],

        "machine learning": [
            "Python",
            "scikit-learn",
            "Jupyter",
        ],

        "deep learning": [
            "PyTorch",
            "TensorFlow",
            "Jupyter",
        ],

        "generative ai": [
            "Hugging Face",
            "LangChain",
            "Ollama",
        ],

        "large language models": [
            "Hugging Face",
            "Transformers",
            "Ollama",
        ],

        "retrieval augmented generation": [
            "LangChain",
            "LlamaIndex",
            "FAISS",
            "Chroma",
        ],

        "ai agents": [
            "LangChain",
            "LangGraph",
        ],

        "mlops": [
            "MLflow",
            "Docker",
            "Kubernetes",
        ],

        "llmops": [
            "Docker",
            "Kubernetes",
            "MLflow",
        ],

        "computer vision": [
            "OpenCV",
            "PyTorch",
            "YOLO",
        ],

        "data engineering": [
            "Apache Spark",
            "Apache Kafka",
            "Apache Airflow",
        ],

        "cloud": [
            "AWS",
            "Azure",
            "GCP",
        ],

    }

    return deduplicate(

        mapping.get(

            canonical,

            [],

        )

    )


# ============================================================
# PROJECT RECOMMENDATION
# ============================================================

def recommend_skill_project(
    skill: str,
) -> str:

    canonical = canonical_skill(
        skill
    )

    if canonical == "machine learning":

        return (
            "End-to-End Machine Learning "
            "Prediction Platform"
        )

    if canonical == "deep learning":

        return (
            "Deep Learning Image or Text "
            "Classification System"
        )

    if canonical in {

        "generative ai",
        "large language models",

    }:

        return (
            "Domain-Specific Generative AI Assistant"
        )

    if canonical in {

        "retrieval augmented generation",

        "rag",

    }:

        return (
            "Enterprise Document RAG Assistant"
        )

    if canonical in {

        "ai agents",
        "agentic ai",

    }:

        return (
            "Multi-Agent Business Automation System"
        )

    if canonical == "computer vision":

        return (
            "Real-Time Computer Vision "
            "Detection Application"
        )

    if canonical == "mlops":

        return (
            "Production ML Deployment "
            "and Monitoring Platform"
        )

    if canonical == "data engineering":

        return (
            "End-to-End Real-Time Data Pipeline"
        )

    return (
        f"Industry Application using {skill}"
    )


# ============================================================
# BUILD GAP
# ============================================================

def build_skill_gap(
    skill: str,
    target_skills: Sequence[str],
    available_skills: Sequence[str],
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> SkillGap:

    config = (
        config
        or
        SkillExtractorConfig()
    )

    profile = build_skill_profile(
        skill
    )

    profile = enrich_skill_industry(
        profile
    )

    best_match = find_best_skill_match(

        skill,

        target_skills,

        config,

    )

    similarity = (

        best_match.similarity

        if best_match

        else 0.0

    )

    prerequisite_impact = (
        calculate_skill_prerequisite_impact(
            skill
        )
    )

    priority = calculate_skill_gap_priority(

        skill,

        similarity,

        profile.industry_relevance,

        profile.employability_impact,

        profile.learning_impact,

        prerequisite_impact,

    )

    gap_type = SKILL_MISSING

    if best_match:

        if best_match.status == SKILL_PARTIAL:

            gap_type = SKILL_PARTIAL

        elif best_match.status == SKILL_PRESENT:

            gap_type = SKILL_PRESENT

    return SkillGap(

        skill=skill,

        category=profile.category,

        gap_type=gap_type,

        severity=determine_gap_severity(
            priority
        ),

        priority_score=priority,

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
            prerequisite_impact
        ),

        best_match=(

            best_match.target_skill

            if best_match

            else None

        ),

        prerequisites=(
            get_skill_prerequisites(
                skill
            )
        ),

        recommended_topics=(
            recommend_skill_topics(
                skill
            )
        ),

        recommended_tools=(
            recommend_skill_tools(
                skill
            )
        ),

        recommended_project=(
            recommend_skill_project(
                skill
            )
        ),

        rationale=(

            f"{skill} has a skill-gap priority "
            f"of {priority:.1f}/100."

        ),

        metadata={

            "missing_prerequisites": [

                item

                for item
                in get_transitive_skill_prerequisites(
                    skill
                )

                if canonical_skill(
                    item
                )
                not in {

                    canonical_skill(
                        existing
                    )

                    for existing
                    in available_skills

                }

            ],

        },

    )


# ============================================================
# IDENTIFY GAPS
# ============================================================

def identify_skill_gaps(
    source_skills: Sequence[str],
    target_skills: Sequence[str],
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> List[SkillGap]:

    config = (
        config
        or
        SkillExtractorConfig()
    )

    source_skills = normalize_skills(
        source_skills
    )

    target_skills = normalize_skills(
        target_skills
    )

    gaps = []

    for skill in source_skills:

        gap = build_skill_gap(

            skill,

            target_skills,

            source_skills,

            config,

        )

        if gap.gap_type == SKILL_PRESENT:

            continue

        gaps.append(
            gap
        )

    return sorted(

        gaps,

        key=lambda item: (

            item.priority_score,

            item.employability_impact,

        ),

        reverse=True,

    )


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# SKILL RECOMMENDATIONS
# ============================================================


# ============================================================
# ESTIMATE HOURS
# ============================================================

def estimate_skill_learning_hours(
    profile: SkillProfile,
) -> float:

    level_hours = {

        PROFICIENCY_UNKNOWN:
            8.0,

        PROFICIENCY_AWARENESS:
            8.0,

        PROFICIENCY_BEGINNER:
            10.0,

        PROFICIENCY_INTERMEDIATE:
            15.0,

        PROFICIENCY_ADVANCED:
            20.0,

        PROFICIENCY_EXPERT:
            25.0,

    }

    hours = level_hours.get(

        profile.proficiency,

        10.0,

    )

    if profile.category in {

        SKILL_TOOL,
        SKILL_FRAMEWORK,
        SKILL_LIBRARY,

    }:

        hours += 5.0

    if profile.category in {

        SKILL_GENERATIVE_AI,
        SKILL_AGENTIC_AI,
        SKILL_MLOPS,
        SKILL_LLMOPS,

    }:

        hours += 5.0

    return round(
        hours,
        1,
    )


# ============================================================
# LEARNING ACTIVITIES
# ============================================================

def recommend_skill_activities(
    profile: SkillProfile,
) -> List[str]:

    activities = [

        "Concept explanation",

        "Hands-on exercises",

        "Practical implementation",

    ]

    if profile.category in {

        SKILL_PROGRAMMING,
        SKILL_TOOL,
        SKILL_FRAMEWORK,
        SKILL_LIBRARY,

    }:

        activities.extend([

            "Coding laboratory",

            "Debugging exercise",

            "Mini project",

        ])

    if profile.category in {

        SKILL_MACHINE_LEARNING,
        SKILL_DEEP_LEARNING,

    }:

        activities.extend([

            "Dataset analysis",

            "Model training",

            "Model evaluation",

        ])

    if profile.category in {

        SKILL_GENERATIVE_AI,
        SKILL_AGENTIC_AI,
        SKILL_LLMOPS,

    }:

        activities.extend([

            "Prompt engineering lab",

            "LLM application lab",

            "Agent workflow exercise",

        ])

    if profile.category == SKILL_SOFT:

        activities.extend([

            "Role-play",

            "Group exercise",

            "Presentation",

        ])

    return deduplicate(
        activities
    )


# ============================================================
# BUILD RECOMMENDATION
# ============================================================

def build_skill_recommendation(
    profile: SkillProfile,
    recommendation_type: str = REC_LEARN,
) -> SkillRecommendation:

    hours = estimate_skill_learning_hours(
        profile
    )

    impact = (

        profile.industry_relevance * 0.30

        +

        profile.employability_impact * 0.35

        +

        profile.learning_impact * 0.20

        +

        profile.emerging_score * 0.15

    )

    if recommendation_type == REC_ADVANCE:

        title = (
            f"Advance {profile.name}"
        )

        description = (

            f"Move from {profile.proficiency} "
            f"toward advanced practical competency "
            f"in {profile.name}."

        )

    elif recommendation_type == REC_PRACTICE:

        title = (
            f"Practice {profile.name}"
        )

        description = (

            f"Strengthen practical ability in "
            f"{profile.name} through hands-on "
            f"implementation."

        )

    else:

        title = (
            f"Learn {profile.name}"
        )

        description = (

            f"Build job-ready competency in "
            f"{profile.name}."

        )

    return SkillRecommendation(

        skill=profile.name,

        recommendation_type=(
            recommendation_type
        ),

        title=title,

        description=description,

        priority=profile.importance,

        estimated_hours=hours,

        prerequisites=(
            get_skill_prerequisites(
                profile.name
            )
        ),

        topics=(
            recommend_skill_topics(
                profile.name
            )
        ),

        activities=(
            recommend_skill_activities(
                profile
            )
        ),

        tools=(
            recommend_skill_tools(
                profile.name
            )
        ),

        project=(
            recommend_skill_project(
                profile.name
            )
        ),

        expected_impact=round(

            clamp(
                impact
            ),

            2,

        ),

        metadata={

            "category":
                profile.category,

            "proficiency":
                profile.proficiency,

            "industry_relevance":
                profile.industry_relevance,

            "employability":
                profile.employability_impact,

        },

    )


# ============================================================
# BUILD RECOMMENDATIONS
# ============================================================

def build_skill_recommendations(
    profiles: Sequence[SkillProfile],
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> List[SkillRecommendation]:

    config = (
        config
        or
        SkillExtractorConfig()
    )

    sorted_profiles = sorted(

        profiles,

        key=lambda profile: (

            profile.industry_relevance,

            profile.employability_impact,

            profile.learning_impact,

        ),

        reverse=True,

    )

    recommendations = []

    for profile in sorted_profiles:

        if profile.proficiency_score < 50:

            recommendation_type = (
                REC_LEARN
            )

        elif profile.proficiency_score < 75:

            recommendation_type = (
                REC_PRACTICE
            )

        else:

            recommendation_type = (
                REC_ADVANCE
            )

        recommendations.append(

            build_skill_recommendation(

                profile,

                recommendation_type,

            )

        )

        if len(
            recommendations
        ) >= config.max_recommendations:

            break

    return recommendations


# ============================================================
# CURRICULUM OBJECT EXTRACTION
# ============================================================

def extract_skills_from_curriculum(
    curriculum: Any,
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> Tuple[
    List[str],
    List[SkillEvidence],
]:

    config = (
        config
        or
        SkillExtractorConfig()
    )

    if curriculum is None:

        return [], []

    if isinstance(
        curriculum,
        str,
    ):

        return extract_skills_from_text(

            curriculum,

            config,

            "curriculum",

        )

    if isinstance(
        curriculum,
        (list, tuple, set),
    ):

        return extract_skills_from_items(

            list(curriculum),

            config,

            "curriculum",

        )

    skills = []

    evidence = []

    if isinstance(
        curriculum,
        dict,
    ):

        fields = [

            "name",
            "title",
            "description",
            "content",
            "modules",
            "topics",
            "skills",
            "technologies",
            "tools",
            "projects",
            "outcomes",
            "course_outcomes",
            "program_outcomes",

        ]

        for field_name in fields:

            if field_name not in curriculum:

                continue

            value = curriculum.get(
                field_name
            )

            if isinstance(
                value,
                (list, tuple, set),
            ):

                s, e = extract_skills_from_items(

                    list(value),

                    config,

                    f"curriculum.{field_name}",

                )

            else:

                s, e = extract_skills_from_text(

                    str(value),

                    config,

                    f"curriculum.{field_name}",

                )

            skills.extend(
                s
            )

            evidence.extend(
                e
            )

    else:

        fields = [

            "name",
            "title",
            "description",
            "content",
            "modules",
            "topics",
            "skills",
            "technologies",
            "tools",
            "projects",
            "outcomes",
            "course_outcomes",
            "program_outcomes",

        ]

        for field_name in fields:

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
                (list, tuple, set),
            ):

                s, e = extract_skills_from_items(

                    list(value),

                    config,

                    f"curriculum.{field_name}",

                )

            else:

                s, e = extract_skills_from_text(

                    str(value),

                    config,

                    f"curriculum.{field_name}",

                )

            skills.extend(
                s
            )

            evidence.extend(
                e
            )

    return (

        normalize_skills(
            skills
        ),

        evidence,

    )


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# MAIN PIPELINE
# SERIALIZATION
# REPORTING
# VALIDATION
# PUBLIC API
# ============================================================


# ============================================================
# ENRICH PROFILE
# ============================================================

def enrich_skill_profile(
    profile: SkillProfile,
    source_text: str = "",
    projects: Optional[
        Sequence[Any]
    ] = None,
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> SkillProfile:

    config = (
        config
        or
        SkillExtractorConfig()
    )

    profile = enrich_skill_industry(
        profile
    )

    profile = enrich_skill_proficiency(

        profile,

        source_text,

    )

    # Related skills.
    related = RELATED_SKILLS.get(

        canonical_skill(
            profile.name
        ),

        [],

    )

    profile.related_skills = deduplicate(

        profile.related_skills
        +
        related

    )

    # Prerequisites.
    profile.prerequisite_skills = (
        get_skill_prerequisites(
            profile.name
        )
    )

    # Recommended tools.
    if config.include_tools:

        profile.tools = deduplicate(

            profile.tools
            +
            recommend_skill_tools(
                profile.name
            )

        )

    # Project evidence.
    if projects and config.include_projects:

        project_evidence = (
            infer_project_evidence(

                profile.name,

                projects,

            )
        )

        profile = merge_skill_evidence(

            profile,

            project_evidence,

            config.max_evidence_per_skill,

        )

        if project_evidence:

            profile.projects.append(
                recommend_skill_project(
                    profile.name
                )
            )

    # Tool evidence.
    if source_text:

        tool_evidence = infer_tool_evidence(

            profile.name,

            source_text,

        )

        profile = merge_skill_evidence(

            profile,

            tool_evidence,

            config.max_evidence_per_skill,

        )

    # Confidence.
    evidence_score = (

        min(
            100.0,
            profile.evidence_count
            * 15.0,
        )

    )

    profile.confidence_score = max(

        profile.confidence_score,

        evidence_score,

    )

    profile.confidence_score = clamp(

        profile.confidence_score

    )

    return profile


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_skills(
    text: Optional[str] = None,
    curriculum: Any = None,
    target_skills: Optional[
        Sequence[str]
    ] = None,
    projects: Optional[
        Sequence[Any]
    ] = None,
    config: Optional[
        SkillExtractorConfig
    ] = None,
) -> SkillExtractionResult:

    config = (
        config
        or
        SkillExtractorConfig()
    )

    all_skills = []

    all_evidence = []

    source_text = clean_text(
        text
    )

    # --------------------------------------------------------
    # Raw text
    # --------------------------------------------------------

    if source_text:

        skills, evidence = (
            extract_skills_from_text(

                source_text,

                config,

                "text",

            )
        )

        all_skills.extend(
            skills
        )

        all_evidence.extend(
            evidence
        )

    # --------------------------------------------------------
    # Curriculum
    # --------------------------------------------------------

    if curriculum is not None:

        skills, evidence = (
            extract_skills_from_curriculum(

                curriculum,

                config,

            )
        )

        all_skills.extend(
            skills
        )

        all_evidence.extend(
            evidence
        )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    if projects:

        skills, evidence = (
            extract_skills_from_items(

                list(projects),

                config,

                "projects",

            )
        )

        all_skills.extend(
            skills
        )

        all_evidence.extend(
            evidence
        )

    all_skills = normalize_skills(
        all_skills
    )

    # --------------------------------------------------------
    # Profiles
    # --------------------------------------------------------

    profiles = build_skill_profiles(

        all_skills,

        all_evidence,

    )

    profiles = [

        enrich_skill_profile(

            profile,

            source_text,

            projects,

            config,

        )

        for profile
        in profiles

    ]

    # --------------------------------------------------------
    # Target matching
    # --------------------------------------------------------

    target_skills = normalize_skills(

        target_skills
        or
        []

    )

    matches = []

    gaps = []

    if target_skills:

        matches = match_skill_collections(

            all_skills,

            target_skills,

            config,

        )

        gaps = identify_skill_gaps(

            all_skills,

            target_skills,

            config,

        )

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = (
        build_skill_recommendations(

            profiles,

            config,

        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = build_skill_summary(

        profiles,

        matches,

        gaps,

        recommendations,

    )

    return SkillExtractionResult(

        skills=profiles,

        evidence=all_evidence,

        matches=matches,

        gaps=gaps,

        recommendations=recommendations,

        summary=summary,

        metadata={

            "version":
                SKILL_EXTRACTOR_VERSION,

            "skill_count":
                len(profiles),

            "evidence_count":
                len(all_evidence),

            "match_count":
                len(matches),

            "gap_count":
                len(gaps),

            "recommendation_count":
                len(recommendations),

        },

    )


# ============================================================
# SUMMARY
# ============================================================

def build_skill_summary(
    profiles: Sequence[SkillProfile],
    matches: Sequence[SkillMatch],
    gaps: Sequence[SkillGap],
    recommendations: Sequence[SkillRecommendation],
) -> Dict[str, Any]:

    categories = {}

    proficiency = {}

    emerging = 0

    high_industry = 0

    high_employability = 0

    strong = 0

    weak = 0

    for profile in profiles:

        categories[
            profile.category
        ] = (

            categories.get(
                profile.category,
                0,
            )
            +
            1

        )

        proficiency[
            profile.proficiency
        ] = (

            proficiency.get(
                profile.proficiency,
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

        if profile.status == SKILL_STRONG:

            strong += 1

        if profile.status == SKILL_WEAK:

            weak += 1

    present = sum(

        1

        for match
        in matches

        if match.status == SKILL_PRESENT

    )

    partial = sum(

        1

        for match
        in matches

        if match.status == SKILL_PARTIAL

    )

    total = len(
        profiles
    )

    return {

        "total_skills":
            total,

        "categories":
            categories,

        "proficiency_distribution":
            proficiency,

        "emerging_skills":
            emerging,

        "high_industry_relevance":
            high_industry,

        "high_employability":
            high_employability,

        "strong_skills":
            strong,

        "weak_skills":
            weak,

        "matched_skills":
            present,

        "partial_skills":
            partial,

        "skill_gaps":
            len(gaps),

        "recommendations":
            len(recommendations),

        "average_proficiency": round(

            (
                sum(

                    profile.proficiency_score

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

    }


# ============================================================
# TOP SKILLS
# ============================================================

def get_top_skills(
    result: SkillExtractionResult,
    limit: int = 10,
) -> List[SkillProfile]:

    return sorted(

        result.skills,

        key=lambda skill: (

            skill.employability_impact,

            skill.industry_relevance,

            skill.confidence_score,

        ),

        reverse=True,

    )[:max(
        1,
        limit,
    )]


# ============================================================
# TOP GAPS
# ============================================================

def get_top_skill_gaps(
    result: SkillExtractionResult,
    limit: int = 10,
) -> List[SkillGap]:

    return sorted(

        result.gaps,

        key=lambda gap: (

            gap.priority_score,

            gap.employability_impact,

        ),

        reverse=True,

    )[:max(
        1,
        limit,
    )]


# ============================================================
# EMERGING SKILLS
# ============================================================

def get_emerging_skills(
    result: SkillExtractionResult,
    threshold: float = 65.0,
) -> List[SkillProfile]:

    return [

        skill

        for skill
        in result.skills

        if skill.emerging_score >= threshold

    ]


# ============================================================
# HIGH EMPLOYABILITY SKILLS
# ============================================================

def get_high_employability_skills(
    result: SkillExtractionResult,
    threshold: float = 80.0,
) -> List[SkillProfile]:

    return [

        skill

        for skill
        in result.skills

        if skill.employability_impact >= threshold

    ]


# ============================================================
# DASHBOARD DATA
# ============================================================

def build_skill_dashboard_data(
    result: SkillExtractionResult,
) -> Dict[str, Any]:

    skills = []

    for profile in result.skills:

        skills.append({

            "skill":
                profile.name,

            "category":
                profile.category,

            "subcategory":
                profile.subcategory,

            "proficiency":
                profile.proficiency,

            "proficiency_score":
                profile.proficiency_score,

            "confidence":
                profile.confidence_score,

            "industry_relevance":
                profile.industry_relevance,

            "employability":
                profile.employability_impact,

            "emerging_score":
                profile.emerging_score,

            "learning_impact":
                profile.learning_impact,

            "importance":
                profile.importance,

            "status":
                profile.status,

        })

    gaps = [

        {

            "skill":
                gap.skill,

            "category":
                gap.category,

            "severity":
                gap.severity,

            "priority":
                gap.priority_score,

            "similarity":
                gap.similarity,

            "industry_relevance":
                gap.industry_relevance,

            "employability":
                gap.employability_impact,

        }

        for gap
        in result.gaps

    ]

    category_distribution = {}

    for profile in result.skills:

        category = profile.category

        category_distribution[
            category
        ] = (

            category_distribution.get(
                category,
                0,
            )
            +
            1

        )

    return {

        "skills":
            skills,

        "gaps":
            gaps,

        "category_distribution":
            category_distribution,

        "summary":
            result.summary,

    }


# ============================================================
# SERIALIZATION
# ============================================================

def skill_profile_to_dict(
    profile: SkillProfile,
) -> Dict[str, Any]:

    return asdict(
        profile
    )


def skill_evidence_to_dict(
    evidence: SkillEvidence,
) -> Dict[str, Any]:

    return asdict(
        evidence
    )


def skill_match_to_dict(
    match: SkillMatch,
) -> Dict[str, Any]:

    return asdict(
        match
    )


def skill_gap_to_dict(
    gap: SkillGap,
) -> Dict[str, Any]:

    return asdict(
        gap
    )


def skill_recommendation_to_dict(
    recommendation: SkillRecommendation,
) -> Dict[str, Any]:

    return asdict(
        recommendation
    )


def skill_result_to_dict(
    result: SkillExtractionResult,
) -> Dict[str, Any]:

    return {

        "skills": [

            skill_profile_to_dict(
                item
            )

            for item
            in result.skills

        ],

        "evidence": [

            skill_evidence_to_dict(
                item
            )

            for item
            in result.evidence

        ],

        "matches": [

            skill_match_to_dict(
                item
            )

            for item
            in result.matches

        ],

        "gaps": [

            skill_gap_to_dict(
                item
            )

            for item
            in result.gaps

        ],

        "recommendations": [

            skill_recommendation_to_dict(
                item
            )

            for item
            in result.recommendations

        ],

        "summary":
            result.summary,

        "metadata":
            result.metadata,

    }


# ============================================================
# JSON
# ============================================================

def skill_result_to_json(
    result: SkillExtractionResult,
    indent: int = 2,
) -> str:

    return json.dumps(

        skill_result_to_dict(
            result
        ),

        indent=indent,

        ensure_ascii=False,

        default=str,

    )


def save_skill_result_json(
    result: SkillExtractionResult,
    file_path: Union[
        str,
        Path,
    ],
) -> Path:

    path = Path(
        file_path
    )

    path.parent.mkdir(

        parents=True,

        exist_ok=True,

    )

    path.write_text(

        skill_result_to_json(
            result
        ),

        encoding="utf-8",

    )

    return path


# ============================================================
# VALIDATION
# ============================================================

def validate_skill_profile(
    profile: SkillProfile,
) -> List[str]:

    errors = []

    if not profile.name:

        errors.append(
            "Skill name is missing."
        )

    if not profile.skill_id:

        errors.append(
            "Skill ID is missing."
        )

    numerical_fields = {

        "proficiency_score":
            profile.proficiency_score,

        "confidence_score":
            profile.confidence_score,

        "industry_relevance":
            profile.industry_relevance,

        "employability_impact":
            profile.employability_impact,

        "emerging_score":
            profile.emerging_score,

        "learning_impact":
            profile.learning_impact,

    }

    for name, value in (
        numerical_fields.items()
    ):

        if not (
            0.0
            <=
            safe_float(
                value
            )
            <=
            100.0
        ):

            errors.append(

                f"{name} must be between 0 and 100."

            )

    return errors


def validate_skill_result(
    result: SkillExtractionResult,
) -> Dict[str, List[str]]:

    errors = {

        "skills": [],

        "evidence": [],

        "matches": [],

        "gaps": [],

        "recommendations": [],

    }

    for profile in result.skills:

        errors[
            "skills"
        ].extend(

            validate_skill_profile(
                profile
            )

        )

    for evidence in result.evidence:

        if not evidence.skill:

            errors[
                "evidence"
            ].append(
                "Evidence skill is missing."
            )

    for match in result.matches:

        if not match.source_skill:

            errors[
                "matches"
            ].append(
                "Source skill is missing."
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
                "Invalid match similarity."
            )

    for gap in result.gaps:

        if not gap.skill:

            errors[
                "gaps"
            ].append(
                "Gap skill is missing."
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
                "Invalid gap priority."
            )

    for recommendation in result.recommendations:

        if not recommendation.skill:

            errors[
                "recommendations"
            ].append(
                "Recommendation skill is missing."
            )

    return errors


# ============================================================
# QUICK SUMMARY
# ============================================================

def skill_quick_summary(
    result: SkillExtractionResult,
) -> Dict[str, Any]:

    summary = result.summary

    return {

        "skills":
            summary.get(
                "total_skills",
                0,
            ),

        "gaps":
            summary.get(
                "skill_gaps",
                0,
            ),

        "emerging":
            summary.get(
                "emerging_skills",
                0,
            ),

        "high_employability":
            summary.get(
                "high_employability",
                0,
            ),

        "average_proficiency":
            summary.get(
                "average_proficiency",
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
# PUBLIC ALIASES
# ============================================================

extract_skills = (
    extract_skills_from_text
)

build_profiles = (
    build_skill_profiles
)

find_gaps = (
    identify_skill_gaps
)

match_skills = (
    match_skill_collections
)


# ============================================================
# CAPABILITIES
# ============================================================

SKILL_EXTRACTOR_CAPABILITIES = [

    "skill_extraction",

    "skill_normalization",

    "skill_classification",

    "technical_skill_detection",

    "programming_skill_detection",

    "tool_detection",

    "framework_detection",

    "soft_skill_detection",

    "cloud_skill_detection",

    "database_skill_detection",

    "ml_skill_detection",

    "deep_learning_skill_detection",

    "generative_ai_skill_detection",

    "agentic_ai_skill_detection",

    "nlp_skill_detection",

    "computer_vision_skill_detection",

    "data_engineering_skill_detection",

    "mlops_skill_detection",

    "llmops_skill_detection",

    "proficiency_estimation",

    "evidence_extraction",

    "industry_relevance",

    "employability_analysis",

    "emerging_skill_detection",

    "skill_similarity",

    "skill_matching",

    "skill_gap_detection",

    "gap_prioritization",

    "prerequisite_analysis",

    "learning_recommendations",

    "project_recommendations",

    "dashboard_data",

    "json_export",

    "validation",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Config
    "SkillExtractorConfig",

    # Models
    "SkillEvidence",
    "SkillProfile",
    "SkillMatch",
    "SkillGap",
    "SkillRecommendation",
    "SkillExtractionResult",

    # Extraction
    "extract_skills",
    "extract_skills_from_text",
    "extract_skills_from_items",
    "extract_skills_from_curriculum",
    "extract_dictionary_skills",
    "extract_candidate_skills",

    # Classification
    "classify_skill_category",
    "classify_skill_subcategory",
    "classify_skill_importance",
    "get_skill_aliases",
    "get_skill_keywords",
    "normalize_skills",

    # Profiles
    "build_skill_profile",
    "build_skill_profiles",
    "build_profiles",
    "enrich_skill_profile",

    # Proficiency
    "estimate_proficiency_from_text",
    "infer_skill_proficiency",
    "enrich_skill_proficiency",

    # Evidence
    "find_skill_evidence_in_text",
    "infer_project_evidence",
    "infer_tool_evidence",
    "merge_skill_evidence",

    # Industry
    "estimate_skill_industry_relevance",
    "estimate_skill_employability",
    "calculate_skill_emerging_score",
    "estimate_skill_learning_impact",

    # Matching
    "skill_similarity",
    "skill_lexical_similarity",
    "skill_token_overlap",
    "skill_semantic_similarity",
    "build_skill_match",
    "find_best_skill_match",
    "match_skill_collections",
    "match_skills",

    # Gaps
    "get_skill_prerequisites",
    "get_transitive_skill_prerequisites",
    "calculate_skill_prerequisite_impact",
    "calculate_skill_gap_priority",
    "build_skill_gap",
    "identify_skill_gaps",
    "find_gaps",

    # Recommendations
    "estimate_skill_learning_hours",
    "recommend_skill_topics",
    "recommend_skill_tools",
    "recommend_skill_project",
    "recommend_skill_activities",
    "build_skill_recommendation",
    "build_skill_recommendations",

    # Main pipeline
    "analyze_skills",

    # Reporting
    "build_skill_summary",
    "get_top_skills",
    "get_top_skill_gaps",
    "get_emerging_skills",
    "get_high_employability_skills",
    "build_skill_dashboard_data",
    "skill_quick_summary",

    # Serialization
    "skill_profile_to_dict",
    "skill_evidence_to_dict",
    "skill_match_to_dict",
    "skill_gap_to_dict",
    "skill_recommendation_to_dict",
    "skill_result_to_dict",
    "skill_result_to_json",
    "save_skill_result_json",

    # Validation
    "validate_skill_profile",
    "validate_skill_result",

    # Constants
    "SKILL_TECHNICAL",
    "SKILL_PROGRAMMING",
    "SKILL_MACHINE_LEARNING",
    "SKILL_DEEP_LEARNING",
    "SKILL_GENERATIVE_AI",
    "SKILL_AGENTIC_AI",
    "SKILL_NLP",
    "SKILL_COMPUTER_VISION",
    "SKILL_DATA_SCIENCE",
    "SKILL_DATA_ENGINEERING",
    "SKILL_MLOPS",
    "SKILL_LLMOPS",
    "SKILL_CLOUD",
    "SKILL_DATABASE",
    "SKILL_DEVOPS",
    "SKILL_CYBERSECURITY",
    "SKILL_SOFTWARE_ENGINEERING",
    "SKILL_BUSINESS_INTELLIGENCE",
    "SKILL_ANALYTICS",
    "SKILL_TOOL",
    "SKILL_FRAMEWORK",
    "SKILL_LIBRARY",
    "SKILL_PLATFORM",
    "SKILL_DOMAIN",
    "SKILL_SOFT",
    "SKILL_COMMUNICATION",
    "SKILL_LEADERSHIP",
    "SKILL_MANAGEMENT",
    "SKILL_PROBLEM_SOLVING",
    "SKILL_OTHER",

    # Proficiency
    "PROFICIENCY_UNKNOWN",
    "PROFICIENCY_AWARENESS",
    "PROFICIENCY_BEGINNER",
    "PROFICIENCY_INTERMEDIATE",
    "PROFICIENCY_ADVANCED",
    "PROFICIENCY_EXPERT",

    # Status
    "SKILL_PRESENT",
    "SKILL_MISSING",
    "SKILL_PARTIAL",
    "SKILL_WEAK",
    "SKILL_STRONG",
    "SKILL_EMERGING",
    "SKILL_OUTDATED",

    # Evidence
    "EVIDENCE_EXPLICIT",
    "EVIDENCE_CONTEXTUAL",
    "EVIDENCE_PROJECT",
    "EVIDENCE_TOOL",
    "EVIDENCE_OUTCOME",
    "EVIDENCE_EXPERIENCE",
    "EVIDENCE_CERTIFICATION",

    # Recommendation types
    "REC_LEARN",
    "REC_PRACTICE",
    "REC_PROJECT",
    "REC_ADVANCE",
    "REC_PREREQUISITE",
    "REC_UPDATE",
    "REC_SPECIALIZE",

    # Version
    "SKILL_EXTRACTOR_VERSION",

    "SKILL_EXTRACTOR_CAPABILITIES",

]


# ============================================================
# END OF FILE
# ============================================================
