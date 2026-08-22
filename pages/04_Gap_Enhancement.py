# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 1/10
# LOAD INTELLIGENCE + INITIALIZE GAP ENHANCEMENT
# ============================================================

"""
AI Curriculum Platform
-----------------------

Page:
    04 - Gap & Enhancement

Purpose:
    Convert Industry/JD Intelligence into an actionable
    curriculum enhancement plan.

Previous Page:
    03_💼_Industry_JD_Intelligence.py

Main Inputs:
    - JD Intelligence
    - Curriculum Intelligence
    - Skill Matching
    - Gap Analysis
    - RAG + LLM Analysis
    - Multi-Agent Analysis
    - Final Enhancement Recommendations

Main Outputs:
    - Prioritized Gaps
    - Module Enhancements
    - Concepts to Add
    - Tools to Add
    - Technologies to Add
    - Projects to Add
    - Learning Outcomes
    - Enhanced Curriculum
    - Implementation Roadmap
"""


# ============================================================
# 1. IMPORTS
# ============================================================

import os
import re
import json
from datetime import datetime
from typing import Any, Dict, List, Optional


import pandas as pd
import streamlit as st


# ============================================================
# 2. PAGE CONFIGURATION
# ============================================================

st.set_page_config(

    page_title=(
        "Gap & Curriculum Enhancement"
    ),

    page_icon="🔍",

    layout="wide",

    initial_sidebar_state="expanded",

)


# ============================================================
# 3. COMMON HELPER FUNCTIONS
# ============================================================

def safe_text(
    value: Any,
    default: str = "",
) -> str:
    """
    Safely convert any value into text.
    """

    if value is None:

        return default


    if isinstance(
        value,
        str,
    ):

        return value.strip()


    try:

        return str(
            value
        ).strip()

    except Exception:

        return default


# ------------------------------------------------------------
# Normalize list
# ------------------------------------------------------------

def normalize_list(
    value: Any,
) -> List[str]:
    """
    Convert different input formats into a clean list.
    """

    if value is None:

        return []


    if isinstance(
        value,
        str,
    ):

        value = value.strip()


        if not value:

            return []


        return [
            value
        ]


    if isinstance(
        value,
        tuple,
    ):

        value = list(
            value
        )


    if not isinstance(
        value,
        list,
    ):

        return [
            safe_text(
                value
            )
        ]


    result = []


    for item in value:

        if isinstance(
            item,
            dict,
        ):

            item_text = (

                item.get(
                    "name"
                )

                or

                item.get(
                    "title"
                )

                or

                item.get(
                    "skill"
                )

                or

                item.get(
                    "item"
                )

                or

                item.get(
                    "concept"
                )

            )

        else:

            item_text = item


        item_text = safe_text(
            item_text
        )


        if item_text:

            result.append(
                item_text
            )


    return result


# ------------------------------------------------------------
# Unique values
# ------------------------------------------------------------

def unique_values(
    values: List[str],
) -> List[str]:
    """
    Remove duplicates while preserving order.
    """

    result = []

    seen = set()


    for value in values:

        normalized = safe_text(
            value
        )


        if not normalized:

            continue


        key = normalized.lower()


        if key in seen:

            continue


        seen.add(
            key
        )


        result.append(
            normalized
        )


    return result


# ------------------------------------------------------------
# Safe numeric
# ------------------------------------------------------------

