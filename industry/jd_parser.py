# ============================================================
# industry/jd_parser.py
# CHUNK 1/10
#
# JOB DESCRIPTION PARSER
#
# Purpose:
#   Parse raw Job Description text into structured industry
#   intelligence that can be consumed by:
#
#       industry/skill_matcher.py
#       industry/taxonomy.py
#       curriculum/skill_extractor.py
#       curriculum/comparator.py
#       04_Gap_Enhancement.py
#       05_Reports.py
#
# Pipeline:
#
#   Raw JD
#      ↓
#   Text Cleaning
#      ↓
#   Section Detection
#      ↓
#   Requirement Extraction
#      ↓
#   Skill / Tool Extraction
#      ↓
#   Experience / Education
#      ↓
#   Role / Seniority
#      ↓
#   Structured JDProfile
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
    Tuple,
    Union,
)


# ============================================================
# VERSION
# ============================================================

JD_PARSER_VERSION = "1.0.0"


# ============================================================
# SECTION TYPES
# ============================================================

SECTION_SUMMARY = "summary"

SECTION_RESPONSIBILITIES = "responsibilities"

SECTION_REQUIREMENTS = "requirements"

SECTION_REQUIRED_SKILLS = "required_skills"

SECTION_PREFERRED_SKILLS = "preferred_skills"

SECTION_TECHNOLOGIES = "technologies"

SECTION_EDUCATION = "education"

SECTION_EXPERIENCE = "experience"

SECTION_CERTIFICATIONS = "certifications"

SECTION_BENEFITS = "benefits"

SECTION_ABOUT_COMPANY = "about_company"

SECTION_OTHER = "other"


# ============================================================
# REQUIREMENT TYPES
# ============================================================

REQUIRED = "required"

PREFERRED = "preferred"

OPTIONAL = "optional"

UNKNOWN = "unknown"


# ============================================================
# SENIORITY
# ============================================================

SENIORITY_INTERN = "intern"

SENIORITY_ENTRY = "entry"

SENIORITY_JUNIOR = "junior"

SENIORITY_MID = "mid"

SENIORITY_SENIOR = "senior"

SENIORITY_LEAD = "lead"

SENIORITY_PRINCIPAL = "principal"

SENIORITY_MANAGER = "manager"

SENIORITY_DIRECTOR = "director"

SENIORITY_UNKNOWN = "unknown"


SENIORITY_ORDER = {

    SENIORITY_INTERN: 0,

    SENIORITY_ENTRY: 1,

    SENIORITY_JUNIOR: 2,

    SENIORITY_MID: 3,

    SENIORITY_SENIOR: 4,

    SENIORITY_LEAD: 5,

    SENIORITY_PRINCIPAL: 6,

    SENIORITY_MANAGER: 7,

    SENIORITY_DIRECTOR: 8,

    SENIORITY_UNKNOWN: -1,

}


# ============================================================
# UTILITY
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


def normalize_name(
    value: Any,
) -> str:

    text = normalize_text(
        value
    )

    text = re.sub(
        r"[^a-z0-9+#./& -]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def deduplicate(
    values: Iterable[Any],
) -> List[Any]:

    result = []

    seen = set()

    for value in values:

        value = clean_text(
            value
        )

        if not value:
            continue

        key = normalize_name(
            value
        )

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
# JD SECTION
# ============================================================

@dataclass
class JDSection:

    name: str

    section_type: str

    content: str = ""

    lines: List[str] = field(
        default_factory=list
    )

    confidence: float = 100.0

    order: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# JD REQUIREMENT
# ============================================================

@dataclass
class JDRequirement:

    text: str

    requirement_type: str = UNKNOWN

    category: str = "general"

    skill: Optional[str] = None

    evidence: Optional[str] = None

    confidence: float = 0.0

    priority: float = 0.0

    years_experience: Optional[float] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# JD SKILL
# ============================================================

@dataclass
class JDSkill:

    name: str

    normalized_name: str = ""

    category: str = "technical"

    requirement_type: str = UNKNOWN

    occurrences: int = 1

    importance: float = 0.0

    confidence: float = 0.0

    evidence: List[str] = field(
        default_factory=list
    )

    aliases: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EXPERIENCE REQUIREMENT
# ============================================================

@dataclass
class ExperienceRequirement:

    minimum_years: Optional[float] = None

    maximum_years: Optional[float] = None

    raw_text: str = ""

    seniority: str = SENIORITY_UNKNOWN

    confidence: float = 0.0


# ============================================================
# JD PROFILE
# ============================================================

@dataclass
class JDProfile:

    raw_text: str = ""

    title: str = ""

    company: str = ""

    location: str = ""

    employment_type: str = ""

    seniority: str = SENIORITY_UNKNOWN

    domain: str = ""

    job_family: str = ""

    summary: str = ""

    responsibilities: List[str] = field(
        default_factory=list
    )

    requirements: List[JDRequirement] = field(
        default_factory=list
    )

    required_skills: List[JDSkill] = field(
        default_factory=list
    )

    preferred_skills: List[JDSkill] = field(
        default_factory=list
    )

    technologies: List[JDSkill] = field(
        default_factory=list
    )

    education: List[str] = field(
        default_factory=list
    )

    certifications: List[str] = field(
        default_factory=list
    )

    experience: ExperienceRequirement = field(
        default_factory=ExperienceRequirement
    )

    sections: List[JDSection] = field(
        default_factory=list
    )

    keywords: List[str] = field(
        default_factory=list
    )

    confidence: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PARSER CONFIG
# ============================================================

@dataclass
class JDParserConfig:

    min_skill_length: int = 2

    max_skill_length: int = 80

    detect_unknown_skills: bool = True

    detect_experience: bool = True

    detect_education: bool = True

    detect_certifications: bool = True

    detect_sections: bool = True

    detect_seniority: bool = True

    include_bullets: bool = True

    minimum_confidence: float = 25.0


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# SECTION DETECTION
# ============================================================


# ============================================================
# SECTION HEADER ALIASES
# ============================================================

SECTION_HEADER_MAP = {

    SECTION_SUMMARY: [

        "summary",

        "job summary",

        "role summary",

        "position summary",

        "about the role",

        "about this role",

        "overview",

    ],

    SECTION_RESPONSIBILITIES: [

        "responsibilities",

        "key responsibilities",

        "roles and responsibilities",

        "what you'll do",

        "what you will do",

        "what you'll be doing",

        "what you will be doing",

        "job responsibilities",

        "duties",

        "key duties",

    ],

    SECTION_REQUIREMENTS: [

        "requirements",

        "qualifications",

        "job requirements",

        "basic qualifications",

        "minimum qualifications",

        "what we're looking for",

        "what we are looking for",

        "candidate requirements",

    ],

    SECTION_REQUIRED_SKILLS: [

        "required skills",

        "must have",

        "must-have",

        "required qualifications",

        "required experience",

        "essential skills",

        "technical requirements",

    ],

    SECTION_PREFERRED_SKILLS: [

        "preferred skills",

        "preferred qualifications",

        "nice to have",

        "nice-to-have",

        "desired qualifications",

        "bonus skills",

        "additional qualifications",

    ],

    SECTION_TECHNOLOGIES: [

        "technologies",

        "technology",

        "tech stack",

        "tools",

        "tools and technologies",

        "technology stack",

        "technical stack",

    ],

    SECTION_EDUCATION: [

        "education",

        "educational qualifications",

        "academic qualifications",

        "degree",

        "education requirements",

    ],

    SECTION_EXPERIENCE: [

        "experience",

        "work experience",

        "professional experience",

        "experience required",

        "years of experience",

    ],

    SECTION_CERTIFICATIONS: [

        "certifications",

        "certification",

        "licenses",

        "professional certifications",

    ],

    SECTION_BENEFITS: [

        "benefits",

        "perks",

        "what we offer",

        "employee benefits",

    ],

    SECTION_ABOUT_COMPANY: [

        "about us",

        "about the company",

        "company overview",

        "who we are",

    ],

}


# ============================================================
# HEADER NORMALIZATION
# ============================================================

