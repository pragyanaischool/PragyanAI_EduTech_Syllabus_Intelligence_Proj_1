# ============================================================
# rag/ocr_loader.py
# CHUNK 1/10
#
# OCR DOCUMENT LOADER
#
# Purpose:
#   Extract text from scanned PDFs and images using OCR.
#
# Supports:
#   - PNG / JPG / JPEG / WEBP / TIFF / BMP
#   - Scanned PDF pages
#   - Tesseract OCR
#   - PyMuPDF PDF rendering
#   - PIL image processing
#   - OpenCV preprocessing (optional)
#   - Page-level OCR documents
#   - OCR confidence
#   - Bounding-box information
#   - RAG-ready document conversion
#
# Recommended packages:
#
#   pip install pytesseract pillow pymupdf
#
# Optional:
#
#   pip install opencv-python
#
# System dependency:
#
#   Tesseract OCR
#
# ============================================================

from __future__ import annotations

import io
import logging
import re

from dataclasses import dataclass, field

from pathlib import Path

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# VERSION
# ============================================================

OCR_LOADER_VERSION = "1.0.0"


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_LANGUAGE = "eng"

DEFAULT_DPI = 200

DEFAULT_MIN_TEXT_LENGTH = 5

DEFAULT_CONFIDENCE_THRESHOLD = 40.0

DEFAULT_MAX_IMAGE_DIMENSION = 5000


# ============================================================
# SUPPORTED IMAGE EXTENSIONS
# ============================================================

SUPPORTED_IMAGE_EXTENSIONS = {

    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".tif",
    ".tiff",
    ".bmp",

}


# ============================================================
# OPTIONAL IMPORTS
# ============================================================

try:

    import pytesseract

except ImportError:

    pytesseract = None


try:

    from PIL import Image

    from PIL import ImageEnhance

    from PIL import ImageFilter

    from PIL import ImageOps

except ImportError:

    Image = None

    ImageEnhance = None

    ImageFilter = None

    ImageOps = None


try:

    import fitz

except ImportError:

    fitz = None


try:

    import cv2

except ImportError:

    cv2 = None


try:

    import numpy as np

except ImportError:

    np = None


# ============================================================
# OCR BLOCK
# ============================================================

@dataclass
class OCRBlock:

    text: str = ""

    confidence: float = 0.0

    left: int = 0

    top: int = 0

    width: int = 0

    height: int = 0

    block_number: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# OCR DOCUMENT
# ============================================================

@dataclass
class OCRDocument:

    text: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    source: str = ""

    filename: str = ""

    file_path: str = ""

    page_number: int = 0

    page_count: int = 0

    confidence: float = 0.0

    language: str = DEFAULT_LANGUAGE

    extraction_method: str = "tesseract"

    is_scanned: bool = True

    blocks: List[OCRBlock] = field(
        default_factory=list
    )

    error: Optional[str] = None


# ============================================================
# OCR RESULT
# ============================================================

@dataclass
class OCRLoadResult:

    documents: List[OCRDocument] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    page_count: int = 0

    successful_pages: int = 0

    failed_pages: int = 0

    average_confidence: float = 0.0

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
# DEPENDENCY CHECKS + TEXT UTILITIES
# ============================================================


# ============================================================
# CHECK TESSERACT
# ============================================================

def is_tesseract_available() -> bool:

    return pytesseract is not None


# ============================================================
# CHECK PIL
# ============================================================

def is_pillow_available() -> bool:

    return Image is not None


# ============================================================
# CHECK PYMUPDF
# ============================================================

def is_pymupdf_available() -> bool:

    return fitz is not None


# ============================================================
# CHECK OPENCV
# ============================================================

def is_opencv_available() -> bool:

    return cv2 is not None


# ============================================================
# REQUIRE TESSERACT
# ============================================================

def require_tesseract() -> None:

    if pytesseract is None:

        raise ImportError(

            "pytesseract is required for OCR. "
            "Install using: pip install pytesseract"

        )


# ============================================================
# REQUIRE PIL
# ============================================================

def require_pillow() -> None:

    if Image is None:

        raise ImportError(

            "Pillow is required for image OCR. "
            "Install using: pip install pillow"

        )


# ============================================================
# REQUIRE PYMUPDF
# ============================================================

def require_pymupdf() -> None:

    if fitz is None:

        raise ImportError(

            "PyMuPDF is required for scanned PDF OCR. "
            "Install using: pip install pymupdf"

        )


# ============================================================
# CLEAN OCR TEXT
# ============================================================

def clean_text(
    text: Any,
) -> str:

    if text is None:

        return ""

    text = str(
        text
    )

    text = text.replace(
        "\x00",
        "",
    )

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    # Remove spaces at line ends.
    text = re.sub(
        r"[ \t]+\n",
        "\n",
        text,
    )

    # Normalize multiple spaces.
    text = re.sub(
        r"[ \t]{2,}",
        " ",
        text,
    )

    # Normalize excessive blank lines.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


# ============================================================
# NORMALIZE LANGUAGE
# ============================================================