def safe_number(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert value to float.
    """

    try:

        return float(
            value
        )

    except Exception:

        return default


# ------------------------------------------------------------
# JSON serializer
# ------------------------------------------------------------

def serialize_json(
    data: Any,
) -> str:
    """
    Serialize Python objects for downloads.
    """

    try:

        return json.dumps(

            data,

            indent=2,

            ensure_ascii=False,

            default=str,

        )

    except Exception:

        return json.dumps(

            {
                "error":
                    "Unable to serialize data."
            },

            indent=2,

        )


# ============================================================
# 4. PAGE HEADER
# ============================================================

st.title(
    "🔍 Gap & Curriculum Enhancement"
)

st.markdown(
    """
### Convert Industry Intelligence into Curriculum Action

This module takes the results from **Industry & JD
Intelligence** and determines:

- What is missing?
- What should be enhanced?
- What should be added?
- What should be reduced?
- Which tools should be introduced?
- Which concepts need deeper coverage?
- Which projects should be added?
- Which modules should change?
- What should be prioritized first?
"""
)


# ============================================================
# 5. ARCHITECTURE DISPLAY
# ============================================================

with st.expander(
    "🔎 View Gap & Enhancement Workflow",
    expanded=False,
):

    st.code(
        """
Industry / JD Intelligence
            │
            ▼
       Gap Analysis
            │
            ▼
    Gap Classification
            │
            ▼
    Priority Assessment
            │
            ▼
      Expert Agent
            │
            ▼
      Critic Agent
            │
            ▼
   Final Enhancement Agent
            │
            ▼
     Enhanced Curriculum
            │
     ┌──────┼──────┐
     ▼      ▼      ▼
  Concepts Tools Projects
     │      │      │
     └──────┼──────┘
            ▼
     Implementation
        Roadmap
        """,
        language="text",
    )


# ============================================================
# 6. LOAD PAGE 03 MASTER PACKAGE
# ============================================================

industry_package = st.session_state.get(
    "industry_intelligence_package"
)


# ============================================================
# 7. LOAD INDIVIDUAL OBJECTS
# ============================================================

industry_report_data = st.session_state.get(
    "industry_report_data",
    {}
)


gap_report_data = st.session_state.get(
    "gap_report_data",
    {}
)


enhancement_report_data = st.session_state.get(
    "enhancement_report_data",
    {}
)


# ------------------------------------------------------------
# JD intelligence
# ------------------------------------------------------------

jd_skill_intelligence = st.session_state.get(
    "jd_skill_intelligence",
    {}
)


# ------------------------------------------------------------
# Curriculum intelligence
# ------------------------------------------------------------

curriculum_skill_intelligence = st.session_state.get(
    "curriculum_skill_intelligence",
    {}
)


# ------------------------------------------------------------
# Skill matching
# ------------------------------------------------------------

skill_match_results = st.session_state.get(
    "skill_match_results",
    []
)


skill_match_summary = st.session_state.get(
    "skill_match_summary",
    {}
)


# ------------------------------------------------------------
# Gap analysis
# ------------------------------------------------------------

industry_gap_analysis = st.session_state.get(
    "industry_gap_analysis",
    {}
)


# ------------------------------------------------------------
# LLM analysis
# ------------------------------------------------------------

llm_gap_analysis = st.session_state.get(
    "llm_gap_analysis",
    {}
)


industry_recommendations = st.session_state.get(
    "industry_recommendations",
    []
)


# ------------------------------------------------------------
# Agent outputs
# ------------------------------------------------------------

agent_gap_analysis = st.session_state.get(
    "agent_gap_analysis"
)


agent_industry_analysis = st.session_state.get(
    "agent_industry_analysis"
)


agent_curriculum_analysis = st.session_state.get(
    "agent_curriculum_analysis"
)


agent_project_analysis = st.session_state.get(
    "agent_project_analysis"
)


agent_critic_analysis = st.session_state.get(
    "agent_critic_analysis"
)


# ------------------------------------------------------------
# Final enhancement
# ------------------------------------------------------------

final_curriculum_enhancement = st.session_state.get(
    "final_curriculum_enhancement"
)


# ============================================================
# 8. RECOVER DATA FROM MASTER PACKAGE
# ============================================================

"""
If the individual session-state objects are unavailable but
the master package exists, recover them from the package.
"""

if industry_package:

    # --------------------------------------------------------
    # JD intelligence
    # --------------------------------------------------------

    if not jd_skill_intelligence:

        jd_skill_intelligence = (
            industry_package.get(
                "jd_intelligence",
                {}
            )
        )


    # --------------------------------------------------------
    # Curriculum intelligence
    # --------------------------------------------------------

    if not curriculum_skill_intelligence:

        curriculum_skill_intelligence = (
            industry_package.get(
                "curriculum_intelligence",
                {}
            )
        )


    # --------------------------------------------------------
    # Skill matching
    # --------------------------------------------------------

    if not skill_match_results:

        matching = industry_package.get(
            "skill_matching",
            {}
        )


        if isinstance(
            matching,
            dict,
        ):

            skill_match_results = (
                matching.get(
                    "results",
                    []
                )
            )


            skill_match_summary = (
                matching.get(
                    "summary",
                    {}
                )
            )


    # --------------------------------------------------------
    # Gap analysis
    # --------------------------------------------------------

    if not industry_gap_analysis:

        industry_gap_analysis = (
            industry_package.get(
                "gap_analysis",
                {}
            )
        )


    # --------------------------------------------------------
    # LLM analysis
    # --------------------------------------------------------

    if not llm_gap_analysis:

        llm_gap_analysis = (
            industry_package.get(
                "llm_industry_analysis",
                {}
            )
        )


    # --------------------------------------------------------
    # Final enhancement
    # --------------------------------------------------------

    if not final_curriculum_enhancement:

        final_curriculum_enhancement = (
            industry_package.get(
                "final_curriculum_enhancement",
                {}
            )
        )


    # --------------------------------------------------------
    # Agent outputs
    # --------------------------------------------------------

    multi_agent_data = (
        industry_package.get(
            "multi_agent_analysis",
            {}
        )
    )


    if isinstance(
        multi_agent_data,
        dict,
    ):

        if not agent_gap_analysis:

            agent_gap_analysis = (
                multi_agent_data.get(
                    "gap_agent"
                )
            )


        if not agent_industry_analysis:

            agent_industry_analysis = (
                multi_agent_data.get(
                    "industry_agent"
                )
            )


        if not agent_curriculum_analysis:

            agent_curriculum_analysis = (
                multi_agent_data.get(
                    "curriculum_agent"
                )
            )


        if not agent_project_analysis:

            agent_project_analysis = (
                multi_agent_data.get(
                    "project_agent"
                )
            )


        if not agent_critic_analysis:

            agent_critic_analysis = (
                multi_agent_data.get(
                    "critic_agent"
                )
            )


# ============================================================
# 9. VALIDATE INPUTS
# ============================================================

has_industry_analysis = bool(
    industry_gap_analysis
    or
    gap_report_data
)


has_curriculum_analysis = bool(
    curriculum_skill_intelligence
)


has_matching_analysis = bool(
    skill_match_results
)


has_ai_analysis = bool(
    llm_gap_analysis
    or
    industry_recommendations
)


has_agent_analysis = bool(
    final_curriculum_enhancement
    or
    agent_critic_analysis
)


# ============================================================
# 10. INPUT STATUS
# ============================================================

st.subheader(
    "📋 Analysis Input Status"
)


status_columns = st.columns(
    6
)


input_status = [

    (
        "JD Intelligence",
        bool(
            jd_skill_intelligence
        ),
    ),

    (
        "Curriculum",
        has_curriculum_analysis,
    ),

    (
        "Skill Matching",
        has_matching_analysis,
    ),

    (
        "Gap Analysis",
        has_industry_analysis,
    ),

    (
        "AI Analysis",
        has_ai_analysis,
    ),

    (
        "Agent Analysis",
        has_agent_analysis,
    ),

]


for column, (
    label,
    available,
) in zip(
    status_columns,
    input_status,
):

    with column:

        if available:

            st.success(
                f"✅ {label}"
            )

        else:

            st.warning(
                f"⏳ {label}"
            )


# ============================================================
# 11. HARD VALIDATION
# ============================================================

if not has_industry_analysis:

    st.error(
        """
        ❌ Industry Gap Analysis is not available.

        Please complete:

        **03_💼_Industry_JD_Intelligence.py**

        before using this page.
        """
    )


    st.stop()


# ============================================================
# 12. BUILD CONSOLIDATED GAP LIST
# ============================================================

def get_all_gaps(
    gap_analysis: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Return all normalized gaps.
    """

    if not gap_analysis:

        return []


    gaps = gap_analysis.get(
        "gaps",
        []
    )


    if not isinstance(
        gaps,
        list,
    ):

        return []


    normalized = []


    for gap in gaps:

        if not isinstance(
            gap,
            dict,
        ):

            continue


        normalized.append({

            "jd_skill":
                safe_text(
                    gap.get(
                        "jd_skill"
                    )
                ),

            "curriculum_match":
                safe_text(
                    gap.get(
                        "curriculum_match"
                    )
                ),

            "status":
                safe_text(
                    gap.get(
                        "status"
                    )
                ),

            "priority":
                safe_text(
                    gap.get(
                        "priority"
                    ),
                    "required",
                ),

            "severity":
                safe_text(
                    gap.get(
                        "severity"
                    ),
                    "medium",
                ),

            "gap_type":
                safe_text(
                    gap.get(
                        "gap_type"
                    ),
                    "General Skill Gap",
                ),

            "gap_category":
                safe_text(
                    gap.get(
                        "gap_category"
                    ),
                    "Other",
                ),

            "confidence":
                safe_number(
                    gap.get(
                        "confidence",
                        0,
                    )
                ),

            "gap_score":
                safe_number(
                    gap.get(
                        "gap_score",
                        0,
                    )
                ),

            "weighted_gap_score":
                safe_number(
                    gap.get(
                        "weighted_gap_score",
                        0,
                    )
                ),

            "module":
                safe_text(
                    gap.get(
                        "module"
                    )
                ),

            "topic":
                safe_text(
                    gap.get(
                        "topic"
                    )
                ),

        })


    return normalized


# ============================================================
# 13. BUILD CONSOLIDATED DATA
# ============================================================

all_gaps = get_all_gaps(
    industry_gap_analysis
)


# ============================================================
# 14. SORT GAPS
# ============================================================

severity_order = {

    "critical": 4,

    "high": 3,

    "medium": 2,

    "low": 1,

}


all_gaps = sorted(

    all_gaps,

    key=lambda gap:

        (

            severity_order.get(

                gap.get(
                    "severity",
                    "low"
                ),

                0,

            ),

            safe_number(
                gap.get(
                    "weighted_gap_score",
                    0,
                )
            ),

        ),

    reverse=True,

)


# ============================================================
# 15. SAVE CONSOLIDATED GAPS
# ============================================================

st.session_state[
    "enhancement_gaps"
] = all_gaps


# ============================================================
# 16. GAP METRICS
# ============================================================

critical_count = len([

    gap

    for gap in all_gaps

    if gap.get(
        "severity"
    ) == "critical"

])


high_count = len([

    gap

    for gap in all_gaps

    if gap.get(
        "severity"
    ) == "high"

])


medium_count = len([

    gap

    for gap in all_gaps

    if gap.get(
        "severity"
    ) == "medium"

])


low_count = len([

    gap

    for gap in all_gaps

    if gap.get(
        "severity"
    ) == "low"

])


missing_count = len([

    gap

    for gap in all_gaps

    if gap.get(
        "status"
    ) == "missing"

])


partial_count = len([

    gap

    for gap in all_gaps

    if gap.get(
        "status"
    ) == "partial"

])


# ============================================================
# 17. GAP DASHBOARD
# ============================================================

st.divider()

st.subheader(
    "📊 Curriculum Gap Dashboard"
)


metric_columns = st.columns(
    6
)


with metric_columns[0]:

    st.metric(
        "Total Gaps",
        len(
            all_gaps
        ),
    )


with metric_columns[1]:

    st.metric(
        "🔴 Critical",
        critical_count,
    )


with metric_columns[2]:

    st.metric(
        "🟠 High",
        high_count,
    )


with metric_columns[3]:

    st.metric(
        "🟡 Medium",
        medium_count,
    )


with metric_columns[4]:

    st.metric(
        "❌ Missing",
        missing_count,
    )


with metric_columns[5]:

    st.metric(
        "⚠️ Partial",
        partial_count,
    )


# ============================================================
# 18. GAP TABLE
# ============================================================

if all_gaps:

    st.markdown(
        "### 🔍 Consolidated Gap List"
    )


    gap_rows = []


    for gap in all_gaps:

        severity = gap.get(
            "severity"
        )


        if severity == "critical":

            severity_label = "🔴 Critical"

        elif severity == "high":

            severity_label = "🟠 High"

        elif severity == "medium":

            severity_label = "🟡 Medium"

        else:

            severity_label = "🔵 Low"


        status = gap.get(
            "status"
        )


        if status == "missing":

            status_label = "❌ Missing"

        elif status == "partial":

            status_label = "⚠️ Partial"

        else:

            status_label = "✅ Covered"


        gap_rows.append({

            "JD Requirement":
                gap.get(
                    "jd_skill"
                ),

            "Status":
                status_label,

            "Priority":
                gap.get(
                    "priority"
                ),

            "Severity":
                severity_label,

            "Gap Type":
                gap.get(
                    "gap_type"
                ),

            "Current Coverage":
                gap.get(
                    "curriculum_match"
                )
                or
                "None identified",

            "Module":
                gap.get(
                    "module"
                )
                or
                "Not mapped",

            "Gap Score":
                f"""
                {
                    gap.get(
                        "gap_score",
                        0
                    )
                }%
                """,

        })


    st.dataframe(

        pd.DataFrame(
            gap_rows
        ),

        use_container_width=True,

        hide_index=True,

    )


# ============================================================
# 19. SAVE PAGE METADATA
# ============================================================

enhancement_metadata = {

    "page":
        "04_Gap_Enhancement",

    "generated_at":
        datetime.now().isoformat(),

    "total_gaps":
        len(
            all_gaps
        ),

    "critical_gaps":
        critical_count,

    "high_gaps":
        high_count,

    "medium_gaps":
        medium_count,

    "low_gaps":
        low_count,

    "missing_gaps":
        missing_count,

    "partial_gaps":
        partial_count,

    "industry_alignment_score":
        safe_number(
            industry_gap_analysis.get(
                "curriculum_alignment_score",
                0,
            )
        ),

}


st.session_state[
    "enhancement_metadata"
] = enhancement_metadata


# ============================================================
# 20. CURRENT STATE SUMMARY
# ============================================================

with st.expander(
    "🧩 View Loaded Intelligence",
    expanded=False,
):

    st.write(
        "JD Skills:",
        len(
            normalize_list(
                jd_skill_intelligence.get(
                    "required_skills"
                )
            )
        ),
    )


    st.write(
        "Curriculum Skills:",
        len(
            normalize_list(
                curriculum_skill_intelligence.get(
                    "all_skills"
                )
            )
        ),
    )


    st.write(
        "Matched Skills:",
        len(
            skill_match_results
        ),
    )


    st.write(
        "Industry Gaps:",
        len(
            all_gaps
        ),
    )


    st.write(
        "AI Recommendations:",
        len(
            industry_recommendations
        ),
    )


    st.write(
        "Final Enhancement Available:",
        bool(
            final_curriculum_enhancement
        ),
    )


# ============================================================
# 21. INITIALIZE ENHANCEMENT STATE
# ============================================================

if "enhancement_analysis" not in st.session_state:

    st.session_state[
        "enhancement_analysis"
    ] = {}


if "enhanced_curriculum" not in st.session_state:

    st.session_state[
        "enhanced_curriculum"
    ] = []


if "enhancement_roadmap" not in st.session_state:

    st.session_state[
        "enhancement_roadmap"
    ] = []


if "enhancement_projects" not in st.session_state:

    st.session_state[
        "enhancement_projects"
    ] = []


# ============================================================
# 22. READY STATUS
# ============================================================

st.divider()

if all_gaps:

    st.success(
        f"""
        ✅ **Gap Enhancement Engine Ready**

        {len(all_gaps)} curriculum-industry gaps have been
        loaded and prioritized.

        The next stages will convert these gaps into
        module-level curriculum enhancements.
        """
    )

else:

    st.warning(
        """
        ⚠️ No curriculum-industry gaps were identified.

        The existing curriculum may already have strong
        alignment with the supplied JD.
        """
    )


# ============================================================
# END OF CHUNK 1/10
# ============================================================
# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 2/10
# INTELLIGENT GAP PRIORITIZATION
# ============================================================

"""
Purpose
-------
Convert raw curriculum-industry gaps into an actionable
Enhancement Priority Matrix.

Input
-----

st.session_state["enhancement_gaps"]

Output
------

st.session_state["prioritized_gaps"]

st.session_state["enhancement_priority_matrix"]

st.session_state["gap_priority_summary"]

Priority factors
----------------

1. JD Priority
2. Gap Severity
3. Gap Status
4. Industry Importance
5. Employability Impact
6. Curriculum Impact
7. Implementation Effort
8. Curriculum Relevance

Decision
--------

Each gap receives:

    Priority Score
    Priority Level
    Recommended Action

Recommended actions:

    ADD
    ENHANCE
    MERGE
    NEW MODULE
    OPTIONAL
"""


# ============================================================
# 1. LOAD GAPS
# ============================================================

enhancement_gaps = st.session_state.get(
    "enhancement_gaps",
    []
)


# ============================================================
# 2. VALIDATION
# ============================================================

if not enhancement_gaps:

    st.warning(
        """
        ⚠️ No enhancement gaps are currently available.

        Complete Chunk 1 before continuing.
        """
    )


# ============================================================
# 3. SCORING CONFIGURATION
# ============================================================

"""
Weights are intentionally transparent.

Users can later tune these values or move them into
configuration.yaml.
"""

PRIORITY_WEIGHTS = {

    "jd_priority": 0.20,

    "severity": 0.20,

    "gap_status": 0.15,

    "industry_importance": 0.15,

    "employability": 0.15,

    "curriculum_impact": 0.10,

    "implementation_feasibility": 0.05,

}


# ============================================================
# 4. SCORE MAPPINGS
# ============================================================

JD_PRIORITY_SCORE = {

    "required": 100,

    "mandatory": 100,

    "preferred": 60,

    "optional": 30,

}


SEVERITY_SCORE = {

    "critical": 100,

    "high": 85,

    "medium": 65,

    "low": 40,

}


STATUS_SCORE = {

    "missing": 100,

    "partial": 70,

    "covered": 0,

}


INDUSTRY_IMPORTANCE_SCORE = {

    "critical": 100,

    "high": 85,

    "medium": 65,

    "low": 40,

}


# ============================================================
# 5. CATEGORY IMPORTANCE
# ============================================================

CATEGORY_IMPORTANCE = {

    "AI / Machine Learning": 95,

    "Programming Language": 95,

    "Framework": 90,

    "Cloud": 90,

    "DevOps / MLOps": 90,

    "Database": 85,

    "Data / Analytics": 90,

    "Business Intelligence": 80,

    "Tool": 75,

    "Engineering Skill Gap": 85,

    "Concept / AI Skill Gap": 90,

    "General Skill Gap": 70,

    "Other": 50,

}


# ============================================================
# 6. CALCULATE EMPLOYABILITY SCORE
# ============================================================

def calculate_employability_score(
    gap,
):
    """
    Estimate how strongly the gap can affect employability.

    This is a deterministic baseline.

    Later, the Industry Expert Agent can override/refine it.
    """

    priority = safe_text(
        gap.get(
            "priority"
        ),
        "required",
    ).lower()


    severity = safe_text(
        gap.get(
            "severity"
        ),
        "medium",
    ).lower()


    gap_type = safe_text(
        gap.get(
            "gap_type"
        ),
        "General Skill Gap",
    )


    score = 50.0


    # --------------------------------------------------------
    # Required JD skills
    # --------------------------------------------------------

    if priority in {
        "required",
        "mandatory",
    }:

        score += 25


    elif priority == "preferred":

        score += 10


    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    if severity == "critical":

        score += 20

    elif severity == "high":

        score += 15

    elif severity == "medium":

        score += 8


    # --------------------------------------------------------
    # Skill categories
    # --------------------------------------------------------

    if gap_type in {

        "Programming Language Gap",

        "Framework Gap",

        "Cloud Technology Gap",

        "DevOps / MLOps Gap",

        "Concept / AI Skill Gap",

    }:

        score += 10


    return min(
        100.0,
        score,
    )


# ============================================================
# 7. CALCULATE CURRICULUM IMPACT
# ============================================================

def calculate_curriculum_impact(
    gap,
):
    """
    Estimate how important the gap is to curriculum quality.
    """

    gap_type = safe_text(
        gap.get(
            "gap_type"
        ),
        "General Skill Gap",
    )


    severity = safe_text(
        gap.get(
            "severity"
        ),
        "medium",
    )


    category_score = CATEGORY_IMPORTANCE.get(

        safe_text(
            gap.get(
                "gap_category"
            ),
            "Other",
        ),

        50,

    )


    severity_score = SEVERITY_SCORE.get(

        severity,

        50,

    )


    score = (

        category_score
        * 0.60

        +

        severity_score
        * 0.40

    )


    return round(
        score,
        2,
    )


# ============================================================
# 8. CALCULATE IMPLEMENTATION FEASIBILITY
# ============================================================

def calculate_implementation_feasibility(
    gap,
):
    """
    Estimate how easy it is to incorporate the requirement.

    Higher score = easier to implement.
    """

    gap_type = safe_text(
        gap.get(
            "gap_type"
        ),
        "General Skill Gap",
    )


    module = safe_text(
        gap.get(
            "module"
        )
    )


    status = safe_text(
        gap.get(
            "status"
        ),
        "missing",
    )


    # --------------------------------------------------------
    # Partial coverage is generally easier to enhance
    # --------------------------------------------------------

    if status == "partial":

        base = 85

    else:

        base = 60


    # --------------------------------------------------------
    # Existing module mapping increases feasibility
    # --------------------------------------------------------

    if module:

        base += 10


    # --------------------------------------------------------
    # New infrastructure-heavy areas
    # --------------------------------------------------------

    if gap_type in {

        "Cloud Technology Gap",

        "DevOps / MLOps Gap",

    }:

        base -= 10


    return max(
        0,
        min(
            100,
            base,
        ),
    )


# ============================================================
# 9. CALCULATE INDUSTRY IMPORTANCE
# ============================================================

def calculate_industry_importance(
    gap,
):
    """
    Calculate industry importance using category + severity.
    """

    category = safe_text(
        gap.get(
            "gap_category"
        ),
        "Other",
    )


    severity = safe_text(
        gap.get(
            "severity"
        ),
        "medium",
    )


    category_score = CATEGORY_IMPORTANCE.get(

        category,

        50,

    )


    severity_score = SEVERITY_SCORE.get(

        severity,

        50,

    )


    return round(

        (
            category_score
            * 0.55
        )

        +

        (
            severity_score
            * 0.45
        ),

        2,

    )


# ============================================================
# 10. CALCULATE GAP STATUS SCORE
# ============================================================

def calculate_gap_status_score(
    gap,
):
    """
    Score missing skills higher than partial skills.
    """

    return STATUS_SCORE.get(

        safe_text(
            gap.get(
                "status"
            ),
            "missing",
        ).lower(),

        50,

    )


# ============================================================
# 11. CALCULATE PRIORITY SCORE
# ============================================================

def calculate_priority_score(
    gap,
):
    """
    Calculate transparent weighted priority score.
    """

    jd_priority = JD_PRIORITY_SCORE.get(

        safe_text(
            gap.get(
                "priority"
            ),
            "required",
        ).lower(),

        50,

    )


    severity = SEVERITY_SCORE.get(

        safe_text(
            gap.get(
                "severity"
            ),
            "medium",
        ).lower(),

        50,

    )


    status = calculate_gap_status_score(
        gap
    )


    industry = calculate_industry_importance(
        gap
    )


    employability = calculate_employability_score(
        gap
    )


    curriculum_impact = calculate_curriculum_impact(
        gap
    )


    feasibility = calculate_implementation_feasibility(
        gap
    )


    score = (

        jd_priority
        *
        PRIORITY_WEIGHTS[
            "jd_priority"
        ]

        +

        severity
        *
        PRIORITY_WEIGHTS[
            "severity"
        ]

        +

        status
        *
        PRIORITY_WEIGHTS[
            "gap_status"
        ]

        +

        industry
        *
        PRIORITY_WEIGHTS[
            "industry_importance"
        ]

        +

        employability
        *
        PRIORITY_WEIGHTS[
            "employability"
        ]

        +

        curriculum_impact
        *
        PRIORITY_WEIGHTS[
            "curriculum_impact"
        ]

        +

        feasibility
        *
        PRIORITY_WEIGHTS[
            "implementation_feasibility"
        ]

    )


    return round(
        score,
        2,
    )


# ============================================================
# 12. DETERMINE PRIORITY LEVEL
# ============================================================

def determine_priority_level(
    score,
):
    """
    Convert numerical score into action priority.
    """

    if score >= 85:

        return "P0 - Critical"

    if score >= 75:

        return "P1 - High"

    if score >= 60:

        return "P2 - Medium"

    return "P3 - Low"


# ============================================================
# 13. DETERMINE RECOMMENDED ACTION
# ============================================================

def determine_recommended_action(
    gap,
    priority_score,
):
    """
    Determine what should happen to the curriculum.
    """

    status = safe_text(
        gap.get(
            "status"
        ),
        "missing",
    ).lower()


    severity = safe_text(
        gap.get(
            "severity"
        ),
        "medium",
    ).lower()


    module = safe_text(
        gap.get(
            "module"
        )
    )


    gap_type = safe_text(
        gap.get(
            "gap_type"
        )
    )


    # --------------------------------------------------------
    # Critical missing requirement
    # --------------------------------------------------------

    if (
        status == "missing"
        and
        severity == "critical"
    ):

        if module:

            return "ENHANCE EXISTING MODULE"

        return "ADD / CREATE MODULE"


    # --------------------------------------------------------
    # High missing requirement
    # --------------------------------------------------------

    if (
        status == "missing"
        and
        priority_score >= 75
    ):

        if module:

            return "ENHANCE EXISTING MODULE"

        return "ADD"


    # --------------------------------------------------------
    # Partial coverage
    # --------------------------------------------------------

    if status == "partial":

        return "DEEPEN EXISTING COVERAGE"


    # --------------------------------------------------------
    # Technology/tool related
    # --------------------------------------------------------

    if gap_type in {

        "Tool Gap",

        "Framework Gap",

    }:

        return "ADD PRACTICAL EXPOSURE"


    # --------------------------------------------------------
    # Cloud / DevOps
    # --------------------------------------------------------

    if gap_type in {

        "Cloud Technology Gap",

        "DevOps / MLOps Gap",

    }:

        return "ADD HANDS-ON MODULE"


    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------

    if priority_score >= 60:

        return "ENHANCE"


    return "OPTIONAL"


# ============================================================
# 14. BUILD PRIORITIZED GAP RECORD
# ============================================================

def build_prioritized_gap(
    gap,
):
    """
    Add scoring and action information to each gap.
    """

    priority_score = calculate_priority_score(
        gap
    )


    priority_level = determine_priority_level(
        priority_score
    )


    action = determine_recommended_action(

        gap,

        priority_score,

    )


    employability = calculate_employability_score(
        gap
    )


    curriculum_impact = calculate_curriculum_impact(
        gap
    )


    industry_importance = calculate_industry_importance(
        gap
    )


    feasibility = calculate_implementation_feasibility(
        gap
    )


    result = dict(
        gap
    )


    result.update({

        "priority_score":
            priority_score,

        "priority_level":
            priority_level,

        "recommended_action":
            action,

        "employability_score":
            employability,

        "curriculum_impact_score":
            curriculum_impact,

        "industry_importance_score":
            industry_importance,

        "implementation_feasibility_score":
            feasibility,

    })


    return result


# ============================================================
# 15. GENERATE PRIORITIZED GAPS
# ============================================================

prioritized_gaps = [

    build_prioritized_gap(
        gap
    )

    for gap in enhancement_gaps

]


# ============================================================
# 16. SORT BY PRIORITY
# ============================================================

prioritized_gaps = sorted(

    prioritized_gaps,

    key=lambda item:

        safe_number(

            item.get(
                "priority_score",
                0,
            )

        ),

    reverse=True,

)


# ============================================================
# 17. ASSIGN RANK
# ============================================================

for index, gap in enumerate(

    prioritized_gaps,

    start=1,

):

    gap[
        "priority_rank"
    ] = index


# ============================================================
# 18. SAVE PRIORITIZED GAPS
# ============================================================

st.session_state[
    "prioritized_gaps"
] = prioritized_gaps


# ============================================================
# 19. BUILD PRIORITY MATRIX
# ============================================================

priority_matrix_rows = []


for gap in prioritized_gaps:

    priority_matrix_rows.append({

        "Rank":
            gap.get(
                "priority_rank"
            ),

        "JD Skill":
            gap.get(
                "jd_skill"
            ),

        "Status":
            gap.get(
                "status"
            ),

        "JD Priority":
            gap.get(
                "priority"
            ),

        "Severity":
            gap.get(
                "severity"
            ),

        "Priority Score":
            gap.get(
                "priority_score"
            ),

        "Priority":
            gap.get(
                "priority_level"
            ),

        "Recommended Action":
            gap.get(
                "recommended_action"
            ),

        "Employability":
            gap.get(
                "employability_score"
            ),

        "Industry Impact":
            gap.get(
                "industry_importance_score"
            ),

        "Curriculum Impact":
            gap.get(
                "curriculum_impact_score"
            ),

        "Feasibility":
            gap.get(
                "implementation_feasibility_score"
            ),

    })


priority_matrix_df = pd.DataFrame(
    priority_matrix_rows
)


st.session_state[
    "enhancement_priority_matrix"
] = priority_matrix_df


# ============================================================
# 20. PRIORITY SUMMARY
# ============================================================

priority_summary = {

    "P0 - Critical":
        len([

            gap

            for gap in prioritized_gaps

            if gap.get(
                "priority_level"
            )
            ==
            "P0 - Critical"

        ]),

    "P1 - High":
        len([

            gap

            for gap in prioritized_gaps

            if gap.get(
                "priority_level"
            )
            ==
            "P1 - High"

        ]),

    "P2 - Medium":
        len([

            gap

            for gap in prioritized_gaps

            if gap.get(
                "priority_level"
            )
            ==
            "P2 - Medium"

        ]),

    "P3 - Low":
        len([

            gap

            for gap in prioritized_gaps

            if gap.get(
                "priority_level"
            )
            ==
            "P3 - Low"

        ]),

}


st.session_state[
    "gap_priority_summary"
] = priority_summary


# ============================================================
# 21. DISPLAY PRIORITY DASHBOARD
# ============================================================

st.divider()

st.subheader(
    "🎯 Enhancement Priority Matrix"
)


priority_cols = st.columns(
    4
)


with priority_cols[0]:

    st.metric(

        "🔴 P0 Critical",

        priority_summary[
            "P0 - Critical"
        ],

    )


with priority_cols[1]:

    st.metric(

        "🟠 P1 High",

        priority_summary[
            "P1 - High"
        ],

    )


with priority_cols[2]:

    st.metric(

        "🟡 P2 Medium",

        priority_summary[
            "P2 - Medium"
        ],

    )


with priority_cols[3]:

    st.metric(

        "🔵 P3 Low",

        priority_summary[
            "P3 - Low"
        ],

    )


# ============================================================
# 22. DISPLAY PRIORITY TABLE
# ============================================================

if not priority_matrix_df.empty:

    st.dataframe(

        priority_matrix_df,

        use_container_width=True,

        hide_index=True,

        column_config={

            "Priority Score":
                st.column_config.ProgressColumn(

                    "Priority Score",

                    min_value=0,

                    max_value=100,

                    format="%.1f",

                ),

            "Employability":
                st.column_config.ProgressColumn(

                    "Employability",

                    min_value=0,

                    max_value=100,

                    format="%.1f",

                ),

            "Industry Impact":
                st.column_config.ProgressColumn(

                    "Industry Impact",

                    min_value=0,

                    max_value=100,

                    format="%.1f",

                ),

            "Curriculum Impact":
                st.column_config.ProgressColumn(

                    "Curriculum Impact",

                    min_value=0,

                    max_value=100,

                    format="%.1f",

                ),

            "Feasibility":
                st.column_config.ProgressColumn(

                    "Feasibility",

                    min_value=0,

                    max_value=100,

                    format="%.1f",

                ),

        },

    )


# ============================================================
# 23. PRIORITY VISUALIZATION
# ============================================================

if not priority_matrix_df.empty:

    st.markdown(
        "### 📈 Gap Priority Distribution"
    )


    chart_data = pd.DataFrame({

        "Priority": [

            "P0 Critical",

            "P1 High",

            "P2 Medium",

            "P3 Low",

        ],

        "Gaps": [

            priority_summary[
                "P0 - Critical"
            ],

            priority_summary[
                "P1 - High"
            ],

            priority_summary[
                "P2 - Medium"
            ],

            priority_summary[
                "P3 - Low"
            ],

        ],

    })


    st.bar_chart(

        chart_data.set_index(
            "Priority"
        )

    )


# ============================================================
# 24. TOP 10 ENHANCEMENT PRIORITIES
# ============================================================

if prioritized_gaps:

    st.divider()

    st.subheader(
        "🔥 Top Enhancement Priorities"
    )


    top_gaps = prioritized_gaps[
        :10
    ]


    for gap in top_gaps:

        priority = gap.get(
            "priority_level"
        )


        if priority.startswith(
            "P0"
        ):

            icon = "🔴"

        elif priority.startswith(
            "P1"
        ):

            icon = "🟠"

        elif priority.startswith(
            "P2"
        ):

            icon = "🟡"

        else:

            icon = "🔵"


        with st.expander(

            f"""
            {icon}
            #{gap.get("priority_rank")}
            {gap.get("jd_skill")}
            — {gap.get("priority_score")}/100
            """,

            expanded=False,

        ):

            detail_col1, detail_col2 = (
                st.columns(2)
            )


            with detail_col1:

                st.write(
                    "**Current Status:**",
                    gap.get(
                        "status"
                    ),
                )


                st.write(
                    "**JD Priority:**",
                    gap.get(
                        "priority"
                    ),
                )


                st.write(
                    "**Severity:**",
                    gap.get(
                        "severity"
                    ),
                )


                st.write(
                    "**Gap Type:**",
                    gap.get(
                        "gap_type"
                    ),
                )


            with detail_col2:

                st.write(
                    "**Recommended Action:**",
                    gap.get(
                        "recommended_action"
                    ),
                )


                st.write(
                    "**Employability Impact:**",
                    f"""
                    {
                        gap.get(
                            "employability_score"
                        )
                    }/100
                    """,
                )


                st.write(
                    "**Industry Impact:**",
                    f"""
                    {
                        gap.get(
                            "industry_importance_score"
                        )
                    }/100
                    """,
                )


                st.write(
                    "**Implementation Feasibility:**",
                    f"""
                    {
                        gap.get(
                            "implementation_feasibility_score"
                        )
                    }/100
                    """,
                )


            current_match = safe_text(

                gap.get(
                    "curriculum_match"
                )

            )


            if current_match:

                st.info(

                    f"""
                    **Current Curriculum Coverage**

                    {current_match}
                    """

                )


# ============================================================
# 25. ACTION DISTRIBUTION
# ============================================================

action_counts = {}


for gap in prioritized_gaps:

    action = safe_text(

        gap.get(
            "recommended_action"
        ),

        "ENHANCE",

    )


    action_counts[
        action
    ] = (
        action_counts.get(
            action,
            0
        )
        +
        1
    )


if action_counts:

    st.divider()

    st.subheader(
        "🛠 Recommended Curriculum Actions"
    )


    action_df = pd.DataFrame({

        "Action":
            list(
                action_counts.keys()
            ),

        "Gaps":
            list(
                action_counts.values()
            ),

    })


    st.dataframe(

        action_df,

        use_container_width=True,

        hide_index=True,

    )


# ============================================================
# 26. BUILD PRIORITY EXECUTION LIST
# ============================================================

priority_execution_list = []


for gap in prioritized_gaps:

    if gap.get(
        "priority_score",
        0,
    ) < 60:

        continue


    priority_execution_list.append({

        "rank":
            gap.get(
                "priority_rank"
            ),

        "skill":
            gap.get(
                "jd_skill"
            ),

        "priority":
            gap.get(
                "priority_level"
            ),

        "action":
            gap.get(
                "recommended_action"
            ),

        "reason":
            (
                f"""
                JD priority={gap.get("priority")};
                severity={gap.get("severity")};
                status={gap.get("status")};
                employability={
                    gap.get(
                        "employability_score"
                    )
                };
                """
            ),

    })


st.session_state[
    "priority_execution_list"
] = priority_execution_list


# ============================================================
# 27. DOWNLOAD PRIORITY MATRIX
# ============================================================

if not priority_matrix_df.empty:

    st.download_button(

        "⬇️ Download Enhancement Priority Matrix",

        data=priority_matrix_df.to_csv(
            index=False
        ),

        file_name=(
            "curriculum_enhancement_priority_matrix.csv"
        ),

        mime="text/csv",

        key="download_enhancement_priority_matrix",

    )


# ============================================================
# 28. COMPLETION FLAG
# ============================================================

st.session_state[
    "gap_prioritization_complete"
] = bool(
    prioritized_gaps
)


# ============================================================
# END OF CHUNK 2/10
# ============================================================
# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 3/10
# MODULE-LEVEL GAP MAPPING & ENHANCEMENT STRATEGY
# ============================================================

"""
Purpose
-------
Map prioritized industry gaps to the existing curriculum.

Input
-----
st.session_state["prioritized_gaps"]

Curriculum intelligence from Page 03.

Output
------
st.session_state["module_gap_mapping"]

st.session_state["module_enhancement_plan"]

st.session_state["unmapped_industry_gaps"]

st.session_state["curriculum_enhancement_summary"]

Decision hierarchy
------------------

1. Existing module + existing topic
       -> ENHANCE TOPIC

2. Existing module + related topic
       -> ADD TOPIC

3. Existing module + concept exists
       -> INCREASE DEPTH

4. Existing module + tool missing
       -> ADD TOOL / LAB

5. Existing module + technology missing
       -> ADD TECHNOLOGY

6. No suitable module
       -> NEW MODULE

7. Skill is minor/preferred
       -> OPTIONAL

"""


# ============================================================
# 1. LOAD DATA
# ============================================================

prioritized_gaps = st.session_state.get(
    "prioritized_gaps",
    []
)

curriculum_skill_intelligence = st.session_state.get(
    "curriculum_skill_intelligence",
    {}
)

industry_gap_analysis = st.session_state.get(
    "industry_gap_analysis",
    {}
)

jd_skill_intelligence = st.session_state.get(
    "jd_skill_intelligence",
    {}
)


# ============================================================
# 2. VALIDATION
# ============================================================

if not prioritized_gaps:

    st.warning(
        """
        ⚠️ Prioritized gaps are not available.

        Complete Chunk 2 first.
        """
    )


# ============================================================
# 3. EXTRACT CURRICULUM STRUCTURE
# ============================================================

def extract_curriculum_modules(
    curriculum_data,
):
    """
    Extract curriculum modules from different possible
    session-state structures.
    """

    if not curriculum_data:

        return []


    modules = curriculum_data.get(
        "modules",
        []
    )


    if isinstance(
        modules,
        dict,
    ):

        modules = [

            {
                "name":
                    key,

                "topics":
                    value,

            }

            for key, value in modules.items()

        ]


    if not isinstance(
        modules,
        list,
    ):

        return []


    normalized = []


    for index, module in enumerate(

        modules,

        start=1,

    ):

        # ----------------------------------------------------
        # String module
        # ----------------------------------------------------

        if isinstance(
            module,
            str,
        ):

            normalized.append({

                "module_id":
                    index,

                "module_name":
                    module.strip(),

                "topics":
                    [],

                "concepts":
                    [],

                "tools":
                    [],

                "technologies":
                    [],

            })

            continue


        # ----------------------------------------------------
        # Dictionary module
        # ----------------------------------------------------

        if not isinstance(
            module,
            dict,
        ):

            continue


        module_name = (

            module.get(
                "module_name"
            )

            or

            module.get(
                "name"
            )

            or

            module.get(
                "title"
            )

            or

            module.get(
                "module"
            )

            or

            f"Module {index}"

        )


        topics = normalize_list(

            module.get(
                "topics"
            )

        )


        concepts = normalize_list(

            module.get(
                "concepts"
            )

        )


        tools = normalize_list(

            module.get(
                "tools"
            )

        )


        technologies = normalize_list(

            module.get(
                "technologies"
            )

        )


        normalized.append({

            "module_id":
                index,

            "module_name":
                safe_text(
                    module_name
                ),

            "topics":
                unique_values(
                    topics
                ),

            "concepts":
                unique_values(
                    concepts
                ),

            "tools":
                unique_values(
                    tools
                ),

            "technologies":
                unique_values(
                    technologies
                ),

            "frameworks":
                unique_values(
                    normalize_list(
                        module.get(
                            "frameworks"
                        )
                    )
                ),

            "projects":
                unique_values(
                    normalize_list(
                        module.get(
                            "projects"
                        )
                    )
                ),

        })


    return normalized


# ============================================================
# 4. GET CURRICULUM MODULES
# ============================================================

curriculum_modules = extract_curriculum_modules(
    curriculum_skill_intelligence
)


# ============================================================
# 5. FALLBACK MODULE EXTRACTION
# ============================================================

"""
Some curriculum extractors store modules separately.
Use those structures as fallback.
"""

if not curriculum_modules:

    raw_modules = st.session_state.get(
        "curriculum_modules",
        []
    )


    curriculum_modules = extract_curriculum_modules({

        "modules":
            raw_modules

    })


# ============================================================
# 6. EXTRACT GLOBAL CURRICULUM CONTENT
# ============================================================

global_topics = unique_values(

    normalize_list(

        curriculum_skill_intelligence.get(
            "topics"
        )

    )

)


global_concepts = unique_values(

    normalize_list(

        curriculum_skill_intelligence.get(
            "concepts"
        )

    )

)


global_skills = unique_values(

    normalize_list(

        curriculum_skill_intelligence.get(
            "all_skills"
        )

    )

)


global_tools = unique_values(

    normalize_list(

        curriculum_skill_intelligence.get(
            "tools"
        )

    )

)


global_technologies = unique_values(

    normalize_list(

        curriculum_skill_intelligence.get(
            "technologies"
        )

    )

)


global_frameworks = unique_values(

    normalize_list(

        curriculum_skill_intelligence.get(
            "frameworks"
        )

    )

)


global_projects = unique_values(

    normalize_list(

        curriculum_skill_intelligence.get(
            "projects"
        )

    )

)


# ============================================================
# 7. NORMALIZE TEXT FOR MATCHING
# ============================================================

def normalize_match_text(
    value,
):
    """
    Normalize text for fuzzy keyword matching.
    """

    text = safe_text(
        value
    ).lower()


    text = re.sub(
        r"[^a-z0-9+#.\- ]+",
        " ",
        text,
    )


    text = re.sub(
        r"\s+",
        " ",
        text,
    )


    return text.strip()


# ============================================================
# 8. TOKENIZE
# ============================================================

def tokenize(
    value,
):
    """
    Convert text into meaningful tokens.
    """

    text = normalize_match_text(
        value
    )


    if not text:

        return set()


    stop_words = {

        "and",
        "or",
        "the",
        "of",
        "for",
        "to",
        "in",
        "with",
        "using",
        "based",
        "on",
        "a",
        "an",
        "from",

    }


    return {

        token

        for token in text.split()

        if (
            len(token) > 1
            and
            token not in stop_words
        )

    }


# ============================================================
# 9. TEXT SIMILARITY
# ============================================================

def text_similarity(
    text_a,
    text_b,
):
    """
    Lightweight lexical similarity.

    This is intentionally dependency-free.

    Returns:
        0 - 100
    """

    tokens_a = tokenize(
        text_a
    )


    tokens_b = tokenize(
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


    if not union:

        return 0.0


    jaccard = (

        len(
            intersection
        )

        /

        len(
            union
        )

    )


    # --------------------------------------------------------
    # Substring bonus
    # --------------------------------------------------------

    normalized_a = normalize_match_text(
        text_a
    )


    normalized_b = normalize_match_text(
        text_b
    )


    substring_bonus = 0.0


    if (
        normalized_a in normalized_b
        or
        normalized_b in normalized_a
    ):

        substring_bonus = 25.0


    score = (

        jaccard * 75.0

        +

        substring_bonus

    )


    return round(

        min(
            score,
            100.0
        ),

        2,

    )


# ============================================================
# 10. MATCH AGAINST LIST
# ============================================================

def best_list_match(
    query,
    candidates,
):
    """
    Find best semantic-ish lexical match.
    """

    if not query or not candidates:

        return {

            "match":
                "",

            "score":
                0.0,

        }


    best_match = ""


    best_score = 0.0


    for candidate in candidates:

        candidate = safe_text(
            candidate
        )


        if not candidate:

            continue


        score = text_similarity(

            query,

            candidate,

        )


        if score > best_score:

            best_score = score

            best_match = candidate


    return {

        "match":
            best_match,

        "score":
            round(
                best_score,
                2,
            ),

    }


# ============================================================
# 11. MATCH GAP TO MODULE
# ============================================================

def match_gap_to_module(
    gap,
    module,
):
    """
    Calculate how strongly a gap relates to an existing module.
    """

    skill = safe_text(

        gap.get(
            "jd_skill"
        )

    )


    gap_topic = safe_text(

        gap.get(
            "topic"
        )

    )


    module_name = safe_text(

        module.get(
            "module_name"
        )

    )


    topics = module.get(
        "topics",
        []
    )


    concepts = module.get(
        "concepts",
        []
    )


    tools = module.get(
        "tools",
        []
    )


    technologies = module.get(
        "technologies",
        []
    )


    frameworks = module.get(
        "frameworks",
        []
    )


    # --------------------------------------------------------
    # Module name score
    # --------------------------------------------------------

    module_score = text_similarity(

        skill,

        module_name,

    )


    # --------------------------------------------------------
    # Topic score
    # --------------------------------------------------------

    topic_match = best_list_match(

        skill,

        topics,

    )


    # --------------------------------------------------------
    # Concept score
    # --------------------------------------------------------

    concept_match = best_list_match(

        skill,

        concepts,

    )


    # --------------------------------------------------------
    # Tool score
    # --------------------------------------------------------

    tool_match = best_list_match(

        skill,

        tools,

    )


    # --------------------------------------------------------
    # Technology score
    # --------------------------------------------------------

    technology_match = best_list_match(

        skill,

        technologies,

    )


    # --------------------------------------------------------
    # Framework score
    # --------------------------------------------------------

    framework_match = best_list_match(

        skill,

        frameworks,

    )


    # --------------------------------------------------------
    # Existing gap topic
    # --------------------------------------------------------

    topic_context_score = text_similarity(

        gap_topic,

        module_name,

    )


    # --------------------------------------------------------
    # Weighted module relevance
    # --------------------------------------------------------

    relevance_score = (

        module_score * 0.25

        +

        topic_match["score"] * 0.20

        +

        concept_match["score"] * 0.15

        +

        tool_match["score"] * 0.10

        +

        technology_match["score"] * 0.10

        +

        framework_match["score"] * 0.10

        +

        topic_context_score * 0.10

    )


    return {

        "module":
            module_name,

        "module_score":
            round(
                module_score,
                2,
            ),

        "topic_match":
            topic_match,

        "concept_match":
            concept_match,

        "tool_match":
            tool_match,

        "technology_match":
            technology_match,

        "framework_match":
            framework_match,

        "relevance_score":
            round(
                relevance_score,
                2,
            ),

    }


# ============================================================
# 12. FIND BEST CURRICULUM MODULE
# ============================================================

def find_best_module(
    gap,
    modules,
):
    """
    Find the most relevant existing module.
    """

    if not modules:

        return {

            "module":
                "",

            "relevance_score":
                0.0,

            "details":
                None,

        }


    matches = []


    for module in modules:

        result = match_gap_to_module(

            gap,

            module,

        )


        matches.append(
            result
        )


    matches = sorted(

        matches,

        key=lambda item:

            safe_number(

                item.get(
                    "relevance_score",
                    0,
                )

            ),

        reverse=True,

    )


    best = matches[0]


    return {

        "module":
            best.get(
                "module",
                ""
            ),

        "relevance_score":
            best.get(
                "relevance_score",
                0.0,
            ),

        "details":
            best,

        "all_matches":
            matches[:5],

    }


# ============================================================
# 13. DETERMINE EXISTING COVERAGE
# ============================================================

def determine_existing_coverage(
    gap,
):
    """
    Determine whether the skill already exists at some level
    in the curriculum.
    """

    skill = safe_text(

        gap.get(
            "jd_skill"
        )

    )


    # --------------------------------------------------------
    # Global skill
    # --------------------------------------------------------

    skill_match = best_list_match(

        skill,

        global_skills,

    )


    # --------------------------------------------------------
    # Topic
    # --------------------------------------------------------

    topic_match = best_list_match(

        skill,

        global_topics,

    )


    # --------------------------------------------------------
    # Concept
    # --------------------------------------------------------

    concept_match = best_list_match(

        skill,

        global_concepts,

    )


    # --------------------------------------------------------
    # Tool
    # --------------------------------------------------------

    tool_match = best_list_match(

        skill,

        global_tools,

    )


    # --------------------------------------------------------
    # Technology
    # --------------------------------------------------------

    technology_match = best_list_match(

        skill,

        global_technologies,

    )


    # --------------------------------------------------------
    # Framework
    # --------------------------------------------------------

    framework_match = best_list_match(

        skill,

        global_frameworks,

    )


    return {

        "skill":
            skill,

        "skill_match":
            skill_match,

        "topic_match":
            topic_match,

        "concept_match":
            concept_match,

        "tool_match":
            tool_match,

        "technology_match":
            technology_match,

        "framework_match":
            framework_match,

    }


# ============================================================
# 14. DETERMINE ENHANCEMENT STRATEGY
# ============================================================

def determine_enhancement_strategy(
    gap,
    module_result,
    coverage_result,
):
    """
    Determine how the curriculum should be changed.
    """

    status = safe_text(

        gap.get(
            "status"
        ),

        "missing",

    ).lower()


    priority = safe_text(

        gap.get(
            "priority"
        ),

        "required",

    ).lower()


    severity = safe_text(

        gap.get(
            "severity"
        ),

        "medium",

    ).lower()


    gap_type = safe_text(

        gap.get(
            "gap_type"
        )

    )


    module_score = safe_number(

        module_result.get(
            "relevance_score",
            0,
        )

    )


    topic_score = safe_number(

        coverage_result.get(
            "topic_match",
            {}
        ).get(
            "score",
            0,
        )

    )


    concept_score = safe_number(

        coverage_result.get(
            "concept_match",
            {}
        ).get(
            "score",
            0,
        )

    )


    tool_score = safe_number(

        coverage_result.get(
            "tool_match",
            {}
        ).get(
            "score",
            0,
        )

    )


    technology_score = safe_number(

        coverage_result.get(
            "technology_match",
            {}
        ).get(
            "score",
            0,
        )

    )


    # ========================================================
    # CASE 1
    # Existing topic + partial
    # ========================================================

    if (

        status == "partial"

        and

        topic_score >= 45

    ):

        return {

            "action":
                "ENHANCE TOPIC",

            "reason":
                (
                    "The curriculum already contains a related "
                    "topic but industry depth appears insufficient."
                ),

            "confidence":
                min(
                    100,
                    topic_score + 20
                ),

        }


    # ========================================================
    # CASE 2
    # Existing concept but weak depth
    # ========================================================

    if (

        concept_score >= 55

        and

        status in {
            "missing",
            "partial",
        }

    ):

        return {

            "action":
                "INCREASE DEPTH",

            "reason":
                (
                    "A related concept already exists, so "
                    "the curriculum should deepen coverage "
                    "rather than duplicate the topic."
                ),

            "confidence":
                concept_score,

        }


    # ========================================================
    # CASE 3
    # Related module
    # ========================================================

    if (

        module_score >= 40

        and

        status in {
            "missing",
            "partial",
        }

    ):

        return {

            "action":
                "ADD TOPIC TO EXISTING MODULE",

            "reason":
                (
                    "An existing module is sufficiently related "
                    "to the industry requirement."
                ),

            "confidence":
                module_score,

        }


    # ========================================================
    # CASE 4
    # Tool gap
    # ========================================================

    if "tool" in gap_type.lower():

        if module_score >= 30:

            return {

                "action":
                    "ADD TOOL + HANDS-ON LAB",

                "reason":
                    (
                        "The tool should be introduced through "
                        "practical work in an existing module."
                    ),

                "confidence":
                    max(
                        module_score,
                        60,
                    ),

            }


    # ========================================================
    # CASE 5
    # Technology / Framework
    # ========================================================

    if (

        "technology" in gap_type.lower()

        or

        "framework" in gap_type.lower()

    ):

        if module_score >= 30:

            return {

                "action":
                    "ADD TECHNOLOGY PRACTICAL",

                "reason":
                    (
                        "The technology is related to an existing "
                        "module and should be introduced practically."
                    ),

                "confidence":
                    module_score,

            }


    # ========================================================
    # CASE 6
    # Cloud
    # ========================================================

    if "cloud" in gap_type.lower():

        return {

            "action":
                "ADD CLOUD HANDS-ON MODULE",

            "reason":
                (
                    "Cloud requirements generally require "
                    "dedicated practical exposure."
                ),

            "confidence":
                80,

        }


    # ========================================================
    # CASE 7
    # DevOps
    # ========================================================

    if "devops" in gap_type.lower():

        return {

            "action":
                "ADD DEVOPS / DEPLOYMENT PRACTICAL",

            "reason":
                (
                    "Deployment and operational skills require "
                    "hands-on practice."
                ),

            "confidence":
                80,

        }


    # ========================================================
    # CASE 8
    # Required + no module
    # ========================================================

    if (

        priority == "required"

        and

        severity in {
            "critical",
            "high",
        }

        and

        module_score < 30

    ):

        return {

            "action":
                "CREATE NEW MODULE",

            "reason":
                (
                    "The requirement is important but no "
                    "sufficiently relevant existing module "
                    "was identified."
                ),

            "confidence":
                85,

        }


    # ========================================================
    # CASE 9
    # Preferred requirement
    # ========================================================

    if priority == "preferred":

        return {

            "action":
                "OPTIONAL ENHANCEMENT",

            "reason":
                (
                    "The requirement is preferred rather than "
                    "mandatory and can be introduced selectively."
                ),

            "confidence":
                70,

        }


    # ========================================================
    # DEFAULT
    # ========================================================

    return {

        "action":
            "REVIEW BY EXPERT AGENT",

        "reason":
            (
                "The deterministic mapper could not confidently "
                "determine the appropriate curriculum intervention."
            ),

        "confidence":
            50,

    }


# ============================================================
# 15. BUILD MODULE GAP RECORD
# ============================================================

def build_module_gap_record(
    gap,
):
    """
    Create a complete module-level enhancement record.
    """

    module_result = find_best_module(

        gap,

        curriculum_modules,

    )


    coverage_result = determine_existing_coverage(
        gap
    )


    strategy = determine_enhancement_strategy(

        gap,

        module_result,

        coverage_result,

    )


    best_module = safe_text(

        module_result.get(
            "module"
        )

    )


    return {

        # ----------------------------------------------------
        # Original gap
        # ----------------------------------------------------

        "priority_rank":
            gap.get(
                "priority_rank"
            ),

        "jd_skill":
            gap.get(
                "jd_skill"
            ),

        "status":
            gap.get(
                "status"
            ),

        "priority":
            gap.get(
                "priority"
            ),

        "severity":
            gap.get(
                "severity"
            ),

        "gap_type":
            gap.get(
                "gap_type"
            ),

        "priority_score":
            gap.get(
                "priority_score"
            ),

        # ----------------------------------------------------
        # Existing curriculum mapping
        # ----------------------------------------------------

        "existing_module":
            best_module,

        "module_relevance":
            module_result.get(
                "relevance_score",
                0,
            ),

        "existing_topic":
            coverage_result.get(
                "topic_match",
                {}
            ).get(
                "match",
                ""
            ),

        "topic_match_score":
            coverage_result.get(
                "topic_match",
                {}
            ).get(
                "score",
                0,
            ),

        "existing_concept":
            coverage_result.get(
                "concept_match",
                {}
            ).get(
                "match",
                ""
            ),

        "concept_match_score":
            coverage_result.get(
                "concept_match",
                {}
            ).get(
                "score",
                0,
            ),

        "existing_tool":
            coverage_result.get(
                "tool_match",
                {}
            ).get(
                "match",
                ""
            ),

        "tool_match_score":
            coverage_result.get(
                "tool_match",
                {}
            ).get(
                "score",
                0,
            ),

        "existing_technology":
            coverage_result.get(
                "technology_match",
                {}
            ).get(
                "match",
                ""
            ),

        "technology_match_score":
            coverage_result.get(
                "technology_match",
                {}
            ).get(
                "score",
                0,
            ),

        "existing_framework":
            coverage_result.get(
                "framework_match",
                {}
            ).get(
                "match",
                ""
            ),

        "framework_match_score":
            coverage_result.get(
                "framework_match",
                {}
            ).get(
                "score",
                0,
            ),

        # ----------------------------------------------------
        # Enhancement strategy
        # ----------------------------------------------------

        "recommended_action":
            strategy.get(
                "action"
            ),

        "strategy_reason":
            strategy.get(
                "reason"
            ),

        "strategy_confidence":
            strategy.get(
                "confidence"
            ),

    }


# ============================================================
# 16. BUILD MODULE GAP MAPPING
# ============================================================

module_gap_mapping = [

    build_module_gap_record(
        gap
    )

    for gap in prioritized_gaps

]


# ============================================================
# 17. SORT BY PRIORITY
# ============================================================

module_gap_mapping = sorted(

    module_gap_mapping,

    key=lambda item:

        safe_number(

            item.get(
                "priority_score",
                0,
            )

        ),

    reverse=True,

)


# ============================================================
# 18. ASSIGN UNMAPPED GAPS
# ============================================================

unmapped_industry_gaps = [

    item

    for item in module_gap_mapping

    if (

        not item.get(
            "existing_module"
        )

        or

        safe_number(
            item.get(
                "module_relevance",
                0,
            )
        ) < 30

    )

]


# ============================================================
# 19. MODULE ENHANCEMENT PLAN
# ============================================================

module_enhancement_plan = []


for item in module_gap_mapping:

    action = safe_text(

        item.get(
            "recommended_action"
        )

    )


    if action == "CREATE NEW MODULE":

        module_name = (
            "New Module Required"
        )

    else:

        module_name = safe_text(

            item.get(
                "existing_module"
            )

        )


    module_enhancement_plan.append({

        "jd_skill":
            item.get(
                "jd_skill"
            ),

        "priority":
            item.get(
                "priority_score"
            ),

        "priority_level":
            next(

                (

                    gap.get(
                        "priority_level"
                    )

                    for gap in prioritized_gaps

                    if gap.get(
                        "jd_skill"
                    )
                    ==
                    item.get(
                        "jd_skill"
                    )

                ),

                "P2 - Medium",

            ),

        "existing_module":
            module_name,

        "existing_topic":
            item.get(
                "existing_topic"
            ),

        "action":
            action,

        "reason":
            item.get(
                "strategy_reason"
            ),

        "confidence":
            item.get(
                "strategy_confidence"
            ),

        "concept_to_enhance":
            item.get(
                "existing_concept"
            ),

        "tool_to_enhance":
            item.get(
                "existing_tool"
            ),

        "technology_to_enhance":
            item.get(
                "existing_technology"
            ),

        "framework_to_enhance":
            item.get(
                "existing_framework"
            ),

    })


# ============================================================
# 20. SAVE RESULTS
# ============================================================

st.session_state[
    "module_gap_mapping"
] = module_gap_mapping


st.session_state[
    "module_enhancement_plan"
] = module_enhancement_plan


st.session_state[
    "unmapped_industry_gaps"
] = unmapped_industry_gaps


# ============================================================
# 21. DISPLAY MODULE MAPPING
# ============================================================

st.divider()

st.subheader(
    "🧩 Module-Level Gap Mapping"
)


if module_gap_mapping:

    mapping_rows = []


    for item in module_gap_mapping:

        mapping_rows.append({

            "JD Skill":
                item.get(
                    "jd_skill"
                ),

            "Priority":
                item.get(
                    "priority_score"
                ),

            "Existing Module":
                item.get(
                    "existing_module"
                )
                or
                "❌ None",

            "Existing Topic":
                item.get(
                    "existing_topic"
                )
                or
                "—",

            "Concept Match":
                item.get(
                    "existing_concept"
                )
                or
                "—",

            "Tool Match":
                item.get(
                    "existing_tool"
                )
                or
                "—",

            "Technology Match":
                item.get(
                    "existing_technology"
                )
                or
                "—",

            "Recommended Action":
                item.get(
                    "recommended_action"
                ),

            "Confidence":
                f"""
                {
                    item.get(
                        "strategy_confidence",
                        0
                    )
                }%
                """,

        })


    st.dataframe(

        pd.DataFrame(
            mapping_rows
        ),

        use_container_width=True,

        hide_index=True,

    )


# ============================================================
# 22. ACTION SUMMARY
# ============================================================

action_summary = {}


for item in module_gap_mapping:

    action = safe_text(

        item.get(
            "recommended_action"
        ),

        "REVIEW",

    )


    action_summary[
        action
    ] = (

        action_summary.get(
            action,
            0
        )
        +
        1

    )


if action_summary:

    st.divider()

    st.subheader(
        "🛠 Curriculum Intervention Summary"
    )


    action_summary_df = pd.DataFrame({

        "Intervention":
            list(
                action_summary.keys()
            ),

        "Number of Gaps":
            list(
                action_summary.values()
            ),

    })


    st.dataframe(

        action_summary_df,

        use_container_width=True,

        hide_index=True,

    )


# ============================================================
# 23. EXISTING MODULE ENHANCEMENTS
# ============================================================

existing_module_items = [

    item

    for item in module_gap_mapping

    if (

        item.get(
            "existing_module"
        )

        and

        item.get(
            "recommended_action"
        )
        !=
        "CREATE NEW MODULE"

    )

]


if existing_module_items:

    st.divider()

    st.subheader(
        "📚 Existing Modules Requiring Enhancement"
    )


    module_groups = {}


    for item in existing_module_items:

        module_name = safe_text(

            item.get(
                "existing_module"
            )

        )


        if module_name not in module_groups:

            module_groups[
                module_name
            ] = []


        module_groups[
            module_name
        ].append(
            item
        )


    for module_name, items in (
        module_groups.items()
    ):

        with st.expander(

            f"📘 {module_name} "
            f"({len(items)} gap(s))",

            expanded=False,

        ):

            for item in items:

                st.markdown(

                    f"""
                    ### 🔹 {item.get("jd_skill")}

                    **Action:**
                    {item.get("recommended_action")}

                    **Current Topic:**
                    {item.get("existing_topic") or "Not identified"}

                    **Current Concept:**
                    {item.get("existing_concept") or "Not identified"}

                    **Reason:**
                    {item.get("strategy_reason")}
                    """

                )


# ============================================================
# 24. NEW MODULE REQUIREMENTS
# ============================================================

new_module_items = [

    item

    for item in module_gap_mapping

    if item.get(
        "recommended_action"
    )
    ==
    "CREATE NEW MODULE"

]


if new_module_items:

    st.divider()

    st.subheader(
        "🆕 Potential New Modules"
    )


    for item in new_module_items:

        st.warning(

            f"""
            ### 🆕 {item.get("jd_skill")}

            **Reason:**
            {item.get("strategy_reason")}

            **Priority Score:**
            {item.get("priority_score")}/100

            **Confidence:**
            {item.get("strategy_confidence")}%
            """

        )


# ============================================================
# 25. UNMAPPED GAPS
# ============================================================

if unmapped_industry_gaps:

    st.divider()

    st.subheader(
        "⚠️ Gaps Without Strong Existing Module Mapping"
    )


    unmapped_rows = []


    for item in unmapped_industry_gaps:

        unmapped_rows.append({

            "JD Skill":
                item.get(
                    "jd_skill"
                ),

            "Priority":
                item.get(
                    "priority_score"
                ),

            "Severity":
                item.get(
                    "severity"
                ),

            "Gap Type":
                item.get(
                    "gap_type"
                ),

            "Best Module":
                item.get(
                    "existing_module"
                )
                or
                "No suitable module",

            "Recommended Action":
                item.get(
                    "recommended_action"
                ),

        })


    st.dataframe(

        pd.DataFrame(
            unmapped_rows
        ),

        use_container_width=True,

        hide_index=True,

    )


# ============================================================
# 26. BUILD CURRICULUM ENHANCEMENT SUMMARY
# ============================================================

curriculum_enhancement_summary = {

    "total_gaps":
        len(
            module_gap_mapping
        ),

    "existing_module_enhancements":
        len(
            existing_module_items
        ),

    "new_module_candidates":
        len(
            new_module_items
        ),

    "unmapped_gaps":
        len(
            unmapped_industry_gaps
        ),

    "action_distribution":
        action_summary,

    "modules_affected":
        list(
            module_groups.keys()
        )
        if existing_module_items
        else [],

}


st.session_state[
    "curriculum_enhancement_summary"
] = curriculum_enhancement_summary


# ============================================================
# 27. DOWNLOAD MODULE GAP MAPPING
# ============================================================

if module_gap_mapping:

    module_mapping_df = pd.DataFrame(
        module_gap_mapping
    )


    st.download_button(

        "⬇️ Download Module Gap Mapping",

        data=module_mapping_df.to_csv(
            index=False
        ),

        file_name=(
            "module_level_gap_mapping.csv"
        ),

        mime="text/csv",

        key="download_module_gap_mapping",

    )


# ============================================================
# 28. COMPLETION FLAG
# ============================================================

st.session_state[
    "module_gap_mapping_complete"
] = bool(
    module_gap_mapping
)


# ============================================================
# END OF CHUNK 3/10
# ============================================================
# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 4/10
# CURRICULUM ENHANCEMENT BLUEPRINT
# ============================================================

"""
Purpose
-------
Create a detailed, structured curriculum enhancement blueprint
from the prioritized module-level industry gaps.

Input
-----
st.session_state["module_gap_mapping"]
st.session_state["module_enhancement_plan"]
st.session_state["prioritized_gaps"]

Output
------
st.session_state["enhancement_blueprint"]

st.session_state["enhancement_blueprint_df"]

st.session_state["enhancement_concepts"]

st.session_state["enhancement_tools"]

st.session_state["enhancement_technologies"]

st.session_state["enhancement_projects"]

st.session_state["enhancement_labs"]

st.session_state["enhancement_learning_outcomes"]

Important
---------
This is a deterministic blueprint.

The Expert Agent in Chunk 5 will review and improve it.

The Critic Agent in Chunk 6 will challenge it.

The Final Enhancement Agent in Chunk 7 will approve/refine it.
"""


# ============================================================
# 1. LOAD PREVIOUS CHUNK OUTPUTS
# ============================================================

module_gap_mapping = st.session_state.get(
    "module_gap_mapping",
    []
)


module_enhancement_plan = st.session_state.get(
    "module_enhancement_plan",
    []
)


prioritized_gaps = st.session_state.get(
    "prioritized_gaps",
    []
)


curriculum_skill_intelligence = st.session_state.get(
    "curriculum_skill_intelligence",
    {}
)


jd_skill_intelligence = st.session_state.get(
    "jd_skill_intelligence",
    {}
)


# ============================================================
# 2. VALIDATION
# ============================================================

if not module_gap_mapping:

    st.warning(
        """
        ⚠️ Module-level gap mapping is not available.

        Please complete Chunk 3 first.
        """
    )


# ============================================================
# 3. DOMAIN TAXONOMY
# ============================================================

"""
Lightweight taxonomy used to generate sensible baseline
recommendations.

The Expert Agent will later refine these recommendations.
"""

DOMAIN_TAXONOMY = {

    "python": {

        "concepts": [
            "Python programming",
            "Functions",
            "Object-oriented programming",
            "Exception handling",
            "File handling",
            "Virtual environments",
            "Package management",
        ],

        "tools": [
            "VS Code",
            "Jupyter Notebook",
            "Google Colab",
        ],

        "technologies": [
            "Python",
            "pip",
            "venv",
        ],

    },


    "machine learning": {

        "concepts": [
            "Supervised learning",
            "Unsupervised learning",
            "Feature engineering",
            "Model evaluation",
            "Cross-validation",
            "Hyperparameter tuning",
        ],

        "tools": [
            "Scikit-learn",
            "Jupyter Notebook",
        ],

        "technologies": [
            "Python",
            "Scikit-learn",
        ],

    },


    "deep learning": {

        "concepts": [
            "Neural networks",
            "Backpropagation",
            "Optimization",
            "CNN",
            "Transfer learning",
            "Model evaluation",
        ],

        "tools": [
            "TensorFlow",
            "Keras",
            "PyTorch",
        ],

        "technologies": [
            "TensorFlow",
            "PyTorch",
            "Keras",
        ],

    },


    "generative ai": {

        "concepts": [
            "Large Language Models",
            "Prompt engineering",
            "Embeddings",
            "RAG",
            "Fine-tuning",
            "Tool calling",
            "Agentic AI",
        ],

        "tools": [
            "Hugging Face",
            "LangChain",
            "LangGraph",
        ],

        "technologies": [
            "LLM",
            "RAG",
            "Vector Database",
            "Generative AI",
        ],

    },


    "llm": {

        "concepts": [
            "Transformer architecture",
            "Tokens",
            "Embeddings",
            "Prompt engineering",
            "Context windows",
            "RAG",
            "Tool calling",
        ],

        "tools": [
            "Hugging Face",
            "LangChain",
            "Groq",
        ],

        "technologies": [
            "LLM",
            "Transformer",
            "Vector Database",
        ],

    },


    "rag": {

        "concepts": [
            "Document ingestion",
            "Chunking",
            "Embeddings",
            "Vector search",
            "Retrieval",
            "Reranking",
            "Grounded generation",
        ],

        "tools": [
            "FAISS",
            "Chroma",
            "LangChain",
        ],

        "technologies": [
            "Vector Database",
            "Embeddings",
            "RAG",
        ],

    },


    "agentic ai": {

        "concepts": [
            "AI agents",
            "Agent planning",
            "Tool calling",
            "Memory",
            "Agent state",
            "Multi-agent systems",
            "Workflow orchestration",
        ],

        "tools": [
            "LangGraph",
            "LangChain",
        ],

        "technologies": [
            "LLM",
            "Agentic AI",
            "Multi-Agent Systems",
        ],

    },


    "langchain": {

        "concepts": [
            "Chains",
            "Prompts",
            "Retrievers",
            "Tools",
            "Agents",
            "Structured output",
        ],

        "tools": [
            "LangChain",
        ],

        "technologies": [
            "LLM",
            "RAG",
            "Agentic AI",
        ],

    },


    "langgraph": {

        "concepts": [
            "Graph-based workflows",
            "State management",
            "Nodes",
            "Edges",
            "Conditional routing",
            "Checkpoints",
            "Multi-agent orchestration",
        ],

        "tools": [
            "LangGraph",
        ],

        "technologies": [
            "Agentic AI",
            "Multi-Agent Systems",
        ],

    },


    "docker": {

        "concepts": [
            "Containers",
            "Images",
            "Dockerfile",
            "Container networking",
            "Volumes",
            "Container registries",
        ],

        "tools": [
            "Docker",
            "Docker Hub",
        ],

        "technologies": [
            "Docker",
            "Containers",
        ],

    },


    "kubernetes": {

        "concepts": [
            "Pods",
            "Deployments",
            "Services",
            "ConfigMaps",
            "Secrets",
            "Scaling",
            "Ingress",
        ],

        "tools": [
            "kubectl",
            "Minikube",
            "Kubernetes",
        ],

        "technologies": [
            "Kubernetes",
            "Containers",
            "Cloud Native",
        ],

    },


    "aws": {

        "concepts": [
            "Cloud computing",
            "IAM",
            "Compute",
            "Storage",
            "Networking",
            "Monitoring",
        ],

        "tools": [
            "AWS Console",
            "AWS CLI",
        ],

        "technologies": [
            "AWS",
            "Cloud Computing",
        ],

    },


    "azure": {

        "concepts": [
            "Cloud computing",
            "Identity",
            "Compute",
            "Storage",
            "Networking",
            "Monitoring",
        ],

        "tools": [
            "Azure Portal",
            "Azure CLI",
        ],

        "technologies": [
            "Microsoft Azure",
            "Cloud Computing",
        ],

    },


    "sql": {

        "concepts": [
            "Relational databases",
            "SELECT",
            "JOIN",
            "Aggregation",
            "Subqueries",
            "Indexes",
            "Transactions",
        ],

        "tools": [
            "PostgreSQL",
            "MySQL",
            "SQL Workbench",
        ],

        "technologies": [
            "SQL",
            "Relational Database",
        ],

    },


    "power bi": {

        "concepts": [
            "Data modeling",
            "Power Query",
            "DAX",
            "Data visualization",
            "Dashboards",
            "KPIs",
        ],

        "tools": [
            "Power BI",
            "Power Query",
        ],

        "technologies": [
            "Business Intelligence",
            "Data Analytics",
        ],

    },


    "tableau": {

        "concepts": [
            "Data visualization",
            "Dashboards",
            "Calculated fields",
            "Filters",
            "Parameters",
            "Storytelling",
        ],

        "tools": [
            "Tableau",
        ],

        "technologies": [
            "Business Intelligence",
            "Data Visualization",
        ],

    },


    "mlops": {

        "concepts": [
            "Model deployment",
            "Model monitoring",
            "Model versioning",
            "Experiment tracking",
            "CI/CD",
            "Data pipelines",
        ],

        "tools": [
            "MLflow",
            "Docker",
            "GitHub Actions",
        ],

        "technologies": [
            "MLOps",
            "CI/CD",
            "Model Serving",
        ],

    },


    "devops": {

        "concepts": [
            "CI/CD",
            "Infrastructure automation",
            "Containers",
            "Monitoring",
            "Version control",
            "Deployment automation",
        ],

        "tools": [
            "Git",
            "Docker",
            "GitHub Actions",
            "Jenkins",
        ],

        "technologies": [
            "DevOps",
            "CI/CD",
            "Cloud",
        ],

    },

}


# ============================================================
# 4. GENERIC DEFAULT TAXONOMY
# ============================================================

DEFAULT_DOMAIN = {

    "concepts": [
        "Core concepts",
        "Industry applications",
        "Best practices",
        "Problem solving",
        "Implementation",
        "Evaluation",
    ],

    "tools": [
        "Industry-standard development environment",
    ],

    "technologies": [
        "Industry-relevant technology",
    ],

}


# ============================================================
# 5. DOMAIN DETECTION
# ============================================================

def detect_domains(
    skill,
    gap_type="",
    module="",
):
    """
    Identify one or more relevant technology domains.
    """

    text = safe_text(

        f"""
        {skill}
        {gap_type}
        {module}
        """

    ).lower()


    domains = []


    for domain in DOMAIN_TAXONOMY.keys():

        if domain in text:

            domains.append(
                domain
            )


    # --------------------------------------------------------
    # Aliases
    # --------------------------------------------------------

    aliases = {

        "llama":
            "llm",

        "large language model":
            "llm",

        "generative ai":
            "generative ai",

        "gen ai":
            "generative ai",

        "agent":
            "agentic ai",

        "multi agent":
            "agentic ai",

        "vector":
            "rag",

        "retrieval":
            "rag",

        "postgres":
            "sql",

        "postgresql":
            "sql",

        "mysql":
            "sql",

        "container":
            "docker",

        "k8s":
            "kubernetes",

        "bi":
            "power bi",

    }


    for alias, domain in aliases.items():

        if alias in text:

            if domain not in domains:

                domains.append(
                    domain
                )


    return unique_values(
        domains
    )


# ============================================================
# 6. GET DOMAIN RECOMMENDATIONS
# ============================================================

def get_domain_recommendations(
    skill,
    gap_type,
    module,
):
    """
    Return baseline concepts, tools and technologies.
    """

    domains = detect_domains(

        skill,

        gap_type,

        module,

    )


    concepts = []

    tools = []

    technologies = []


    for domain in domains:

        taxonomy = DOMAIN_TAXONOMY.get(
            domain,
            {}
        )


        concepts.extend(

            taxonomy.get(
                "concepts",
                []
            )

        )


        tools.extend(

            taxonomy.get(
                "tools",
                []
            )

        )


        technologies.extend(

            taxonomy.get(
                "technologies",
                []
            )

        )


    if not domains:

        concepts.extend(

            DEFAULT_DOMAIN[
                "concepts"
            ]

        )


        tools.extend(

            DEFAULT_DOMAIN[
                "tools"
            ]

        )


        technologies.extend(

            DEFAULT_DOMAIN[
                "technologies"
            ]

        )


    return {

        "domains":
            domains,

        "concepts":
            unique_values(
                concepts
            ),

        "tools":
            unique_values(
                tools
            ),

        "technologies":
            unique_values(
                technologies
            ),

    }


# ============================================================
# 7. RECOMMENDED DEPTH
# ============================================================

def determine_depth(
    gap,
):
    """
    Determine suggested learning depth.
    """

    priority = safe_text(

        gap.get(
            "priority"
        ),

        "preferred",

    ).lower()


    severity = safe_text(

        gap.get(
            "severity"
        ),

        "medium",

    ).lower()


    action = safe_text(

        gap.get(
            "recommended_action"
        )

    ).upper()


    score = safe_number(

        gap.get(
            "priority_score",
            0,
        )

    )


    if (

        priority in {
            "required",
            "mandatory",
        }

        and

        severity == "critical"

    ):

        return "Advanced"


    if score >= 85:

        return "Advanced"


    if score >= 70:

        return "Intermediate to Advanced"


    if score >= 55:

        return "Intermediate"


    if action == "OPTIONAL ENHANCEMENT":

        return "Awareness / Foundation"


    return "Foundation"


# ============================================================
# 8. RECOMMENDED HOURS
# ============================================================

def determine_hours(
    gap,
):
    """
    Estimate learning hours for the enhancement.

    This is a baseline estimate and should be validated by
    the Expert Agent.
    """

    priority_score = safe_number(

        gap.get(
            "priority_score",
            0,
        )

    )


    severity = safe_text(

        gap.get(
            "severity"
        ),

        "medium",

    ).lower()


    action = safe_text(

        gap.get(
            "recommended_action"
        )

    ).upper()


    # --------------------------------------------------------
    # New module
    # --------------------------------------------------------

    if "CREATE NEW MODULE" in action:

        if severity == "critical":

            return 12

        if severity == "high":

            return 10

        return 8


    # --------------------------------------------------------
    # Cloud / DevOps
    # --------------------------------------------------------

    if (

        "CLOUD" in action

        or

        "DEVOPS" in action

    ):

        return 6


    # --------------------------------------------------------
    # Deep enhancement
    # --------------------------------------------------------

    if (

        "INCREASE DEPTH" in action

        or

        "ENHANCE" in action

    ):

        if priority_score >= 85:

            return 6

        if priority_score >= 70:

            return 4

        return 3


    # --------------------------------------------------------
    # Tool / lab
    # --------------------------------------------------------

    if "TOOL" in action:

        return 3


    # --------------------------------------------------------
    # Optional
    # --------------------------------------------------------

    if "OPTIONAL" in action:

        return 2


    return 3


# ============================================================
# 9. LAB GENERATION
# ============================================================

def generate_lab(
    skill,
    module,
    concepts,
    tools,
):
    """
    Generate a practical lab recommendation.
    """

    skill_text = safe_text(
        skill
    )


    module_text = safe_text(
        module
    )


    tool_text = (
        ", ".join(
            tools[:3]
        )
        if tools
        else
        "appropriate industry tool"
    )


    concept_text = (
        ", ".join(
            concepts[:4]
        )
        if concepts
        else
        "core concepts"
    )


    return {

        "title":
            f"{skill_text} Hands-on Lab",

        "module":
            module_text
            or
            "Industry Skills Module",

        "objective":
            (
                f"Implement {skill_text} using "
                f"{tool_text}."
            ),

        "activities": [

            (
                f"Understand the fundamentals of "
                f"{skill_text}."
            ),

            (
                f"Implement {concept_text}."
            ),

            (
                f"Use {tool_text} in a practical workflow."
            ),

            (
                "Test and evaluate the implementation."
            ),

            (
                "Document the solution and findings."
            ),

        ],

        "deliverable":
            (
                f"Working {skill_text} implementation "
                "with documentation."
            ),

    }


# ============================================================
# 10. PROJECT GENERATION
# ============================================================

def generate_project(
    skill,
    module,
    concepts,
    technologies,
):
    """
    Generate a project recommendation.
    """

    skill_text = safe_text(
        skill
    )


    module_text = safe_text(
        module
    )


    technology_text = (

        ", ".join(
            technologies[:4]
        )

        if technologies

        else

        "industry-standard technology"

    )


    concept_text = (

        ", ".join(
            concepts[:5]
        )

        if concepts

        else

        "core concepts"

    )


    return {

        "title":
            f"Industry Project - {skill_text}",

        "module":
            module_text
            or
            "Industry Application",

        "problem_statement":
            (
                f"Design and implement a real-world solution "
                f"using {skill_text}."
            ),

        "technologies":
            technology_text,

        "concepts":
            concept_text,

        "scope": [

            "Problem definition",

            "Data / input preparation",

            "System implementation",

            "Testing",

            "Evaluation",

            "Documentation",

            "Presentation",

        ],

        "deliverables": [

            "Source code",

            "README",

            "Technical documentation",

            "Demo",

            "Evaluation report",

        ],

    }


# ============================================================
# 11. LEARNING OUTCOME GENERATION
# ============================================================

def generate_learning_outcomes(
    skill,
    concepts,
):
    """
    Generate baseline measurable learning outcomes.
    """

    skill_text = safe_text(
        skill
    )


    outcomes = [

        (
            f"Explain the fundamental concepts of "
            f"{skill_text}."
        ),

        (
            f"Apply {skill_text} concepts to a "
            "practical problem."
        ),

        (
            f"Implement a solution using "
            f"{skill_text}."
        ),

        (
            f"Evaluate the effectiveness of a "
            f"{skill_text} solution."
        ),

        (
            f"Develop an industry-oriented project "
            f"using {skill_text}."
        ),

    ]


    if concepts:

        outcomes.append(

            (
                "Integrate the following concepts: "
                +
                ", ".join(
                    concepts[:4]
                )
                +
                "."
            )

        )


    return unique_values(
        outcomes
    )


# ============================================================
# 12. ASSESSMENT RECOMMENDATIONS
# ============================================================

def generate_assessment_plan(
    skill,
    priority_score,
):
    """
    Recommend assessment methods.
    """

    score = safe_number(
        priority_score
    )


    assessments = [

        "Conceptual MCQ",

        "Short-answer questions",

        "Hands-on coding exercise",

    ]


    if score >= 70:

        assessments.extend([

            "Practical laboratory evaluation",

            "Industry case study",

            "Mini project",

        ])


    if score >= 85:

        assessments.extend([

            "Interview-style technical assessment",

            "Production-oriented project",

        ])


    return unique_values(
        assessments
    )


# ============================================================
# 13. BUILD ENHANCEMENT BLUEPRINT
# ============================================================

def build_blueprint(
    item,
):
    """
    Convert a module gap into a complete enhancement blueprint.
    """

    skill = safe_text(

        item.get(
            "jd_skill"
        )

    )


    module = safe_text(

        item.get(
            "existing_module"
        )

    )


    action = safe_text(

        item.get(
            "recommended_action"
        )

    )


    gap_type = safe_text(

        item.get(
            "gap_type"
        )

    )


    priority_score = safe_number(

        item.get(
            "priority_score",
            0,
        )

    )


    priority_level = safe_text(

        item.get(
            "priority_level"
        ),

        "P2 - Medium",

    )


    # --------------------------------------------------------
    # Domain intelligence
    # --------------------------------------------------------

    domain_data = get_domain_recommendations(

        skill,

        gap_type,

        module,

    )


    concepts = domain_data[
        "concepts"
    ]


    tools = domain_data[
        "tools"
    ]


    technologies = domain_data[
        "technologies"
    ]


    # --------------------------------------------------------
    # Existing content
    # --------------------------------------------------------

    existing_topic = safe_text(

        item.get(
            "existing_topic"
        )

    )


    existing_concept = safe_text(

        item.get(
            "existing_concept"
        )

    )


    existing_tool = safe_text(

        item.get(
            "existing_tool"
        )

    )


    existing_technology = safe_text(

        item.get(
            "existing_technology"
        )

    )


    existing_framework = safe_text(

        item.get(
            "existing_framework"
        )

    )


    # --------------------------------------------------------
    # Depth and hours
    # --------------------------------------------------------

    depth = determine_depth(
        item
    )


    hours = determine_hours(
        item
    )


    # --------------------------------------------------------
    # Topic
    # --------------------------------------------------------

    if existing_topic:

        recommended_topic = (
            existing_topic
        )

    else:

        recommended_topic = (
            f"{skill} - Industry Applications"
        )


    # --------------------------------------------------------
    # Module
    # --------------------------------------------------------

    if module:

        recommended_module = module

    else:

        recommended_module = (
            f"New Module: {skill}"
        )


    # --------------------------------------------------------
    # Practical Lab
    # --------------------------------------------------------

    lab = generate_lab(

        skill,

        recommended_module,

        concepts,

        tools,

    )


    # --------------------------------------------------------
    # Project
    # --------------------------------------------------------

    project = generate_project(

        skill,

        recommended_module,

        concepts,

        technologies,

    )


    # --------------------------------------------------------
    # Learning outcomes
    # --------------------------------------------------------

    learning_outcomes = generate_learning_outcomes(

        skill,

        concepts,

    )


    # --------------------------------------------------------
    # Assessments
    # --------------------------------------------------------

    assessments = generate_assessment_plan(

        skill,

        priority_score,

    )


    # --------------------------------------------------------
    # Recommended changes
    # --------------------------------------------------------

    changes = []


    if action:

        changes.append(
            action
        )


    if not existing_topic:

        changes.append(
            "Add new topic"
        )


    if not existing_concept:

        changes.append(
            "Add industry concepts"
        )


    if not existing_tool:

        changes.append(
            "Add practical tools"
        )


    if not existing_technology:

        changes.append(
            "Add industry technology"
        )


    changes.append(
        "Add hands-on practice"
    )


    if priority_score >= 70:

        changes.append(
            "Add industry project"
        )


    return {

        # ====================================================
        # Identity
        # ====================================================

        "jd_skill":
            skill,

        "priority_score":
            priority_score,

        "priority_level":
            priority_level,

        "gap_type":
            gap_type,

        "action":
            action,

        # ====================================================
        # Curriculum mapping
        # ====================================================

        "existing_module":
            module,

        "recommended_module":
            recommended_module,

        "existing_topic":
            existing_topic,

        "recommended_topic":
            recommended_topic,

        # ====================================================
        # Concepts
        # ====================================================

        "existing_concept":
            existing_concept,

        "recommended_concepts":
            concepts,

        # ====================================================
        # Tools
        # ====================================================

        "existing_tool":
            existing_tool,

        "recommended_tools":
            tools,

        # ====================================================
        # Technologies
        # ====================================================

        "existing_technology":
            existing_technology,

        "existing_framework":
            existing_framework,

        "recommended_technologies":
            technologies,

        # ====================================================
        # Domains
        # ====================================================

        "domains":
            domain_data[
                "domains"
            ],

        # ====================================================
        # Learning depth
        # ====================================================

        "recommended_depth":
            depth,

        "recommended_hours":
            hours,

        # ====================================================
        # Learning outcomes
        # ====================================================

        "learning_outcomes":
            learning_outcomes,

        # ====================================================
        # Practical
        # ====================================================

        "lab":
            lab,

        "project":
            project,

        # ====================================================
        # Assessment
        # ====================================================

        "assessment_methods":
            assessments,

        # ====================================================
        # Change list
        # ====================================================

        "recommended_changes":
            unique_values(
                changes
            ),

    }


# ============================================================
# 14. GENERATE BLUEPRINTS
# ============================================================

enhancement_blueprint = [

    build_blueprint(
        item
    )

    for item in module_gap_mapping

]


# ============================================================
# 15. REMOVE DUPLICATE SKILLS
# ============================================================

unique_blueprints = []


seen_skills = set()


for blueprint in enhancement_blueprint:

    skill = normalize_match_text(

        blueprint.get(
            "jd_skill"
        )

    )


    if not skill:

        continue


    if skill in seen_skills:

        continue


    seen_skills.add(
        skill
    )


    unique_blueprints.append(
        blueprint
    )


enhancement_blueprint = (
    unique_blueprints
)


# ============================================================
# 16. SAVE BLUEPRINT
# ============================================================

st.session_state[
    "enhancement_blueprint"
] = enhancement_blueprint


# ============================================================
# 17. AGGREGATE CONCEPTS
# ============================================================

enhancement_concepts = []


for blueprint in enhancement_blueprint:

    enhancement_concepts.extend(

        blueprint.get(
            "recommended_concepts",
            []
        )

    )


enhancement_concepts = unique_values(
    enhancement_concepts
)


st.session_state[
    "enhancement_concepts"
] = enhancement_concepts


# ============================================================
# 18. AGGREGATE TOOLS
# ============================================================

enhancement_tools = []


for blueprint in enhancement_blueprint:

    enhancement_tools.extend(

        blueprint.get(
            "recommended_tools",
            []
        )

    )


enhancement_tools = unique_values(
    enhancement_tools
)


st.session_state[
    "enhancement_tools"
] = enhancement_tools


# ============================================================
# 19. AGGREGATE TECHNOLOGIES
# ============================================================

enhancement_technologies = []


for blueprint in enhancement_blueprint:

    enhancement_technologies.extend(

        blueprint.get(
            "recommended_technologies",
            []
        )

    )


enhancement_technologies = unique_values(
    enhancement_technologies
)


st.session_state[
    "enhancement_technologies"
] = enhancement_technologies


# ============================================================
# 20. AGGREGATE PROJECTS
# ============================================================

enhancement_projects = []


for blueprint in enhancement_blueprint:

    project = blueprint.get(
        "project"
    )


    if project:

        enhancement_projects.append(
            project
        )


st.session_state[
    "enhancement_projects"
] = enhancement_projects


# ============================================================
# 21. AGGREGATE LABS
# ============================================================

enhancement_labs = []


for blueprint in enhancement_blueprint:

    lab = blueprint.get(
        "lab"
    )


    if lab:

        enhancement_labs.append(
            lab
        )


st.session_state[
    "enhancement_labs"
] = enhancement_labs


# ============================================================
# 22. AGGREGATE LEARNING OUTCOMES
# ============================================================

enhancement_learning_outcomes = []


for blueprint in enhancement_blueprint:

    enhancement_learning_outcomes.extend(

        blueprint.get(
            "learning_outcomes",
            []
        )

    )


enhancement_learning_outcomes = unique_values(

    enhancement_learning_outcomes

)


st.session_state[
    "enhancement_learning_outcomes"
] = (
    enhancement_learning_outcomes
)


# ============================================================
# 23. DISPLAY BLUEPRINT SUMMARY
# ============================================================

st.divider()

st.subheader(
    "🧠 Curriculum Enhancement Blueprint"
)


blueprint_columns = st.columns(
    5
)


with blueprint_columns[0]:

    st.metric(

        "Enhancement Items",

        len(
            enhancement_blueprint
        ),

    )


with blueprint_columns[1]:

    st.metric(

        "Concepts",

        len(
            enhancement_concepts
        ),

    )


with blueprint_columns[2]:

    st.metric(

        "Tools",

        len(
            enhancement_tools
        ),

    )


with blueprint_columns[3]:

    st.metric(

        "Technologies",

        len(
            enhancement_technologies
        ),

    )


with blueprint_columns[4]:

    st.metric(

        "Projects",

        len(
            enhancement_projects
        ),

    )


# ============================================================
# 24. BLUEPRINT TABLE
# ============================================================

if enhancement_blueprint:

    blueprint_rows = []


    for blueprint in enhancement_blueprint:

        blueprint_rows.append({

            "Skill":
                blueprint.get(
                    "jd_skill"
                ),

            "Priority":
                blueprint.get(
                    "priority_score"
                ),

            "Module":
                blueprint.get(
                    "recommended_module"
                ),

            "Topic":
                blueprint.get(
                    "recommended_topic"
                ),

            "Action":
                blueprint.get(
                    "action"
                ),

            "Depth":
                blueprint.get(
                    "recommended_depth"
                ),

            "Hours":
                blueprint.get(
                    "recommended_hours"
                ),

            "Tools":
                ", ".join(

                    blueprint.get(
                        "recommended_tools",
                        []
                    )[:4]

                ),

            "Technologies":
                ", ".join(

                    blueprint.get(
                        "recommended_technologies",
                        []
                    )[:4]

                ),

        })


    blueprint_df = pd.DataFrame(
        blueprint_rows
    )


    st.session_state[
        "enhancement_blueprint_df"
    ] = blueprint_df


    st.dataframe(

        blueprint_df,

        use_container_width=True,

        hide_index=True,

    )


# ============================================================
# 25. BLUEPRINT DETAILS
# ============================================================

if enhancement_blueprint:

    st.divider()

    st.subheader(
        "📖 Detailed Enhancement Blueprint"
    )


    for blueprint in enhancement_blueprint:

        skill = safe_text(

            blueprint.get(
                "jd_skill"
            )

        )


        priority = safe_number(

            blueprint.get(
                "priority_score",
                0,
            )

        )


        with st.expander(

            f"""
            🔹 {skill}
            —
            {priority}/100
            """,

            expanded=False,

        ):

            left, right = st.columns(
                2
            )


            with left:

                st.markdown(
                    "### 📚 Curriculum"
                )


                st.write(

                    "**Recommended Module:**",

                    blueprint.get(
                        "recommended_module"
                    ),

                )


                st.write(

                    "**Recommended Topic:**",

                    blueprint.get(
                        "recommended_topic"
                    ),

                )


                st.write(

                    "**Action:**",

                    blueprint.get(
                        "action"
                    ),

                )


                st.write(

                    "**Depth:**",

                    blueprint.get(
                        "recommended_depth"
                    ),

                )


                st.write(

                    "**Recommended Hours:**",

                    blueprint.get(
                        "recommended_hours"
                    ),

                )


            with right:

                st.markdown(
                    "### 🛠 Industry Stack"
                )


                st.write(

                    "**Concepts:**",

                    ", ".join(

                        blueprint.get(
                            "recommended_concepts",
                            []
                        )

                    ),

                )


                st.write(

                    "**Tools:**",

                    ", ".join(

                        blueprint.get(
                            "recommended_tools",
                            []
                        )

                    ),

                )


                st.write(

                    "**Technologies:**",

                    ", ".join(

                        blueprint.get(
                            "recommended_technologies",
                            []
                        )

                    ),

                )


            st.markdown(
                "### 🎯 Learning Outcomes"
            )


            for outcome in blueprint.get(

                "learning_outcomes",
                [],

            ):

                st.markdown(
                    f"- {outcome}"
                )


            st.markdown(
                "### 🧪 Practical Lab"
            )


            lab = blueprint.get(
                "lab",
                {}
            )


            if lab:

                st.write(

                    "**Lab:**",

                    lab.get(
                        "title"
                    ),

                )


                st.write(

                    "**Objective:**",

                    lab.get(
                        "objective"
                    ),

                )


                for activity in lab.get(

                    "activities",
                    [],

                ):

                    st.markdown(

                        f"- {activity}"

                    )


            st.markdown(
                "### 🚀 Recommended Project"
            )


            project = blueprint.get(
                "project",
                {}
            )


            if project:

                st.write(

                    "**Project:**",

                    project.get(
                        "title"
                    ),

                )


                st.write(

                    "**Problem:**",

                    project.get(
                        "problem_statement"
                    ),

                )


                st.write(

                    "**Technologies:**",

                    project.get(
                        "technologies"
                    ),

                )


# ============================================================
# 26. CURRICULUM ENHANCEMENT INVENTORY
# ============================================================

st.divider()

st.subheader(
    "📦 Enhancement Inventory"
)


inventory_col1, inventory_col2 = (
    st.columns(2)
)


with inventory_col1:

    st.markdown(
        "### 🧠 Concepts to Add / Deepen"
    )


    for concept in enhancement_concepts:

        st.markdown(
            f"- {concept}"
        )


with inventory_col2:

    st.markdown(
        "### 🛠 Tools & Technologies"
    )


    for tool in enhancement_tools:

        st.markdown(
            f"- {tool}"
        )


    st.markdown(
        "#### Technologies"
    )


    for technology in enhancement_technologies:

        st.markdown(
            f"- {technology}"
        )


# ============================================================
# 27. PROJECT ROADMAP PREVIEW
# ============================================================

if enhancement_projects:

    st.divider()

    st.subheader(
        "🚀 Project Roadmap Preview"
    )


    project_rows = []


    for project in enhancement_projects:

        project_rows.append({

            "Project":
                project.get(
                    "title"
                ),

            "Module":
                project.get(
                    "module"
                ),

            "Technologies":
                project.get(
                    "technologies"
                ),

            "Concepts":
                project.get(
                    "concepts"
                ),

        })


    st.dataframe(

        pd.DataFrame(
            project_rows
        ),

        use_container_width=True,

        hide_index=True,

    )


# ============================================================
# 28. EXPORT BLUEPRINT
# ============================================================

if enhancement_blueprint:

    st.download_button(

        "⬇️ Download Enhancement Blueprint JSON",

        data=serialize_json(

            enhancement_blueprint

        ),

        file_name=(

            "curriculum_enhancement_blueprint.json"

        ),

        mime="application/json",

        key="download_enhancement_blueprint_json",

    )


# ============================================================
# 29. COMPLETION FLAG
# ============================================================

st.session_state[
    "enhancement_blueprint_complete"
] = bool(
    enhancement_blueprint
)


# ============================================================
# 30. STATUS
# ============================================================

if enhancement_blueprint:

    st.success(
        """
        ✅ **Curriculum Enhancement Blueprint Generated**

        The deterministic engine has converted industry gaps
        into proposed:

        **Modules → Topics → Concepts → Tools → Technologies
        → Labs → Projects → Learning Outcomes → Assessments.**

        The next stage is Expert AI review.
        """
    )


# ============================================================
# END OF CHUNK 4/10
# ============================================================
# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 5/10
# CURRICULUM EXPERT AGENT
# ============================================================

"""
Purpose
-------
Use an LLM-powered Curriculum / Industry Expert Agent to
review the deterministic enhancement blueprint.

Pipeline
--------

Deterministic Analysis
        │
        ▼
Enhancement Blueprint
        │
        ▼
Curriculum Expert Agent
        │
        ▼
Expert Recommendations
        │
        ▼
Critic Agent
        │
        ▼
Final Enhancement Agent


Technology
----------

Groq
Llama
LangChain

Environment variable
--------------------

GROQ_API_KEY

Optional:

GROQ_MODEL

Default model:

llama-3.3-70b-versatile


Output
------

st.session_state["expert_enhancement_analysis"]

st.session_state["expert_recommendations"]

st.session_state["expert_agent_complete"]
"""


# ============================================================
# 1. IMPORTS
# ============================================================

import os
import json
from typing import Any, Dict, List


# ============================================================
# 2. LANGCHAIN IMPORTS
# ============================================================

try:

    from langchain_groq import ChatGroq

    from langchain_core.prompts import ChatPromptTemplate

except ImportError:

    ChatGroq = None

    ChatPromptTemplate = None


# ============================================================
# 3. LOAD CURRENT BLUEPRINT
# ============================================================

enhancement_blueprint = st.session_state.get(
    "enhancement_blueprint",
    []
)


module_gap_mapping = st.session_state.get(
    "module_gap_mapping",
    []
)


prioritized_gaps = st.session_state.get(
    "prioritized_gaps",
    []
)


enhancement_concepts = st.session_state.get(
    "enhancement_concepts",
    []
)


enhancement_tools = st.session_state.get(
    "enhancement_tools",
    []
)


enhancement_technologies = st.session_state.get(
    "enhancement_technologies",
    []
)


enhancement_projects = st.session_state.get(
    "enhancement_projects",
    []
)


# ============================================================
# 4. LOAD CURRICULUM / JD DATA
# ============================================================

curriculum_skill_intelligence = st.session_state.get(
    "curriculum_skill_intelligence",
    {}
)


jd_skill_intelligence = st.session_state.get(
    "jd_skill_intelligence",
    {}
)


industry_gap_analysis = st.session_state.get(
    "industry_gap_analysis",
    {}
)


# ============================================================
# 5. VALIDATION
# ============================================================

if not enhancement_blueprint:

    st.warning(
        """
        ⚠️ Enhancement Blueprint is not available.

        Complete Chunks 1–4 before running the Expert Agent.
        """
    )


# ============================================================
# 6. GROQ CONFIGURATION
# ============================================================

DEFAULT_GROQ_MODEL = (
    "llama-3.3-70b-versatile"
)


groq_api_key = os.getenv(
    "GROQ_API_KEY",
    "",
).strip()


groq_model = os.getenv(
    "GROQ_MODEL",
    DEFAULT_GROQ_MODEL,
).strip()


# ============================================================
# 7. OPTIONAL STREAMLIT SECRET SUPPORT
# ============================================================

if not groq_api_key:

    try:

        groq_api_key = st.secrets.get(
            "GROQ_API_KEY",
            "",
        )

    except Exception:

        groq_api_key = ""


groq_api_key = safe_text(
    groq_api_key
)


# ============================================================
# 8. MODEL FACTORY
# ============================================================

def create_expert_llm():
    """
    Create Groq LLM.

    Returns
    -------
    ChatGroq or None
    """

    if ChatGroq is None:

        return None


    if not groq_api_key:

        return None


    try:

        return ChatGroq(

            api_key=groq_api_key,

            model=groq_model,

            temperature=0.1,

            max_tokens=8000,

        )

    except TypeError:

        # ----------------------------------------------------
        # Compatibility fallback for older versions
        # ----------------------------------------------------

        try:

            return ChatGroq(

                groq_api_key=groq_api_key,

                model=groq_model,

                temperature=0.1,

                max_tokens=8000,

            )

        except Exception:

            return None

    except Exception:

        return None


# ============================================================
# 9. CREATE MODEL
# ============================================================

expert_llm = create_expert_llm()


# ============================================================
# 10. EXPERT SYSTEM PROMPT
# ============================================================

EXPERT_SYSTEM_PROMPT = """
You are a senior Curriculum Intelligence Expert,
Industry Skills Architect, University Curriculum Designer,
and AI Engineering Education Expert.

Your task is to critically review an existing academic
curriculum against current industry requirements.

You must NOT blindly accept the proposed enhancements.

You must determine:

1. Which industry requirements are genuinely important.
2. Which curriculum gaps are real.
3. Which proposed additions are redundant.
4. Which existing topics can be enhanced instead of adding
   duplicate topics.
5. Which concepts require deeper coverage.
6. Which tools are actually relevant.
7. Which technologies are currently industry-relevant.
8. Which projects should be added.
9. Which projects should be rejected as too generic.
10. Which modules should be changed.
11. Which new modules are genuinely required.
12. Whether the recommended learning hours are realistic.
13. Whether the proposed learning outcomes are measurable.
14. Whether the enhancement is appropriate for academic
    education and employability.

IMPORTANT PRINCIPLES

- Do not recommend a technology simply because it appears
  in one JD.
- Prefer durable concepts over short-lived tools.
- Prefer industry-relevant tools for practical exposure.
- Avoid unnecessary curriculum expansion.
- Avoid duplicate concepts.
- Do not convert every JD keyword into a separate topic.
- Distinguish foundational knowledge from tool-specific skills.
- Distinguish academic depth from job-oriented practical skills.
- Prioritize employability.
- Preserve academic fundamentals.
- Recommend practical projects where appropriate.
- Recommend hands-on work for important technologies.
- Identify obsolete or low-value curriculum components.
- Identify topics that should be reduced or merged.
- Consider prerequisites and learning sequence.
- Consider student workload.
- Consider faculty feasibility.
- Consider laboratory infrastructure.
- Consider whether the proposed hours are realistic.

You are an expert reviewer.

You must produce structured JSON.

Do not include Markdown fences.

Return ONLY valid JSON.
"""


# ============================================================
# 11. EXPERT USER PROMPT
# ============================================================

EXPERT_USER_PROMPT = """
Review the following curriculum intelligence package.

==============================
JD / INDUSTRY INTELLIGENCE
==============================

{jd_data}


==============================
CURRICULUM INTELLIGENCE
==============================

{curriculum_data}


==============================
INDUSTRY GAP ANALYSIS
==============================

{gap_data}


==============================
PRIORITIZED GAPS
==============================

{prioritized_gaps}


==============================
MODULE GAP MAPPING
==============================

{module_mapping}


==============================
DETERMINISTIC ENHANCEMENT BLUEPRINT
==============================

{enhancement_blueprint}


==============================
AGGREGATED CONCEPTS
==============================

{concepts}


==============================
AGGREGATED TOOLS
==============================

{tools}


==============================
AGGREGATED TECHNOLOGIES
==============================

{technologies}


==============================
CURRENT PROJECT RECOMMENDATIONS
==============================

{projects}


==============================
TASK
==============================

Perform a deep expert review.

For EVERY major gap determine:

- whether the gap is real
- importance
- recommended action
- existing module to modify
- topic to add or enhance
- concepts to add
- tools to add
- technologies to add
- project requirement
- practical requirement
- recommended hours
- learning depth
- prerequisites
- rationale
- risks

Also identify:

A. Topics that should be added.

B. Topics that should be enhanced.

C. Topics that should be merged.

D. Topics that should be removed or reduced.

E. New modules that are genuinely required.

F. Industry tools that should be introduced.

G. Industry technologies that should be introduced.

H. Projects that should be introduced.

I. Projects that should be rejected or simplified.

J. Concepts that should receive greater depth.

K. Curriculum sequencing problems.

L. Faculty delivery concerns.

M. Student workload concerns.

N. Academic fundamentals that must not be removed.

Finally provide a prioritized enhancement plan.

Use this JSON structure:

{
  "executive_summary": "...",

  "overall_curriculum_assessment": {
    "strengths": [],
    "weaknesses": [],
    "industry_alignment": 0,
    "academic_quality": 0,
    "employability_alignment": 0
  },

  "gap_reviews": [
    {
      "jd_skill": "",
      "gap_is_valid": true,
      "importance": "",
      "priority": "",
      "severity": "",
      "existing_module": "",
      "recommended_module": "",
      "recommended_topic": "",
      "action": "",
      "concepts_to_add": [],
      "tools_to_add": [],
      "technologies_to_add": [],
      "depth": "",
      "hours": 0,
      "practical_lab_required": true,
      "project_required": true,
      "prerequisites": [],
      "rationale": "",
      "risks": []
    }
  ],

  "topics_to_add": [],

  "topics_to_enhance": [],

  "topics_to_merge": [],

  "topics_to_reduce": [],

  "topics_to_remove": [],

  "new_modules": [],

  "tools_to_add": [],

  "technologies_to_add": [],

  "concepts_to_deepen": [],

  "projects_to_add": [],

  "projects_to_reject": [],

  "sequencing_recommendations": [],

  "faculty_considerations": [],

  "student_workload_considerations": [],

  "academic_fundamentals_to_preserve": [],

  "final_expert_recommendations": []
}
"""


# ============================================================
# 12. SAFE JSON EXTRACTION
# ============================================================

def extract_json_from_response(
    response_text,
):
    """
    Extract JSON even if the model accidentally returns
    Markdown fences or surrounding text.
    """

    text = safe_text(
        response_text
    )


    # --------------------------------------------------------
    # Remove Markdown fences
    # --------------------------------------------------------

    text = text.replace(
        "```json",
        "",
    )


    text = text.replace(
        "```",
        "",
    )


    text = text.strip()


    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:

        return json.loads(
            text
        )

    except Exception:

        pass


    # --------------------------------------------------------
    # Find first JSON object
    # --------------------------------------------------------

    start = text.find(
        "{"
    )


    end = text.rfind(
        "}"
    )


    if (

        start >= 0

        and

        end > start

    ):

        candidate = text[
            start:
            end + 1
        ]


        try:

            return json.loads(
                candidate
            )

        except Exception:

            pass


    return {

        "error":
            "Unable to parse expert agent JSON.",

        "raw_response":
            text,

    }


# ============================================================
# 13. CONVERT OBJECT TO COMPACT JSON
# ============================================================

def compact_json(
    value,
    max_chars=30000,
):
    """
    Convert data to JSON and truncate excessively large
    payloads to avoid unnecessary LLM context usage.
    """

    try:

        text = json.dumps(

            value,

            ensure_ascii=False,

            default=str,

        )

    except Exception:

        text = str(
            value
        )


    if len(text) <= max_chars:

        return text


    return (

        text[
            :max_chars
        ]

        +

        "\n...[TRUNCATED]..."

    )


# ============================================================
# 14. BUILD EXPERT PROMPT
# ============================================================

def build_expert_prompt():
    """
    Build final expert-agent prompt.
    """

    if ChatPromptTemplate is None:

        return None


    try:

        prompt = ChatPromptTemplate.from_messages([

            (
                "system",

                EXPERT_SYSTEM_PROMPT,

            ),

            (
                "human",

                EXPERT_USER_PROMPT,

            ),

        ])


        return prompt

    except Exception:

        return None


# ============================================================
# 15. RUN EXPERT AGENT
# ============================================================

def run_expert_agent():
    """
    Run Curriculum Expert Agent.

    Returns
    -------
    dict
    """

    if not enhancement_blueprint:

        return {

            "error":
                "Enhancement blueprint is empty."

        }


    if expert_llm is None:

        return {

            "error":
                (
                    "Groq LLM is not configured. "
                    "Set GROQ_API_KEY and install "
                    "langchain-groq."
                )

        }


    prompt = build_expert_prompt()


    if prompt is None:

        return {

            "error":
                (
                    "LangChain prompt could not be created."
                )

        }


    try:

        chain = (
            prompt
            |
            expert_llm
        )


        response = chain.invoke({

            "jd_data":
                compact_json(
                    jd_skill_intelligence
                ),

            "curriculum_data":
                compact_json(
                    curriculum_skill_intelligence
                ),

            "gap_data":
                compact_json(
                    industry_gap_analysis
                ),

            "prioritized_gaps":
                compact_json(
                    prioritized_gaps
                ),

            "module_mapping":
                compact_json(
                    module_gap_mapping
                ),

            "enhancement_blueprint":
                compact_json(
                    enhancement_blueprint
                ),

            "concepts":
                compact_json(
                    enhancement_concepts
                ),

            "tools":
                compact_json(
                    enhancement_tools
                ),

            "technologies":
                compact_json(
                    enhancement_technologies
                ),

            "projects":
                compact_json(
                    enhancement_projects
                ),

        })


        # ----------------------------------------------------
        # Extract model content
        # ----------------------------------------------------

        if hasattr(
            response,
            "content",
        ):

            response_text = response.content

        else:

            response_text = str(
                response
            )


        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        result = extract_json_from_response(

            response_text

        )


        # ----------------------------------------------------
        # Add metadata
        # ----------------------------------------------------

        result["_metadata"] = {

            "agent":
                "Curriculum Expert Agent",

            "model":
                groq_model,

            "provider":
                "Groq",

            "framework":
                "LangChain",

            "generated_at":
                datetime.now().isoformat(),

        }


        return result


    except Exception as exc:

        return {

            "error":
                str(
                    exc
                ),

            "_metadata": {

                "agent":
                    "Curriculum Expert Agent",

                "model":
                    groq_model,

            },

        }


# ============================================================
# 16. EXPERT AGENT UI
# ============================================================

st.divider()

st.subheader(
    "🧠 Curriculum Expert Agent"
)


st.markdown(
    """
The **Expert Agent** independently reviews the proposed
curriculum enhancements against the supplied industry
requirements.

It can:

- Validate gaps
- Reject unnecessary additions
- Recommend deeper concepts
- Recommend industry tools
- Recommend technologies
- Improve project recommendations
- Recommend module changes
- Identify sequencing problems
- Protect important academic fundamentals
"""
)


# ============================================================
# 17. CONFIGURATION STATUS
# ============================================================

config_col1, config_col2, config_col3 = (
    st.columns(3)
)


with config_col1:

    if groq_api_key:

        st.success(
            "✅ GROQ_API_KEY detected"
        )

    else:

        st.error(
            "❌ GROQ_API_KEY missing"
        )


with config_col2:

    if ChatGroq is not None:

        st.success(
            "✅ langchain-groq available"
        )

    else:

        st.error(
            "❌ langchain-groq missing"
        )


with config_col3:

    st.info(
        f"Model: {groq_model}"
    )


# ============================================================
# 18. RUN BUTTON
# ============================================================

run_expert = st.button(

    "🚀 Run Curriculum Expert Agent",

    type="primary",

    use_container_width=True,

    disabled=(

        not enhancement_blueprint

        or

        expert_llm is None

    ),

)


# ============================================================
# 19. EXECUTE EXPERT AGENT
# ============================================================

if run_expert:

    with st.spinner(

        """
        🧠 Expert Agent is analysing curriculum,
        industry requirements and proposed enhancements...
        """

    ):

        expert_result = run_expert_agent()


    st.session_state[
        "expert_enhancement_analysis"
    ] = expert_result


    st.session_state[
        "expert_agent_complete"
    ] = bool(

        expert_result

        and

        not expert_result.get(
            "error"
        )

    )


# ============================================================
# 20. LOAD EXISTING RESULT
# ============================================================

expert_result = st.session_state.get(

    "expert_enhancement_analysis",

    {}

)


# ============================================================
# 21. HANDLE ERROR
# ============================================================

if expert_result.get(
    "error"
):

    st.error(

        expert_result.get(
            "error"
        )

    )


# ============================================================
# 22. DISPLAY EXPERT SUMMARY
# ============================================================

if (

    expert_result

    and

    not expert_result.get(
        "error"
    )

):

    st.success(
        "✅ Expert Agent analysis completed."
    )


    executive_summary = safe_text(

        expert_result.get(
            "executive_summary"
        )

    )


    if executive_summary:

        st.markdown(
            "### 📌 Expert Executive Summary"
        )


        st.info(
            executive_summary
        )


# ============================================================
# 23. OVERALL ASSESSMENT
# ============================================================

if expert_result:

    overall = expert_result.get(

        "overall_curriculum_assessment",

        {}

    )


    if isinstance(
        overall,
        dict,
    ):

        st.markdown(
            "### 📊 Expert Curriculum Assessment"
        )


        assessment_cols = st.columns(
            3
        )


        with assessment_cols[0]:

            st.metric(

                "Industry Alignment",

                overall.get(
                    "industry_alignment",
                    0,
                ),

            )


        with assessment_cols[1]:

            st.metric(

                "Academic Quality",

                overall.get(
                    "academic_quality",
                    0,
                ),

            )


        with assessment_cols[2]:

            st.metric(

                "Employability",

                overall.get(
                    "employability_alignment",
                    0,
                ),

            )


# ============================================================
# 24. EXPERT GAP REVIEW
# ============================================================

gap_reviews = expert_result.get(

    "gap_reviews",

    []

)


if gap_reviews:

    st.divider()

    st.subheader(
        "🔬 Expert Gap Review"
    )


    for review in gap_reviews:

        if not isinstance(
            review,
            dict,
        ):

            continue


        skill = safe_text(

            review.get(
                "jd_skill"
            ),

            "Industry Requirement",

        )


        valid = review.get(
            "gap_is_valid",
            True,
        )


        if valid:

            icon = "✅"

        else:

            icon = "❌"


        with st.expander(

            f"""
            {icon} {skill}
            """

        ):

            col1, col2 = st.columns(
                2
            )


            with col1:

                st.write(

                    "**Gap Valid:**",

                    "Yes"
                    if valid
                    else
                    "No",

                )


                st.write(

                    "**Importance:**",

                    review.get(
                        "importance"
                    ),

                )


                st.write(

                    "**Priority:**",

                    review.get(
                        "priority"
                    ),

                )


                st.write(

                    "**Severity:**",

                    review.get(
                        "severity"
                    ),

                )


                st.write(

                    "**Recommended Action:**",

                    review.get(
                        "action"
                    ),

                )


            with col2:

                st.write(

                    "**Recommended Module:**",

                    review.get(
                        "recommended_module"
                    ),

                )


                st.write(

                    "**Recommended Topic:**",

                    review.get(
                        "recommended_topic"
                    ),

                )


                st.write(

                    "**Depth:**",

                    review.get(
                        "depth"
                    ),

                )


                st.write(

                    "**Hours:**",

                    review.get(
                        "hours"
                    ),

                )


            concepts = normalize_list(

                review.get(
                    "concepts_to_add"
                )

            )


            tools = normalize_list(

                review.get(
                    "tools_to_add"
                )

            )


            technologies = normalize_list(

                review.get(
                    "technologies_to_add"
                )

            )


            prerequisites = normalize_list(

                review.get(
                    "prerequisites"
                )

            )


            if concepts:

                st.markdown(
                    "#### 🧠 Concepts"
                )


                for concept in concepts:

                    st.markdown(
                        f"- {concept}"
                    )


            if tools:

                st.markdown(
                    "#### 🛠 Tools"
                )


                for tool in tools:

                    st.markdown(
                        f"- {tool}"
                    )


            if technologies:

                st.markdown(
                    "#### ⚙️ Technologies"
                )


                for technology in technologies:

                    st.markdown(
                        f"- {technology}"
                    )


            if prerequisites:

                st.markdown(
                    "#### 🔗 Prerequisites"
                )


                for prerequisite in prerequisites:

                    st.markdown(
                        f"- {prerequisite}"
                    )


            rationale = safe_text(

                review.get(
                    "rationale"
                )

            )


            if rationale:

                st.markdown(
                    "#### 💡 Rationale"
                )


                st.write(
                    rationale
                )


# ============================================================
# 25. TOPICS TO ADD
# ============================================================

topics_to_add = normalize_list(

    expert_result.get(
        "topics_to_add"
    )

)


if topics_to_add:

    st.divider()

    st.subheader(
        "➕ Topics Recommended by Expert"
    )


    for topic in topics_to_add:

        st.markdown(
            f"- {topic}"
        )


# ============================================================
# 26. TOPICS TO ENHANCE
# ============================================================

topics_to_enhance = normalize_list(

    expert_result.get(
        "topics_to_enhance"
    )

)


if topics_to_enhance:

    st.subheader(
        "🔧 Topics to Enhance"
    )


    for topic in topics_to_enhance:

        st.markdown(
            f"- {topic}"
        )


# ============================================================
# 27. TOPICS TO MERGE
# ============================================================

topics_to_merge = normalize_list(

    expert_result.get(
        "topics_to_merge"
    )

)


if topics_to_merge:

    st.subheader(
        "🔗 Topics to Merge"
    )


    for topic in topics_to_merge:

        st.markdown(
            f"- {topic}"
        )


# ============================================================
# 28. TOPICS TO REDUCE
# ============================================================

topics_to_reduce = normalize_list(

    expert_result.get(
        "topics_to_reduce"
    )

)


if topics_to_reduce:

    st.subheader(
        "📉 Topics to Reduce"
    )


    for topic in topics_to_reduce:

        st.markdown(
            f"- {topic}"
        )


# ============================================================
# 29. NEW MODULES
# ============================================================

new_modules = normalize_list(

    expert_result.get(
        "new_modules"
    )

)


if new_modules:

    st.divider()

    st.subheader(
        "🆕 Expert Recommended Modules"
    )


    for module in new_modules:

        st.markdown(
            f"- {module}"
        )


# ============================================================
# 30. TOOLS
# ============================================================

expert_tools = normalize_list(

    expert_result.get(
        "tools_to_add"
    )

)


if expert_tools:

    st.subheader(
        "🛠 Industry Tools Recommended"
    )


    for tool in expert_tools:

        st.markdown(
            f"- {tool}"
        )


# ============================================================
# 31. TECHNOLOGIES
# ============================================================

expert_technologies = normalize_list(

    expert_result.get(
        "technologies_to_add"
    )

)


if expert_technologies:

    st.subheader(
        "⚙️ Technologies Recommended"
    )


    for technology in expert_technologies:

        st.markdown(
            f"- {technology}"
        )


# ============================================================
# 32. CONCEPTS TO DEEPEN
# ============================================================

concepts_to_deepen = normalize_list(

    expert_result.get(
        "concepts_to_deepen"
    )

)


if concepts_to_deepen:

    st.subheader(
        "🧠 Concepts Requiring Greater Depth"
    )


    for concept in concepts_to_deepen:

        st.markdown(
            f"- {concept}"
        )


# ============================================================
# 33. PROJECT RECOMMENDATIONS
# ============================================================

projects_to_add = normalize_list(

    expert_result.get(
        "projects_to_add"
    )

)


if projects_to_add:

    st.divider()

    st.subheader(
        "🚀 Expert Project Recommendations"
    )


    for project in projects_to_add:

        st.markdown(
            f"- {project}"
        )


# ============================================================
# 34. PROJECTS TO REJECT
# ============================================================

projects_to_reject = normalize_list(

    expert_result.get(
        "projects_to_reject"
    )

)


if projects_to_reject:

    st.subheader(
        "❌ Projects Expert Recommends Rejecting"
    )


    for project in projects_to_reject:

        st.markdown(
            f"- {project}"
        )


# ============================================================
# 35. SEQUENCING
# ============================================================

sequencing = normalize_list(

    expert_result.get(
        "sequencing_recommendations"
    )

)


if sequencing:

    st.divider()

    st.subheader(
        "🔀 Curriculum Sequencing Recommendations"
    )


    for item in sequencing:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 36. FACULTY CONSIDERATIONS
# ============================================================

faculty_considerations = normalize_list(

    expert_result.get(
        "faculty_considerations"
    )

)


if faculty_considerations:

    st.subheader(
        "👨‍🏫 Faculty Delivery Considerations"
    )


    for item in faculty_considerations:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 37. STUDENT WORKLOAD
# ============================================================

student_workload = normalize_list(

    expert_result.get(
        "student_workload_considerations"
    )

)


if student_workload:

    st.subheader(
        "🎓 Student Workload Considerations"
    )


    for item in student_workload:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 38. ACADEMIC FUNDAMENTALS
# ============================================================

academic_fundamentals = normalize_list(

    expert_result.get(
        "academic_fundamentals_to_preserve"
    )

)


if academic_fundamentals:

    st.divider()

    st.subheader(
        "🎓 Academic Fundamentals to Preserve"
    )


    for item in academic_fundamentals:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 39. FINAL EXPERT RECOMMENDATIONS
# ============================================================

final_expert_recommendations = normalize_list(

    expert_result.get(
        "final_expert_recommendations"
    )

)


st.session_state[
    "expert_recommendations"
] = final_expert_recommendations


if final_expert_recommendations:

    st.divider()

    st.subheader(
        "⭐ Final Expert Recommendations"
    )


    for index, recommendation in enumerate(

        final_expert_recommendations,

        start=1,

    ):

        st.markdown(

            f"""
            **{index}.**
            {recommendation}
            """

        )


# ============================================================
# 40. SAVE COMPLETE EXPERT PACKAGE
# ============================================================

expert_package = {

    "expert_analysis":
        expert_result,

    "recommendations":
        final_expert_recommendations,

    "topics_to_add":
        topics_to_add,

    "topics_to_enhance":
        topics_to_enhance,

    "topics_to_merge":
        topics_to_merge,

    "topics_to_reduce":
        topics_to_reduce,

    "new_modules":
        new_modules,

    "tools_to_add":
        expert_tools,

    "technologies_to_add":
        expert_technologies,

    "concepts_to_deepen":
        concepts_to_deepen,

    "projects_to_add":
        projects_to_add,

    "projects_to_reject":
        projects_to_reject,

    "sequencing":
        sequencing,

    "faculty_considerations":
        faculty_considerations,

    "student_workload":
        student_workload,

    "academic_fundamentals":
        academic_fundamentals,

}


st.session_state[
    "expert_enhancement_package"
] = expert_package


# ============================================================
# 41. DOWNLOAD EXPERT ANALYSIS
# ============================================================

if (

    expert_result

    and

    not expert_result.get(
        "error"
    )

):

    st.download_button(

        "⬇️ Download Expert Analysis JSON",

        data=serialize_json(
            expert_result
        ),

        file_name=(
            "curriculum_expert_analysis.json"
        ),

        mime="application/json",

        key="download_expert_analysis",

    )


# ============================================================
# 42. COMPLETION STATUS
# ============================================================

if st.session_state.get(

    "expert_agent_complete",

    False,

):

    st.success(
        """
        ✅ **Expert Agent Review Complete**

        The proposed curriculum enhancements have now been
        independently reviewed by the Curriculum / Industry
        Expert Agent.

        The next stage is the **Critic Agent**, which will
        challenge these recommendations and identify:

        - Over-recommendations
        - Unsupported technologies
        - Duplicate topics
        - Unrealistic hours
        - Weak projects
        - Missing prerequisites
        - Academic quality risks
        - Industry alignment errors
        """
    )


# ============================================================
# END OF CHUNK 5/10
# ============================================================
# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 6/10
# CURRICULUM CRITIC AGENT
# ============================================================

"""
Purpose
-------
Independently critique the Expert Agent recommendations.

The Critic Agent must NOT simply agree with the Expert Agent.

It should identify:

    - Invalid gaps
    - Weak recommendations
    - Unsupported technologies
    - Tool over-dependence
    - Duplicate curriculum content
    - Excessive curriculum expansion
    - Unrealistic hours
    - Missing prerequisites
    - Weak projects
    - Poor sequencing
    - Academic quality risks
    - Industry alignment risks

Input
-----

1. Original curriculum
2. JD intelligence
3. Prioritized gaps
4. Module mapping
5. Deterministic blueprint
6. Expert Agent output

Output
------

st.session_state["critic_enhancement_analysis"]

st.session_state["critic_recommendations"]

st.session_state["critic_decisions"]

st.session_state["critic_agent_complete"]


Technology
----------

Groq
Llama
LangChain
"""


# ============================================================
# 1. LOAD EXPERT PACKAGE
# ============================================================

expert_enhancement_package = st.session_state.get(
    "expert_enhancement_package",
    {}
)


expert_enhancement_analysis = st.session_state.get(
    "expert_enhancement_analysis",
    {}
)


expert_recommendations = st.session_state.get(
    "expert_recommendations",
    []
)


# ============================================================
# 2. LOAD ORIGINAL ANALYSIS
# ============================================================

enhancement_blueprint = st.session_state.get(
    "enhancement_blueprint",
    []
)


module_gap_mapping = st.session_state.get(
    "module_gap_mapping",
    []
)


prioritized_gaps = st.session_state.get(
    "prioritized_gaps",
    []
)


curriculum_skill_intelligence = st.session_state.get(
    "curriculum_skill_intelligence",
    {}
)


jd_skill_intelligence = st.session_state.get(
    "jd_skill_intelligence",
    {}
)


industry_gap_analysis = st.session_state.get(
    "industry_gap_analysis",
    {}
)


# ============================================================
# 3. LOAD GROQ CONFIGURATION
# ============================================================

groq_api_key = os.getenv(
    "GROQ_API_KEY",
    "",
).strip()


groq_model = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
).strip()


if not groq_api_key:

    try:

        groq_api_key = st.secrets.get(
            "GROQ_API_KEY",
            "",
        )

    except Exception:

        groq_api_key = ""


groq_api_key = safe_text(
    groq_api_key
)


# ============================================================
# 4. CREATE CRITIC LLM
# ============================================================

def create_critic_llm():
    """
    Create independent LLM instance for the Critic Agent.
    """

    if ChatGroq is None:

        return None


    if not groq_api_key:

        return None


    try:

        return ChatGroq(

            api_key=groq_api_key,

            model=groq_model,

            temperature=0.0,

            max_tokens=8000,

        )

    except TypeError:

        try:

            return ChatGroq(

                groq_api_key=groq_api_key,

                model=groq_model,

                temperature=0.0,

                max_tokens=8000,

            )

        except Exception:

            return None

    except Exception:

        return None


critic_llm = create_critic_llm()


# ============================================================
# 5. CRITIC SYSTEM PROMPT
# ============================================================

CRITIC_SYSTEM_PROMPT = """
You are an independent Curriculum Critic Agent.

Your role is NOT to create new recommendations blindly.

Your role is to challenge the recommendations produced by
another AI Expert Agent.

You are a skeptical senior academic reviewer, industry
technical architect, curriculum accreditation reviewer,
and employability specialist.

You must determine whether the Expert Agent recommendations
are justified.

CRITICAL PRINCIPLES

1. Do not accept a recommendation merely because the Expert
   Agent proposed it.

2. Every major recommendation should have evidence from:
   - JD requirements
   - Multiple relevant industry skills
   - Curriculum gaps
   - Educational value

3. A single JD keyword should NOT automatically become a
   complete academic module.

4. Prefer concepts over temporary tools.

5. Tools should be added when they provide practical value.

6. Technologies should be included when they are relevant
   to the learning objective.

7. Do not unnecessarily increase curriculum size.

8. Detect duplicate or overlapping topics.

9. Detect unrealistic teaching hours.

10. Detect projects that are too generic.

11. Detect projects that are simply tool demonstrations.

12. Check whether prerequisites exist.

13. Check whether the sequence is pedagogically sound.

14. Protect academic fundamentals.

15. Separate:
      Foundation
      Intermediate
      Advanced
      Industry Practice

16. Identify recommendations that are:
      ACCEPT
      MODIFY
      REJECT
      MERGE

17. If a recommendation is weak, explain why.

18. If the Expert Agent missed an important requirement,
    identify it.

19. Do not invent unsupported industry requirements.

20. The final curriculum should remain academically strong,
    industry aligned, practical, and manageable.

CRITIC CHECKLIST

For each recommendation evaluate:

- Evidence strength
- Industry relevance
- Academic relevance
- Employability value
- Duplication risk
- Tool dependency
- Technology stability
- Implementation effort
- Student workload
- Faculty feasibility
- Prerequisites
- Learning depth
- Hours
- Project quality
- Assessment quality

Return ONLY valid JSON.

No Markdown fences.
"""


# ============================================================
# 6. CRITIC USER PROMPT
# ============================================================

CRITIC_USER_PROMPT = """
You are reviewing an AI-generated curriculum enhancement.

==============================
ORIGINAL JD INTELLIGENCE
==============================

{jd_data}


==============================
ORIGINAL CURRICULUM
==============================

{curriculum_data}


==============================
ORIGINAL GAP ANALYSIS
==============================

{gap_data}


==============================
PRIORITIZED GAPS
==============================

{prioritized_gaps}


==============================
MODULE GAP MAPPING
==============================

{module_mapping}


==============================
DETERMINISTIC BLUEPRINT
==============================

{blueprint}


==============================
EXPERT AGENT ANALYSIS
==============================

{expert_analysis}


==============================
EXPERT RECOMMENDATIONS
==============================

{expert_recommendations}


==============================
CRITIC TASK
==============================

Independently critique the Expert Agent.

For every important expert recommendation:

1. Decide:
   ACCEPT
   MODIFY
   REJECT
   MERGE

2. Explain the decision.

3. Identify supporting evidence.

4. Identify missing evidence.

5. Determine whether the recommendation is:
   - Industry justified
   - Academically justified
   - Employability justified

6. Check whether the recommendation duplicates an existing
   curriculum topic.

7. Check whether a tool is unnecessarily specific.

8. Check whether the proposed technology should instead be
   taught as a concept.

9. Check whether the recommended hours are realistic.

10. Check prerequisites.

11. Check project quality.

12. Check assessment quality.

13. Identify risks.

Also identify:

A. Expert recommendations that should be rejected.

B. Expert recommendations that should be modified.

C. Expert recommendations that should be merged.

D. Expert recommendations that should be accepted.

E. Important industry gaps the Expert missed.

F. Important academic topics the Expert incorrectly tried
   to remove or reduce.

G. Curriculum bloat risks.

H. Sequencing problems.

I. Workload risks.

J. Faculty feasibility risks.

K. Technology/tool volatility risks.

Finally produce a critic-approved recommendation set.

Return this exact JSON structure:

{
  "critic_summary": "",

  "overall_critic_score": 0,

  "quality_assessment": {
    "industry_alignment": 0,
    "academic_quality": 0,
    "employability": 0,
    "curriculum_manageability": 0
  },

  "recommendation_reviews": [
    {
      "jd_skill": "",
      "expert_action": "",
      "decision": "ACCEPT",
      "evidence_strength": 0,
      "industry_justification": "",
      "academic_justification": "",
      "employability_justification": "",
      "duplication_risk": "LOW",
      "tool_dependency_risk": "LOW",
      "workload_risk": "LOW",
      "hours_valid": true,
      "recommended_hours": 0,
      "prerequisites_missing": [],
      "modifications": [],
      "reason": "",
      "risks": []
    }
  ],

  "accepted_recommendations": [],

  "modified_recommendations": [],

  "rejected_recommendations": [],

  "merged_recommendations": [],

  "missed_industry_gaps": [],

  "academic_topics_to_preserve": [],

  "curriculum_bloat_risks": [],

  "sequencing_issues": [],

  "faculty_feasibility_issues": [],

  "student_workload_issues": [],

  "technology_volatility_risks": [],

  "critic_approved_recommendations": []
}
"""


# ============================================================
# 7. BUILD CRITIC PROMPT
# ============================================================

def build_critic_prompt():
    """
    Build LangChain ChatPromptTemplate for Critic Agent.
    """

    if ChatPromptTemplate is None:

        return None


    try:

        return ChatPromptTemplate.from_messages([

            (
                "system",

                CRITIC_SYSTEM_PROMPT,

            ),

            (
                "human",

                CRITIC_USER_PROMPT,

            ),

        ])

    except Exception:

        return None


# ============================================================
# 8. RUN CRITIC AGENT
# ============================================================

def run_critic_agent():
    """
    Execute independent Critic Agent.
    """

    if not expert_enhancement_analysis:

        return {

            "error":
                (
                    "Expert Agent analysis is not available."
                )

        }


    if critic_llm is None:

        return {

            "error":
                (
                    "Groq LLM is not configured. "
                    "Set GROQ_API_KEY and install "
                    "langchain-groq."
                )

        }


    prompt = build_critic_prompt()


    if prompt is None:

        return {

            "error":
                "Unable to create Critic Agent prompt."

        }


    try:

        chain = (
            prompt
            |
            critic_llm
        )


        response = chain.invoke({

            "jd_data":
                compact_json(
                    jd_skill_intelligence
                ),

            "curriculum_data":
                compact_json(
                    curriculum_skill_intelligence
                ),

            "gap_data":
                compact_json(
                    industry_gap_analysis
                ),

            "prioritized_gaps":
                compact_json(
                    prioritized_gaps
                ),

            "module_mapping":
                compact_json(
                    module_gap_mapping
                ),

            "blueprint":
                compact_json(
                    enhancement_blueprint
                ),

            "expert_analysis":
                compact_json(
                    expert_enhancement_analysis
                ),

            "expert_recommendations":
                compact_json(
                    expert_recommendations
                ),

        })


        if hasattr(
            response,
            "content",
        ):

            response_text = response.content

        else:

            response_text = str(
                response
            )


        result = extract_json_from_response(

            response_text

        )


        result["_metadata"] = {

            "agent":
                "Curriculum Critic Agent",

            "model":
                groq_model,

            "provider":
                "Groq",

            "framework":
                "LangChain",

            "temperature":
                0.0,

            "generated_at":
                datetime.now().isoformat(),

        }


        return result


    except Exception as exc:

        return {

            "error":
                str(
                    exc
                ),

            "_metadata": {

                "agent":
                    "Curriculum Critic Agent",

                "model":
                    groq_model,

            },

        }


# ============================================================
# 9. CRITIC UI
# ============================================================

st.divider()

st.subheader(
    "🧐 Critic Agent"
)


st.markdown(
    """
The Critic Agent is intentionally **independent and
skeptical**.

It does not simply approve the Expert Agent.

It challenges:

**Expert Recommendation → Evidence → Risk → Decision**

Possible decisions:

- ✅ ACCEPT
- 🔧 MODIFY
- 🔗 MERGE
- ❌ REJECT
"""
)


# ============================================================
# 10. INPUT STATUS
# ============================================================

critic_status_cols = st.columns(
    4
)


with critic_status_cols[0]:

    if expert_enhancement_analysis:

        st.success(
            "✅ Expert Analysis"
        )

    else:

        st.warning(
            "⏳ Expert Analysis"
        )


with critic_status_cols[1]:

    if enhancement_blueprint:

        st.success(
            "✅ Blueprint"
        )

    else:

        st.warning(
            "⏳ Blueprint"
        )


with critic_status_cols[2]:

    if groq_api_key:

        st.success(
            "✅ Groq"
        )

    else:

        st.error(
            "❌ Groq API Key"
        )


with critic_status_cols[3]:

    st.info(
        f"Model: {groq_model}"
    )


# ============================================================
# 11. RUN CRITIC BUTTON
# ============================================================

run_critic = st.button(

    "🧐 Run Independent Critic Agent",

    type="primary",

    use_container_width=True,

    disabled=(

        not expert_enhancement_analysis

        or

        critic_llm is None

    ),

)


# ============================================================
# 12. EXECUTE CRITIC
# ============================================================

if run_critic:

    with st.spinner(

        """
        🧐 Critic Agent is challenging the Expert Agent
        recommendations...
        """

    ):

        critic_result = run_critic_agent()


    st.session_state[
        "critic_enhancement_analysis"
    ] = critic_result


    st.session_state[
        "critic_agent_complete"
    ] = bool(

        critic_result

        and

        not critic_result.get(
            "error"
        )

    )


# ============================================================
# 13. LOAD CRITIC RESULT
# ============================================================

critic_result = st.session_state.get(

    "critic_enhancement_analysis",

    {}

)


# ============================================================
# 14. ERROR HANDLING
# ============================================================

if critic_result.get(
    "error"
):

    st.error(

        critic_result.get(
            "error"
        )

    )


# ============================================================
# 15. CRITIC SUMMARY
# ============================================================

if (

    critic_result

    and

    not critic_result.get(
        "error"
    )

):

    st.success(
        "✅ Critic Agent analysis completed."
    )


    critic_summary = safe_text(

        critic_result.get(
            "critic_summary"
        )

    )


    if critic_summary:

        st.info(
            critic_summary
        )


# ============================================================
# 16. CRITIC SCORE
# ============================================================

if critic_result:

    critic_score = safe_number(

        critic_result.get(
            "overall_critic_score",
            0,
        )

    )


    quality = critic_result.get(

        "quality_assessment",

        {}

    )


    score_cols = st.columns(
        5
    )


    with score_cols[0]:

        st.metric(

            "Critic Score",

            f"{critic_score:.0f}/100",

        )


    with score_cols[1]:

        st.metric(

            "Industry",

            quality.get(
                "industry_alignment",
                0,
            ),

        )


    with score_cols[2]:

        st.metric(

            "Academic",

            quality.get(
                "academic_quality",
                0,
            ),

        )


    with score_cols[3]:

        st.metric(

            "Employability",

            quality.get(
                "employability",
                0,
            ),

        )


    with score_cols[4]:

        st.metric(

            "Manageability",

            quality.get(
                "curriculum_manageability",
                0,
            ),

        )


# ============================================================
# 17. RECOMMENDATION REVIEWS
# ============================================================

recommendation_reviews = critic_result.get(

    "recommendation_reviews",

    []

)


if recommendation_reviews:

    st.divider()

    st.subheader(
        "🔬 Expert Recommendation Review"
    )


    review_rows = []


    for review in recommendation_reviews:

        if not isinstance(
            review,
            dict,
        ):

            continue


        decision = safe_text(

            review.get(
                "decision"
            ),

            "REVIEW",

        ).upper()


        if decision == "ACCEPT":

            icon = "✅"

        elif decision == "MODIFY":

            icon = "🔧"

        elif decision == "MERGE":

            icon = "🔗"

        elif decision == "REJECT":

            icon = "❌"

        else:

            icon = "⚠️"


        review_rows.append({

            "Decision":
                f"{icon} {decision}",

            "JD Skill":
                review.get(
                    "jd_skill"
                ),

            "Expert Action":
                review.get(
                    "expert_action"
                ),

            "Evidence":
                review.get(
                    "evidence_strength"
                ),

            "Duplication Risk":
                review.get(
                    "duplication_risk"
                ),

            "Tool Risk":
                review.get(
                    "tool_dependency_risk"
                ),

            "Workload Risk":
                review.get(
                    "workload_risk"
                ),

            "Hours Valid":
                review.get(
                    "hours_valid"
                ),

            "Recommended Hours":
                review.get(
                    "recommended_hours"
                ),

        })


    if review_rows:

        critic_df = pd.DataFrame(
            review_rows
        )


        st.dataframe(

            critic_df,

            use_container_width=True,

            hide_index=True,

        )


# ============================================================
# 18. DETAILED CRITIC REVIEWS
# ============================================================

for review in recommendation_reviews:

    if not isinstance(
        review,
        dict,
    ):

        continue


    skill = safe_text(

        review.get(
            "jd_skill"
        ),

        "Recommendation",

    )


    decision = safe_text(

        review.get(
            "decision"
        ),

        "REVIEW",

    ).upper()


    with st.expander(

        f"""
        {skill}
        — {decision}
        """

    ):

        col1, col2 = st.columns(
            2
        )


        with col1:

            st.write(

                "**Expert Action:**",

                review.get(
                    "expert_action"
                ),

            )


            st.write(

                "**Decision:**",

                decision,

            )


            st.write(

                "**Evidence Strength:**",

                review.get(
                    "evidence_strength"
                ),

            )


            st.write(

                "**Hours Valid:**",

                review.get(
                    "hours_valid"
                ),

            )


            st.write(

                "**Recommended Hours:**",

                review.get(
                    "recommended_hours"
                ),

            )


        with col2:

            st.write(

                "**Duplication Risk:**",

                review.get(
                    "duplication_risk"
                ),

            )


            st.write(

                "**Tool Dependency Risk:**",

                review.get(
                    "tool_dependency_risk"
                ),

            )


            st.write(

                "**Workload Risk:**",

                review.get(
                    "workload_risk"
                ),

            )


        industry_reason = safe_text(

            review.get(
                "industry_justification"
            )

        )


        academic_reason = safe_text(

            review.get(
                "academic_justification"
            )

        )


        employability_reason = safe_text(

            review.get(
                "employability_justification"
            )

        )


        if industry_reason:

            st.markdown(
                "### 🏭 Industry Justification"
            )


            st.write(
                industry_reason
            )


        if academic_reason:

            st.markdown(
                "### 🎓 Academic Justification"
            )


            st.write(
                academic_reason
            )


        if employability_reason:

            st.markdown(
                "### 💼 Employability Justification"
            )


            st.write(
                employability_reason
            )


        prerequisites = normalize_list(

            review.get(
                "prerequisites_missing"
            )

        )


        modifications = normalize_list(

            review.get(
                "modifications"
            )

        )


        risks = normalize_list(

            review.get(
                "risks"
            )

        )


        if prerequisites:

            st.markdown(
                "### 🔗 Missing Prerequisites"
            )


            for item in prerequisites:

                st.markdown(
                    f"- {item}"
                )


        if modifications:

            st.markdown(
                "### 🔧 Required Modifications"
            )


            for item in modifications:

                st.markdown(
                    f"- {item}"
                )


        if risks:

            st.markdown(
                "### ⚠️ Risks"
            )


            for item in risks:

                st.markdown(
                    f"- {item}"
                )


        reason = safe_text(

            review.get(
                "reason"
            )

        )


        if reason:

            st.markdown(
                "### 💡 Critic Reason"
            )


            st.info(
                reason
            )


# ============================================================
# 19. DECISION CATEGORIES
# ============================================================

accepted = normalize_list(

    critic_result.get(
        "accepted_recommendations"
    )

)


modified = normalize_list(

    critic_result.get(
        "modified_recommendations"
    )

)


rejected = normalize_list(

    critic_result.get(
        "rejected_recommendations"
    )

)


merged = normalize_list(

    critic_result.get(
        "merged_recommendations"
    )

)


decision_cols = st.columns(
    4
)


with decision_cols[0]:

    st.metric(
        "✅ Accepted",
        len(
            accepted
        ),
    )


with decision_cols[1]:

    st.metric(
        "🔧 Modified",
        len(
            modified
        ),
    )


with decision_cols[2]:

    st.metric(
        "🔗 Merged",
        len(
            merged
        ),
    )


with decision_cols[3]:

    st.metric(
        "❌ Rejected",
        len(
            rejected
        ),
    )


# ============================================================
# 20. ACCEPTED RECOMMENDATIONS
# ============================================================

if accepted:

    st.divider()

    st.subheader(
        "✅ Critic Accepted"
    )


    for item in accepted:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 21. MODIFIED RECOMMENDATIONS
# ============================================================

if modified:

    st.subheader(
        "🔧 Critic Modified"
    )


    for item in modified:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 22. MERGED RECOMMENDATIONS
# ============================================================

if merged:

    st.subheader(
        "🔗 Critic Suggested Merge"
    )


    for item in merged:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 23. REJECTED RECOMMENDATIONS
# ============================================================

if rejected:

    st.subheader(
        "❌ Critic Rejected"
    )


    for item in rejected:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 24. MISSED INDUSTRY GAPS
# ============================================================

missed_industry_gaps = normalize_list(

    critic_result.get(
        "missed_industry_gaps"
    )

)


if missed_industry_gaps:

    st.divider()

    st.subheader(
        "🚨 Industry Gaps Missed by Expert"
    )


    for item in missed_industry_gaps:

        st.warning(
            item
        )


# ============================================================
# 25. ACADEMIC TOPICS TO PRESERVE
# ============================================================

academic_topics = normalize_list(

    critic_result.get(
        "academic_topics_to_preserve"
    )

)


if academic_topics:

    st.divider()

    st.subheader(
        "🎓 Academic Topics to Preserve"
    )


    for item in academic_topics:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 26. CURRICULUM BLOAT
# ============================================================

bloat_risks = normalize_list(

    critic_result.get(
        "curriculum_bloat_risks"
    )

)


if bloat_risks:

    st.divider()

    st.subheader(
        "📦 Curriculum Bloat Risks"
    )


    for item in bloat_risks:

        st.warning(
            item
        )


# ============================================================
# 27. SEQUENCING ISSUES
# ============================================================

sequencing_issues = normalize_list(

    critic_result.get(
        "sequencing_issues"
    )

)


if sequencing_issues:

    st.subheader(
        "🔀 Sequencing Issues"
    )


    for item in sequencing_issues:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 28. FACULTY FEASIBILITY
# ============================================================

faculty_issues = normalize_list(

    critic_result.get(
        "faculty_feasibility_issues"
    )

)


if faculty_issues:

    st.subheader(
        "👨‍🏫 Faculty Feasibility Issues"
    )


    for item in faculty_issues:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 29. STUDENT WORKLOAD
# ============================================================

workload_issues = normalize_list(

    critic_result.get(
        "student_workload_issues"
    )

)


if workload_issues:

    st.subheader(
        "🎓 Student Workload Issues"
    )


    for item in workload_issues:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 30. TECHNOLOGY VOLATILITY
# ============================================================

technology_risks = normalize_list(

    critic_result.get(
        "technology_volatility_risks"
    )

)


if technology_risks:

    st.subheader(
        "⚠️ Technology Volatility Risks"
    )


    for item in technology_risks:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 31. CRITIC APPROVED RECOMMENDATIONS
# ============================================================

critic_approved = normalize_list(

    critic_result.get(
        "critic_approved_recommendations"
    )

)


st.session_state[
    "critic_recommendations"
] = critic_approved


# ============================================================
# 32. SAVE CRITIC DECISIONS
# ============================================================

critic_decisions = {

    "accepted":
        accepted,

    "modified":
        modified,

    "merged":
        merged,

    "rejected":
        rejected,

    "missed_industry_gaps":
        missed_industry_gaps,

    "academic_topics_to_preserve":
        academic_topics,

    "bloat_risks":
        bloat_risks,

    "sequencing_issues":
        sequencing_issues,

    "faculty_issues":
        faculty_issues,

    "workload_issues":
        workload_issues,

    "technology_risks":
        technology_risks,

    "approved":
        critic_approved,

}


st.session_state[
    "critic_decisions"
] = critic_decisions


# ============================================================
# 33. SAVE COMPLETE CRITIC PACKAGE
# ============================================================

critic_package = {

    "analysis":
        critic_result,

    "decisions":
        critic_decisions,

    "approved_recommendations":
        critic_approved,

    "generated_at":
        datetime.now().isoformat(),

}


st.session_state[
    "critic_enhancement_package"
] = critic_package


# ============================================================
# 34. DOWNLOAD CRITIC REPORT
# ============================================================

if (

    critic_result

    and

    not critic_result.get(
        "error"
    )

):

    st.download_button(

        "⬇️ Download Critic Analysis JSON",

        data=serialize_json(
            critic_result
        ),

        file_name=(
            "curriculum_critic_analysis.json"
        ),

        mime="application/json",

        key="download_critic_analysis",

    )


# ============================================================
# 35. COMPLETION STATUS
# ============================================================

if st.session_state.get(

    "critic_agent_complete",

    False,

):

    st.success(
        """
        ✅ **Critic Agent Review Complete**

        The Expert Agent recommendations have now passed
        through an independent critical review.

        The next stage is the **Final Enhancement Agent**.

        Final decision flow:

        Expert
          ↓
        Critic
          ↓
        Final Enhancement Agent
          ↓
        Approved Enhanced Curriculum
        """
    )


# ============================================================
# END OF CHUNK 6/10
# ============================================================
# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 7/10
# FINAL CURRICULUM ENHANCEMENT AGENT
# ============================================================

"""
Purpose
-------
Reconcile:

    Original Curriculum
            +
    Industry / JD Intelligence
            +
    Gap Analysis
            +
    Enhancement Blueprint
            +
    Expert Agent
            +
    Critic Agent

and produce the final enhanced curriculum proposal.

Decision types
--------------

KEEP
ENHANCE
ADD
MERGE
REDUCE
REMOVE
REORDER

Output
------

st.session_state["final_enhancement_analysis"]

st.session_state["final_curriculum"]

st.session_state["final_modules"]

st.session_state["final_topics"]

st.session_state["final_projects"]

st.session_state["final_tools"]

st.session_state["final_technologies"]

st.session_state["final_enhancement_complete"]


Technology
----------

Groq
Llama
LangChain
"""


# ============================================================
# 1. LOAD ORIGINAL DATA
# ============================================================

curriculum_skill_intelligence = st.session_state.get(
    "curriculum_skill_intelligence",
    {}
)


jd_skill_intelligence = st.session_state.get(
    "jd_skill_intelligence",
    {}
)


industry_gap_analysis = st.session_state.get(
    "industry_gap_analysis",
    {}
)


prioritized_gaps = st.session_state.get(
    "prioritized_gaps",
    []
)


module_gap_mapping = st.session_state.get(
    "module_gap_mapping",
    []
)


enhancement_blueprint = st.session_state.get(
    "enhancement_blueprint",
    []
)


# ============================================================
# 2. LOAD EXPERT ANALYSIS
# ============================================================

expert_enhancement_analysis = st.session_state.get(
    "expert_enhancement_analysis",
    {}
)


expert_enhancement_package = st.session_state.get(
    "expert_enhancement_package",
    {}
)


expert_recommendations = st.session_state.get(
    "expert_recommendations",
    []
)


# ============================================================
# 3. LOAD CRITIC ANALYSIS
# ============================================================

critic_enhancement_analysis = st.session_state.get(
    "critic_enhancement_analysis",
    {}
)


critic_enhancement_package = st.session_state.get(
    "critic_enhancement_package",
    {}
)


critic_recommendations = st.session_state.get(
    "critic_recommendations",
    []
)


critic_decisions = st.session_state.get(
    "critic_decisions",
    {}
)


# ============================================================
# 4. VALIDATION
# ============================================================

missing_inputs = []


if not curriculum_skill_intelligence:

    missing_inputs.append(
        "Curriculum Intelligence"
    )


if not enhancement_blueprint:

    missing_inputs.append(
        "Enhancement Blueprint"
    )


if not expert_enhancement_analysis:

    missing_inputs.append(
        "Expert Agent Analysis"
    )


if not critic_enhancement_analysis:

    missing_inputs.append(
        "Critic Agent Analysis"
    )


if missing_inputs:

    st.warning(

        "⚠️ Final Enhancement Agent requires: "
        +
        ", ".join(
            missing_inputs
        )

    )


# ============================================================
# 5. GROQ CONFIGURATION
# ============================================================

groq_api_key = os.getenv(
    "GROQ_API_KEY",
    "",
).strip()


groq_model = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
).strip()