def normalize_header(
    value: str,
) -> str:

    text = normalize_name(
        value
    )

    text = text.strip(
        " :-"
    )

    return text


# ============================================================
# IDENTIFY SECTION TYPE
# ============================================================

def identify_section_type(
    header: str,
) -> Optional[str]:

    normalized = normalize_header(
        header
    )

    if not normalized:
        return None

    for section_type, aliases in (
        SECTION_HEADER_MAP.items()
    ):

        for alias in aliases:

            alias_normalized = normalize_header(
                alias
            )

            if normalized == alias_normalized:

                return section_type

    return None


# ============================================================
# HEADER HEURISTIC
# ============================================================

def looks_like_section_header(
    line: str,
) -> bool:

    line = clean_text(
        line
    )

    if not line:
        return False

    section_type = identify_section_type(
        line
    )

    if section_type:
        return True

    # Markdown headers.
    if re.match(
        r"^#{1,6}\s+",
        line,
    ):

        return True

    # Colon-ended headings.
    if (
        len(line) < 80
        and line.endswith(":")
        and not re.search(
            r"[.!?]\s*$",
            line,
        )
    ):

        return True

    # Short uppercase headings.
    letters = re.sub(
        r"[^A-Za-z]",
        "",
        line,
    )

    if (
        len(line) < 70
        and len(letters) >= 4
        and letters.isupper()
    ):

        return True

    return False


# ============================================================
# CLEAN HEADER
# ============================================================

def clean_section_header(
    line: str,
) -> str:

    line = clean_text(
        line
    )

    line = re.sub(
        r"^#{1,6}\s*",
        "",
        line,
    )

    line = line.strip(
        " :-"
    )

    return line


# ============================================================
# SPLIT INTO SECTIONS
# ============================================================

def split_into_sections(
    text: str,
) -> List[JDSection]:

    text = clean_text(
        text
    )

    if not text:
        return []

    lines = text.split(
        "\n"
    )

    sections = []

    current_name = "General"

    current_type = SECTION_OTHER

    current_lines = []

    order = 0

    def flush():

        nonlocal order

        if not current_lines:
            return

        content = "\n".join(
            current_lines
        ).strip()

        if not content:
            return

        sections.append(

            JDSection(

                name=current_name,

                section_type=current_type,

                content=content,

                lines=[

                    clean_text(
                        line
                    )

                    for line
                    in current_lines

                    if clean_text(
                        line
                    )

                ],

                confidence=100.0,

                order=order,

            )

        )

        order += 1

    for raw_line in lines:

        line = clean_text(
            raw_line
        )

        if not line:
            current_lines.append(
                ""
            )
            continue

        if looks_like_section_header(
            line
        ):

            flush()

            current_name = clean_section_header(
                line
            )

            detected = identify_section_type(
                current_name
            )

            current_type = (

                detected

                if detected

                else SECTION_OTHER

            )

            current_lines = []

            continue

        current_lines.append(
            line
        )

    flush()

    return sections


# ============================================================
# MERGE ADJACENT SAME SECTIONS
# ============================================================

def merge_sections(
    sections: Sequence[JDSection],
) -> List[JDSection]:

    if not sections:
        return []

    merged = []

    for section in sections:

        if (

            merged

            and

            merged[-1].section_type
            ==
            section.section_type

        ):

            merged[-1].content += (
                "\n"
                +
                section.content
            )

            merged[-1].lines.extend(
                section.lines
            )

        else:

            merged.append(
                section
            )

    return merged


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# GENERAL JD METADATA EXTRACTION
# ============================================================


# ============================================================
# BULLET CLEANING
# ============================================================

BULLET_PATTERN = re.compile(
    r"^\s*(?:[-*•▪◦‣➢➤]|\d+[.)])\s+"
)


def clean_bullet(
    line: str,
) -> str:

    line = clean_text(
        line
    )

    line = BULLET_PATTERN.sub(
        "",
        line,
    )

    return line.strip()


# ============================================================
# EXTRACT BULLETS
# ============================================================

def extract_bullets(
    text: str,
) -> List[str]:

    lines = clean_text(
        text
    ).split(
        "\n"
    )

    bullets = []

    for line in lines:

        cleaned = clean_bullet(
            line
        )

        if not cleaned:
            continue

        if (
            cleaned != line
            or
            BULLET_PATTERN.match(
                line
            )
        ):

            bullets.append(
                cleaned
            )

    return deduplicate(
        bullets
    )


# ============================================================
# EXTRACT SENTENCES
# ============================================================

def extract_sentences(
    text: str,
) -> List[str]:

    text = clean_text(
        text
    )

    if not text:
        return []

    parts = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    return deduplicate(
        parts
    )


# ============================================================
# TITLE PATTERNS
# ============================================================

TITLE_PATTERNS = [

    r"(?:job|position|role)\s*title\s*[:\-]\s*(.+)",

    r"(?:title)\s*[:\-]\s*(.+)",

    r"(?:position)\s*[:\-]\s*(.+)",

]


# ============================================================
# COMMON ROLE KEYWORDS
# ============================================================

ROLE_KEYWORDS = [

    "engineer",

    "developer",

    "scientist",

    "analyst",

    "architect",

    "manager",

    "consultant",

    "specialist",

    "administrator",

    "designer",

    "researcher",

    "intern",

    "lead",

    "director",

    "associate",

    "devops",

    "data",

    "machine learning",

    "ai",

    "software",

]


# ============================================================
# EXTRACT TITLE
# ============================================================

def extract_title(
    text: str,
    sections: Optional[
        Sequence[JDSection]
    ] = None,
) -> str:

    lines = clean_text(
        text
    ).split(
        "\n"
    )

    # Explicit title.
    for line in lines:

        normalized = normalize_text(
            line
        )

        for pattern in TITLE_PATTERNS:

            match = re.search(
                pattern,
                normalized,
                re.IGNORECASE,
            )

            if match:

                return clean_text(
                    match.group(
                        1
                    )
                )

    # First short role-like line.
    for line in lines[:20]:

        cleaned = clean_bullet(
            line
        )

        if not cleaned:
            continue

        normalized = normalize_text(
            cleaned
        )

        if any(

            keyword in normalized

            for keyword
            in ROLE_KEYWORDS

        ):

            if len(cleaned) <= 100:

                return cleaned

    return ""


# ============================================================
# COMPANY PATTERNS
# ============================================================

COMPANY_PATTERNS = [

    r"(?:company|employer|organization)\s*[:\-]\s*(.+)",

    r"(?:company name)\s*[:\-]\s*(.+)",

]


# ============================================================
# EXTRACT COMPANY
# ============================================================

def extract_company(
    text: str,
) -> str:

    lines = clean_text(
        text
    ).split(
        "\n"
    )

    for line in lines:

        for pattern in COMPANY_PATTERNS:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE,
            )

            if match:

                return clean_text(
                    match.group(
                        1
                    )
                )

    return ""


# ============================================================
# LOCATION PATTERNS
# ============================================================

LOCATION_PATTERNS = [

    r"(?:location|job location|work location)\s*[:\-]\s*(.+)",

    r"(?:based in)\s+([A-Za-z][A-Za-z ,/&-]{2,80})",

]


# ============================================================
# EXTRACT LOCATION
# ============================================================

def extract_location(
    text: str,
) -> str:

    for pattern in LOCATION_PATTERNS:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            return clean_text(
                match.group(
                    1
                )
            )

    return ""


# ============================================================
# EMPLOYMENT TYPES
# ============================================================

EMPLOYMENT_TYPES = [

    "full-time",

    "full time",

    "part-time",

    "part time",

    "contract",

    "contractor",

    "internship",

    "intern",

    "temporary",

    "freelance",

    "remote",

    "hybrid",

]


# ============================================================
# EXTRACT EMPLOYMENT TYPE
# ============================================================

def extract_employment_type(
    text: str,
) -> str:

    normalized = normalize_text(
        text
    )

    for employment_type in EMPLOYMENT_TYPES:

        if employment_type in normalized:

            return employment_type

    return ""


# ============================================================
# EXTRACT SUMMARY
# ============================================================

