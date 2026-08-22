# pages/01_📥_Extract_Syllabus.py

import json
from pathlib import Path
import os
import streamlit as st

from curriculum.extractor import extract_syllabus
from rag.document_loader import process_uploaded_file


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Extract Syllabus | PragyanAI",
    page_icon="📥",
    layout="wide",
)


# ============================================================
# CONSTANTS
# ============================================================

SUPPORTED_FILE_TYPES = [
    "pdf",
    "docx",
    "png",
    "jpg",
    "jpeg",
]

MAX_PREVIEW_CHARS = 20000


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

DEFAULT_STATE = {
    "primary_syllabus": None,
    "primary_syllabus_text": "",
    "primary_filename": "",
    "primary_extraction_pages": [],
    "primary_extraction_complete": False,
}


for key, default_value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = default_value


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_value(
    value,
    default="Not Available",
):
    """
    Safely display empty values.
    """

    if value is None:
        return default

    if isinstance(value, str):

        if not value.strip():
            return default

        return value.strip()

    return value


def get_module_topic_count(
    syllabus: dict,
) -> int:

    total = 0

    for module in syllabus.get(
        "modules",
        [],
    ):

        total += len(
            module.get(
                "topics",
                [],
            )
        )

    return total


def get_total_modules(
    syllabus: dict,
) -> int:

    return len(
        syllabus.get(
            "modules",
            [],
        )
    )


def get_total_outcomes(
    syllabus: dict,
) -> int:

    return len(
        syllabus.get(
            "course_outcomes",
            [],
        )
    )


def get_total_tools(
    syllabus: dict,
) -> int:

    return len(
        syllabus.get(
            "tools",
            [],
        )
    )


def normalize_extracted_pages(
    pages,
) -> list[dict]:

    normalized = []

    if not pages:
        return normalized

    for index, page in enumerate(
        pages,
        start=1,
    ):

        if not isinstance(
            page,
            dict,
        ):
            continue

        text = page.get(
            "text",
            "",
        )

        if text is None:
            text = ""

        text = str(
            text
        ).strip()

        normalized.append({

            "page":
                page.get(
                    "page",
                    index,
                ),

            "text":
                text,

            "source":
                page.get(
                    "source",
                    "",
                ),
        })

    return normalized


def combine_pages(
    pages: list[dict],
) -> str:

    chunks = []

    for page in pages:

        page_number = page.get(
            "page",
            "",
        )

        text = page.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        chunks.append(
            f"\n\n===== PAGE {page_number} =====\n\n"
            f"{text}"
        )

    return "".join(
        chunks
    ).strip()


def validate_extraction(
    syllabus: dict,
) -> list[str]:
    """
    Performs basic validation after LLM extraction.

    This does not replace human review.
    """

    warnings = []

    if not syllabus.get(
        "subject_name"
    ):

        warnings.append(
            "Subject name could not be confidently extracted."
        )

    if not syllabus.get(
        "subject_code"
    ):

        warnings.append(
            "Subject code could not be confidently extracted."
        )

    if not syllabus.get(
        "university"
    ):

        warnings.append(
            "University name could not be confidently extracted."
        )

    if not syllabus.get(
        "modules"
    ):

        warnings.append(
            "No modules were detected."
        )

    for index, module in enumerate(
        syllabus.get(
            "modules",
            [],
        ),
        start=1,
    ):

        if not module.get(
            "name"
        ):

            warnings.append(
                f"Module {index} does not have a module name."
            )

        if not module.get(
            "topics"
        ):

            warnings.append(
                f"Module {index} contains no detected topics."
            )

    return warnings


def format_module_for_display(
    module: dict,
) -> str:

    name = safe_value(
        module.get(
            "name"
        ),
        "Unnamed Module",
    )

    hours = module.get(
        "hours"
    )

    if hours is not None:

        header = (
            f"### {name} — {hours} Hours"
        )

    else:

        header = (
            f"### {name}"
        )

    lines = [header]

    topics = module.get(
        "topics",
        [],
    )

    if not topics:

        lines.append(
            "No topics detected."
        )

        return "\n".join(
            lines
        )

    for topic in topics:

        topic_name = safe_value(
            topic.get(
                "name"
            ),
            "Unnamed Topic",
        )

        description = (
            topic.get(
                "description",
                "",
            )
            or ""
        ).strip()

        lines.append(
            f"- **{topic_name}**"
        )

        if description:

            lines.append(
                f"  - {description}"
            )

    return "\n".join(
        lines
    )


def display_list(
    values,
    empty_message="Not available.",
):
    """
    Generic list renderer.
    """

    if not values:

        st.info(
            empty_message
        )

        return

    for value in values:

        if isinstance(
            value,
            dict,
        ):

            st.json(
                value
            )

        else:

            st.markdown(
                f"- {value}"
            )


