# ============================================================
# industry/taxonomy.py
# CHUNK 1/10
#
# INDUSTRY SKILL / ROLE TAXONOMY
#
# Purpose:
#   Provide a structured taxonomy connecting:
#
#       Industry
#          ↓
#       Domain
#          ↓
#       Job Family
#          ↓
#       Role
#          ↓
#       Skills
#          ↓
#       Tools / Technologies
#          ↓
#       Concepts
#
# Used by:
#
#   industry/jd_parser.py
#   industry/skill_matcher.py
#   curriculum/skill_extractor.py
#   curriculum/comparator.py
#   curriculum/concept_intelligence.py
#   04_Gap_Enhancement.py
#   05_Reports.py
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
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)


# ============================================================
# VERSION
# ============================================================

TAXONOMY_VERSION = "1.0.0"


# ============================================================
# LEVELS
# ============================================================

LEVEL_INDUSTRY = "industry"

LEVEL_DOMAIN = "domain"

LEVEL_JOB_FAMILY = "job_family"

LEVEL_ROLE = "role"

LEVEL_SKILL = "skill"

LEVEL_TOOL = "tool"

LEVEL_CONCEPT = "concept"


# ============================================================
# NORMALIZATION
# ============================================================

def clean_text(
    value: Any,
) -> str:

    if value is None:
        return ""

    text = str(value)

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def normalize_text(
    value: Any,
) -> str:

    text = clean_text(
        value
    ).lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def normalize_key(
    value: Any,
) -> str:

    text = normalize_text(
        value
    )

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
# TAXONOMY NODE
# ============================================================