def extract_summary(
    sections: Sequence[JDSection],
) -> str:

    for section in sections:

        if section.section_type == SECTION_SUMMARY:

            return clean_text(
                section.content
            )

    # Fallback to first general section.
    for section in sections:

        if section.section_type == SECTION_OTHER:

            content = clean_text(
                section.content
            )

            if content:

                return content[:1500]

    return ""


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# EXPERIENCE + SENIORITY EXTRACTION
# ============================================================


# ============================================================
# EXPERIENCE PATTERNS
# ============================================================

EXPERIENCE_PATTERNS = [

    # 3+ years
    r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",

    # minimum 3 years
    r"(?:minimum|at least|minimum of)\s+(\d+(?:\.\d+)?)\s*years?",

    # 3 to 5 years
    r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*years?",

    # 3-5 years experience
    r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*years?\s+(?:of\s+)?experience",

]


# ============================================================
# EXTRACT EXPERIENCE
# ============================================================

def extract_experience(
    text: str,
) -> ExperienceRequirement:

    normalized = normalize_text(
        text
    )

    candidates = []

    # Range first.
    for match in re.finditer(

        EXPERIENCE_PATTERNS[2],

        normalized,

        re.IGNORECASE,

    ):

        minimum = float(
            match.group(
                1
            )
        )

        maximum = float(
            match.group(
                2
            )
        )

        candidates.append(

            ExperienceRequirement(

                minimum_years=minimum,

                maximum_years=maximum,

                raw_text=match.group(
                    0
                ),

                confidence=95.0,

            )

        )

    # Single requirement.
    for pattern in (
        EXPERIENCE_PATTERNS[0],
        EXPERIENCE_PATTERNS[1],
    ):

        for match in re.finditer(

            pattern,

            normalized,

            re.IGNORECASE,

        ):

            minimum = float(
                match.group(
                    1
                )
            )

            candidates.append(

                ExperienceRequirement(

                    minimum_years=minimum,

                    maximum_years=None,

                    raw_text=match.group(
                        0
                    ),

                    confidence=90.0,

                )

            )

    if not candidates:

        return ExperienceRequirement()

    # Prefer highest confidence.
    candidates.sort(

        key=lambda item: (

            item.confidence,

            item.minimum_years or 0.0,

        ),

        reverse=True,

    )

    result = candidates[0]

    result.seniority = infer_seniority_from_years(

        result.minimum_years

    )

    return result


# ============================================================
# SENIORITY KEYWORDS
# ============================================================

SENIORITY_KEYWORDS = {

    SENIORITY_INTERN: [

        "intern",

        "internship",

        "trainee",

    ],

    SENIORITY_ENTRY: [

        "entry level",

        "entry-level",

        "graduate",

        "fresher",

        "fresh graduate",

    ],

    SENIORITY_JUNIOR: [

        "junior",

        "jr.",

        "associate developer",

    ],

    SENIORITY_MID: [

        "mid level",

        "mid-level",

        "intermediate",

    ],

    SENIORITY_SENIOR: [

        "senior",

        "sr.",

    ],

    SENIORITY_LEAD: [

        "lead",

        "technical lead",

        "team lead",

    ],

    SENIORITY_PRINCIPAL: [

        "principal",

        "staff",

        "distinguished",

    ],

    SENIORITY_MANAGER: [

        "manager",

        "engineering manager",

        "product manager",

    ],

    SENIORITY_DIRECTOR: [

        "director",

        "head of",

        "vp",

        "vice president",

    ],

}


# ============================================================
# INFER SENIORITY FROM YEARS
# ============================================================

def infer_seniority_from_years(
    years: Optional[float],
) -> str:

    if years is None:

        return SENIORITY_UNKNOWN

    if years < 1:

        return SENIORITY_INTERN

    if years < 2:

        return SENIORITY_ENTRY

    if years < 3:

        return SENIORITY_JUNIOR

    if years < 6:

        return SENIORITY_MID

    if years < 10:

        return SENIORITY_SENIOR

    if years < 15:

        return SENIORITY_LEAD

    return SENIORITY_PRINCIPAL


# ============================================================
# EXTRACT SENIORITY
# ============================================================

def extract_seniority(
    text: str,
    title: str = "",
    experience: Optional[
        ExperienceRequirement
    ] = None,
) -> str:

    combined = normalize_text(

        f"{title} {text}"

    )

    # Strong title-level signals.
    priority = [

        SENIORITY_DIRECTOR,

        SENIORITY_MANAGER,

        SENIORITY_PRINCIPAL,

        SENIORITY_LEAD,

        SENIORITY_SENIOR,

        SENIORITY_MID,

        SENIORITY_JUNIOR,

        SENIORITY_ENTRY,

        SENIORITY_INTERN,

    ]

    for seniority in priority:

        for keyword in (
            SENIORITY_KEYWORDS[
                seniority
            ]
        ):

            if keyword in combined:

                return seniority

    if experience:

        return infer_seniority_from_years(

            experience.minimum_years

        )

    return SENIORITY_UNKNOWN


# ============================================================
# EXPERIENCE SENTENCES
# ============================================================

def extract_experience_requirements(
    sections: Sequence[JDSection],
) -> List[JDRequirement]:

    requirements = []

    for section in sections:

        if section.section_type not in {

            SECTION_EXPERIENCE,

            SECTION_REQUIREMENTS,

            SECTION_REQUIRED_SKILLS,

        }:

            continue

        sentences = (

            extract_bullets(
                section.content
            )

            or

            extract_sentences(
                section.content
            )

        )

        for sentence in sentences:

            if re.search(

                r"\b\d+(?:\.\d+)?\s*\+?\s*years?\b",

                sentence,

                re.IGNORECASE,

            ):

                experience = extract_experience(
                    sentence
                )

                requirements.append(

                    JDRequirement(

                        text=sentence,

                        requirement_type=REQUIRED,

                        category="experience",

                        confidence=experience.confidence,

                        years_experience=(

                            experience.minimum_years

                        ),

                    )

                )

    return requirements


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# EDUCATION + CERTIFICATION EXTRACTION
# ============================================================


# ============================================================
# EDUCATION KEYWORDS
# ============================================================

EDUCATION_PATTERNS = [

    r"\b(?:bachelor'?s?|b\.?e\.?|b\.?tech|bsc|bca)\b",

    r"\b(?:master'?s?|m\.?e\.?|m\.?tech|msc|mca)\b",

    r"\b(?:ph\.?d|doctorate|doctoral)\b",

    r"\b(?:mba|pgdm|postgraduate)\b",

    r"\b(?:degree|diploma)\b",

    r"\b(?:computer science|information technology|artificial intelligence|data science)\b",

]


# ============================================================
# EDUCATION DEGREE MAP
# ============================================================

EDUCATION_DEGREE_PATTERNS = {

    "bachelor":

        r"\b(?:bachelor'?s?|b\.?e\.?|b\.?tech|bsc|bca)\b",

    "master":

        r"\b(?:master'?s?|m\.?e\.?|m\.?tech|msc|mca)\b",

    "phd":

        r"\b(?:ph\.?d|doctorate|doctoral)\b",

    "mba":

        r"\b(?:mba|pgdm)\b",

    "diploma":

        r"\b(?:diploma)\b",

}


# ============================================================
# EXTRACT EDUCATION
# ============================================================

def extract_education(
    text: str,
    sections: Optional[
        Sequence[JDSection]
    ] = None,
) -> List[str]:

    source_text = text

    if sections:

        education_sections = [

            section.content

            for section
            in sections

            if section.section_type
            == SECTION_EDUCATION

        ]

        if education_sections:

            source_text = "\n".join(
                education_sections
            )

    lines = source_text.split(
        "\n"
    )

    results = []

    for line in lines:

        cleaned = clean_bullet(
            line
        )

        if not cleaned:
            continue

        if any(

            re.search(
                pattern,
                cleaned,
                re.IGNORECASE,
            )

            for pattern
            in EDUCATION_PATTERNS

        ):

            results.append(
                cleaned
            )

    # Sentence fallback.
    if not results:

        for sentence in extract_sentences(
            source_text
        ):

            if any(

                re.search(
                    pattern,
                    sentence,
                    re.IGNORECASE,
                )

                for pattern
                in EDUCATION_PATTERNS

            ):

                results.append(
                    sentence
                )

    return deduplicate(
        results
    )