# ============================================================
# PAGE HEADER
# ============================================================

st.title(
    "📥 Extract Syllabus"
)

st.markdown(
    """
### AI-Powered Curriculum / Syllabus Extraction

Upload an official university syllabus and extract structured
academic information including:

- Institution information
- University / College
- Program / Department
- Subject name and code
- Semester / Regulation
- Credits and contact hours
- Course objectives
- Prerequisites
- Modules and topics
- Course Outcomes
- Program Outcomes
- PSOs
- CO-PO mapping
- Teaching methodology
- Practical / laboratory components
- Assessment pattern
- Textbooks and references
- Tools and technologies
- Datasets
- Projects and case studies
- Other curriculum information
"""
)

st.divider()


# ============================================================
# UPLOAD SECTION
# ============================================================

st.subheader(
    "1️⃣ Upload Official Syllabus"
)

uploaded_file = st.file_uploader(

    "Upload syllabus / curriculum document",

    type=SUPPORTED_FILE_TYPES,

    help=(
        "Supported formats: PDF, DOCX, PNG, JPG and JPEG. "
        "Scanned syllabus pages can be processed using OCR."
    ),
)


if uploaded_file:

    file_size_mb = (
        len(
            uploaded_file.getvalue()
        )
        / (
            1024 * 1024
        )
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "File",
            uploaded_file.name,
        )

    with col2:

        st.metric(
            "Format",
            Path(
                uploaded_file.name
            ).suffix.upper(),
        )

    with col3:

        st.metric(
            "Size",
            f"{file_size_mb:.2f} MB",
        )


# ============================================================
# EXTRACTION BUTTON
# ============================================================

if uploaded_file:

    st.divider()

    st.subheader(
        "2️⃣ Extract Complete Syllabus"
    )

    st.caption(
        "The document is first converted to text and then "
        "analyzed by the curriculum extraction LLM."
    )

    extract_clicked = st.button(

        "🚀 Extract Complete Syllabus",

        type="primary",

        use_container_width=True,
    )

    if extract_clicked:

        progress = st.progress(
            0
        )

        status_box = st.empty()

        try:

            # ------------------------------------------------
            # STEP 1 — DOCUMENT EXTRACTION
            # ------------------------------------------------

            status_box.info(
                "Step 1/4 — Reading uploaded document..."
            )

            progress.progress(
                20
            )

            pages = process_uploaded_file(
                uploaded_file
            )

            pages = normalize_extracted_pages(
                pages
            )

            if not pages:

                raise ValueError(
                    "The document could not be processed."
                )

            # ------------------------------------------------
            # STEP 2 — COMBINE TEXT
            # ------------------------------------------------

            status_box.info(
                "Step 2/4 — Preparing extracted text..."
            )

            progress.progress(
                40
            )

            extracted_text = combine_pages(
                pages
            )

            if not extracted_text.strip():

                raise ValueError(
                    "No readable text was extracted from the document."
                )

            # ------------------------------------------------
            # STEP 3 — LLM EXTRACTION
            # ------------------------------------------------

            status_box.info(
                "Step 3/4 — AI is extracting curriculum structure..."
            )

            progress.progress(
                65
            )

            syllabus = extract_syllabus(
                extracted_text
            )

            if not isinstance(
                syllabus,
                dict,
            ):

                raise ValueError(
                    "The extraction engine returned an invalid result."
                )

            # ------------------------------------------------
            # STEP 4 — VALIDATION
            # ------------------------------------------------

            status_box.info(
                "Step 4/4 — Validating extracted curriculum..."
            )

            progress.progress(
                90
            )

            warnings = validate_extraction(
                syllabus
            )

            # ------------------------------------------------
            # SAVE TO SESSION
            # ------------------------------------------------

            st.session_state[
                "primary_syllabus"
            ] = syllabus

            st.session_state[
                "primary_syllabus_text"
            ] = extracted_text

            st.session_state[
                "primary_filename"
            ] = uploaded_file.name

            st.session_state[
                "primary_extraction_pages"
            ] = pages

            st.session_state[
                "primary_extraction_complete"
            ] = True

            progress.progress(
                100
            )

            status_box.success(
                "✅ Syllabus extraction completed successfully."
            )

            if warnings:

                st.warning(
                    "The extraction completed, but some fields "
                    "may require human verification."
                )

                for warning in warnings:

                    st.write(
                        f"⚠️ {warning}"
                    )

        except Exception as exc:

            progress.empty()

            status_box.error(
                "❌ Syllabus extraction failed."
            )

            st.exception(
                exc
            )


# ============================================================
# LOAD CURRENT RESULT
# ============================================================

syllabus = st.session_state.get(
    "primary_syllabus"
)


