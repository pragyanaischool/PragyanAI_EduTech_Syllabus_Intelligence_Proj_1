# ============================================================
# curriculum/taxonomy.py
# CHUNK 1/10
#
# CURRICULUM TAXONOMY ENGINE
#
# Purpose:
#   Build a normalized hierarchy of:
#
#       Domain
#          ↓
#       Subject
#          ↓
#       Module
#          ↓
#       Topic
#          ↓
#       Concept
#          ↓
#       Skill
#          ↓
#       Tool / Technology
#
# Also supports:
#   - Taxonomy normalization
#   - Hierarchical classification
#   - Parent-child relationships
#   - Skill-to-concept mapping
#   - Topic clustering
#   - Difficulty levels
#   - Learning pathways
#   - Prerequisite relationships
#   - Industry taxonomy
#   - Job-oriented taxonomy
#   - Taxonomy comparison
#   - Gap analysis
#   - JSON export
#
# ============================================================

from __future__ import annotations

import json
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
# OPTIONAL NUMPY
# ============================================================

try:

    import numpy as np

except ImportError:

    np = None


# ============================================================
# VERSION
# ============================================================

TAXONOMY_VERSION = "1.0.0"


# ============================================================
# NODE TYPES
# ============================================================

NODE_DOMAIN = "domain"

NODE_SUBJECT = "subject"

NODE_MODULE = "module"

NODE_TOPIC = "topic"

NODE_CONCEPT = "concept"

NODE_SKILL = "skill"

NODE_TOOL = "tool"

NODE_TECHNOLOGY = "technology"

NODE_FRAMEWORK = "framework"

NODE_PROJECT = "project"

NODE_ROLE = "role"

NODE_OUTCOME = "outcome"


# ============================================================
# DIFFICULTY
# ============================================================

DIFFICULTY_FOUNDATION = "foundation"

DIFFICULTY_BEGINNER = "beginner"

DIFFICULTY_INTERMEDIATE = "intermediate"

DIFFICULTY_ADVANCED = "advanced"

DIFFICULTY_EXPERT = "expert"


DIFFICULTY_ORDER = {

    DIFFICULTY_FOUNDATION: 0,

    DIFFICULTY_BEGINNER: 1,

    DIFFICULTY_INTERMEDIATE: 2,

    DIFFICULTY_ADVANCED: 3,

    DIFFICULTY_EXPERT: 4,

}


# ============================================================
# RELATION TYPES
# ============================================================

REL_PARENT = "parent"

REL_CHILD = "child"

REL_PREREQUISITE = "prerequisite"

REL_RELATED = "related"

REL_SUPPORTS = "supports"

REL_IMPLIES = "implies"

REL_DEVELOPS = "develops"

REL_USES = "uses"

REL_ALTERNATIVE = "alternative"

REL_SPECIALIZATION = "specialization"


# ============================================================
# STATUS
# ============================================================

STATUS_ACTIVE = "active"

STATUS_DEPRECATED = "deprecated"

STATUS_EMERGING = "emerging"

STATUS_OPTIONAL = "optional"

STATUS_REQUIRED = "required"


# ============================================================
# UTILITY FUNCTIONS
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


