# ============================================================
# curriculum/models.py
# CHUNK 1/5
#
# AI CURRICULUM INTELLIGENCE PLATFORM
#
# Purpose:
#   Central Pydantic data models used across the application.
#
# Used by:
#   - curriculum/extractor.py
#   - curriculum/comparator.py
#   - curriculum/concept_intelligence.py
#   - curriculum/skill_extractor.py
#   - industry/jd_parser.py
#   - industry/skill_matcher.py
#   - agents/gap_agent.py
#   - agents/enhancement_agent.py
#   - pages/*.py
#
# Pydantic Version:
#   Compatible with Pydantic v2
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

from __future__ import annotations


from enum import Enum


from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)


from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# ============================================================
# 2. BASE MODEL
# ============================================================

class CurriculumBaseModel(
    BaseModel
):
    """
    Base model shared by all curriculum models.

    Configuration:
        - Ignore unknown fields instead of failing.
        - Allow validation from ORM-like objects.
        - Validate assignments after object creation.
    """

    model_config = ConfigDict(

        extra="ignore",

        from_attributes=True,

        validate_assignment=True,

    )


# ============================================================
# 3. ENUMS
# ============================================================

class DifficultyLevel(
    str,
    Enum,
):
    """
    Difficulty classification.
    """

    BEGINNER = "Beginner"

    INTERMEDIATE = "Intermediate"

    ADVANCED = "Advanced"

    EXPERT = "Expert"


class LearningType(
    str,
    Enum,
):
    """
    Type of learning activity.
    """

    THEORY = "Theory"

    PRACTICAL = "Practical"

    LAB = "Lab"

    PROJECT = "Project"

    CASE_STUDY = "Case Study"

    RESEARCH = "Research"

    DISCUSSION = "Discussion"

    ASSESSMENT = "Assessment"


class SkillCategory(
    str,
    Enum,
):
    """
    Standard skill categories.
    """

    PROGRAMMING = "Programming"

    DATA = "Data"

    MACHINE_LEARNING = "Machine Learning"

    DEEP_LEARNING = "Deep Learning"

    GENERATIVE_AI = "Generative AI"

    AGENTIC_AI = "Agentic AI"

    CLOUD = "Cloud"

    DEVOPS = "DevOps"

    MLOPS = "MLOps"

    DATABASE = "Database"

    WEB = "Web"

    SECURITY = "Cybersecurity"

    DOMAIN = "Domain"

    BUSINESS = "Business"

    SOFT_SKILL = "Soft Skill"

    TOOL = "Tool"

    OTHER = "Other"


class ConceptType(
    str,
    Enum,
):
    """
    Classification of a curriculum concept.
    """

    FUNDAMENTAL = "Fundamental"

    CORE = "Core"

    ADVANCED = "Advanced"

    EMERGING = "Emerging"

    INDUSTRY = "Industry"

    PRACTICAL = "Practical"

    PREREQUISITE = "Prerequisite"

    RELATED = "Related"


class MatchType(
    str,
    Enum,
):
    """
    Semantic comparison result.
    """

    EXACT = "Exact"

    STRONG = "Strong"

    PARTIAL = "Partial"

    WEAK = "Weak"

    MISSING = "Missing"

    ADDITIONAL = "Additional"

    NOT_APPLICABLE = "Not Applicable"


class GapSeverity(
    str,
    Enum,
):
    """
    Curriculum gap severity.
    """

    CRITICAL = "Critical"

    HIGH = "High"

    MEDIUM = "Medium"

    LOW = "Low"

    INFORMATIONAL = "Informational"


class PriorityLevel(
    str,
    Enum,
):
    """
    Recommendation priority.
    """

    CRITICAL = "Critical"

    HIGH = "High"

    MEDIUM = "Medium"

    LOW = "Low"


class BloomLevel(
    str,
    Enum,
):
    """
    Bloom's taxonomy levels.
    """

    REMEMBER = "Remember"

    UNDERSTAND = "Understand"

    APPLY = "Apply"

    ANALYZE = "Analyze"

    EVALUATE = "Evaluate"

    CREATE = "Create"


class OutcomeType(
    str,
    Enum,
):
    """
    Academic outcome type.
    """

    CO = "CO"

    PO = "PO"

    PSO = "PSO"


# ============================================================
# 4. COURSE METADATA
# ============================================================

class CourseMetadata(
    CurriculumBaseModel
):
    """
    Metadata extracted from the uploaded syllabus.

    Example:

        University:
            Visvesvaraya Technological University

        College:
            ABC Institute of Technology

        Subject:
            Machine Learning

        Code:
            21CSL45
    """

    university: Optional[str] = Field(

        default=None,

        description=(
            "University or academic institution."
        ),

    )


    college: Optional[str] = Field(

        default=None,

        description=(
            "College or institution offering "
            "the course."
        ),

    )


    department: Optional[str] = Field(

        default=None,

        description=(
            "Academic department."
        ),

    )


    faculty_name: Optional[str] = Field(

        default=None,

        description=(
            "Faculty or instructor name if "
            "present in the syllabus."
        ),

    )


    program: Optional[str] = Field(

        default=None,

        description=(
            "Degree or academic program."
        ),

    )


    branch: Optional[str] = Field(

        default=None,

        description=(
            "Branch or specialization."
        ),

    )


    course_name: Optional[str] = Field(

        default=None,

        description=(
            "Subject or course name."
        ),

    )


    subject_name: Optional[str] = Field(

        default=None,

        description=(
            "Subject name."
        ),

    )


    course_code: Optional[str] = Field(

        default=None,

        description=(
            "Course or subject code."
        ),

    )


    semester: Optional[str] = Field(

        default=None,

        description=(
            "Semester in which the course "
            "is offered."
        ),

    )


    academic_year: Optional[str] = Field(

        default=None,

        description=(
            "Academic year."
        ),

    )


    regulation: Optional[str] = Field(

        default=None,

        description=(
            "Academic regulation or curriculum "
            "version."
        ),

    )


    credits: Optional[float] = Field(

        default=None,

        ge=0,

        description=(
            "Course credit value."
        ),

    )


    lecture_hours: Optional[float] = Field(

        default=None,

        ge=0,

        description=(
            "Weekly or total lecture hours."
        ),

    )


    tutorial_hours: Optional[float] = Field(

        default=None,

        ge=0,

        description=(
            "Tutorial hours."
        ),

    )


    practical_hours: Optional[float] = Field(

        default=None,

        ge=0,

        description=(
            "Practical or laboratory hours."
        ),

    )


    total_hours: Optional[float] = Field(

        default=None,

        ge=0,

        description=(
            "Total course hours."
        ),

    )


    prerequisites: List[str] = Field(

        default_factory=list,

        description=(
            "Prerequisite courses, skills or "
            "knowledge."
        ),

    )


    course_type: Optional[str] = Field(

        default=None,

        description=(
            "Core, elective, open elective, lab, "
            "professional elective, etc."
        ),

    )


    source_file: Optional[str] = Field(

        default=None,

        description=(
            "Original syllabus filename."
        ),

    )


    source_type: Optional[str] = Field(

        default=None,

        description=(
            "PDF, DOCX, image, OCR, text, etc."
        ),

    )


    extraction_confidence: Optional[float] = Field(

        default=None,

        ge=0,

        le=100,

        description=(
            "Confidence score of metadata extraction."
        ),

    )


    # ========================================================
    # VALIDATORS
    # ========================================================

    @field_validator(
        "university",
        "college",
        "department",
        "faculty_name",
        "program",
        "branch",
        "course_name",
        "subject_name",
        "course_code",
        "semester",
        "academic_year",
        "regulation",
        "course_type",
        "source_file",
        "source_type",
        mode="before",
    )
    @classmethod
    def clean_strings(
        cls,
        value: Any,
    ) -> Optional[str]:
        """
        Normalize optional string fields.
        """

        if value is None:

            return None


        if isinstance(
            value,
            str,
        ):

            value = value.strip()


            if not value:

                return None


            return value


        return str(
            value
        )


# ============================================================
# END OF CHUNK 1
# ============================================================
# ============================================================
# curriculum/models.py
# CHUNK 2/5
#
# CONCEPT / SKILL / TOOL / TECHNOLOGY / PROJECT / TOPIC MODELS
# ============================================================


# ============================================================
# 5. CONCEPT MODEL
# ============================================================

class Concept(
    CurriculumBaseModel
):
    """
    Represents an academic or industry concept.

    Example:

        name:
            "Gradient Descent"

        type:
            "Core"

        importance:
            90

        industry_relevance:
            85
    """

    name: str = Field(

        ...,

        min_length=1,

        description=(
            "Name of the concept."
        ),

    )


    description: Optional[str] = Field(

        default=None,

        description=(
            "Explanation of the concept."
        ),

    )


    concept_type: ConceptType = Field(

        default=ConceptType.CORE,

        description=(
            "Classification of the concept."
        ),

    )


    importance_score: float = Field(

        default=50,

        ge=0,

        le=100,

        description=(
            "Importance of the concept "
            "within the curriculum."
        ),

    )


    industry_relevance_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Industry relevance score."
        ),

    )


    difficulty: DifficultyLevel = Field(

        default=DifficultyLevel.INTERMEDIATE,

        description=(
            "Difficulty level."
        ),

    )


    prerequisites: List[str] = Field(

        default_factory=list,

        description=(
            "Prerequisite concepts."
        ),

    )


    related_concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Related concepts."
        ),

    )


    emerging: bool = Field(

        default=False,

        description=(
            "Whether the concept is emerging."
        ),

    )


    industry_used: bool = Field(

        default=False,

        description=(
            "Whether the concept is used "
            "in industry."
        ),

    )


    source_references: List[str] = Field(

        default_factory=list,

        description=(
            "References used to validate "
            "the concept."
        ),

    )