# ============================================================
# EXTRACTION SUMMARY
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "3️⃣ Extraction Summary"
    )

    modules_count = get_total_modules(
        syllabus
    )

    topics_count = get_module_topic_count(
        syllabus
    )

    outcomes_count = get_total_outcomes(
        syllabus
    )

    tools_count = get_total_tools(
        syllabus
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Modules",
            modules_count,
        )

    with col2:

        st.metric(
            "Topics",
            topics_count,
        )

    with col3:

        st.metric(
            "Course Outcomes",
            outcomes_count,
        )

    with col4:

        st.metric(
            "Tools / Technologies",
            tools_count,
        )


# ============================================================
# INSTITUTION INFORMATION
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "4️⃣ Institution & Academic Information"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 🏫 Institution"
        )

        st.write(
            "**College:**",
            safe_value(
                syllabus.get(
                    "college"
                )
            ),
        )

        st.write(
            "**University:**",
            safe_value(
                syllabus.get(
                    "university"
                )
            ),
        )

        st.write(
            "**Program:**",
            safe_value(
                syllabus.get(
                    "program"
                )
            ),
        )

        st.write(
            "**Department:**",
            safe_value(
                syllabus.get(
                    "department"
                )
            ),
        )

    with col2:

        st.markdown(
            "### 📚 Academic Details"
        )

        st.write(
            "**Academic Year:**",
            safe_value(
                syllabus.get(
                    "academic_year"
                )
            ),
        )

        st.write(
            "**Regulation:**",
            safe_value(
                syllabus.get(
                    "regulation"
                )
            ),
        )

        st.write(
            "**Semester:**",
            safe_value(
                syllabus.get(
                    "semester"
                )
            ),
        )

        st.write(
            "**Category:**",
            safe_value(
                syllabus.get(
                    "category"
                )
            ),
        )


# ============================================================
# SUBJECT INFORMATION
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "5️⃣ Subject Information"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            "**Subject Name**"
        )

        st.info(
            safe_value(
                syllabus.get(
                    "subject_name"
                )
            )
        )

    with col2:

        st.markdown(
            "**Subject Code**"
        )

        st.info(
            safe_value(
                syllabus.get(
                    "subject_code"
                )
            )
        )

    with col3:

        st.markdown(
            "**Credits**"
        )

        credits = syllabus.get(
            "credits"
        )

        st.info(
            str(
                credits
                if credits is not None
                else "Not Available"
            )
        )

    with col4:

        st.markdown(
            "**Contact Hours**"
        )

        st.info(
            safe_value(
                syllabus.get(
                    "contact_hours"
                )
            )
        )


# ============================================================
# OBJECTIVES & PREREQUISITES
# ============================================================

if syllabus:

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "🎯 Course Objectives"
        )

        display_list(
            syllabus.get(
                "course_objectives",
                [],
            ),
            "No course objectives detected.",
        )

    with col2:

        st.subheader(
            "📌 Prerequisites"
        )

        display_list(
            syllabus.get(
                "prerequisites",
                [],
            ),
            "No prerequisites detected.",
        )


# ============================================================
# MODULES
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "6️⃣ Modules & Topics"
    )

    modules = syllabus.get(
        "modules",
        [],
    )

    if not modules:

        st.warning(
            "No modules were detected."
        )

    else:

        for index, module in enumerate(
            modules,
            start=1,
        ):

            module_name = safe_value(
                module.get(
                    "name"
                ),
                f"Module {index}",
            )

            hours = module.get(
                "hours"
            )

            if hours is not None:

                expander_title = (
                    f"Module {index}: "
                    f"{module_name} "
                    f"({hours} Hours)"
                )

            else:

                expander_title = (
                    f"Module {index}: "
                    f"{module_name}"
                )

            with st.expander(
                expander_title,
                expanded=False,
            ):

                topics = module.get(
                    "topics",
                    [],
                )

                if not topics:

                    st.warning(
                        "No topics detected for this module."
                    )

                else:

                    for topic_index, topic in enumerate(
                        topics,
                        start=1,
                    ):

                        topic_name = safe_value(
                            topic.get(
                                "name"
                            ),
                            f"Topic {topic_index}",
                        )

                        st.markdown(
                            f"**{topic_index}. {topic_name}**"
                        )

                        description = (
                            topic.get(
                                "description",
                                "",
                            )
                            or ""
                        ).strip()

                        if description:

                            st.caption(
                                description
                            )


# ============================================================
# COURSE OUTCOMES
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "7️⃣ Course Outcomes — CO"
    )

    outcomes = syllabus.get(
        "course_outcomes",
        [],
    )

    if not outcomes:

        st.info(
            "No Course Outcomes detected."
        )

    else:

        for index, outcome in enumerate(
            outcomes,
            start=1,
        ):

            st.markdown(
                f"**CO{index}:** {outcome}"
            )


# ============================================================
# PO / PSO
# ============================================================