if not groq_api_key:

    try:

        groq_api_key = st.secrets.get(
            "GROQ_API_KEY",
            "",
        )

    except Exception:

        groq_api_key = ""


groq_api_key = safe_text(
    groq_api_key
)


# ============================================================
# 6. CREATE FINAL AGENT LLM
# ============================================================

def create_final_agent_llm():
    """
    Create LLM for final curriculum decision.
    """

    if ChatGroq is None:

        return None


    if not groq_api_key:

        return None


    try:

        return ChatGroq(

            api_key=groq_api_key,

            model=groq_model,

            temperature=0.1,

            max_tokens=12000,

        )

    except TypeError:

        try:

            return ChatGroq(

                groq_api_key=groq_api_key,

                model=groq_model,

                temperature=0.1,

                max_tokens=12000,

            )

        except Exception:

            return None

    except Exception:

        return None


final_agent_llm = create_final_agent_llm()


# ============================================================
# 7. FINAL AGENT SYSTEM PROMPT
# ============================================================

FINAL_AGENT_SYSTEM_PROMPT = """
You are the Final Curriculum Enhancement Agent.

You are the final decision-maker in a multi-agent Curriculum
Intelligence system.

You have access to:

1. Original academic curriculum
2. Industry / Job Description intelligence
3. Gap analysis
4. Prioritized gaps
5. Module-level gap mapping
6. Deterministic enhancement blueprint
7. Curriculum Expert Agent analysis
8. Independent Critic Agent analysis

Your job is to produce the FINAL ENHANCED CURRICULUM.

IMPORTANT:

You must NOT blindly follow the Expert Agent.

You must NOT blindly follow the Critic Agent.

You must reconcile all evidence.

============================================================
DECISION PRINCIPLES
============================================================

For every existing module/topic choose one:

KEEP
ENHANCE
MERGE
REDUCE
REMOVE
REORDER

For industry requirements not currently covered choose:

ADD

Only add content when there is sufficient evidence.

============================================================
ACADEMIC PRINCIPLES
============================================================

Preserve:

- Core theoretical foundations
- Mathematical foundations where appropriate
- Fundamental algorithms
- Core programming concepts
- Core problem-solving skills
- Academic progression
- Assessment integrity

Do not transform an academic curriculum into a list of
vendor-specific tools.

============================================================
INDUSTRY PRINCIPLES
============================================================

Prioritize:

- Strong industry skills
- High-frequency job requirements
- Practical implementation
- Modern engineering practices
- Relevant tools
- Relevant technologies
- Real-world projects
- Deployment
- Evaluation
- Problem solving

============================================================
CURRICULUM BLOAT
============================================================

Avoid:

- Duplicate modules
- Duplicate concepts
- Excessive tools
- Unnecessary frameworks
- Every JD keyword becoming a topic
- Unrealistic hours
- Too many unrelated projects

Prefer:

Existing Module
      ↓
Enhance it

instead of:

Existing Module
      +
New duplicate module

============================================================
TOOLS VS CONCEPTS
============================================================

If a tool is temporary but the concept is durable:

Teach the concept deeply.

Then use the tool as a practical implementation.

Example:

RAG
  +
Embeddings
  +
Vector Search
  +
Retrieval
  +
Evaluation

is more important than simply teaching:

"Tool X"

============================================================
PROJECT PRINCIPLES
============================================================

Projects must demonstrate:

- Problem definition
- Concepts
- Technologies
- Implementation
- Evaluation
- Real-world relevance

Reject projects that are only:

- Hello World
- Simple CRUD
- Copy-paste demos
- Tool demonstrations
- Trivial notebooks

============================================================
SEQUENCING
============================================================

Consider:

Foundation
    ↓
Core Concepts
    ↓
Applied Concepts
    ↓
Tools
    ↓
Advanced Concepts
    ↓
Industry Practice
    ↓
Project

Do not introduce advanced topics before prerequisites.

============================================================
HOURS
============================================================

Recommended hours must be realistic.

Consider:

- Existing curriculum hours
- Student workload
- Faculty workload
- Practical labs
- Projects
- Assessment
- Prerequisites

============================================================
FINAL DECISION
============================================================

Produce:

A. Final module structure

B. Final topics for each module

C. Concepts

D. Tools

E. Technologies

F. Practical labs

G. Projects

H. Recommended hours

I. Learning outcomes

J. Prerequisites

K. Assessment recommendations

L. Industry alignment

M. Changes from original curriculum

N. Rationale for major changes

O. Curriculum enhancement summary

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

No Markdown fences.
"""