# ============================================================
# 6. SKILL MODEL
# ============================================================

class Skill(
    CurriculumBaseModel
):
    """
    Represents a skill extracted from the curriculum.

    Example:

        Python
        SQL
        Machine Learning
        TensorFlow
        Docker
    """

    name: str = Field(

        ...,

        min_length=1,

        description=(
            "Skill name."
        ),

    )


    normalized_name: Optional[str] = Field(

        default=None,

        description=(
            "Normalized/canonical skill name."
        ),

    )


    category: SkillCategory = Field(

        default=SkillCategory.OTHER,

        description=(
            "Skill category."
        ),

    )


    description: Optional[str] = Field(

        default=None,

        description=(
            "Description of the skill."
        ),

    )


    proficiency_level: DifficultyLevel = Field(

        default=DifficultyLevel.INTERMEDIATE,

        description=(
            "Expected proficiency level."
        ),

    )


    importance_score: float = Field(

        default=50,

        ge=0,

        le=100,

        description=(
            "Importance of the skill."
        ),

    )


    industry_relevance_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Industry relevance."
        ),

    )


    years_relevance: Optional[float] = Field(

        default=None,

        ge=0,

        description=(
            "Approximate industry relevance "
            "in years, if available."
        ),

    )


    aliases: List[str] = Field(

        default_factory=list,

        description=(
            "Alternative names for the skill."
        ),

    )


    source_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Topics from which the skill "
            "was extracted."
        ),

    )


# ============================================================
# 7. TOOL MODEL
# ============================================================

class Tool(
    CurriculumBaseModel
):
    """
    Represents a software tool used in the curriculum.

    Examples:

        Git
        Docker
        Jupyter
        MLflow
        Postman
    """

    name: str = Field(

        ...,

        min_length=1,

        description=(
            "Tool name."
        ),

    )


    category: Optional[str] = Field(

        default=None,

        description=(
            "Tool category."
        ),

    )


    purpose: Optional[str] = Field(

        default=None,

        description=(
            "Purpose of the tool."
        ),

    )


    version: Optional[str] = Field(

        default=None,

        description=(
            "Tool version when specified."
        ),

    )


    industry_relevance_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Industry relevance."
        ),

    )


    recommended: bool = Field(

        default=False,

        description=(
            "Whether the tool is recommended "
            "for curriculum enhancement."
        ),

    )


# ============================================================
# 8. TECHNOLOGY MODEL
# ============================================================

class Technology(
    CurriculumBaseModel
):
    """
    Represents a technology, framework, platform,
    programming language or ecosystem.

    Examples:

        Python
        PyTorch
        AWS
        LangChain
        Kubernetes
    """

    name: str = Field(

        ...,

        min_length=1,

        description=(
            "Technology name."
        ),

    )


    category: Optional[str] = Field(

        default=None,

        description=(
            "Technology category."
        ),

    )


    description: Optional[str] = Field(

        default=None,

        description=(
            "Technology description."
        ),

    )


    current_version: Optional[str] = Field(

        default=None,

        description=(
            "Current/recommended version."
        ),

    )


    industry_relevance_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Industry relevance."
        ),

    )


    emerging: bool = Field(

        default=False,

        description=(
            "Whether this technology "
            "is emerging."
        ),

    )


    recommended: bool = Field(

        default=False,

        description=(
            "Whether it should be added "
            "to the curriculum."
        ),

    )


# ============================================================
# 9. PROJECT MODEL
# ============================================================

class Project(
    CurriculumBaseModel
):
    """
    Represents a practical or capstone project.

    Example:

        AI-Based Resume Screening System
    """

    title: str = Field(

        ...,

        min_length=1,

        description=(
            "Project title."
        ),

    )


    description: Optional[str] = Field(

        default=None,

        description=(
            "Project description."
        ),

    )


    project_type: LearningType = Field(

        default=LearningType.PROJECT,

        description=(
            "Type of project."
        ),

    )


    difficulty: DifficultyLevel = Field(

        default=DifficultyLevel.INTERMEDIATE,

        description=(
            "Project difficulty."
        ),

    )


    duration_hours: Optional[float] = Field(

        default=None,

        ge=0,

        description=(
            "Estimated project effort."
        ),

    )


    skills: List[str] = Field(

        default_factory=list,

        description=(
            "Skills developed through "
            "the project."
        ),

    )


    concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Concepts applied."
        ),

    )


    tools: List[str] = Field(

        default_factory=list,

        description=(
            "Tools used."
        ),

    )


    technologies: List[str] = Field(

        default_factory=list,

        description=(
            "Technologies used."
        ),

    )


    industry_relevance_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Industry relevance score."
        ),

    )


    portfolio_ready: bool = Field(

        default=False,

        description=(
            "Whether the project is "
            "suitable for a student portfolio."
        ),

    )


    real_world_problem: bool = Field(

        default=False,

        description=(
            "Whether it solves a real-world "
            "problem."
        ),

    )


# ============================================================
# 10. TOPIC MODEL
# ============================================================

class Topic(
    CurriculumBaseModel
):
    """
    Represents a topic within a curriculum module.

    A topic can contain:

        - Concepts
        - Skills
        - Tools
        - Technologies
        - Projects
        - Learning objectives
    """

    topic_id: Optional[str] = Field(

        default=None,

        description=(
            "Unique topic identifier."
        ),

    )


    topic_name: str = Field(

        ...,

        min_length=1,

        description=(
            "Topic name."
        ),

    )


    description: Optional[str] = Field(

        default=None,

        description=(
            "Topic description."
        ),

    )


    hours: float = Field(

        default=0,

        ge=0,

        description=(
            "Teaching hours allocated "
            "to this topic."
        ),

    )


    sequence: Optional[int] = Field(

        default=None,

        ge=1,

        description=(
            "Topic sequence inside the module."
        ),

    )


    learning_type: LearningType = Field(

        default=LearningType.THEORY,

        description=(
            "Learning activity type."
        ),

    )


    difficulty: DifficultyLevel = Field(

        default=DifficultyLevel.INTERMEDIATE,

        description=(
            "Topic difficulty."
        ),

    )


    bloom_level: BloomLevel = Field(

        default=BloomLevel.UNDERSTAND,

        description=(
            "Expected Bloom's taxonomy level."
        ),

    )


    concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Concept names covered."
        ),

    )


    skills: List[str] = Field(

        default_factory=list,

        description=(
            "Skills developed."
        ),

    )


    tools: List[str] = Field(

        default_factory=list,

        description=(
            "Tools used."
        ),

    )


    technologies: List[str] = Field(

        default_factory=list,

        description=(
            "Technologies covered."
        ),

    )


    prerequisites: List[str] = Field(

        default_factory=list,

        description=(
            "Prerequisite topics/concepts."
        ),

    )


    learning_objectives: List[str] = Field(

        default_factory=list,

        description=(
            "Learning objectives."
        ),

    )


    projects: List[str] = Field(

        default_factory=list,

        description=(
            "Projects associated with "
            "the topic."
        ),

    )


    case_studies: List[str] = Field(

        default_factory=list,

        description=(
            "Case studies associated "
            "with the topic."
        ),

    )


    references: List[str] = Field(

        default_factory=list,

        description=(
            "Books, papers, URLs or references."
        ),

    )


    industry_relevance_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Industry relevance of the topic."
        ),

    )


    importance_score: float = Field(

        default=50,

        ge=0,

        le=100,

        description=(
            "Academic importance of the topic."
        ),

    )


    current: bool = Field(

        default=True,

        description=(
            "Whether the topic is considered "
            "current/relevant."
        ),

    )


    recommended_enhancement: bool = Field(

        default=False,

        description=(
            "Whether the topic has been "
            "recommended for enhancement."
        ),

    )


# ============================================================
# 11. TOPIC VALIDATION
# ============================================================

    @field_validator(
        "topic_name",
        "topic_id",
        mode="before",
    )
    @classmethod
    def clean_topic_strings(
        cls,
        value: Any,
    ) -> Any:
        """
        Clean topic string values.
        """

        if value is None:

            return value


        if isinstance(
            value,
            str,
        ):

            value = value.strip()


            return value or None


        return str(
            value
        )


# ============================================================
# END OF CHUNK 2
# ============================================================
# ============================================================
# curriculum/models.py
# CHUNK 3/5
#
# MODULE + CO + PO + PSO + CURRICULUM MODELS
# ============================================================


# ============================================================
# 12. MODULE MODEL
# ============================================================