def normalize_language(
    language: Optional[str],
) -> str:

    if not language:

        return DEFAULT_LANGUAGE

    language = str(
        language
    ).strip()

    return language or DEFAULT_LANGUAGE


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
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# IMAGE LOADING + PREPROCESSING
# ============================================================


# ============================================================
# VALIDATE IMAGE PATH
# ============================================================

def validate_image_path(
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

            f"Image file does not exist: {path}"

        )

    if not path.is_file():

        raise ValueError(

            f"Path is not a file: {path}"

        )

    if path.suffix.lower() not in (
        SUPPORTED_IMAGE_EXTENSIONS
    ):

        raise ValueError(

            f"Unsupported image type: {path.suffix}"

        )

    return path


# ============================================================
# OPEN IMAGE
# ============================================================

def open_image(
    file_path: Union[
        str,
        Path,
    ],
) -> Any:

    require_pillow()

    path = validate_image_path(
        file_path
    )

    try:

        image = Image.open(
            path
        )

        # Make an independent copy so the underlying
        # file handle can be closed safely.
        image = image.copy()

        return image

    except Exception as exc:

        logger.exception(

            "Unable to open image: %s",

            path,

        )

        raise RuntimeError(

            f"Unable to open image: {path}"

        ) from exc


# ============================================================
# OPEN IMAGE BYTES
# ============================================================

def open_image_bytes(
    data: bytes,
) -> Any:

    require_pillow()

    if not data:

        raise ValueError(
            "Image data is empty."
        )

    try:

        image = Image.open(
            io.BytesIO(data)
        )

        return image.copy()

    except Exception as exc:

        raise RuntimeError(

            "Unable to open image from bytes."

        ) from exc


# ============================================================
# RESIZE IMAGE
# ============================================================

def resize_image(
    image: Any,
    max_dimension: int = DEFAULT_MAX_IMAGE_DIMENSION,
) -> Any:

    require_pillow()

    if image is None:

        raise ValueError(
            "Image cannot be None."
        )

    width, height = image.size

    largest = max(
        width,
        height,
    )

    if largest <= max_dimension:

        return image

    scale = (
        max_dimension
        /
        largest
    )

    new_size = (

        max(
            1,
            int(
                width * scale
            ),
        ),

        max(
            1,
            int(
                height * scale
            ),
        ),

    )

    return image.resize(
        new_size,
        Image.Resampling.LANCZOS,
    )


# ============================================================
# BASIC IMAGE PREPROCESSING
# ============================================================

def preprocess_image(
    image: Any,
    grayscale: bool = True,
    autocontrast: bool = True,
    sharpen: bool = True,
    denoise: bool = False,
    threshold: bool = False,
    resize: bool = True,
    max_dimension: int = DEFAULT_MAX_IMAGE_DIMENSION,
) -> Any:

    require_pillow()

    if image is None:

        raise ValueError(
            "Image cannot be None."
        )

    processed = image.copy()

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    if resize:

        processed = resize_image(

            processed,

            max_dimension=max_dimension,

        )

    # --------------------------------------------------------
    # Grayscale
    # --------------------------------------------------------

    if grayscale:

        processed = processed.convert(
            "L"
        )

    # --------------------------------------------------------
    # Auto contrast
    # --------------------------------------------------------

    if autocontrast:

        try:

            processed = ImageOps.autocontrast(
                processed
            )

        except Exception:

            pass

    # --------------------------------------------------------
    # Denoise
    # --------------------------------------------------------

    if denoise:

        try:

            processed = processed.filter(
                ImageFilter.MedianFilter(
                    size=3
                )
            )

        except Exception:

            pass

    # --------------------------------------------------------
    # Sharpen
    # --------------------------------------------------------

    if sharpen:

        try:

            processed = processed.filter(
                ImageFilter.SHARPEN
            )

        except Exception:

            pass

    # --------------------------------------------------------
    # Binary threshold
    # --------------------------------------------------------

    if threshold:

        processed = processed.point(

            lambda pixel:
            255
            if pixel > 180
            else 0

        )

    return processed


# ============================================================
# OPENCV PREPROCESSING
# ============================================================

def preprocess_image_opencv(
    image: Any,
    threshold: bool = False,
) -> Any:

    if cv2 is None or np is None:

        logger.warning(

            "OpenCV preprocessing requested but "
            "opencv-python/numpy is unavailable."

        )

        return preprocess_image(
            image
        )

    require_pillow()

    # PIL → NumPy
    array = np.array(
        image
    )

    # --------------------------------------------------------
    # Grayscale
    # --------------------------------------------------------

    if len(
        array.shape
    ) == 3:

        gray = cv2.cvtColor(

            array,

            cv2.COLOR_RGB2GRAY,

        )

    else:

        gray = array

    # --------------------------------------------------------
    # Denoising
    # --------------------------------------------------------

    gray = cv2.GaussianBlur(

        gray,

        (
            3,
            3,
        ),

        0,

    )

    # --------------------------------------------------------
    # Adaptive threshold
    # --------------------------------------------------------

    if threshold:

        processed = cv2.adaptiveThreshold(

            gray,

            255,

            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

            cv2.THRESH_BINARY,

            11,

            2,

        )

    else:

        processed = gray

    return Image.fromarray(
        processed
    )


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# TESSERACT OCR
# ============================================================