# ============================================================
# 8. FINAL AGENT USER PROMPT
# ============================================================

FINAL_AGENT_USER_PROMPT = """
Create the final enhanced curriculum.

============================================================
ORIGINAL CURRICULUM
============================================================

{curriculum_data}


============================================================
JD / INDUSTRY INTELLIGENCE
============================================================

{jd_data}


============================================================
INDUSTRY GAP ANALYSIS
============================================================

{gap_analysis}


============================================================
PRIORITIZED GAPS
============================================================

{prioritized_gaps}


============================================================
MODULE GAP MAPPING
============================================================

{module_mapping}


============================================================
DETERMINISTIC ENHANCEMENT BLUEPRINT
============================================================

{blueprint}


============================================================
EXPERT AGENT
============================================================

{expert_analysis}


============================================================
EXPERT RECOMMENDATIONS
============================================================

{expert_recommendations}


============================================================
CRITIC AGENT
============================================================

{critic_analysis}


============================================================
CRITIC DECISIONS
============================================================

{critic_decisions}


============================================================
TASK
============================================================

Reconcile all the above information.

Produce a complete final enhanced curriculum.

For each original module:

- Determine whether to KEEP, ENHANCE, MERGE, REDUCE,
  REMOVE, or REORDER.
- Explain the reason.
- Preserve valuable existing content.
- Add missing industry content only where justified.

For new requirements:

- Determine whether to ADD.
- Specify the module.
- Specify topics.
- Specify concepts.
- Specify tools.
- Specify technologies.
- Specify practical lab.
- Specify project.
- Specify hours.
- Specify prerequisites.
- Specify learning outcomes.

Also provide:

- Final module sequence
- Final total estimated hours
- Industry alignment score
- Academic quality score
- Employability score
- Curriculum manageability score
- Major changes
- Removed/reduced content
- Merged content
- Added content
- Industry skills covered
- Remaining industry gaps

Use this exact JSON structure:

{
  "executive_summary": "",

  "overall_assessment": {
    "industry_alignment": 0,
    "academic_quality": 0,
    "employability": 0,
    "curriculum_manageability": 0,
    "overall_score": 0
  },

  "curriculum_decisions": [
    {
      "module_id": "",
      "original_module": "",
      "decision": "KEEP",
      "reason": "",
      "new_module_name": "",
      "recommended_hours": 0
    }
  ],

  "final_modules": [
    {
      "module_id": "",
      "module_name": "",
      "sequence": 1,
      "purpose": "",
      "recommended_hours": 0,
      "level": "",
      "prerequisites": [],
      "topics": [
        {
          "topic_id": "",
          "topic_name": "",
          "description": "",
          "concepts": [],
          "tools": [],
          "technologies": [],
          "hours": 0,
          "depth": "",
          "lab_required": true,
          "project_required": false,
          "learning_outcomes": [],
          "assessment_methods": []
        }
      ],
      "module_learning_outcomes": [],
      "module_project": "",
      "industry_skills": []
    }
  ],

  "added_topics": [],

  "enhanced_topics": [],

  "merged_topics": [],

  "reduced_topics": [],

  "removed_topics": [],

  "reordered_topics": [],

  "new_tools": [],

  "new_technologies": [],

  "concepts_to_deepen": [],

  "final_projects": [
    {
      "title": "",
      "module": "",
      "problem_statement": "",
      "industry_relevance": "",
      "concepts": [],
      "technologies": [],
      "tools": [],
      "deliverables": [],
      "evaluation_criteria": []
    }
  ],

  "industry_skills_covered": [],

  "remaining_industry_gaps": [],

  "major_changes": [],

  "implementation_notes": [],

  "faculty_requirements": [],

  "student_workload_notes": [],

  "final_recommendations": []
}
"""