# ============================================================
# CERTIFICATION PATTERNS
# ============================================================

CERTIFICATION_KEYWORDS = [

    "certified",

    "certification",

    "certificate",

    "professional certification",

    "aws certified",

    "azure certification",

    "google cloud certification",

    "pmp",

    "scrum master",

    "cissp",

    "comptia",

    "cka",

    "ckad",

]


# ============================================================
# EXTRACT CERTIFICATIONS
# ============================================================

def extract_certifications(
    text: str,
    sections: Optional[
        Sequence[JDSection]
    ] = None,
) -> List[str]:

    source_text = text

    if sections:

        certification_sections = [

            section.content

            for section
            in sections

            if section.section_type
            == SECTION_CERTIFICATIONS

        ]

        if certification_sections:

            source_text = "\n".join(
                certification_sections
            )

    lines = source_text.split(
        "\n"
    )

    results = []

    for line in lines:

        cleaned = clean_bullet(
            line
        )

        if not cleaned:
            continue

        normalized = normalize_text(
            cleaned
        )

        if any(

            keyword in normalized

            for keyword
            in CERTIFICATION_KEYWORDS

        ):

            results.append(
                cleaned
            )

    return deduplicate(
        results
    )


# ============================================================
# EXTRACT EDUCATION REQUIREMENTS
# ============================================================

def extract_education_requirements(
    sections: Sequence[JDSection],
) -> List[JDRequirement]:

    requirements = []

    for section in sections:

        if section.section_type not in {

            SECTION_EDUCATION,

            SECTION_REQUIREMENTS,

            SECTION_REQUIRED_SKILLS,

        }:

            continue

        for line in (

            extract_bullets(
                section.content
            )

            or

            extract_sentences(
                section.content
            )

        ):

            if any(

                re.search(
                    pattern,
                    line,
                    re.IGNORECASE,
                )

                for pattern
                in EDUCATION_PATTERNS

            ):

                requirements.append(

                    JDRequirement(

                        text=line,

                        requirement_type=REQUIRED,

                        category="education",

                        confidence=85.0,

                    )

                )

    return requirements


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# SKILL / TECHNOLOGY KNOWLEDGE BASE
# ============================================================


# ============================================================
# CANONICAL SKILLS
# ============================================================

CANONICAL_SKILLS = {

    # --------------------------------------------------------
    # Programming
    # --------------------------------------------------------

    "python": [

        "python",

        "python programming",

    ],

    "java": [

        "java",

    ],

    "javascript": [

        "javascript",

        "js",

    ],

    "typescript": [

        "typescript",

        "ts",

    ],

    "c++": [

        "c++",

        "cpp",

    ],

    "c#": [

        "c#",

        "c sharp",

    ],

    "sql": [

        "sql",

        "structured query language",

    ],

    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

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

    "data analysis": [

        "data analysis",

        "data analytics",

    ],

    "statistics": [

        "statistics",

        "statistical analysis",

    ],

    # --------------------------------------------------------
    # Machine Learning
    # --------------------------------------------------------

    "machine learning": [

        "machine learning",

        "ml",

    ],

    "deep learning": [

        "deep learning",

        "dl",

    ],

    "feature engineering": [

        "feature engineering",

    ],

    "model evaluation": [

        "model evaluation",

        "model validation",

    ],

    "time series": [

        "time series",

        "time-series",

        "forecasting",

    ],

    "recommendation systems": [

        "recommendation systems",

        "recommender systems",

    ],

    # --------------------------------------------------------
    # Deep Learning
    # --------------------------------------------------------

    "tensorflow": [

        "tensorflow",

    ],

    "keras": [

        "keras",

    ],

    "pytorch": [

        "pytorch",

        "torch",

    ],

    "transformers": [

        "transformers",

        "transformer architecture",

    ],

    # --------------------------------------------------------
    # NLP / GenAI
    # --------------------------------------------------------

    "natural language processing": [

        "natural language processing",

        "nlp",

    ],

    "generative ai": [

        "generative ai",

        "gen ai",

        "genai",

    ],

    "large language models": [

        "large language models",

        "large language model",

        "llm",

        "llms",

    ],

    "prompt engineering": [

        "prompt engineering",

        "prompt design",

    ],

    "embeddings": [

        "embeddings",

        "embedding models",

    ],

    "retrieval augmented generation": [

        "retrieval augmented generation",

        "retrieval-augmented generation",

        "rag",

    ],

    "vector databases": [

        "vector databases",

        "vector database",

        "vector db",

    ],

    "fine tuning": [

        "fine tuning",

        "fine-tuning",

        "finetuning",

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

    "hugging face": [

        "hugging face",

        "huggingface",

    ],

    # --------------------------------------------------------
    # Cloud
    # --------------------------------------------------------

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

        "google cloud",

        "google cloud platform",

    ],

    # --------------------------------------------------------
    # DevOps
    # --------------------------------------------------------

    "git": [

        "git",

        "github",

        "gitlab",

    ],

    "docker": [

        "docker",

        "containerization",

        "containers",

    ],

    "kubernetes": [

        "kubernetes",

        "k8s",

    ],

    "terraform": [

        "terraform",

        "infrastructure as code",

    ],

    "ci/cd": [

        "ci/cd",

        "continuous integration",

        "continuous delivery",

        "continuous deployment",

    ],

    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------

    "postgresql": [

        "postgresql",

        "postgres",

    ],

    "mysql": [

        "mysql",

    ],

    "mongodb": [

        "mongodb",

        "mongo",

    ],

    "redis": [

        "redis",

    ],

    # --------------------------------------------------------
    # Data Engineering
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Computer Vision
    # --------------------------------------------------------

    "computer vision": [

        "computer vision",

        "cv",

    ],

    "opencv": [

        "opencv",

        "opencv-python",

    ],

    "yolo": [

        "yolo",

        "yolov5",

        "yolov8",

        "yolov9",

        "yolov10",

        "yolov11",

    ],

    # --------------------------------------------------------
    # BI
    # --------------------------------------------------------

    "power bi": [

        "power bi",

        "powerbi",

    ],

    "tableau": [

        "tableau",

    ],

    "excel": [

        "excel",

        "microsoft excel",

    ],

}


# ============================================================
# TECHNOLOGY CATEGORIES
# ============================================================

SKILL_CATEGORIES = {

    "python": "programming",

    "java": "programming",

    "javascript": "programming",

    "typescript": "programming",

    "c++": "programming",

    "c#": "programming",

    "sql": "database",

    "pandas": "data",

    "numpy": "data",

    "scikit-learn": "machine_learning",

    "machine learning": "machine_learning",

    "deep learning": "deep_learning",

    "tensorflow": "deep_learning",

    "keras": "deep_learning",

    "pytorch": "deep_learning",

    "transformers": "generative_ai",

    "natural language processing": "nlp",

    "generative ai": "generative_ai",

    "large language models": "generative_ai",

    "prompt engineering": "generative_ai",

    "embeddings": "generative_ai",

    "retrieval augmented generation": "generative_ai",

    "vector databases": "database",

    "fine tuning": "generative_ai",

    "langchain": "generative_ai",

    "langgraph": "agentic_ai",

    "llamaindex": "generative_ai",

    "hugging face": "generative_ai",

    "aws": "cloud",

    "azure": "cloud",

    "gcp": "cloud",

    "git": "devops",

    "docker": "devops",

    "kubernetes": "devops",

    "terraform": "devops",

    "ci/cd": "devops",

    "postgresql": "database",

    "mysql": "database",

    "mongodb": "database",

    "redis": "database",

    "apache spark": "data_engineering",

    "apache kafka": "data_engineering",

    "apache airflow": "data_engineering",

    "computer vision": "computer_vision",

    "opencv": "computer_vision",

    "yolo": "computer_vision",

    "power bi": "business_intelligence",

    "tableau": "business_intelligence",

    "excel": "business_intelligence",

}