@dataclass
class TaxonomyNode:

    id: str

    name: str

    level: str

    description: str = ""

    parent_id: Optional[str] = None

    aliases: List[str] = field(
        default_factory=list
    )

    children: List[str] = field(
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

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SKILL DEFINITION
# ============================================================

@dataclass
class SkillDefinition:

    name: str

    category: str = "technical"

    description: str = ""

    aliases: List[str] = field(
        default_factory=list
    )

    parent_skills: List[str] = field(
        default_factory=list
    )

    related_skills: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    concepts: List[str] = field(
        default_factory=list
    )

    industries: List[str] = field(
        default_factory=list
    )

    job_families: List[str] = field(
        default_factory=list
    )

    beginner: bool = True

    intermediate: bool = True

    advanced: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# ROLE DEFINITION
# ============================================================

@dataclass
class RoleDefinition:

    name: str

    job_family: str

    domain: str

    description: str = ""

    aliases: List[str] = field(
        default_factory=list
    )

    core_skills: List[str] = field(
        default_factory=list
    )

    supporting_skills: List[str] = field(
        default_factory=list
    )

    tools: List[str] = field(
        default_factory=list
    )

    concepts: List[str] = field(
        default_factory=list
    )

    seniority_levels: List[str] = field(
        default_factory=list
    )

    industries: List[str] = field(
        default_factory=list
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
# INDUSTRY + DOMAIN TAXONOMY
# ============================================================


# ============================================================
# INDUSTRIES
# ============================================================

INDUSTRIES: Dict[str, Dict[str, Any]] = {

    "information_technology": {

        "name": "Information Technology",

        "aliases": [
            "IT",
            "Information Technology",
            "Technology",
        ],

        "domains": [

            "software_engineering",

            "data_science",

            "artificial_intelligence",

            "data_engineering",

            "cloud_computing",

            "devops",

            "cybersecurity",

            "business_intelligence",

            "web_development",

            "mobile_development",

        ],

    },

    "banking_financial_services": {

        "name":
            "Banking, Financial Services & Insurance",

        "aliases": [

            "BFSI",

            "Banking",

            "Finance",

            "Financial Services",

            "Insurance",

        ],

        "domains": [

            "financial_analytics",

            "risk_analytics",

            "fraud_detection",

            "fintech",

            "quantitative_finance",

            "financial_ai",

        ],

    },

    "healthcare": {

        "name": "Healthcare",

        "aliases": [

            "Healthcare",

            "Health Tech",

            "Medical Technology",

        ],

        "domains": [

            "healthcare_analytics",

            "medical_ai",

            "medical_imaging",

            "clinical_data",

            "healthcare_automation",

        ],

    },

    "manufacturing": {

        "name": "Manufacturing",

        "aliases": [

            "Manufacturing",

            "Industrial",

            "Industry 4.0",

        ],

        "domains": [

            "industrial_ai",

            "predictive_maintenance",

            "quality_analytics",

            "computer_vision",

            "robotics",

            "supply_chain_analytics",

        ],

    },

    "retail": {

        "name": "Retail & E-Commerce",

        "aliases": [

            "Retail",

            "E-commerce",

            "Ecommerce",

        ],

        "domains": [

            "customer_analytics",

            "recommendation_systems",

            "retail_ai",

            "demand_forecasting",

            "pricing_analytics",

        ],

    },

    "telecommunications": {

        "name": "Telecommunications",

        "aliases": [

            "Telecom",

            "Telecommunications",

        ],

        "domains": [

            "network_analytics",

            "telecom_ai",

            "network_automation",

            "customer_analytics",

        ],

    },

    "automotive": {

        "name": "Automotive",

        "aliases": [

            "Automotive",

            "Automobile",

            "Auto",

        ],

        "domains": [

            "autonomous_driving",

            "automotive_ai",

            "computer_vision",

            "predictive_maintenance",

            "embedded_ai",

        ],

    },

    "education": {

        "name": "Education & EdTech",

        "aliases": [

            "Education",

            "EdTech",

            "E-learning",

        ],

        "domains": [

            "educational_ai",

            "learning_analytics",

            "adaptive_learning",

            "intelligent_tutoring",

        ],

    },

    "logistics": {

        "name": "Logistics & Supply Chain",

        "aliases": [

            "Logistics",

            "Supply Chain",

        ],

        "domains": [

            "supply_chain_analytics",

            "route_optimization",

            "demand_forecasting",

            "logistics_ai",

        ],

    },

    "agriculture": {

        "name": "Agriculture & AgriTech",

        "aliases": [

            "Agriculture",

            "AgriTech",

            "AgTech",

        ],

        "domains": [

            "precision_agriculture",

            "crop_intelligence",

            "agricultural_ai",

            "remote_sensing",

        ],

    },

    "energy": {

        "name": "Energy & Utilities",

        "aliases": [

            "Energy",

            "Utilities",

            "Power",

        ],

        "domains": [

            "energy_analytics",

            "smart_grid",

            "energy_ai",

            "predictive_maintenance",

        ],

    },

    "media_entertainment": {

        "name": "Media & Entertainment",

        "aliases": [

            "Media",

            "Entertainment",

            "OTT",

        ],

        "domains": [

            "recommendation_systems",

            "content_ai",

            "computer_vision",

            "generative_ai",

        ],

    },

}


# ============================================================
# DOMAINS
# ============================================================

DOMAINS: Dict[str, Dict[str, Any]] = {

    "software_engineering": {

        "name": "Software Engineering",

        "industry": "information_technology",

        "job_families": [

            "backend_engineering",

            "frontend_engineering",

            "full_stack_engineering",

            "software_architecture",

        ],

    },

    "data_science": {

        "name": "Data Science",

        "industry": "information_technology",

        "job_families": [

            "data_science",

            "machine_learning",

            "applied_data_science",

        ],

    },

    "artificial_intelligence": {

        "name": "Artificial Intelligence",

        "industry": "information_technology",

        "job_families": [

            "machine_learning",

            "generative_ai",

            "computer_vision",

            "natural_language_processing",

            "agentic_ai",

        ],

    },

    "data_engineering": {

        "name": "Data Engineering",

        "industry": "information_technology",

        "job_families": [

            "data_engineering",

            "big_data",

            "analytics_engineering",

        ],

    },

    "cloud_computing": {

        "name": "Cloud Computing",

        "industry": "information_technology",

        "job_families": [

            "cloud_engineering",

            "cloud_architecture",

            "platform_engineering",

        ],

    },

    "devops": {

        "name": "DevOps & Platform Engineering",

        "industry": "information_technology",

        "job_families": [

            "devops",

            "site_reliability",

            "platform_engineering",

            "mlops",

        ],

    },

    "cybersecurity": {

        "name": "Cybersecurity",

        "industry": "information_technology",

        "job_families": [

            "security_engineering",

            "security_operations",

            "application_security",

            "ai_security",

        ],

    },

    "business_intelligence": {

        "name": "Business Intelligence",

        "industry": "information_technology",

        "job_families": [

            "business_intelligence",

            "data_analytics",

            "business_analysis",

        ],

    },

    "medical_ai": {

        "name": "Medical AI",

        "industry": "healthcare",

        "job_families": [

            "medical_imaging_ai",

            "clinical_ai",

            "healthcare_data_science",

        ],

    },

    "industrial_ai": {

        "name": "Industrial AI",

        "industry": "manufacturing",

        "job_families": [

            "industrial_data_science",

            "predictive_maintenance",

            "industrial_computer_vision",

        ],

    },

    "recommendation_systems": {

        "name": "Recommendation Systems",

        "industry": "retail",

        "job_families": [

            "recommender_engineering",

            "personalization",

            "customer_data_science",

        ],

    },

    "fintech": {

        "name": "FinTech",

        "industry": "banking_financial_services",

        "job_families": [

            "fintech_engineering",

            "financial_data_science",

            "fraud_analytics",

        ],

    },

}
# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# JOB FAMILIES + ROLES
# ============================================================


# ============================================================
# JOB FAMILIES
# ============================================================

JOB_FAMILIES: Dict[str, Dict[str, Any]] = {

    "machine_learning": {

        "name": "Machine Learning",

        "domain": "artificial_intelligence",

        "roles": [

            "machine_learning_engineer",

            "ml_engineer",

            "applied_ml_engineer",

        ],

    },

    "data_science": {

        "name": "Data Science",

        "domain": "data_science",

        "roles": [

            "data_scientist",

            "senior_data_scientist",

            "applied_data_scientist",

        ],

    },

    "generative_ai": {

        "name": "Generative AI",

        "domain": "artificial_intelligence",

        "roles": [

            "generative_ai_engineer",

            "llm_engineer",

            "rag_engineer",

            "ai_engineer",

        ],

    },

    "agentic_ai": {

        "name": "Agentic AI",

        "domain": "artificial_intelligence",

        "roles": [

            "agentic_ai_engineer",

            "ai_agent_engineer",

            "agent_engineer",

        ],

    },

    "natural_language_processing": {

        "name": "Natural Language Processing",

        "domain": "artificial_intelligence",

        "roles": [

            "nlp_engineer",

            "nlp_data_scientist",

            "language_ai_engineer",

        ],

    },

    "computer_vision": {

        "name": "Computer Vision",

        "domain": "artificial_intelligence",

        "roles": [

            "computer_vision_engineer",

            "vision_engineer",

            "image_ai_engineer",

        ],

    },

    "data_engineering": {

        "name": "Data Engineering",

        "domain": "data_engineering",

        "roles": [

            "data_engineer",

            "senior_data_engineer",

            "analytics_engineer",

        ],

    },

    "big_data": {

        "name": "Big Data",

        "domain": "data_engineering",

        "roles": [

            "big_data_engineer",

            "spark_engineer",

            "data_platform_engineer",

        ],

    },

    "backend_engineering": {

        "name": "Backend Engineering",

        "domain": "software_engineering",

        "roles": [

            "backend_engineer",

            "backend_developer",

            "api_engineer",

        ],

    },

    "frontend_engineering": {

        "name": "Frontend Engineering",

        "domain": "software_engineering",

        "roles": [

            "frontend_engineer",

            "frontend_developer",

            "ui_engineer",

        ],

    },

    "full_stack_engineering": {

        "name": "Full Stack Engineering",

        "domain": "software_engineering",

        "roles": [

            "full_stack_engineer",

            "full_stack_developer",

        ],

    },

    "cloud_engineering": {

        "name": "Cloud Engineering",

        "domain": "cloud_computing",

        "roles": [

            "cloud_engineer",

            "cloud_developer",

            "cloud_operations_engineer",

        ],

    },

    "cloud_architecture": {

        "name": "Cloud Architecture",

        "domain": "cloud_computing",

        "roles": [

            "cloud_architect",

            "solutions_architect",

        ],

    },

    "devops": {

        "name": "DevOps",

        "domain": "devops",

        "roles": [

            "devops_engineer",

            "devops_specialist",

        ],

    },

    "site_reliability": {

        "name": "Site Reliability Engineering",

        "domain": "devops",

        "roles": [

            "site_reliability_engineer",

            "sre_engineer",

        ],

    },

    "mlops": {

        "name": "MLOps",

        "domain": "devops",

        "roles": [

            "mlops_engineer",

            "machine_learning_platform_engineer",

        ],

    },

    "security_engineering": {

        "name": "Security Engineering",

        "domain": "cybersecurity",

        "roles": [

            "security_engineer",

            "application_security_engineer",

        ],

    },

    "security_operations": {

        "name": "Security Operations",

        "domain": "cybersecurity",

        "roles": [

            "soc_analyst",

            "security_operations_engineer",

        ],

    },

    "ai_security": {

        "name": "AI Security",

        "domain": "cybersecurity",

        "roles": [

            "ai_security_engineer",

            "llm_security_engineer",

            "ai_red_team_engineer",

        ],

    },

    "business_intelligence": {

        "name": "Business Intelligence",

        "domain": "business_intelligence",

        "roles": [

            "bi_developer",

            "business_intelligence_analyst",

            "power_bi_developer",

        ],

    },

    "data_analytics": {

        "name": "Data Analytics",

        "domain": "business_intelligence",

        "roles": [

            "data_analyst",

            "senior_data_analyst",

            "analytics_consultant",

        ],

    },

}


# ============================================================
# ROLE DEFINITIONS
# ============================================================

ROLES: Dict[str, RoleDefinition] = {

    "machine_learning_engineer":

        RoleDefinition(

            name="Machine Learning Engineer",

            job_family="machine_learning",

            domain="artificial_intelligence",

            aliases=[
                "ML Engineer",
                "Machine Learning Developer",
            ],

            core_skills=[

                "python",

                "machine learning",

                "scikit-learn",

                "statistics",

                "feature engineering",

                "model evaluation",

            ],

            supporting_skills=[

                "sql",

                "pandas",

                "numpy",

                "docker",

                "git",

            ],

            tools=[

                "scikit-learn",

                "pytorch",

                "tensorflow",

            ],

            concepts=[

                "supervised learning",

                "unsupervised learning",

                "model deployment",

                "feature engineering",

                "model evaluation",

            ],

            seniority_levels=[

                "entry",

                "junior",

                "mid",

                "senior",

                "lead",

            ],

        ),

    "data_scientist":

        RoleDefinition(

            name="Data Scientist",

            job_family="data_science",

            domain="data_science",

            aliases=[
                "Data Science Specialist",
            ],

            core_skills=[

                "python",

                "statistics",

                "machine learning",

                "data analysis",

                "pandas",

                "numpy",

                "sql",

            ],

            supporting_skills=[

                "scikit-learn",

                "visualization",

                "feature engineering",

                "time series",

            ],

            tools=[

                "jupyter",

                "pandas",

                "scikit-learn",

                "power bi",

                "tableau",

            ],

            concepts=[

                "statistical modeling",

                "predictive modeling",

                "experimentation",

                "hypothesis testing",

            ],

            seniority_levels=[

                "entry",

                "junior",

                "mid",

                "senior",

                "lead",

            ],

        ),

    "generative_ai_engineer":

        RoleDefinition(

            name="Generative AI Engineer",

            job_family="generative_ai",

            domain="artificial_intelligence",

            aliases=[

                "GenAI Engineer",

                "Generative AI Developer",

            ],

            core_skills=[

                "python",

                "generative ai",

                "large language models",

                "prompt engineering",

                "retrieval augmented generation",

                "embeddings",

            ],

            supporting_skills=[

                "vector databases",

                "langchain",

                "llamaindex",

                "hugging face",

                "docker",

                "aws",

            ],

            tools=[

                "LangChain",

                "LlamaIndex",

                "Hugging Face",

                "FAISS",

                "Chroma",

            ],

            concepts=[

                "transformers",

                "RAG",

                "fine tuning",

                "embeddings",

                "LLM evaluation",

            ],

            seniority_levels=[

                "junior",

                "mid",

                "senior",

                "lead",

            ],

        ),

    "llm_engineer":

        RoleDefinition(

            name="LLM Engineer",

            job_family="generative_ai",

            domain="artificial_intelligence",

            aliases=[

                "Large Language Model Engineer",

            ],

            core_skills=[

                "python",

                "large language models",

                "transformers",

                "prompt engineering",

                "retrieval augmented generation",

            ],

            supporting_skills=[

                "fine tuning",

                "embeddings",

                "vector databases",

                "langchain",

                "hugging face",

            ],

            tools=[

                "Hugging Face",

                "LangChain",

                "LlamaIndex",

            ],

            concepts=[

                "transformer architecture",

                "attention",

                "tokenization",

                "RAG",

                "fine tuning",

            ],

            seniority_levels=[

                "mid",

                "senior",

                "lead",

            ],

        ),

    "data_engineer":

        RoleDefinition(

            name="Data Engineer",

            job_family="data_engineering",

            domain="data_engineering",

            core_skills=[

                "python",

                "sql",

                "data engineering",

                "etl",

                "data pipelines",

            ],

            supporting_skills=[

                "apache spark",

                "apache kafka",

                "apache airflow",

                "cloud",

            ],

            tools=[

                "Spark",

                "Kafka",

                "Airflow",

                "AWS",

                "Azure",

                "GCP",

            ],

            concepts=[

                "data warehousing",

                "data lakes",

                "distributed systems",

                "ETL",

                "ELT",

            ],

            seniority_levels=[

                "entry",

                "junior",

                "mid",

                "senior",

                "lead",

            ],

        ),

    "devops_engineer":

        RoleDefinition(

            name="DevOps Engineer",

            job_family="devops",

            domain="devops",

            core_skills=[

                "git",

                "docker",

                "kubernetes",

                "ci/cd",

                "terraform",

            ],

            supporting_skills=[

                "aws",

                "azure",

                "gcp",

                "linux",

                "monitoring",

            ],

            tools=[

                "Docker",

                "Kubernetes",

                "Terraform",

                "Jenkins",

                "GitHub Actions",

            ],

            concepts=[

                "continuous integration",

                "continuous deployment",

                "infrastructure as code",

                "containerization",

                "observability",

            ],

            seniority_levels=[

                "junior",

                "mid",

                "senior",

                "lead",

            ],

        ),

}


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# SKILL TAXONOMY
# ============================================================


SKILLS: Dict[str, SkillDefinition] = {}


def register_skill(
    name: str,
    category: str = "technical",
    description: str = "",
    aliases: Optional[
        Sequence[str]
    ] = None,
    parent_skills: Optional[
        Sequence[str]
    ] = None,
    related_skills: Optional[
        Sequence[str]
    ] = None,
    tools: Optional[
        Sequence[str]
    ] = None,
    concepts: Optional[
        Sequence[str]
    ] = None,
    industries: Optional[
        Sequence[str]
    ] = None,
    job_families: Optional[
        Sequence[str]
    ] = None,
    beginner: bool = True,
    intermediate: bool = True,
    advanced: bool = True,
) -> SkillDefinition:

    definition = SkillDefinition(

        name=name,

        category=category,

        description=description,

        aliases=list(
            aliases
            or
            []
        ),

        parent_skills=list(
            parent_skills
            or
            []
        ),

        related_skills=list(
            related_skills
            or
            []
        ),

        tools=list(
            tools
            or
            []
        ),

        concepts=list(
            concepts
            or
            []
        ),

        industries=list(
            industries
            or
            []
        ),

        job_families=list(
            job_families
            or
            []
        ),

        beginner=beginner,

        intermediate=intermediate,

        advanced=advanced,

    )

    SKILLS[
        slugify(
            name
        )
    ] = definition

    return definition


# ============================================================
# PROGRAMMING
# ============================================================

register_skill(
    "Python",
    "programming",
    "General-purpose programming language widely used in AI and data engineering.",
    ["Python Programming"],
    related_skills=[
        "Pandas",
        "NumPy",
        "Scikit-Learn",
    ],
    concepts=[
        "functions",
        "classes",
        "modules",
        "object oriented programming",
    ],
    job_families=[
        "machine_learning",
        "data_science",
        "generative_ai",
        "data_engineering",
    ],
)

register_skill(
    "Java",
    "programming",
    aliases=[
        "Java Programming",
    ],
)

register_skill(
    "JavaScript",
    "programming",
    aliases=[
        "JS",
    ],
)

register_skill(
    "TypeScript",
    "programming",
    aliases=[
        "TS",
    ],
)

register_skill(
    "C++",
    "programming",
    aliases=[
        "CPP",
    ],
)

register_skill(
    "C#",
    "programming",
    aliases=[
        "C Sharp",
    ],
)

register_skill(
    "SQL",
    "database",
    aliases=[
        "Structured Query Language",
    ],
    related_skills=[
        "PostgreSQL",
        "MySQL",
        "Data Engineering",
    ],
    job_families=[
        "data_science",
        "data_engineering",
        "business_intelligence",
    ],
)


# ============================================================
# DATA
# ============================================================

register_skill(
    "Pandas",
    "data",
    aliases=[
        "Python Pandas",
    ],
    parent_skills=[
        "Python",
    ],
    related_skills=[
        "NumPy",
        "Data Analysis",
    ],
    tools=[
        "Python",
    ],
)

register_skill(
    "NumPy",
    "data",
    aliases=[
        "Numpy",
    ],
    parent_skills=[
        "Python",
    ],
)

register_skill(
    "Data Analysis",
    "data",
    aliases=[
        "Data Analytics",
    ],
    concepts=[
        "exploratory data analysis",
        "statistical analysis",
        "data visualization",
    ],
)

register_skill(
    "Statistics",
    "mathematics",
    aliases=[
        "Statistical Analysis",
    ],
    concepts=[
        "probability",
        "hypothesis testing",
        "regression",
        "confidence intervals",
    ],
)


# ============================================================
# MACHINE LEARNING
# ============================================================

register_skill(
    "Machine Learning",
    "machine_learning",
    aliases=[
        "ML",
    ],
    concepts=[
        "supervised learning",
        "unsupervised learning",
        "model evaluation",
        "feature engineering",
    ],
)

register_skill(
    "Scikit-Learn",
    "machine_learning",
    aliases=[
        "Sklearn",
        "Scikit Learn",
    ],
    parent_skills=[
        "Machine Learning",
    ],
    tools=[
        "Python",
    ],
)

register_skill(
    "Feature Engineering",
    "machine_learning",
    concepts=[
        "feature selection",
        "feature extraction",
        "dimensionality reduction",
    ],
)

register_skill(
    "Model Evaluation",
    "machine_learning",
    concepts=[
        "cross validation",
        "precision",
        "recall",
        "f1 score",
        "roc auc",
    ],
)

register_skill(
    "Time Series",
    "machine_learning",
    aliases=[
        "Time-Series",
        "Forecasting",
    ],
    concepts=[
        "forecasting",
        "seasonality",
        "trend",
        "arima",
    ],
)

register_skill(
    "Recommendation Systems",
    "machine_learning",
    aliases=[
        "Recommender Systems",
        "Recommendation Engines",
    ],
    concepts=[
        "collaborative filtering",
        "content based filtering",
        "personalization",
    ],
)


# ============================================================
# DEEP LEARNING
# ============================================================

register_skill(
    "Deep Learning",
    "deep_learning",
    aliases=[
        "DL",
    ],
    concepts=[
        "neural networks",
        "backpropagation",
        "optimization",
        "representation learning",
    ],
)

register_skill(
    "TensorFlow",
    "deep_learning",
    aliases=[
        "Tensor Flow",
    ],
    parent_skills=[
        "Deep Learning",
    ],
)

register_skill(
    "PyTorch",
    "deep_learning",
    aliases=[
        "Torch",
    ],
    parent_skills=[
        "Deep Learning",
    ],
)

register_skill(
    "Keras",
    "deep_learning",
    parent_skills=[
        "TensorFlow",
        "Deep Learning",
    ],
)


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# GENERATIVE AI + NLP + AGENTIC AI
# ============================================================


# ============================================================
# NLP
# ============================================================

register_skill(
    "Natural Language Processing",
    "nlp",
    aliases=[
        "NLP",
    ],
    concepts=[
        "tokenization",
        "stemming",
        "lemmatization",
        "named entity recognition",
        "text classification",
        "sentiment analysis",
    ],
)

register_skill(
    "Transformers",
    "nlp",
    concepts=[
        "attention",
        "self attention",
        "encoder decoder",
        "transformer architecture",
    ],
    related_skills=[
        "Large Language Models",
        "Hugging Face",
    ],
)

register_skill(
    "Large Language Models",
    "generative_ai",
    aliases=[
        "LLM",
        "LLMs",
        "Large Language Model",
    ],
    parent_skills=[
        "Generative AI",
    ],
    related_skills=[
        "Transformers",
        "Prompt Engineering",
        "RAG",
        "Fine Tuning",
    ],
    concepts=[
        "tokenization",
        "attention",
        "context window",
        "inference",
        "evaluation",
    ],
)


# ============================================================
# GENERATIVE AI
# ============================================================

register_skill(
    "Generative AI",
    "generative_ai",
    aliases=[
        "GenAI",
        "Gen AI",
    ],
    concepts=[
        "foundation models",
        "large language models",
        "multimodal models",
        "AI agents",
        "synthetic data",
    ],
    job_families=[
        "generative_ai",
        "agentic_ai",
    ],
)

register_skill(
    "Prompt Engineering",
    "generative_ai",
    aliases=[
        "Prompt Design",
    ],
    parent_skills=[
        "Generative AI",
    ],
    concepts=[
        "few shot prompting",
        "zero shot prompting",
        "chain of thought",
        "structured prompting",
        "prompt optimization",
    ],
)

register_skill(
    "Embeddings",
    "generative_ai",
    aliases=[
        "Embedding Models",
        "Vector Embeddings",
    ],
    concepts=[
        "semantic similarity",
        "dense vectors",
        "representation learning",
    ],
)

register_skill(
    "Retrieval Augmented Generation",
    "generative_ai",
    aliases=[
        "RAG",
        "Retrieval-Augmented Generation",
    ],
    parent_skills=[
        "Large Language Models",
    ],
    related_skills=[
        "Embeddings",
        "Vector Databases",
        "LangChain",
        "LlamaIndex",
    ],
    concepts=[
        "retrieval",
        "chunking",
        "reranking",
        "context injection",
        "grounding",
    ],
)

register_skill(
    "Vector Databases",
    "database",
    aliases=[
        "Vector Database",
        "Vector DB",
    ],
    related_skills=[
        "Embeddings",
        "RAG",
    ],
    tools=[
        "FAISS",
        "Chroma",
        "Pinecone",
        "Weaviate",
    ],
)

register_skill(
    "Fine Tuning",
    "generative_ai",
    aliases=[
        "Fine-Tuning",
        "Finetuning",
    ],
    concepts=[
        "supervised fine tuning",
        "instruction tuning",
        "parameter efficient fine tuning",
        "LoRA",
        "QLoRA",
    ],
)


# ============================================================
# LANGCHAIN
# ============================================================

register_skill(
    "LangChain",
    "generative_ai",
    aliases=[
        "Lang Chain",
    ],
    related_skills=[
        "RAG",
        "LLM",
        "Agentic AI",
    ],
    tools=[
        "Python",
    ],
)


# ============================================================
# LANGGRAPH
# ============================================================

register_skill(
    "LangGraph",
    "agentic_ai",
    aliases=[
        "Lang Graph",
    ],
    parent_skills=[
        "LangChain",
    ],
    related_skills=[
        "Agentic AI",
        "Multi Agent Systems",
    ],
    concepts=[
        "state machines",
        "workflow graphs",
        "agent orchestration",
        "checkpointing",
        "human in the loop",
    ],
)


# ============================================================
# LLAMAINDEX
# ============================================================

register_skill(
    "LlamaIndex",
    "generative_ai",
    aliases=[
        "Llama Index",
    ],
    related_skills=[
        "RAG",
        "Embeddings",
        "Vector Databases",
    ],
)


# ============================================================
# HUGGING FACE
# ============================================================

register_skill(
    "Hugging Face",
    "generative_ai",
    aliases=[
        "HuggingFace",
    ],
    related_skills=[
        "Transformers",
        "LLM",
        "Fine Tuning",
    ],
)


# ============================================================
# AGENTIC AI
# ============================================================

register_skill(
    "Agentic AI",
    "agentic_ai",
    aliases=[
        "AI Agents",
        "Agentic Artificial Intelligence",
    ],
    related_skills=[
        "Generative AI",
        "LangGraph",
        "LangChain",
    ],
    concepts=[
        "tool calling",
        "planning",
        "reasoning",
        "memory",
        "workflow orchestration",
        "multi agent systems",
        "human in the loop",
    ],
)

register_skill(
    "Multi Agent Systems",
    "agentic_ai",
    aliases=[
        "Multi-Agent Systems",
        "Multi Agent AI",
    ],
    parent_skills=[
        "Agentic AI",
    ],
    concepts=[
        "agent coordination",
        "agent communication",
        "task delegation",
        "agent orchestration",
    ],
)


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# CLOUD + DEVOPS + DATA ENGINEERING + MLOPS
# ============================================================


# ============================================================
# CLOUD
# ============================================================

register_skill(
    "Cloud Computing",
    "cloud",
    aliases=[
        "Cloud",
        "Cloud Technology",
    ],
    concepts=[
        "cloud architecture",
        "scalability",
        "high availability",
        "cloud security",
    ],
)

register_skill(
    "AWS",
    "cloud",
    aliases=[
        "Amazon Web Services",
    ],
    parent_skills=[
        "Cloud Computing",
    ],
)

register_skill(
    "Azure",
    "cloud",
    aliases=[
        "Microsoft Azure",
    ],
    parent_skills=[
        "Cloud Computing",
    ],
)

register_skill(
    "GCP",
    "cloud",
    aliases=[
        "Google Cloud",
        "Google Cloud Platform",
    ],
    parent_skills=[
        "Cloud Computing",
    ],
)


# ============================================================
# DEVOPS
# ============================================================

register_skill(
    "Git",
    "devops",
    aliases=[
        "Git Version Control",
    ],
)

register_skill(
    "Docker",
    "devops",
    aliases=[
        "Containerization",
        "Containers",
    ],
    concepts=[
        "containerization",
        "images",
        "containers",
        "registries",
    ],
)

register_skill(
    "Kubernetes",
    "devops",
    aliases=[
        "K8s",
    ],
    concepts=[
        "pods",
        "services",
        "deployments",
        "orchestration",
    ],
)

register_skill(
    "Terraform",
    "devops",
    aliases=[
        "Infrastructure as Code",
        "IaC",
    ],
    concepts=[
        "infrastructure as code",
        "cloud provisioning",
        "state management",
    ],
)

register_skill(
    "CI/CD",
    "devops",
    aliases=[
        "Continuous Integration",
        "Continuous Delivery",
        "Continuous Deployment",
    ],
)


# ============================================================
# MLOPS
# ============================================================

register_skill(
    "MLOps",
    "mlops",
    aliases=[
        "Machine Learning Operations",
    ],
    parent_skills=[
        "DevOps",
    ],
    concepts=[
        "model deployment",
        "model monitoring",
        "model versioning",
        "experiment tracking",
        "model registry",
    ],
)

register_skill(
    "MLflow",
    "mlops",
    concepts=[
        "experiment tracking",
        "model registry",
        "model lifecycle",
    ],
)

register_skill(
    "Kubeflow",
    "mlops",
    concepts=[
        "ML pipelines",
        "model serving",
        "machine learning orchestration",
    ],
)


# ============================================================
# DATA ENGINEERING
# ============================================================

register_skill(
    "Data Engineering",
    "data_engineering",
    aliases=[
        "Data Engineering",
    ],
    concepts=[
        "ETL",
        "ELT",
        "data pipelines",
        "data warehousing",
        "data lakes",
    ],
)

register_skill(
    "Apache Spark",
    "data_engineering",
    aliases=[
        "Spark",
        "PySpark",
    ],
    related_skills=[
        "Data Engineering",
        "Big Data",
    ],
)

register_skill(
    "Apache Kafka",
    "data_engineering",
    aliases=[
        "Kafka",
    ],
    concepts=[
        "event streaming",
        "message queues",
        "distributed systems",
    ],
)

register_skill(
    "Apache Airflow",
    "data_engineering",
    aliases=[
        "Airflow",
    ],
    concepts=[
        "workflow orchestration",
        "DAGs",
        "data pipelines",
    ],
)


# ============================================================
# DATABASES
# ============================================================

register_skill(
    "PostgreSQL",
    "database",
    aliases=[
        "Postgres",
    ],
)

register_skill(
    "MySQL",
    "database",
)

register_skill(
    "MongoDB",
    "database",
    aliases=[
        "Mongo",
    ],
)

register_skill(
    "Redis",
    "database",
)


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# COMPUTER VISION + BI + CYBERSECURITY
# + INDUSTRY-SPECIFIC SKILLS
# ============================================================


# ============================================================
# COMPUTER VISION
# ============================================================

register_skill(
    "Computer Vision",
    "computer_vision",
    aliases=[
        "CV",
        "Computer Vision AI",
    ],
    concepts=[
        "image classification",
        "object detection",
        "image segmentation",
        "image processing",
        "feature extraction",
    ],
)

register_skill(
    "OpenCV",
    "computer_vision",
    aliases=[
        "OpenCV-Python",
    ],
    parent_skills=[
        "Computer Vision",
    ],
)

register_skill(
    "YOLO",
    "computer_vision",
    aliases=[
        "YOLOv5",
        "YOLOv8",
        "YOLOv9",
        "YOLOv10",
        "YOLOv11",
    ],
    parent_skills=[
        "Computer Vision",
    ],
    concepts=[
        "object detection",
        "real time detection",
    ],
)

register_skill(
    "Image Segmentation",
    "computer_vision",
    parent_skills=[
        "Computer Vision",
    ],
)

register_skill(
    "Object Detection",
    "computer_vision",
    parent_skills=[
        "Computer Vision",
    ],
)


# ============================================================
# BUSINESS INTELLIGENCE
# ============================================================

register_skill(
    "Business Intelligence",
    "business_intelligence",
    aliases=[
        "BI",
        "Business Analytics",
    ],
    concepts=[
        "dashboarding",
        "reporting",
        "data visualization",
        "KPI analysis",
    ],
)

register_skill(
    "Power BI",
    "business_intelligence",
    aliases=[
        "PowerBI",
        "Microsoft Power BI",
    ],
    parent_skills=[
        "Business Intelligence",
    ],
    concepts=[
        "DAX",
        "data modeling",
        "dashboarding",
    ],
)

register_skill(
    "Tableau",
    "business_intelligence",
    parent_skills=[
        "Business Intelligence",
    ],
)

register_skill(
    "Excel",
    "business_intelligence",
    aliases=[
        "Microsoft Excel",
    ],
)


# ============================================================
# CYBERSECURITY
# ============================================================

register_skill(
    "Cybersecurity",
    "cybersecurity",
    aliases=[
        "Cyber Security",
        "Information Security",
    ],
    concepts=[
        "threat detection",
        "vulnerability management",
        "security monitoring",
        "incident response",
    ],
)

register_skill(
    "Application Security",
    "cybersecurity",
    aliases=[
        "AppSec",
    ],
    parent_skills=[
        "Cybersecurity",
    ],
)

register_skill(
    "Cloud Security",
    "cybersecurity",
    parent_skills=[
        "Cybersecurity",
    ],
)

register_skill(
    "AI Security",
    "ai_security",
    aliases=[
        "AI Cybersecurity",
    ],
    parent_skills=[
        "Cybersecurity",
    ],
    concepts=[
        "prompt injection",
        "LLM security",
        "AI red teaming",
        "model security",
    ],
)

register_skill(
    "LLM Security",
    "ai_security",
    parent_skills=[
        "AI Security",
    ],
    concepts=[
        "prompt injection",
        "jailbreak detection",
        "data leakage",
        "model abuse",
    ],
)


# ============================================================
# FINTECH
# ============================================================

register_skill(
    "Financial Analytics",
    "finance",
    concepts=[
        "financial modeling",
        "risk analysis",
        "forecasting",
    ],
    industries=[
        "banking_financial_services",
    ],
)

register_skill(
    "Fraud Detection",
    "finance",
    concepts=[
        "anomaly detection",
        "classification",
        "transaction monitoring",
    ],
    industries=[
        "banking_financial_services",
        "retail",
    ],
)

register_skill(
    "Risk Analytics",
    "finance",
    concepts=[
        "credit risk",
        "market risk",
        "operational risk",
    ],
    industries=[
        "banking_financial_services",
    ],
)


# ============================================================
# MANUFACTURING
# ============================================================

register_skill(
    "Predictive Maintenance",
    "industrial_ai",
    concepts=[
        "anomaly detection",
        "time series forecasting",
        "condition monitoring",
    ],
    industries=[
        "manufacturing",
        "automotive",
        "energy",
    ],
)

register_skill(
    "Quality Analytics",
    "industrial_ai",
    concepts=[
        "quality control",
        "defect detection",
        "statistical process control",
    ],
    industries=[
        "manufacturing",
    ],
)

register_skill(
    "Industrial Computer Vision",
    "industrial_ai",
    parent_skills=[
        "Computer Vision",
    ],
    industries=[
        "manufacturing",
        "automotive",
    ],
)


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# TAXONOMY ENGINE
# ============================================================


class IndustryTaxonomy:

    def __init__(
        self,
    ):

        self.industries = INDUSTRIES

        self.domains = DOMAINS

        self.job_families = JOB_FAMILIES

        self.roles = ROLES

        self.skills = SKILLS


    # ========================================================
    # INDUSTRIES
    # ========================================================

    def list_industries(
        self,
    ) -> List[str]:

        return [

            item["name"]

            for item
            in self.industries.values()

        ]


    # ========================================================
    # DOMAINS
    # ========================================================

    def list_domains(
        self,
    ) -> List[str]:

        return [

            item["name"]

            for item
            in self.domains.values()

        ]


    # ========================================================
    # JOB FAMILIES
    # ========================================================

    def list_job_families(
        self,
    ) -> List[str]:

        return [

            item["name"]

            for item
            in self.job_families.values()

        ]


    # ========================================================
    # ROLES
    # ========================================================

    def list_roles(
        self,
    ) -> List[str]:

        return [

            role.name

            for role
            in self.roles.values()

        ]


    # ========================================================
    # SKILLS
    # ========================================================

    def list_skills(
        self,
    ) -> List[str]:

        return [

            skill.name

            for skill
            in self.skills.values()

        ]


    # ========================================================
    # FIND INDUSTRY
    # ========================================================

    def find_industry(
        self,
        value: str,
    ) -> Optional[str]:

        normalized = normalize_key(
            value
        )

        for key, item in (
            self.industries.items()
        ):

            if normalize_key(
                item["name"]
            ) == normalized:

                return key

            for alias in item.get(
                "aliases",
                [],
            ):

                if normalize_key(
                    alias
                ) == normalized:

                    return key

            if key == slugify(
                value
            ):

                return key

        return None


    # ========================================================
    # FIND DOMAIN
    # ========================================================

    def find_domain(
        self,
        value: str,
    ) -> Optional[str]:

        normalized = normalize_key(
            value
        )

        for key, item in (
            self.domains.items()
        ):

            if normalize_key(
                item["name"]
            ) == normalized:

                return key

            if key == slugify(
                value
            ):

                return key

        return None


    # ========================================================
    # FIND JOB FAMILY
    # ========================================================

    def find_job_family(
        self,
        value: str,
    ) -> Optional[str]:

        normalized = normalize_key(
            value
        )

        for key, item in (
            self.job_families.items()
        ):

            if normalize_key(
                item["name"]
            ) == normalized:

                return key

            if key == slugify(
                value
            ):

                return key

        return None


    # ========================================================
    # FIND ROLE
    # ========================================================

    def find_role(
        self,
        value: str,
    ) -> Optional[str]:

        normalized = normalize_key(
            value
        )

        slug = slugify(
            value
        )

        for key, role in (
            self.roles.items()
        ):

            if key == slug:

                return key

            if normalize_key(
                role.name
            ) == normalized:

                return key

            for alias in role.aliases:

                if normalize_key(
                    alias
                ) == normalized:

                    return key

        return None


    # ========================================================
    # FIND SKILL
    # ========================================================

    def find_skill(
        self,
        value: str,
    ) -> Optional[str]:

        normalized = normalize_key(
            value
        )

        slug = slugify(
            value
        )

        for key, skill in (
            self.skills.items()
        ):

            if key == slug:

                return key

            if normalize_key(
                skill.name
            ) == normalized:

                return key

            for alias in skill.aliases:

                if normalize_key(
                    alias
                ) == normalized:

                    return key

        return None


    # ========================================================
    # GET INDUSTRY DOMAINS
    # ========================================================

    def get_industry_domains(
        self,
        industry: str,
    ) -> List[str]:

        key = self.find_industry(
            industry
        )

        if not key:
            return []

        return list(

            self.industries[
                key
            ].get(
                "domains",
                [],
            )

        )


    # ========================================================
    # GET DOMAIN JOB FAMILIES
    # ========================================================

    def get_domain_job_families(
        self,
        domain: str,
    ) -> List[str]:

        key = self.find_domain(
            domain
        )

        if not key:
            return []

        return list(

            self.domains[
                key
            ].get(
                "job_families",
                [],
            )

        )


    # ========================================================
    # GET JOB FAMILY ROLES
    # ========================================================

    def get_job_family_roles(
        self,
        job_family: str,
    ) -> List[str]:

        key = self.find_job_family(
            job_family
        )

        if not key:
            return []

        return list(

            self.job_families[
                key
            ].get(
                "roles",
                [],
            )

        )


# ============================================================
# GLOBAL TAXONOMY INSTANCE
# ============================================================

taxonomy = IndustryTaxonomy()


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# SKILL + ROLE INTELLIGENCE
# ============================================================


# ============================================================
# GET SKILL DEFINITION
# ============================================================

def get_skill_definition(
    skill: str,
) -> Optional[SkillDefinition]:

    key = taxonomy.find_skill(
        skill
    )

    if not key:
        return None

    return taxonomy.skills.get(
        key
    )


# ============================================================
# GET SKILL ALIASES
# ============================================================

def get_skill_aliases(
    skill: str,
) -> List[str]:

    definition = get_skill_definition(
        skill
    )

    if not definition:
        return []

    return deduplicate(

        [

            definition.name

        ]

        +

        definition.aliases

    )


# ============================================================
# GET PARENT SKILLS
# ============================================================

def get_parent_skills(
    skill: str,
) -> List[str]:

    definition = get_skill_definition(
        skill
    )

    if not definition:
        return []

    return deduplicate(

        definition.parent_skills

    )


# ============================================================
# GET RELATED SKILLS
# ============================================================

def get_related_skills(
    skill: str,
) -> List[str]:

    definition = get_skill_definition(
        skill
    )

    if not definition:
        return []

    return deduplicate(

        definition.related_skills

    )


# ============================================================
# GET SKILL TOOLS
# ============================================================

def get_skill_tools(
    skill: str,
) -> List[str]:

    definition = get_skill_definition(
        skill
    )

    if not definition:
        return []

    return deduplicate(

        definition.tools

    )


# ============================================================
# GET SKILL CONCEPTS
# ============================================================

def get_skill_concepts(
    skill: str,
) -> List[str]:

    definition = get_skill_definition(
        skill
    )

    if not definition:
        return []

    return deduplicate(

        definition.concepts

    )


# ============================================================
# GET SKILL CATEGORY
# ============================================================

def get_skill_category(
    skill: str,
) -> str:

    definition = get_skill_definition(
        skill
    )

    if not definition:
        return "unknown"

    return definition.category


# ============================================================
# GET ROLE
# ============================================================

def get_role_definition(
    role: str,
) -> Optional[RoleDefinition]:

    key = taxonomy.find_role(
        role
    )

    if not key:
        return None

    return taxonomy.roles.get(
        key
    )


# ============================================================
# ROLE SKILLS
# ============================================================

def get_role_skills(
    role: str,
) -> List[str]:

    definition = get_role_definition(
        role
    )

    if not definition:
        return []

    return deduplicate(

        definition.core_skills

        +

        definition.supporting_skills

    )


# ============================================================
# ROLE CORE SKILLS
# ============================================================

def get_role_core_skills(
    role: str,
) -> List[str]:

    definition = get_role_definition(
        role
    )

    if not definition:
        return []

    return deduplicate(

        definition.core_skills

    )


# ============================================================
# ROLE SUPPORTING SKILLS
# ============================================================

def get_role_supporting_skills(
    role: str,
) -> List[str]:

    definition = get_role_definition(
        role
    )

    if not definition:
        return []

    return deduplicate(

        definition.supporting_skills

    )


# ============================================================
# ROLE TOOLS
# ============================================================

def get_role_tools(
    role: str,
) -> List[str]:

    definition = get_role_definition(
        role
    )

    if not definition:
        return []

    return deduplicate(

        definition.tools

    )


# ============================================================
# ROLE CONCEPTS
# ============================================================

def get_role_concepts(
    role: str,
) -> List[str]:

    definition = get_role_definition(
        role
    )

    if not definition:
        return []

    return deduplicate(

        definition.concepts

    )


# ============================================================
# ROLE → INDUSTRIES
# ============================================================

def get_role_industries(
    role: str,
) -> List[str]:

    definition = get_role_definition(
        role
    )

    if not definition:
        return []

    return deduplicate(

        definition.industries

    )


# ============================================================
# FIND ROLES FOR SKILL
# ============================================================

def find_roles_for_skill(
    skill: str,
) -> List[str]:

    normalized = normalize_key(
        skill
    )

    results = []

    for key, role in (
        taxonomy.roles.items()
    ):

        role_skills = (

            role.core_skills

            +

            role.supporting_skills

        )

        if any(

            normalize_key(
                item
            )
            ==
            normalized

            for item
            in role_skills

        ):

            results.append(
                role.name
            )

    return deduplicate(
        results
    )


# ============================================================
# FIND SKILLS FOR INDUSTRY
# ============================================================

def find_industry_skills(
    industry: str,
) -> List[str]:

    industry_key = taxonomy.find_industry(
        industry
    )

    if not industry_key:
        return []

    results = []

    for skill in taxonomy.skills.values():

        if industry_key in skill.industries:

            results.append(
                skill.name
            )

    # Also infer from roles under domains.
    domains = taxonomy.get_industry_domains(
        industry_key
    )

    for domain in domains:

        for family in taxonomy.get_domain_job_families(
            domain
        ):

            for role_key in taxonomy.get_job_family_roles(
                family
            ):

                role = taxonomy.roles.get(
                    role_key
                )

                if role:

                    results.extend(
                        role.core_skills
                    )

                    results.extend(
                        role.supporting_skills
                    )

    return deduplicate(
        results
    )


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# SEARCH + CLASSIFICATION + SERIALIZATION
# ============================================================


# ============================================================
# SEARCH TAXONOMY
# ============================================================

def search_taxonomy(
    query: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:

    normalized = normalize_key(
        query
    )

    if not normalized:
        return []

    results = []

    # --------------------------------------------------------
    # Industries
    # --------------------------------------------------------

    for key, item in (
        taxonomy.industries.items()
    ):

        score = 0.0

        name = normalize_key(
            item["name"]
        )

        if normalized == name:

            score = 1.0

        elif normalized in name:

            score = 0.85

        else:

            for alias in item.get(
                "aliases",
                [],
            ):

                alias_normalized = normalize_key(
                    alias
                )

                if normalized in alias_normalized:

                    score = max(
                        score,
                        0.75,
                    )

        if score > 0:

            results.append({

                "type":
                    LEVEL_INDUSTRY,

                "id":
                    key,

                "name":
                    item["name"],

                "score":
                    score,

            })

    # --------------------------------------------------------
    # Domains
    # --------------------------------------------------------

    for key, item in (
        taxonomy.domains.items()
    ):

        name = normalize_key(
            item["name"]
        )

        score = 0.0

        if normalized == name:

            score = 1.0

        elif normalized in name:

            score = 0.85

        if score > 0:

            results.append({

                "type":
                    LEVEL_DOMAIN,

                "id":
                    key,

                "name":
                    item["name"],

                "score":
                    score,

            })

    # --------------------------------------------------------
    # Job Families
    # --------------------------------------------------------

    for key, item in (
        taxonomy.job_families.items()
    ):

        name = normalize_key(
            item["name"]
        )

        score = 0.0

        if normalized == name:

            score = 1.0

        elif normalized in name:

            score = 0.85

        if score > 0:

            results.append({

                "type":
                    LEVEL_JOB_FAMILY,

                "id":
                    key,

                "name":
                    item["name"],

                "score":
                    score,

            })

    # --------------------------------------------------------
    # Roles
    # --------------------------------------------------------

    for key, role in (
        taxonomy.roles.items()
    ):

        score = 0.0

        name = normalize_key(
            role.name
        )

        if normalized == name:

            score = 1.0

        elif normalized in name:

            score = 0.85

        else:

            for alias in role.aliases:

                if normalized in normalize_key(
                    alias
                ):

                    score = 0.75

        if score > 0:

            results.append({

                "type":
                    LEVEL_ROLE,

                "id":
                    key,

                "name":
                    role.name,

                "score":
                    score,

            })

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    for key, skill in (
        taxonomy.skills.items()
    ):

        score = 0.0

        name = normalize_key(
            skill.name
        )

        if normalized == name:

            score = 1.0

        elif normalized in name:

            score = 0.85

        else:

            for alias in skill.aliases:

                if normalized in normalize_key(
                    alias
                ):

                    score = 0.75

        if score > 0:

            results.append({

                "type":
                    LEVEL_SKILL,

                "id":
                    key,

                "name":
                    skill.name,

                "score":
                    score,

                "category":
                    skill.category,

            })

    results.sort(

        key=lambda item:
            item["score"],

        reverse=True,

    )

    return results[
        :limit
    ]


# ============================================================
# CLASSIFY SKILL
# ============================================================

def classify_skill(
    skill: str,
) -> Dict[str, Any]:

    definition = get_skill_definition(
        skill
    )

    if not definition:

        return {

            "skill":
                skill,

            "normalized":
                normalize_key(
                    skill
                ),

            "known":
                False,

            "category":
                "unknown",

            "aliases":
                [],

            "parent_skills":
                [],

            "related_skills":
                [],

            "tools":
                [],

            "concepts":
                [],

            "job_families":
                [],

            "industries":
                [],

        }

    return {

        "skill":
            definition.name,

        "normalized":
            normalize_key(
                definition.name
            ),

        "known":
            True,

        "category":
            definition.category,

        "aliases":
            definition.aliases,

        "parent_skills":
            definition.parent_skills,

        "related_skills":
            definition.related_skills,

        "tools":
            definition.tools,

        "concepts":
            definition.concepts,

        "job_families":
            definition.job_families,

        "industries":
            definition.industries,

    }


# ============================================================
# ROLE INTELLIGENCE
# ============================================================

def role_intelligence(
    role: str,
) -> Dict[str, Any]:

    definition = get_role_definition(
        role
    )

    if not definition:

        return {

            "role":
                role,

            "known":
                False,

            "job_family":
                "",

            "domain":
                "",

            "core_skills":
                [],

            "supporting_skills":
                [],

            "tools":
                [],

            "concepts":
                [],

            "seniority_levels":
                [],

        }

    return {

        "role":
            definition.name,

        "known":
            True,

        "job_family":
            definition.job_family,

        "domain":
            definition.domain,

        "description":
            definition.description,

        "aliases":
            definition.aliases,

        "core_skills":
            definition.core_skills,

        "supporting_skills":
            definition.supporting_skills,

        "tools":
            definition.tools,

        "concepts":
            definition.concepts,

        "seniority_levels":
            definition.seniority_levels,

        "industries":
            definition.industries,

    }


# ============================================================
# TAXONOMY TREE
# ============================================================

def taxonomy_tree() -> Dict[str, Any]:

    result = {}

    for industry_key, industry in (
        taxonomy.industries.items()
    ):

        result[
            industry_key
        ] = {

            "name":
                industry["name"],

            "domains": {},

        }

        for domain_key in industry.get(
            "domains",
            [],
        ):

            domain = taxonomy.domains.get(
                domain_key
            )

            if not domain:
                continue

            result[
                industry_key
            ][
                "domains"
            ][
                domain_key
            ] = {

                "name":
                    domain["name"],

                "job_families": {},

            }

            for family_key in domain.get(
                "job_families",
                [],
            ):

                family = taxonomy.job_families.get(
                    family_key
                )

                if not family:
                    continue

                result[
                    industry_key
                ][
                    "domains"
                ][
                    domain_key
                ][
                    "job_families"
                ][
                    family_key
                ] = {

                    "name":
                        family["name"],

                    "roles":
                        family.get(
                            "roles",
                            [],
                        ),

                }

    return result


# ============================================================
# SERIALIZATION
# ============================================================

def taxonomy_to_dict() -> Dict[str, Any]:

    return {

        "version":
            TAXONOMY_VERSION,

        "industries":
            taxonomy.industries,

        "domains":
            taxonomy.domains,

        "job_families":
            taxonomy.job_families,

        "roles": {

            key:
                asdict(
                    value
                )

            for key, value
            in taxonomy.roles.items()

        },

        "skills": {

            key:
                asdict(
                    value
                )

            for key, value
            in taxonomy.skills.items()

        },

    }


# ============================================================
# TAXONOMY JSON
# ============================================================

def taxonomy_to_json(
    indent: int = 2,
) -> str:

    return json.dumps(

        taxonomy_to_dict(),

        indent=indent,

        ensure_ascii=False,

    )


# ============================================================
# SAVE TAXONOMY
# ============================================================

def save_taxonomy(
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

        taxonomy_to_json(),

        encoding="utf-8",

    )

    return path


# ============================================================
# TAXONOMY STATISTICS
# ============================================================

def taxonomy_statistics() -> Dict[str, int]:

    return {

        "industries":
            len(
                taxonomy.industries
            ),

        "domains":
            len(
                taxonomy.domains
            ),

        "job_families":
            len(
                taxonomy.job_families
            ),

        "roles":
            len(
                taxonomy.roles
            ),

        "skills":
            len(
                taxonomy.skills
            ),

    }


# ============================================================
# PUBLIC API
# ============================================================

TAXONOMY_CAPABILITIES = [

    "industry_taxonomy",

    "domain_taxonomy",

    "job_family_taxonomy",

    "role_taxonomy",

    "skill_taxonomy",

    "skill_aliases",

    "skill_relationships",

    "skill_parent_mapping",

    "skill_category_mapping",

    "skill_to_role_mapping",

    "role_to_skill_mapping",

    "industry_to_skill_mapping",

    "taxonomy_search",

    "skill_classification",

    "role_intelligence",

    "taxonomy_tree",

    "taxonomy_serialization",

    "taxonomy_statistics",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "TAXONOMY_VERSION",

    # Levels
    "LEVEL_INDUSTRY",

    "LEVEL_DOMAIN",

    "LEVEL_JOB_FAMILY",

    "LEVEL_ROLE",

    "LEVEL_SKILL",

    "LEVEL_TOOL",

    "LEVEL_CONCEPT",

    # Models
    "TaxonomyNode",

    "SkillDefinition",

    "RoleDefinition",

    # Data
    "INDUSTRIES",

    "DOMAINS",

    "JOB_FAMILIES",

    "ROLES",

    "SKILLS",

    # Engine
    "IndustryTaxonomy",

    "taxonomy",

    # Utilities
    "clean_text",

    "normalize_text",

    "normalize_key",

    "slugify",

    "deduplicate",

    # Skill intelligence
    "get_skill_definition",

    "get_skill_aliases",

    "get_parent_skills",

    "get_related_skills",

    "get_skill_tools",

    "get_skill_concepts",

    "get_skill_category",

    # Role intelligence
    "get_role_definition",

    "get_role_skills",

    "get_role_core_skills",

    "get_role_supporting_skills",

    "get_role_tools",

    "get_role_concepts",

    "get_role_industries",

    # Discovery
    "find_roles_for_skill",

    "find_industry_skills",

    "search_taxonomy",

    "classify_skill",

    "role_intelligence",

    "taxonomy_tree",

    # Serialization
    "taxonomy_to_dict",

    "taxonomy_to_json",

    "save_taxonomy",

    "taxonomy_statistics",

    "TAXONOMY_CAPABILITIES",

]


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    print(
        "============================================"
    )

    print(
        "INDUSTRY TAXONOMY TEST"
    )

    print(
        "============================================"
    )

    print(
        "\nStatistics:"
    )

    print(
        json.dumps(
            taxonomy_statistics(),
            indent=2,
        )
    )

    print(
        "\nSkill Classification:"
    )

    print(

        json.dumps(

            classify_skill(
                "RAG"
            ),

            indent=2,

        )

    )

    print(
        "\nGenerative AI Engineer:"
    )

    print(

        json.dumps(

            role_intelligence(
                "Generative AI Engineer"
            ),

            indent=2,

        )

    )

    print(
        "\nSearch: machine learning"
    )

    print(

        json.dumps(

            search_taxonomy(
                "machine learning"
            ),

            indent=2,

        )

    )

    print(
        "\nIndustry Skills: Manufacturing"
    )

    print(

        find_industry_skills(
            "Manufacturing"
        )

    )

    print(
        "\n============================================"
    )


# ============================================================
# END OF industry/taxonomy.py
# ============================================================