# ============================================================
# 9. BUILD FINAL AGENT PROMPT
# ============================================================

def build_final_agent_prompt():
    """
    Build LangChain prompt.
    """

    if ChatPromptTemplate is None:

        return None


    try:

        return ChatPromptTemplate.from_messages([

            (
                "system",
                FINAL_AGENT_SYSTEM_PROMPT,
            ),

            (
                "human",
                FINAL_AGENT_USER_PROMPT,
            ),

        ])

    except Exception:

        return None


# ============================================================
# 10. RUN FINAL AGENT
# ============================================================

def run_final_enhancement_agent():
    """
    Run final curriculum reconciliation agent.
    """

    if missing_inputs:

        return {

            "error":
                (
                    "Missing required inputs: "
                    +
                    ", ".join(
                        missing_inputs
                    )
                )

        }


    if final_agent_llm is None:

        return {

            "error":
                (
                    "Groq LLM is not configured. "
                    "Set GROQ_API_KEY and install "
                    "langchain-groq."
                )

        }


    prompt = build_final_agent_prompt()


    if prompt is None:

        return {

            "error":
                "Unable to create Final Agent prompt."

        }


    try:

        chain = (
            prompt
            |
            final_agent_llm
        )


        response = chain.invoke({

            "curriculum_data":
                compact_json(
                    curriculum_skill_intelligence
                ),

            "jd_data":
                compact_json(
                    jd_skill_intelligence
                ),

            "gap_analysis":
                compact_json(
                    industry_gap_analysis
                ),

            "prioritized_gaps":
                compact_json(
                    prioritized_gaps
                ),

            "module_mapping":
                compact_json(
                    module_gap_mapping
                ),

            "blueprint":
                compact_json(
                    enhancement_blueprint
                ),

            "expert_analysis":
                compact_json(
                    expert_enhancement_analysis
                ),

            "expert_recommendations":
                compact_json(
                    expert_recommendations
                ),

            "critic_analysis":
                compact_json(
                    critic_enhancement_analysis
                ),

            "critic_decisions":
                compact_json(
                    critic_decisions
                ),

        })


        if hasattr(
            response,
            "content",
        ):

            response_text = response.content

        else:

            response_text = str(
                response
            )


        result = extract_json_from_response(
            response_text
        )


        result["_metadata"] = {

            "agent":
                "Final Curriculum Enhancement Agent",

            "model":
                groq_model,

            "provider":
                "Groq",

            "framework":
                "LangChain",

            "generated_at":
                datetime.now().isoformat(),

        }


        return result


    except Exception as exc:

        return {

            "error":
                str(
                    exc
                ),

            "_metadata": {

                "agent":
                    "Final Curriculum Enhancement Agent",

                "model":
                    groq_model,

            },

        }


# ============================================================
# 11. UI HEADER
# ============================================================

st.divider()

st.subheader(
    "🏆 Final Curriculum Enhancement Agent"
)


st.markdown(
    """
This is the final decision stage of the multi-agent
Curriculum Intelligence pipeline.

The agent reconciles:

**Original Curriculum + Industry/JD + Gap Analysis +
Enhancement Blueprint + Expert + Critic**

and produces the proposed **Final Enhanced Curriculum**.
"""
)


# ============================================================
# 12. PIPELINE STATUS
# ============================================================

status_cols = st.columns(
    6
)


with status_cols[0]:

    if curriculum_skill_intelligence:

        st.success(
            "✅ Curriculum"
        )

    else:

        st.error(
            "❌ Curriculum"
        )


with status_cols[1]:

    if jd_skill_intelligence:

        st.success(
            "✅ JD"
        )

    else:

        st.warning(
            "⚠️ JD"
        )


with status_cols[2]:

    if enhancement_blueprint:

        st.success(
            "✅ Blueprint"
        )

    else:

        st.error(
            "❌ Blueprint"
        )


with status_cols[3]:

    if expert_enhancement_analysis:

        st.success(
            "✅ Expert"
        )

    else:

        st.error(
            "❌ Expert"
        )


with status_cols[4]:

    if critic_enhancement_analysis:

        st.success(
            "✅ Critic"
        )

    else:

        st.error(
            "❌ Critic"
        )


with status_cols[5]:

    st.info(
        groq_model
    )


# ============================================================
# 13. RUN BUTTON
# ============================================================

run_final_agent = st.button(

    "🏆 Generate Final Enhanced Curriculum",

    type="primary",

    use_container_width=True,

    disabled=(

        bool(
            missing_inputs
        )

        or

        final_agent_llm is None

    ),

)


# ============================================================
# 14. EXECUTE FINAL AGENT
# ============================================================

if run_final_agent:

    with st.spinner(

        """
        🏆 Final Enhancement Agent is reconciling
        curriculum, industry requirements, expert analysis
        and critic decisions...
        """

    ):

        final_result = (
            run_final_enhancement_agent()
        )


    st.session_state[
        "final_enhancement_analysis"
    ] = final_result


    st.session_state[
        "final_enhancement_complete"
    ] = bool(

        final_result

        and

        not final_result.get(
            "error"
        )

    )


# ============================================================
# 15. LOAD FINAL RESULT
# ============================================================

final_result = st.session_state.get(

    "final_enhancement_analysis",

    {}

)


# ============================================================
# 16. ERROR
# ============================================================

if final_result.get(
    "error"
):

    st.error(

        final_result.get(
            "error"
        )

    )


# ============================================================
# 17. EXECUTIVE SUMMARY
# ============================================================

if (

    final_result

    and

    not final_result.get(
        "error"
    )

):

    st.success(
        "✅ Final Enhanced Curriculum generated."
    )


    summary = safe_text(

        final_result.get(
            "executive_summary"
        )

    )


    if summary:

        st.markdown(
            "### 📌 Executive Summary"
        )


        st.info(
            summary
        )


# ============================================================
# 18. OVERALL ASSESSMENT
# ============================================================

overall_assessment = final_result.get(

    "overall_assessment",

    {}

)


if isinstance(
    overall_assessment,
    dict,
):

    st.markdown(
        "### 📊 Final Curriculum Score"
    )


    score_cols = st.columns(
        5
    )


    with score_cols[0]:

        st.metric(

            "Overall",

            overall_assessment.get(
                "overall_score",
                0,
            ),

        )


    with score_cols[1]:

        st.metric(

            "Industry",

            overall_assessment.get(
                "industry_alignment",
                0,
            ),

        )


    with score_cols[2]:

        st.metric(

            "Academic",

            overall_assessment.get(
                "academic_quality",
                0,
            ),

        )


    with score_cols[3]:

        st.metric(

            "Employability",

            overall_assessment.get(
                "employability",
                0,
            ),

        )


    with score_cols[4]:

        st.metric(

            "Manageability",

            overall_assessment.get(
                "curriculum_manageability",
                0,
            ),

        )


# ============================================================
# 19. CURRICULUM DECISIONS
# ============================================================

curriculum_decisions = final_result.get(

    "curriculum_decisions",

    []

)


if curriculum_decisions:

    st.divider()

    st.subheader(
        "🔄 Curriculum Change Decisions"
    )


    decision_rows = []


    for item in curriculum_decisions:

        if not isinstance(
            item,
            dict,
        ):

            continue


        decision = safe_text(

            item.get(
                "decision"
            ),

            "KEEP",

        ).upper()


        icon_map = {

            "KEEP":
                "🟢",

            "ENHANCE":
                "🔵",

            "ADD":
                "➕",

            "MERGE":
                "🔗",

            "REDUCE":
                "🟡",

            "REMOVE":
                "🔴",

            "REORDER":
                "🔀",

        }


        icon = icon_map.get(

            decision,

            "⚪",

        )


        decision_rows.append({

            "Decision":
                f"{icon} {decision}",

            "Original Module":
                item.get(
                    "original_module"
                ),

            "New Module":
                item.get(
                    "new_module_name"
                ),

            "Hours":
                item.get(
                    "recommended_hours"
                ),

            "Reason":
                item.get(
                    "reason"
                ),

        })


    if decision_rows:

        decisions_df = pd.DataFrame(
            decision_rows
        )


        st.dataframe(

            decisions_df,

            use_container_width=True,

            hide_index=True,

        )


# ============================================================
# 20. FINAL MODULES
# ============================================================

final_modules = final_result.get(

    "final_modules",

    []

)


st.session_state[
    "final_modules"
] = final_modules


if final_modules:

    st.divider()

    st.subheader(
        "📚 Final Enhanced Curriculum"
    )


    st.write(

        f"**Total Modules: {len(final_modules)}**"

    )


    for module in final_modules:

        if not isinstance(
            module,
            dict,
        ):

            continue


        module_name = safe_text(

            module.get(
                "module_name"
            ),

            "Module",

        )


        sequence = module.get(
            "sequence",
            "",
        )


        hours = module.get(
            "recommended_hours",
            0,
        )


        level = safe_text(

            module.get(
                "level"
            )

        )


        with st.expander(

            f"""
            Module {sequence}: {module_name}
            """

        ):

            header_cols = st.columns(
                3
            )


            with header_cols[0]:

                st.metric(

                    "Hours",

                    hours,

                )


            with header_cols[1]:

                st.metric(

                    "Level",

                    level
                    or
                    "Not specified",

                )


            with header_cols[2]:

                st.metric(

                    "Topics",

                    len(

                        module.get(
                            "topics",
                            []
                        )

                    ),

                )


            purpose = safe_text(

                module.get(
                    "purpose"
                )

            )


            if purpose:

                st.write(

                    "**Purpose:**",

                    purpose,

                )


            prerequisites = normalize_list(

                module.get(
                    "prerequisites"
                )

            )


            if prerequisites:

                st.markdown(
                    "### 🔗 Prerequisites"
                )


                for prerequisite in prerequisites:

                    st.markdown(
                        f"- {prerequisite}"
                    )


            # ------------------------------------------------
            # Topics
            # ------------------------------------------------

            topics = module.get(

                "topics",

                []

            )


            if topics:

                st.markdown(
                    "### 📖 Topics"
                )


                for topic in topics:

                    if not isinstance(
                        topic,
                        dict,
                    ):

                        continue


                    topic_name = safe_text(

                        topic.get(
                            "topic_name"
                        ),

                        "Topic",

                    )


                    topic_hours = topic.get(
                        "hours",
                        0,
                    )


                    depth = safe_text(

                        topic.get(
                            "depth"
                        )

                    )


                    with st.expander(

                        f"""
                        {topic_name}
                        —
                        {topic_hours} hrs
                        """

                    ):

                        st.write(

                            "**Description:**",

                            topic.get(
                                "description"
                            ),

                        )


                        st.write(

                            "**Depth:**",

                            depth,

                        )


                        concepts = normalize_list(

                            topic.get(
                                "concepts"
                            )

                        )


                        tools = normalize_list(

                            topic.get(
                                "tools"
                            )

                        )


                        technologies = normalize_list(

                            topic.get(
                                "technologies"
                            )

                        )


                        outcomes = normalize_list(

                            topic.get(
                                "learning_outcomes"
                            )

                        )


                        assessments = normalize_list(

                            topic.get(
                                "assessment_methods"
                            )

                        )


                        if concepts:

                            st.markdown(
                                "**Concepts**"
                            )


                            for concept in concepts:

                                st.markdown(
                                    f"- {concept}"
                                )


                        if tools:

                            st.markdown(
                                "**Tools**"
                            )


                            for tool in tools:

                                st.markdown(
                                    f"- {tool}"
                                )


                        if technologies:

                            st.markdown(
                                "**Technologies**"
                            )


                            for technology in technologies:

                                st.markdown(
                                    f"- {technology}"
                                )


                        if outcomes:

                            st.markdown(
                                "**Learning Outcomes**"
                            )


                            for outcome in outcomes:

                                st.markdown(
                                    f"- {outcome}"
                                )


                        if assessments:

                            st.markdown(
                                "**Assessment**"
                            )


                            for assessment in assessments:

                                st.markdown(
                                    f"- {assessment}"
                                )


            # ------------------------------------------------
            # Module outcomes
            # ------------------------------------------------

            module_outcomes = normalize_list(

                module.get(
                    "module_learning_outcomes"
                )

            )


            if module_outcomes:

                st.markdown(
                    "### 🎯 Module Learning Outcomes"
                )


                for outcome in module_outcomes:

                    st.markdown(
                        f"- {outcome}"
                    )


            # ------------------------------------------------
            # Module project
            # ------------------------------------------------

            module_project = safe_text(

                module.get(
                    "module_project"
                )

            )


            if module_project:

                st.markdown(
                    "### 🚀 Module Project"
                )


                st.info(
                    module_project
                )


            # ------------------------------------------------
            # Industry skills
            # ------------------------------------------------

            industry_skills = normalize_list(

                module.get(
                    "industry_skills"
                )

            )


            if industry_skills:

                st.markdown(
                    "### 💼 Industry Skills"
                )


                for skill in industry_skills:

                    st.markdown(
                        f"- {skill}"
                    )


# ============================================================
# 21. SAVE FINAL TOPICS
# ============================================================

final_topics = []


for module in final_modules:

    if not isinstance(
        module,
        dict,
    ):

        continue


    for topic in module.get(
        "topics",
        [],
    ):

        if not isinstance(
            topic,
            dict,
        ):

            continue


        final_topics.append({

            "module_id":
                module.get(
                    "module_id"
                ),

            "module_name":
                module.get(
                    "module_name"
                ),

            "topic_id":
                topic.get(
                    "topic_id"
                ),

            "topic_name":
                topic.get(
                    "topic_name"
                ),

            "description":
                topic.get(
                    "description"
                ),

            "concepts":
                topic.get(
                    "concepts",
                    []
                ),

            "tools":
                topic.get(
                    "tools",
                    []
                ),

            "technologies":
                topic.get(
                    "technologies",
                    []
                ),

            "hours":
                topic.get(
                    "hours",
                    0
                ),

            "depth":
                topic.get(
                    "depth"
                ),

            "learning_outcomes":
                topic.get(
                    "learning_outcomes",
                    []
                ),

            "assessment_methods":
                topic.get(
                    "assessment_methods",
                    []
                ),

        })


st.session_state[
    "final_topics"
] = final_topics


# ============================================================
# 22. NEW / ENHANCED TOPICS
# ============================================================

added_topics = normalize_list(

    final_result.get(
        "added_topics"
    )

)


enhanced_topics = normalize_list(

    final_result.get(
        "enhanced_topics"
    )

)


merged_topics = normalize_list(

    final_result.get(
        "merged_topics"
    )

)


reduced_topics = normalize_list(

    final_result.get(
        "reduced_topics"
    )

)


removed_topics = normalize_list(

    final_result.get(
        "removed_topics"
    )

)


reordered_topics = normalize_list(

    final_result.get(
        "reordered_topics"
    )

)


# ============================================================
# 23. CHANGE SUMMARY
# ============================================================

st.divider()

st.subheader(
    "📝 Curriculum Change Summary"
)


change_cols = st.columns(
    6
)


with change_cols[0]:

    st.metric(
        "➕ Added",
        len(
            added_topics
        ),
    )


with change_cols[1]:

    st.metric(
        "🔧 Enhanced",
        len(
            enhanced_topics
        ),
    )


with change_cols[2]:

    st.metric(
        "🔗 Merged",
        len(
            merged_topics
        ),
    )


with change_cols[3]:

    st.metric(
        "📉 Reduced",
        len(
            reduced_topics
        ),
    )


with change_cols[4]:

    st.metric(
        "❌ Removed",
        len(
            removed_topics
        ),
    )


with change_cols[5]:

    st.metric(
        "🔀 Reordered",
        len(
            reordered_topics
        ),
    )


# ============================================================
# 24. DISPLAY CHANGE LISTS
# ============================================================

change_sections = [

    (
        "➕ Topics Added",
        added_topics,
    ),

    (
        "🔧 Topics Enhanced",
        enhanced_topics,
    ),

    (
        "🔗 Topics Merged",
        merged_topics,
    ),

    (
        "📉 Topics Reduced",
        reduced_topics,
    ),

    (
        "❌ Topics Removed",
        removed_topics,
    ),

    (
        "🔀 Topics Reordered",
        reordered_topics,
    ),

]


for title, items in change_sections:

    if not items:

        continue


    st.markdown(
        f"### {title}"
    )


    for item in items:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 25. TOOLS
# ============================================================

final_tools = normalize_list(

    final_result.get(
        "new_tools"
    )

)


st.session_state[
    "final_tools"
] = final_tools


if final_tools:

    st.divider()

    st.subheader(
        "🛠 Final Industry Tools"
    )


    for tool in final_tools:

        st.markdown(
            f"- {tool}"
        )


# ============================================================
# 26. TECHNOLOGIES
# ============================================================

final_technologies = normalize_list(

    final_result.get(
        "new_technologies"
    )

)


st.session_state[
    "final_technologies"
] = final_technologies


if final_technologies:

    st.subheader(
        "⚙️ Final Industry Technologies"
    )


    for technology in final_technologies:

        st.markdown(
            f"- {technology}"
        )


# ============================================================
# 27. CONCEPTS TO DEEPEN
# ============================================================

final_concepts = normalize_list(

    final_result.get(
        "concepts_to_deepen"
    )

)


st.session_state[
    "final_concepts"
] = final_concepts


if final_concepts:

    st.subheader(
        "🧠 Concepts to Deepen"
    )


    for concept in final_concepts:

        st.markdown(
            f"- {concept}"
        )


# ============================================================
# 28. FINAL PROJECTS
# ============================================================

final_projects = final_result.get(

    "final_projects",

    []

)


st.session_state[
    "final_projects"
] = final_projects


if final_projects:

    st.divider()

    st.subheader(
        "🚀 Final Industry Projects"
    )


    for project in final_projects:

        if not isinstance(
            project,
            dict,
        ):

            continue


        title = safe_text(

            project.get(
                "title"
            ),

            "Industry Project",

        )


        with st.expander(
            title
        ):

            st.write(

                "**Module:**",

                project.get(
                    "module"
                ),

            )


            st.write(

                "**Problem Statement:**",

                project.get(
                    "problem_statement"
                ),

            )


            st.write(

                "**Industry Relevance:**",

                project.get(
                    "industry_relevance"
                ),

            )


            concepts = normalize_list(

                project.get(
                    "concepts"
                )

            )


            technologies = normalize_list(

                project.get(
                    "technologies"
                )

            )


            tools = normalize_list(

                project.get(
                    "tools"
                )

            )


            deliverables = normalize_list(

                project.get(
                    "deliverables"
                )

            )


            evaluation = normalize_list(

                project.get(
                    "evaluation_criteria"
                )

            )


            if concepts:

                st.markdown(
                    "### 🧠 Concepts"
                )


                for item in concepts:

                    st.markdown(
                        f"- {item}"
                    )


            if technologies:

                st.markdown(
                    "### ⚙️ Technologies"
                )


                for item in technologies:

                    st.markdown(
                        f"- {item}"
                    )


            if tools:

                st.markdown(
                    "### 🛠 Tools"
                )


                for item in tools:

                    st.markdown(
                        f"- {item}"
                    )


            if deliverables:

                st.markdown(
                    "### 📦 Deliverables"
                )


                for item in deliverables:

                    st.markdown(
                        f"- {item}"
                    )


            if evaluation:

                st.markdown(
                    "### 📊 Evaluation"
                )


                for item in evaluation:

                    st.markdown(
                        f"- {item}"
                    )


# ============================================================
# 29. INDUSTRY SKILLS COVERED
# ============================================================

industry_skills_covered = normalize_list(

    final_result.get(
        "industry_skills_covered"
    )

)


st.session_state[
    "industry_skills_covered"
] = industry_skills_covered


if industry_skills_covered:

    st.divider()

    st.subheader(
        "💼 Industry Skills Covered"
    )


    for skill in industry_skills_covered:

        st.markdown(
            f"- {skill}"
        )


# ============================================================
# 30. REMAINING GAPS
# ============================================================

remaining_gaps = normalize_list(

    final_result.get(
        "remaining_industry_gaps"
    )

)


st.session_state[
    "remaining_industry_gaps"
] = remaining_gaps


if remaining_gaps:

    st.divider()

    st.subheader(
        "⚠️ Remaining Industry Gaps"
    )


    for gap in remaining_gaps:

        st.warning(
            gap
        )


# ============================================================
# 31. MAJOR CHANGES
# ============================================================

major_changes = normalize_list(

    final_result.get(
        "major_changes"
    )

)


if major_changes:

    st.divider()

    st.subheader(
        "⭐ Major Curriculum Changes"
    )


    for change in major_changes:

        st.markdown(
            f"- {change}"
        )


# ============================================================
# 32. IMPLEMENTATION NOTES
# ============================================================

implementation_notes = normalize_list(

    final_result.get(
        "implementation_notes"
    )

)