class Module(
    CurriculumBaseModel
):
    """
    Represents a major unit/module of a curriculum.

    Example:

        Module 1:
            Introduction to Machine Learning

        Module 2:
            Regression and Classification
    """

    module_id: Optional[str] = Field(

        default=None,

        description=(
            "Unique module/unit identifier."
        ),

    )


    module_name: str = Field(

        ...,

        min_length=1,

        description=(
            "Module/unit name."
        ),

    )


    description: Optional[str] = Field(

        default=None,

        description=(
            "Description of the module."
        ),

    )


    sequence: Optional[int] = Field(

        default=None,

        ge=1,

        description=(
            "Module sequence."
        ),

    )


    hours: float = Field(

        default=0,

        ge=0,

        description=(
            "Total teaching hours "
            "allocated to the module."
        ),

    )


    credits: Optional[float] = Field(

        default=None,

        ge=0,

        description=(
            "Module credit value."
        ),

    )


    topics: List[Topic] = Field(

        default_factory=list,

        description=(
            "Topics contained in the module."
        ),

    )


    concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Important concepts covered "
            "across the module."
        ),

    )


    skills: List[str] = Field(

        default_factory=list,

        description=(
            "Skills developed in the module."
        ),

    )


    tools: List[str] = Field(

        default_factory=list,

        description=(
            "Tools used in the module."
        ),

    )


    technologies: List[str] = Field(

        default_factory=list,

        description=(
            "Technologies covered."
        ),

    )


    projects: List[Project] = Field(

        default_factory=list,

        description=(
            "Projects associated with "
            "the module."
        ),

    )


    case_studies: List[str] = Field(

        default_factory=list,

        description=(
            "Industry or academic case studies."
        ),

    )


    learning_objectives: List[str] = Field(

        default_factory=list,

        description=(
            "Learning objectives for "
            "the module."
        ),

    )


    prerequisites: List[str] = Field(

        default_factory=list,

        description=(
            "Prerequisites for this module."
        ),

    )


    bloom_levels: List[BloomLevel] = Field(

        default_factory=list,

        description=(
            "Bloom levels represented "
            "within the module."
        ),

    )


    difficulty: DifficultyLevel = Field(

        default=DifficultyLevel.INTERMEDIATE,

        description=(
            "Overall module difficulty."
        ),

    )


    industry_relevance_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Industry relevance score."
        ),

    )


    academic_relevance_score: float = Field(

        default=50,

        ge=0,

        le=100,

        description=(
            "Academic relevance score."
        ),

    )


    currency_score: float = Field(

        default=50,

        ge=0,

        le=100,

        description=(
            "How current the module content is."
        ),

    )


    recommended: bool = Field(

        default=False,

        description=(
            "Whether the module has been "
            "recommended for modification."
        ),

    )


    enhancement_notes: List[str] = Field(

        default_factory=list,

        description=(
            "Recommended module enhancements."
        ),

    )


    co_mapping: List[str] = Field(

        default_factory=list,

        description=(
            "Course Outcomes mapped to this module."
        ),

    )


    # ========================================================
    # MODULE VALIDATORS
    # ========================================================

    @field_validator(
        "module_name",
        "module_id",
        mode="before",
    )
    @classmethod
    def clean_module_strings(
        cls,
        value: Any,
    ) -> Any:
        """
        Normalize module identifiers and names.
        """

        if value is None:

            return value


        if isinstance(
            value,
            str,
        ):

            value = value.strip()

            return value or None


        return str(
            value
        )


# ============================================================
# 13. COURSE OBJECTIVE MODEL
# ============================================================

class CourseObjective(
    CurriculumBaseModel
):
    """
    Represents a course objective.

    Example:

        COJ1:
        Understand fundamental concepts of ML.

        COJ2:
        Apply ML algorithms to real-world datasets.
    """

    code: Optional[str] = Field(

        default=None,

        description=(
            "Objective identifier."
        ),

    )


    description: str = Field(

        ...,

        min_length=1,

        description=(
            "Course objective description."
        ),

    )


    bloom_level: Optional[BloomLevel] = Field(

        default=None,

        description=(
            "Bloom level associated with "
            "the objective."
        ),

    )


# ============================================================
# 14. COURSE OUTCOME MODEL
# ============================================================

class CourseOutcome(
    CurriculumBaseModel
):
    """
    Represents a Course Outcome (CO).

    Example:

        CO1:
        Explain fundamental machine learning concepts.

        CO2:
        Apply supervised learning algorithms.

        CO3:
        Evaluate ML models using appropriate metrics.
    """

    code: str = Field(

        ...,

        min_length=1,

        description=(
            "Outcome code, e.g. CO1."
        ),

    )


    description: str = Field(

        ...,

        min_length=1,

        description=(
            "Course outcome statement."
        ),

    )


    bloom_level: BloomLevel = Field(

        default=BloomLevel.UNDERSTAND,

        description=(
            "Bloom's taxonomy level."
        ),

    )


    knowledge_area: Optional[str] = Field(

        default=None,

        description=(
            "Knowledge area associated "
            "with the outcome."
        ),

    )


    mapped_modules: List[str] = Field(

        default_factory=list,

        description=(
            "Modules contributing to this CO."
        ),

    )


    mapped_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Topics contributing to this CO."
        ),

    )


    assessment_methods: List[str] = Field(

        default_factory=list,

        description=(
            "Assessment methods used to "
            "measure this CO."
        ),

    )


# ============================================================
# 15. PROGRAM OUTCOME MODEL
# ============================================================

class ProgramOutcome(
    CurriculumBaseModel
):
    """
    Represents an NBA-style Program Outcome.

    Example:

        PO1:
        Engineering knowledge.

        PO2:
        Problem analysis.

        PO3:
        Design/development of solutions.
    """

    code: str = Field(

        ...,

        min_length=1,

        description=(
            "PO identifier."
        ),

    )


    description: str = Field(

        ...,

        min_length=1,

        description=(
            "Program outcome description."
        ),

    )


    category: Optional[str] = Field(

        default=None,

        description=(
            "PO category."
        ),

    )


# ============================================================
# 16. PROGRAM SPECIFIC OUTCOME MODEL
# ============================================================

class ProgramSpecificOutcome(
    CurriculumBaseModel
):
    """
    Represents a Program Specific Outcome (PSO).
    """

    code: str = Field(

        ...,

        min_length=1,

        description=(
            "PSO identifier."
        ),

    )


    description: str = Field(

        ...,

        min_length=1,

        description=(
            "Program-specific outcome."
        ),

    )


    category: Optional[str] = Field(

        default=None,

        description=(
            "PSO category."
        ),

    )


# ============================================================
# 17. CO-PO MAPPING MODEL
# ============================================================

class COPOMapping(
    CurriculumBaseModel
):
    """
    CO-PO mapping.

    Typical NBA scale:

        0 = No correlation
        1 = Low
        2 = Medium
        3 = High
    """

    co_code: str = Field(

        ...,

        min_length=1,

        description=(
            "Course Outcome code."
        ),

    )


    po_code: str = Field(

        ...,

        min_length=1,

        description=(
            "Program Outcome code."
        ),

    )


    correlation: int = Field(

        default=0,

        ge=0,

        le=3,

        description=(
            "Correlation strength: 0-3."
        ),

    )


    justification: Optional[str] = Field(

        default=None,

        description=(
            "Reason for the mapping."
        ),

    )


# ============================================================
# 18. CO-PSO MAPPING MODEL
# ============================================================

class COPSOmapping(
    CurriculumBaseModel
):
    """
    CO-PSO mapping.
    """

    co_code: str = Field(

        ...,

        min_length=1,

        description=(
            "Course Outcome code."
        ),

    )


    pso_code: str = Field(

        ...,

        min_length=1,

        description=(
            "Program Specific Outcome code."
        ),

    )


    correlation: int = Field(

        default=0,

        ge=0,

        le=3,

        description=(
            "Correlation strength: 0-3."
        ),

    )


    justification: Optional[str] = Field(

        default=None,

        description=(
            "Reason for the mapping."
        ),

    )


# ============================================================
# 19. CURRICULUM MODEL
# ============================================================