# ============================================================
# OCR IMAGE
# ============================================================

def ocr_image(
    image: Any,
    language: str = DEFAULT_LANGUAGE,
    config: str = "",
) -> str:

    require_tesseract()

    require_pillow()

    language = normalize_language(
        language
    )

    try:

        text = pytesseract.image_to_string(

            image,

            lang=language,

            config=config,

        )

        return clean_text(
            text
        )

    except Exception as exc:

        logger.exception(
            "OCR text extraction failed."
        )

        raise RuntimeError(
            "Tesseract OCR failed."
        ) from exc


# ============================================================
# OCR DATA
# ============================================================

def ocr_image_data(
    image: Any,
    language: str = DEFAULT_LANGUAGE,
    config: str = "",
) -> Dict[str, Any]:

    require_tesseract()

    language = normalize_language(
        language
    )

    try:

        data = pytesseract.image_to_data(

            image,

            lang=language,

            config=config,

            output_type=pytesseract.Output.DICT,

        )

        return data

    except Exception as exc:

        logger.exception(
            "OCR data extraction failed."
        )

        raise RuntimeError(
            "Tesseract OCR data extraction failed."
        ) from exc


# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# OCR BLOCKS
# ============================================================

def extract_ocr_blocks(
    image: Any,
    language: str = DEFAULT_LANGUAGE,
    config: str = "",
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> List[OCRBlock]:

    data = ocr_image_data(

        image=image,

        language=language,

        config=config,

    )

    blocks = []

    texts = data.get(
        "text",
        [],
    )

    confidences = data.get(
        "conf",
        [],
    )

    lefts = data.get(
        "left",
        [],
    )

    tops = data.get(
        "top",
        [],
    )

    widths = data.get(
        "width",
        [],
    )

    heights = data.get(
        "height",
        [],
    )

    block_numbers = data.get(
        "block_num",
        [],
    )

    for index, raw_text in enumerate(
        texts
    ):

        text = clean_text(
            raw_text
        )

        confidence = safe_float(

            confidences[index]
            if index < len(
                confidences
            )
            else 0.0

        )

        if not text:

            continue

        if confidence < confidence_threshold:

            continue

        block = OCRBlock(

            text=text,

            confidence=confidence,

            left=int(

                safe_float(

                    lefts[index]
                    if index < len(
                        lefts
                    )
                    else 0

                )

            ),

            top=int(

                safe_float(

                    tops[index]
                    if index < len(
                        tops
                    )
                    else 0

                )

            ),

            width=int(

                safe_float(

                    widths[index]
                    if index < len(
                        widths
                    )
                    else 0

                )

            ),

            height=int(

                safe_float(

                    heights[index]
                    if index < len(
                        heights
                    )
                    else 0

                )

            ),

            block_number=int(

                safe_float(

                    block_numbers[index]
                    if index < len(
                        block_numbers
                    )
                    else 0

                )

            ),

            metadata={

                "ocr_index":
                    index,

            },

        )

        blocks.append(
            block
        )

    return blocks


# ============================================================
# AVERAGE CONFIDENCE
# ============================================================

def average_confidence(
    blocks: Sequence[OCRBlock],
) -> float:

    values = [

        block.confidence

        for block
        in blocks

        if block.confidence > 0

    ]

    if not values:

        return 0.0

    return round(

        sum(values)
        /
        len(values),

        2,

    )


# ============================================================
# BLOCKS TO TEXT
# ============================================================

def blocks_to_text(
    blocks: Sequence[OCRBlock],
) -> str:

    texts = [

        clean_text(
            block.text
        )

        for block
        in blocks

        if clean_text(
            block.text
        )

    ]

    return "\n".join(
        texts
    ).strip()


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# IMAGE OCR LOADER
# ============================================================


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(
    file_path: Union[
        str,
        Path,
    ],
    language: str = DEFAULT_LANGUAGE,
    preprocess: bool = True,
    use_opencv: bool = False,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> OCRLoadResult:

    path = validate_image_path(
        file_path
    )

    try:

        image = open_image(
            path
        )

        original_size = image.size

        # ----------------------------------------------------
        # Preprocessing
        # ----------------------------------------------------

        if preprocess:

            if use_opencv:

                image = preprocess_image_opencv(
                    image
                )

            else:

                image = preprocess_image(
                    image
                )

        # ----------------------------------------------------
        # OCR blocks
        # ----------------------------------------------------

        blocks = extract_ocr_blocks(

            image=image,

            language=language,

            confidence_threshold=confidence_threshold,

        )

        text = blocks_to_text(
            blocks
        )

        confidence = average_confidence(
            blocks
        )

        metadata = {

            "filename":
                path.name,

            "file_path":
                str(
                    path.resolve()
                ),

            "original_width":
                original_size[0],

            "original_height":
                original_size[1],

            "processed_width":
                image.size[0],

            "processed_height":
                image.size[1],

            "language":
                normalize_language(
                    language
                ),

            "confidence":
                confidence,

            "block_count":
                len(blocks),

        }

        document = OCRDocument(

            text=text,

            metadata=metadata,

            source=str(
                path
            ),

            filename=path.name,

            file_path=str(
                path.resolve()
            ),

            page_number=1,

            page_count=1,

            confidence=confidence,

            language=normalize_language(
                language
            ),

            extraction_method="tesseract",

            is_scanned=True,

            blocks=blocks,

        )

        warnings = []

        if not text:

            warnings.append(
                "OCR produced no text."
            )

        if confidence < confidence_threshold:

            warnings.append(

                "OCR confidence is below the configured threshold."

            )

        return OCRLoadResult(

            documents=[
                document
            ],

            metadata=metadata,

            page_count=1,

            successful_pages=1,

            failed_pages=0,

            average_confidence=confidence,

            success=True,

            warnings=warnings,

        )

    except Exception as exc:

        logger.exception(

            "Image OCR failed: %s",

            path,

        )

        return OCRLoadResult(

            documents=[],

            metadata={

                "filename":
                    path.name,

                "file_path":
                    str(path),

            },

            page_count=1,

            successful_pages=0,

            failed_pages=1,

            average_confidence=0.0,

            success=False,

            error=str(
                exc
            ),

        )


# ============================================================
# OCR IMAGE BYTES
# ============================================================

def load_image_bytes(
    data: bytes,
    filename: str = "image.png",
    source: str = "memory",
    language: str = DEFAULT_LANGUAGE,
    preprocess: bool = True,
    use_opencv: bool = False,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> OCRLoadResult:

    try:

        image = open_image_bytes(
            data
        )

        original_size = image.size

        if preprocess:

            if use_opencv:

                image = preprocess_image_opencv(
                    image
                )

            else:

                image = preprocess_image(
                    image
                )

        blocks = extract_ocr_blocks(

            image=image,

            language=language,

            confidence_threshold=confidence_threshold,

        )

        text = blocks_to_text(
            blocks
        )

        confidence = average_confidence(
            blocks
        )

        metadata = {

            "filename":
                normalize_filename(
                    filename
                ),

            "source":
                source,

            "original_width":
                original_size[0],

            "original_height":
                original_size[1],

            "language":
                normalize_language(
                    language
                ),

            "confidence":
                confidence,

            "block_count":
                len(blocks),

        }

        document = OCRDocument(

            text=text,

            metadata=metadata,

            source=source,

            filename=normalize_filename(
                filename
            ),

            file_path="",

            page_number=1,

            page_count=1,

            confidence=confidence,

            language=normalize_language(
                language
            ),

            extraction_method="tesseract",

            is_scanned=True,

            blocks=blocks,

        )

        return OCRLoadResult(

            documents=[
                document
            ],

            metadata=metadata,

            page_count=1,

            successful_pages=1,

            failed_pages=0,

            average_confidence=confidence,

            success=True,

            warnings=[],

        )

    except Exception as exc:

        logger.exception(
            "Image byte OCR failed."
        )

        return OCRLoadResult(

            success=False,

            error=str(
                exc
            ),

            page_count=1,

            failed_pages=1,

        )


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# SCANNED PDF OCR
# ============================================================


# ============================================================
# RENDER PDF PAGE
# ============================================================

def render_pdf_page(
    page: Any,
    dpi: int = DEFAULT_DPI,
) -> Any:

    require_pymupdf()

    require_pillow()

    if dpi <= 0:

        raise ValueError(
            "DPI must be greater than zero."
        )

    zoom = dpi / 72.0

    matrix = fitz.Matrix(
        zoom,
        zoom,
    )

    try:

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False,
        )

        image_bytes = pixmap.tobytes(
            "png"
        )

        image = Image.open(
            io.BytesIO(
                image_bytes
            )
        )

        return image.copy()

    except Exception as exc:

        logger.exception(
            "Failed to render PDF page."
        )

        raise RuntimeError(
            "Unable to render PDF page."
        ) from exc


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

    path = Path(
        file_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"PDF does not exist: {path}"
        )

    if path.suffix.lower() != ".pdf":

        raise ValueError(
            "Expected a PDF file."
        )

    try:

        return fitz.open(
            str(path)
        )

    except Exception as exc:

        raise RuntimeError(
            f"Unable to open PDF: {path}"
        ) from exc


# ============================================================
# OCR PDF PAGE
# ============================================================

def ocr_pdf_page(
    page: Any,
    page_number: int,
    page_count: int,
    source: str = "",
    filename: str = "",
    file_path: str = "",
    language: str = DEFAULT_LANGUAGE,
    dpi: int = DEFAULT_DPI,
    preprocess: bool = True,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> OCRDocument:

    try:

        image = render_pdf_page(

            page=page,

            dpi=dpi,

        )

        if preprocess:

            image = preprocess_image(
                image
            )

        blocks = extract_ocr_blocks(

            image=image,

            language=language,

            confidence_threshold=confidence_threshold,

        )

        text = blocks_to_text(
            blocks
        )

        confidence = average_confidence(
            blocks
        )

        metadata = {

            "page_number":
                page_number,

            "page_index":
                page_number - 1,

            "page_count":
                page_count,

            "dpi":
                dpi,

            "language":
                normalize_language(
                    language
                ),

            "confidence":
                confidence,

            "block_count":
                len(blocks),

        }

        return OCRDocument(

            text=text,

            metadata=metadata,

            source=source,

            filename=filename,

            file_path=file_path,

            page_number=page_number,

            page_count=page_count,

            confidence=confidence,

            language=normalize_language(
                language
            ),

            extraction_method="tesseract-pdf-render",

            is_scanned=True,

            blocks=blocks,

        )

    except Exception as exc:

        logger.exception(

            "OCR failed for PDF page %s.",

            page_number,

        )

        return OCRDocument(

            text="",

            metadata={

                "page_number":
                    page_number,

            },

            source=source,

            filename=filename,

            file_path=file_path,

            page_number=page_number,

            page_count=page_count,

            confidence=0.0,

            language=normalize_language(
                language
            ),

            extraction_method="tesseract-pdf-render",

            is_scanned=True,

            blocks=[],

            error=str(
                exc
            ),

        )


# ============================================================
# LOAD SCANNED PDF
# ============================================================

def load_scanned_pdf(
    file_path: Union[
        str,
        Path,
    ],
    language: str = DEFAULT_LANGUAGE,
    dpi: int = DEFAULT_DPI,
    preprocess: bool = True,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> OCRLoadResult:

    path = Path(
        file_path
    )

    pdf = None

    try:

        pdf = open_pdf(
            path
        )

        page_count = len(
            pdf
        )

        documents = []

        warnings = []

        for index in range(
            page_count
        ):

            page_number = index + 1

            page = pdf[
                index
            ]

            document = ocr_pdf_page(

                page=page,

                page_number=page_number,

                page_count=page_count,

                source=str(
                    path
                ),

                filename=path.name,

                file_path=str(
                    path.resolve()
                ),

                language=language,

                dpi=dpi,

                preprocess=preprocess,

                confidence_threshold=confidence_threshold,

            )

            documents.append(
                document
            )

            if document.error:

                warnings.append(

                    f"Page {page_number}: "
                    f"{document.error}"

                )

        successful = sum(

            1

            for document
            in documents

            if (
                not document.error
                and
                document.text
            )

        )

        failed = (

            page_count
            -
            successful

        )

        confidence_values = [

            document.confidence

            for document
            in documents

            if document.confidence > 0

        ]

        avg_confidence = (

            sum(
                confidence_values
            )
            /
            len(
                confidence_values
            )

            if confidence_values

            else 0.0

        )

        return OCRLoadResult(

            documents=documents,

            metadata={

                "filename":
                    path.name,

                "file_path":
                    str(
                        path.resolve()
                    ),

                "dpi":
                    dpi,

                "language":
                    normalize_language(
                        language
                    ),

            },

            page_count=page_count,

            successful_pages=successful,

            failed_pages=failed,

            average_confidence=round(

                avg_confidence,

                2,

            ),

            success=failed == 0,

            error=None,

            warnings=warnings,

        )

    except Exception as exc:

        logger.exception(
            "Scanned PDF OCR failed."
        )

        return OCRLoadResult(

            documents=[],

            metadata={},

            page_count=0,

            successful_pages=0,

            failed_pages=0,

            average_confidence=0.0,

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
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# PDF BYTES + AUTOMATIC OCR
# ============================================================


# ============================================================
# LOAD SCANNED PDF BYTES
# ============================================================

def load_scanned_pdf_bytes(
    data: bytes,
    filename: str = "document.pdf",
    source: str = "memory",
    language: str = DEFAULT_LANGUAGE,
    dpi: int = DEFAULT_DPI,
    preprocess: bool = True,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> OCRLoadResult:

    require_pymupdf()

    if not data:

        raise ValueError(
            "PDF data is empty."
        )

    pdf = None

    try:

        pdf = fitz.open(

            stream=data,

            filetype="pdf",

        )

        page_count = len(
            pdf
        )

        documents = []

        warnings = []

        for index in range(
            page_count
        ):

            page_number = index + 1

            document = ocr_pdf_page(

                page=pdf[index],

                page_number=page_number,

                page_count=page_count,

                source=source,

                filename=normalize_filename(
                    filename
                ),

                file_path="",

                language=language,

                dpi=dpi,

                preprocess=preprocess,

                confidence_threshold=confidence_threshold,

            )

            documents.append(
                document
            )

            if document.error:

                warnings.append(

                    f"Page {page_number}: "
                    f"{document.error}"

                )

        successful = sum(

            1

            for document
            in documents

            if (
                document.text
                and
                not document.error
            )

        )

        failed = (

            page_count
            -
            successful

        )

        values = [

            document.confidence

            for document
            in documents

            if document.confidence > 0

        ]

        avg_confidence = (

            sum(values)
            /
            len(values)

            if values

            else 0.0

        )

        return OCRLoadResult(

            documents=documents,

            metadata={

                "filename":
                    normalize_filename(
                        filename
                    ),

                "source":
                    source,

                "dpi":
                    dpi,

                "language":
                    normalize_language(
                        language
                    ),

            },

            page_count=page_count,

            successful_pages=successful,

            failed_pages=failed,

            average_confidence=round(

                avg_confidence,

                2,

            ),

            success=failed == 0,

            warnings=warnings,

        )

    except Exception as exc:

        logger.exception(
            "PDF byte OCR failed."
        )

        return OCRLoadResult(

            success=False,

            error=str(
                exc
            ),

        )

    finally:

        if pdf is not None:

            try:

                pdf.close()

            except Exception:

                pass


# ============================================================
# AUTOMATIC OCR FOR PDF OR IMAGE
# ============================================================

def load(
    source: Union[
        str,
        Path,
        bytes,
        Any,
    ],
    filename: str = "",
    language: str = DEFAULT_LANGUAGE,
    dpi: int = DEFAULT_DPI,
    preprocess: bool = True,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> OCRLoadResult:

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

        path = Path(
            source
        )

        suffix = path.suffix.lower()

        if suffix == ".pdf":

            return load_scanned_pdf(

                path,

                language=language,

                dpi=dpi,

                preprocess=preprocess,

                confidence_threshold=confidence_threshold,

            )

        if suffix in SUPPORTED_IMAGE_EXTENSIONS:

            return load_image(

                path,

                language=language,

                preprocess=preprocess,

                confidence_threshold=confidence_threshold,

            )

        raise ValueError(

            f"Unsupported OCR source: {suffix}"

        )

    # --------------------------------------------------------
    # Bytes
    # --------------------------------------------------------

    if isinstance(
        source,
        bytes,
    ):

        name = (
            filename.lower()
            if filename
            else ""
        )

        if name.endswith(
            ".pdf"
        ):

            return load_scanned_pdf_bytes(

                source,

                filename=filename,

                language=language,

                dpi=dpi,

                preprocess=preprocess,

                confidence_threshold=confidence_threshold,

            )

        return load_image_bytes(

            source,

            filename=filename
            or
            "image.png",

            language=language,

            preprocess=preprocess,

            confidence_threshold=confidence_threshold,

        )

    # --------------------------------------------------------
    # Stream
    # --------------------------------------------------------

    if hasattr(
        source,
        "read",
    ):

        data = source.read()

        return load(

            data,

            filename=filename,

            language=language,

            dpi=dpi,

            preprocess=preprocess,

            confidence_threshold=confidence_threshold,

        )

    raise TypeError(

        "Unsupported OCR source. Expected path, bytes, "
        "or file-like object."

    )


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# RAG / LANGCHAIN CONVERSION
# ============================================================


# ============================================================
# OPTIONAL LANGCHAIN
# ============================================================

try:

    from langchain_core.documents import Document as LangChainDocument

except ImportError:

    LangChainDocument = None


# ============================================================
# OCR DOCUMENT → DICT
# ============================================================

def document_to_dict(
    document: OCRDocument,
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

        "confidence":
            document.confidence,

        "language":
            document.language,

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
# OCR DOCUMENT → LANGCHAIN
# ============================================================

def document_to_langchain(
    document: OCRDocument,
) -> Any:

    if LangChainDocument is None:

        raise ImportError(

            "langchain-core is required. "
            "Install using: pip install langchain-core"

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

        "confidence":
            document.confidence,

        "language":
            document.language,

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
    result: OCRLoadResult,
    skip_empty: bool = True,
) -> List[Any]:

    documents = []

    for document in result.documents:

        if (
            skip_empty
            and
            not clean_text(
                document.text
            )
        ):

            continue

        documents.append(

            document_to_langchain(
                document
            )

        )

    return documents


# ============================================================
# RESULT → DICTS
# ============================================================

def to_document_dicts(
    result: OCRLoadResult,
    skip_empty: bool = True,
) -> List[Dict[str, Any]]:

    documents = []

    for document in result.documents:

        if (
            skip_empty
            and
            not clean_text(
                document.text
            )
        ):

            continue

        documents.append(

            document_to_dict(
                document
            )

        )

    return documents


# ============================================================
# BLOCK → DICT
# ============================================================

def block_to_dict(
    block: OCRBlock,
) -> Dict[str, Any]:

    metadata = dict(
        block.metadata
    )

    metadata.update({

        "confidence":
            block.confidence,

        "left":
            block.left,

        "top":
            block.top,

        "width":
            block.width,

        "height":
            block.height,

        "block_number":
            block.block_number,

    })

    return {

        "text":
            block.text,

        "confidence":
            block.confidence,

        "bbox": [

            block.left,

            block.top,

            block.width,

            block.height,

        ],

        "metadata":
            metadata,

    }


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# BATCH PROCESSING + STATISTICS
# ============================================================


# ============================================================
# DOCUMENT STATISTICS
# ============================================================

def document_statistics(
    result: OCRLoadResult,
) -> Dict[str, Any]:

    total_characters = 0

    total_words = 0

    confidence_values = []

    block_count = 0

    for document in result.documents:

        text = clean_text(
            document.text
        )

        total_characters += len(
            text
        )

        total_words += len(
            text.split()
        )

        if document.confidence > 0:

            confidence_values.append(
                document.confidence
            )

        block_count += len(
            document.blocks
        )

    average_confidence_value = (

        sum(
            confidence_values
        )
        /
        len(
            confidence_values
        )

        if confidence_values

        else 0.0

    )

    return {

        "page_count":
            result.page_count,

        "successful_pages":
            result.successful_pages,

        "failed_pages":
            result.failed_pages,

        "document_count":
            len(
                result.documents
            ),

        "block_count":
            block_count,

        "total_characters":
            total_characters,

        "total_words":
            total_words,

        "average_confidence":
            round(
                average_confidence_value,
                2,
            ),

    }


# ============================================================
# LOAD IMAGE DIRECTORY
# ============================================================

def load_image_directory(
    directory: Union[
        str,
        Path,
    ],
    recursive: bool = True,
    language: str = DEFAULT_LANGUAGE,
) -> List[OCRLoadResult]:

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

    files = []

    for extension in SUPPORTED_IMAGE_EXTENSIONS:

        if recursive:

            files.extend(
                path.rglob(
                    f"*{extension}"
                )
            )

        else:

            files.extend(
                path.glob(
                    f"*{extension}"
                )
            )

    results = []

    for file_path in sorted(
        set(files)
    ):

        try:

            results.append(

                load_image(

                    file_path,

                    language=language,

                )

            )

        except Exception as exc:

            logger.exception(

                "Failed OCR for %s",

                file_path,

            )

            results.append(

                OCRLoadResult(

                    success=False,

                    error=str(
                        exc
                    ),

                )

            )

    return results


# ============================================================
# BATCH OCR
# ============================================================

def batch_load(
    sources: Iterable[
        Union[
            str,
            Path,
            bytes,
        ]
    ],
    language: str = DEFAULT_LANGUAGE,
) -> List[OCRLoadResult]:

    results = []

    for source in sources:

        try:

            results.append(

                load(

                    source,

                    language=language,

                )

            )

        except Exception as exc:

            logger.exception(
                "Batch OCR failed."
            )

            results.append(

                OCRLoadResult(

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
        OCRLoadResult
    ],
) -> OCRLoadResult:

    documents = []

    metadata = {

        "source_count":
            len(
                results
            ),

    }

    warnings = []

    errors = []

    successful_pages = 0

    failed_pages = 0

    page_count = 0

    confidence_values = []

    success = True

    for result in results:

        documents.extend(
            result.documents
        )

        warnings.extend(
            result.warnings
        )

        successful_pages += (
            result.successful_pages
        )

        failed_pages += (
            result.failed_pages
        )

        page_count += (
            result.page_count
        )

        if result.average_confidence > 0:

            confidence_values.append(

                result.average_confidence

            )

        if not result.success:

            success = False

            if result.error:

                errors.append(
                    result.error
                )

    average = (

        sum(
            confidence_values
        )
        /
        len(
            confidence_values
        )

        if confidence_values

        else 0.0

    )

    return OCRLoadResult(

        documents=documents,

        metadata=metadata,

        page_count=page_count,

        successful_pages=successful_pages,

        failed_pages=failed_pages,

        average_confidence=round(
            average,
            2,
        ),

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
# VALIDATE RESULT
# ============================================================

def validate_load_result(
    result: OCRLoadResult,
) -> Dict[str, Any]:

    errors = []

    warnings = []

    if not isinstance(
        result,
        OCRLoadResult,
    ):

        return {

            "valid":
                False,

            "errors": [
                "Invalid OCRLoadResult."
            ],

            "warnings": [],

        }

    if not result.success:

        errors.append(

            result.error
            or
            "OCR loading failed."

        )

    if result.page_count < 0:

        errors.append(
            "Page count cannot be negative."
        )

    if result.successful_pages < 0:

        errors.append(
            "Successful page count cannot be negative."
        )

    if result.failed_pages < 0:

        errors.append(
            "Failed page count cannot be negative."
        )

    if (

        result.successful_pages
        +
        result.failed_pages
        >
        result.page_count

    ):

        errors.append(

            "OCR page statistics are inconsistent."

        )

    if (
        result.average_confidence < 0
        or
        result.average_confidence > 100
    ):

        errors.append(

            "OCR confidence must be between 0 and 100."

        )

    if (
        result.average_confidence > 0
        and
        result.average_confidence < 40
    ):

        warnings.append(

            "Average OCR confidence is low."

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
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# SUMMARY + GENERIC API + EXPORTS + SELF TEST
# ============================================================


# ============================================================
# LOADER SUMMARY
# ============================================================

def loader_summary(
    result: OCRLoadResult,
) -> Dict[str, Any]:

    statistics = document_statistics(
        result
    )

    return {

        "loader_version":
            OCR_LOADER_VERSION,

        "success":
            result.success,

        "page_count":
            result.page_count,

        "successful_pages":
            result.successful_pages,

        "failed_pages":
            result.failed_pages,

        "document_count":
            len(
                result.documents
            ),

        "average_confidence":
            result.average_confidence,

        "total_words":
            statistics[
                "total_words"
            ],

        "total_characters":
            statistics[
                "total_characters"
            ],

        "warnings":
            result.warnings,

        "error":
            result.error,

    }


# ============================================================
# OCR CAPABILITIES
# ============================================================

OCR_LOADER_CAPABILITIES = [

    "image_ocr",

    "pdf_ocr",

    "scanned_pdf_ocr",

    "ocr_confidence",

    "ocr_bounding_boxes",

    "image_preprocessing",

    "opencv_preprocessing",

    "tesseract",

    "pdf_rendering",

    "bytes_loading",

    "stream_loading",

    "batch_processing",

    "directory_processing",

    "langchain_conversion",

    "rag_document_conversion",

]


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "OCR_LOADER_VERSION",

    # Models
    "OCRBlock",

    "OCRDocument",

    "OCRLoadResult",

    # Dependency checks
    "is_tesseract_available",

    "is_pillow_available",

    "is_pymupdf_available",

    "is_opencv_available",

    "require_tesseract",

    "require_pillow",

    "require_pymupdf",

    # Utilities
    "clean_text",

    "normalize_language",

    "normalize_filename",

    # Image
    "validate_image_path",

    "open_image",

    "open_image_bytes",

    "resize_image",

    "preprocess_image",

    "preprocess_image_opencv",

    # OCR
    "ocr_image",

    "ocr_image_data",

    "extract_ocr_blocks",

    "average_confidence",

    "blocks_to_text",

    # Image loading
    "load_image",

    "load_image_bytes",

    # PDF
    "render_pdf_page",

    "open_pdf",

    "ocr_pdf_page",

    "load_scanned_pdf",

    "load_scanned_pdf_bytes",

    # Generic
    "load",

    # RAG
    "document_to_dict",

    "document_to_langchain",

    "to_langchain_documents",

    "to_document_dicts",

    "block_to_dict",

    # Statistics
    "document_statistics",

    "loader_summary",

    # Batch
    "load_image_directory",

    "batch_load",

    "combine_results",

    # Validation
    "validate_load_result",

    # Capabilities
    "OCR_LOADER_CAPABILITIES",

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
        "OCR LOADER SELF TEST"
    )

    print(
        "============================================"
    )

    # --------------------------------------------------------
    # Dependency status
    # --------------------------------------------------------

    print(
        "\nTesseract available:"
    )

    print(
        is_tesseract_available()
    )

    print(
        "\nPillow available:"
    )

    print(
        is_pillow_available()
    )

    print(
        "\nPyMuPDF available:"
    )

    print(
        is_pymupdf_available()
    )

    print(
        "\nOpenCV available:"
    )

    print(
        is_opencv_available()
    )

    # --------------------------------------------------------
    # Text cleaning
    # --------------------------------------------------------

    sample = """

        This is     OCR text.


        It contains multiple spaces.

        And extra blank lines.

    """

    print(
        "\nCleaned Text:"
    )

    print(
        clean_text(
            sample
        )
    )

    # --------------------------------------------------------
    # OCR block
    # --------------------------------------------------------

    block = OCRBlock(

        text="Generative AI",

        confidence=92.5,

        left=10,

        top=20,

        width=200,

        height=40,

        block_number=1,

        metadata={

            "test":
                True,

        },

    )

    print(
        "\nOCR Block:"
    )

    print(
        block_to_dict(
            block
        )
    )

    # --------------------------------------------------------
    # OCR document
    # --------------------------------------------------------

    document = OCRDocument(

        text=(
            "Generative AI curriculum "
            "requires Python, LLM, RAG "
            "and Agentic AI skills."
        ),

        metadata={

            "test":
                True,

        },

        source="demo",

        filename="demo.png",

        file_path="",

        page_number=1,

        page_count=1,

        confidence=92.5,

        language="eng",

        extraction_method="tesseract",

        is_scanned=True,

        blocks=[block],

    )

    result = OCRLoadResult(

        documents=[
            document
        ],

        metadata={

            "filename":
                "demo.png",

        },

        page_count=1,

        successful_pages=1,

        failed_pages=0,

        average_confidence=92.5,

        success=True,

    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print(
        "\nStatistics:"
    )

    print(
        document_statistics(
            result
        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\nSummary:"
    )

    print(
        loader_summary(
            result
        )
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print(
        "\nValidation:"
    )

    print(
        validate_load_result(
            result
        )
    )

    # --------------------------------------------------------
    # Dict
    # --------------------------------------------------------

    print(
        "\nDocument Dict:"
    )

    print(
        document_to_dict(
            document
        )
    )

    # --------------------------------------------------------
    # Optional actual file
    # --------------------------------------------------------

    if len(sys.argv) > 1:

        source = sys.argv[1]

        print(
            "\nLoading:"
        )

        print(
            source
        )

        actual_result = load(
            source
        )

        print(
            "\nLoader Summary:"
        )

        print(
            loader_summary(
                actual_result
            )
        )

        print(
            "\nExtracted Text Preview:"
        )

        for item in actual_result.documents:

            print(

                f"\n--- Page "
                f"{item.page_number}"
                f" ---"

            )

            print(
                item.text[:3000]
            )

    print(
        "\n============================================"
    )

    print(
        "OCR LOADER TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF rag/ocr_loader.py
# ============================================================