if implementation_notes:

    st.subheader(
        "⚙️ Implementation Notes"
    )


    for note in implementation_notes:

        st.markdown(
            f"- {note}"
        )


# ============================================================
# 33. FACULTY REQUIREMENTS
# ============================================================

faculty_requirements = normalize_list(

    final_result.get(
        "faculty_requirements"
    )

)


st.session_state[
    "faculty_requirements"
] = faculty_requirements


if faculty_requirements:

    st.subheader(
        "👨‍🏫 Faculty Requirements"
    )


    for item in faculty_requirements:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 34. STUDENT WORKLOAD
# ============================================================

student_workload_notes = normalize_list(

    final_result.get(
        "student_workload_notes"
    )

)


st.session_state[
    "student_workload_notes"
] = student_workload_notes


if student_workload_notes:

    st.subheader(
        "🎓 Student Workload"
    )


    for item in student_workload_notes:

        st.markdown(
            f"- {item}"
        )


# ============================================================
# 35. FINAL RECOMMENDATIONS
# ============================================================

final_recommendations = normalize_list(

    final_result.get(
        "final_recommendations"
    )

)


st.session_state[
    "final_recommendations"
] = final_recommendations


if final_recommendations:

    st.divider()

    st.subheader(
        "🏆 Final Recommendations"
    )


    for index, recommendation in enumerate(

        final_recommendations,

        start=1,

    ):

        st.markdown(

            f"""
            **{index}.**
            {recommendation}
            """

        )


# ============================================================
# 36. SAVE COMPLETE FINAL CURRICULUM
# ============================================================

final_curriculum = {

    "executive_summary":
        final_result.get(
            "executive_summary"
        ),

    "overall_assessment":
        overall_assessment,

    "modules":
        final_modules,

    "topics":
        final_topics,

    "projects":
        final_projects,

    "industry_skills":
        industry_skills_covered,

    "remaining_gaps":
        remaining_gaps,

    "major_changes":
        major_changes,

    "tools":
        final_tools,

    "technologies":
        final_technologies,

    "concepts":
        final_concepts,

    "recommendations":
        final_recommendations,

    "generated_at":
        datetime.now().isoformat(),

}


st.session_state[
    "final_curriculum"
] = final_curriculum


# ============================================================
# 37. FINAL JSON DOWNLOAD
# ============================================================

if (

    final_result

    and

    not final_result.get(
        "error"
    )

):

    st.download_button(

        "⬇️ Download Final Enhanced Curriculum JSON",

        data=serialize_json(

            final_curriculum

        ),

        file_name=(

            "final_enhanced_curriculum.json"

        ),

        mime="application/json",

        key="download_final_curriculum_json",

    )


# ============================================================
# 38. FINAL AGENT STATUS
# ============================================================

if st.session_state.get(

    "final_enhancement_complete",

    False,

):

    st.success(
        """
        🎉 **FINAL CURRICULUM ENHANCEMENT COMPLETE**

        The curriculum has passed through:

        1. Curriculum Intelligence
        2. Industry / JD Intelligence
        3. Gap Analysis
        4. Deterministic Enhancement Blueprint
        5. Curriculum Expert Agent
        6. Independent Critic Agent
        7. Final Enhancement Agent

        The resulting curriculum is now ready for:

        - CO / PO mapping
        - Detailed syllabus generation
        - Lesson-plan generation
        - Faculty teaching plan
        - Student learning plan
        - Assessment generation
        - Project roadmap
        - Final curriculum report
        """
    )


# ============================================================
# END OF CHUNK 7/10
# ============================================================
# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 8/10
# CO / PO + FINAL ACADEMIC SYLLABUS STRUCTURING
# ============================================================

"""
Purpose
-------
Convert the AI-approved final curriculum into a formal
academic syllabus structure.

Input
-----

st.session_state["final_curriculum"]

Output
------

st.session_state["academic_syllabus"]

st.session_state["course_outcomes"]

st.session_state["program_outcomes"]

st.session_state["program_specific_outcomes"]

st.session_state["co_po_matrix"]

st.session_state["co_pso_matrix"]

st.session_state["syllabus_validation"]

st.session_state["academic_syllabus_complete"]

This chunk is primarily deterministic.

Why?

CO / PO mapping should be transparent and auditable.

The Final Enhancement Agent has already performed the
creative curriculum reasoning.

This stage converts that result into an academic structure.
"""


# ============================================================
# 1. LOAD FINAL CURRICULUM
# ============================================================

final_curriculum = st.session_state.get(
    "final_curriculum",
    {}
)


final_modules = st.session_state.get(
    "final_modules",
    []
)


final_topics = st.session_state.get(
    "final_topics",
    []
)


final_projects = st.session_state.get(
    "final_projects",
    []
)


industry_skills_covered = st.session_state.get(
    "industry_skills_covered",
    []
)


final_tools = st.session_state.get(
    "final_tools",
    []
)


final_technologies = st.session_state.get(
    "final_technologies",
    []
)


final_concepts = st.session_state.get(
    "final_concepts",
    []
)


# ============================================================
# 2. LOAD COURSE INFORMATION
# ============================================================

course_metadata = st.session_state.get(
    "syllabus_metadata",
    {}
)


# ============================================================
# 3. VALIDATION
# ============================================================

if not final_curriculum:

    st.warning(
        """
        ⚠️ Final curriculum is not available.

        Complete Chunk 7 before generating the academic
        syllabus.
        """
    )


# ============================================================
# 4. DEFAULT PROGRAM OUTCOMES
# ============================================================

"""
Generic engineering / technology POs.

These can later be replaced by institution-specific POs.
"""

DEFAULT_PROGRAM_OUTCOMES = {

    "PO1": (
        "Engineering Knowledge",
        "Apply knowledge of mathematics, science, "
        "engineering fundamentals and computing principles "
        "to solve complex engineering problems."
    ),

    "PO2": (
        "Problem Analysis",
        "Identify, formulate, review research literature, "
        "and analyse complex engineering problems."
    ),

    "PO3": (
        "Design / Development",
        "Design solutions for complex engineering problems "
        "and develop systems that meet specified needs."
    ),

    "PO4": (
        "Investigation",
        "Conduct investigations using research-based "
        "knowledge and appropriate methods."
    ),

    "PO5": (
        "Modern Tool Usage",
        "Create, select and apply appropriate techniques, "
        "resources and modern engineering tools."
    ),

    "PO6": (
        "Engineer and Society",
        "Apply reasoning informed by contextual knowledge "
        "to assess societal, health, safety and legal "
        "responsibilities."
    ),

    "PO7": (
        "Environment and Sustainability",
        "Understand the impact of engineering solutions "
        "in societal and environmental contexts."
    ),

    "PO8": (
        "Ethics",
        "Apply ethical principles and commit to professional "
        "ethics and responsibilities."
    ),

    "PO9": (
        "Individual and Team Work",
        "Function effectively as an individual and as a "
        "member or leader of diverse teams."
    ),

    "PO10": (
        "Communication",
        "Communicate effectively on complex engineering "
        "activities with technical and non-technical audiences."
    ),

    "PO11": (
        "Project Management",
        "Demonstrate knowledge and understanding of "
        "engineering management and project execution."
    ),

    "PO12": (
        "Life-long Learning",
        "Recognize the need for lifelong learning and "
        "engage in independent learning."
    ),

}


# ============================================================
# 5. DEFAULT PROGRAM SPECIFIC OUTCOMES
# ============================================================

DEFAULT_PSOS = {

    "PSO1": (
        "Technical Application",
        "Apply computing, AI and data-driven technologies "
        "to develop practical engineering solutions."
    ),

    "PSO2": (
        "Industry Readiness",
        "Apply modern software, AI and engineering tools "
        "to solve industry-oriented problems."
    ),

    "PSO3": (
        "Innovation",
        "Design and implement technology-driven solutions "
        "for real-world applications."
    ),

}


# ============================================================
# 6. BLOOM TAXONOMY
# ============================================================

BLOOM_LEVELS = {

    "Remember": [
        "define",
        "identify",
        "list",
        "state",
        "recognize",
        "recall",
    ],

    "Understand": [
        "explain",
        "describe",
        "summarize",
        "interpret",
        "discuss",
    ],

    "Apply": [
        "apply",
        "implement",
        "use",
        "execute",
        "demonstrate",
        "develop",
    ],

    "Analyze": [
        "analyze",
        "compare",
        "differentiate",
        "examine",
        "evaluate",
    ],

    "Evaluate": [
        "evaluate",
        "assess",
        "validate",
        "critique",
        "justify",
    ],

    "Create": [
        "design",
        "develop",
        "construct",
        "create",
        "formulate",
        "build",
    ],

}


# ============================================================
# 7. DETECT BLOOM LEVEL
# ============================================================

def detect_bloom_level(
    text,
    default="Apply",
):
    """
    Infer Bloom level from learning outcome text.
    """

    text = safe_text(
        text
    ).lower()


    for level, verbs in BLOOM_LEVELS.items():

        for verb in verbs:

            if verb in text:

                return level


    return default


# ============================================================
# 8. BLOOM NUMERIC LEVEL
# ============================================================

BLOOM_SCORE = {

    "Remember":
        1,

    "Understand":
        2,

    "Apply":
        3,

    "Analyze":
        4,

    "Evaluate":
        5,

    "Create":
        6,

}


# ============================================================
# 9. GENERATE COURSE OUTCOMES
# ============================================================

def generate_course_outcomes(
    modules,
):
    """
    Generate course-level COs from final modules.

    Maximum recommended COs = 6.
    """

    outcomes = []


    # --------------------------------------------------------
    # Outcome templates
    # --------------------------------------------------------

    templates = [

        (
            "Explain and apply the fundamental concepts "
            "covered in the course."
        ),

        (
            "Analyze engineering problems using appropriate "
            "computational and analytical techniques."
        ),

        (
            "Implement practical solutions using relevant "
            "software tools and technologies."
        ),

        (
            "Evaluate technical solutions using appropriate "
            "performance and validation methods."
        ),

        (
            "Design and develop industry-oriented solutions "
            "through practical projects."
        ),

        (
            "Demonstrate professional, ethical and "
            "lifelong-learning capabilities."
        ),

    ]


    for index, template in enumerate(

        templates,

        start=1,

    ):

        outcomes.append({

            "co_id":
                f"CO{index}",

            "statement":
                template,

            "bloom_level":
                detect_bloom_level(
                    template
                ),

            "bloom_score":
                BLOOM_SCORE.get(

                    detect_bloom_level(
                        template
                    ),

                    3,

                ),

        })


    return outcomes


# ============================================================
# 10. GENERATE MODULE-SPECIFIC OUTCOMES
# ============================================================

def generate_module_outcomes(
    module,
):
    """
    Convert module learning outcomes into structured outcomes.
    """

    existing = normalize_list(

        module.get(
            "module_learning_outcomes"
        )

    )


    if existing:

        return existing


    module_name = safe_text(

        module.get(
            "module_name"
        ),

        "this module",

    )


    return [

        (
            f"Explain the key concepts associated with "
            f"{module_name}."
        ),

        (
            f"Apply {module_name} concepts to practical "
            "engineering problems."
        ),

        (
            f"Implement practical solutions using "
            f"{module_name}."
        ),

    ]


# ============================================================
# 11. CO-PO MAPPING RULE
# ============================================================

def calculate_co_po_value(
    co,
    po_code,
    modules,
):
    """
    Generate a transparent CO-PO mapping.

    Scale:

    0 = No direct correlation
    1 = Low
    2 = Moderate
    3 = High
    """

    co_text = safe_text(

        co.get(
            "statement"
        )

    ).lower()


    bloom = safe_text(

        co.get(
            "bloom_level"
        )

    )


    # --------------------------------------------------------
    # CO1 / Fundamentals
    # --------------------------------------------------------

    if co.get(
        "co_id"
    ) == "CO1":

        mapping = {

            "PO1": 3,

            "PO2": 2,

            "PO3": 1,

            "PO4": 1,

            "PO5": 1,

            "PO6": 0,

            "PO7": 0,

            "PO8": 0,

            "PO9": 0,

            "PO10": 1,

            "PO11": 0,

            "PO12": 2,

        }


        return mapping.get(
            po_code,
            0
        )


    # --------------------------------------------------------
    # CO2 / Analysis
    # --------------------------------------------------------

    if co.get(
        "co_id"
    ) == "CO2":

        mapping = {

            "PO1": 2,

            "PO2": 3,

            "PO3": 2,

            "PO4": 2,

            "PO5": 2,

            "PO6": 1,

            "PO7": 1,

            "PO8": 0,

            "PO9": 1,

            "PO10": 1,

            "PO11": 1,

            "PO12": 2,

        }


        return mapping.get(
            po_code,
            0
        )


    # --------------------------------------------------------
    # CO3 / Implementation
    # --------------------------------------------------------

    if co.get(
        "co_id"
    ) == "CO3":

        mapping = {

            "PO1": 2,

            "PO2": 2,

            "PO3": 3,

            "PO4": 2,

            "PO5": 3,

            "PO6": 1,

            "PO7": 1,

            "PO8": 0,

            "PO9": 2,

            "PO10": 1,

            "PO11": 1,

            "PO12": 2,

        }


        return mapping.get(
            po_code,
            0
        )


    # --------------------------------------------------------
    # CO4 / Evaluation
    # --------------------------------------------------------

    if co.get(
        "co_id"
    ) == "CO4":

        mapping = {

            "PO1": 2,

            "PO2": 3,

            "PO3": 2,

            "PO4": 3,

            "PO5": 2,

            "PO6": 1,

            "PO7": 1,

            "PO8": 1,

            "PO9": 1,

            "PO10": 1,

            "PO11": 1,

            "PO12": 2,

        }


        return mapping.get(
            po_code,
            0
        )


    # --------------------------------------------------------
    # CO5 / Design
    # --------------------------------------------------------

    if co.get(
        "co_id"
    ) == "CO5":

        mapping = {

            "PO1": 2,

            "PO2": 2,

            "PO3": 3,

            "PO4": 2,

            "PO5": 3,

            "PO6": 1,

            "PO7": 1,

            "PO8": 1,

            "PO9": 3,

            "PO10": 2,

            "PO11": 3,

            "PO12": 2,

        }


        return mapping.get(
            po_code,
            0
        )


    # --------------------------------------------------------
    # CO6 / Professional learning
    # --------------------------------------------------------

    if co.get(
        "co_id"
    ) == "CO6":

        mapping = {

            "PO1": 1,

            "PO2": 1,

            "PO3": 1,

            "PO4": 1,

            "PO5": 2,

            "PO6": 2,

            "PO7": 2,

            "PO8": 3,

            "PO9": 3,

            "PO10": 3,

            "PO11": 3,

            "PO12": 3,

        }


        return mapping.get(
            po_code,
            0
        )


    return 0


# ============================================================
# 12. CO-PSO MAPPING
# ============================================================

def calculate_co_pso_value(
    co_id,
    pso_code,
):
    """
    Generate CO-PSO mapping.

    Scale:

    0 = No correlation
    1 = Low
    2 = Moderate
    3 = High
    """

    mapping = {

        "CO1": {
            "PSO1": 3,
            "PSO2": 1,
            "PSO3": 1,
        },

        "CO2": {
            "PSO1": 3,
            "PSO2": 2,
            "PSO3": 2,
        },

        "CO3": {
            "PSO1": 3,
            "PSO2": 3,
            "PSO3": 2,
        },

        "CO4": {
            "PSO1": 3,
            "PSO2": 3,
            "PSO3": 2,
        },

        "CO5": {
            "PSO1": 3,
            "PSO2": 3,
            "PSO3": 3,
        },

        "CO6": {
            "PSO1": 2,
            "PSO2": 3,
            "PSO3": 3,
        },

    }


    return mapping.get(

        co_id,

        {}

    ).get(

        pso_code,

        0,

    )


# ============================================================
# 13. MAP TOPIC TO CO
# ============================================================

def map_topic_to_co(
    topic,
):
    """
    Map topic to one or more course outcomes.

    Returns CO codes.
    """

    topic_text = safe_text(

        f"""
        {topic.get("topic_name")}
        {topic.get("description")}
        {" ".join(topic.get("concepts", []))}
        {" ".join(topic.get("technologies", []))}
        """

    ).lower()


    mapping = []


    # Fundamentals
    if any(

        keyword in topic_text

        for keyword in [

            "fundamental",
            "basic",
            "introduction",
            "concept",
            "theory",

        ]

    ):

        mapping.append(
            "CO1"
        )


    # Analysis
    if any(

        keyword in topic_text

        for keyword in [

            "analysis",
            "analyze",
            "compare",
            "evaluation",
            "data analysis",

        ]

    ):

        mapping.append(
            "CO2"
        )


    # Implementation
    if any(

        keyword in topic_text

        for keyword in [

            "implement",
            "coding",
            "programming",
            "tool",
            "technology",
            "framework",

        ]

    ):

        mapping.append(
            "CO3"
        )


    # Evaluation
    if any(

        keyword in topic_text

        for keyword in [

            "evaluate",
            "validation",
            "testing",
            "performance",
            "assessment",

        ]

    ):

        mapping.append(
            "CO4"
        )


    # Design
    if any(

        keyword in topic_text

        for keyword in [

            "design",
            "develop",
            "project",
            "architecture",
            "application",

        ]

    ):

        mapping.append(
            "CO5"
        )


    # Professional
    if any(

        keyword in topic_text

        for keyword in [

            "industry",
            "ethics",
            "team",
            "communication",
            "deployment",
            "professional",

        ]

    ):

        mapping.append(
            "CO6"
        )


    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not mapping:

        mapping.append(
            "CO1"
        )


    return unique_values(
        mapping
    )


# ============================================================
# 14. MAP TOPIC TO POs
# ============================================================

def topic_po_mapping(
    topic,
):
    """
    Determine directly relevant POs from topic content.
    """

    text = safe_text(

        f"""
        {topic.get("topic_name")}
        {topic.get("description")}
        {" ".join(topic.get("concepts", []))}
        {" ".join(topic.get("tools", []))}
        {" ".join(topic.get("technologies", []))}
        """

    ).lower()


    po_codes = []


    if any(

        item in text

        for item in [

            "algorithm",
            "mathematics",
            "model",
            "machine learning",
            "deep learning",
            "programming",

        ]

    ):

        po_codes.append(
            "PO1"
        )


    if any(

        item in text

        for item in [

            "analysis",
            "problem",
            "data",
            "evaluation",

        ]

    ):

        po_codes.append(
            "PO2"
        )


    if any(

        item in text

        for item in [

            "design",
            "develop",
            "architecture",
            "application",
            "project",

        ]

    ):

        po_codes.append(
            "PO3"
        )


    if any(

        item in text

        for item in [

            "experiment",
            "research",
            "investigation",
            "validation",

        ]

    ):

        po_codes.append(
            "PO4"
        )


    if any(

        item in text

        for item in [

            "python",
            "software",
            "tool",
            "framework",
            "technology",
            "docker",
            "cloud",
            "llm",
            "ai",

        ]

    ):

        po_codes.append(
            "PO5"
        )


    if any(

        item in text

        for item in [

            "team",
            "collaboration",

        ]

    ):

        po_codes.append(
            "PO9"
        )


    if any(

        item in text

        for item in [

            "communication",
            "presentation",
            "documentation",

        ]

    ):

        po_codes.append(
            "PO10"
        )


    if any(

        item in text

        for item in [

            "project",
            "management",
            "deployment",

        ]

    ):

        po_codes.append(
            "PO11"
        )


    if any(

        item in text

        for item in [

            "lifelong",
            "learning",
            "research",

        ]

    ):

        po_codes.append(
            "PO12"
        )


    return unique_values(
        po_codes
    )


# ============================================================
# 15. CREATE STRUCTURED MODULE
# ============================================================

def structure_module(
    module,
):
    """
    Convert final module to formal academic structure.
    """

    module_id = safe_text(

        module.get(
            "module_id"
        )

    )


    if not module_id:

        sequence = module.get(
            "sequence",
            1,
        )


        module_id = (
            f"M{sequence}"
        )


    module_name = safe_text(

        module.get(
            "module_name"
        ),

        f"Module {module_id}",

    )


    module_hours = safe_number(

        module.get(
            "recommended_hours",
            0,
        )

    )


    module_outcomes = generate_module_outcomes(

        module

    )


    structured_topics = []


    for index, topic in enumerate(

        module.get(
            "topics",
            []
        ),

        start=1,

    ):

        if not isinstance(
            topic,
            dict,
        ):

            continue


        topic_id = safe_text(

            topic.get(
                "topic_id"
            )

        )


        if not topic_id:

            topic_id = (

                f"{module_id}.T{index}"

            )


        topic_name = safe_text(

            topic.get(
                "topic_name"
            ),

            f"Topic {index}",

        )


        topic_description = safe_text(

            topic.get(
                "description"
            )

        )


        topic_hours = safe_number(

            topic.get(
                "hours",
                0,
            )

        )


        concepts = normalize_list(

            topic.get(
                "concepts"
            )

        )


        tools = normalize_list(

            topic.get(
                "tools"
            )

        )


        technologies = normalize_list(

            topic.get(
                "technologies"
            )

        )


        learning_outcomes = normalize_list(

            topic.get(
                "learning_outcomes"
            )

        )


        assessment_methods = normalize_list(

            topic.get(
                "assessment_methods"
            )

        )


        topic_cos = map_topic_to_co(

            topic

        )


        topic_pos = topic_po_mapping(

            topic

        )


        bloom_levels = []


        for outcome in learning_outcomes:

            bloom_levels.append(

                detect_bloom_level(
                    outcome
                )

            )


        bloom_levels = unique_values(

            bloom_levels

        )


        structured_topics.append({

            "topic_id":
                topic_id,

            "topic_name":
                topic_name,

            "description":
                topic_description,

            "hours":
                topic_hours,

            "concepts":
                concepts,

            "tools":
                tools,

            "technologies":
                technologies,

            "learning_outcomes":
                learning_outcomes,

            "bloom_levels":
                bloom_levels,

            "co_mapping":
                topic_cos,

            "po_mapping":
                topic_pos,

            "assessment_methods":
                assessment_methods,

            "theory_hours":
                round(
                    topic_hours * 0.6,
                    2,
                ),

            "practical_hours":
                round(
                    topic_hours * 0.4,
                    2,
                ),

            "lab_required":
                bool(

                    topic.get(
                        "lab_required",
                        True,
                    )

                ),

            "project_required":
                bool(

                    topic.get(
                        "project_required",
                        False,
                    )

                ),

        })


    return {

        "module_id":
            module_id,

        "module_name":
            module_name,

        "sequence":
            module.get(
                "sequence",
                1,
            ),

        "purpose":
            safe_text(
                module.get(
                    "purpose"
                )
            ),

        "level":
            safe_text(
                module.get(
                    "level"
                )
            ),

        "recommended_hours":
            module_hours,

        "prerequisites":
            normalize_list(

                module.get(
                    "prerequisites"
                )

            ),

        "topics":
            structured_topics,

        "module_learning_outcomes":
            module_outcomes,

        "module_project":
            safe_text(

                module.get(
                    "module_project"
                )

            ),

        "industry_skills":
            normalize_list(

                module.get(
                    "industry_skills"
                )

            ),

    }


# ============================================================
# 16. BUILD FINAL MODULE STRUCTURE
# ============================================================

academic_modules = [

    structure_module(
        module
    )

    for module in final_modules

    if isinstance(
        module,
        dict,
    )

]


# ============================================================
# 17. SORT MODULES
# ============================================================

academic_modules.sort(

    key=lambda x:
        safe_number(
            x.get(
                "sequence",
                0,
            )
        )

)


# ============================================================
# 18. GENERATE COs
# ============================================================

course_outcomes = generate_course_outcomes(

    academic_modules

)


st.session_state[
    "course_outcomes"
] = course_outcomes


# ============================================================
# 19. GENERATE POs
# ============================================================

program_outcomes = []


for code, data in DEFAULT_PROGRAM_OUTCOMES.items():

    name, statement = data


    program_outcomes.append({

        "po_code":
            code,

        "name":
            name,

        "statement":
            statement,

    })


st.session_state[
    "program_outcomes"
] = program_outcomes


# ============================================================
# 20. GENERATE PSOs
# ============================================================

program_specific_outcomes = []


for code, data in DEFAULT_PSOS.items():

    name, statement = data


    program_specific_outcomes.append({

        "pso_code":
            code,

        "name":
            name,

        "statement":
            statement,

    })


st.session_state[
    "program_specific_outcomes"
] = (
    program_specific_outcomes
)


# ============================================================
# 21. CO-PO MATRIX
# ============================================================

co_po_matrix = []


for co in course_outcomes:

    row = {

        "CO":
            co.get(
                "co_id"
            ),

        "Statement":
            co.get(
                "statement"
            ),

    }


    for po in program_outcomes:

        po_code = po.get(
            "po_code"
        )


        row[po_code] = calculate_co_po_value(

            co,

            po_code,

            academic_modules,

        )


    co_po_matrix.append(
        row
    )


st.session_state[
    "co_po_matrix"
] = co_po_matrix


# ============================================================
# 22. CO-PSO MATRIX
# ============================================================

co_pso_matrix = []


for co in course_outcomes:

    row = {

        "CO":
            co.get(
                "co_id"
            ),

        "Statement":
            co.get(
                "statement"
            ),

    }


    for pso in program_specific_outcomes:

        pso_code = pso.get(
            "pso_code"
        )


        row[pso_code] = calculate_co_pso_value(

            co.get(
                "co_id"
            ),

            pso_code,

        )


    co_pso_matrix.append(
        row
    )


st.session_state[
    "co_pso_matrix"
] = co_pso_matrix


# ============================================================
# 23. CO COVERAGE ANALYSIS
# ============================================================

co_coverage = {}


for co in course_outcomes:

    co_id = co.get(
        "co_id"
    )


    count = 0


    for module in academic_modules:

        for topic in module.get(
            "topics",
            [],
        ):

            if co_id in topic.get(
                "co_mapping",
                [],
            ):

                count += 1


    co_coverage[co_id] = count


st.session_state[
    "co_coverage"
] = co_coverage


# ============================================================
# 24. PO COVERAGE ANALYSIS
# ============================================================

po_coverage = {}


for po in program_outcomes:

    po_code = po.get(
        "po_code"
    )


    count = 0


    for module in academic_modules:

        for topic in module.get(
            "topics",
            [],
        ):

            if po_code in topic.get(
                "po_mapping",
                [],
            ):

                count += 1


    po_coverage[po_code] = count


st.session_state[
    "po_coverage"
] = po_coverage


# ============================================================
# 25. TOTAL HOURS
# ============================================================

total_hours = sum(

    safe_number(

        module.get(
            "recommended_hours",
            0,
        )

    )

    for module in academic_modules

)


total_topic_hours = sum(

    safe_number(

        topic.get(
            "hours",
            0,
        )

    )

    for module in academic_modules

    for topic in module.get(
        "topics",
        []
    )

)


# ============================================================
# 26. THEORY / PRACTICAL HOURS
# ============================================================

total_theory_hours = sum(

    safe_number(

        topic.get(
            "theory_hours",
            0,
        )

    )

    for module in academic_modules

    for topic in module.get(
        "topics",
        []
    )

)


total_practical_hours = sum(

    safe_number(

        topic.get(
            "practical_hours",
            0,
        )

    )

    for module in academic_modules

    for topic in module.get(
        "topics",
        []
    )

)


# ============================================================
# 27. CURRICULUM VALIDATION
# ============================================================

validation_issues = []


validation_warnings = []


validation_passes = []


# ------------------------------------------------------------
# Module validation
# ------------------------------------------------------------

if not academic_modules:

    validation_issues.append(
        "No academic modules generated."
    )

else:

    validation_passes.append(
        "Academic modules are available."
    )


# ------------------------------------------------------------
# CO validation
# ------------------------------------------------------------

if len(
    course_outcomes
) < 4:

    validation_warnings.append(
        "Fewer than four Course Outcomes are defined."
    )

else:

    validation_passes.append(
        "Course Outcomes are defined."
    )


# ------------------------------------------------------------
# PO validation
# ------------------------------------------------------------

if len(
    program_outcomes
) < 10:

    validation_warnings.append(
        "Program Outcome set may be incomplete."
    )

else:

    validation_passes.append(
        "Program Outcomes are defined."
    )


# ------------------------------------------------------------
# Topic validation
# ------------------------------------------------------------

topic_count = sum(

    len(

        module.get(
            "topics",
            []
        )

    )

    for module in academic_modules

)


if topic_count == 0:

    validation_issues.append(
        "No topics are present."
    )

else:

    validation_passes.append(
        f"{topic_count} topics are structured."
    )


# ------------------------------------------------------------
# Hours validation
# ------------------------------------------------------------

if total_hours <= 0:

    validation_issues.append(
        "Total curriculum hours are zero."
    )

else:

    validation_passes.append(
        f"Total curriculum hours: {total_hours}."
    )


# ------------------------------------------------------------
# CO mapping validation
# ------------------------------------------------------------

unmapped_topics = []


for module in academic_modules:

    for topic in module.get(
        "topics",
        []
    ):

        if not topic.get(
            "co_mapping"
        ):

            unmapped_topics.append(

                topic.get(
                    "topic_name"
                )

            )


if unmapped_topics:

    validation_warnings.append(

        f"{len(unmapped_topics)} topics have no CO mapping."

    )

else:

    validation_passes.append(
        "All topics have CO mapping."
    )


# ------------------------------------------------------------
# PO mapping validation
# ------------------------------------------------------------

unmapped_po_topics = []


for module in academic_modules:

    for topic in module.get(
        "topics",
        []
    ):

        if not topic.get(
            "po_mapping"
        ):

            unmapped_po_topics.append(

                topic.get(
                    "topic_name"
                )

            )


if unmapped_po_topics:

    validation_warnings.append(

        f"{len(unmapped_po_topics)} topics have no PO mapping."

    )

else:

    validation_passes.append(
        "Topics have PO mappings."
    )


# ------------------------------------------------------------
# Practical validation
# ------------------------------------------------------------

if total_practical_hours <= 0:

    validation_warnings.append(
        "No practical hours detected."
    )

else:

    validation_passes.append(
        "Practical learning hours are present."
    )


# ------------------------------------------------------------
# Project validation
# ------------------------------------------------------------

if not final_projects:

    validation_warnings.append(
        "No industry projects are defined."
    )

else:

    validation_passes.append(
        f"{len(final_projects)} industry projects defined."
    )


# ============================================================
# 28. INDUSTRY COVERAGE
# ============================================================

industry_skill_count = len(

    unique_values(

        industry_skills_covered

    )

)


tool_count = len(

    unique_values(
        final_tools
    )

)


technology_count = len(

    unique_values(
        final_technologies
    )

)


concept_count = len(

    unique_values(
        final_concepts
    )

)


# ============================================================
# 29. SYLLABUS METADATA
# ============================================================

course_code = safe_text(

    course_metadata.get(
        "course_code"
    ),

    st.session_state.get(
        "course_code",
        ""
    ),

)


course_name = safe_text(

    course_metadata.get(
        "course_name"
    ),

    st.session_state.get(
        "subject_name",
        ""
    ),

)


university_name = safe_text(

    course_metadata.get(
        "university"
    ),

    st.session_state.get(
        "university_name",
        ""
    ),

)


college_name = safe_text(

    course_metadata.get(
        "college"
    ),

    st.session_state.get(
        "college_name",
        ""
    ),

)


# ============================================================
# 30. BUILD ACADEMIC SYLLABUS
# ============================================================

academic_syllabus = {

    "course_information": {

        "course_code":
            course_code,

        "course_name":
            course_name,

        "university":
            university_name,

        "college":
            college_name,

        "total_hours":
            total_hours,

        "theory_hours":
            round(
                total_theory_hours,
                2,
            ),

        "practical_hours":
            round(
                total_practical_hours,
                2,
            ),

        "module_count":
            len(
                academic_modules
            ),

        "topic_count":
            topic_count,

        "industry_skill_count":
            industry_skill_count,

        "tool_count":
            tool_count,

        "technology_count":
            technology_count,

    },


    "course_outcomes":
        course_outcomes,


    "program_outcomes":
        program_outcomes,


    "program_specific_outcomes":
        program_specific_outcomes,


    "modules":
        academic_modules,


    "co_po_matrix":
        co_po_matrix,


    "co_pso_matrix":
        co_pso_matrix,


    "industry_skills":
        industry_skills_covered,


    "tools":
        final_tools,


    "technologies":
        final_technologies,


    "concepts":
        final_concepts,


    "projects":
        final_projects,


    "validation": {

        "passes":
            validation_passes,

        "warnings":
            validation_warnings,

        "issues":
            validation_issues,

    },


    "generated_at":
        datetime.now().isoformat(),

}


# ============================================================
# 31. SAVE ACADEMIC SYLLABUS
# ============================================================

st.session_state[
    "academic_syllabus"
] = academic_syllabus


st.session_state[
    "academic_syllabus_complete"
] = bool(

    academic_modules

    and

    course_outcomes

)


# ============================================================
# 32. DISPLAY HEADER
# ============================================================

st.divider()

st.subheader(
    "🎓 Academic Syllabus Structure"
)


st.markdown(
    """
The AI-enhanced curriculum has now been converted into a
structured academic syllabus containing:

**Modules → Topics → Hours → CO → PO → PSO → Bloom Level →
Tools → Technologies → Labs → Projects → Assessment**
"""
)


# ============================================================
# 33. COURSE METRICS
# ============================================================

metric_cols = st.columns(
    6
)


with metric_cols[0]:

    st.metric(
        "Modules",
        len(
            academic_modules
        ),
    )


with metric_cols[1]:

    st.metric(
        "Topics",
        topic_count,
    )


with metric_cols[2]:

    st.metric(
        "Hours",
        total_hours,
    )


with metric_cols[3]:

    st.metric(
        "COs",
        len(
            course_outcomes
        ),
    )


with metric_cols[4]:

    st.metric(
        "POs",
        len(
            program_outcomes
        ),
    )


with metric_cols[5]:

    st.metric(
        "Projects",
        len(
            final_projects
        ),
    )


# ============================================================
# 34. COURSE OUTCOMES DISPLAY
# ============================================================

st.divider()

st.subheader(
    "🎯 Course Outcomes"
)


co_rows = []


for co in course_outcomes:

    co_rows.append({

        "CO":
            co.get(
                "co_id"
            ),

        "Outcome":
            co.get(
                "statement"
            ),

        "Bloom":
            co.get(
                "bloom_level"
            ),

        "Level":
            co.get(
                "bloom_score"
            ),

        "Topic Coverage":
            co_coverage.get(
                co.get(
                    "co_id"
                ),
                0,
            ),

    })


st.dataframe(

    pd.DataFrame(
        co_rows
    ),

    use_container_width=True,

    hide_index=True,

)


# ============================================================
# 35. PROGRAM OUTCOMES DISPLAY
# ============================================================

st.divider()

st.subheader(
    "🎓 Program Outcomes"
)


po_rows = []


for po in program_outcomes:

    po_code = po.get(
        "po_code"
    )


    po_rows.append({

        "PO":
            po_code,

        "Name":
            po.get(
                "name"
            ),

        "Statement":
            po.get(
                "statement"
            ),

        "Topic Coverage":
            po_coverage.get(
                po_code,
                0,
            ),

    })


st.dataframe(

    pd.DataFrame(
        po_rows
    ),

    use_container_width=True,

    hide_index=True,

)


# ============================================================
# 36. PROGRAM SPECIFIC OUTCOMES
# ============================================================

st.divider()

st.subheader(
    "🎯 Program Specific Outcomes"
)


pso_rows = []


for pso in program_specific_outcomes:

    pso_rows.append({

        "PSO":
            pso.get(
                "pso_code"
            ),

        "Name":
            pso.get(
                "name"
            ),

        "Statement":
            pso.get(
                "statement"
            ),

    })


st.dataframe(

    pd.DataFrame(
        pso_rows
    ),

    use_container_width=True,

    hide_index=True,

)


# ============================================================
# 37. CO-PO MATRIX
# ============================================================

st.divider()

st.subheader(
    "📊 CO–PO Mapping Matrix"
)


co_po_df = pd.DataFrame(
    co_po_matrix
)


st.session_state[
    "co_po_matrix_df"
] = co_po_df


st.dataframe(

    co_po_df,

    use_container_width=True,

    hide_index=True,

)


# ============================================================
# 38. CO-PSO MATRIX
# ============================================================

st.divider()

st.subheader(
    "📊 CO–PSO Mapping Matrix"
)


co_pso_df = pd.DataFrame(
    co_pso_matrix
)


st.session_state[
    "co_pso_matrix_df"
] = co_pso_df


st.dataframe(

    co_pso_df,

    use_container_width=True,

    hide_index=True,

)


# ============================================================
# 39. MODULE STRUCTURE
# ============================================================

st.divider()

st.subheader(
    "📚 Module-wise Academic Structure"
)