class Curriculum(
    CurriculumBaseModel
):
    """
    Complete structured curriculum.

    This is the central object passed between:

        Document Extraction
              ↓
        Curriculum Intelligence
              ↓
        Industry Intelligence
              ↓
        Gap Analysis
              ↓
        Enhancement
              ↓
        Reports
    """

    curriculum_id: Optional[str] = Field(

        default=None,

        description=(
            "Unique curriculum identifier."
        ),

    )


    version: Optional[str] = Field(

        default=None,

        description=(
            "Curriculum version."
        ),

    )


    metadata: CourseMetadata = Field(

        default_factory=CourseMetadata,

        description=(
            "Course and institution metadata."
        ),

    )


    title: Optional[str] = Field(

        default=None,

        description=(
            "Curriculum title."
        ),

    )


    description: Optional[str] = Field(

        default=None,

        description=(
            "Overall curriculum description."
        ),

    )


    objectives: List[CourseObjective] = Field(

        default_factory=list,

        description=(
            "Course objectives."
        ),

    )


    prerequisites: List[str] = Field(

        default_factory=list,

        description=(
            "Overall course prerequisites."
        ),

    )


    modules: List[Module] = Field(

        default_factory=list,

        description=(
            "Curriculum modules."
        ),

    )


    concepts: List[Concept] = Field(

        default_factory=list,

        description=(
            "Global concepts extracted "
            "from the curriculum."
        ),

    )


    skills: List[Skill] = Field(

        default_factory=list,

        description=(
            "Global skills extracted "
            "from the curriculum."
        ),

    )


    tools: List[Tool] = Field(

        default_factory=list,

        description=(
            "Global tools used."
        ),

    )


    technologies: List[Technology] = Field(

        default_factory=list,

        description=(
            "Global technologies used."
        ),

    )


    projects: List[Project] = Field(

        default_factory=list,

        description=(
            "Global curriculum projects."
        ),

    )


    course_outcomes: List[CourseOutcome] = Field(

        default_factory=list,

        description=(
            "Course Outcomes."
        ),

    )


    program_outcomes: List[ProgramOutcome] = Field(

        default_factory=list,

        description=(
            "Program Outcomes."
        ),

    )


    program_specific_outcomes: List[
        ProgramSpecificOutcome
    ] = Field(

        default_factory=list,

        description=(
            "Program Specific Outcomes."
        ),

    )


    co_po_mappings: List[COPOMapping] = Field(

        default_factory=list,

        description=(
            "CO-PO mapping matrix."
        ),

    )


    co_pso_mappings: List[COPSOmapping] = Field(

        default_factory=list,

        description=(
            "CO-PSO mapping matrix."
        ),

    )


    total_hours: float = Field(

        default=0,

        ge=0,

        description=(
            "Total curriculum hours."
        ),

    )


    total_credits: float = Field(

        default=0,

        ge=0,

        description=(
            "Total curriculum credits."
        ),

    )


    extraction_confidence: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Overall extraction confidence."
        ),

    )


    source_documents: List[str] = Field(

        default_factory=list,

        description=(
            "Source documents used to construct "
            "the curriculum."
        ),

    )


    notes: List[str] = Field(

        default_factory=list,

        description=(
            "Additional curriculum notes."
        ),

    )


    # ========================================================
    # CURRICULUM HELPERS
    # ========================================================

    def get_module(
        self,
        module_id: str,
    ) -> Optional[Module]:
        """
        Find a module by module ID.
        """

        for module in self.modules:

            if module.module_id == module_id:

                return module


        return None


    def get_topic(
        self,
        topic_id: str,
    ) -> Optional[Topic]:
        """
        Find a topic by topic ID.
        """

        for module in self.modules:

            for topic in module.topics:

                if topic.topic_id == topic_id:

                    return topic


        return None


    def all_topic_names(
        self,
    ) -> List[str]:
        """
        Return all topic names.
        """

        result = []


        for module in self.modules:

            for topic in module.topics:

                result.append(
                    topic.topic_name
                )


        return result


    def all_module_names(
        self,
    ) -> List[str]:
        """
        Return all module names.
        """

        return [

            module.module_name

            for module in self.modules

        ]


    def all_skills(
        self,
    ) -> List[str]:
        """
        Return unique curriculum skills
        from both global and module level.
        """

        skills = set()


        for skill in self.skills:

            skills.add(
                skill.name
            )


        for module in self.modules:

            for skill in module.skills:

                skills.add(
                    skill
                )


            for topic in module.topics:

                for skill in topic.skills:

                    skills.add(
                        skill
                    )


        return sorted(
            skills
        )


    def all_tools(
        self,
    ) -> List[str]:
        """
        Return unique tools.
        """

        tools = set()


        for tool in self.tools:

            tools.add(
                tool.name
            )


        for module in self.modules:

            tools.update(
                module.tools
            )


            for topic in module.topics:

                tools.update(
                    topic.tools
                )


        return sorted(
            tools
        )


    def all_technologies(
        self,
    ) -> List[str]:
        """
        Return unique technologies.
        """

        technologies = set()


        for technology in self.technologies:

            technologies.add(
                technology.name
            )


        for module in self.modules:

            technologies.update(
                module.technologies
            )


            for topic in module.topics:

                technologies.update(
                    topic.technologies
                )


        return sorted(
            technologies
        )


# ============================================================
# 20. CURRICULUM VALIDATION
# ============================================================

    @field_validator(
        "title",
        "description",
        "curriculum_id",
        "version",
        mode="before",
    )
    @classmethod
    def clean_curriculum_strings(
        cls,
        value: Any,
    ) -> Any:
        """
        Normalize curriculum strings.
        """

        if value is None:

            return value


        if isinstance(
            value,
            str,
        ):

            value = value.strip()

            return value or None


        return str(
            value
        )


# ============================================================
# END OF CHUNK 3
# ============================================================
# ============================================================
# curriculum/models.py
# CHUNK 4/5
#
# CURRICULUM INTELLIGENCE / GAP / ENHANCEMENT MODELS
# ============================================================


# ============================================================
# 21. CONCEPT COMPARISON MODEL
# ============================================================

class ConceptComparison(
    CurriculumBaseModel
):
    """
    Comparison of a concept between two curricula.

    Example:

        Curriculum A:
            Machine Learning

        Curriculum B:
            Machine Learning

        Result:
            Strong Match
    """

    source_concept: str = Field(

        ...,

        min_length=1,

        description=(
            "Concept from source curriculum."
        ),

    )


    target_concept: Optional[str] = Field(

        default=None,

        description=(
            "Corresponding concept from target curriculum."
        ),

    )


    match_type: MatchType = Field(

        default=MatchType.NOT_APPLICABLE,

        description=(
            "Semantic match classification."
        ),

    )


    similarity_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Semantic similarity percentage."
        ),

    )


    explanation: Optional[str] = Field(

        default=None,

        description=(
            "Explanation of why the concepts match "
            "or differ."
        ),

    )


    source: Optional[str] = Field(

        default=None,

        description=(
            "Source of comparison evidence."
        ),

    )


# ============================================================
# 22. TOPIC COMPARISON MODEL
# ============================================================

class TopicComparison(
    CurriculumBaseModel
):
    """
    Module/topic level comparison.

    Used by Curriculum Intelligence.
    """

    source_topic: str = Field(

        ...,

        min_length=1,

        description=(
            "Topic from source curriculum."
        ),

    )


    target_topic: Optional[str] = Field(

        default=None,

        description=(
            "Matching topic from target curriculum."
        ),

    )


    source_module: Optional[str] = Field(

        default=None,

        description=(
            "Source module."
        ),

    )


    target_module: Optional[str] = Field(

        default=None,

        description=(
            "Target module."
        ),

    )


    match_type: MatchType = Field(

        default=MatchType.NOT_APPLICABLE,

        description=(
            "Match classification."
        ),

    )


    similarity_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Topic semantic similarity."
        ),

    )


    source_hours: float = Field(

        default=0,

        ge=0,

        description=(
            "Hours assigned in source curriculum."
        ),

    )


    target_hours: float = Field(

        default=0,

        ge=0,

        description=(
            "Hours assigned in target curriculum."
        ),

    )


    hours_difference: float = Field(

        default=0,

        description=(
            "Difference between source and target hours."
        ),

    )


    source_concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Concepts in source topic."
        ),

    )


    target_concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Concepts in target topic."
        ),

    )


    missing_concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Concepts missing from source."
        ),

    )


    additional_concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Additional concepts in source."
        ),

    )


    explanation: Optional[str] = Field(

        default=None,

        description=(
            "LLM/semantic explanation."
        ),

    )


# ============================================================
# 23. MODULE COMPARISON MODEL
# ============================================================

class ModuleComparison(
    CurriculumBaseModel
):
    """
    Complete module-level curriculum comparison.
    """

    source_module_id: Optional[str] = Field(

        default=None,

        description=(
            "Source module identifier."
        ),

    )


    source_module_name: str = Field(

        ...,

        min_length=1,

        description=(
            "Source module name."
        ),

    )


    target_module_id: Optional[str] = Field(

        default=None,

        description=(
            "Target module identifier."
        ),

    )


    target_module_name: Optional[str] = Field(

        default=None,

        description=(
            "Target module name."
        ),

    )


    match_type: MatchType = Field(

        default=MatchType.NOT_APPLICABLE,

        description=(
            "Module match classification."
        ),

    )


    similarity_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Module similarity percentage."
        ),

    )


    source_hours: float = Field(

        default=0,

        ge=0,

        description=(
            "Source module hours."
        ),

    )


    target_hours: float = Field(

        default=0,

        ge=0,

        description=(
            "Target module hours."
        ),

    )


    topic_comparisons: List[
        TopicComparison
    ] = Field(

        default_factory=list,

        description=(
            "Topic-level comparisons."
        ),

    )


    matched_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Matched topics."
        ),

    )


    partial_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Partially matched topics."
        ),

    )


    missing_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Missing topics."
        ),

    )


    additional_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Additional topics."
        ),

    )


    missing_skills: List[str] = Field(

        default_factory=list,

        description=(
            "Missing skills."
        ),

    )


    missing_tools: List[str] = Field(

        default_factory=list,

        description=(
            "Missing tools."
        ),

    )


    missing_technologies: List[str] = Field(

        default_factory=list,

        description=(
            "Missing technologies."
        ),

    )


    recommendations: List[str] = Field(

        default_factory=list,

        description=(
            "Module-level recommendations."
        ),

    )


# ============================================================
# 24. CURRICULUM COMPARISON MODEL
# ============================================================

class CurriculumComparison(
    CurriculumBaseModel
):
    """
    Complete comparison between two curricula.
    """

    source_curriculum: Optional[str] = Field(

        default=None,

        description=(
            "Name of source curriculum."
        ),

    )


    target_curriculum: Optional[str] = Field(

        default=None,

        description=(
            "Name of target curriculum."
        ),

    )


    overall_similarity_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Overall semantic similarity."
        ),

    )


    module_similarity_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Module-level similarity."
        ),

    )


    topic_similarity_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Topic-level similarity."
        ),

    )


    concept_similarity_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Concept-level similarity."
        ),

    )


    skill_similarity_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Skill-level similarity."
        ),

    )


    module_comparisons: List[
        ModuleComparison
    ] = Field(

        default_factory=list,

        description=(
            "Module-level comparison results."
        ),

    )


    matched_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Overall matched topics."
        ),

    )


    partial_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Overall partial matches."
        ),

    )


    missing_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Topics missing from source curriculum."
        ),

    )


    additional_topics: List[str] = Field(

        default_factory=list,

        description=(
            "Topics additional to source curriculum."
        ),

    )


    missing_concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Missing concepts."
        ),

    )


    additional_concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Additional concepts."
        ),

    )


    missing_skills: List[str] = Field(

        default_factory=list,

        description=(
            "Missing skills."
        ),

    )


    additional_skills: List[str] = Field(

        default_factory=list,

        description=(
            "Additional skills."
        ),

    )


    recommendations: List[str] = Field(

        default_factory=list,

        description=(
            "Overall comparison recommendations."
        ),

    )


    methodology: List[str] = Field(

        default_factory=list,

        description=(
            "Methods used for comparison."
        ),

    )