# ============================================================
# CANONICALIZE SKILL
# ============================================================

def canonicalize_skill(
    skill: str,
) -> str:

    normalized = normalize_name(
        skill
    )

    if not normalized:
        return ""

    for canonical, aliases in (
        CANONICAL_SKILLS.items()
    ):

        if normalized == normalize_name(
            canonical
        ):

            return canonical

        for alias in aliases:

            if normalized == normalize_name(
                alias
            ):

                return canonical

    return normalized


# ============================================================
# SKILL CATEGORY
# ============================================================

def skill_category(
    skill: str,
) -> str:

    canonical = canonicalize_skill(
        skill
    )

    return SKILL_CATEGORIES.get(
        canonical,
        "technical",
    )


# ============================================================
# SKILL ALIASES
# ============================================================

def skill_aliases(
    skill: str,
) -> List[str]:

    canonical = canonicalize_skill(
        skill
    )

    aliases = CANONICAL_SKILLS.get(
        canonical,
        [],
    )

    return deduplicate(
        aliases
    )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# SKILL EXTRACTION
# ============================================================


# ============================================================
# SAFE PHRASE SEARCH
# ============================================================

def phrase_occurrences(
    text: str,
    phrase: str,
) -> int:

    normalized_text = normalize_text(
        text
    )

    normalized_phrase = normalize_text(
        phrase
    )

    if not normalized_text or not normalized_phrase:
        return 0

    pattern = (

        r"(?<![a-z0-9+#])"

        +
        re.escape(
            normalized_phrase
        )

        +
        r"(?![a-z0-9+#])"

    )

    return len(
        re.findall(
            pattern,
            normalized_text,
        )
    )


# ============================================================
# EXTRACT KNOWN SKILLS
# ============================================================

def extract_known_skills(
    text: str,
    requirement_type: str = UNKNOWN,
) -> List[JDSkill]:

    text = clean_text(
        text
    )

    results = []

    for canonical, aliases in (
        CANONICAL_SKILLS.items()
    ):

        occurrences = 0

        evidence = []

        for alias in (

            [canonical]
            +
            aliases

        ):

            count = phrase_occurrences(
                text,
                alias,
            )

            if count > 0:

                occurrences += count

                evidence.append(
                    alias
                )

        if occurrences <= 0:
            continue

        importance = min(

            100.0,

            30.0
            +
            occurrences * 15.0,

        )

        results.append(

            JDSkill(

                name=canonical,

                normalized_name=canonical,

                category=skill_category(
                    canonical
                ),

                requirement_type=requirement_type,

                occurrences=occurrences,

                importance=importance,

                confidence=95.0,

                evidence=deduplicate(
                    evidence
                ),

                aliases=skill_aliases(
                    canonical
                ),

            )

        )

    return results


# ============================================================
# UNKNOWN SKILL CANDIDATE EXTRACTION
# ============================================================

UNKNOWN_SKILL_PATTERNS = [

    r"\b[A-Z][A-Za-z0-9+#.-]{1,30}\b",

    r"\b[A-Za-z][A-Za-z0-9+#.-]{1,25}\s+(?:AI|API|SDK|Cloud|Platform)\b",

]


def extract_unknown_skill_candidates(
    text: str,
) -> List[str]:

    candidates = []

    for pattern in UNKNOWN_SKILL_PATTERNS:

        matches = re.findall(
            pattern,
            text,
        )

        candidates.extend(
            matches
        )

    stopwords = {

        "The",

        "This",

        "That",

        "You",

        "We",

        "Our",

        "Your",

        "Job",

        "Role",

        "Responsibilities",

        "Requirements",

        "Experience",

        "Education",

        "Skills",

        "Team",

        "About",

        "Company",

        "Candidate",

    }

    cleaned = []

    for candidate in candidates:

        candidate = clean_text(
            candidate
        )

        if candidate in stopwords:
            continue

        if len(candidate) < 2:
            continue

        if len(candidate) > 80:
            continue

        cleaned.append(
            candidate
        )

    return deduplicate(
        cleaned
    )


# ============================================================
# CLASSIFY REQUIREMENT TYPE
# ============================================================

PREFERRED_MARKERS = [

    "preferred",

    "preferably",

    "nice to have",

    "nice-to-have",

    "bonus",

    "plus",

    "desired",

    "would be a plus",

    "good to have",

]


REQUIRED_MARKERS = [

    "required",

    "must",

    "mandatory",

    "essential",

    "minimum",

    "should have",

    "strong experience",

]


def classify_requirement_type(
    text: str,
    section_type: str = SECTION_OTHER,
) -> str:

    normalized = normalize_text(
        text
    )

    if section_type in {

        SECTION_PREFERRED_SKILLS,

    }:

        return PREFERRED

    if section_type in {

        SECTION_REQUIRED_SKILLS,

        SECTION_REQUIREMENTS,

    }:

        for marker in PREFERRED_MARKERS:

            if marker in normalized:

                return PREFERRED

        return REQUIRED

    for marker in PREFERRED_MARKERS:

        if marker in normalized:

            return PREFERRED

    for marker in REQUIRED_MARKERS:

        if marker in normalized:

            return REQUIRED

    return UNKNOWN


# ============================================================
# EXTRACT REQUIREMENTS
# ============================================================

def extract_requirements(
    sections: Sequence[JDSection],
) -> List[JDRequirement]:

    requirements = []

    relevant_sections = {

        SECTION_REQUIREMENTS,

        SECTION_REQUIRED_SKILLS,

        SECTION_PREFERRED_SKILLS,

        SECTION_EXPERIENCE,

        SECTION_EDUCATION,

        SECTION_RESPONSIBILITIES,

    }

    for section in sections:

        if section.section_type not in relevant_sections:
            continue

        lines = (

            extract_bullets(
                section.content
            )

            or

            extract_sentences(
                section.content
            )

        )

        for line in lines:

            if not line:
                continue

            requirement_type = (
                classify_requirement_type(

                    line,

                    section.section_type,

                )
            )

            category = "general"

            if section.section_type == SECTION_RESPONSIBILITIES:
                category = "responsibility"

            elif section.section_type == SECTION_EXPERIENCE:
                category = "experience"

            elif section.section_type == SECTION_EDUCATION:
                category = "education"

            elif section.section_type in {

                SECTION_REQUIRED_SKILLS,

                SECTION_PREFERRED_SKILLS,

            }:
                category = "skill"

            confidence = (

                90.0

                if requirement_type
                != UNKNOWN

                else 60.0

            )

            requirements.append(

                JDRequirement(

                    text=line,

                    requirement_type=requirement_type,

                    category=category,

                    confidence=confidence,

                )

            )

    return requirements


# ============================================================
# ASSIGN SKILL REQUIREMENT TYPE
# ============================================================

def assign_skill_requirements(
    skills: List[JDSkill],
    sections: Sequence[JDSection],
) -> List[JDSkill]:

    for skill in skills:

        evidence_text = " ".join(
            skill.evidence
        )

        # Search sections where skill appears.
        matched_types = []

        for section in sections:

            if phrase_occurrences(

                section.content,

                skill.name,

            ) <= 0:

                continue

            matched_types.append(

                classify_requirement_type(

                    section.content,

                    section.section_type,

                )

            )

        if PREFERRED in matched_types:

            skill.requirement_type = PREFERRED

        elif REQUIRED in matched_types:

            skill.requirement_type = REQUIRED

        else:

            skill.requirement_type = UNKNOWN

        skill.evidence = deduplicate(

            skill.evidence
            +
            [

                evidence_text

            ]
            if evidence_text
            else skill.evidence

        )

    return skills


# ============================================================
# SPLIT REQUIRED / PREFERRED
# ============================================================

def split_skill_requirements(
    skills: Sequence[JDSkill],
) -> Tuple[
    List[JDSkill],
    List[JDSkill],
]:

    required = []

    preferred = []

    for skill in skills:

        if skill.requirement_type == PREFERRED:

            preferred.append(
                skill
            )

        else:

            required.append(
                skill
            )

    return required, preferred


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# ROLE / DOMAIN / RESPONSIBILITY INTELLIGENCE
# ============================================================