for module in academic_modules:

    module_name = safe_text(

        module.get(
            "module_name"
        ),

        "Module",

    )


    with st.expander(

        f"""
        {module.get("module_id")}
        —
        {module_name}
        """

    ):

        st.write(

            "**Hours:**",

            module.get(
                "recommended_hours"
            ),

        )


        st.write(

            "**Level:**",

            module.get(
                "level"
            ),

        )


        topics = module.get(
            "topics",
            []
        )


        if topics:

            topic_rows = []


            for topic in topics:

                topic_rows.append({

                    "Topic":
                        topic.get(
                            "topic_name"
                        ),

                    "Hours":
                        topic.get(
                            "hours"
                        ),

                    "CO":
                        ", ".join(

                            topic.get(
                                "co_mapping",
                                []
                            )

                        ),

                    "PO":
                        ", ".join(

                            topic.get(
                                "po_mapping",
                                []
                            )

                        ),

                    "Bloom":
                        ", ".join(

                            topic.get(
                                "bloom_levels",
                                []
                            )

                        ),

                    "Lab":
                        "Yes"
                        if topic.get(
                            "lab_required"
                        )
                        else
                        "No",

                    "Project":
                        "Yes"
                        if topic.get(
                            "project_required"
                        )
                        else
                        "No",

                })


            st.dataframe(

                pd.DataFrame(
                    topic_rows
                ),

                use_container_width=True,

                hide_index=True,

            )


# ============================================================
# 40. VALIDATION REPORT
# ============================================================

st.divider()

st.subheader(
    "✅ Academic Syllabus Validation"
)


if validation_passes:

    st.markdown(
        "### ✅ Passed"
    )


    for item in validation_passes:

        st.markdown(
            f"- {item}"
        )


if validation_warnings:

    st.markdown(
        "### ⚠️ Warnings"
    )


    for item in validation_warnings:

        st.warning(
            item
        )


if validation_issues:

    st.markdown(
        "### ❌ Issues"
    )


    for item in validation_issues:

        st.error(
            item
        )


# ============================================================
# 41. DOWNLOAD ACADEMIC SYLLABUS
# ============================================================

st.divider()


st.download_button(

    "⬇️ Download Academic Syllabus JSON",

    data=serialize_json(

        academic_syllabus

    ),

    file_name=(
        "academic_enhanced_syllabus.json"
    ),

    mime="application/json",

    key="download_academic_syllabus",

)


# ============================================================
# 42. DOWNLOAD CO-PO MATRIX
# ============================================================

if co_po_matrix:

    st.download_button(

        "⬇️ Download CO–PO Matrix CSV",

        data=co_po_df.to_csv(
            index=False
        ),

        file_name=(
            "CO_PO_Matrix.csv"
        ),

        mime="text/csv",

        key="download_co_po_matrix",

    )


# ============================================================
# 43. COMPLETION STATUS
# ============================================================

if st.session_state.get(

    "academic_syllabus_complete",

    False,

):

    st.success(
        """
        🎉 **Academic Syllabus Structuring Complete**

        The final enhanced curriculum now has:

        ✓ Course Outcomes (CO)
        ✓ Program Outcomes (PO)
        ✓ Program Specific Outcomes (PSO)
        ✓ CO–PO Matrix
        ✓ CO–PSO Matrix
        ✓ Module-wise structure
        ✓ Topic-wise hours
        ✓ Bloom levels
        ✓ Industry skills
        ✓ Tools
        ✓ Technologies
        ✓ Practical learning
        ✓ Project mapping
        ✓ Assessment mapping
        ✓ Validation report

        This structured syllabus can now drive the next
        learning-intelligence modules.
        """
    )


# ============================================================
# END OF CHUNK 8/10
# ============================================================
# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 9/10
# AI LESSON PLAN + TEACHING CONTENT GENERATOR
# ============================================================

"""
Purpose
-------
Generate a complete teaching package for every topic in the
final validated academic syllabus.

Input
-----

st.session_state["academic_syllabus"]

Output
------

st.session_state["lesson_plans"]

st.session_state["teaching_content"]

st.session_state["pre_class_content"]

st.session_state["in_class_content"]

st.session_state["post_class_content"]

st.session_state["lesson_plan_complete"]

Every topic receives:

    1-hour lesson plan
    Learning objectives
    Prerequisites
    Pre-class reading
    Pre-class MCQs
    Faculty notes
    Concept explanation
    Examples
    Classroom activity
    Hands-on exercise
    Post-class reading
    Assignment
    Practice MCQs
    Assessment
    Industry connection
    Teacher focus

Technology
----------

Groq
Llama
LangChain
Streamlit
"""


# ============================================================
# 1. LOAD ACADEMIC SYLLABUS
# ============================================================

academic_syllabus = st.session_state.get(
    "academic_syllabus",
    {}
)


academic_modules = academic_syllabus.get(
    "modules",
    []
)


course_outcomes = academic_syllabus.get(
    "course_outcomes",
    []
)


program_outcomes = academic_syllabus.get(
    "program_outcomes",
    []
)


program_specific_outcomes = academic_syllabus.get(
    "program_specific_outcomes",
    []
)


# ============================================================
# 2. LOAD INDUSTRY INFORMATION
# ============================================================

industry_skills_covered = st.session_state.get(
    "industry_skills_covered",
    []
)


final_tools = st.session_state.get(
    "final_tools",
    []
)


final_technologies = st.session_state.get(
    "final_technologies",
    []
)


final_projects = st.session_state.get(
    "final_projects",
    []
)


remaining_industry_gaps = st.session_state.get(
    "remaining_industry_gaps",
    []
)


# ============================================================
# 3. VALIDATION
# ============================================================

if not academic_syllabus:

    st.warning(
        """
        ⚠️ Academic syllabus is not available.

        Complete Chunk 8 before generating lesson plans.
        """
    )


if not academic_modules:

    st.warning(
        """
        ⚠️ No academic modules are available.
        """
    )


# ============================================================
# 4. GROQ CONFIGURATION
# ============================================================

groq_api_key = os.getenv(
    "GROQ_API_KEY",
    "",
).strip()


groq_model = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
).strip()


if not groq_api_key:

    try:

        groq_api_key = st.secrets.get(
            "GROQ_API_KEY",
            "",
        )

    except Exception:

        groq_api_key = ""


groq_api_key = safe_text(
    groq_api_key
)


# ============================================================
# 5. CREATE LESSON LLM
# ============================================================

def create_lesson_llm():
    """
    Create Groq LLM for lesson generation.
    """

    if ChatGroq is None:

        return None


    if not groq_api_key:

        return None


    try:

        return ChatGroq(

            api_key=groq_api_key,

            model=groq_model,

            temperature=0.2,

            max_tokens=10000,

        )

    except TypeError:

        try:

            return ChatGroq(

                groq_api_key=groq_api_key,

                model=groq_model,

                temperature=0.2,

                max_tokens=10000,

            )

        except Exception:

            return None

    except Exception:

        return None


lesson_llm = create_lesson_llm()


# ============================================================
# 6. LESSON GENERATION SYSTEM PROMPT
# ============================================================

LESSON_SYSTEM_PROMPT = """
You are an expert university faculty member, instructional
designer, curriculum expert and industry practitioner.

Your task is to create a high-quality ONE-HOUR LESSON PLAN
for one academic topic.

The lesson must be practical, structured, teachable and
appropriate for engineering / technology students.

============================================================
ONE-HOUR RULE
============================================================

The total class time MUST equal approximately 60 minutes.

Recommended structure:

0-5 minutes
    Recap / motivation / prerequisite check

5-15 minutes
    Concept introduction

15-30 minutes
    Detailed concept explanation

30-45 minutes
    Demonstration / worked example / coding

45-55 minutes
    Student hands-on activity

55-60 minutes
    Recap / questions / exit assessment

Adjust the distribution where appropriate.

============================================================
TEACHING PRINCIPLES
============================================================

Do NOT produce generic teaching plans.

Connect the topic to:

- previous topics
- future topics
- real-world applications
- industry requirements
- relevant tools
- practical problems

Teach concepts first.

Then demonstrate tools.

Do not turn the class into a tool tutorial.

============================================================
PRE-CLASS
============================================================

Prepare:

- prerequisites
- short reading
- preparation checklist
- 5 MCQs
- expected preparation time

============================================================
IN-CLASS
============================================================

Prepare:

- learning objectives
- detailed instructor flow
- explanation points
- examples
- classroom questions
- demonstration
- activity
- hands-on exercise
- expected student output
- common misconceptions

============================================================
POST-CLASS
============================================================

Prepare:

- study material
- summary
- assignment
- practical task
- 5 practice MCQs
- reflection questions
- further reading
- expected submission

============================================================
FACULTY SUPPORT
============================================================

Provide:

- what the teacher should emphasize
- what the teacher should not spend excessive time on
- common student difficulties
- likely misconceptions
- intervention suggestions
- questions to ask students

============================================================
ASSESSMENT
============================================================

Assessment should align with the learning objectives and
Bloom's level.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use this exact structure:

{
  "lesson_metadata": {
    "module_id": "",
    "module_name": "",
    "topic_id": "",
    "topic_name": "",
    "duration_minutes": 60,
    "level": "",
    "hours": 1
  },

  "learning_objectives": [],

  "prerequisites": [],

  "co_mapping": [],

  "po_mapping": [],

  "industry_skills": [],

  "tools": [],

  "technologies": [],

  "pre_class": {
    "purpose": "",
    "estimated_time_minutes": 15,
    "reading_material": [],
    "preparation_checklist": [],
    "mcqs": [
      {
        "question": "",
        "options": [],
        "answer": "",
        "explanation": ""
      }
    ]
  },

  "one_hour_plan": [
    {
      "start_minute": 0,
      "end_minute": 5,
      "duration": 5,
      "segment": "",
      "teacher_action": "",
      "student_action": "",
      "content": "",
      "activity": ""
    }
  ],

  "concept_explanation": {
    "core_concepts": [],
    "detailed_explanation": "",
    "worked_example": "",
    "real_world_example": "",
    "industry_example": ""
  },

  "faculty_notes": {
    "key_points": [],
    "emphasize": [],
    "avoid_overexplaining": [],
    "common_misconceptions": [],
    "likely_student_questions": [],
    "teacher_questions": []
  },

  "hands_on_activity": {
    "title": "",
    "objective": "",
    "instructions": [],
    "expected_output": "",
    "tools_required": [],
    "time_minutes": 15
  },

  "post_class": {
    "summary": "",
    "study_material": [],
    "assignment": {
      "title": "",
      "problem_statement": "",
      "requirements": [],
      "deliverables": [],
      "difficulty": "",
      "estimated_hours": 0
    },
    "mcqs": [
      {
        "question": "",
        "options": [],
        "answer": "",
        "explanation": ""
      }
    ],
    "reflection_questions": [],
    "further_reading": []
  },

  "assessment": {
    "method": "",
    "questions": [],
    "rubric": [],
    "bloom_level": ""
  },

  "teacher_focus": {
    "priority": "",
    "student_risk": "",
    "intervention": "",
    "next_class_preparation": ""
  }
}
"""


# ============================================================
# 7. LESSON USER PROMPT
# ============================================================

LESSON_USER_PROMPT = """
Create a complete one-hour lesson plan for the following topic.

============================================================
COURSE
============================================================

Course Code:
{course_code}

Course Name:
{course_name}


============================================================
MODULE
============================================================

Module ID:
{module_id}

Module Name:
{module_name}

Module Purpose:
{module_purpose}


============================================================
TOPIC
============================================================

Topic ID:
{topic_id}

Topic Name:
{topic_name}

Description:
{topic_description}

Hours:
{topic_hours}

Concepts:
{concepts}

Tools:
{tools}

Technologies:
{technologies}

Learning Outcomes:
{learning_outcomes}

CO Mapping:
{co_mapping}

PO Mapping:
{po_mapping}


============================================================
INDUSTRY CONTEXT
============================================================

Industry Skills:
{industry_skills}

Relevant Technologies:
{industry_technologies}

Remaining Industry Gaps:
{remaining_gaps}


============================================================
PROJECT CONTEXT
============================================================

Relevant Projects:
{projects}


============================================================
REQUIREMENTS
============================================================

Generate a practical 60-minute lesson.

The lesson should:

1. Start from prerequisites.
2. Explain the concept clearly.
3. Include a worked example.
4. Include an industry example.
5. Include teacher-led explanation.
6. Include student participation.
7. Include a hands-on activity.
8. Include a short assessment.
9. Include pre-class reading.
10. Include 5 pre-class MCQs.
11. Include post-class study material.
12. Include an assignment.
13. Include 5 post-class MCQs.
14. Include teacher intervention guidance.
15. Align with CO, PO and Bloom's level.
16. Use tools only where relevant.
17. Avoid unnecessary tool complexity.

The class MUST fit into approximately 60 minutes.

Return ONLY valid JSON.
"""


# ============================================================
# 8. BUILD LESSON PROMPT
# ============================================================

def build_lesson_prompt():

    if ChatPromptTemplate is None:

        return None


    try:

        return ChatPromptTemplate.from_messages([

            (
                "system",
                LESSON_SYSTEM_PROMPT,
            ),

            (
                "human",
                LESSON_USER_PROMPT,
            ),

        ])

    except Exception:

        return None


# ============================================================
# 9. GENERATE ONE LESSON
# ============================================================

def generate_lesson_plan(
    module,
    topic,
):
    """
    Generate lesson plan for one topic.
    """

    if lesson_llm is None:

        return {

            "error":
                (
                    "Groq LLM is not configured."
                )

        }


    prompt = build_lesson_prompt()


    if prompt is None:

        return {

            "error":
                "Unable to create lesson prompt."

        }


    try:

        chain = (
            prompt
            |
            lesson_llm
        )


        course_info = academic_syllabus.get(

            "course_information",

            {}

        )


        response = chain.invoke({

            "course_code":
                course_info.get(
                    "course_code",
                    ""
                ),

            "course_name":
                course_info.get(
                    "course_name",
                    ""
                ),

            "module_id":
                module.get(
                    "module_id"
                ),

            "module_name":
                module.get(
                    "module_name"
                ),

            "module_purpose":
                module.get(
                    "purpose"
                ),

            "topic_id":
                topic.get(
                    "topic_id"
                ),

            "topic_name":
                topic.get(
                    "topic_name"
                ),

            "topic_description":
                topic.get(
                    "description"
                ),

            "topic_hours":
                topic.get(
                    "hours",
                    1
                ),

            "concepts":
                compact_json(
                    topic.get(
                        "concepts",
                        []
                    )
                ),

            "tools":
                compact_json(
                    topic.get(
                        "tools",
                        []
                    )
                ),

            "technologies":
                compact_json(
                    topic.get(
                        "technologies",
                        []
                    )
                ),

            "learning_outcomes":
                compact_json(
                    topic.get(
                        "learning_outcomes",
                        []
                    )
                ),

            "co_mapping":
                compact_json(
                    topic.get(
                        "co_mapping",
                        []
                    )
                ),

            "po_mapping":
                compact_json(
                    topic.get(
                        "po_mapping",
                        []
                    )
                ),

            "industry_skills":
                compact_json(
                    module.get(
                        "industry_skills",
                        []
                    )
                ),

            "industry_technologies":
                compact_json(
                    final_technologies
                ),

            "remaining_gaps":
                compact_json(
                    remaining_industry_gaps
                ),

            "projects":
                compact_json(
                    final_projects
                ),

        })


        if hasattr(
            response,
            "content",
        ):

            response_text = response.content

        else:

            response_text = str(
                response
            )


        result = extract_json_from_response(

            response_text

        )


        result["_metadata"] = {

            "agent":
                "AI Lesson Plan Generator",

            "model":
                groq_model,

            "provider":
                "Groq",

            "topic_id":
                topic.get(
                    "topic_id"
                ),

            "generated_at":
                datetime.now().isoformat(),

        }


        return result


    except Exception as exc:

        return {

            "error":
                str(
                    exc
                )

        }


# ============================================================
# 10. EXTRACT ALL TOPICS
# ============================================================

all_topics_for_lessons = []


for module in academic_modules:

    if not isinstance(
        module,
        dict,
    ):

        continue


    for topic in module.get(
        "topics",
        []
    ):

        if not isinstance(
            topic,
            dict,
        ):

            continue


        all_topics_for_lessons.append({

            "module":
                module,

            "topic":
                topic,

        })


# ============================================================
# 11. DISPLAY HEADER
# ============================================================

st.divider()

st.subheader(
    "📖 AI Lesson Plan Generator"
)


st.markdown(
    """
Generate a complete teaching package for every topic in the
enhanced syllabus.

### Each topic receives

**Pre-Class → 1-Hour Class → Hands-On → Post-Class**

including:

- Reading
- MCQs
- Faculty notes
- Explanation
- Examples
- Activity
- Assignment
- Practice MCQs
- Assessment
- Teacher focus
"""
)


# ============================================================
# 12. TOPIC COUNT
# ============================================================

topic_count = len(
    all_topics_for_lessons
)


metric_cols = st.columns(
    4
)


with metric_cols[0]:

    st.metric(
        "Modules",
        len(
            academic_modules
        ),
    )


with metric_cols[1]:

    st.metric(
        "Topics",
        topic_count,
    )


with metric_cols[2]:

    st.metric(
        "Lesson Duration",
        "60 min",
    )


with metric_cols[3]:

    st.metric(
        "Model",
        groq_model,
    )


# ============================================================
# 13. GENERATION OPTIONS
# ============================================================

st.markdown(
    "### ⚙️ Generation Options"
)


generation_mode = st.radio(

    "Generation Mode",

    [

        "Generate Selected Topic",

        "Generate Selected Module",

        "Generate All Lessons",

    ],

    horizontal=True,

    key="lesson_generation_mode",

)


# ============================================================
# 14. TOPIC SELECTOR
# ============================================================

topic_labels = []


topic_lookup = {}


for item in all_topics_for_lessons:

    module = item[
        "module"
    ]

    topic = item[
        "topic"
    ]


    label = (

        f"{module.get('module_id')} — "
        f"{module.get('module_name')} — "
        f"{topic.get('topic_id')} — "
        f"{topic.get('topic_name')}"

    )


    topic_labels.append(
        label
    )


    topic_lookup[
        label
    ] = item


selected_topic_label = None


if (

    generation_mode
    ==
    "Generate Selected Topic"

):

    selected_topic_label = st.selectbox(

        "Select Topic",

        topic_labels,

        key="selected_lesson_topic",

    )


# ============================================================
# 15. MODULE SELECTOR
# ============================================================

selected_module = None


if (

    generation_mode
    ==
    "Generate Selected Module"

):

    module_labels = [

        (
            f"{module.get('module_id')} — "
            f"{module.get('module_name')}"
        )

        for module in academic_modules

    ]


    selected_module_label = st.selectbox(

        "Select Module",

        module_labels,

        key="selected_lesson_module",

    )


    for module in academic_modules:

        label = (

            f"{module.get('module_id')} — "
            f"{module.get('module_name')}"
        )


        if label == selected_module_label:

            selected_module = module

            break


# ============================================================
# 16. GENERATE BUTTON
# ============================================================

generate_lessons = st.button(

    "🚀 Generate AI Lesson Plan",

    type="primary",

    use_container_width=True,

    disabled=(

        lesson_llm is None

        or

        not all_topics_for_lessons

    ),

)


# ============================================================
# 17. SESSION STATE
# ============================================================

if "lesson_plans" not in st.session_state:

    st.session_state[
        "lesson_plans"
    ] = {}


# ============================================================
# 18. GENERATE SELECTED TOPIC
# ============================================================

if (

    generate_lessons

    and

    generation_mode
    ==
    "Generate Selected Topic"

):

    selected_item = topic_lookup.get(

        selected_topic_label

    )


    if selected_item:

        module = selected_item[
            "module"
        ]

        topic = selected_item[
            "topic"
        ]


        with st.spinner(

            f"""
            Generating lesson plan for
            {topic.get('topic_name')}...
            """

        ):

            lesson_result = generate_lesson_plan(

                module,

                topic,

            )


        topic_id = topic.get(
            "topic_id"
        )


        st.session_state[
            "lesson_plans"
        ][topic_id] = lesson_result


# ============================================================
# 19. GENERATE MODULE
# ============================================================

if (

    generate_lessons

    and

    generation_mode
    ==
    "Generate Selected Module"

):

    if selected_module:

        module_topics = selected_module.get(

            "topics",

            []

        )


        progress = st.progress(
            0
        )


        generated_count = 0


        for topic in module_topics:

            with st.spinner(

                f"""
                Generating:
                {topic.get('topic_name')}
                """

            ):

                lesson_result = generate_lesson_plan(

                    selected_module,

                    topic,

                )


            topic_id = topic.get(
                "topic_id"
            )


            st.session_state[
                "lesson_plans"
            ][topic_id] = lesson_result


            generated_count += 1


            progress.progress(

                generated_count
                /
                max(
                    len(
                        module_topics
                    ),
                    1,
                )

            )


        st.success(

            f"""
            Generated
            {generated_count}
            lesson plans.
            """

        )


# ============================================================
# 20. GENERATE ALL
# ============================================================

if (

    generate_lessons

    and

    generation_mode
    ==
    "Generate All Lessons"

):

    progress = st.progress(
        0
    )


    total = len(
        all_topics_for_lessons
    )


    generated_count = 0


    for item in all_topics_for_lessons:

        module = item[
            "module"
        ]

        topic = item[
            "topic"
        ]


        with st.spinner(

            f"""
            Generating:
            {topic.get('topic_name')}
            """

        ):

            lesson_result = generate_lesson_plan(

                module,

                topic,

            )


        topic_id = topic.get(
            "topic_id"
        )


        st.session_state[
            "lesson_plans"
        ][topic_id] = lesson_result


        generated_count += 1


        progress.progress(

            generated_count
            /
            max(
                total,
                1,
            )

        )


    st.success(

        f"""
        🎉 Generated
        {generated_count}
        lesson plans.
        """

    )


# ============================================================
# 21. LOAD LESSON PLANS
# ============================================================

lesson_plans = st.session_state.get(

    "lesson_plans",

    {}

)


# ============================================================
# 22. GENERATION SUMMARY
# ============================================================

if lesson_plans:

    st.divider()

    st.subheader(
        "📊 Lesson Generation Summary"
    )


    successful = 0

    failed = 0


    for result in lesson_plans.values():

        if isinstance(
            result,
            dict,
        ) and not result.get(
            "error"
        ):

            successful += 1

        else:

            failed += 1


    summary_cols = st.columns(
        3
    )


    with summary_cols[0]:

        st.metric(
            "Generated",
            successful,
        )


    with summary_cols[1]:

        st.metric(
            "Failed",
            failed,
        )


    with summary_cols[2]:

        st.metric(
            "Total Topics",
            topic_count,
        )


# ============================================================
# 23. DISPLAY LESSON PLANS
# ============================================================

if lesson_plans:

    st.divider()

    st.subheader(
        "📚 Generated Lesson Plans"
    )


    for item in all_topics_for_lessons:

        module = item[
            "module"
        ]

        topic = item[
            "topic"
        ]


        topic_id = topic.get(
            "topic_id"
        )


        lesson = lesson_plans.get(
            topic_id
        )


        if not lesson:

            continue


        if lesson.get(
            "error"
        ):

            st.error(

                f"""
                {topic.get('topic_name')}:
                {lesson.get('error')}
                """

            )

            continue


        topic_name = safe_text(

            topic.get(
                "topic_name"
            ),

            "Topic",

        )


        with st.expander(

            f"""
            {topic_id} — {topic_name}
            """

        ):

            # ------------------------------------------------
            # Metadata
            # ------------------------------------------------

            metadata = lesson.get(

                "lesson_metadata",

                {}

            )


            meta_cols = st.columns(
                5
            )


            with meta_cols[0]:

                st.metric(

                    "Duration",

                    metadata.get(
                        "duration_minutes",
                        60,
                    ),

                )


            with meta_cols[1]:

                st.metric(

                    "Hours",

                    metadata.get(
                        "hours",
                        1,
                    ),

                )


            with meta_cols[2]:

                st.metric(

                    "Module",

                    metadata.get(
                        "module_id",
                        ""
                    ),

                )


            with meta_cols[3]:

                st.metric(

                    "CO",

                    ", ".join(

                        lesson.get(
                            "co_mapping",
                            []
                        )

                    ),

                )


            with meta_cols[4]:

                st.metric(

                    "PO",

                    ", ".join(

                        lesson.get(
                            "po_mapping",
                            []
                        )

                    ),

                )


            # ------------------------------------------------
            # Learning objectives
            # ------------------------------------------------

            st.markdown(
                "### 🎯 Learning Objectives"
            )


            for objective in normalize_list(

                lesson.get(
                    "learning_objectives"
                )

            ):

                st.markdown(
                    f"- {objective}"
                )


            # ------------------------------------------------
            # Prerequisites
            # ------------------------------------------------

            prerequisites = normalize_list(

                lesson.get(
                    "prerequisites"
                )

            )


            if prerequisites:

                st.markdown(
                    "### 🔗 Prerequisites"
                )


                for item in prerequisites:

                    st.markdown(
                        f"- {item}"
                    )


            # ------------------------------------------------
            # Pre-class
            # ------------------------------------------------

            pre_class = lesson.get(

                "pre_class",

                {}

            )


            st.markdown(
                "### 📖 Pre-Class Preparation"
            )


            st.write(

                "**Purpose:**",

                pre_class.get(
                    "purpose"
                ),

            )


            st.write(

                "**Estimated Preparation Time:**",

                pre_class.get(
                    "estimated_time_minutes",
                    15,
                ),

                "minutes",

            )


            reading = normalize_list(

                pre_class.get(
                    "reading_material"
                )

            )


            if reading:

                st.markdown(
                    "**Reading Material**"
                )


                for item in reading:

                    st.markdown(
                        f"- {item}"
                    )


            checklist = normalize_list(

                pre_class.get(
                    "preparation_checklist"
                )

            )


            if checklist:

                st.markdown(
                    "**Preparation Checklist**"
                )


                for item in checklist:

                    st.markdown(
                        f"- {item}"
                    )


            pre_mcqs = pre_class.get(

                "mcqs",

                []

            )


            if pre_mcqs:

                st.markdown(
                    "#### 📝 Pre-Class MCQs"
                )


                for index, mcq in enumerate(

                    pre_mcqs,

                    start=1,

                ):

                    if not isinstance(
                        mcq,
                        dict,
                    ):

                        continue


                    st.write(

                        f"**Q{index}.** "
                        +
                        safe_text(

                            mcq.get(
                                "question"
                            )

                        )

                    )


                    options = normalize_list(

                        mcq.get(
                            "options"
                        )

                    )


                    for option in options:

                        st.markdown(
                            f"- {option}"
                        )


            # ------------------------------------------------
            # One hour plan
            # ------------------------------------------------

            st.markdown(
                "### ⏱️ One-Hour Teaching Plan"
            )


            plan = lesson.get(

                "one_hour_plan",

                []

            )


            plan_rows = []


            for segment in plan:

                if not isinstance(
                    segment,
                    dict,
                ):

                    continue


                plan_rows.append({

                    "Time":
                        (
                            f"{segment.get('start_minute', 0)}"
                            f"-"
                            f"{segment.get('end_minute', 0)} min"
                        ),

                    "Duration":
                        segment.get(
                            "duration",
                            0,
                        ),

                    "Segment":
                        segment.get(
                            "segment"
                        ),

                    "Teacher":
                        segment.get(
                            "teacher_action"
                        ),

                    "Student":
                        segment.get(
                            "student_action"
                        ),

                    "Activity":
                        segment.get(
                            "activity"
                        ),

                })


            if plan_rows:

                st.dataframe(

                    pd.DataFrame(
                        plan_rows
                    ),

                    use_container_width=True,

                    hide_index=True,

                )


            # ------------------------------------------------
            # Concept explanation
            # ------------------------------------------------

            explanation = lesson.get(

                "concept_explanation",

                {}

            )


            st.markdown(
                "### 🧠 Concept Explanation"
            )


            core_concepts = normalize_list(

                explanation.get(
                    "core_concepts"
                )

            )


            for concept in core_concepts:

                st.markdown(
                    f"- {concept}"
                )


            st.write(

                "**Detailed Explanation:**",

                explanation.get(
                    "detailed_explanation"
                ),

            )


            st.write(

                "**Worked Example:**",

                explanation.get(
                    "worked_example"
                ),

            )


            st.write(

                "**Real-World Example:**",

                explanation.get(
                    "real_world_example"
                ),

            )


            st.write(

                "**Industry Example:**",

                explanation.get(
                    "industry_example"
                ),

            )


            # ------------------------------------------------
            # Faculty notes
            # ------------------------------------------------

            faculty_notes = lesson.get(

                "faculty_notes",

                {}

            )


            st.markdown(
                "### 👨‍🏫 Faculty Notes"
            )


            faculty_sections = [

                (
                    "Key Points",
                    faculty_notes.get(
                        "key_points"
                    ),
                ),

                (
                    "Emphasize",
                    faculty_notes.get(
                        "emphasize"
                    ),
                ),

                (
                    "Avoid Overexplaining",
                    faculty_notes.get(
                        "avoid_overexplaining"
                    ),
                ),

                (
                    "Common Misconceptions",
                    faculty_notes.get(
                        "common_misconceptions"
                    ),
                ),

                (
                    "Likely Student Questions",
                    faculty_notes.get(
                        "likely_student_questions"
                    ),
                ),

                (
                    "Questions to Ask Students",
                    faculty_notes.get(
                        "teacher_questions"
                    ),
                ),

            ]


            for title, values in faculty_sections:

                values = normalize_list(
                    values
                )


                if not values:

                    continue


                st.markdown(
                    f"**{title}**"
                )


                for value in values:

                    st.markdown(
                        f"- {value}"
                    )


            # ------------------------------------------------
            # Hands-on activity
            # ------------------------------------------------

            hands_on = lesson.get(

                "hands_on_activity",

                {}

            )


            if hands_on:

                st.markdown(
                    "### 💻 Hands-On Activity"
                )


                st.write(

                    "**Title:**",

                    hands_on.get(
                        "title"
                    ),

                )


                st.write(

                    "**Objective:**",

                    hands_on.get(
                        "objective"
                    ),

                )


                instructions = normalize_list(

                    hands_on.get(
                        "instructions"
                    )

                )


                if instructions:

                    st.markdown(
                        "**Instructions**"
                    )


                    for instruction in instructions:

                        st.markdown(
                            f"- {instruction}"
                        )


                st.write(

                    "**Expected Output:**",

                    hands_on.get(
                        "expected_output"
                    ),

                )


                activity_tools = normalize_list(

                    hands_on.get(
                        "tools_required"
                    )

                )


                if activity_tools:

                    st.write(

                        "**Tools:**",

                        ", ".join(
                            activity_tools
                        ),

                    )


            # ------------------------------------------------
            # Post class
            # ------------------------------------------------

            post_class = lesson.get(

                "post_class",

                {}

            )


            st.markdown(
                "### 📚 Post-Class"
            )


            st.write(

                "**Summary:**",

                post_class.get(
                    "summary"
                ),

            )


            study_material = normalize_list(

                post_class.get(
                    "study_material"
                )

            )


            if study_material:

                st.markdown(
                    "**Study Material**"
                )


                for item in study_material:

                    st.markdown(
                        f"- {item}"
                    )


            # ------------------------------------------------
            # Assignment
            # ------------------------------------------------

            assignment = post_class.get(

                "assignment",

                {}

            )


            if assignment:

                st.markdown(
                    "### 📝 Assignment"
                )


                st.write(

                    "**Title:**",

                    assignment.get(
                        "title"
                    ),

                )


                st.write(

                    "**Problem:**",

                    assignment.get(
                        "problem_statement"
                    ),

                )


                requirements = normalize_list(

                    assignment.get(
                        "requirements"
                    )

                )


                if requirements:

                    st.markdown(
                        "**Requirements**"
                    )


                    for item in requirements:

                        st.markdown(
                            f"- {item}"
                        )


                deliverables = normalize_list(

                    assignment.get(
                        "deliverables"
                    )

                )


                if deliverables:

                    st.markdown(
                        "**Deliverables**"
                    )


                    for item in deliverables:

                        st.markdown(
                            f"- {item}"
                        )


                st.write(

                    "**Difficulty:**",

                    assignment.get(
                        "difficulty"
                    ),

                )


                st.write(

                    "**Estimated Hours:**",

                    assignment.get(
                        "estimated_hours"
                    ),

                )


            # ------------------------------------------------
            # Post-class MCQs
            # ------------------------------------------------

            post_mcqs = post_class.get(

                "mcqs",

                []

            )


            if post_mcqs:

                st.markdown(
                    "### 🧠 Practice MCQs"
                )


                for index, mcq in enumerate(

                    post_mcqs,

                    start=1,

                ):

                    if not isinstance(
                        mcq,
                        dict,
                    ):

                        continue


                    st.write(

                        f"**Q{index}.** "
                        +
                        safe_text(

                            mcq.get(
                                "question"
                            )

                        )

                    )


                    options = normalize_list(

                        mcq.get(
                            "options"
                        )

                    )


                    for option in options:

                        st.markdown(
                            f"- {option}"
                        )


                    st.caption(

                        "Answer: "
                        +
                        safe_text(

                            mcq.get(
                                "answer"
                            )

                        )

                    )


            # ------------------------------------------------
            # Reflection
            # ------------------------------------------------

            reflection = normalize_list(

                post_class.get(
                    "reflection_questions"
                )

            )


            if reflection:

                st.markdown(
                    "### 🤔 Reflection Questions"
                )


                for question in reflection:

                    st.markdown(
                        f"- {question}"
                    )


            # ------------------------------------------------
            # Assessment
            # ------------------------------------------------

            assessment = lesson.get(

                "assessment",

                {}

            )


            st.markdown(
                "### 📊 Assessment"
            )


            st.write(

                "**Method:**",

                assessment.get(
                    "method"
                ),

            )


            st.write(

                "**Bloom Level:**",

                assessment.get(
                    "bloom_level"
                ),

            )


            assessment_questions = normalize_list(

                assessment.get(
                    "questions"
                )

            )


            if assessment_questions:

                for question in assessment_questions:

                    st.markdown(
                        f"- {question}"
                    )


            rubric = normalize_list(

                assessment.get(
                    "rubric"
                )

            )


            if rubric:

                st.markdown(
                    "**Rubric**"
                )


                for item in rubric:

                    st.markdown(
                        f"- {item}"
                    )


            # ------------------------------------------------
            # Teacher focus
            # ------------------------------------------------

            teacher_focus = lesson.get(

                "teacher_focus",

                {}

            )


            st.markdown(
                "### 🎯 Teacher Focus"
            )


            st.write(

                "**Priority:**",

                teacher_focus.get(
                    "priority"
                ),

            )


            st.write(

                "**Student Risk:**",

                teacher_focus.get(
                    "student_risk"
                ),

            )


            st.write(

                "**Intervention:**",

                teacher_focus.get(
                    "intervention"
                ),

            )


            st.write(

                "**Next Class Preparation:**",

                teacher_focus.get(
                    "next_class_preparation"
                ),

            )


# ============================================================
# 24. BUILD TEACHING CONTENT COLLECTION
# ============================================================

teaching_content = []


pre_class_content = []


in_class_content = []


post_class_content = []


for item in all_topics_for_lessons:

    module = item[
        "module"
    ]

    topic = item[
        "topic"
    ]


    topic_id = topic.get(
        "topic_id"
    )


    lesson = lesson_plans.get(
        topic_id
    )


    if not isinstance(
        lesson,
        dict,
    ):

        continue


    if lesson.get(
        "error"
    ):

        continue


    teaching_content.append({

        "module_id":
            module.get(
                "module_id"
            ),

        "module_name":
            module.get(
                "module_name"
            ),

        "topic_id":
            topic_id,

        "topic_name":
            topic.get(
                "topic_name"
            ),

        "lesson":
            lesson,

    })


    pre_class_content.append({

        "topic_id":
            topic_id,

        "topic_name":
            topic.get(
                "topic_name"
            ),

        "pre_class":
            lesson.get(
                "pre_class",
                {}
            ),

    })


    in_class_content.append({

        "topic_id":
            topic_id,

        "topic_name":
            topic.get(
                "topic_name"
            ),

        "one_hour_plan":
            lesson.get(
                "one_hour_plan",
                []
            ),

        "concept_explanation":
            lesson.get(
                "concept_explanation",
                {}
            ),

        "faculty_notes":
            lesson.get(
                "faculty_notes",
                {}
            ),

        "hands_on_activity":
            lesson.get(
                "hands_on_activity",
                {}
            ),

    })


    post_class_content.append({

        "topic_id":
            topic_id,

        "topic_name":
            topic.get(
                "topic_name"
            ),

        "post_class":
            lesson.get(
                "post_class",
                {}
            ),

        "assessment":
            lesson.get(
                "assessment",
                {}
            ),

    })


# ============================================================
# 25. SAVE CONTENT
# ============================================================

st.session_state[
    "teaching_content"
] = teaching_content


st.session_state[
    "pre_class_content"
] = pre_class_content


st.session_state[
    "in_class_content"
] = in_class_content


st.session_state[
    "post_class_content"
] = post_class_content


# ============================================================
# 26. LESSON PLAN COMPLETION
# ============================================================