# ============================================================
# 25. SKILL MATCH MODEL
# ============================================================

class SkillMatch(
    CurriculumBaseModel
):
    """
    Matches curriculum skills against industry/JD skills.
    """

    curriculum_skill: str = Field(

        ...,

        min_length=1,

        description=(
            "Skill found in curriculum."
        ),

    )


    jd_skill: Optional[str] = Field(

        default=None,

        description=(
            "Corresponding skill in job description."
        ),

    )


    normalized_skill: Optional[str] = Field(

        default=None,

        description=(
            "Canonical skill name."
        ),

    )


    match_type: MatchType = Field(

        default=MatchType.MISSING,

        description=(
            "Skill match classification."
        ),

    )


    similarity_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Semantic similarity score."
        ),

    )


    importance_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Importance of the skill to industry/JD."
        ),

    )


    industry_demand_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Estimated industry demand."
        ),

    )


    evidence: List[str] = Field(

        default_factory=list,

        description=(
            "Evidence supporting the match."
        ),

    )


    recommendation: Optional[str] = Field(

        default=None,

        description=(
            "Recommendation based on skill matching."
        ),

    )


# ============================================================
# 26. INDUSTRY ALIGNMENT MODEL
# ============================================================

class IndustryAlignment(
    CurriculumBaseModel
):
    """
    Overall curriculum-to-industry alignment.
    """

    overall_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Overall industry alignment."
        ),

    )


    skill_coverage: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "JD skill coverage percentage."
        ),

    )


    technology_coverage: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Technology coverage."
        ),

    )


    tool_coverage: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Tool coverage."
        ),

    )


    project_alignment: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Project-to-industry alignment."
        ),

    )


    concept_alignment: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Concept-to-industry alignment."
        ),

    )


    covered_skills: List[str] = Field(

        default_factory=list,

        description=(
            "Skills covered by curriculum."
        ),

    )


    partial_skills: List[str] = Field(

        default_factory=list,

        description=(
            "Partially covered skills."
        ),

    )


    missing_skills: List[str] = Field(

        default_factory=list,

        description=(
            "Missing industry skills."
        ),

    )


    missing_tools: List[str] = Field(

        default_factory=list,

        description=(
            "Missing tools."
        ),

    )


    missing_technologies: List[str] = Field(

        default_factory=list,

        description=(
            "Missing technologies."
        ),

    )


    recommended_projects: List[str] = Field(

        default_factory=list,

        description=(
            "Recommended industry projects."
        ),

    )


# ============================================================
# 27. CURRICULUM GAP MODEL
# ============================================================

class CurriculumGap(
    CurriculumBaseModel
):
    """
    Represents a curriculum gap identified through
    curriculum comparison, industry analysis,
    RAG research or expert analysis.
    """

    gap_id: Optional[str] = Field(

        default=None,

        description=(
            "Unique gap identifier."
        ),

    )


    category: str = Field(

        ...,

        min_length=1,

        description=(
            "Gap category."
        ),

    )


    title: str = Field(

        ...,

        min_length=1,

        description=(
            "Short gap title."
        ),

    )


    description: str = Field(

        ...,

        min_length=1,

        description=(
            "Detailed gap description."
        ),

    )


    severity: GapSeverity = Field(

        default=GapSeverity.MEDIUM,

        description=(
            "Gap severity."
        ),

    )


    priority: PriorityLevel = Field(

        default=PriorityLevel.MEDIUM,

        description=(
            "Implementation priority."
        ),

    )


    module_id: Optional[str] = Field(

        default=None,

        description=(
            "Affected module."
        ),

    )


    module_name: Optional[str] = Field(

        default=None,

        description=(
            "Affected module name."
        ),

    )


    topic: Optional[str] = Field(

        default=None,

        description=(
            "Affected topic."
        ),

    )


    missing_concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Missing concepts."
        ),

    )


    missing_skills: List[str] = Field(

        default_factory=list,

        description=(
            "Missing skills."
        ),

    )


    missing_tools: List[str] = Field(

        default_factory=list,

        description=(
            "Missing tools."
        ),

    )


    missing_technologies: List[str] = Field(

        default_factory=list,

        description=(
            "Missing technologies."
        ),

    )


    industry_evidence: List[str] = Field(

        default_factory=list,

        description=(
            "Industry evidence."
        ),

    )


    academic_evidence: List[str] = Field(

        default_factory=list,

        description=(
            "Academic evidence."
        ),

    )


    jd_evidence: List[str] = Field(

        default_factory=list,

        description=(
            "Job description evidence."
        ),

    )


    gap_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Quantitative gap score."
        ),

    )


    confidence_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Confidence in the gap."
        ),

    )


    recommended_action: Optional[str] = Field(

        default=None,

        description=(
            "Recommended action."
        ),

    )


# ============================================================
# 28. ENHANCEMENT RECOMMENDATION MODEL
# ============================================================

class EnhancementRecommendation(
    CurriculumBaseModel
):
    """
    Proposed curriculum enhancement.

    Example:

        Add:
            LangChain + LangGraph

        Module:
            Generative AI

        Reason:
            Increasing industry demand.
    """

    enhancement_id: Optional[str] = Field(

        default=None,

        description=(
            "Unique enhancement identifier."
        ),

    )


    category: str = Field(

        ...,

        min_length=1,

        description=(
            "Enhancement category."
        ),

    )


    title: str = Field(

        ...,

        min_length=1,

        description=(
            "Enhancement title."
        ),

    )


    description: str = Field(

        ...,

        min_length=1,

        description=(
            "Detailed recommendation."
        ),

    )


    priority: PriorityLevel = Field(

        default=PriorityLevel.MEDIUM,

        description=(
            "Recommendation priority."
        ),

    )


    module_id: Optional[str] = Field(

        default=None,

        description=(
            "Module to which enhancement "
            "should be added."
        ),

    )


    module_name: Optional[str] = Field(

        default=None,

        description=(
            "Module name."
        ),

    )


    target_topic: Optional[str] = Field(

        default=None,

        description=(
            "Topic that should be enhanced."
        ),

    )


    concepts_to_add: List[str] = Field(

        default_factory=list,

        description=(
            "Concepts to add."
        ),

    )


    skills_to_add: List[str] = Field(

        default_factory=list,

        description=(
            "Skills to add."
        ),

    )


    tools_to_add: List[str] = Field(

        default_factory=list,

        description=(
            "Tools to add."
        ),

    )


    technologies_to_add: List[str] = Field(

        default_factory=list,

        description=(
            "Technologies to add."
        ),

    )


    projects_to_add: List[str] = Field(

        default_factory=list,

        description=(
            "Projects to add."
        ),

    )


    hours_to_add: float = Field(

        default=0,

        ge=0,

        description=(
            "Recommended additional hours."
        ),

    )


    rationale: Optional[str] = Field(

        default=None,

        description=(
            "Reason for recommendation."
        ),

    )


    industry_evidence: List[str] = Field(

        default_factory=list,

        description=(
            "Industry evidence."
        ),

    )


    jd_evidence: List[str] = Field(

        default_factory=list,

        description=(
            "JD evidence."
        ),

    )


    academic_evidence: List[str] = Field(

        default_factory=list,

        description=(
            "Academic evidence."
        ),

    )


    expected_outcome: Optional[str] = Field(

        default=None,

        description=(
            "Expected learning or industry outcome."
        ),

    )


    implementation_effort: DifficultyLevel = Field(

        default=DifficultyLevel.INTERMEDIATE,

        description=(
            "Estimated implementation effort."
        ),

    )


# ============================================================
# 29. ENHANCEMENT TRACEABILITY MODEL
# ============================================================

class EnhancementTraceability(
    CurriculumBaseModel
):
    """
    Tracks the reason an enhancement was recommended.

    This creates:

        JD
         ↓
        Gap
         ↓
        Enhancement
         ↓
        Final Module
         ↓
        CO
    """

    enhancement_id: str = Field(

        ...,

        min_length=1,

        description=(
            "Enhancement identifier."
        ),

    )


    source_gaps: List[str] = Field(

        default_factory=list,

        description=(
            "Gap IDs responsible for "
            "the enhancement."
        ),

    )


    source_jd_skills: List[str] = Field(

        default_factory=list,

        description=(
            "JD skills responsible for "
            "the enhancement."
        ),

    )


    source_concepts: List[str] = Field(

        default_factory=list,

        description=(
            "Concept intelligence sources."
        ),

    )


    source_research: List[str] = Field(

        default_factory=list,

        description=(
            "Research references."
        ),

    )


    target_module: Optional[str] = Field(

        default=None,

        description=(
            "Final target module."
        ),

    )


    target_topic: Optional[str] = Field(

        default=None,

        description=(
            "Final target topic."
        ),

    )


    mapped_cos: List[str] = Field(

        default_factory=list,

        description=(
            "Course Outcomes affected."
        ),

    )


    implementation_status: str = Field(

        default="Proposed",

        description=(
            "Proposed, Accepted, Rejected, Implemented."
        ),

    )


# ============================================================
# 30. EXPERT RECOMMENDATION MODEL
# ============================================================