# ============================================================
# DOMAIN KEYWORDS
# ============================================================

DOMAIN_KEYWORDS = {

    "artificial intelligence": [

        "artificial intelligence",

        "ai",

        "machine learning",

        "deep learning",

        "generative ai",

        "llm",

        "agentic ai",

    ],

    "data science": [

        "data scientist",

        "data science",

        "predictive modeling",

        "statistical modeling",

        "machine learning",

    ],

    "data engineering": [

        "data engineer",

        "data engineering",

        "etl",

        "data pipeline",

        "spark",

        "kafka",

    ],

    "software engineering": [

        "software engineer",

        "software developer",

        "application developer",

        "backend developer",

        "frontend developer",

        "full stack",

    ],

    "devops": [

        "devops",

        "site reliability",

        "sre",

        "kubernetes",

        "docker",

        "ci/cd",

    ],

    "cloud computing": [

        "cloud",

        "aws",

        "azure",

        "gcp",

        "cloud architecture",

    ],

    "cybersecurity": [

        "cybersecurity",

        "cyber security",

        "security engineer",

        "soc",

        "penetration testing",

        "threat detection",

    ],

    "business intelligence": [

        "business intelligence",

        "bi developer",

        "power bi",

        "tableau",

        "dashboard",

        "reporting",

    ],

}


# ============================================================
# JOB FAMILY KEYWORDS
# ============================================================

JOB_FAMILY_KEYWORDS = {

    "machine learning": [

        "machine learning engineer",

        "ml engineer",

        "machine learning",

    ],

    "data science": [

        "data scientist",

        "data science",

    ],

    "generative ai": [

        "generative ai",

        "genai",

        "llm engineer",

        "rag engineer",

    ],

    "software engineering": [

        "software engineer",

        "software developer",

        "backend developer",

        "frontend developer",

        "full stack developer",

    ],

    "data engineering": [

        "data engineer",

        "data engineering",

    ],

    "devops": [

        "devops engineer",

        "site reliability engineer",

        "sre",

        "platform engineer",

    ],

    "cloud": [

        "cloud engineer",

        "cloud architect",

        "cloud developer",

    ],

    "business intelligence": [

        "bi developer",

        "business intelligence",

        "data analyst",

        "business analyst",

    ],

}


# ============================================================
# EXTRACT DOMAIN
# ============================================================

def extract_domain(
    text: str,
    title: str = "",
) -> str:

    combined = normalize_text(

        f"{title} {text}"

    )

    scores = {}

    for domain, keywords in (
        DOMAIN_KEYWORDS.items()
    ):

        score = 0

        for keyword in keywords:

            occurrences = phrase_occurrences(

                combined,

                keyword,

            )

            score += occurrences

        if score > 0:

            scores[
                domain
            ] = score

    if not scores:
        return ""

    return max(

        scores,

        key=scores.get,

    )


# ============================================================
# EXTRACT JOB FAMILY
# ============================================================

def extract_job_family(
    text: str,
    title: str = "",
) -> str:

    combined = normalize_text(

        f"{title} {text}"

    )

    scores = {}

    for family, keywords in (
        JOB_FAMILY_KEYWORDS.items()
    ):

        score = 0

        for keyword in keywords:

            score += phrase_occurrences(

                combined,

                keyword,

            )

        if score:

            scores[
                family
            ] = score

    if not scores:
        return ""

    return max(

        scores,

        key=scores.get,

    )


# ============================================================
# RESPONSIBILITY VERBS
# ============================================================

RESPONSIBILITY_VERBS = [

    "develop",

    "design",

    "build",

    "implement",

    "deploy",

    "maintain",

    "manage",

    "lead",

    "analyze",

    "analyse",

    "create",

    "optimize",

    "optimise",

    "monitor",

    "integrate",

    "automate",

    "research",

    "evaluate",

    "test",

    "debug",

    "architect",

]


# ============================================================
# EXTRACT RESPONSIBILITIES
# ============================================================

def extract_responsibilities(
    sections: Sequence[JDSection],
) -> List[str]:

    results = []

    for section in sections:

        if section.section_type != SECTION_RESPONSIBILITIES:

            continue

        bullets = extract_bullets(
            section.content
        )

        if bullets:

            results.extend(
                bullets
            )

            continue

        sentences = extract_sentences(
            section.content
        )

        for sentence in sentences:

            normalized = normalize_text(
                sentence
            )

            if any(

                normalized.startswith(
                    verb
                )

                or
                f" {verb} " in normalized

                for verb
                in RESPONSIBILITY_VERBS

            ):

                results.append(
                    sentence
                )

    return deduplicate(
        results
    )


# ============================================================
# EXTRACT KEYWORDS
# ============================================================

def extract_keywords(
    text: str,
    skills: Sequence[JDSkill],
) -> List[str]:

    keywords = [

        skill.name

        for skill
        in skills

    ]

    # Common business/technical terms.
    common_terms = [

        "api",

        "rest api",

        "microservices",

        "agile",

        "scrum",

        "testing",

        "automation",

        "analytics",

        "cloud",

        "deployment",

        "architecture",

        "security",

        "scalability",

        "performance",

        "optimization",

        "monitoring",

        "documentation",

    ]

    normalized = normalize_text(
        text
    )

    for term in common_terms:

        if phrase_occurrences(

            normalized,

            term,

        ):

            keywords.append(
                term
            )

    return deduplicate(
        keywords
    )


# ============================================================
# EXTRACT TECHNOLOGIES
# ============================================================

def extract_technologies(
    text: str,
    requirement_type: str = UNKNOWN,
) -> List[JDSkill]:

    skills = extract_known_skills(

        text,

        requirement_type,

    )

    technology_categories = {

        "programming",

        "database",

        "cloud",

        "devops",

        "deep_learning",

        "generative_ai",

        "agentic_ai",

        "computer_vision",

        "data_engineering",

        "business_intelligence",

    }

    return [

        skill

        for skill
        in skills

        if skill.category
        in technology_categories

    ]


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# MAIN JD PARSER
# ============================================================


