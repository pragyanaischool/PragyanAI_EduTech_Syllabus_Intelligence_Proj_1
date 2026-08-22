# ============================================================
# rag/pdf_loader.py
# CHUNK 1/10
#
# PDF DOCUMENT LOADER
#
# Purpose:
#   Load PDF documents for the Curriculum Intelligence / RAG
#   pipeline.
#
# Features:
#   - PyMuPDF / fitz based extraction
#   - Page-by-page extraction
#   - Metadata extraction
#   - Scanned PDF detection
#   - Text cleaning
#   - Page-level document objects
#   - Error handling
#   - Optional OCR handoff
#
# Pipeline:
#
#   PDF
#    │
#    ▼
#   PyMuPDF
#    │
#    ├── Metadata
#    ├── Pages
#    └── Text
#         │
#         ▼
#      Cleaning
#         │
#         ▼
#   Document Objects
#         │
#         ▼
#      Chunker
#
# ============================================================

from __future__ import annotations

import logging
import re

from dataclasses import (
    dataclass,
    field,
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
    Union,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(
    __name__
)


# ============================================================
# VERSION
# ============================================================

PDF_LOADER_VERSION = "1.0.0"


# ============================================================
# DEFAULT CONFIGURATION
# ============================================================

DEFAULT_MIN_TEXT_LENGTH = 20

DEFAULT_MAX_TEXT_LENGTH = 1_000_000

DEFAULT_ENCODING = "utf-8"


# ============================================================
# SUPPORTED EXTENSIONS
# ============================================================

SUPPORTED_PDF_EXTENSIONS = {

    ".pdf",

}


# ============================================================
# PDF DOCUMENT MODEL
# ============================================================

@dataclass
class PDFDocument:

    text: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    page_number: int = 0

    source: str = ""

    filename: str = ""

    file_path: str = ""

    page_count: int = 0

    is_scanned: bool = False

    extraction_method: str = "pymupdf"

    error: Optional[str] = None


# ============================================================
# PDF LOAD RESULT
# ============================================================

@dataclass
class PDFLoadResult:

    documents: List[PDFDocument] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    page_count: int = 0

    extracted_page_count: int = 0

    empty_page_count: int = 0

    is_scanned: bool = False

    success: bool = True

    error: Optional[str] = None

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# PYMUPDF + BASIC UTILITIES
# ============================================================


# ============================================================
# OPTIONAL PYMUPDF IMPORT
# ============================================================

try:

    import fitz

except ImportError:

    fitz = None


# ============================================================
# CHECK PYMUPDF
# ============================================================

def is_pymupdf_available() -> bool:

    return fitz is not None


# ============================================================
# REQUIRE PYMUPDF
# ============================================================

def require_pymupdf() -> None:

    if fitz is None:

        raise ImportError(

            "PyMuPDF is required for PDF loading. "
            "Install it using: pip install pymupdf"

        )


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(
    text: Any,
) -> str:

    if text is None:

        return ""

    text = str(
        text
    )

    # --------------------------------------------------------
    # Normalize line endings
    # --------------------------------------------------------

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    # --------------------------------------------------------
    # Remove null characters
    # --------------------------------------------------------

    text = text.replace(
        "\x00",
        "",
    )

    # --------------------------------------------------------
    # Normalize spaces
    # --------------------------------------------------------

    text = re.sub(

        r"[ \t]+",

        " ",

        text,

    )

    # --------------------------------------------------------
    # Normalize excessive newlines
    # --------------------------------------------------------

    text = re.sub(

        r"\n{3,}",

        "\n\n",

        text,

    )

    # --------------------------------------------------------
    # Remove whitespace around lines
    # --------------------------------------------------------

    lines = [

        line.strip()

        for line
        in text.split(
            "\n"
        )

    ]

    # --------------------------------------------------------
    # Remove repeated empty lines
    # --------------------------------------------------------

    cleaned_lines = []

    previous_empty = False

    for line in lines:

        if not line:

            if previous_empty:

                continue

            previous_empty = True

            cleaned_lines.append(
                ""
            )

        else:

            previous_empty = False

            cleaned_lines.append(
                line
            )

    return "\n".join(
        cleaned_lines
    ).strip()


# ============================================================
# NORMALIZE FILENAME
# ============================================================

def normalize_filename(
    filename: Any,
) -> str:

    if filename is None:

        return ""

    return Path(
        str(filename)
    ).name


# ============================================================
# NORMALIZE SOURCE
# ============================================================

def normalize_source(
    source: Any,
) -> str:

    if source is None:

        return ""

    return str(
        source
    ).strip()


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# PDF VALIDATION + METADATA
# ============================================================


# ============================================================
# VALIDATE PDF PATH
# ============================================================

def validate_pdf_path(
    file_path: Union[
        str,
        Path,
    ],
) -> Path:

    path = Path(
        file_path
    )

    if not path.exists():

        raise FileNotFoundError(

            f"PDF file does not exist: {path}"

        )

    if not path.is_file():

        raise ValueError(

            f"Path is not a file: {path}"

        )

    if path.suffix.lower() not in (
        SUPPORTED_PDF_EXTENSIONS
    ):

        raise ValueError(

            f"Unsupported file type: {path.suffix}. "
            "Expected a PDF file."

        )

    return path


# ============================================================
# VALIDATE PDF BYTES
# ============================================================

def validate_pdf_bytes(
    data: bytes,
) -> None:

    if not data:

        raise ValueError(
            "PDF data is empty."
        )

    # --------------------------------------------------------
    # PDF files normally begin with %PDF
    # --------------------------------------------------------

    if not data.startswith(
        b"%PDF"
    ):

        logger.warning(

            "PDF bytes do not start with the expected %PDF header."

        )


# ============================================================
# EXTRACT METADATA
# ============================================================

def extract_metadata(
    pdf_document: Any,
) -> Dict[str, Any]:

    metadata = {}

    try:

        raw_metadata = (
            pdf_document.metadata
            or
            {}
        )

        for key, value in raw_metadata.items():

            if value is None:

                continue

            value = str(
                value
            ).strip()

            if value:

                metadata[
                    key
                ] = value

    except Exception as exc:

        logger.warning(

            "Unable to extract PDF metadata: %s",

            exc,

        )

    # --------------------------------------------------------
    # Additional PDF information
    # --------------------------------------------------------

    try:

        metadata[
            "page_count"
        ] = len(
            pdf_document
        )

    except Exception:

        pass

    try:

        metadata[
            "pdf_version"
        ] = getattr(

            pdf_document,

            "pdf_version",

            "",

        )

    except Exception:

        pass

    return metadata


# ============================================================
# DETECT SCANNED PDF
# ============================================================

def detect_scanned_pdf(
    pages: Sequence[PDFDocument],
    min_text_length: int = DEFAULT_MIN_TEXT_LENGTH,
) -> bool:

    if not pages:

        return False

    text_pages = 0

    for page in pages:

        text = clean_text(
            page.text
        )

        if len(text) >= min_text_length:

            text_pages += 1

    # --------------------------------------------------------
    # If less than 20% of pages contain meaningful text,
    # treat document as likely scanned.
    # --------------------------------------------------------

    ratio = (

        text_pages
        /
        max(
            len(pages),
            1,
        )

    )

    return ratio < 0.20


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# PAGE EXTRACTION
# ============================================================


# ============================================================
# EXTRACT SINGLE PAGE
# ============================================================

def extract_page(
    page: Any,
    page_number: int,
    source: str = "",
    filename: str = "",
    file_path: str = "",
    page_count: int = 0,
) -> PDFDocument:

    try:

        raw_text = page.get_text(
            "text"
        )

        text = clean_text(
            raw_text
        )

        metadata = {

            "page_number":
                page_number,

            "page_index":
                page_number - 1,

        }

        # ----------------------------------------------------
        # Page dimensions
        # ----------------------------------------------------

        try:

            rect = page.rect

            metadata[
                "width"
            ] = float(
                rect.width
            )

            metadata[
                "height"
            ] = float(
                rect.height
            )

        except Exception:

            pass

        # ----------------------------------------------------
        # Block count
        # ----------------------------------------------------

        try:

            blocks = page.get_text(
                "blocks"
            )

            metadata[
                "block_count"
            ] = len(
                blocks
            )

        except Exception:

            pass

        return PDFDocument(

            text=text,

            metadata=metadata,

            page_number=page_number,

            source=source,

            filename=filename,

            file_path=file_path,

            page_count=page_count,

            is_scanned=len(text) < DEFAULT_MIN_TEXT_LENGTH,

            extraction_method="pymupdf",

        )

    except Exception as exc:

        logger.exception(

            "Failed to extract page %s",

            page_number,

        )

        return PDFDocument(

            text="",

            metadata={

                "page_number":
                    page_number,

            },

            page_number=page_number,

            source=source,

            filename=filename,

            file_path=file_path,

            page_count=page_count,

            is_scanned=True,

            extraction_method="pymupdf",

            error=str(
                exc
            ),

        )


# ============================================================
# EXTRACT ALL PAGES
# ============================================================

def extract_pages(
    pdf_document: Any,
    source: str = "",
    filename: str = "",
    file_path: str = "",
) -> List[PDFDocument]:

    page_count = len(
        pdf_document
    )

    documents = []

    for index in range(
        page_count
    ):

        page_number = index + 1

        page = pdf_document[
            index
        ]

        document = extract_page(

            page=page,

            page_number=page_number,

            source=source,

            filename=filename,

            file_path=file_path,

            page_count=page_count,

        )

        documents.append(
            document
        )

    return documents


# ============================================================
# EXTRACT PAGE RANGE
# ============================================================

def extract_page_range(
    pdf_document: Any,
    start_page: int,
    end_page: int,
    source: str = "",
    filename: str = "",
    file_path: str = "",
) -> List[PDFDocument]:

    page_count = len(
        pdf_document
    )

    start_page = max(
        1,
        int(
            start_page
        ),
    )

    end_page = min(

        page_count,

        int(
            end_page
        ),

    )

    if start_page > end_page:

        return []

    documents = []

    for page_number in range(

        start_page,

        end_page + 1,

    ):

        page = pdf_document[
            page_number - 1
        ]

        documents.append(

            extract_page(

                page,

                page_number,

                source,

                filename,

                file_path,

                page_count,

            )

        )

    return documents


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# FILE-BASED PDF LOADING
# ============================================================


# ============================================================
# OPEN PDF
# ============================================================

def open_pdf(
    file_path: Union[
        str,
        Path,
    ],
) -> Any:

    require_pymupdf()

    path = validate_pdf_path(
        file_path
    )

    try:

        return fitz.open(
            str(path)
        )

    except Exception as exc:

        logger.exception(
            "Unable to open PDF: %s",
            path,
        )

        raise RuntimeError(

            f"Unable to open PDF: {path}"

        ) from exc


# ============================================================
# LOAD PDF FILE
# ============================================================

def load_pdf(
    file_path: Union[
        str,
        Path,
    ],
    min_text_length: int = DEFAULT_MIN_TEXT_LENGTH,
) -> PDFLoadResult:

    path = validate_pdf_path(
        file_path
    )

    pdf = None

    try:

        pdf = open_pdf(
            path
        )

        metadata = extract_metadata(
            pdf
        )

        documents = extract_pages(

            pdf_document=pdf,

            source=str(
                path
            ),

            filename=path.name,

            file_path=str(
                path.resolve()
            ),

        )

        # ----------------------------------------------------
        # Detect scanned status
        # ----------------------------------------------------

        scanned = detect_scanned_pdf(

            documents,

            min_text_length=min_text_length,

        )

        # ----------------------------------------------------
        # Update page scan information
        # ----------------------------------------------------

        for document in documents:

            document.is_scanned = scanned

        extracted_count = sum(

            1

            for document
            in documents

            if len(
                clean_text(
                    document.text
                )
            ) >= min_text_length

        )

        empty_count = (

            len(
                documents
            )

            -

            extracted_count

        )

        warnings = []

        if scanned:

            warnings.append(

                "PDF appears to be scanned or contains "
                "very little machine-readable text. OCR "
                "may be required."

            )

        if empty_count:

            warnings.append(

                f"{empty_count} page(s) contain little "
                "or no extractable text."

            )

        return PDFLoadResult(

            documents=documents,

            metadata=metadata,

            page_count=len(
                documents
            ),

            extracted_page_count=extracted_count,

            empty_page_count=empty_count,

            is_scanned=scanned,

            success=True,

            warnings=warnings,

        )

    except Exception as exc:

        logger.exception(

            "PDF loading failed: %s",

            path,

        )

        return PDFLoadResult(

            documents=[],

            metadata={

                "filename":
                    path.name,

                "file_path":
                    str(path),

            },

            page_count=0,

            extracted_page_count=0,

            empty_page_count=0,

            is_scanned=False,

            success=False,

            error=str(
                exc
            ),

            warnings=[],

        )

    finally:

        if pdf is not None:

            try:

                pdf.close()

            except Exception:

                pass


# ============================================================
# LOAD PDF STRICT
# ============================================================

def load_pdf_strict(
    file_path: Union[
        str,
        Path,
    ],
) -> PDFLoadResult:

    result = load_pdf(
        file_path
    )

    if not result.success:

        raise RuntimeError(

            result.error
            or
            "Unknown PDF loading error."

        )

    return result


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# BYTES / STREAM PDF LOADING
# ============================================================


# ============================================================
# OPEN PDF BYTES
# ============================================================

def open_pdf_bytes(
    data: bytes,
) -> Any:

    require_pymupdf()

    validate_pdf_bytes(
        data
    )

    try:

        return fitz.open(

            stream=data,

            filetype="pdf",

        )

    except Exception as exc:

        logger.exception(
            "Unable to open PDF bytes."
        )

        raise RuntimeError(

            "Unable to open PDF from bytes."

        ) from exc


# ============================================================
# LOAD PDF BYTES
# ============================================================

def load_pdf_bytes(
    data: bytes,
    filename: str = "document.pdf",
    source: str = "memory",
    min_text_length: int = DEFAULT_MIN_TEXT_LENGTH,
) -> PDFLoadResult:

    pdf = None

    try:

        pdf = open_pdf_bytes(
            data
        )

        metadata = extract_metadata(
            pdf
        )

        documents = extract_pages(

            pdf_document=pdf,

            source=source,

            filename=normalize_filename(
                filename
            ),

            file_path="",

        )

        scanned = detect_scanned_pdf(

            documents,

            min_text_length=min_text_length,

        )

        for document in documents:

            document.is_scanned = scanned

        extracted_count = sum(

            1

            for document
            in documents

            if len(
                clean_text(
                    document.text
                )
            ) >= min_text_length

        )

        empty_count = (

            len(
                documents
            )

            -

            extracted_count

        )

        warnings = []

        if scanned:

            warnings.append(

                "PDF appears to be scanned. "
                "OCR may be required."

            )

        return PDFLoadResult(

            documents=documents,

            metadata=metadata,

            page_count=len(
                documents
            ),

            extracted_page_count=extracted_count,

            empty_page_count=empty_count,

            is_scanned=scanned,

            success=True,

            warnings=warnings,

        )

    except Exception as exc:

        logger.exception(
            "PDF byte loading failed."
        )

        return PDFLoadResult(

            documents=[],

            metadata={},

            page_count=0,

            extracted_page_count=0,

            empty_page_count=0,

            is_scanned=False,

            success=False,

            error=str(
                exc
            ),

            warnings=[],

        )

    finally:

        if pdf is not None:

            try:

                pdf.close()

            except Exception:

                pass


# ============================================================
# LOAD PDF STREAM
# ============================================================

def load_pdf_stream(
    stream: Any,
    filename: str = "document.pdf",
    source: str = "stream",
) -> PDFLoadResult:

    if stream is None:

        raise ValueError(
            "PDF stream cannot be None."
        )

    try:

        data = stream.read()

    except AttributeError as exc:

        raise TypeError(

            "Expected a file-like object with read()."

        ) from exc

    if not isinstance(
        data,
        bytes,
    ):

        raise TypeError(

            "PDF stream must return bytes."

        )

    return load_pdf_bytes(

        data=data,

        filename=filename,

        source=source,

    )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# TEXT EXTRACTION HELPERS
# ============================================================


# ============================================================
# GET PAGE TEXT
# ============================================================

def get_page_text(
    document: PDFDocument,
) -> str:

    return clean_text(
        document.text
    )


# ============================================================
# GET ALL TEXT
# ============================================================

def get_all_text(
    result: PDFLoadResult,
    separator: str = "\n\n",
) -> str:

    texts = []

    for document in result.documents:

        text = get_page_text(
            document
        )

        if not text:

            continue

        # ----------------------------------------------------
        # Add page marker
        # ----------------------------------------------------

        page_marker = (

            f"[Page "
            f"{document.page_number}"
            f"]"

        )

        texts.append(

            page_marker
            +
            "\n"
            +
            text

        )

    return separator.join(
        texts
    ).strip()


# ============================================================
# GET NON-EMPTY PAGES
# ============================================================

def get_non_empty_pages(
    result: PDFLoadResult,
    min_text_length: int = DEFAULT_MIN_TEXT_LENGTH,
) -> List[PDFDocument]:

    return [

        document

        for document
        in result.documents

        if len(
            clean_text(
                document.text
            )
        )
        >=
        min_text_length

    ]


# ============================================================
# GET EMPTY PAGES
# ============================================================

def get_empty_pages(
    result: PDFLoadResult,
    min_text_length: int = DEFAULT_MIN_TEXT_LENGTH,
) -> List[PDFDocument]:

    return [

        document

        for document
        in result.documents

        if len(
            clean_text(
                document.text
            )
        )
        <
        min_text_length

    ]


# ============================================================
# PAGE TEXT STATISTICS
# ============================================================

def page_statistics(
    document: PDFDocument,
) -> Dict[str, Any]:

    text = clean_text(
        document.text
    )

    words = (

        text.split()

        if text

        else []

    )

    return {

        "page_number":
            document.page_number,

        "characters":
            len(text),

        "words":
            len(words),

        "lines":
            len(
                text.splitlines()
            )
            if text
            else 0,

        "is_empty":
            not bool(text),

        "is_scanned":
            document.is_scanned,

        "has_error":
            bool(
                document.error
            ),

    }


# ============================================================
# DOCUMENT STATISTICS
# ============================================================

def document_statistics(
    result: PDFLoadResult,
) -> Dict[str, Any]:

    page_stats = [

        page_statistics(
            document
        )

        for document
        in result.documents

    ]

    total_characters = sum(

        item[
            "characters"
        ]

        for item
        in page_stats

    )

    total_words = sum(

        item[
            "words"
        ]

        for item
        in page_stats

    )

    return {

        "page_count":
            result.page_count,

        "extracted_pages":
            result.extracted_page_count,

        "empty_pages":
            result.empty_page_count,

        "is_scanned":
            result.is_scanned,

        "total_characters":
            total_characters,

        "total_words":
            total_words,

        "average_words_per_page": (

            round(

                total_words
                /
                max(
                    result.page_count,
                    1,
                ),

                2,

            )

        ),

        "pages":
            page_stats,

    }


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# LANGCHAIN / RAG DOCUMENT CONVERSION
# ============================================================


# ============================================================
# OPTIONAL LANGCHAIN DOCUMENT
# ============================================================

try:

    from langchain_core.documents import (
        Document as LangChainDocument,
    )

except ImportError:

    LangChainDocument = None


# ============================================================
# CONVERT PAGE TO DICT
# ============================================================

def page_to_dict(
    document: PDFDocument,
) -> Dict[str, Any]:

    metadata = dict(
        document.metadata
    )

    metadata.update({

        "source":
            document.source,

        "filename":
            document.filename,

        "file_path":
            document.file_path,

        "page":
            document.page_number,

        "page_count":
            document.page_count,

        "is_scanned":
            document.is_scanned,

        "extraction_method":
            document.extraction_method,

    })

    return {

        "page_content":
            document.text,

        "metadata":
            metadata,

    }


# ============================================================
# CONVERT TO LANGCHAIN DOCUMENT
# ============================================================

def page_to_langchain_document(
    document: PDFDocument,
) -> Any:

    if LangChainDocument is None:

        raise ImportError(

            "langchain-core is required for LangChain "
            "Document conversion. Install it using: "
            "pip install langchain-core"

        )

    metadata = dict(
        document.metadata
    )

    metadata.update({

        "source":
            document.source,

        "filename":
            document.filename,

        "file_path":
            document.file_path,

        "page":
            document.page_number,

        "page_count":
            document.page_count,

        "is_scanned":
            document.is_scanned,

        "extraction_method":
            document.extraction_method,

    })

    return LangChainDocument(

        page_content=document.text,

        metadata=metadata,

    )


# ============================================================
# RESULT → LANGCHAIN DOCUMENTS
# ============================================================

def to_langchain_documents(
    result: PDFLoadResult,
    skip_empty: bool = True,
) -> List[Any]:

    documents = []

    for document in result.documents:

        if skip_empty and not clean_text(
            document.text
        ):

            continue

        try:

            documents.append(

                page_to_langchain_document(
                    document
                )

            )

        except ImportError:

            raise

        except Exception as exc:

            logger.warning(

                "Failed converting page %s: %s",

                document.page_number,

                exc,

            )

    return documents


# ============================================================
# RESULT → SIMPLE DOCUMENT DICTS
# ============================================================

def to_document_dicts(
    result: PDFLoadResult,
    skip_empty: bool = True,
) -> List[Dict[str, Any]]:

    documents = []

    for document in result.documents:

        if skip_empty and not clean_text(
            document.text
        ):

            continue

        documents.append(
            page_to_dict(
                document
            )
        )

    return documents


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# OCR HANDOFF + BATCH PDF LOADING
# ============================================================


# ============================================================
# FIND SCANNED PAGES
# ============================================================

def find_scanned_pages(
    result: PDFLoadResult,
    min_text_length: int = DEFAULT_MIN_TEXT_LENGTH,
) -> List[int]:

    return [

        document.page_number

        for document
        in result.documents

        if len(
            clean_text(
                document.text
            )
        )
        <
        min_text_length

    ]


# ============================================================
# SHOULD_USE_OCR
# ============================================================

def should_use_ocr(
    result: PDFLoadResult,
    threshold: float = 0.20,
) -> bool:

    if not result.documents:

        return False

    empty_ratio = (

        result.empty_page_count
        /
        max(
            result.page_count,
            1,
        )

    )

    return (

        result.is_scanned

        or

        empty_ratio >= threshold

    )


# ============================================================
# OCR HANDOFF INFORMATION
# ============================================================

def get_ocr_handoff(
    result: PDFLoadResult,
) -> Dict[str, Any]:

    return {

        "required":
            should_use_ocr(
                result
            ),

        "page_numbers":
            find_scanned_pages(
                result
            ),

        "page_count":
            result.page_count,

        "scanned":
            result.is_scanned,

        "empty_pages":
            result.empty_page_count,

    }


# ============================================================
# LOAD PDF DIRECTORY
# ============================================================

def load_pdf_directory(
    directory: Union[
        str,
        Path,
    ],
    recursive: bool = True,
) -> List[PDFLoadResult]:

    path = Path(
        directory
    )

    if not path.exists():

        raise FileNotFoundError(

            f"Directory does not exist: {path}"

        )

    if not path.is_dir():

        raise ValueError(

            f"Not a directory: {path}"

        )

    if recursive:

        files = path.rglob(
            "*.pdf"
        )

    else:

        files = path.glob(
            "*.pdf"
        )

    results = []

    for file_path in sorted(
        files
    ):

        try:

            results.append(

                load_pdf(
                    file_path
                )

            )

        except Exception as exc:

            logger.exception(

                "Failed loading %s",

                file_path,

            )

            results.append(

                PDFLoadResult(

                    success=False,

                    error=str(
                        exc
                    ),

                )

            )

    return results


# ============================================================
# BATCH LOAD
# ============================================================

def batch_load_pdfs(
    file_paths: Iterable[
        Union[
            str,
            Path,
        ]
    ],
) -> List[PDFLoadResult]:

    results = []

    for file_path in file_paths:

        try:

            results.append(

                load_pdf(
                    file_path
                )

            )

        except Exception as exc:

            logger.exception(

                "Batch PDF loading failed: %s",

                file_path,

            )

            results.append(

                PDFLoadResult(

                    success=False,

                    error=str(
                        exc
                    ),

                )

            )

    return results


# ============================================================
# COMBINE RESULTS
# ============================================================

def combine_results(
    results: Sequence[
        PDFLoadResult
    ],
) -> PDFLoadResult:

    documents = []

    metadata = {

        "source_count":
            len(
                results
            ),

    }

    warnings = []

    success = True

    errors = []

    for result in results:

        documents.extend(
            result.documents
        )

        warnings.extend(
            result.warnings
        )

        if not result.success:

            success = False

            if result.error:

                errors.append(
                    result.error
                )

    page_count = len(
        documents
    )

    extracted_page_count = sum(

        1

        for document
        in documents

        if clean_text(
            document.text
        )

    )

    empty_page_count = (

        page_count
        -
        extracted_page_count

    )

    is_scanned = (

        any(

            document.is_scanned

            for document
            in documents

        )

    )

    return PDFLoadResult(

        documents=documents,

        metadata=metadata,

        page_count=page_count,

        extracted_page_count=extracted_page_count,

        empty_page_count=empty_page_count,

        is_scanned=is_scanned,

        success=success,

        error=(

            "; ".join(
                errors
            )

            if errors

            else None

        ),

        warnings=warnings,

    )


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# PUBLIC API + VALIDATION + SELF TEST
# ============================================================


# ============================================================
# VALIDATE LOAD RESULT
# ============================================================

def validate_load_result(
    result: PDFLoadResult,
) -> Dict[str, Any]:

    errors = []

    warnings = []

    if not isinstance(
        result,
        PDFLoadResult,
    ):

        return {

            "valid":
                False,

            "errors": [
                "Invalid PDFLoadResult."
            ],

            "warnings": [],

        }

    if not result.success:

        errors.append(

            result.error
            or
            "PDF loading failed."

        )

    if result.page_count < 0:

        errors.append(

            "Page count cannot be negative."

        )

    if result.extracted_page_count < 0:

        errors.append(

            "Extracted page count cannot be negative."

        )

    if result.empty_page_count < 0:

        errors.append(

            "Empty page count cannot be negative."

        )

    if (

        result.extracted_page_count
        +
        result.empty_page_count
        >
        result.page_count

    ):

        errors.append(

            "Page statistics are inconsistent."

        )

    if result.is_scanned:

        warnings.append(

            "OCR may be required for this PDF."

        )

    warnings.extend(
        result.warnings
    )

    return {

        "valid":
            len(errors) == 0,

        "errors":
            list(
                dict.fromkeys(
                    errors
                )
            ),

        "warnings":
            list(
                dict.fromkeys(
                    warnings
                )
            ),

    }


# ============================================================
# LOADER SUMMARY
# ============================================================

def loader_summary(
    result: PDFLoadResult,
) -> Dict[str, Any]:

    statistics = document_statistics(
        result
    )

    return {

        "loader_version":
            PDF_LOADER_VERSION,

        "success":
            result.success,

        "page_count":
            result.page_count,

        "extracted_page_count":
            result.extracted_page_count,

        "empty_page_count":
            result.empty_page_count,

        "is_scanned":
            result.is_scanned,

        "total_words":
            statistics[
                "total_words"
            ],

        "total_characters":
            statistics[
                "total_characters"
            ],

        "ocr_required":
            should_use_ocr(
                result
            ),

        "warnings":
            result.warnings,

        "error":
            result.error,

    }


# ============================================================
# GENERIC LOAD FUNCTION
# ============================================================

def load(
    source: Union[
        str,
        Path,
        bytes,
        Any,
    ],
    filename: str = "document.pdf",
) -> PDFLoadResult:

    # --------------------------------------------------------
    # Path
    # --------------------------------------------------------

    if isinstance(
        source,
        (
            str,
            Path,
        ),
    ):

        return load_pdf(
            source
        )

    # --------------------------------------------------------
    # Bytes
    # --------------------------------------------------------

    if isinstance(
        source,
        bytes,
    ):

        return load_pdf_bytes(

            source,

            filename=filename,

        )

    # --------------------------------------------------------
    # File-like object
    # --------------------------------------------------------

    if hasattr(
        source,
        "read",
    ):

        return load_pdf_stream(

            source,

            filename=filename,

        )

    raise TypeError(

        "Unsupported PDF source. Expected a path, "
        "bytes, or file-like object."

    )


# ============================================================
# PUBLIC CAPABILITIES
# ============================================================

PDF_LOADER_CAPABILITIES = [

    "pdf_file_loading",

    "pdf_bytes_loading",

    "pdf_stream_loading",

    "page_level_extraction",

    "pdf_metadata_extraction",

    "text_cleaning",

    "scanned_pdf_detection",

    "ocr_handoff",

    "page_statistics",

    "document_statistics",

    "langchain_document_conversion",

    "batch_pdf_loading",

    "directory_pdf_loading",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "PDF_LOADER_VERSION",

    # Models
    "PDFDocument",

    "PDFLoadResult",

    # Utilities
    "clean_text",

    "normalize_filename",

    "normalize_source",

    "is_pymupdf_available",

    "require_pymupdf",

    # Validation
    "validate_pdf_path",

    "validate_pdf_bytes",

    # Metadata
    "extract_metadata",

    "detect_scanned_pdf",

    # Extraction
    "extract_page",

    "extract_pages",

    "extract_page_range",

    # Loading
    "open_pdf",

    "load_pdf",

    "load_pdf_strict",

    "open_pdf_bytes",

    "load_pdf_bytes",

    "load_pdf_stream",

    "load",

    # Text
    "get_page_text",

    "get_all_text",

    "get_non_empty_pages",

    "get_empty_pages",

    # Statistics
    "page_statistics",

    "document_statistics",

    "loader_summary",

    # RAG
    "page_to_dict",

    "page_to_langchain_document",

    "to_langchain_documents",

    "to_document_dicts",

    # OCR
    "find_scanned_pages",

    "should_use_ocr",

    "get_ocr_handoff",

    # Batch
    "load_pdf_directory",

    "batch_load_pdfs",

    "combine_results",

    # Validation
    "validate_load_result",

    # Capabilities
    "PDF_LOADER_CAPABILITIES",

]


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    import sys

    print(
        "\n"
        "============================================"
    )

    print(
        "PDF LOADER SELF TEST"
    )

    print(
        "============================================"
    )

    print(
        "\nPyMuPDF available:"
    )

    print(
        is_pymupdf_available()
    )

    # --------------------------------------------------------
    # Test text cleaning
    # --------------------------------------------------------

    sample_text = """

        This is     a sample PDF text.


        It contains     excessive spaces.

        And multiple blank lines.

    """

    cleaned = clean_text(
        sample_text
    )

    print(
        "\nCleaned Text:"
    )

    print(
        cleaned
    )

    # --------------------------------------------------------
    # Test model creation
    # --------------------------------------------------------

    sample_page = PDFDocument(

        text="Sample PDF page text.",

        metadata={

            "author":
                "Demo",

        },

        page_number=1,

        source="demo",

        filename="demo.pdf",

        file_path="",

        page_count=1,

        is_scanned=False,

        extraction_method="pymupdf",

    )

    sample_result = PDFLoadResult(

        documents=[
            sample_page
        ],

        metadata={

            "title":
                "Demo PDF",

        },

        page_count=1,

        extracted_page_count=1,

        empty_page_count=0,

        is_scanned=False,

        success=True,

    )

    # --------------------------------------------------------
    # Test statistics
    # --------------------------------------------------------

    print(
        "\nPage Statistics:"
    )

    print(
        page_statistics(
            sample_page
        )
    )

    print(
        "\nDocument Statistics:"
    )

    print(
        document_statistics(
            sample_result
        )
    )

    # --------------------------------------------------------
    # Test summary
    # --------------------------------------------------------

    print(
        "\nLoader Summary:"
    )

    print(
        loader_summary(
            sample_result
        )
    )

    # --------------------------------------------------------
    # Test validation
    # --------------------------------------------------------

    print(
        "\nValidation:"
    )

    print(
        validate_load_result(
            sample_result
        )
    )

    # --------------------------------------------------------
    # Test document conversion
    # --------------------------------------------------------

    print(
        "\nDocument Dict:"
    )

    print(
        page_to_dict(
            sample_page
        )
    )

    # --------------------------------------------------------
    # Optional actual PDF
    # --------------------------------------------------------

    if len(sys.argv) > 1:

        pdf_path = sys.argv[1]

        print(
            "\nLoading:"
        )

        print(
            pdf_path
        )

        result = load_pdf(
            pdf_path
        )

        print(
            "\nResult:"
        )

        print(
            loader_summary(
                result
            )
        )

        print(
            "\nOCR Handoff:"
        )

        print(
            get_ocr_handoff(
                result
            )
        )

        print(
            "\nExtracted Text Preview:"
        )

        print(

            get_all_text(
                result
            )[:3000]

        )

    print(
        "\n============================================"
    )

    print(
        "PDF LOADER TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF rag/pdf_loader.py
# ============================================================