class ExpertRecommendation(
    CurriculumBaseModel
):
    """
    Final recommendation produced after combining:

        - Curriculum analysis
        - Industry analysis
        - JD analysis
        - RAG evidence
        - LLM reasoning
        - Critic agent
    """

    recommendation_id: Optional[str] = Field(

        default=None,

        description=(
            "Unique recommendation identifier."
        ),

    )


    title: str = Field(

        ...,

        min_length=1,

        description=(
            "Recommendation title."
        ),

    )


    recommendation: str = Field(

        ...,

        min_length=1,

        description=(
            "Final recommendation."
        ),

    )


    priority: PriorityLevel = Field(

        default=PriorityLevel.MEDIUM,

        description=(
            "Recommendation priority."
        ),

    )


    confidence_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Confidence score."
        ),

    )


    supporting_evidence: List[str] = Field(

        default_factory=list,

        description=(
            "Supporting evidence."
        ),

    )


    risks: List[str] = Field(

        default_factory=list,

        description=(
            "Risks or limitations."
        ),

    )


    expected_impact: Optional[str] = Field(

        default=None,

        description=(
            "Expected curriculum impact."
        ),

    )


    implementation_notes: List[str] = Field(

        default_factory=list,

        description=(
            "Implementation guidance."
        ),

    )


# ============================================================
# 31. AGENT DECISION MODEL
# ============================================================

class AgentDecision(
    CurriculumBaseModel
):
    """
    Stores the output of an AI agent.

    Used for:

        Gap Agent
        Expert Agent
        Critic Agent
        Enhancement Agent
    """

    agent_name: str = Field(

        ...,

        min_length=1,

        description=(
            "Agent name."
        ),

    )


    decision: str = Field(

        ...,

        min_length=1,

        description=(
            "Agent decision."
        ),

    )


    reasoning: Optional[str] = Field(

        default=None,

        description=(
            "Reasoning summary."
        ),

    )


    confidence_score: float = Field(

        default=0,

        ge=0,

        le=100,

        description=(
            "Agent confidence."
        ),

    )


    recommendations: List[str] = Field(

        default_factory=list,

        description=(
            "Agent recommendations."
        ),

    )


    evidence: List[str] = Field(

        default_factory=list,

        description=(
            "Evidence used by agent."
        ),

    )


    concerns: List[str] = Field(

        default_factory=list,

        description=(
            "Critic concerns."
        ),

    )


# ============================================================
# 32. END OF CHUNK 4
# ============================================================
# ============================================================
# curriculum/models.py
# CHUNK 5/5
#
# REPORT / VALIDATION / ANALYTICS / SERIALIZATION
# ============================================================


# ============================================================
# 33. CURRICULUM STATISTICS MODEL
# ============================================================

class CurriculumStatistics(
    CurriculumBaseModel
):
    """
    Aggregated statistics for a curriculum.

    Used by:
        - Reports page
        - Executive dashboard
        - Curriculum comparison
        - Gap analysis
    """

    module_count: int = Field(
        default=0,
        ge=0,
    )

    topic_count: int = Field(
        default=0,
        ge=0,
    )

    concept_count: int = Field(
        default=0,
        ge=0,
    )

    skill_count: int = Field(
        default=0,
        ge=0,
    )

    tool_count: int = Field(
        default=0,
        ge=0,
    )

    technology_count: int = Field(
        default=0,
        ge=0,
    )

    project_count: int = Field(
        default=0,
        ge=0,
    )

    course_outcome_count: int = Field(
        default=0,
        ge=0,
    )

    program_outcome_count: int = Field(
        default=0,
        ge=0,
    )

    pso_count: int = Field(
        default=0,
        ge=0,
    )

    total_hours: float = Field(
        default=0,
        ge=0,
    )

    total_credits: float = Field(
        default=0,
        ge=0,
    )

    practical_hours: float = Field(
        default=0,
        ge=0,
    )

    theory_hours: float = Field(
        default=0,
        ge=0,
    )

    project_hours: float = Field(
        default=0,
        ge=0,
    )

    industry_relevance_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    currency_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    industry_alignment_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    curriculum_quality_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )


# ============================================================
# 34. VALIDATION ISSUE MODEL
# ============================================================

class ValidationIssue(
    CurriculumBaseModel
):
    """
    Represents a validation issue found in
    curriculum/report data.
    """

    issue_id: Optional[str] = Field(
        default=None,
    )

    category: str = Field(
        ...,
        min_length=1,
    )

    check: str = Field(
        ...,
        min_length=1,
    )

    status: str = Field(
        ...,
        min_length=1,
    )

    severity: str = Field(
        default="Info",
    )

    message: str = Field(
        ...,
        min_length=1,
    )

    module_id: Optional[str] = Field(
        default=None,
    )

    topic_id: Optional[str] = Field(
        default=None,
    )

    recommendation: Optional[str] = Field(
        default=None,
    )


# ============================================================
# 35. VALIDATION REPORT MODEL
# ============================================================

class ValidationReport(
    CurriculumBaseModel
):
    """
    Complete validation result for the
    curriculum intelligence pipeline.
    """

    validation_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    report_completeness: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    gap_enhancement_traceability: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    enhancement_syllabus_traceability: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    pass_count: int = Field(
        default=0,
        ge=0,
    )

    warning_count: int = Field(
        default=0,
        ge=0,
    )

    fail_count: int = Field(
        default=0,
        ge=0,
    )

    status: str = Field(
        default="Draft",
    )

    approval_status: str = Field(
        default="Draft",
    )

    issues: List[ValidationIssue] = Field(
        default_factory=list,
    )

    recommendations: List[str] = Field(
        default_factory=list,
    )


# ============================================================
# 36. CURRICULUM QUALITY MODEL
# ============================================================

class CurriculumQuality(
    CurriculumBaseModel
):
    """
    Overall quality assessment.

    Combines academic and industry dimensions.
    """

    academic_quality: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    industry_alignment: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    concept_depth: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    skill_coverage: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    technology_currency: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    practical_exposure: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    project_quality: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    assessment_quality: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    outcome_alignment: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    overall_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    strengths: List[str] = Field(
        default_factory=list,
    )

    weaknesses: List[str] = Field(
        default_factory=list,
    )


# ============================================================
# 37. FINAL SYLLABUS MODEL
# ============================================================

class FinalSyllabus(
    CurriculumBaseModel
):
    """
    Final AI-enhanced syllabus.

    This is the final academic object generated
    after curriculum comparison, industry analysis,
    gap detection and enhancement.
    """

    syllabus_id: Optional[str] = Field(
        default=None,
    )

    original_curriculum_id: Optional[str] = Field(
        default=None,
    )

    version: str = Field(
        default="1.0",
    )

    title: Optional[str] = Field(
        default=None,
    )

    metadata: CourseMetadata = Field(
        default_factory=CourseMetadata,
    )

    modules: List[Module] = Field(
        default_factory=list,
    )

    objectives: List[CourseObjective] = Field(
        default_factory=list,
    )

    course_outcomes: List[CourseOutcome] = Field(
        default_factory=list,
    )

    program_outcomes: List[ProgramOutcome] = Field(
        default_factory=list,
    )

    program_specific_outcomes: List[
        ProgramSpecificOutcome
    ] = Field(
        default_factory=list,
    )

    co_po_mappings: List[COPOMapping] = Field(
        default_factory=list,
    )

    co_pso_mappings: List[COPSOmapping] = Field(
        default_factory=list,
    )

    accepted_enhancements: List[
        EnhancementRecommendation
    ] = Field(
        default_factory=list,
    )

    rejected_enhancements: List[
        EnhancementRecommendation
    ] = Field(
        default_factory=list,
    )

    statistics: CurriculumStatistics = Field(
        default_factory=CurriculumStatistics,
    )

    quality: CurriculumQuality = Field(
        default_factory=CurriculumQuality,
    )

    validation: Optional[ValidationReport] = Field(
        default=None,
    )

    approval_status: str = Field(
        default="Draft",
    )

    approved_by: Optional[str] = Field(
        default=None,
    )

    approval_notes: Optional[str] = Field(
        default=None,
    )


# ============================================================
# 38. REPORT SECTION MODEL
# ============================================================

class ReportSection(
    CurriculumBaseModel
):
    """
    Generic report section.

    Used to build:
        - Executive report
        - Comparison report
        - JD report
        - Gap report
        - Enhancement report
    """

    title: str = Field(
        ...,
        min_length=1,
    )

    description: Optional[str] = Field(
        default=None,
    )

    summary: Optional[str] = Field(
        default=None,
    )

    findings: List[str] = Field(
        default_factory=list,
    )

    recommendations: List[str] = Field(
        default_factory=list,
    )

    tables: List[
        Dict[str, Any]
    ] = Field(
        default_factory=list,
    )

    charts: List[
        Dict[str, Any]
    ] = Field(
        default_factory=list,
    )

    evidence: List[str] = Field(
        default_factory=list,
    )


# ============================================================
# 39. CURRICULUM INTELLIGENCE REPORT
# ============================================================