def normalize_name(
    value: Any,
) -> str:

    text = clean_text(
        value
    ).lower()

    text = text.replace(
        "&",
        " and ",
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


def slugify(
    value: Any,
) -> str:

    text = normalize_name(
        value
    )

    text = text.replace(
        "/",
        "-",
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
        r"[^a-z0-9-]+",
        "-",
        text,
    )

    text = re.sub(
        r"-+",
        "-",
        text,
    )

    return text.strip(
        "-"
    )


def deduplicate(
    values: Iterable[Any],
) -> List[Any]:

    result = []

    seen = set()

    for value in values:

        key = normalize_name(
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
# TAXONOMY NODE
# ============================================================

@dataclass
class TaxonomyNode:

    node_id: str

    name: str

    node_type: str

    parent_id: Optional[str] = None

    description: str = ""

    aliases: List[str] = field(
        default_factory=list
    )

    keywords: List[str] = field(
        default_factory=list
    )

    children: List[str] = field(
        default_factory=list
    )

    prerequisites: List[str] = field(
        default_factory=list
    )

    related_nodes: List[str] = field(
        default_factory=list
    )

    difficulty: str = DIFFICULTY_FOUNDATION

    status: str = STATUS_ACTIVE

    industry_relevance: float = 0.0

    employability_score: float = 0.0

    emerging_score: float = 0.0

    order: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# TAXONOMY RELATION
# ============================================================

@dataclass
class TaxonomyRelation:

    source_id: str

    target_id: str

    relation_type: str

    weight: float = 1.0

    confidence: float = 100.0

    description: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# TAXONOMY PATH
# ============================================================

@dataclass
class TaxonomyPath:

    node_ids: List[str] = field(
        default_factory=list
    )

    node_names: List[str] = field(
        default_factory=list
    )

    node_types: List[str] = field(
        default_factory=list
    )

    total_depth: int = 0

    description: str = ""


# ============================================================
# TAXONOMY GAP
# ============================================================

@dataclass
class TaxonomyGap:

    node_id: str

    node_name: str

    node_type: str

    missing_parent: Optional[str] = None

    missing_prerequisites: List[str] = field(
        default_factory=list
    )

    severity: str = "medium"

    priority_score: float = 0.0

    industry_relevance: float = 0.0

    employability_score: float = 0.0

    rationale: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# TAXONOMY RESULT
# ============================================================

@dataclass
class TaxonomyResult:

    nodes: List[TaxonomyNode] = field(
        default_factory=list
    )

    relations: List[TaxonomyRelation] = field(
        default_factory=list
    )

    paths: List[TaxonomyPath] = field(
        default_factory=list
    )

    gaps: List[TaxonomyGap] = field(
        default_factory=list
    )

    summary: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class TaxonomyConfig:

    max_nodes: int = 5000

    max_depth: int = 10

    include_tools: bool = True

    include_projects: bool = True

    include_roles: bool = True

    include_prerequisites: bool = True

    include_industry_scores: bool = True

    include_emerging_scores: bool = True

    minimum_relevance: float = 0.0

    normalize_aliases: bool = True


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# CANONICAL TAXONOMY KNOWLEDGE BASE
# ============================================================


# ============================================================
# ROOT DOMAINS
# ============================================================

DOMAIN_TAXONOMY = {

    "artificial intelligence": {

        "description":
            "Artificial Intelligence and intelligent systems.",

        "subjects": [

            "machine learning",

            "deep learning",

            "generative ai",

            "agentic ai",

            "natural language processing",

            "computer vision",

            "reinforcement learning",

        ],

    },

    "data science": {

        "description":
            "Data analysis, statistics, machine learning and decision intelligence.",

        "subjects": [

            "statistics",

            "data analysis",

            "machine learning",

            "data visualization",

            "predictive analytics",

        ],

    },

    "data engineering": {

        "description":
            "Data pipelines, processing, storage and distributed systems.",

        "subjects": [

            "etl",

            "data pipelines",

            "data warehousing",

            "big data",

            "stream processing",

        ],

    },

    "software engineering": {

        "description":
            "Software development, architecture, APIs and engineering practices.",

        "subjects": [

            "programming",

            "software development",

            "api development",

            "software architecture",

            "testing",

        ],

    },

    "cloud computing": {

        "description":
            "Cloud platforms, infrastructure and cloud-native applications.",

        "subjects": [

            "aws",

            "azure",

            "gcp",

            "cloud architecture",

            "serverless",

        ],

    },

    "devops": {

        "description":
            "Infrastructure automation, deployment, CI/CD and reliability.",

        "subjects": [

            "git",

            "ci/cd",

            "docker",

            "kubernetes",

            "terraform",

            "monitoring",

        ],

    },

    "cybersecurity": {

        "description":
            "Security engineering, threat detection and secure systems.",

        "subjects": [

            "network security",

            "application security",

            "cloud security",

            "ai security",

            "security operations",

        ],

    },

    "business intelligence": {

        "description":
            "Business reporting, dashboards, analytics and decision support.",

        "subjects": [

            "data visualization",

            "business analytics",

            "reporting",

            "dashboard development",

        ],

    },

}


# ============================================================
# SUBJECT HIERARCHY
# ============================================================

SUBJECT_TAXONOMY = {

    "machine learning": {

        "domain":
            "artificial intelligence",

        "topics": [

            "supervised learning",

            "unsupervised learning",

            "classification",

            "regression",

            "clustering",

            "ensemble learning",

            "feature engineering",

            "model evaluation",

            "hyperparameter tuning",

            "recommender systems",

            "time series forecasting",

            "anomaly detection",

        ],

    },

    "deep learning": {

        "domain":
            "artificial intelligence",

        "topics": [

            "neural networks",

            "cnn",

            "rnn",

            "lstm",

            "transformers",

            "attention mechanisms",

            "transfer learning",

            "fine tuning",

        ],

    },

    "generative ai": {

        "domain":
            "artificial intelligence",

        "topics": [

            "large language models",

            "prompt engineering",

            "embeddings",

            "retrieval augmented generation",

            "vector databases",

            "llm evaluation",

            "multimodal ai",

            "synthetic data",

        ],

    },

    "agentic ai": {

        "domain":
            "artificial intelligence",

        "topics": [

            "ai agents",

            "tool calling",

            "function calling",

            "agent memory",

            "agent orchestration",

            "multi agent systems",

            "planning",

            "reflection",

        ],

    },

    "natural language processing": {

        "domain":
            "artificial intelligence",

        "topics": [

            "tokenization",

            "text classification",

            "sentiment analysis",

            "named entity recognition",

            "text summarization",

            "machine translation",

        ],

    },

    "computer vision": {

        "domain":
            "artificial intelligence",

        "topics": [

            "image classification",

            "object detection",

            "image segmentation",

            "image processing",

            "ocr",

            "face recognition",

            "pose estimation",

        ],

    },

    "data analysis": {

        "domain":
            "data science",

        "topics": [

            "data cleaning",

            "exploratory data analysis",

            "statistical analysis",

            "feature engineering",

            "data visualization",

        ],

    },

    "statistics": {

        "domain":
            "data science",

        "topics": [

            "descriptive statistics",

            "probability",

            "hypothesis testing",

            "correlation",

            "regression analysis",

            "bayesian statistics",

        ],

    },

    "data pipelines": {

        "domain":
            "data engineering",

        "topics": [

            "etl",

            "batch processing",

            "stream processing",

            "data quality",

            "data orchestration",

        ],

    },

    "cloud architecture": {

        "domain":
            "cloud computing",

        "topics": [

            "cloud infrastructure",

            "networking",

            "storage",

            "compute",

            "serverless",

            "security",

        ],

    },

    "kubernetes": {

        "domain":
            "devops",

        "topics": [

            "pods",

            "deployments",

            "services",

            "configmaps",

            "secrets",

            "helm",

            "autoscaling",

        ],

    },

}


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# TOPIC → CONCEPT → SKILL → TOOL TAXONOMY
# ============================================================


# ============================================================
# TOPIC CONCEPT MAP
# ============================================================

TOPIC_CONCEPTS = {

    "supervised learning": [

        "training data",

        "labels",

        "classification",

        "regression",

        "generalization",

        "overfitting",

        "underfitting",

    ],

    "classification": [

        "binary classification",

        "multiclass classification",

        "decision boundary",

        "precision",

        "recall",

        "f1 score",

        "roc auc",

    ],

    "regression": [

        "linear regression",

        "polynomial regression",

        "regularization",

        "mean squared error",

        "mean absolute error",

        "r squared",

    ],

    "clustering": [

        "k means",

        "hierarchical clustering",

        "dbscan",

        "cluster distance",

        "silhouette score",

    ],

    "neural networks": [

        "neurons",

        "weights",

        "bias",

        "activation functions",

        "forward propagation",

        "backpropagation",

        "gradient descent",

    ],

    "cnn": [

        "convolution",

        "filters",

        "feature maps",

        "pooling",

        "padding",

        "stride",

    ],

    "transformers": [

        "self attention",

        "multi head attention",

        "positional encoding",

        "encoder",

        "decoder",

        "transformer block",

    ],

    "large language models": [

        "tokenization",

        "embeddings",

        "attention",

        "pretraining",

        "instruction tuning",

        "context window",

        "inference",

    ],

    "prompt engineering": [

        "zero shot prompting",

        "few shot prompting",

        "chain of thought",

        "role prompting",

        "structured prompting",

        "prompt evaluation",

    ],

    "retrieval augmented generation": [

        "document ingestion",

        "chunking",

        "embedding generation",

        "vector search",

        "retrieval",

        "reranking",

        "context injection",

        "answer generation",

    ],

    "ai agents": [

        "agent state",

        "tool selection",

        "tool execution",

        "planning",

        "memory",

        "reflection",

        "reasoning",

    ],

    "data pipelines": [

        "data ingestion",

        "transformation",

        "validation",

        "orchestration",

        "monitoring",

    ],

    "kubernetes": [

        "container",

        "pod",

        "deployment",

        "service",

        "ingress",

        "configmap",

        "secret",

    ],

}


# ============================================================
# CONCEPT → SKILLS
# ============================================================

CONCEPT_SKILLS = {

    "classification": [

        "machine learning",

        "python",

        "scikit-learn",

        "model evaluation",

    ],

    "regression": [

        "machine learning",

        "statistics",

        "python",

        "scikit-learn",

    ],

    "cnn": [

        "deep learning",

        "computer vision",

        "pytorch",

        "tensorflow",

    ],

    "transformers": [

        "deep learning",

        "natural language processing",

        "large language models",

        "pytorch",

    ],

    "large language models": [

        "generative ai",

        "transformers",

        "prompt engineering",

        "hugging face",

    ],

    "retrieval augmented generation": [

        "generative ai",

        "large language models",

        "embeddings",

        "vector databases",

        "langchain",

    ],

    "ai agents": [

        "agentic ai",

        "large language models",

        "tool calling",

        "function calling",

        "langgraph",

    ],

    "data pipelines": [

        "data engineering",

        "etl",

        "python",

        "sql",

        "apache airflow",

    ],

    "kubernetes": [

        "devops",

        "docker",

        "kubernetes",

        "cloud",

    ],

}


# ============================================================
# SKILL → TOOLS
# ============================================================

SKILL_TOOLS = {

    "machine learning": [

        "python",

        "scikit-learn",

        "jupyter",

    ],

    "deep learning": [

        "pytorch",

        "tensorflow",

        "keras",

    ],

    "generative ai": [

        "hugging face",

        "transformers",

        "langchain",

        "llamaindex",

    ],

    "large language models": [

        "hugging face",

        "transformers",

        "ollama",

    ],

    "retrieval augmented generation": [

        "langchain",

        "llamaindex",

        "faiss",

        "chroma",

        "pinecone",

    ],

    "ai agents": [

        "langchain",

        "langgraph",

        "crewai",

    ],

    "data engineering": [

        "apache spark",

        "apache kafka",

        "apache airflow",

    ],

    "mlops": [

        "mlflow",

        "kubeflow",

        "docker",

        "kubernetes",

    ],

    "cloud": [

        "aws",

        "azure",

        "gcp",

    ],

    "computer vision": [

        "opencv",

        "yolo",

        "pytorch",

        "tensorflow",

    ],

}


# ============================================================
# TOOL → SKILL
# ============================================================

TOOL_SKILLS = {

    "python": [

        "programming",

        "data analysis",

        "machine learning",

        "automation",

    ],

    "pandas": [

        "data analysis",

        "data science",

    ],

    "numpy": [

        "numerical computing",

        "data science",

        "machine learning",

    ],

    "scikit-learn": [

        "machine learning",

        "data science",

    ],

    "pytorch": [

        "deep learning",

        "computer vision",

        "natural language processing",

    ],

    "tensorflow": [

        "deep learning",

        "computer vision",

    ],

    "langchain": [

        "generative ai",

        "retrieval augmented generation",

        "ai agents",

    ],

    "langgraph": [

        "agentic ai",

        "ai agents",

    ],

    "docker": [

        "containerization",

        "devops",

        "mlops",

    ],

    "kubernetes": [

        "container orchestration",

        "devops",

        "mlops",

    ],

}


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# NORMALIZATION + ALIAS ENGINE
# ============================================================


# ============================================================
# GLOBAL ALIASES
# ============================================================

TAXONOMY_ALIASES = {

    "ai":
        "artificial intelligence",

    "artificial intelligence":
        "artificial intelligence",

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
        "large language models",

    "llms":
        "large language models",

    "rag":
        "retrieval augmented generation",

    "retrieval-augmented generation":
        "retrieval augmented generation",

    "nlp":
        "natural language processing",

    "cv":
        "computer vision",

    "k8s":
        "kubernetes",

    "pbi":
        "power bi",

    "powerbi":
        "power bi",

    "sklearn":
        "scikit-learn",

    "scikit learn":
        "scikit-learn",

    "hf":
        "hugging face",

    "huggingface":
        "hugging face",

    "llama index":
        "llamaindex",

    "postgres":
        "postgresql",

    "mongo":
        "mongodb",

    "aws":
        "aws",

    "azure":
        "azure",

    "gcp":
        "gcp",

}


# ============================================================
# CANONICAL NAME
# ============================================================

def canonical_name(
    value: Any,
) -> str:

    normalized = normalize_name(
        value
    )

    return TAXONOMY_ALIASES.get(

        normalized,

        normalized,

    )


# ============================================================
# NODE ID
# ============================================================

def make_node_id(
    node_type: str,
    name: str,
) -> str:

    return (

        f"{node_type}:"
        f"{slugify(name)}"

    )


# ============================================================
# GET ALIASES
# ============================================================

def get_aliases(
    name: str,
) -> List[str]:

    canonical = canonical_name(
        name
    )

    aliases = []

    for alias, target in (
        TAXONOMY_ALIASES.items()
    ):

        if target == canonical:

            aliases.append(
                alias
            )

    return deduplicate(
        aliases
    )


# ============================================================
# GET KEYWORDS
# ============================================================

def get_keywords(
    name: str,
) -> List[str]:

    canonical = canonical_name(
        name
    )

    tokens = re.split(

        r"[\s,;/|:+#.-]+",

        canonical,

    )

    aliases = get_aliases(
        canonical
    )

    return deduplicate(

        aliases
        +
        [

            token

            for token
            in tokens

            if token

        ]

    )


# ============================================================
# FIND CANONICAL NODE TYPE
# ============================================================

def infer_node_type(
    name: str,
) -> str:

    canonical = canonical_name(
        name
    )

    # Domains.
    if canonical in DOMAIN_TAXONOMY:

        return NODE_DOMAIN

    # Subjects.
    if canonical in SUBJECT_TAXONOMY:

        return NODE_SUBJECT

    # Topics.
    for subject in SUBJECT_TAXONOMY.values():

        if canonical in [

            canonical_name(
                topic
            )

            for topic
            in subject.get(
                "topics",
                [],
            )

        ]:

            return NODE_TOPIC

    # Concepts.
    if canonical in {

        canonical_name(
            concept
        )

        for concepts
        in TOPIC_CONCEPTS.values()

        for concept
        in concepts

    }:

        return NODE_CONCEPT

    # Skills.
    if canonical in {

        canonical_name(
            skill
        )

        for skills
        in CONCEPT_SKILLS.values()

        for skill
        in skills

    }:

        return NODE_SKILL

    # Tools.
    if canonical in {

        canonical_name(
            tool
        )

        for tools
        in SKILL_TOOLS.values()

        for tool
        in tools

    }:

        return NODE_TOOL

    return NODE_TOPIC


# ============================================================
# NORMALIZE NODE
# ============================================================

def normalize_node(
    node: Union[
        TaxonomyNode,
        Dict[str, Any],
        str,
    ],
    default_type: str = NODE_TOPIC,
) -> TaxonomyNode:

    if isinstance(
        node,
        TaxonomyNode,
    ):

        return node

    if isinstance(
        node,
        str,
    ):

        name = canonical_name(
            node
        )

        node_type = infer_node_type(
            name
        )

        return TaxonomyNode(

            node_id=make_node_id(
                node_type,
                name,
            ),

            name=name,

            node_type=node_type,

            aliases=get_aliases(
                name
            ),

            keywords=get_keywords(
                name
            ),

        )

    data = dict(
        node
    )

    name = canonical_name(

        data.get(
            "name",
            data.get(
                "title",
                "",
            ),
        )

    )

    node_type = data.get(
        "node_type",
        data.get(
            "type",
            default_type,
        ),
    )

    node_type = (
        node_type
        or
        infer_node_type(
            name
        )
    )

    return TaxonomyNode(

        node_id=data.get(

            "node_id",

            make_node_id(
                node_type,
                name,
            ),

        ),

        name=name,

        node_type=node_type,

        parent_id=data.get(
            "parent_id"
        ),

        description=clean_text(
            data.get(
                "description",
                "",
            )
        ),

        aliases=deduplicate(

            data.get(
                "aliases",
                [],
            )

        ),

        keywords=deduplicate(

            data.get(
                "keywords",
                [],
            )

        ),

        children=deduplicate(

            data.get(
                "children",
                [],
            )

        ),

        prerequisites=deduplicate(

            data.get(
                "prerequisites",
                [],
            )

        ),

        related_nodes=deduplicate(

            data.get(
                "related_nodes",
                [],
            )

        ),

        difficulty=data.get(

            "difficulty",

            DIFFICULTY_FOUNDATION,

        ),

        status=data.get(

            "status",

            STATUS_ACTIVE,

        ),

        industry_relevance=float(

            data.get(
                "industry_relevance",
                0.0,
            )
            or
            0.0

        ),

        employability_score=float(

            data.get(
                "employability_score",
                0.0,
            )
            or
            0.0

        ),

        emerging_score=float(

            data.get(
                "emerging_score",
                0.0,
            )
            or
            0.0

        ),

        order=int(

            data.get(
                "order",
                0,
            )
            or
            0

        ),

        metadata=dict(

            data.get(
                "metadata",
                {},
            )

        ),

    )


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# TAXONOMY BUILDER
# ============================================================


class TaxonomyBuilder:

    """
    Builds the normalized curriculum taxonomy graph.
    """

    def __init__(
        self,
        config: Optional[
            TaxonomyConfig
        ] = None,
    ):

        self.config = (

            config

            or

            TaxonomyConfig()

        )

        self.nodes: Dict[
            str,
            TaxonomyNode,
        ] = {}

        self.relations: List[
            TaxonomyRelation
        ] = []


    # ========================================================
    # ADD NODE
    # ========================================================

    def add_node(
        self,
        node: TaxonomyNode,
    ) -> TaxonomyNode:

        if len(
            self.nodes
        ) >= self.config.max_nodes:

            existing = self.nodes.get(
                node.node_id
            )

            if existing:

                return existing

            raise ValueError(
                "Maximum taxonomy node limit reached."
            )

        existing = self.nodes.get(
            node.node_id
        )

        if existing:

            existing.aliases = deduplicate(

                existing.aliases
                +
                node.aliases

            )

            existing.keywords = deduplicate(

                existing.keywords
                +
                node.keywords

            )

            existing.children = deduplicate(

                existing.children
                +
                node.children

            )

            existing.prerequisites = deduplicate(

                existing.prerequisites
                +
                node.prerequisites

            )

            existing.related_nodes = deduplicate(

                existing.related_nodes
                +
                node.related_nodes

            )

            existing.description = (

                existing.description

                or

                node.description

            )

            existing.industry_relevance = max(

                existing.industry_relevance,

                node.industry_relevance,

            )

            existing.employability_score = max(

                existing.employability_score,

                node.employability_score,

            )

            existing.emerging_score = max(

                existing.emerging_score,

                node.emerging_score,

            )

            return existing

        self.nodes[
            node.node_id
        ] = node

        return node


    # ========================================================
    # ADD RELATION
    # ========================================================

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        confidence: float = 100.0,
        description: str = "",
    ) -> TaxonomyRelation:

        relation = TaxonomyRelation(

            source_id=source_id,

            target_id=target_id,

            relation_type=relation_type,

            weight=weight,

            confidence=confidence,

            description=description,

        )

        self.relations.append(
            relation
        )

        return relation


    # ========================================================
    # ADD HIERARCHY
    # ========================================================

    def connect_parent_child(
        self,
        parent: TaxonomyNode,
        child: TaxonomyNode,
    ) -> None:

        child.parent_id = parent.node_id

        parent.children = deduplicate(

            parent.children
            +
            [child.node_id]

        )

        self.add_relation(

            parent.node_id,

            child.node_id,

            REL_PARENT,

        )


    # ========================================================
    # BUILD DOMAIN
    # ========================================================

    def add_domain(
        self,
        name: str,
        description: str = "",
    ) -> TaxonomyNode:

        canonical = canonical_name(
            name
        )

        node = TaxonomyNode(

            node_id=make_node_id(
                NODE_DOMAIN,
                canonical,
            ),

            name=canonical,

            node_type=NODE_DOMAIN,

            description=description,

            aliases=get_aliases(
                canonical
            ),

            keywords=get_keywords(
                canonical
            ),

            difficulty=DIFFICULTY_FOUNDATION,

        )

        return self.add_node(
            node
        )


    # ========================================================
    # BUILD SUBJECT
    # ========================================================

    def add_subject(
        self,
        name: str,
        domain: Optional[
            Union[
                str,
                TaxonomyNode,
            ]
        ] = None,
    ) -> TaxonomyNode:

        canonical = canonical_name(
            name
        )

        node = TaxonomyNode(

            node_id=make_node_id(
                NODE_SUBJECT,
                canonical,
            ),

            name=canonical,

            node_type=NODE_SUBJECT,

            aliases=get_aliases(
                canonical
            ),

            keywords=get_keywords(
                canonical
            ),

            difficulty=DIFFICULTY_BEGINNER,

        )

        node = self.add_node(
            node
        )

        if domain:

            parent = (

                domain

                if isinstance(
                    domain,
                    TaxonomyNode,
                )

                else

                self.add_domain(
                    domain
                )

            )

            self.connect_parent_child(

                parent,

                node,

            )

        return node


    # ========================================================
    # BUILD TOPIC
    # ========================================================

    def add_topic(
        self,
        name: str,
        parent: Optional[
            Union[
                str,
                TaxonomyNode,
            ]
        ] = None,
        difficulty: str = DIFFICULTY_INTERMEDIATE,
    ) -> TaxonomyNode:

        canonical = canonical_name(
            name
        )

        node = TaxonomyNode(

            node_id=make_node_id(
                NODE_TOPIC,
                canonical,
            ),

            name=canonical,

            node_type=NODE_TOPIC,

            aliases=get_aliases(
                canonical
            ),

            keywords=get_keywords(
                canonical
            ),

            difficulty=difficulty,

        )

        node = self.add_node(
            node
        )

        if parent:

            if isinstance(
                parent,
                TaxonomyNode,
            ):

                parent_node = parent

            else:

                parent_type = infer_node_type(
                    parent
                )

                parent_node = self.add_node(

                    TaxonomyNode(

                        node_id=make_node_id(

                            parent_type,

                            canonical_name(
                                parent
                            ),

                        ),

                        name=canonical_name(
                            parent
                        ),

                        node_type=parent_type,

                    )

                )

            self.connect_parent_child(

                parent_node,

                node,

            )

        return node


    # ========================================================
    # BUILD CONCEPT
    # ========================================================

    def add_concept(
        self,
        name: str,
        parent: Optional[
            Union[
                str,
                TaxonomyNode,
            ]
        ] = None,
        difficulty: str = DIFFICULTY_INTERMEDIATE,
    ) -> TaxonomyNode:

        canonical = canonical_name(
            name
        )

        node = TaxonomyNode(

            node_id=make_node_id(
                NODE_CONCEPT,
                canonical,
            ),

            name=canonical,

            node_type=NODE_CONCEPT,

            aliases=get_aliases(
                canonical
            ),

            keywords=get_keywords(
                canonical
            ),

            difficulty=difficulty,

        )

        node = self.add_node(
            node
        )

        if parent:

            parent_node = (

                parent

                if isinstance(
                    parent,
                    TaxonomyNode,
                )

                else

                self.add_topic(
                    parent
                )

            )

            self.connect_parent_child(

                parent_node,

                node,

            )

        return node


    # ========================================================
    # BUILD SKILL
    # ========================================================

    def add_skill(
        self,
        name: str,
        parent: Optional[
            Union[
                str,
                TaxonomyNode,
            ]
        ] = None,
    ) -> TaxonomyNode:

        canonical = canonical_name(
            name
        )

        node = TaxonomyNode(

            node_id=make_node_id(
                NODE_SKILL,
                canonical,
            ),

            name=canonical,

            node_type=NODE_SKILL,

            aliases=get_aliases(
                canonical
            ),

            keywords=get_keywords(
                canonical
            ),

            difficulty=DIFFICULTY_INTERMEDIATE,

        )

        node = self.add_node(
            node
        )

        if parent:

            parent_node = (

                parent

                if isinstance(
                    parent,
                    TaxonomyNode,
                )

                else

                self.add_concept(
                    parent
                )

            )

            self.connect_parent_child(

                parent_node,

                node,

            )

        return node


    # ========================================================
    # BUILD TOOL
    # ========================================================

    def add_tool(
        self,
        name: str,
        parent: Optional[
            Union[
                str,
                TaxonomyNode,
            ]
        ] = None,
    ) -> TaxonomyNode:

        canonical = canonical_name(
            name
        )

        node = TaxonomyNode(

            node_id=make_node_id(
                NODE_TOOL,
                canonical,
            ),

            name=canonical,

            node_type=NODE_TOOL,

            aliases=get_aliases(
                canonical
            ),

            keywords=get_keywords(
                canonical
            ),

            difficulty=DIFFICULTY_INTERMEDIATE,

        )

        node = self.add_node(
            node
        )

        if parent:

            parent_node = (

                parent

                if isinstance(
                    parent,
                    TaxonomyNode,
                )

                else

                self.add_skill(
                    parent
                )

            )

            self.connect_parent_child(

                parent_node,

                node,

            )

        return node


    # ========================================================
    # BUILD COMPLETE CANONICAL TAXONOMY
    # ========================================================

    def build_default(
        self,
    ) -> "TaxonomyBuilder":

        # ----------------------------------------------------
        # Domains
        # ----------------------------------------------------

        domains = {}

        for domain_name, domain_data in (
            DOMAIN_TAXONOMY.items()
        ):

            domains[
                domain_name
            ] = self.add_domain(

                domain_name,

                domain_data.get(
                    "description",
                    "",
                ),

            )

        # ----------------------------------------------------
        # Subjects
        # ----------------------------------------------------

        subjects = {}

        for subject_name, subject_data in (
            SUBJECT_TAXONOMY.items()
        ):

            domain_name = subject_data.get(
                "domain"
            )

            subjects[
                subject_name
            ] = self.add_subject(

                subject_name,

                domains.get(
                    domain_name
                ),

            )

        # ----------------------------------------------------
        # Topics
        # ----------------------------------------------------

        for subject_name, subject_data in (
            SUBJECT_TAXONOMY.items()
        ):

            subject_node = subjects[
                subject_name
            ]

            for index, topic_name in enumerate(

                subject_data.get(
                    "topics",
                    [],
                )

            ):

                topic = self.add_topic(

                    topic_name,

                    subject_node,

                )

                topic.order = index

        # ----------------------------------------------------
        # Concepts
        # ----------------------------------------------------

        for topic_name, concepts in (
            TOPIC_CONCEPTS.items()
        ):

            topic_node = self.get_node_by_name(
                topic_name
            )

            if not topic_node:

                topic_node = self.add_topic(
                    topic_name
                )

            for index, concept_name in enumerate(
                concepts
            ):

                concept = self.add_concept(

                    concept_name,

                    topic_node,

                )

                concept.order = index

        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        for concept_name, skills in (
            CONCEPT_SKILLS.items()
        ):

            concept_node = self.get_node_by_name(
                concept_name
            )

            if not concept_node:

                concept_node = self.add_concept(
                    concept_name
                )

            for index, skill_name in enumerate(
                skills
            ):

                skill = self.add_skill(

                    skill_name,

                    concept_node,

                )

                skill.order = index

        # ----------------------------------------------------
        # Tools
        # ----------------------------------------------------

        if self.config.include_tools:

            for skill_name, tools in (
                SKILL_TOOLS.items()
            ):

                skill_node = self.get_node_by_name(
                    skill_name
                )

                if not skill_node:

                    skill_node = self.add_skill(
                        skill_name
                    )

                for index, tool_name in enumerate(
                    tools
                ):

                    tool = self.add_tool(

                        tool_name,

                        skill_node,

                    )

                    tool.order = index

        self._build_prerequisite_relations()

        self._build_related_relations()

        self._calculate_scores()

        return self


    # ========================================================
    # GET NODE
    # ========================================================

    def get_node(
        self,
        node_id: str,
    ) -> Optional[TaxonomyNode]:

        return self.nodes.get(
            node_id
        )


    # ========================================================
    # GET NODE BY NAME
    # ========================================================

    def get_node_by_name(
        self,
        name: str,
    ) -> Optional[TaxonomyNode]:

        canonical = canonical_name(
            name
        )

        for node in self.nodes.values():

            if node.name == canonical:

                return node

        return None


    # ========================================================
    # END CHUNK 5
    # ========================================================
  # ============================================================
# CHUNK 6/10
#
# RELATIONSHIPS + PREREQUISITES + SCORING
# ============================================================


# ============================================================
# METHODS ATTACHED TO TaxonomyBuilder
# ============================================================


def _builder_build_prerequisite_relations(
    self: TaxonomyBuilder,
) -> None:

    for node in list(
        self.nodes.values()
    ):

        prerequisites = []

        if node.node_type == NODE_SUBJECT:

            if node.name == "deep learning":

                prerequisites = [
                    "machine learning",
                    "linear algebra",
                ]

            elif node.name == "generative ai":

                prerequisites = [
                    "deep learning",
                    "natural language processing",
                ]

            elif node.name == "agentic ai":

                prerequisites = [
                    "generative ai",
                    "large language models",
                ]

        elif node.node_type == NODE_TOPIC:

            mapping = {

                "classification": [
                    "supervised learning",
                ],

                "regression": [
                    "supervised learning",
                ],

                "transformers": [
                    "neural networks",
                    "attention mechanisms",
                ],

                "large language models": [
                    "transformers",
                ],

                "retrieval augmented generation": [
                    "large language models",
                    "embeddings",
                ],

                "ai agents": [
                    "large language models",
                    "tool calling",
                ],

                "multi agent systems": [
                    "ai agents",
                ],

            }

            prerequisites = mapping.get(

                node.name,

                [],

            )

        elif node.node_type == NODE_CONCEPT:

            mapping = {

                "backpropagation": [
                    "gradient descent",
                ],

                "attention": [
                    "neural networks",
                ],

                "self attention": [
                    "attention mechanisms",
                ],

                "embedding generation": [
                    "embeddings",
                ],

                "vector search": [
                    "vector databases",
                ],

            }

            prerequisites = mapping.get(

                node.name,

                [],

            )

        for prerequisite in prerequisites:

            prerequisite_node = (
                self.get_node_by_name(
                    prerequisite
                )
            )

            if not prerequisite_node:

                continue

            node.prerequisites = deduplicate(

                node.prerequisites
                +
                [
                    prerequisite_node.node_id
                ]

            )

            self.add_relation(

                node.node_id,

                prerequisite_node.node_id,

                REL_PREREQUISITE,

                weight=1.0,

                confidence=90.0,

            )


def _builder_build_related_relations(
    self: TaxonomyBuilder,
) -> None:

    for skill, related_skills in (
        SKILL_TOOLS.items()
    ):

        source = self.get_node_by_name(
            skill
        )

        if not source:

            continue

        for tool_name in related_skills:

            target = self.get_node_by_name(
                tool_name
            )

            if not target:

                continue

            source.related_nodes = deduplicate(

                source.related_nodes
                +
                [
                    target.node_id
                ]

            )

            self.add_relation(

                source.node_id,

                target.node_id,

                REL_USES,

                weight=1.0,

                confidence=95.0,

                description=(

                    f"{source.name} uses "
                    f"{target.name}."

                ),

            )

    for concept, skills in (
        CONCEPT_SKILLS.items()
    ):

        concept_node = self.get_node_by_name(
            concept
        )

        if not concept_node:

            continue

        for skill_name in skills:

            skill_node = self.get_node_by_name(
                skill_name
            )

            if not skill_node:

                continue

            self.add_relation(

                concept_node.node_id,

                skill_node.node_id,

                REL_DEVELOPS,

                weight=1.0,

                confidence=90.0,

                description=(

                    f"{concept_node.name} develops "
                    f"{skill_node.name}."

                ),

            )


def _builder_calculate_scores(
    self: TaxonomyBuilder,
) -> None:

    emerging_keywords = {

        "generative ai",

        "large language models",

        "retrieval augmented generation",

        "ai agents",

        "agentic ai",

        "multimodal ai",

        "llmops",

        "vector databases",

    }

    high_employability = {

        "python",

        "sql",

        "machine learning",

        "deep learning",

        "generative ai",

        "large language models",

        "retrieval augmented generation",

        "ai agents",

        "cloud",

        "aws",

        "azure",

        "gcp",

        "docker",

        "kubernetes",

        "mlops",

        "data engineering",

    }

    for node in self.nodes.values():

        if node.name in emerging_keywords:

            node.emerging_score = 95.0

            node.status = STATUS_EMERGING

        elif any(

            word in node.name

            for word in (

                "agent",

                "llm",

                "generative",

                "vector",

                "multimodal",

            )

        ):

            node.emerging_score = 75.0

        else:

            node.emerging_score = 35.0

        if node.name in high_employability:

            node.employability_score = 95.0

        elif node.node_type in {

            NODE_SKILL,

            NODE_TOOL,

            NODE_TECHNOLOGY,

            NODE_FRAMEWORK,

        }:

            node.employability_score = 70.0

        elif node.node_type == NODE_TOPIC:

            node.employability_score = 65.0

        else:

            node.employability_score = 55.0

        node.industry_relevance = (

            node.employability_score * 0.70

            +

            node.emerging_score * 0.30

        )


TaxonomyBuilder._build_prerequisite_relations = (
    _builder_build_prerequisite_relations
)

TaxonomyBuilder._build_related_relations = (
    _builder_build_related_relations
)

TaxonomyBuilder._calculate_scores = (
    _builder_calculate_scores
)


# ============================================================
# CHILDREN
# ============================================================

def _builder_get_children(
    self: TaxonomyBuilder,
    node_id: str,
) -> List[TaxonomyNode]:

    node = self.nodes.get(
        node_id
    )

    if not node:

        return []

    return [

        self.nodes[child_id]

        for child_id
        in node.children

        if child_id in self.nodes

    ]


TaxonomyBuilder.get_children = (
    _builder_get_children
)


# ============================================================
# PARENTS
# ============================================================

def _builder_get_parent(
    self: TaxonomyBuilder,
    node_id: str,
) -> Optional[TaxonomyNode]:

    node = self.nodes.get(
        node_id
    )

    if not node:

        return None

    if not node.parent_id:

        return None

    return self.nodes.get(
        node.parent_id
    )


TaxonomyBuilder.get_parent = (
    _builder_get_parent
)


# ============================================================
# PREREQUISITES
# ============================================================

def _builder_get_prerequisites(
    self: TaxonomyBuilder,
    node_id: str,
) -> List[TaxonomyNode]:

    node = self.nodes.get(
        node_id
    )

    if not node:

        return []

    return [

        self.nodes[pid]

        for pid
        in node.prerequisites

        if pid in self.nodes

    ]


TaxonomyBuilder.get_prerequisites = (
    _builder_get_prerequisites
)


# ============================================================
# DESCENDANTS
# ============================================================

def _builder_get_descendants(
    self: TaxonomyBuilder,
    node_id: str,
    max_depth: Optional[int] = None,
) -> List[TaxonomyNode]:

    max_depth = (

        max_depth

        if max_depth is not None

        else self.config.max_depth

    )

    result = []

    visited = set()

    def visit(
        current_id: str,
        depth: int,
    ):

        if depth > max_depth:

            return

        if current_id in visited:

            return

        visited.add(
            current_id
        )

        for child in self.get_children(
            current_id
        ):

            result.append(
                child
            )

            visit(

                child.node_id,

                depth + 1,

            )

    visit(
        node_id,
        0,
    )

    return result


TaxonomyBuilder.get_descendants = (
    _builder_get_descendants
)


# ============================================================
# ANCESTORS
# ============================================================

def _builder_get_ancestors(
    self: TaxonomyBuilder,
    node_id: str,
) -> List[TaxonomyNode]:

    result = []

    current = self.get_parent(
        node_id
    )

    visited = set()

    while current:

        if current.node_id in visited:

            break

        visited.add(
            current.node_id
        )

        result.append(
            current
        )

        current = self.get_parent(
            current.node_id
        )

    return result


TaxonomyBuilder.get_ancestors = (
    _builder_get_ancestors
)


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# PATH DISCOVERY + CLASSIFICATION
# ============================================================


# ============================================================
# FIND PATH TO ROOT
# ============================================================

def get_taxonomy_path(
    builder: TaxonomyBuilder,
    node_id: str,
) -> TaxonomyPath:

    node = builder.get_node(
        node_id
    )

    if not node:

        return TaxonomyPath()


    chain = [

        node

    ]

    visited = {
        node.node_id
    }

    current = node

    while current.parent_id:

        parent = builder.get_node(
            current.parent_id
        )

        if not parent:

            break

        if parent.node_id in visited:

            break

        chain.append(
            parent
        )

        visited.add(
            parent.node_id
        )

        current = parent

    chain.reverse()

    return TaxonomyPath(

        node_ids=[

            item.node_id

            for item
            in chain

        ],

        node_names=[

            item.name

            for item
            in chain

        ],

        node_types=[

            item.node_type

            for item
            in chain

        ],

        total_depth=len(
            chain
        ),

        description=(
            " > ".join(
                item.name
                for item
                in chain
            )
        ),

    )


# ============================================================
# FIND NODE BY TEXT
# ============================================================

def find_taxonomy_nodes(
    builder: TaxonomyBuilder,
    text: str,
    node_types: Optional[
        Sequence[str]
    ] = None,
) -> List[TaxonomyNode]:

    text = normalize_name(
        text
    )

    if not text:

        return []

    allowed_types = (

        set(
            node_types
        )

        if node_types

        else None

    )

    results = []

    for node in builder.nodes.values():

        if (
            allowed_types
            and
            node.node_type
            not in allowed_types
        ):

            continue

        names = [

            node.name

        ] + node.aliases + node.keywords

        if any(

            normalize_name(
                value
            ) in text

            for value
            in names

        ):

            results.append(
                node
            )

    return results


# ============================================================
# CLASSIFY TEXT
# ============================================================

def classify_text_into_taxonomy(
    builder: TaxonomyBuilder,
    text: str,
) -> List[TaxonomyNode]:

    text = normalize_name(
        text
    )

    if not text:

        return []

    candidates = []

    for node in builder.nodes.values():

        phrases = [

            node.name

        ] + node.aliases

        for phrase in phrases:

            phrase = normalize_name(
                phrase
            )

            if not phrase:

                continue

            pattern = (

                r"(?<![a-z0-9])"

                +
                re.escape(
                    phrase
                )

                +
                r"(?![a-z0-9])"

            )

            if re.search(
                pattern,
                text,
            ):

                candidates.append(
                    node
                )

                break

    # Prefer higher-level nodes when there
    # is a semantic match, but preserve details.
    candidates.sort(

        key=lambda item: (

            DIFFICULTY_ORDER.get(

                item.difficulty,

                0,

            ),

            item.industry_relevance,

            item.employability_score,

        ),

        reverse=True,

    )

    return candidates


# ============================================================
# CLASSIFY SKILLS
# ============================================================

def classify_skills(
    builder: TaxonomyBuilder,
    skills: Sequence[str],
) -> Dict[str, List[TaxonomyNode]]:

    result = {}

    for skill in skills:

        canonical = canonical_name(
            skill
        )

        nodes = find_taxonomy_nodes(

            builder,

            canonical,

            [

                NODE_SKILL,

                NODE_TOOL,

                NODE_TECHNOLOGY,

                NODE_FRAMEWORK,

            ],

        )

        result[
            canonical
        ] = nodes

    return result


# ============================================================
# TAXONOMY COVERAGE
# ============================================================

def calculate_taxonomy_coverage(
    builder: TaxonomyBuilder,
    names: Sequence[str],
) -> float:

    if not names:

        return 0.0

    matched = 0

    for name in names:

        if builder.get_node_by_name(
            name
        ):

            matched += 1

    return round(

        (
            matched
            /
            len(names)
        )
        * 100.0,

        2,

    )


# ============================================================
# TAXONOMY DEPTH
# ============================================================

def calculate_taxonomy_depth(
    builder: TaxonomyBuilder,
) -> int:

    maximum = 0

    for node in builder.nodes.values():

        path = get_taxonomy_path(

            builder,

            node.node_id,

        )

        maximum = max(

            maximum,

            path.total_depth,

        )

    return maximum


# ============================================================
# NODE COUNTS
# ============================================================

def taxonomy_node_counts(
    builder: TaxonomyBuilder,
) -> Dict[str, int]:

    counts = {}

    for node in builder.nodes.values():

        counts[
            node.node_type
        ] = (

            counts.get(
                node.node_type,
                0,
            )
            +
            1

        )

    return counts


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# GAP ANALYSIS + LEARNING PATHS
# ============================================================


# ============================================================
# GAP PRIORITY
# ============================================================

def calculate_taxonomy_gap_priority(
    node: TaxonomyNode,
    missing_prerequisites: int = 0,
) -> float:

    prerequisite_score = min(

        100.0,

        missing_prerequisites * 15.0,

    )

    score = (

        node.industry_relevance * 0.35

        +

        node.employability_score * 0.35

        +

        node.emerging_score * 0.15

        +

        prerequisite_score * 0.15

    )

    return round(

        min(
            100.0,
            max(
                0.0,
                score,
            ),
        ),

        2,

    )


# ============================================================
# GAP SEVERITY
# ============================================================

def gap_severity(
    priority: float,
) -> str:

    if priority >= 85:

        return "critical"

    if priority >= 70:

        return "high"

    if priority >= 45:

        return "medium"

    return "low"


# ============================================================
# IDENTIFY TAXONOMY GAPS
# ============================================================

def identify_taxonomy_gaps(
    builder: TaxonomyBuilder,
    available_names: Sequence[str],
    target_names: Sequence[str],
) -> List[TaxonomyGap]:

    available = {

        canonical_name(
            name
        )

        for name
        in available_names

    }

    gaps = []

    for target_name in target_names:

        canonical = canonical_name(
            target_name
        )

        node = builder.get_node_by_name(
            canonical
        )

        if not node:

            continue

        if canonical in available:

            continue

        missing_prerequisites = []

        for prerequisite_id in (
            node.prerequisites
        ):

            prerequisite = builder.get_node(
                prerequisite_id
            )

            if not prerequisite:

                continue

            if prerequisite.name not in available:

                missing_prerequisites.append(

                    prerequisite.name

                )

        priority = (
            calculate_taxonomy_gap_priority(

                node,

                len(
                    missing_prerequisites
                ),

            )
        )

        gaps.append(

            TaxonomyGap(

                node_id=node.node_id,

                node_name=node.name,

                node_type=node.node_type,

                missing_parent=(

                    builder.get_parent(
                        node.node_id
                    ).name

                    if builder.get_parent(
                        node.node_id
                    )

                    else None

                ),

                missing_prerequisites=(

                    missing_prerequisites

                ),

                severity=gap_severity(
                    priority
                ),

                priority_score=priority,

                industry_relevance=(

                    node.industry_relevance

                ),

                employability_score=(

                    node.employability_score

                ),

                rationale=(

                    f"{node.name} is not covered "
                    f"in the available taxonomy."

                ),

            )

        )

    return sorted(

        gaps,

        key=lambda item: item.priority_score,

        reverse=True,

    )


# ============================================================
# BUILD LEARNING PATH
# ============================================================

def build_learning_path(
    builder: TaxonomyBuilder,
    target_name: str,
) -> TaxonomyPath:

    target = builder.get_node_by_name(
        target_name
    )

    if not target:

        return TaxonomyPath()

    prerequisites = []

    visited = set()

    def visit(
        node: TaxonomyNode,
    ):

        if node.node_id in visited:

            return

        visited.add(
            node.node_id
        )

        for prerequisite_id in (
            node.prerequisites
        ):

            prerequisite = builder.get_node(
                prerequisite_id
            )

            if prerequisite:

                visit(
                    prerequisite
                )

        prerequisites.append(
            node
        )

    visit(
        target
    )

    # Add the hierarchical path of target.
    hierarchy = get_taxonomy_path(

        builder,

        target.node_id,

    )

    ordered = []

    seen = set()

    for node in prerequisites:

        if node.node_id not in seen:

            ordered.append(
                node
            )

            seen.add(
                node.node_id
            )

    for node_id in hierarchy.node_ids:

        node = builder.get_node(
            node_id
        )

        if not node:

            continue

        if node.node_id not in seen:

            ordered.append(
                node
            )

            seen.add(
                node.node_id
            )

    return TaxonomyPath(

        node_ids=[

            node.node_id

            for node
            in ordered

        ],

        node_names=[

            node.name

            for node
            in ordered

        ],

        node_types=[

            node.node_type

            for node
            in ordered

        ],

        total_depth=len(
            ordered
        ),

        description=(

            " → ".join(

                node.name

                for node
                in ordered

            )

        ),

    )


# ============================================================
# MULTIPLE LEARNING PATHS
# ============================================================

def build_learning_paths(
    builder: TaxonomyBuilder,
    targets: Sequence[str],
) -> List[TaxonomyPath]:

    paths = []

    for target in targets:

        path = build_learning_path(

            builder,

            target,

        )

        if path.node_ids:

            paths.append(
                path
            )

    return paths


# ============================================================
# RECOMMENDED NEXT NODE
# ============================================================

def recommend_next_nodes(
    builder: TaxonomyBuilder,
    completed_names: Sequence[str],
    limit: int = 10,
) -> List[TaxonomyNode]:

    completed = {

        canonical_name(
            name
        )

        for name
        in completed_names

    }

    candidates = []

    for node in builder.nodes.values():

        if node.name in completed:

            continue

        prerequisites_met = True

        for prerequisite_id in (
            node.prerequisites
        ):

            prerequisite = builder.get_node(
                prerequisite_id
            )

            if prerequisite:

                if prerequisite.name not in completed:

                    prerequisites_met = False

                    break

        if not prerequisites_met:

            continue

        candidates.append(
            node
        )

    candidates.sort(

        key=lambda node: (

            node.industry_relevance,

            node.employability_score,

            node.emerging_score,

        ),

        reverse=True,

    )

    return candidates[
        :max(
            1,
            limit,
        )
    ]


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# SERIALIZATION + COMPARISON + REPORTING
# ============================================================


# ============================================================
# NODE DICT
# ============================================================

def node_to_dict(
    node: TaxonomyNode,
) -> Dict[str, Any]:

    return asdict(
        node
    )


# ============================================================
# RELATION DICT
# ============================================================

def relation_to_dict(
    relation: TaxonomyRelation,
) -> Dict[str, Any]:

    return asdict(
        relation
    )


# ============================================================
# PATH DICT
# ============================================================

def path_to_dict(
    path: TaxonomyPath,
) -> Dict[str, Any]:

    return asdict(
        path
    )


# ============================================================
# GAP DICT
# ============================================================

def taxonomy_gap_to_dict(
    gap: TaxonomyGap,
) -> Dict[str, Any]:

    return asdict(
        gap
    )


# ============================================================
# RESULT DICT
# ============================================================

def taxonomy_result_to_dict(
    result: TaxonomyResult,
) -> Dict[str, Any]:

    return {

        "nodes": [

            node_to_dict(
                node
            )

            for node
            in result.nodes

        ],

        "relations": [

            relation_to_dict(
                relation
            )

            for relation
            in result.relations

        ],

        "paths": [

            path_to_dict(
                path
            )

            for path
            in result.paths

        ],

        "gaps": [

            taxonomy_gap_to_dict(
                gap
            )

            for gap
            in result.gaps

        ],

        "summary":
            result.summary,

        "metadata":
            result.metadata,

    }


# ============================================================
# JSON
# ============================================================

def taxonomy_result_to_json(
    result: TaxonomyResult,
    indent: int = 2,
) -> str:

    return json.dumps(

        taxonomy_result_to_dict(
            result
        ),

        indent=indent,

        ensure_ascii=False,

        default=str,

    )


# ============================================================
# SAVE JSON
# ============================================================

def save_taxonomy_json(
    result: TaxonomyResult,
    path: Union[
        str,
        Path,
    ],
) -> Path:

    path = Path(
        path
    )

    path.parent.mkdir(

        parents=True,

        exist_ok=True,

    )

    path.write_text(

        taxonomy_result_to_json(
            result
        ),

        encoding="utf-8",

    )

    return path


# ============================================================
# COMPARE TAXONOMIES
# ============================================================

def compare_taxonomies(
    source: TaxonomyBuilder,
    target: TaxonomyBuilder,
) -> Dict[str, Any]:

    source_names = {

        node.name

        for node
        in source.nodes.values()

    }

    target_names = {

        node.name

        for node
        in target.nodes.values()

    }

    common = sorted(

        source_names
        &
        target_names

    )

    missing = sorted(

        target_names
        -
        source_names

    )

    extra = sorted(

        source_names
        -
        target_names

    )

    coverage = (

        (
            len(common)
            /
            len(target_names)
        )
        *
        100.0

        if target_names

        else 0.0

    )

    return {

        "source_nodes":
            len(source_names),

        "target_nodes":
            len(target_names),

        "common_nodes":
            len(common),

        "missing_nodes":
            len(missing),

        "extra_nodes":
            len(extra),

        "coverage":
            round(
                coverage,
                2,
            ),

        "common":
            common,

        "missing":
            missing,

        "extra":
            extra,

    }


# ============================================================
# CATEGORY REPORT
# ============================================================

def build_taxonomy_summary(
    builder: TaxonomyBuilder,
) -> Dict[str, Any]:

    counts = taxonomy_node_counts(
        builder
    )

    emerging = [

        node

        for node
        in builder.nodes.values()

        if node.emerging_score >= 65.0

    ]

    high_employability = [

        node

        for node
        in builder.nodes.values()

        if node.employability_score >= 80.0

    ]

    average_industry = (

        sum(

            node.industry_relevance

            for node
            in builder.nodes.values()

        )
        /
        len(
            builder.nodes
        )

        if builder.nodes

        else 0.0

    )

    average_employability = (

        sum(

            node.employability_score

            for node
            in builder.nodes.values()

        )
        /
        len(
            builder.nodes
        )

        if builder.nodes

        else 0.0

    )

    return {

        "version":
            TAXONOMY_VERSION,

        "total_nodes":
            len(builder.nodes),

        "total_relations":
            len(builder.relations),

        "node_counts":
            counts,

        "taxonomy_depth":
            calculate_taxonomy_depth(
                builder
            ),

        "emerging_nodes":
            len(emerging),

        "high_employability_nodes":
            len(high_employability),

        "average_industry_relevance":
            round(
                average_industry,
                2,
            ),

        "average_employability":
            round(
                average_employability,
                2,
            ),

    }


# ============================================================
# EXPORT FLAT TABLE
# ============================================================

def taxonomy_to_rows(
    builder: TaxonomyBuilder,
) -> List[Dict[str, Any]]:

    rows = []

    for node in builder.nodes.values():

        path = get_taxonomy_path(

            builder,

            node.node_id,

        )

        rows.append({

            "node_id":
                node.node_id,

            "name":
                node.name,

            "node_type":
                node.node_type,

            "parent":
                (
                    builder.get_parent(
                        node.node_id
                    ).name

                    if builder.get_parent(
                        node.node_id
                    )

                    else ""

                ),

            "path":
                path.description,

            "difficulty":
                node.difficulty,

            "status":
                node.status,

            "industry_relevance":
                node.industry_relevance,

            "employability":
                node.employability_score,

            "emerging_score":
                node.emerging_score,

        })

    return rows


# ============================================================
# BUILD RESULT
# ============================================================

def build_taxonomy_result(
    builder: TaxonomyBuilder,
    target_names: Optional[
        Sequence[str]
    ] = None,
    available_names: Optional[
        Sequence[str]
    ] = None,
) -> TaxonomyResult:

    target_names = list(
        target_names
        or
        []
    )

    available_names = list(
        available_names
        or
        []
    )

    gaps = []

    if target_names:

        gaps = identify_taxonomy_gaps(

            builder,

            available_names,

            target_names,

        )

    paths = [

        build_learning_path(

            builder,

            target,

        )

        for target
        in target_names

        if builder.get_node_by_name(
            target
        )

    ]

    return TaxonomyResult(

        nodes=list(
            builder.nodes.values()
        ),

        relations=list(
            builder.relations
        ),

        paths=paths,

        gaps=gaps,

        summary=build_taxonomy_summary(
            builder
        ),

        metadata={

            "version":
                TAXONOMY_VERSION,

            "config":
                asdict(
                    builder.config
                ),

        },

    )


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# PUBLIC API
# ============================================================


# ============================================================
# BUILD DEFAULT TAXONOMY
# ============================================================

def build_default_taxonomy(
    config: Optional[
        TaxonomyConfig
    ] = None,
) -> TaxonomyBuilder:

    builder = TaxonomyBuilder(
        config
    )

    builder.build_default()

    return builder


# ============================================================
# BUILD FROM CURRICULUM
# ============================================================

def build_taxonomy_from_curriculum(
    curriculum: Any,
    config: Optional[
        TaxonomyConfig
    ] = None,
) -> TaxonomyBuilder:

    builder = build_default_taxonomy(
        config
    )

    if curriculum is None:

        return builder

    # --------------------------------------------------------
    # Dictionary curriculum
    # --------------------------------------------------------

    if isinstance(
        curriculum,
        dict,
    ):

        domains = curriculum.get(
            "domains",
            curriculum.get(
                "subjects",
                [],
            ),
        )

        modules = curriculum.get(
            "modules",
            [],
        )

        topics = curriculum.get(
            "topics",
            [],
        )

        concepts = curriculum.get(
            "concepts",
            [],
        )

        skills = curriculum.get(
            "skills",
            [],
        )

        for domain in (
            domains
            if isinstance(
                domains,
                (list, tuple),
            )
            else [domains]
        ):

            if isinstance(
                domain,
                dict,
            ):

                name = domain.get(
                    "name",
                    domain.get(
                        "title",
                        "",
                    ),
                )

            else:

                name = str(
                    domain
                )

            if name:

                builder.add_domain(
                    name
                )

        for module in (
            modules
            if isinstance(
                modules,
                (list, tuple),
            )
            else [modules]
        ):

            if isinstance(
                module,
                dict,
            ):

                name = module.get(
                    "name",
                    module.get(
                        "title",
                        "",
                    ),
                )

                parent = module.get(
                    "subject",
                    module.get(
                        "domain",
                        None,
                    ),
                )

            else:

                name = str(
                    module
                )

                parent = None

            if name:

                builder.add_topic(

                    name,

                    parent,

                )

        for topic in (
            topics
            if isinstance(
                topics,
                (list, tuple),
            )
            else [topics]
        ):

            if isinstance(
                topic,
                dict,
            ):

                name = topic.get(
                    "name",
                    topic.get(
                        "title",
                        "",
                    ),
                )

                parent = topic.get(
                    "module",
                    topic.get(
                        "subject",
                        None,
                    ),
                )

            else:

                name = str(
                    topic
                )

                parent = None

            if name:

                builder.add_topic(

                    name,

                    parent,

                )

        for concept in (
            concepts
            if isinstance(
                concepts,
                (list, tuple),
            )
            else [concepts]
        ):

            if isinstance(
                concept,
                dict,
            ):

                name = concept.get(
                    "name",
                    concept.get(
                        "title",
                        "",
                    ),
                )

                parent = concept.get(
                    "topic",
                    None,
                )

            else:

                name = str(
                    concept
                )

                parent = None

            if name:

                builder.add_concept(

                    name,

                    parent,

                )

        for skill in (
            skills
            if isinstance(
                skills,
                (list, tuple),
            )
            else [skills]
        ):

            if isinstance(
                skill,
                dict,
            ):

                name = skill.get(
                    "name",
                    skill.get(
                        "skill",
                        "",
                    ),
                )

                parent = skill.get(
                    "concept",
                    None,
                )

            else:

                name = str(
                    skill
                )

                parent = None

            if name:

                builder.add_skill(

                    name,

                    parent,

                )

    # --------------------------------------------------------
    # List curriculum
    # --------------------------------------------------------

    elif isinstance(
        curriculum,
        (list, tuple, set),
    ):

        for item in curriculum:

            if isinstance(
                item,
                dict,
            ):

                name = item.get(
                    "name",
                    item.get(
                        "title",
                        "",
                    ),
                )

                node_type = item.get(
                    "type",
                    item.get(
                        "node_type",
                        NODE_TOPIC,
                    ),
                )

            else:

                name = str(
                    item
                )

                node_type = NODE_TOPIC

            if not name:

                continue

            if node_type == NODE_DOMAIN:

                builder.add_domain(
                    name
                )

            elif node_type == NODE_SUBJECT:

                builder.add_subject(
                    name
                )

            elif node_type == NODE_CONCEPT:

                builder.add_concept(
                    name
                )

            elif node_type == NODE_SKILL:

                builder.add_skill(
                    name
                )

            elif node_type == NODE_TOOL:

                builder.add_tool(
                    name
                )

            else:

                builder.add_topic(
                    name
                )

    return builder


# ============================================================
# QUICK TAXONOMY ANALYSIS
# ============================================================

def analyze_taxonomy(
    curriculum: Any = None,
    target_names: Optional[
        Sequence[str]
    ] = None,
    available_names: Optional[
        Sequence[str]
    ] = None,
    config: Optional[
        TaxonomyConfig
    ] = None,
) -> TaxonomyResult:

    if curriculum is None:

        builder = build_default_taxonomy(
            config
        )

    else:

        builder = build_taxonomy_from_curriculum(

            curriculum,

            config,

        )

    return build_taxonomy_result(

        builder,

        target_names,

        available_names,

    )


# ============================================================
# QUICK LOOKUP
# ============================================================

def taxonomy_lookup(
    name: str,
) -> Dict[str, Any]:

    builder = build_default_taxonomy()

    node = builder.get_node_by_name(
        name
    )

    if not node:

        return {

            "found": False,

            "name":
                canonical_name(
                    name
                ),

        }

    path = get_taxonomy_path(

        builder,

        node.node_id,

    )

    prerequisites = [

        item.name

        for item
        in builder.get_prerequisites(
            node.node_id
        )

    ]

    children = [

        item.name

        for item
        in builder.get_children(
            node.node_id
        )

    ]

    return {

        "found": True,

        "node":
            node_to_dict(
                node
            ),

        "path":
            path_to_dict(
                path
            ),

        "prerequisites":
            prerequisites,

        "children":
            children,

    }


# ============================================================
# TAXONOMY TREE
# ============================================================

def taxonomy_tree(
    builder: TaxonomyBuilder,
    root_name: Optional[str] = None,
) -> Dict[str, Any]:

    if root_name:

        root = builder.get_node_by_name(
            root_name
        )

    else:

        root = None

    if root:

        roots = [
            root
        ]

    else:

        roots = [

            node

            for node
            in builder.nodes.values()

            if not node.parent_id

        ]

    def serialize(
        node: TaxonomyNode,
    ) -> Dict[str, Any]:

        return {

            "id":
                node.node_id,

            "name":
                node.name,

            "type":
                node.node_type,

            "difficulty":
                node.difficulty,

            "status":
                node.status,

            "industry_relevance":
                node.industry_relevance,

            "employability":
                node.employability_score,

            "emerging_score":
                node.emerging_score,

            "children": [

                serialize(
                    child
                )

                for child
                in builder.get_children(
                    node.node_id
                )

            ],

        }

    return {

        "roots": [

            serialize(
                root
            )

            for root
            in roots

        ],

    }


# ============================================================
# CAPABILITIES
# ============================================================

TAXONOMY_CAPABILITIES = [

    "domain_taxonomy",

    "subject_taxonomy",

    "module_taxonomy",

    "topic_taxonomy",

    "concept_taxonomy",

    "skill_taxonomy",

    "tool_taxonomy",

    "technology_taxonomy",

    "framework_taxonomy",

    "taxonomy_normalization",

    "taxonomy_aliases",

    "hierarchical_classification",

    "parent_child_relationships",

    "prerequisite_relationships",

    "related_skill_relationships",

    "skill_to_tool_mapping",

    "concept_to_skill_mapping",

    "topic_to_concept_mapping",

    "taxonomy_path_generation",

    "taxonomy_search",

    "taxonomy_coverage",

    "taxonomy_gap_analysis",

    "learning_path_generation",

    "next_skill_recommendation",

    "industry_relevance_scoring",

    "employability_scoring",

    "emerging_skill_scoring",

    "taxonomy_comparison",

    "taxonomy_dashboard_data",

    "json_export",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "TAXONOMY_VERSION",

    # Models
    "TaxonomyNode",
    "TaxonomyRelation",
    "TaxonomyPath",
    "TaxonomyGap",
    "TaxonomyResult",
    "TaxonomyConfig",

    # Builder
    "TaxonomyBuilder",

    # Constants
    "NODE_DOMAIN",
    "NODE_SUBJECT",
    "NODE_MODULE",
    "NODE_TOPIC",
    "NODE_CONCEPT",
    "NODE_SKILL",
    "NODE_TOOL",
    "NODE_TECHNOLOGY",
    "NODE_FRAMEWORK",
    "NODE_PROJECT",
    "NODE_ROLE",
    "NODE_OUTCOME",

    "DIFFICULTY_FOUNDATION",
    "DIFFICULTY_BEGINNER",
    "DIFFICULTY_INTERMEDIATE",
    "DIFFICULTY_ADVANCED",
    "DIFFICULTY_EXPERT",

    "REL_PARENT",
    "REL_CHILD",
    "REL_PREREQUISITE",
    "REL_RELATED",
    "REL_SUPPORTS",
    "REL_IMPLIES",
    "REL_DEVELOPS",
    "REL_USES",
    "REL_ALTERNATIVE",
    "REL_SPECIALIZATION",

    "STATUS_ACTIVE",
    "STATUS_DEPRECATED",
    "STATUS_EMERGING",
    "STATUS_OPTIONAL",
    "STATUS_REQUIRED",

    # Utilities
    "clean_text",
    "normalize_name",
    "canonical_name",
    "slugify",
    "deduplicate",
    "make_node_id",
    "get_aliases",
    "get_keywords",
    "infer_node_type",
    "normalize_node",

    # Paths
    "get_taxonomy_path",
    "build_learning_path",
    "build_learning_paths",

    # Search
    "find_taxonomy_nodes",
    "classify_text_into_taxonomy",
    "classify_skills",
    "taxonomy_lookup",

    # Analysis
    "calculate_taxonomy_coverage",
    "calculate_taxonomy_depth",
    "taxonomy_node_counts",
    "calculate_taxonomy_gap_priority",
    "identify_taxonomy_gaps",

    # Recommendations
    "recommend_next_nodes",

    # Reporting
    "build_taxonomy_summary",
    "taxonomy_to_rows",
    "taxonomy_tree",

    # Comparison
    "compare_taxonomies",

    # Serialization
    "node_to_dict",
    "relation_to_dict",
    "path_to_dict",
    "taxonomy_gap_to_dict",
    "taxonomy_result_to_dict",
    "taxonomy_result_to_json",
    "save_taxonomy_json",

    # Builders
    "build_default_taxonomy",
    "build_taxonomy_from_curriculum",
    "build_taxonomy_result",

    # Main API
    "analyze_taxonomy",

    # Knowledge base
    "DOMAIN_TAXONOMY",
    "SUBJECT_TAXONOMY",
    "TOPIC_CONCEPTS",
    "CONCEPT_SKILLS",
    "SKILL_TOOLS",
    "TOOL_SKILLS",
    "TAXONOMY_ALIASES",

    # Capabilities
    "TAXONOMY_CAPABILITIES",

]


# ============================================================
# END OF curriculum/taxonomy.py
# ============================================================