class JDParser:
    """
    Production-oriented Job Description parser.

    The parser intentionally uses deterministic extraction first.
    This makes it reliable, debuggable and suitable for later
    augmentation with an LLM/embedding layer.
    """

    def __init__(
        self,
        config: Optional[
            JDParserConfig
        ] = None,
    ):

        self.config = (

            config

            or

            JDParserConfig()

        )


    # ========================================================
    # PARSE
    # ========================================================

    def parse(
        self,
        text: str,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> JDProfile:

        raw_text = clean_text(
            text
        )

        if not raw_text:

            return JDProfile(

                raw_text="",

                confidence=0.0,

                metadata=metadata or {},

            )

        # ----------------------------------------------------
        # Sections
        # ----------------------------------------------------

        sections = (

            split_into_sections(
                raw_text
            )

            if self.config.detect_sections

            else [

                JDSection(

                    name="General",

                    section_type=SECTION_OTHER,

                    content=raw_text,

                    lines=raw_text.split(
                        "\n"
                    ),

                )

            ]

        )

        sections = merge_sections(
            sections
        )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        title = extract_title(

            raw_text,

            sections,

        )

        company = extract_company(
            raw_text
        )

        location = extract_location(
            raw_text
        )

        employment_type = extract_employment_type(
            raw_text
        )

        summary = extract_summary(
            sections
        )

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        experience = (

            extract_experience(
                raw_text
            )

            if self.config.detect_experience

            else ExperienceRequirement()

        )

        # ----------------------------------------------------
        # Seniority
        # ----------------------------------------------------

        seniority = (

            extract_seniority(

                raw_text,

                title,

                experience,

            )

            if self.config.detect_seniority

            else SENIORITY_UNKNOWN

        )

        experience.seniority = seniority

        # ----------------------------------------------------
        # Responsibilities
        # ----------------------------------------------------

        responsibilities = extract_responsibilities(
            sections
        )

        # ----------------------------------------------------
        # Requirements
        # ----------------------------------------------------

        requirements = extract_requirements(
            sections
        )

        # ----------------------------------------------------
        # Experience requirements
        # ----------------------------------------------------

        requirements.extend(

            extract_experience_requirements(
                sections
            )

        )

        # ----------------------------------------------------
        # Education requirements
        # ----------------------------------------------------

        requirements.extend(

            extract_education_requirements(
                sections
            )

        )

        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        all_skills = extract_known_skills(

            raw_text,

            UNKNOWN,

        )

        all_skills = assign_skill_requirements(

            all_skills,

            sections,

        )

        required_skills, preferred_skills = (
            split_skill_requirements(
                all_skills
            )
        )

        # ----------------------------------------------------
        # Technologies
        # ----------------------------------------------------

        technologies = extract_technologies(
            raw_text
        )

        # ----------------------------------------------------
        # Education
        # ----------------------------------------------------

        education = (

            extract_education(

                raw_text,

                sections,

            )

            if self.config.detect_education

            else []

        )

        # ----------------------------------------------------
        # Certifications
        # ----------------------------------------------------

        certifications = (

            extract_certifications(

                raw_text,

                sections,

            )

            if self.config.detect_certifications

            else []

        )

        # ----------------------------------------------------
        # Domain
        # ----------------------------------------------------

        domain = extract_domain(

            raw_text,

            title,

        )

        job_family = extract_job_family(

            raw_text,

            title,

        )

        # ----------------------------------------------------
        # Keywords
        # ----------------------------------------------------

        keywords = extract_keywords(

            raw_text,

            all_skills,

        )

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        confidence = self._calculate_confidence(

            title=title,

            sections=sections,

            skills=all_skills,

            responsibilities=responsibilities,

            experience=experience,

        )

        # ----------------------------------------------------
        # Profile
        # ----------------------------------------------------

        profile = JDProfile(

            raw_text=raw_text,

            title=title,

            company=company,

            location=location,

            employment_type=employment_type,

            seniority=seniority,

            domain=domain,

            job_family=job_family,

            summary=summary,

            responsibilities=responsibilities,

            requirements=requirements,

            required_skills=required_skills,

            preferred_skills=preferred_skills,

            technologies=technologies,

            education=education,

            certifications=certifications,

            experience=experience,

            sections=sections,

            keywords=keywords,

            confidence=confidence,

            metadata={

                **(

                    metadata
                    or
                    {}

                ),

                "parser_version":
                    JD_PARSER_VERSION,

            },

        )

        return profile


    # ========================================================
    # CONFIDENCE
    # ========================================================

    def _calculate_confidence(
        self,
        title: str,
        sections: Sequence[JDSection],
        skills: Sequence[JDSkill],
        responsibilities: Sequence[str],
        experience: ExperienceRequirement,
    ) -> float:

        score = 0.0

        factors = 0

        if title:

            score += 20.0

        factors += 20.0

        if sections:

            score += 20.0

        factors += 20.0

        if skills:

            score += 20.0

        factors += 20.0

        if responsibilities:

            score += 20.0

        factors += 20.0

        if experience.minimum_years is not None:

            score += 20.0

        factors += 20.0

        if factors <= 0:

            return 0.0

        return round(

            (
                score
                /
                factors
            )
            *
            100.0,

            2,

        )


    # ========================================================
    # PARSE FILE
    # ========================================================

    def parse_file(
        self,
        path: Union[
            str,
            Path,
        ],
        encoding: str = "utf-8",
    ) -> JDProfile:

        path = Path(
            path
        )

        text = path.read_text(
            encoding=encoding
        )

        return self.parse(

            text,

            metadata={

                "source_file":
                    str(path),

                "file_name":
                    path.name,

            },

        )


    # ========================================================
    # PARSE MULTIPLE
    # ========================================================

    def parse_many(
        self,
        texts: Sequence[str],
    ) -> List[JDProfile]:

        return [

            self.parse(
                text
            )

            for text
            in texts

        ]


    # ========================================================
    # PARSE MANY FILES
    # ========================================================

    def parse_files(
        self,
        paths: Sequence[
            Union[
                str,
                Path,
            ]
        ],
    ) -> List[JDProfile]:

        return [

            self.parse_file(
                path
            )

            for path
            in paths

        ]


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# SERIALIZATION + ANALYSIS + PUBLIC API
# ============================================================


# ============================================================
# DATACLASS SERIALIZATION
# ============================================================

def requirement_to_dict(
    requirement: JDRequirement,
) -> Dict[str, Any]:

    return asdict(
        requirement
    )


def skill_to_dict(
    skill: JDSkill,
) -> Dict[str, Any]:

    return asdict(
        skill
    )


def section_to_dict(
    section: JDSection,
) -> Dict[str, Any]:

    return asdict(
        section
    )


def experience_to_dict(
    experience: ExperienceRequirement,
) -> Dict[str, Any]:

    return asdict(
        experience
    )


# ============================================================
# PROFILE TO DICT
# ============================================================

def jd_profile_to_dict(
    profile: JDProfile,
) -> Dict[str, Any]:

    return {

        "raw_text":
            profile.raw_text,

        "title":
            profile.title,

        "company":
            profile.company,

        "location":
            profile.location,

        "employment_type":
            profile.employment_type,

        "seniority":
            profile.seniority,

        "domain":
            profile.domain,

        "job_family":
            profile.job_family,

        "summary":
            profile.summary,

        "responsibilities":
            profile.responsibilities,

        "requirements": [

            requirement_to_dict(
                item
            )

            for item
            in profile.requirements

        ],

        "required_skills": [

            skill_to_dict(
                item
            )

            for item
            in profile.required_skills

        ],

        "preferred_skills": [

            skill_to_dict(
                item
            )

            for item
            in profile.preferred_skills

        ],

        "technologies": [

            skill_to_dict(
                item
            )

            for item
            in profile.technologies

        ],

        "education":
            profile.education,

        "certifications":
            profile.certifications,

        "experience":
            experience_to_dict(
                profile.experience
            ),

        "sections": [

            section_to_dict(
                item
            )

            for item
            in profile.sections

        ],

        "keywords":
            profile.keywords,

        "confidence":
            profile.confidence,

        "metadata":
            profile.metadata,

    }


# ============================================================
# PROFILE TO JSON
# ============================================================

def jd_profile_to_json(
    profile: JDProfile,
    indent: int = 2,
) -> str:

    return json.dumps(

        jd_profile_to_dict(
            profile
        ),

        indent=indent,

        ensure_ascii=False,

        default=str,

    )


# ============================================================
# SAVE PROFILE
# ============================================================

def save_jd_profile(
    profile: JDProfile,
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

        jd_profile_to_json(
            profile
        ),

        encoding="utf-8",

    )

    return path


# ============================================================
# GET REQUIRED SKILL NAMES
# ============================================================

def get_required_skill_names(
    profile: JDProfile,
) -> List[str]:

    return [

        skill.name

        for skill
        in profile.required_skills

    ]


# ============================================================
# GET PREFERRED SKILL NAMES
# ============================================================

def get_preferred_skill_names(
    profile: JDProfile,
) -> List[str]:

    return [

        skill.name

        for skill
        in profile.preferred_skills

    ]


# ============================================================
# GET ALL SKILL NAMES
# ============================================================

def get_all_skill_names(
    profile: JDProfile,
) -> List[str]:

    return deduplicate(

        get_required_skill_names(
            profile
        )

        +

        get_preferred_skill_names(
            profile
        )

        +

        [

            skill.name

            for skill
            in profile.technologies

        ]

    )


# ============================================================
# SKILL STATISTICS
# ============================================================

def skill_statistics(
    profile: JDProfile,
) -> Dict[str, Any]:

    required = profile.required_skills

    preferred = profile.preferred_skills

    technologies = profile.technologies

    categories = {}

    for skill in (

        required
        +
        preferred
        +
        technologies

    ):

        category = skill.category

        categories[
            category
        ] = (

            categories.get(
                category,
                0,
            )
            +
            1

        )

    return {

        "required_skills":
            len(required),

        "preferred_skills":
            len(preferred),

        "technologies":
            len(technologies),

        "total_unique_skills":
            len(
                get_all_skill_names(
                    profile
                )
            ),

        "categories":
            categories,

    }


# ============================================================
# JD SUMMARY
# ============================================================

def jd_summary(
    profile: JDProfile,
) -> Dict[str, Any]:

    return {

        "title":
            profile.title,

        "company":
            profile.company,

        "location":
            profile.location,

        "employment_type":
            profile.employment_type,

        "seniority":
            profile.seniority,

        "domain":
            profile.domain,

        "job_family":
            profile.job_family,

        "minimum_experience_years":
            profile.experience.minimum_years,

        "maximum_experience_years":
            profile.experience.maximum_years,

        "required_skill_count":
            len(
                profile.required_skills
            ),

        "preferred_skill_count":
            len(
                profile.preferred_skills
            ),

        "technology_count":
            len(
                profile.technologies
            ),

        "responsibility_count":
            len(
                profile.responsibilities
            ),

        "education_count":
            len(
                profile.education
            ),

        "certification_count":
            len(
                profile.certifications
            ),

        "parser_confidence":
            profile.confidence,

    }


# ============================================================
# REQUIREMENT MATRIX
# ============================================================

def requirement_matrix(
    profile: JDProfile,
) -> List[Dict[str, Any]]:

    rows = []

    for requirement in profile.requirements:

        rows.append({

            "requirement":
                requirement.text,

            "type":
                requirement.requirement_type,

            "category":
                requirement.category,

            "skill":
                requirement.skill,

            "years_experience":
                requirement.years_experience,

            "confidence":
                requirement.confidence,

            "priority":
                requirement.priority,

        })

    return rows


# ============================================================
# ANALYZE JD
# ============================================================

def analyze_jd(
    text: str,
    config: Optional[
        JDParserConfig
    ] = None,
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> JDProfile:

    parser = JDParser(
        config
    )

    return parser.parse(

        text,

        metadata,

    )


# ============================================================
# PARSE JD FILE
# ============================================================

def parse_jd_file(
    path: Union[
        str,
        Path,
    ],
    config: Optional[
        JDParserConfig
    ] = None,
) -> JDProfile:

    parser = JDParser(
        config
    )

    return parser.parse_file(
        path
    )


# ============================================================
# EXTRACT SKILLS FROM JD
# ============================================================

def extract_jd_skills(
    text: str,
) -> List[str]:

    profile = analyze_jd(
        text
    )

    return get_all_skill_names(
        profile
    )


# ============================================================
# EXTRACT REQUIRED SKILLS
# ============================================================

def extract_required_jd_skills(
    text: str,
) -> List[str]:

    profile = analyze_jd(
        text
    )

    return get_required_skill_names(
        profile
    )


# ============================================================
# EXTRACT PREFERRED SKILLS
# ============================================================

def extract_preferred_jd_skills(
    text: str,
) -> List[str]:

    profile = analyze_jd(
        text
    )

    return get_preferred_skill_names(
        profile
    )


# ============================================================
# PUBLIC CAPABILITIES
# ============================================================

JD_PARSER_CAPABILITIES = [

    "job_description_parsing",

    "section_detection",

    "title_extraction",

    "company_extraction",

    "location_extraction",

    "employment_type_detection",

    "seniority_detection",

    "experience_extraction",

    "education_extraction",

    "certification_extraction",

    "responsibility_extraction",

    "skill_extraction",

    "technology_extraction",

    "required_skill_detection",

    "preferred_skill_detection",

    "domain_detection",

    "job_family_detection",

    "keyword_extraction",

    "skill_normalization",

    "skill_alias_detection",

    "requirement_classification",

    "jd_profile_generation",

    "jd_json_export",

    "jd_batch_processing",

    "jd_file_processing",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "JD_PARSER_VERSION",

    # Models
    "JDSection",

    "JDRequirement",

    "JDSkill",

    "ExperienceRequirement",

    "JDProfile",

    "JDParserConfig",

    # Parser
    "JDParser",

    # Constants
    "SECTION_SUMMARY",

    "SECTION_RESPONSIBILITIES",

    "SECTION_REQUIREMENTS",

    "SECTION_REQUIRED_SKILLS",

    "SECTION_PREFERRED_SKILLS",

    "SECTION_TECHNOLOGIES",

    "SECTION_EDUCATION",

    "SECTION_EXPERIENCE",

    "SECTION_CERTIFICATIONS",

    "SECTION_BENEFITS",

    "SECTION_ABOUT_COMPANY",

    "SECTION_OTHER",

    "REQUIRED",

    "PREFERRED",

    "OPTIONAL",

    "UNKNOWN",

    "SENIORITY_INTERN",

    "SENIORITY_ENTRY",

    "SENIORITY_JUNIOR",

    "SENIORITY_MID",

    "SENIORITY_SENIOR",

    "SENIORITY_LEAD",

    "SENIORITY_PRINCIPAL",

    "SENIORITY_MANAGER",

    "SENIORITY_DIRECTOR",

    "SENIORITY_UNKNOWN",

    # Utilities
    "clean_text",

    "normalize_text",

    "normalize_name",

    "deduplicate",

    "clean_bullet",

    "extract_bullets",

    "extract_sentences",

    # Sections
    "identify_section_type",

    "looks_like_section_header",

    "split_into_sections",

    "merge_sections",

    # Metadata
    "extract_title",

    "extract_company",

    "extract_location",

    "extract_employment_type",

    "extract_summary",

    # Experience
    "extract_experience",

    "extract_seniority",

    "infer_seniority_from_years",

    "extract_experience_requirements",

    # Education
    "extract_education",

    "extract_certifications",

    "extract_education_requirements",

    # Skills
    "canonicalize_skill",

    "skill_category",

    "skill_aliases",

    "extract_known_skills",

    "extract_unknown_skill_candidates",

    "classify_requirement_type",

    "extract_requirements",

    "split_skill_requirements",

    "extract_technologies",

    # Domain
    "extract_domain",

    "extract_job_family",

    "extract_responsibilities",

    "extract_keywords",

    # Serialization
    "requirement_to_dict",

    "skill_to_dict",

    "section_to_dict",

    "experience_to_dict",

    "jd_profile_to_dict",

    "jd_profile_to_json",

    "save_jd_profile",

    # Analysis
    "get_required_skill_names",

    "get_preferred_skill_names",

    "get_all_skill_names",

    "skill_statistics",

    "jd_summary",

    "requirement_matrix",

    # Public API
    "analyze_jd",

    "parse_jd_file",

    "extract_jd_skills",

    "extract_required_jd_skills",

    "extract_preferred_jd_skills",

    "JD_PARSER_CAPABILITIES",

]


# ============================================================
# OPTIONAL COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    sample_jd = """

    Senior Generative AI Engineer

    About the Role

    We are looking for a Senior Generative AI Engineer
    to build production AI applications.

    Responsibilities

    - Design and develop LLM-powered applications.
    - Build Retrieval Augmented Generation pipelines.
    - Develop AI agents using LangChain and LangGraph.
    - Deploy applications on AWS.
    - Work with engineering teams to improve scalability.

    Requirements

    - 5+ years of software engineering experience.
    - Strong Python programming skills.
    - Experience with machine learning and deep learning.
    - Experience with Large Language Models.
    - Strong knowledge of RAG and vector databases.
    - Experience with Docker and Kubernetes.

    Preferred Skills

    - Experience with PyTorch.
    - Experience with Hugging Face.
    - Knowledge of MLOps.

    Education

    Bachelor's degree in Computer Science or related field.

    """

    profile = analyze_jd(
        sample_jd
    )

    print(
        json.dumps(
            jd_summary(
                profile
            ),
            indent=2,
        )
    )

    print(
        "\nRequired Skills:"
    )

    for skill in profile.required_skills:

        print(
            f"- {skill.name}"
        )

    print(
        "\nPreferred Skills:"
    )

    for skill in profile.preferred_skills:

        print(
            f"- {skill.name}"
        )


# ============================================================
# END OF industry/jd_parser.py
# ============================================================