successful_lessons = sum(

    1

    for lesson in lesson_plans.values()

    if isinstance(
        lesson,
        dict,
    )

    and

    not lesson.get(
        "error"
    )

)


st.session_state[
    "lesson_plan_complete"
] = (

    successful_lessons
    ==
    topic_count

    and

    topic_count
    >
    0

)


# ============================================================
# 27. DOWNLOAD COMPLETE LESSON PLANS
# ============================================================

if teaching_content:

    st.divider()

    st.download_button(

        "⬇️ Download All Lesson Plans JSON",

        data=serialize_json(

            teaching_content

        ),

        file_name=(
            "all_lesson_plans.json"
        ),

        mime="application/json",

        key="download_all_lesson_plans",

    )


# ============================================================
# 28. DOWNLOAD PRE-CLASS CONTENT
# ============================================================

if pre_class_content:

    st.download_button(

        "⬇️ Download Pre-Class Content",

        data=serialize_json(

            pre_class_content

        ),

        file_name=(
            "pre_class_learning_content.json"
        ),

        mime="application/json",

        key="download_pre_class_content",

    )


# ============================================================
# 29. DOWNLOAD IN-CLASS CONTENT
# ============================================================

if in_class_content:

    st.download_button(

        "⬇️ Download Faculty Teaching Content",

        data=serialize_json(

            in_class_content

        ),

        file_name=(
            "faculty_teaching_content.json"
        ),

        mime="application/json",

        key="download_in_class_content",

    )


# ============================================================
# 30. DOWNLOAD POST-CLASS CONTENT
# ============================================================

if post_class_content:

    st.download_button(

        "⬇️ Download Post-Class Content",

        data=serialize_json(

            post_class_content

        ),

        file_name=(
            "post_class_learning_content.json"
        ),

        mime="application/json",

        key="download_post_class_content",

    )


# ============================================================
# 31. COMPLETION STATUS
# ============================================================

if st.session_state.get(

    "lesson_plan_complete",

    False,

):

    st.success(
        """
        🎉 **AI Lesson Plan Generation Complete**

        Every syllabus topic now has:

        ✓ Pre-class preparation
        ✓ Pre-class MCQs
        ✓ Learning objectives
        ✓ One-hour teaching plan
        ✓ Concept explanation
        ✓ Worked examples
        ✓ Industry examples
        ✓ Faculty notes
        ✓ Classroom activity
        ✓ Hands-on exercise
        ✓ Post-class study material
        ✓ Assignment
        ✓ Practice MCQs
        ✓ Assessment
        ✓ Teacher intervention guidance

        The next layer can use these teaching artifacts to
        create student-level adaptive learning and
        performance intelligence.
        """
    )


# ============================================================
# END OF CHUNK 9/10
# ============================================================
# ============================================================
# 04_🔍_Gap_Enhancement.py
# CHUNK 10/10
#
# FINAL VALIDATION
# INDUSTRY COVERAGE
# CURRICULUM ENHANCEMENT SUMMARY
# EXPORT PACKAGE
# REPORT HANDOFF
# ============================================================

"""
FINAL PURPOSE
-------------

This is the final stage of:

04_🔍_Gap_Enhancement.py

It validates and packages all intelligence generated by
the Curriculum / Industry / JD / Agentic pipeline.

Pipeline:

    Original Syllabus
            ↓
    Curriculum Intelligence
            ↓
    Industry / JD Intelligence
            ↓
    Gap Analysis
            ↓
    Enhancement Blueprint
            ↓
    Expert Agent
            ↓
    Critic Agent
            ↓
    Final Enhancement Agent
            ↓
    CO / PO / PSO
            ↓
    Academic Syllabus
            ↓
    Lesson Plans
            ↓
    FINAL VALIDATION
            ↓
    REPORT HANDOFF

The output is consumed by:

    05_📊_Reports.py


Important Session State
-----------------------

final_curriculum
academic_syllabus
lesson_plans
teaching_content
pre_class_content
in_class_content
post_class_content

final_enhancement_package

report_handoff


============================================================
"""


# ============================================================
# 1. LOAD ALL PIPELINE DATA
# ============================================================

final_curriculum = st.session_state.get(
    "final_curriculum",
    {}
)


academic_syllabus = st.session_state.get(
    "academic_syllabus",
    {}
)


lesson_plans = st.session_state.get(
    "lesson_plans",
    {}
)


teaching_content = st.session_state.get(
    "teaching_content",
    []
)


pre_class_content = st.session_state.get(
    "pre_class_content",
    []
)


in_class_content = st.session_state.get(
    "in_class_content",
    []
)


post_class_content = st.session_state.get(
    "post_class_content",
    []
)


curriculum_skill_intelligence = st.session_state.get(
    "curriculum_skill_intelligence",
    {}
)


jd_skill_intelligence = st.session_state.get(
    "jd_skill_intelligence",
    {}
)


industry_gap_analysis = st.session_state.get(
    "industry_gap_analysis",
    {}
)


prioritized_gaps = st.session_state.get(
    "prioritized_gaps",
    []
)


module_gap_mapping = st.session_state.get(
    "module_gap_mapping",
    []
)


enhancement_blueprint = st.session_state.get(
    "enhancement_blueprint",
    []
)


expert_enhancement_analysis = st.session_state.get(
    "expert_enhancement_analysis",
    {}
)


critic_enhancement_analysis = st.session_state.get(
    "critic_enhancement_analysis",
    {}
)


expert_recommendations = st.session_state.get(
    "expert_recommendations",
    []
)


critic_recommendations = st.session_state.get(
    "critic_recommendations",
    []
)


remaining_industry_gaps = st.session_state.get(
    "remaining_industry_gaps",
    []
)


final_recommendations = st.session_state.get(
    "final_recommendations",
    []
)


final_projects = st.session_state.get(
    "final_projects",
    []
)


final_tools = st.session_state.get(
    "final_tools",
    []
)


final_technologies = st.session_state.get(
    "final_technologies",
    []
)


industry_skills_covered = st.session_state.get(
    "industry_skills_covered",
    []
)


# ============================================================
# 2. EXTRACT ACADEMIC STRUCTURE
# ============================================================

academic_modules = academic_syllabus.get(
    "modules",
    []
)


course_outcomes = academic_syllabus.get(
    "course_outcomes",
    []
)


program_outcomes = academic_syllabus.get(
    "program_outcomes",
    []
)


program_specific_outcomes = academic_syllabus.get(
    "program_specific_outcomes",
    []
)


co_po_matrix = academic_syllabus.get(
    "co_po_matrix",
    []
)


co_pso_matrix = academic_syllabus.get(
    "co_pso_matrix",
    []
)


course_information = academic_syllabus.get(
    "course_information",
    {}
)


# ============================================================
# 3. BASIC COUNTERS
# ============================================================

module_count = len(
    academic_modules
)


topic_count = sum(

    len(
        module.get(
            "topics",
            []
        )
    )

    for module in academic_modules

    if isinstance(
        module,
        dict,
    )

)


total_hours = safe_number(

    course_information.get(
        "total_hours",
        0,
    )

)


project_count = len(
    final_projects
)


lesson_count = len(
    lesson_plans
)


successful_lesson_count = sum(

    1

    for result in lesson_plans.values()

    if isinstance(
        result,
        dict,
    )

    and not result.get(
        "error"
    )

)


failed_lesson_count = (

    lesson_count
    -
    successful_lesson_count

)


# ============================================================
# 4. FINAL CURRICULUM CHANGE COUNTS
# ============================================================

added_topics = normalize_list(

    final_curriculum.get(
        "added_topics",
        []
    )

)


enhanced_topics = normalize_list(

    final_curriculum.get(
        "enhanced_topics",
        []
    )

)


merged_topics = normalize_list(

    final_curriculum.get(
        "merged_topics",
        []
    )

)


reduced_topics = normalize_list(

    final_curriculum.get(
        "reduced_topics",
        []
    )

)


removed_topics = normalize_list(

    final_curriculum.get(
        "removed_topics",
        []
    )

)


reordered_topics = normalize_list(

    final_curriculum.get(
        "reordered_topics",
        []
    )

)


# ============================================================
# 5. EXTRACT ORIGINAL / INDUSTRY SKILLS
# ============================================================

def extract_skill_list(
    data,
    possible_keys,
):
    """
    Extract skills from different possible structures.
    """

    if not isinstance(
        data,
        dict,
    ):

        return []


    result = []


    for key in possible_keys:

        value = data.get(
            key
        )


        if isinstance(
            value,
            list,
        ):

            result.extend(
                value
            )


        elif isinstance(
            value,
            dict,
        ):

            for nested_value in value.values():

                if isinstance(
                    nested_value,
                    list,
                ):

                    result.extend(
                        nested_value
                    )


    return unique_values(

        [
            safe_text(
                item
            )

            for item in result

            if safe_text(
                item
            )

        ]

    )


# ============================================================
# 6. CURRICULUM SKILLS
# ============================================================

curriculum_skills = extract_skill_list(

    curriculum_skill_intelligence,

    [

        "skills",

        "curriculum_skills",

        "covered_skills",

        "technical_skills",

        "concepts",

    ],

)


# ============================================================
# 7. JD SKILLS
# ============================================================

jd_skills = extract_skill_list(

    jd_skill_intelligence,

    [

        "skills",

        "jd_skills",

        "required_skills",

        "technical_skills",

        "key_skills",

        "skills_required",

        "missing_skills",

    ],

)


# ============================================================
# 8. NORMALIZE SKILLS
# ============================================================

def normalize_skill(
    skill,
):
    """
    Normalize skill names for comparison.
    """

    text = safe_text(
        skill
    ).lower().strip()


    replacements = {

        "machine learning":
            "machine learning",

        "ml":
            "machine learning",

        "artificial intelligence":
            "artificial intelligence",

        "ai":
            "artificial intelligence",

        "deep learning":
            "deep learning",

        "dl":
            "deep learning",

        "large language model":
            "llm",

        "large language models":
            "llm",

        "generative ai":
            "generative ai",

        "gen ai":
            "generative ai",

        "natural language processing":
            "nlp",

    }


    return replacements.get(
        text,
        text,
    )


# ============================================================
# 9. NORMALIZED SKILL SETS
# ============================================================

curriculum_skill_map = {

    normalize_skill(
        skill
    ):
        skill

    for skill in curriculum_skills

}


jd_skill_map = {

    normalize_skill(
        skill
    ):
        skill

    for skill in jd_skills

}


covered_skill_keys = sorted(

    set(
        curriculum_skill_map.keys()
    )
    &
    set(
        jd_skill_map.keys()
    )

)


missing_skill_keys = sorted(

    set(
        jd_skill_map.keys()
    )
    -
    set(
        curriculum_skill_map.keys()
    )

)


extra_curriculum_skill_keys = sorted(

    set(
        curriculum_skill_map.keys()
    )
    -
    set(
        jd_skill_map.keys()
    )

)


# ============================================================
# 10. SKILL COVERAGE SCORE
# ============================================================

if jd_skill_map:

    skill_coverage_percentage = round(

        (
            len(
                covered_skill_keys
            )
            /
            len(
                jd_skill_map
            )
        )
        *
        100,

        2,

    )

else:

    skill_coverage_percentage = 0.0


# ============================================================
# 11. TOPIC COVERAGE
# ============================================================

topics_with_industry_skill = 0


topics_with_tools = 0


topics_with_assessment = 0


topics_with_practical = 0


topics_with_co = 0


topics_with_po = 0


for module in academic_modules:

    if not isinstance(
        module,
        dict,
    ):

        continue


    for topic in module.get(
        "topics",
        []
    ):

        if not isinstance(
            topic,
            dict,
        ):

            continue


        topic_industry_text = " ".join(

            [

                safe_text(
                    module.get(
                        "industry_skills"
                    )
                ),

                safe_text(
                    topic.get(
                        "concepts"
                    )
                ),

                safe_text(
                    topic.get(
                        "technologies"
                    )
                ),

            ]

        ).strip()


        if topic_industry_text:

            topics_with_industry_skill += 1


        if topic.get(
            "tools"
        ) or topic.get(
            "technologies"
        ):

            topics_with_tools += 1


        if topic.get(
            "assessment_methods"
        ):

            topics_with_assessment += 1


        if topic.get(
            "lab_required"
        ):

            topics_with_practical += 1


        if topic.get(
            "co_mapping"
        ):

            topics_with_co += 1


        if topic.get(
            "po_mapping"
        ):

            topics_with_po += 1


# ============================================================
# 12. TOPIC COVERAGE PERCENTAGES
# ============================================================

def percentage(
    numerator,
    denominator,
):
    """
    Safe percentage calculation.
    """

    if not denominator:

        return 0.0


    return round(

        (
            numerator
            /
            denominator
        )
        *
        100,

        2,

    )


topic_industry_percentage = percentage(

    topics_with_industry_skill,

    topic_count,

)


topic_tool_percentage = percentage(

    topics_with_tools,

    topic_count,

)


topic_assessment_percentage = percentage(

    topics_with_assessment,

    topic_count,

)


topic_practical_percentage = percentage(

    topics_with_practical,

    topic_count,

)


topic_co_percentage = percentage(

    topics_with_co,

    topic_count,

)


topic_po_percentage = percentage(

    topics_with_po,

    topic_count,

)


# ============================================================
# 13. LESSON PLAN COVERAGE
# ============================================================

lesson_plan_coverage = percentage(

    successful_lesson_count,

    topic_count,

)


# ============================================================
# 14. PRE-CLASS COVERAGE
# ============================================================

topics_with_pre_class = sum(

    1

    for item in pre_class_content

    if isinstance(
        item,
        dict,
    )

    and item.get(
        "pre_class"
    )

)


pre_class_coverage = percentage(

    topics_with_pre_class,

    topic_count,

)


# ============================================================
# 15. IN-CLASS COVERAGE
# ============================================================

topics_with_in_class = sum(

    1

    for item in in_class_content

    if isinstance(
        item,
        dict,
    )

    and (

        item.get(
            "one_hour_plan"
        )

        or

        item.get(
            "concept_explanation"
        )

    )

)


in_class_coverage = percentage(

    topics_with_in_class,

    topic_count,

)


# ============================================================
# 16. POST-CLASS COVERAGE
# ============================================================

topics_with_post_class = sum(

    1

    for item in post_class_content

    if isinstance(
        item,
        dict,
    )

    and item.get(
        "post_class"
    )

)


post_class_coverage = percentage(

    topics_with_post_class,

    topic_count,

)


# ============================================================
# 17. MCQ COVERAGE
# ============================================================

topics_with_mcqs = 0


total_mcqs = 0


for lesson in lesson_plans.values():

    if not isinstance(
        lesson,
        dict,
    ):

        continue


    pre_mcqs = (

        lesson.get(
            "pre_class",
            {}
        )
        .get(
            "mcqs",
            []
        )

    )


    post_mcqs = (

        lesson.get(
            "post_class",
            {}
        )
        .get(
            "mcqs",
            []
        )

    )


    current_mcq_count = (

        len(
            pre_mcqs
        )
        +
        len(
            post_mcqs
        )

    )


    if current_mcq_count > 0:

        topics_with_mcqs += 1


    total_mcqs += current_mcq_count


mcq_coverage = percentage(

    topics_with_mcqs,

    topic_count,

)


# ============================================================
# 18. ASSIGNMENT COVERAGE
# ============================================================

topics_with_assignment = 0


for lesson in lesson_plans.values():

    if not isinstance(
        lesson,
        dict,
    ):

        continue


    assignment = (

        lesson.get(
            "post_class",
            {}
        )
        .get(
            "assignment"
        )

    )


    if isinstance(
        assignment,
        dict,
    ) and assignment:

        topics_with_assignment += 1


assignment_coverage = percentage(

    topics_with_assignment,

    topic_count,

)


# ============================================================
# 19. FINAL ENHANCEMENT SCORE
# ============================================================

enhancement_components = [

    skill_coverage_percentage,

    topic_industry_percentage,

    topic_tool_percentage,

    topic_assessment_percentage,

    topic_practical_percentage,

    lesson_plan_coverage,

    assignment_coverage,

    mcq_coverage,

]


enhancement_score = round(

    sum(
        enhancement_components
    )
    /
    max(
        len(
            enhancement_components
        ),
        1,
    ),

    2,

)


# ============================================================
# 20. CURRICULUM READINESS SCORE
# ============================================================

readiness_components = [

    topic_co_percentage,

    topic_po_percentage,

    lesson_plan_coverage,

    assignment_coverage,

    mcq_coverage,

    topic_practical_percentage,

    skill_coverage_percentage,

]


curriculum_readiness_score = round(

    sum(
        readiness_components
    )
    /
    max(
        len(
            readiness_components
        ),
        1,
    ),

    2,

)


# ============================================================
# 21. IDENTIFY FINAL REMAINING GAPS
# ============================================================

final_remaining_gaps = []


# JD skills not covered
for skill_key in missing_skill_keys:

    final_remaining_gaps.append({

        "type":
            "Industry Skill",

        "gap":
            jd_skill_map.get(
                skill_key,
                skill_key,
            ),

        "priority":
            "High",

        "recommendation":
            (
                "Consider adding the skill to the relevant "
                "module or creating a practical project."
            ),

    })


# Existing remaining gaps
for gap in remaining_industry_gaps:

    if isinstance(
        gap,
        dict,
    ):

        final_remaining_gaps.append(
            gap
        )

    else:

        final_remaining_gaps.append({

            "type":
                "Industry / Curriculum",

            "gap":
                safe_text(
                    gap
                ),

            "priority":
                "Medium",

            "recommendation":
                (
                    "Review during the next curriculum "
                    "revision cycle."
                ),

        })


# ============================================================
# 22. REMOVE DUPLICATE GAPS
# ============================================================

unique_gap_keys = set()


deduplicated_gaps = []


for gap in final_remaining_gaps:

    if not isinstance(
        gap,
        dict,
    ):

        continue


    gap_text = safe_text(

        gap.get(
            "gap"
        ),

        safe_text(
            gap
        ),

    )


    gap_key = gap_text.lower().strip()


    if not gap_key:

        continue


    if gap_key in unique_gap_keys:

        continue


    unique_gap_keys.add(
        gap_key
    )


    deduplicated_gaps.append(
        gap
    )


final_remaining_gaps = deduplicated_gaps


# ============================================================
# 23. GAP SEVERITY
# ============================================================

high_gaps = [

    gap

    for gap in final_remaining_gaps

    if safe_text(
        gap.get(
            "priority"
        )
    ).lower()
    ==
    "high"

]


medium_gaps = [

    gap

    for gap in final_remaining_gaps

    if safe_text(
        gap.get(
            "priority"
        )
    ).lower()
    ==
    "medium"

]


low_gaps = [

    gap

    for gap in final_remaining_gaps

    if safe_text(
        gap.get(
            "priority"
        )
    ).lower()
    ==
    "low"

]


# ============================================================
# 24. FINAL STATUS
# ============================================================

if curriculum_readiness_score >= 85:

    curriculum_status = (
        "Industry-ready / highly mature"
    )

elif curriculum_readiness_score >= 70:

    curriculum_status = (
        "Strong curriculum with minor improvements"
    )

elif curriculum_readiness_score >= 50:

    curriculum_status = (
        "Moderately aligned; enhancement required"
    )

else:

    curriculum_status = (
        "Significant curriculum enhancement required"
    )


# ============================================================
# 25. AUTOMATIC RECOMMENDATIONS
# ============================================================

automatic_recommendations = []


if skill_coverage_percentage < 70:

    automatic_recommendations.append(

        "Increase direct coverage of high-priority "
        "industry/JD skills."

    )


if topic_practical_percentage < 60:

    automatic_recommendations.append(

        "Increase hands-on laboratory and implementation "
        "activities."

    )


if assignment_coverage < 80:

    automatic_recommendations.append(

        "Ensure every major topic has a meaningful "
        "post-class assignment."

    )


if mcq_coverage < 80:

    automatic_recommendations.append(

        "Add formative MCQ assessment to more topics."

    )


if topic_co_percentage < 90:

    automatic_recommendations.append(

        "Review CO mapping for all topics."

    )


if topic_po_percentage < 90:

    automatic_recommendations.append(

        "Review PO mapping and ensure outcome alignment."

    )


if lesson_plan_coverage < 90:

    automatic_recommendations.append(

        "Complete AI-generated lesson plans for remaining "
        "topics."

    )


if project_count == 0:

    automatic_recommendations.append(

        "Add at least one industry-oriented capstone project."

    )


if not automatic_recommendations:

    automatic_recommendations.append(

        "Curriculum is structurally strong; continue "
        "periodic industry/JD review."

    )


# ============================================================
# 26. COMBINE AI + AUTOMATIC RECOMMENDATIONS
# ============================================================

all_recommendations = unique_values(

    [

        *final_recommendations,

        *automatic_recommendations,

    ]

)


# ============================================================
# 27. BUILD INDUSTRY COVERAGE REPORT
# ============================================================

industry_coverage_report = {

    "jd_skill_count":
        len(
            jd_skill_map
        ),

    "curriculum_skill_count":
        len(
            curriculum_skill_map
        ),

    "covered_skill_count":
        len(
            covered_skill_keys
        ),

    "missing_skill_count":
        len(
            missing_skill_keys
        ),

    "coverage_percentage":
        skill_coverage_percentage,

    "covered_skills":
        [

            jd_skill_map.get(
                key,
                key,
            )

            for key in covered_skill_keys

        ],

    "missing_skills":
        [

            jd_skill_map.get(
                key,
                key,
            )

            for key in missing_skill_keys

        ],

    "additional_curriculum_skills":
        [

            curriculum_skill_map.get(
                key,
                key,
            )

            for key in extra_curriculum_skill_keys

        ],

}


# ============================================================
# 28. BUILD LEARNING DELIVERY REPORT
# ============================================================

learning_delivery_report = {

    "topic_count":
        topic_count,

    "lesson_plan_count":
        successful_lesson_count,

    "lesson_plan_coverage":
        lesson_plan_coverage,

    "pre_class_coverage":
        pre_class_coverage,

    "in_class_coverage":
        in_class_coverage,

    "post_class_coverage":
        post_class_coverage,

    "mcq_coverage":
        mcq_coverage,

    "total_mcqs":
        total_mcqs,

    "assignment_coverage":
        assignment_coverage,

    "topics_with_practical":
        topics_with_practical,

    "practical_coverage":
        topic_practical_percentage,

}


# ============================================================
# 29. BUILD ACADEMIC ALIGNMENT REPORT
# ============================================================

academic_alignment_report = {

    "course_outcomes":
        len(
            course_outcomes
        ),

    "program_outcomes":
        len(
            program_outcomes
        ),

    "program_specific_outcomes":
        len(
            program_specific_outcomes
        ),

    "co_mapping_coverage":
        topic_co_percentage,

    "po_mapping_coverage":
        topic_po_percentage,

    "co_po_matrix_rows":
        len(
            co_po_matrix
        ),

    "co_pso_matrix_rows":
        len(
            co_pso_matrix
        ),

    "theory_hours":
        course_information.get(
            "theory_hours",
            0,
        ),

    "practical_hours":
        course_information.get(
            "practical_hours",
            0,
        ),

}


# ============================================================
# 30. BUILD ENHANCEMENT SUMMARY
# ============================================================

enhancement_summary = {

    "added_topics":
        len(
            added_topics
        ),

    "enhanced_topics":
        len(
            enhanced_topics
        ),

    "merged_topics":
        len(
            merged_topics
        ),

    "reduced_topics":
        len(
            reduced_topics
        ),

    "removed_topics":
        len(
            removed_topics
        ),

    "reordered_topics":
        len(
            reordered_topics
        ),

    "new_tools":
        len(
            final_tools
        ),

    "new_technologies":
        len(
            final_technologies
        ),

    "industry_projects":
        project_count,

    "industry_skills":
        len(
            industry_skills_covered
        ),

    "remaining_gaps":
        len(
            final_remaining_gaps
        ),

}


# ============================================================
# 31. BUILD FINAL VALIDATION
# ============================================================

final_validation = {

    "status":
        curriculum_status,

    "enhancement_score":
        enhancement_score,

    "curriculum_readiness_score":
        curriculum_readiness_score,

    "industry_skill_coverage":
        skill_coverage_percentage,

    "lesson_plan_coverage":
        lesson_plan_coverage,

    "assignment_coverage":
        assignment_coverage,

    "mcq_coverage":
        mcq_coverage,

    "co_coverage":
        topic_co_percentage,

    "po_coverage":
        topic_po_percentage,

    "practical_coverage":
        topic_practical_percentage,

    "high_priority_gaps":
        len(
            high_gaps
        ),

    "medium_priority_gaps":
        len(
            medium_gaps
        ),

    "low_priority_gaps":
        len(
            low_gaps
        ),

    "successful_lessons":
        successful_lesson_count,

    "failed_lessons":
        failed_lesson_count,

}


# ============================================================
# 32. BUILD FINAL ENHANCEMENT PACKAGE
# ============================================================

final_enhancement_package = {

    "package_version":
        "1.0",

    "generated_at":
        datetime.now().isoformat(),

    "course_information":
        course_information,

    "original_curriculum":
        curriculum_skill_intelligence,

    "curriculum_intelligence":
        curriculum_skill_intelligence,

    "industry_jd_intelligence":
        jd_skill_intelligence,

    "gap_analysis":
        industry_gap_analysis,

    "prioritized_gaps":
        prioritized_gaps,

    "module_gap_mapping":
        module_gap_mapping,

    "enhancement_blueprint":
        enhancement_blueprint,

    "expert_analysis":
        expert_enhancement_analysis,

    "expert_recommendations":
        expert_recommendations,

    "critic_analysis":
        critic_enhancement_analysis,

    "critic_recommendations":
        critic_recommendations,

    "final_curriculum":
        final_curriculum,

    "academic_syllabus":
        academic_syllabus,

    "industry_coverage":
        industry_coverage_report,

    "academic_alignment":
        academic_alignment_report,

    "learning_delivery":
        learning_delivery_report,

    "enhancement_summary":
        enhancement_summary,

    "validation":
        final_validation,

    "remaining_gaps":
        final_remaining_gaps,

    "recommendations":
        all_recommendations,

    "lesson_plans":
        lesson_plans,

    "teaching_content":
        teaching_content,

    "pre_class_content":
        pre_class_content,

    "in_class_content":
        in_class_content,

    "post_class_content":
        post_class_content,

    "projects":
        final_projects,

    "tools":
        final_tools,

    "technologies":
        final_technologies,

}


# ============================================================
# 33. SAVE FINAL PACKAGE
# ============================================================

st.session_state[
    "final_enhancement_package"
] = final_enhancement_package


# ============================================================
# 34. REPORT HANDOFF OBJECT
# ============================================================

"""
05_📊_Reports.py should consume this object.

Keeping one consolidated handoff object prevents the Reports
page from having to reconstruct data from multiple agents.
"""

report_handoff = {

    "course":
        course_information,

    "final_curriculum":
        final_curriculum,

    "academic_syllabus":
        academic_syllabus,

    "industry_coverage":
        industry_coverage_report,

    "academic_alignment":
        academic_alignment_report,

    "learning_delivery":
        learning_delivery_report,

    "enhancement_summary":
        enhancement_summary,

    "validation":
        final_validation,

    "remaining_gaps":
        final_remaining_gaps,

    "recommendations":
        all_recommendations,

    "lesson_plans":
        lesson_plans,

    "projects":
        final_projects,

}


st.session_state[
    "report_handoff"
] = report_handoff


# ============================================================
# 35. FINAL DASHBOARD
# ============================================================

st.divider()

st.subheader(
    "🏆 Curriculum Intelligence Final Dashboard"
)


dashboard_cols = st.columns(
    6
)


with dashboard_cols[0]:

    st.metric(

        "Industry Coverage",

        f"{skill_coverage_percentage}%",

    )


with dashboard_cols[1]:

    st.metric(

        "CO Coverage",

        f"{topic_co_percentage}%",

    )


with dashboard_cols[2]:

    st.metric(

        "PO Coverage",

        f"{topic_po_percentage}%",

    )


with dashboard_cols[3]:

    st.metric(

        "Lesson Coverage",

        f"{lesson_plan_coverage}%",

    )


with dashboard_cols[4]:

    st.metric(

        "Assignment Coverage",

        f"{assignment_coverage}%",

    )


with dashboard_cols[5]:

    st.metric(

        "Readiness",

        f"{curriculum_readiness_score}%",

    )


# ============================================================
# 36. INDUSTRY COVERAGE DISPLAY
# ============================================================

st.markdown(
    "### 💼 Industry / JD Coverage"
)


industry_cols = st.columns(
    4
)


with industry_cols[0]:

    st.metric(

        "JD Skills",

        len(
            jd_skill_map
        ),

    )


with industry_cols[1]:

    st.metric(

        "Covered",

        len(
            covered_skill_keys
        ),

    )


with industry_cols[2]:

    st.metric(

        "Missing",

        len(
            missing_skill_keys
        ),

    )


with industry_cols[3]:

    st.metric(

        "Coverage",

        f"{skill_coverage_percentage}%",

    )


# ============================================================
# 37. COVERED SKILLS
# ============================================================

if covered_skill_keys:

    with st.expander(
        "✅ Covered Industry Skills"
    ):

        for key in covered_skill_keys:

            st.markdown(

                f"- {jd_skill_map.get(key, key)}"

            )


# ============================================================
# 38. MISSING SKILLS
# ============================================================

if missing_skill_keys:

    with st.expander(
        "⚠️ Missing Industry Skills"
    ):

        for key in missing_skill_keys:

            st.warning(

                jd_skill_map.get(
                    key,
                    key,
                )

            )


# ============================================================
# 39. ENHANCEMENT STATISTICS
# ============================================================

st.markdown(
    "### 🔧 Enhancement Statistics"
)


enhancement_cols = st.columns(
    6
)


with enhancement_cols[0]:

    st.metric(
        "Added",
        len(
            added_topics
        ),
    )


with enhancement_cols[1]:

    st.metric(
        "Enhanced",
        len(
            enhanced_topics
        ),
    )


with enhancement_cols[2]:

    st.metric(
        "Merged",
        len(
            merged_topics
        ),
    )


with enhancement_cols[3]:

    st.metric(
        "Reduced",
        len(
            reduced_topics
        ),
    )


with enhancement_cols[4]:

    st.metric(
        "Removed",
        len(
            removed_topics
        ),
    )


with enhancement_cols[5]:

    st.metric(
        "Projects",
        project_count,
    )


# ============================================================
# 40. LEARNING DELIVERY STATISTICS
# ============================================================

st.markdown(
    "### 👨‍🏫 Teaching & Learning Readiness"
)


learning_cols = st.columns(
    5
)


with learning_cols[0]:

    st.metric(

        "Lessons",

        successful_lesson_count,

    )


with learning_cols[1]:

    st.metric(

        "Pre-Class",

        f"{pre_class_coverage}%",

    )


with learning_cols[2]:

    st.metric(

        "In-Class",

        f"{in_class_coverage}%",

    )


with learning_cols[3]:

    st.metric(

        "Post-Class",

        f"{post_class_coverage}%",

    )


with learning_cols[4]:

    st.metric(

        "MCQs",

        total_mcqs,

    )


# ============================================================
# 41. FINAL REMAINING GAPS
# ============================================================

if final_remaining_gaps:

    st.divider()

    st.subheader(
        "⚠️ Remaining Curriculum Gaps"
    )


    gap_rows = []


    for gap in final_remaining_gaps:

        if not isinstance(
            gap,
            dict,
        ):

            continue


        gap_rows.append({

            "Type":
                gap.get(
                    "type"
                ),

            "Gap":
                gap.get(
                    "gap"
                ),

            "Priority":
                gap.get(
                    "priority"
                ),

            "Recommendation":
                gap.get(
                    "recommendation"
                ),

        })


    if gap_rows:

        st.dataframe(

            pd.DataFrame(
                gap_rows
            ),

            use_container_width=True,

            hide_index=True,

        )


# ============================================================
# 42. FINAL RECOMMENDATIONS
# ============================================================

st.divider()

st.subheader(
    "🎯 Final Recommendations"
)


for index, recommendation in enumerate(

    all_recommendations,

    start=1,

):

    st.markdown(

        f"""
        **{index}.**
        {recommendation}
        """

    )


# ============================================================
# 43. CURRICULUM STATUS
# ============================================================

st.divider()

if curriculum_readiness_score >= 85:

    st.success(

        f"""
        🟢 **{curriculum_status}**

        Curriculum readiness:
        **{curriculum_readiness_score}%**
        """

    )

elif curriculum_readiness_score >= 70:

    st.info(

        f"""
        🔵 **{curriculum_status}**

        Curriculum readiness:
        **{curriculum_readiness_score}%**
        """

    )

elif curriculum_readiness_score >= 50:

    st.warning(

        f"""
        🟡 **{curriculum_status}**

        Curriculum readiness:
        **{curriculum_readiness_score}%**
        """

    )

else:

    st.error(

        f"""
        🔴 **{curriculum_status}**

        Curriculum readiness:
        **{curriculum_readiness_score}%**
        """

    )


# ============================================================
# 44. DOWNLOAD FINAL ENHANCEMENT PACKAGE
# ============================================================

st.divider()

st.subheader(
    "📦 Export Complete Curriculum Intelligence Package"
)


st.download_button(

    "⬇️ Download Complete Enhancement Package",

    data=serialize_json(

        final_enhancement_package

    ),

    file_name=(

        "curriculum_intelligence_complete_package.json"

    ),

    mime="application/json",

    key="download_complete_enhancement_package",

)


# ============================================================
# 45. DOWNLOAD REPORT HANDOFF
# ============================================================

st.download_button(

    "⬇️ Download Report Handoff JSON",

    data=serialize_json(

        report_handoff

    ),

    file_name=(

        "curriculum_report_handoff.json"

    ),

    mime="application/json",

    key="download_report_handoff",

)


# ============================================================
# 46. DOWNLOAD INDUSTRY COVERAGE
# ============================================================

st.download_button(

    "⬇️ Download Industry Coverage",

    data=serialize_json(

        industry_coverage_report

    ),

    file_name=(

        "industry_jd_coverage.json"

    ),

    mime="application/json",

    key="download_industry_coverage",

)


# ============================================================
# 47. DOWNLOAD VALIDATION REPORT
# ============================================================

st.download_button(

    "⬇️ Download Validation Report",

    data=serialize_json(

        final_validation

    ),

    file_name=(

        "curriculum_validation_report.json"

    ),

    mime="application/json",

    key="download_curriculum_validation",

)


# ============================================================
# 48. FINAL SESSION STATE
# ============================================================

st.session_state[
    "curriculum_intelligence_complete"
] = True


st.session_state[
    "final_curriculum_ready"
] = True


st.session_state[
    "academic_syllabus_ready"
] = bool(
    academic_syllabus
)


st.session_state[
    "lesson_plans_ready"
] = (

    successful_lesson_count
    ==
    topic_count

    and

    topic_count > 0

)


st.session_state[
    "reports_ready"
] = True


# ============================================================
# 49. FINAL COMPLETION MESSAGE
# ============================================================

st.success(
    """
    🎉 **CURRICULUM / SYLLABUS INTELLIGENCE PIPELINE COMPLETE**

    The complete AI-powered curriculum enhancement workflow
    has been executed.

    ─────────────────────────────────────────────

    01  📥 Syllabus Extraction
            ↓
    02  📚 Curriculum Intelligence
            ↓
    03  💼 Industry / JD Intelligence
            ↓
    04  🔍 Gap Analysis
            ↓
        Enhancement Blueprint
            ↓
        Expert Agent
            ↓
        Critic Agent
            ↓
        Final Enhancement Agent
            ↓
        CO / PO / PSO
            ↓
        Academic Syllabus
            ↓
        AI Lesson Plans
            ↓
        Teaching Content
            ↓
        Assessment Content
            ↓
        Final Validation
            ↓
    05  📊 Reports

    ─────────────────────────────────────────────

    FINAL OUTPUTS

    ✓ Enhanced Curriculum
    ✓ Academic Syllabus
    ✓ CO / PO / PSO
    ✓ CO–PO Matrix
    ✓ CO–PSO Matrix
    ✓ Industry / JD Coverage
    ✓ Curriculum Gaps
    ✓ Enhancement Recommendations
    ✓ Industry Projects
    ✓ Tools
    ✓ Technologies
    ✓ Topic-level Lesson Plans
    ✓ Pre-Class Content
    ✓ Faculty Teaching Content
    ✓ Post-Class Content
    ✓ Assignments
    ✓ MCQs
    ✓ Final Validation
    ✓ Report Handoff

    The complete package is now available to the Reports
    module.
    """
)


# ============================================================
# 50. HANDOFF INFORMATION
# ============================================================

st.info(
    """
    **Next Page: 05_📊_Reports.py**

    The Reports module should read:

        st.session_state["report_handoff"]

    and generate:

        • Syllabus Comparison Report
        • Curriculum Intelligence Report
        • Industry / JD Analysis Report
        • Gap Analysis Report
        • Enhancement Report
        • Final Enhanced Syllabus
        • CO / PO Report
        • Lesson Plan Report
        • Industry Skill Coverage Report
        • Final Curriculum PDF / DOCX
    """
)


# ============================================================
# END OF CHUNK 10/10
# ============================================================