if syllabus:

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "🎓 Program Outcomes — PO"
        )

        display_list(
            syllabus.get(
                "program_outcomes",
                [],
            ),
            "No Program Outcomes detected.",
        )

    with col2:

        st.subheader(
            "🎓 Program Specific Outcomes — PSO"
        )

        display_list(
            syllabus.get(
                "program_specific_outcomes",
                [],
            ),
            "No Program Specific Outcomes detected.",
        )


# ============================================================
# CO-PO MAPPING
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "8️⃣ CO-PO / CO-PSO Mapping"
    )

    mapping = syllabus.get(
        "co_po_mapping"
    )

    if mapping:

        st.json(
            mapping
        )

    else:

        st.info(
            "No CO-PO mapping detected."
        )


# ============================================================
# TEACHING / PRACTICAL
# ============================================================

if syllabus:

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "👨‍🏫 Teaching & Learning Methods"
        )

        display_list(
            syllabus.get(
                "teaching_learning_methods",
                [],
            ),
            "No teaching methods detected.",
        )

    with col2:

        st.subheader(
            "🧪 Practical / Laboratory"
        )

        display_list(
            syllabus.get(
                "practical_components",
                [],
            ),
            "No practical components detected.",
        )


# ============================================================
# ASSESSMENT
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "9️⃣ Assessment Pattern"
    )

    assessment = syllabus.get(
        "assessment_pattern"
    )

    if assessment:

        st.json(
            assessment
        )

    else:

        st.info(
            "No assessment pattern detected."
        )


# ============================================================
# TEXTBOOKS
# ============================================================

if syllabus:

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "📖 Textbooks"
        )

        display_list(
            syllabus.get(
                "textbooks",
                [],
            ),
            "No textbooks detected.",
        )

    with col2:

        st.subheader(
            "📚 Reference Books"
        )

        display_list(
            syllabus.get(
                "reference_books",
                [],
            ),
            "No reference books detected.",
        )


# ============================================================
# ONLINE RESOURCES
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "🌐 Online Resources"
    )

    display_list(
        syllabus.get(
            "online_resources",
            [],
        ),
        "No online resources detected.",
    )


# ============================================================
# TOOLS / TECHNOLOGIES
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "🛠 Tools & Technologies"
    )

    tools = syllabus.get(
        "tools",
        [],
    )

    if tools:

        columns = st.columns(
            min(
                max(
                    len(tools),
                    1,
                ),
                4,
            )
        )

        for index, tool in enumerate(
            tools
        ):

            columns[
                index % len(columns)
            ].success(
                tool
            )

    else:

        st.info(
            "No tools or technologies detected."
        )


# ============================================================
# DATASETS
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "🗃️ Datasets"
    )

    display_list(
        syllabus.get(
            "datasets",
            [],
        ),
        "No datasets detected.",
    )


# ============================================================
# PROJECTS / CASE STUDIES
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "🚀 Projects & Case Studies"
    )

    display_list(
        syllabus.get(
            "projects_case_studies",
            [],
        ),
        "No projects or case studies detected.",
    )


# ============================================================
# OTHER INFORMATION
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "📌 Other Extracted Information"
    )

    display_list(
        syllabus.get(
            "other_information",
            [],
        ),
        "No additional information detected.",
    )


# ============================================================
# RAW DOCUMENT TEXT
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "📄 Extracted Document Text"
    )

    raw_text = st.session_state.get(
        "primary_syllabus_text",
        "",
    )

    if raw_text:

        with st.expander(
            "View Raw Extracted Text",
            expanded=False,
        ):

            if len(raw_text) > MAX_PREVIEW_CHARS:

                st.text(
                    raw_text[
                        :MAX_PREVIEW_CHARS
                    ]
                )

                st.caption(
                    f"Showing first "
                    f"{MAX_PREVIEW_CHARS:,} characters."
                )

            else:

                st.text(
                    raw_text
                )

    else:

        st.info(
            "Raw extracted text is not available."
        )


# ============================================================
# JSON EXPORT
# ============================================================

if syllabus:

    st.divider()

    st.subheader(
        "⬇️ Export Extracted Curriculum"
    )

    json_data = json.dumps(
        syllabus,
        indent=2,
        ensure_ascii=False,
    )

    st.download_button(

        label="⬇️ Download Extracted Syllabus JSON",

        data=json_data,

        file_name=(
            "extracted_syllabus.json"
        ),

        mime="application/json",

        use_container_width=True,
    )


# ============================================================
# EXTRACTION STATUS
# ============================================================

if syllabus:

    st.divider()

    st.success(
        "✅ Syllabus is stored in session state and is now "
        "available to Curriculum Intelligence, Industry/JD "
        "Intelligence, Gap Analysis and Reports."
    )

    st.caption(
        f"Source file: "
        f"{st.session_state.get('primary_filename', 'Unknown')}"
    )