class CurriculumIntelligenceReport(
    CurriculumBaseModel
):
    """
    Complete curriculum intelligence report.
    """

    report_id: Optional[str] = Field(
        default=None,
    )

    report_title: str = Field(
        default="Curriculum Intelligence Report",
    )

    generated_at: Optional[str] = Field(
        default=None,
    )

    curriculum: Optional[Curriculum] = Field(
        default=None,
    )

    statistics: CurriculumStatistics = Field(
        default_factory=CurriculumStatistics,
    )

    comparison: Optional[
        CurriculumComparison
    ] = Field(
        default=None,
    )

    industry_alignment: Optional[
        IndustryAlignment
    ] = Field(
        default=None,
    )

    gaps: List[
        CurriculumGap
    ] = Field(
        default_factory=list,
    )

    enhancements: List[
        EnhancementRecommendation
    ] = Field(
        default_factory=list,
    )

    expert_recommendations: List[
        ExpertRecommendation
    ] = Field(
        default_factory=list,
    )

    quality: CurriculumQuality = Field(
        default_factory=CurriculumQuality,
    )

    validation: Optional[
        ValidationReport
    ] = Field(
        default=None,
    )

    sections: List[
        ReportSection
    ] = Field(
        default_factory=list,
    )

    executive_summary: Optional[str] = Field(
        default=None,
    )

    final_recommendation: Optional[str] = Field(
        default=None,
    )


# ============================================================
# 40. MASTER REPORT MODEL
# ============================================================

class MasterCurriculumReport(
    CurriculumBaseModel
):
    """
    Master report combining all five application stages.

    01 Extract
    02 Curriculum Intelligence
    03 Industry/JD Intelligence
    04 Gap & Enhancement
    05 Reports
    """

    report_id: Optional[str] = Field(
        default=None,
    )

    report_title: str = Field(
        default="AI Curriculum Intelligence Master Report",
    )

    metadata: CourseMetadata = Field(
        default_factory=CourseMetadata,
    )

    original_curriculum: Optional[
        Curriculum
    ] = Field(
        default=None,
    )

    curriculum_intelligence: Optional[
        CurriculumIntelligenceReport
    ] = Field(
        default=None,
    )

    industry_alignment: Optional[
        IndustryAlignment
    ] = Field(
        default=None,
    )

    gaps: List[
        CurriculumGap
    ] = Field(
        default_factory=list,
    )

    enhancements: List[
        EnhancementRecommendation
    ] = Field(
        default_factory=list,
    )

    traceability: List[
        EnhancementTraceability
    ] = Field(
        default_factory=list,
    )

    final_syllabus: Optional[
        FinalSyllabus
    ] = Field(
        default=None,
    )

    validation: Optional[
        ValidationReport
    ] = Field(
        default=None,
    )

    final_readiness_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    overall_curriculum_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    approval_status: str = Field(
        default="Draft",
    )

    system_status: str = Field(
        default="Draft",
    )

    executive_summary: Optional[str] = Field(
        default=None,
    )


# ============================================================
# 41. CURRICULUM VERSION MODEL
# ============================================================

class CurriculumVersion(
    CurriculumBaseModel
):
    """
    Tracks curriculum changes across versions.

    Example:

        v1.0 → Original syllabus
        v1.1 → Added Generative AI
        v1.2 → Added Agentic AI
        v2.0 → Complete industry-aligned syllabus
    """

    version: str = Field(
        ...,
        min_length=1,
    )

    previous_version: Optional[str] = Field(
        default=None,
    )

    change_summary: str = Field(
        default="",
    )

    added_topics: List[str] = Field(
        default_factory=list,
    )

    removed_topics: List[str] = Field(
        default_factory=list,
    )

    modified_topics: List[str] = Field(
        default_factory=list,
    )

    added_skills: List[str] = Field(
        default_factory=list,
    )

    removed_skills: List[str] = Field(
        default_factory=list,
    )

    added_tools: List[str] = Field(
        default_factory=list,
    )

    added_technologies: List[str] = Field(
        default_factory=list,
    )

    added_projects: List[str] = Field(
        default_factory=list,
    )

    enhancement_ids: List[str] = Field(
        default_factory=list,
    )

    created_at: Optional[str] = Field(
        default=None,
    )

    created_by: Optional[str] = Field(
        default=None,
    )


# ============================================================
# 42. GENERIC SERIALIZATION HELPERS
# ============================================================

def model_to_dict(
    model: CurriculumBaseModel,
) -> Dict[str, Any]:
    """
    Convert a Pydantic model into a dictionary.

    Pydantic v2:
        model.model_dump()
    """

    return model.model_dump(
        mode="json",
        exclude_none=True,
    )


def model_to_json(
    model: CurriculumBaseModel,
    indent: int = 2,
) -> str:
    """
    Convert a model into JSON.
    """

    return model.model_dump_json(
        indent=indent,
        exclude_none=True,
    )


# ============================================================
# 43. GENERIC MODEL FACTORY
# ============================================================

def model_from_dict(
    model_class: Any,
    data: Dict[str, Any],
) -> Any:
    """
    Safely construct a Pydantic model from
    dictionary data.

    Example:

        curriculum = model_from_dict(
            Curriculum,
            json_data
        )
    """

    return model_class.model_validate(
        data
    )


# ============================================================
# 44. CURRICULUM STATISTICS CALCULATOR
# ============================================================

def calculate_curriculum_statistics(
    curriculum: Curriculum,
) -> CurriculumStatistics:
    """
    Calculate high-level curriculum statistics.
    """

    topic_count = 0

    project_count = 0

    practical_hours = 0.0

    theory_hours = 0.0

    project_hours = 0.0


    for module in curriculum.modules:

        for topic in module.topics:

            topic_count += 1


            if topic.learning_type in [

                LearningType.PRACTICAL,

                LearningType.LAB,

            ]:

                practical_hours += topic.hours

            else:

                theory_hours += topic.hours


        project_count += len(
            module.projects
        )


        for project in module.projects:

            project_hours += (
                project.duration_hours or 0
            )


    industry_scores = [

        module.industry_relevance_score

        for module in curriculum.modules

        if module.industry_relevance_score > 0

    ]


    currency_scores = [

        module.currency_score

        for module in curriculum.modules

        if module.currency_score > 0

    ]


    if industry_scores:

        industry_relevance = (

            sum(industry_scores)
            /
            len(industry_scores)

        )

    else:

        industry_relevance = 0


    if currency_scores:

        currency_score = (

            sum(currency_scores)
            /
            len(currency_scores)

        )

    else:

        currency_score = 0


    statistics = CurriculumStatistics(

        module_count=len(
            curriculum.modules
        ),

        topic_count=topic_count,

        concept_count=len(
            curriculum.concepts
        ),

        skill_count=len(
            curriculum.skills
        ),

        tool_count=len(
            curriculum.tools
        ),

        technology_count=len(
            curriculum.technologies
        ),

        project_count=project_count,

        course_outcome_count=len(
            curriculum.course_outcomes
        ),

        program_outcome_count=len(
            curriculum.program_outcomes
        ),

        pso_count=len(
            curriculum.program_specific_outcomes
        ),

        total_hours=curriculum.total_hours,

        total_credits=curriculum.total_credits,

        practical_hours=practical_hours,

        theory_hours=theory_hours,

        project_hours=project_hours,

        industry_relevance_score=round(
            industry_relevance,
            2,
        ),

        currency_score=round(
            currency_score,
            2,
        ),

    )


    return statistics


# ============================================================
# 45. CURRICULUM BASIC VALIDATOR
# ============================================================

def validate_curriculum(
    curriculum: Curriculum,
) -> List[ValidationIssue]:
    """
    Perform basic structural validation.

    Returns:
        List[ValidationIssue]
    """

    issues: List[
        ValidationIssue
    ] = []


    # --------------------------------------------------------
    # Module check
    # --------------------------------------------------------

    if not curriculum.modules:

        issues.append(

            ValidationIssue(

                category="Structure",

                check="Modules",

                status="FAIL",

                severity="Critical",

                message=(
                    "Curriculum contains no modules."
                ),

                recommendation=(
                    "Extract or define at least one "
                    "curriculum module."
                ),

            )

        )


    # --------------------------------------------------------
    # Topic check
    # --------------------------------------------------------

    for module in curriculum.modules:

        if not module.topics:

            issues.append(

                ValidationIssue(

                    category="Structure",

                    check="Module Topics",

                    status="WARNING",

                    severity="High",

                    message=(
                        f"Module '{module.module_name}' "
                        "contains no topics."
                    ),

                    module_id=module.module_id,

                    recommendation=(
                        "Add or extract topics for "
                        "this module."
                    ),

                )

            )


        # ----------------------------------------------------
        # Hours check
        # ----------------------------------------------------

        if module.hours <= 0:

            issues.append(

                ValidationIssue(

                    category="Academic Structure",

                    check="Module Hours",

                    status="WARNING",

                    severity="Medium",

                    message=(
                        f"Module '{module.module_name}' "
                        "has no allocated hours."
                    ),

                    module_id=module.module_id,

                    recommendation=(
                        "Verify module teaching hours."
                    ),

                )

            )


    # --------------------------------------------------------
    # CO check
    # --------------------------------------------------------

    if not curriculum.course_outcomes:

        issues.append(

            ValidationIssue(

                category="Outcome Mapping",

                check="Course Outcomes",

                status="WARNING",

                severity="High",

                message=(
                    "No Course Outcomes are defined."
                ),

                recommendation=(
                    "Define measurable Course Outcomes."
                ),

            )

        )


    # --------------------------------------------------------
    # PO check
    # --------------------------------------------------------

    if not curriculum.program_outcomes:

        issues.append(

            ValidationIssue(

                category="Outcome Mapping",

                check="Program Outcomes",

                status="WARNING",

                severity="Medium",

                message=(
                    "No Program Outcomes are defined."
                ),

                recommendation=(
                    "Add relevant Program Outcomes."
                ),

            )

        )


    # --------------------------------------------------------
    # Skill check
    # --------------------------------------------------------

    if not curriculum.skills:

        issues.append(

            ValidationIssue(

                category="Industry Alignment",

                check="Skills",

                status="WARNING",

                severity="High",

                message=(
                    "No structured skills were extracted "
                    "from the curriculum."
                ),

                recommendation=(
                    "Run skill extraction using "
                    "skill_extractor.py."
                ),

            )

        )


    # --------------------------------------------------------
    # Technology check
    # --------------------------------------------------------

    if not curriculum.technologies:

        issues.append(

            ValidationIssue(

                category="Industry Alignment",

                check="Technologies",

                status="WARNING",

                severity="Medium",

                message=(
                    "No technologies were identified."
                ),

                recommendation=(
                    "Run technology extraction and "
                    "industry intelligence."
                ),

            )

        )


    return issues


# ============================================================
# 46. CALCULATE VALIDATION SCORE
# ============================================================

def calculate_validation_score(
    issues: List[ValidationIssue],
) -> float:
    """
    Calculate a simple validation score.

    PASS      = 100
    WARNING   = 50
    FAIL      = 0
    """

    if not issues:

        return 100.0


    total_weight = 0.0

    achieved_weight = 0.0


    for issue in issues:

        status = issue.status.upper()


        if status == "FAIL":

            weight = 3

            score = 0

        elif status == "WARNING":

            weight = 2

            score = 50

        else:

            weight = 1

            score = 100


        total_weight += weight

        achieved_weight += (
            weight * score
        )


    if total_weight == 0:

        return 100.0


    return round(

        achieved_weight
        /
        total_weight,

        2,

    )


# ============================================================
# 47. BUILD VALIDATION REPORT
# ============================================================

def build_validation_report(
    curriculum: Curriculum,
) -> ValidationReport:
    """
    Build a ValidationReport from a curriculum.
    """

    issues = validate_curriculum(
        curriculum
    )


    validation_score = (
        calculate_validation_score(
            issues
        )
    )


    pass_count = sum(

        1

        for issue in issues

        if issue.status.upper() == "PASS"

    )


    warning_count = sum(

        1

        for issue in issues

        if issue.status.upper() == "WARNING"

    )


    fail_count = sum(

        1

        for issue in issues

        if issue.status.upper() == "FAIL"

    )


    if fail_count > 0:

        status = "Validation Failed"

    elif validation_score >= 90:

        status = "Ready"

    elif validation_score >= 75:

        status = "Ready with Warnings"

    else:

        status = "Requires Review"


    recommendations = [

        issue.recommendation

        for issue in issues

        if issue.recommendation

    ]


    return ValidationReport(

        validation_score=validation_score,

        pass_count=pass_count,

        warning_count=warning_count,

        fail_count=fail_count,

        status=status,

        recommendations=recommendations,

        issues=issues,

    )


# ============================================================
# 48. CURRICULUM QUALITY CALCULATOR
# ============================================================

def calculate_curriculum_quality(
    curriculum: Curriculum,
    industry_alignment_score: float = 0,
) -> CurriculumQuality:
    """
    Calculate a high-level curriculum quality score.
    """

    # --------------------------------------------------------
    # Academic structure
    # --------------------------------------------------------

    academic_score = 0.0


    if curriculum.modules:

        academic_score += 20


    if curriculum.course_outcomes:

        academic_score += 20


    if curriculum.program_outcomes:

        academic_score += 15


    if curriculum.modules and all(

        module.topics

        for module in curriculum.modules

    ):

        academic_score += 25


    if curriculum.co_po_mappings:

        academic_score += 20


    # --------------------------------------------------------
    # Skill coverage
    # --------------------------------------------------------

    skill_score = min(

        100,

        len(
            curriculum.skills
        )
        * 5,

    )


    # --------------------------------------------------------
    # Technology currency
    # --------------------------------------------------------

    technology_score = min(

        100,

        len(
            curriculum.technologies
        )
        * 10,

    )


    # --------------------------------------------------------
    # Practical exposure
    # --------------------------------------------------------

    project_score = min(

        100,

        len(
            curriculum.projects
        )
        * 15,

    )


    practical_score = min(

        100,

        (

            sum(

                topic.hours

                for module in curriculum.modules

                for topic in module.topics

                if topic.learning_type
                in [

                    LearningType.PRACTICAL,

                    LearningType.LAB,

                    LearningType.PROJECT,

                ]

            )

            /

            max(
                curriculum.total_hours,
                1,
            )

        )

        * 100,

    )


    # --------------------------------------------------------
    # Outcome alignment
    # --------------------------------------------------------

    outcome_score = 0.0


    if curriculum.course_outcomes:

        outcome_score += 40


    if curriculum.program_outcomes:

        outcome_score += 30


    if curriculum.co_po_mappings:

        outcome_score += 30


    # --------------------------------------------------------
    # Overall
    # --------------------------------------------------------

    overall_score = round(

        (

            academic_score * 0.20

            +

            industry_alignment_score * 0.20

            +

            skill_score * 0.15

            +

            technology_score * 0.10

            +

            practical_score * 0.10

            +

            project_score * 0.10

            +

            outcome_score * 0.05

        ),

        2,

    )


    strengths = []

    weaknesses = []


    if academic_score >= 80:

        strengths.append(
            "Strong academic structure."
        )

    else:

        weaknesses.append(
            "Academic structure requires improvement."
        )


    if industry_alignment_score >= 80:

        strengths.append(
            "Strong industry alignment."
        )

    else:

        weaknesses.append(
            "Industry alignment requires improvement."
        )


    if practical_score >= 60:

        strengths.append(
            "Good practical exposure."
        )

    else:

        weaknesses.append(
            "Practical exposure is limited."
        )


    if technology_score >= 60:

        strengths.append(
            "Good technology coverage."
        )

    else:

        weaknesses.append(
            "Technology coverage may be outdated or limited."
        )


    return CurriculumQuality(

        academic_quality=round(
            academic_score,
            2,
        ),

        industry_alignment=round(
            industry_alignment_score,
            2,
        ),

        concept_depth=round(
            min(
                100,
                len(
                    curriculum.concepts
                )
                * 5,
            ),
            2,
        ),

        skill_coverage=round(
            skill_score,
            2,
        ),

        technology_currency=round(
            technology_score,
            2,
        ),

        practical_exposure=round(
            practical_score,
            2,
        ),

        project_quality=round(
            project_score,
            2,
        ),

        assessment_quality=round(
            outcome_score,
            2,
        ),

        outcome_alignment=round(
            outcome_score,
            2,
        ),

        overall_score=overall_score,

        strengths=strengths,

        weaknesses=weaknesses,

    )


# ============================================================
# 49. SAFE LIST NORMALIZER
# ============================================================

def normalize_string_list(
    values: Optional[
        List[Any]
    ],
) -> List[str]:
    """
    Normalize arbitrary values into a clean
    list of unique strings.
    """

    if not values:

        return []


    result = []

    seen = set()


    for value in values:

        if value is None:

            continue


        text = str(
            value
        ).strip()


        if not text:

            continue


        key = text.lower()


        if key in seen:

            continue


        seen.add(key)

        result.append(
            text
        )


    return result


# ============================================================
# 50. PUBLIC EXPORTS
# ============================================================

__all__ = [

    # --------------------------------------------------------
    # Base
    # --------------------------------------------------------

    "CurriculumBaseModel",


    # --------------------------------------------------------
    # Enums
    # --------------------------------------------------------

    "DifficultyLevel",

    "LearningType",

    "SkillCategory",

    "ConceptType",

    "MatchType",

    "GapSeverity",

    "PriorityLevel",

    "BloomLevel",

    "OutcomeType",


    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    "CourseMetadata",


    # --------------------------------------------------------
    # Curriculum building blocks
    # --------------------------------------------------------

    "Concept",

    "Skill",

    "Tool",

    "Technology",

    "Project",

    "Topic",

    "Module",


    # --------------------------------------------------------
    # Academic outcomes
    # --------------------------------------------------------

    "CourseObjective",

    "CourseOutcome",

    "ProgramOutcome",

    "ProgramSpecificOutcome",

    "COPOMapping",

    "COPSOmapping",


    # --------------------------------------------------------
    # Main curriculum
    # --------------------------------------------------------

    "Curriculum",


    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    "ConceptComparison",

    "TopicComparison",

    "ModuleComparison",

    "CurriculumComparison",


    # --------------------------------------------------------
    # Industry
    # --------------------------------------------------------

    "SkillMatch",

    "IndustryAlignment",


    # --------------------------------------------------------
    # Gap / Enhancement
    # --------------------------------------------------------

    "CurriculumGap",

    "EnhancementRecommendation",

    "EnhancementTraceability",

    "ExpertRecommendation",

    "AgentDecision",


    # --------------------------------------------------------
    # Analytics
    # --------------------------------------------------------

    "CurriculumStatistics",

    "CurriculumQuality",


    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    "ValidationIssue",

    "ValidationReport",


    # --------------------------------------------------------
    # Final syllabus
    # --------------------------------------------------------

    "FinalSyllabus",

    "CurriculumVersion",


    # --------------------------------------------------------
    # Reports
    # --------------------------------------------------------

    "ReportSection",

    "CurriculumIntelligenceReport",

    "MasterCurriculumReport",


    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    "model_to_dict",

    "model_to_json",

    "model_from_dict",

    "calculate_curriculum_statistics",

    "validate_curriculum",

    "calculate_validation_score",

    "build_validation_report",

    "calculate_curriculum_quality",

    "normalize_string_list",

]


# ============================================================
# END OF curriculum/models.py
# ============================================================
