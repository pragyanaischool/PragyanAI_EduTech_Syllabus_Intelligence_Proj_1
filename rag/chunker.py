# ============================================================
# rag/chunker.py
# CHUNK 1/10
#
# UNIVERSAL DOCUMENT CHUNKER
#
# Purpose:
#   Convert extracted PDF / DOCX / OCR / text documents into
#   retrieval-friendly chunks for embeddings and vector stores.
#
# Features:
#   - Character based chunking
#   - Word based chunking
#   - Sentence-aware chunking
#   - Paragraph-aware chunking
#   - Heading-aware chunking
#   - Token-aware approximation
#   - Configurable overlap
#   - Metadata preservation
#   - Source/page/section tracking
#   - Chunk IDs
#   - Parent document IDs
#   - Deduplication
#   - Minimum / maximum chunk size
#   - LangChain compatibility
#   - Batch processing
#
# Recommended:
#   pip install langchain-text-splitters
#
# Optional:
#   pip install tiktoken
#
# ============================================================

from __future__ import annotations

import hashlib
import logging
import re

from dataclasses import dataclass, field

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

CHUNKER_VERSION = "1.0.0"


# ============================================================
# DEFAULTS
# ============================================================

DEFAULT_CHUNK_SIZE = 1000

DEFAULT_CHUNK_OVERLAP = 150

DEFAULT_MIN_CHUNK_SIZE = 50

DEFAULT_MAX_CHUNK_SIZE = 1500

DEFAULT_SEPARATOR = "\n\n"


# ============================================================
# CHUNKING METHODS
# ============================================================

CHUNKING_METHODS = {

    "character",

    "word",

    "sentence",

    "paragraph",

    "heading",

    "recursive",

    "token",

}


# ============================================================
# CHUNK MODEL
# ============================================================

@dataclass
class TextChunk:

    text: str = ""

    chunk_id: str = ""

    parent_document_id: str = ""

    source: str = ""

    filename: str = ""

    page: Optional[int] = None

    section: str = ""

    chunk_index: int = 0

    total_chunks: int = 0

    start_char: int = 0

    end_char: int = 0

    word_count: int = 0

    character_count: int = 0

    token_count: int = 0

    chunking_method: str = "recursive"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CHUNK RESULT
# ============================================================

@dataclass
class ChunkingResult:

    chunks: List[TextChunk] = field(
        default_factory=list
    )

    source: str = ""

    document_id: str = ""

    total_chunks: int = 0

    total_characters: int = 0

    total_words: int = 0

    average_chunk_size: float = 0.0

    success: bool = True

    error: Optional[str] = None

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# CHUNK CONFIGURATION
# ============================================================

@dataclass
class ChunkConfig:

    chunk_size: int = DEFAULT_CHUNK_SIZE

    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP

    min_chunk_size: int = DEFAULT_MIN_CHUNK_SIZE

    max_chunk_size: int = DEFAULT_MAX_CHUNK_SIZE

    method: str = "recursive"

    separator: str = DEFAULT_SEPARATOR

    preserve_sentences: bool = True

    preserve_paragraphs: bool = True

    preserve_headings: bool = True

    deduplicate: bool = True

    normalize_whitespace: bool = True

    include_metadata: bool = True

    token_model: Optional[str] = None


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# TEXT NORMALIZATION + IDENTIFIERS
# ============================================================


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

    # Normalize tabs.
    text = text.replace(
        "\t",
        " ",
    )

    # Remove spaces before newlines.
    text = re.sub(
        r"[ \t]+\n",
        "\n",
        text,
    )

    # Normalize repeated spaces.
    text = re.sub(
        r"[ ]{2,}",
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
# NORMALIZE WHITESPACE
# ============================================================

def normalize_whitespace(
    text: str,
) -> str:

    text = clean_text(
        text
    )

    lines = []

    for line in text.split(
        "\n"
    ):

        line = line.strip()

        if line:

            lines.append(
                line
            )

        elif (
            lines
            and
            lines[-1] != ""
        ):

            lines.append("")

    return "\n".join(
        lines
    ).strip()


# ============================================================
# WORD COUNT
# ============================================================

def word_count(
    text: str,
) -> int:

    text = clean_text(
        text
    )

    if not text:

        return 0

    return len(
        re.findall(
            r"\S+",
            text,
        )
    )


# ============================================================
# APPROXIMATE TOKEN COUNT
# ============================================================

def approximate_token_count(
    text: str,
) -> int:

    text = clean_text(
        text
    )

    if not text:

        return 0

    # Rough approximation:
    #
    # English text is often approximately
    # 1 token ≈ 4 characters.
    #
    # This is intentionally only an approximation.
    return max(
        1,
        int(
            len(text) / 4
        ),
    )


# ============================================================
# GENERATE DOCUMENT ID
# ============================================================

def generate_document_id(
    source: str = "",
    text: str = "",
) -> str:

    base = (

        f"{source}|"
        f"{text[:1000]}"

    )

    return hashlib.sha1(
        base.encode(
            "utf-8",
            errors="ignore",
        )
    ).hexdigest()


# ============================================================
# GENERATE CHUNK ID
# ============================================================

def generate_chunk_id(
    document_id: str,
    chunk_index: int,
    text: str,
) -> str:

    base = (

        f"{document_id}|"
        f"{chunk_index}|"
        f"{text}"

    )

    return hashlib.sha1(
        base.encode(
            "utf-8",
            errors="ignore",
        )
    ).hexdigest()


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
# SENTENCE / PARAGRAPH SPLITTING
# ============================================================


# ============================================================
# SENTENCE PATTERN
# ============================================================

SENTENCE_PATTERN = re.compile(

    r"""
    (?<=[.!?])
    (?:
        ["'”’)\]]+
    )?
    \s+
    """

    ,

    re.VERBOSE,

)


# ============================================================
# SPLIT SENTENCES
# ============================================================

def split_sentences(
    text: str,
) -> List[str]:

    text = clean_text(
        text
    )

    if not text:

        return []

    # First split by explicit line breaks where appropriate.
    paragraphs = re.split(
        r"\n+",
        text,
    )

    sentences = []

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:

            continue

        parts = SENTENCE_PATTERN.split(
            paragraph
        )

        for part in parts:

            part = clean_text(
                part
            )

            if part:

                sentences.append(
                    part
                )

    return sentences


# ============================================================
# SPLIT PARAGRAPHS
# ============================================================

def split_paragraphs(
    text: str,
) -> List[str]:

    text = clean_text(
        text
    )

    if not text:

        return []

    paragraphs = re.split(
        r"\n\s*\n",
        text,
    )

    return [

        clean_text(
            paragraph
        )

        for paragraph
        in paragraphs

        if clean_text(
            paragraph
        )

    ]


# ============================================================
# SPLIT LINES
# ============================================================

def split_lines(
    text: str,
) -> List[str]:

    text = clean_text(
        text
    )

    return [

        clean_text(
            line
        )

        for line
        in text.split(
            "\n"
        )

        if clean_text(
            line
        )

    ]


# ============================================================
# SPLIT WORDS
# ============================================================

def split_words(
    text: str,
) -> List[str]:

    text = clean_text(
        text
    )

    if not text:

        return []

    return re.findall(
        r"\S+",
        text,
    )


# ============================================================
# JOIN TEXT PARTS
# ============================================================

def join_parts(
    parts: Sequence[str],
    separator: str = " ",
) -> str:

    cleaned = [

        clean_text(
            part
        )

        for part
        in parts

        if clean_text(
            part
        )

    ]

    return separator.join(
        cleaned
    ).strip()


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# BASIC CHUNKING METHODS
# ============================================================


# ============================================================
# CHARACTER CHUNKING
# ============================================================

def chunk_by_characters(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Tuple[str, int, int]]:

    text = clean_text(
        text
    )

    if not text:

        return []

    if chunk_size <= 0:

        raise ValueError(
            "chunk_size must be greater than zero."
        )

    if chunk_overlap < 0:

        raise ValueError(
            "chunk_overlap cannot be negative."
        )

    if chunk_overlap >= chunk_size:

        raise ValueError(

            "chunk_overlap must be smaller than chunk_size."

        )

    chunks = []

    start = 0

    text_length = len(
        text
    )

    step = (
        chunk_size
        -
        chunk_overlap
    )

    while start < text_length:

        end = min(

            start + chunk_size,

            text_length,

        )

        chunk_text = text[
            start:end
        ].strip()

        if chunk_text:

            chunks.append(

                (
                    chunk_text,
                    start,
                    end,
                )

            )

        if end >= text_length:

            break

        start += step

    return chunks


# ============================================================
# WORD CHUNKING
# ============================================================

def chunk_by_words(
    text: str,
    chunk_size: int = 250,
    chunk_overlap: int = 40,
) -> List[Tuple[str, int, int]]:

    text = clean_text(
        text
    )

    if not text:

        return []

    words = list(
        re.finditer(
            r"\S+",
            text,
        )
    )

    if not words:

        return []

    if chunk_size <= 0:

        raise ValueError(
            "chunk_size must be greater than zero."
        )

    if chunk_overlap >= chunk_size:

        raise ValueError(

            "chunk_overlap must be smaller than chunk_size."

        )

    chunks = []

    step = (
        chunk_size
        -
        chunk_overlap
    )

    start_word = 0

    while start_word < len(
        words
    ):

        end_word = min(

            start_word + chunk_size,

            len(words),

        )

        start_char = words[
            start_word
        ].start()

        end_char = words[
            end_word - 1
        ].end()

        chunk_text = text[
            start_char:end_char
        ].strip()

        if chunk_text:

            chunks.append(

                (
                    chunk_text,
                    start_char,
                    end_char,
                )

            )

        if end_word >= len(
            words
        ):

            break

        start_word += step

    return chunks


# ============================================================
# SENTENCE CHUNKING
# ============================================================

def chunk_by_sentences(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Tuple[str, int, int]]:

    text = clean_text(
        text
    )

    if not text:

        return []

    sentences = split_sentences(
        text
    )

    if not sentences:

        return []

    chunks = []

    current = []

    current_length = 0

    search_position = 0

    sentence_locations = []

    for sentence in sentences:

        position = text.find(
            sentence,
            search_position,
        )

        if position < 0:

            position = search_position

        end_position = (
            position
            +
            len(sentence)
        )

        sentence_locations.append(

            (
                sentence,
                position,
                end_position,
            )

        )

        search_position = end_position

    for sentence, start, end in sentence_locations:

        sentence_length = len(
            sentence
        )

        if (

            current
            and
            current_length
            +
            sentence_length
            >
            chunk_size

        ):

            chunk_text = " ".join(
                current
            ).strip()

            chunk_start = sentence_locations[
                max(
                    0,
                    len(
                        sentence_locations
                    )
                    -
                    len(current),
                )
            ][1]

            # Find exact start more safely.
            first_sentence = current[0]

            chunk_start = text.find(
                first_sentence
            )

            chunk_end = (
                chunk_start
                +
                len(chunk_text)
            )

            chunks.append(

                (
                    chunk_text,
                    chunk_start,
                    min(
                        chunk_end,
                        len(text),
                    ),
                )

            )

            # Preserve sentence overlap.
            overlap_sentences = []

            overlap_length = 0

            for previous in reversed(
                current
            ):

                if (
                    overlap_length
                    +
                    len(previous)
                    >
                    chunk_overlap
                ):

                    break

                overlap_sentences.insert(
                    0,
                    previous,
                )

                overlap_length += (
                    len(previous)
                    +
                    1
                )

            current = (
                overlap_sentences
                +
                [sentence]
            )

            current_length = sum(

                len(item)
                +
                1

                for item
                in current

            )

        else:

            current.append(
                sentence
            )

            current_length += (
                sentence_length
                +
                1
            )

    if current:

        chunk_text = " ".join(
            current
        ).strip()

        chunk_start = text.find(
            current[0]
        )

        chunk_end = min(

            len(text),

            chunk_start
            +
            len(chunk_text),

        )

        chunks.append(

            (
                chunk_text,
                chunk_start,
                chunk_end,
            )

        )

    return chunks


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# PARAGRAPH / HEADING / RECURSIVE CHUNKING
# ============================================================


# ============================================================
# PARAGRAPH CHUNKING
# ============================================================

def chunk_by_paragraphs(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> List[Tuple[str, int, int]]:

    text = clean_text(
        text
    )

    if not text:

        return []

    paragraphs = split_paragraphs(
        text
    )

    chunks = []

    current_parts = []

    current_length = 0

    search_position = 0

    for paragraph in paragraphs:

        position = text.find(
            paragraph,
            search_position,
        )

        if position < 0:

            position = search_position

        paragraph_length = len(
            paragraph
        )

        if (

            current_parts
            and
            current_length
            +
            paragraph_length
            >
            chunk_size

        ):

            chunk_text = "\n\n".join(
                current_parts
            ).strip()

            start = text.find(
                current_parts[0]
            )

            end = min(

                len(text),

                start
                +
                len(chunk_text),

            )

            chunks.append(

                (
                    chunk_text,
                    start,
                    end,
                )

            )

            current_parts = [
                paragraph
            ]

            current_length = paragraph_length

        else:

            current_parts.append(
                paragraph
            )

            current_length += (
                paragraph_length
                +
                2
            )

        search_position = (
            position
            +
            paragraph_length
        )

    if current_parts:

        chunk_text = "\n\n".join(
            current_parts
        ).strip()

        start = text.find(
            current_parts[0]
        )

        end = min(

            len(text),

            start
            +
            len(chunk_text),

        )

        chunks.append(

            (
                chunk_text,
                start,
                end,
            )

        )

    return chunks


# ============================================================
# HEADING DETECTION
# ============================================================

HEADING_PATTERN = re.compile(

    r"""
    ^
    (?:
        \#{1,6}\s+
        |
        (?:chapter|section|module|unit|topic)
        \s+
        [0-9A-Za-z.\-]+
        (?::|\s)
    )
    .+
    $

    """,

    re.IGNORECASE
    |
    re.VERBOSE,

)


# ============================================================
# IS HEADING
# ============================================================

def is_heading_line(
    line: str,
) -> bool:

    line = clean_text(
        line
    )

    if not line:

        return False

    if HEADING_PATTERN.match(
        line
    ):

        return True

    # Short title-like lines.
    words = line.split()

    if (
        len(words) <= 12
        and
        len(line) <= 100
        and
        not line.endswith(
            "."
        )
    ):

        # Avoid treating normal sentences as headings.
        if not re.search(
            r"[,:;!?]$",
            line,
        ):

            return True

    return False


# ============================================================
# HEADING-AWARE CHUNKING
# ============================================================

def chunk_by_headings(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> List[Tuple[str, int, int, str]]:

    text = clean_text(
        text
    )

    if not text:

        return []

    lines = text.split(
        "\n"
    )

    sections = []

    current_heading = ""

    current_lines = []

    current_start = 0

    position = 0

    for line in lines:

        stripped = line.strip()

        line_start = position

        line_end = (
            position
            +
            len(line)
        )

        position = (
            line_end
            +
            1
        )

        if (
            stripped
            and
            is_heading_line(
                stripped
            )
        ):

            if current_lines:

                section_text = "\n".join(
                    current_lines
                ).strip()

                if section_text:

                    sections.append(

                        (
                            section_text,
                            current_start,
                            line_start,
                            current_heading,
                        )

                    )

            current_heading = stripped

            current_lines = []

            current_start = line_end + 1

        else:

            if stripped:

                current_lines.append(
                    stripped
                )

    if current_lines:

        section_text = "\n".join(
            current_lines
        ).strip()

        if section_text:

            sections.append(

                (
                    section_text,
                    current_start,
                    len(text),
                    current_heading,
                )

            )

    # Split oversized sections.
    output = []

    for section_text, start, end, heading in sections:

        if len(section_text) <= chunk_size:

            output.append(

                (
                    section_text,
                    start,
                    end,
                    heading,
                )

            )

        else:

            smaller = chunk_by_sentences(

                section_text,

                chunk_size=chunk_size,

                chunk_overlap=min(
                    100,
                    chunk_size // 5,
                ),

            )

            for sub_text, sub_start, sub_end in smaller:

                output.append(

                    (
                        sub_text,
                        start + sub_start,
                        min(
                            end,
                            start + sub_end,
                        ),
                        heading,
                    )

                )

    return output


# ============================================================
# RECURSIVE CHUNKING
# ============================================================

def recursive_split(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: Optional[
        Sequence[str]
    ] = None,
) -> List[Tuple[str, int, int]]:

    text = clean_text(
        text
    )

    if not text:

        return []

    if separators is None:

        separators = [

            "\n\n",

            "\n",

            ". ",

            " ",

            "",

        ]

    # Base case.
    if len(text) <= chunk_size:

        return [

            (
                text,
                0,
                len(text),
            )

        ]

    separator = separators[0]

    if separator == "":

        return chunk_by_characters(

            text,

            chunk_size=chunk_size,

            chunk_overlap=chunk_overlap,

        )

    pieces = text.split(
        separator
    )

    if len(pieces) == 1:

        return recursive_split(

            text,

            chunk_size,

            chunk_overlap,

            separators[1:],

        )

    chunks = []

    current = []

    current_length = 0

    search_position = 0

    for piece in pieces:

        piece = piece.strip()

        if not piece:

            continue

        piece_length = len(
            piece
        )

        if (

            current
            and
            current_length
            +
            piece_length
            +
            len(separator)
            >
            chunk_size

        ):

            chunk_text = separator.join(
                current
            ).strip()

            start = text.find(
                current[0],
                search_position,
            )

            if start < 0:

                start = search_position

            end = min(

                len(text),

                start
                +
                len(chunk_text),

            )

            chunks.append(

                (
                    chunk_text,
                    start,
                    end,
                )

            )

            # Overlap using the tail of the previous pieces.
            overlap_parts = []

            overlap_length = 0

            for previous in reversed(
                current
            ):

                if (

                    overlap_length
                    +
                    len(previous)
                    >
                    chunk_overlap

                ):

                    break

                overlap_parts.insert(
                    0,
                    previous,
                )

                overlap_length += (
                    len(previous)
                    +
                    len(separator)
                )

            current = (
                overlap_parts
                +
                [piece]
            )

            current_length = sum(

                len(item)
                +
                len(separator)

                for item
                in current

            )

        else:

            current.append(
                piece
            )

            current_length += (

                piece_length
                +
                len(separator)

            )

        found = text.find(
            piece,
            search_position,
        )

        if found >= 0:

            search_position = (
                found
                +
                len(piece)
            )

    if current:

        chunk_text = separator.join(
            current
        ).strip()

        start = text.find(
            current[0]
        )

        if start < 0:

            start = 0

        end = min(

            len(text),

            start
            +
            len(chunk_text),

        )

        chunks.append(

            (
                chunk_text,
                start,
                end,
            )

        )

    return chunks


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# CONFIGURATION + CHUNK OBJECT CREATION
# ============================================================


# ============================================================
# VALIDATE CONFIG
# ============================================================

def validate_config(
    config: ChunkConfig,
) -> ChunkConfig:

    if config.chunk_size <= 0:

        raise ValueError(
            "chunk_size must be greater than zero."
        )

    if config.chunk_overlap < 0:

        raise ValueError(
            "chunk_overlap cannot be negative."
        )

    if config.chunk_overlap >= config.chunk_size:

        raise ValueError(

            "chunk_overlap must be smaller than chunk_size."

        )

    if config.min_chunk_size < 0:

        raise ValueError(

            "min_chunk_size cannot be negative."

        )

    if config.max_chunk_size < config.chunk_size:

        config.max_chunk_size = config.chunk_size

    if config.method not in CHUNKING_METHODS:

        raise ValueError(

            f"Unsupported chunking method: {config.method}. "
            f"Supported: {sorted(CHUNKING_METHODS)}"

        )

    return config


# ============================================================
# BUILD METADATA
# ============================================================

def build_chunk_metadata(
    source: str = "",
    filename: str = "",
    page: Optional[int] = None,
    section: str = "",
    document_metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> Dict[str, Any]:

    metadata = dict(
        document_metadata
        or
        {}
    )

    metadata.update({

        "source":
            source,

        "filename":
            filename,

        "page":
            page,

        "section":
            section,

    })

    return metadata


# ============================================================
# CREATE CHUNK
# ============================================================

def create_chunk(
    text: str,
    document_id: str,
    chunk_index: int,
    source: str = "",
    filename: str = "",
    page: Optional[int] = None,
    section: str = "",
    start_char: int = 0,
    end_char: int = 0,
    method: str = "recursive",
    document_metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> TextChunk:

    text = clean_text(
        text
    )

    chunk_id = generate_chunk_id(

        document_id=document_id,

        chunk_index=chunk_index,

        text=text,

    )

    metadata = build_chunk_metadata(

        source=source,

        filename=filename,

        page=page,

        section=section,

        document_metadata=document_metadata,

    )

    metadata.update({

        "chunk_id":
            chunk_id,

        "document_id":
            document_id,

        "chunk_index":
            chunk_index,

        "start_char":
            start_char,

        "end_char":
            end_char,

        "word_count":
            word_count(
                text
            ),

        "character_count":
            len(text),

        "token_count":
            approximate_token_count(
                text
            ),

        "chunking_method":
            method,

    })

    return TextChunk(

        text=text,

        chunk_id=chunk_id,

        parent_document_id=document_id,

        source=source,

        filename=filename,

        page=page,

        section=section,

        chunk_index=chunk_index,

        total_chunks=0,

        start_char=start_char,

        end_char=end_char,

        word_count=word_count(
            text
        ),

        character_count=len(
            text
        ),

        token_count=approximate_token_count(
            text
        ),

        chunking_method=method,

        metadata=metadata,

    )


# ============================================================
# DEDUPLICATE CHUNKS
# ============================================================

def deduplicate_chunks(
    chunks: Sequence[TextChunk],
) -> List[TextChunk]:

    output = []

    seen = set()

    for chunk in chunks:

        normalized = re.sub(

            r"\s+",
            " ",

            chunk.text.lower().strip(),

        )

        if not normalized:

            continue

        fingerprint = hashlib.sha1(

            normalized.encode(
                "utf-8",
                errors="ignore",
            )

        ).hexdigest()

        if fingerprint in seen:

            continue

        seen.add(
            fingerprint
        )

        output.append(
            chunk
        )

    return output


# ============================================================
# UPDATE CHUNK INDICES
# ============================================================

def update_chunk_indices(
    chunks: List[TextChunk],
) -> List[TextChunk]:

    total = len(
        chunks
    )

    for index, chunk in enumerate(
        chunks
    ):

        chunk.chunk_index = index

        chunk.total_chunks = total

        chunk.metadata[
            "chunk_index"
        ] = index

        chunk.metadata[
            "total_chunks"
        ] = total

    return chunks


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# UNIVERSAL CHUNKING ENGINE
# ============================================================


# ============================================================
# CHUNK TEXT
# ============================================================

def chunk_text(
    text: str,
    config: Optional[
        ChunkConfig
    ] = None,
) -> List[
    Tuple[
        str,
        int,
        int,
        str,
    ]
]:

    if config is None:

        config = ChunkConfig()

    config = validate_config(
        config
    )

    if config.normalize_whitespace:

        text = normalize_whitespace(
            text
        )

    else:

        text = clean_text(
            text
        )

    if not text:

        return []

    method = config.method

    # --------------------------------------------------------
    # Character
    # --------------------------------------------------------

    if method == "character":

        basic = chunk_by_characters(

            text,

            chunk_size=config.chunk_size,

            chunk_overlap=config.chunk_overlap,

        )

        return [

            (
                chunk_text,
                start,
                end,
                "",
            )

            for chunk_text, start, end
            in basic

        ]

    # --------------------------------------------------------
    # Word
    # --------------------------------------------------------

    if method == "word":

        # chunk_size is interpreted as word count.
        basic = chunk_by_words(

            text,

            chunk_size=config.chunk_size,

            chunk_overlap=config.chunk_overlap,

        )

        return [

            (
                chunk_text,
                start,
                end,
                "",
            )

            for chunk_text, start, end
            in basic

        ]

    # --------------------------------------------------------
    # Sentence
    # --------------------------------------------------------

    if method == "sentence":

        basic = chunk_by_sentences(

            text,

            chunk_size=config.chunk_size,

            chunk_overlap=config.chunk_overlap,

        )

        return [

            (
                chunk_text,
                start,
                end,
                "",
            )

            for chunk_text, start, end
            in basic

        ]

    # --------------------------------------------------------
    # Paragraph
    # --------------------------------------------------------

    if method == "paragraph":

        basic = chunk_by_paragraphs(

            text,

            chunk_size=config.chunk_size,

        )

        return [

            (
                chunk_text,
                start,
                end,
                "",
            )

            for chunk_text, start, end
            in basic

        ]

    # --------------------------------------------------------
    # Heading
    # --------------------------------------------------------

    if method == "heading":

        basic = chunk_by_headings(

            text,

            chunk_size=config.chunk_size,

        )

        return [

            (
                chunk_text,
                start,
                end,
                heading,
            )

            for (
                chunk_text,
                start,
                end,
                heading,
            )
            in basic

        ]

    # --------------------------------------------------------
    # Recursive
    # --------------------------------------------------------

    if method == "recursive":

        basic = recursive_split(

            text,

            chunk_size=config.chunk_size,

            chunk_overlap=config.chunk_overlap,

        )

        return [

            (
                chunk_text,
                start,
                end,
                "",
            )

            for chunk_text, start, end
            in basic

        ]

    # --------------------------------------------------------
    # Token approximation
    # --------------------------------------------------------

    if method == "token":

        # Convert approximate token limit to characters.
        character_size = (
            config.chunk_size
            *
            4
        )

        character_overlap = (
            config.chunk_overlap
            *
            4
        )

        basic = chunk_by_characters(

            text,

            chunk_size=character_size,

            chunk_overlap=character_overlap,

        )

        return [

            (
                chunk_text,
                start,
                end,
                "",
            )

            for chunk_text, start, end
            in basic

        ]

    raise ValueError(

        f"Unsupported chunking method: {method}"

    )


# ============================================================
# CHUNK DOCUMENT
# ============================================================

def chunk_document(
    text: str,
    source: str = "",
    filename: str = "",
    page: Optional[int] = None,
    section: str = "",
    document_id: Optional[str] = None,
    config: Optional[
        ChunkConfig
    ] = None,
    document_metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> ChunkingResult:

    try:

        if config is None:

            config = ChunkConfig()

        config = validate_config(
            config
        )

        text = (

            normalize_whitespace(
                text
            )

            if config.normalize_whitespace

            else clean_text(
                text
            )

        )

        if not text:

            return ChunkingResult(

                chunks=[],

                source=source,

                document_id=document_id or "",

                total_chunks=0,

                total_characters=0,

                total_words=0,

                average_chunk_size=0.0,

                success=True,

                warnings=[
                    "Document contains no text."
                ],

            )

        if document_id is None:

            document_id = generate_document_id(

                source=source,

                text=text,

            )

        raw_chunks = chunk_text(

            text=text,

            config=config,

        )

        chunks = []

        for index, (
            chunk_text_value,
            start,
            end,
            heading,
        ) in enumerate(
            raw_chunks
        ):

            chunk_section = (
                heading
                or
                section
            )

            # Merge metadata.
            metadata = dict(
                document_metadata
                or
                {}
            )

            metadata[
                "original_section"
            ] = section

            chunk = create_chunk(

                text=chunk_text_value,

                document_id=document_id,

                chunk_index=index,

                source=source,

                filename=filename,

                page=page,

                section=chunk_section,

                start_char=start,

                end_char=end,

                method=config.method,

                document_metadata=metadata,

            )

            # Minimum chunk filter.
            if (

                chunk.character_count
                <
                config.min_chunk_size

                and
                len(raw_chunks) > 1

            ):

                continue

            # Maximum chunk protection.
            if (

                chunk.character_count
                >
                config.max_chunk_size

            ):

                logger.warning(

                    "Chunk exceeds configured maximum: %s",

                    chunk.character_count,

                )

            chunks.append(
                chunk
            )

        if config.deduplicate:

            chunks = deduplicate_chunks(
                chunks
            )

        chunks = update_chunk_indices(
            chunks
        )

        total_characters = sum(

            chunk.character_count

            for chunk
            in chunks

        )

        total_words = sum(

            chunk.word_count

            for chunk
            in chunks

        )

        average_size = (

            total_characters
            /
            len(chunks)

            if chunks

            else 0.0

        )

        warnings = []

        if not chunks:

            warnings.append(

                "No chunks were produced."

            )

        return ChunkingResult(

            chunks=chunks,

            source=source,

            document_id=document_id,

            total_chunks=len(
                chunks
            ),

            total_characters=total_characters,

            total_words=total_words,

            average_chunk_size=round(
                average_size,
                2,
            ),

            success=True,

            warnings=warnings,

        )

    except Exception as exc:

        logger.exception(
            "Document chunking failed."
        )

        return ChunkingResult(

            chunks=[],

            source=source,

            document_id=document_id or "",

            success=False,

            error=str(
                exc
            ),

        )


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# INTEGRATION WITH PDF / DOCX / OCR LOADERS
# ============================================================


# ============================================================
# EXTRACT DOCUMENT FIELDS
# ============================================================

def extract_document_fields(
    document: Any,
) -> Tuple[
    str,
    str,
    str,
    Optional[int],
    str,
    Dict[str, Any],
]:

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    text = getattr(
        document,
        "text",
        None,
    )

    if text is None:

        text = getattr(
            document,
            "page_content",
            "",
        )

    text = clean_text(
        text
    )

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    source = getattr(
        document,
        "source",
        "",
    )

    # --------------------------------------------------------
    # Filename
    # --------------------------------------------------------

    filename = getattr(
        document,
        "filename",
        "",
    )

    # --------------------------------------------------------
    # Page
    # --------------------------------------------------------

    page = getattr(
        document,
        "page_number",
        None,
    )

    if page is None:

        page = getattr(
            document,
            "page",
            None,
        )

    # --------------------------------------------------------
    # Section
    # --------------------------------------------------------

    section = getattr(
        document,
        "section",
        "",
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = getattr(
        document,
        "metadata",
        {},
    )

    if metadata is None:

        metadata = {}

    metadata = dict(
        metadata
    )

    return (

        text,

        str(
            source or ""
        ),

        str(
            filename or ""
        ),

        page,

        str(
            section or ""
        ),

        metadata,

    )


# ============================================================
# CHUNK LOADER DOCUMENT
# ============================================================

def chunk_loader_document(
    document: Any,
    config: Optional[
        ChunkConfig
    ] = None,
) -> ChunkingResult:

    (
        text,
        source,
        filename,
        page,
        section,
        metadata,
    ) = extract_document_fields(
        document
    )

    document_id = metadata.get(
        "document_id"
    )

    if not document_id:

        document_id = generate_document_id(

            source=source,

            text=text,

        )

    return chunk_document(

        text=text,

        source=source,

        filename=filename,

        page=page,

        section=section,

        document_id=document_id,

        config=config,

        document_metadata=metadata,

    )


# ============================================================
# CHUNK LOADER RESULT
# ============================================================

def chunk_loader_result(
    result: Any,
    config: Optional[
        ChunkConfig
    ] = None,
) -> ChunkingResult:

    documents = getattr(
        result,
        "documents",
        None,
    )

    if documents is None:

        raise ValueError(

            "Loader result must contain a 'documents' attribute."

        )

    all_chunks = []

    source = ""

    document_ids = []

    warnings = []

    success = True

    errors = []

    for document in documents:

        chunk_result = chunk_loader_document(

            document,

            config=config,

        )

        all_chunks.extend(
            chunk_result.chunks
        )

        if chunk_result.source:

            source = chunk_result.source

        if chunk_result.document_id:

            document_ids.append(
                chunk_result.document_id
            )

        warnings.extend(
            chunk_result.warnings
        )

        if not chunk_result.success:

            success = False

            if chunk_result.error:

                errors.append(
                    chunk_result.error
                )

    # --------------------------------------------------------
    # Global deduplication
    # --------------------------------------------------------

    if config is None:

        config = ChunkConfig()

    if config.deduplicate:

        all_chunks = deduplicate_chunks(
            all_chunks
        )

    all_chunks = update_chunk_indices(
        all_chunks
    )

    total_characters = sum(

        chunk.character_count

        for chunk
        in all_chunks

    )

    total_words = sum(

        chunk.word_count

        for chunk
        in all_chunks

    )

    average_size = (

        total_characters
        /
        len(all_chunks)

        if all_chunks

        else 0.0

    )

    return ChunkingResult(

        chunks=all_chunks,

        source=source,

        document_id=(

            document_ids[0]
            if len(document_ids) == 1
            else ""

        ),

        total_chunks=len(
            all_chunks
        ),

        total_characters=total_characters,

        total_words=total_words,

        average_chunk_size=round(
            average_size,
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
# BATCH CHUNK DOCUMENTS
# ============================================================

def batch_chunk_documents(
    documents: Iterable[Any],
    config: Optional[
        ChunkConfig
    ] = None,
) -> List[ChunkingResult]:

    results = []

    for document in documents:

        try:

            results.append(

                chunk_loader_document(

                    document,

                    config=config,

                )

            )

        except Exception as exc:

            logger.exception(
                "Batch chunking failed."
            )

            results.append(

                ChunkingResult(

                    success=False,

                    error=str(
                        exc
                    ),

                )

            )

    return results


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 8/10
#
# INTEGRATION WITH PDF / DOCX / OCR LOADERS
# ============================================================


# ============================================================
# EXTRACT DOCUMENT FIELDS
# ============================================================

def extract_document_fields(
    document: Any,
) -> Tuple[
    str,
    str,
    str,
    Optional[int],
    str,
    Dict[str, Any],
]:

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    text = getattr(
        document,
        "text",
        None,
    )

    if text is None:

        text = getattr(
            document,
            "page_content",
            "",
        )

    text = clean_text(
        text
    )

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    source = getattr(
        document,
        "source",
        "",
    )

    # --------------------------------------------------------
    # Filename
    # --------------------------------------------------------

    filename = getattr(
        document,
        "filename",
        "",
    )

    # --------------------------------------------------------
    # Page
    # --------------------------------------------------------

    page = getattr(
        document,
        "page_number",
        None,
    )

    if page is None:

        page = getattr(
            document,
            "page",
            None,
        )

    # --------------------------------------------------------
    # Section
    # --------------------------------------------------------

    section = getattr(
        document,
        "section",
        "",
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = getattr(
        document,
        "metadata",
        {},
    )

    if metadata is None:

        metadata = {}

    metadata = dict(
        metadata
    )

    return (

        text,

        str(
            source or ""
        ),

        str(
            filename or ""
        ),

        page,

        str(
            section or ""
        ),

        metadata,

    )


# ============================================================
# CHUNK LOADER DOCUMENT
# ============================================================

def chunk_loader_document(
    document: Any,
    config: Optional[
        ChunkConfig
    ] = None,
) -> ChunkingResult:

    (
        text,
        source,
        filename,
        page,
        section,
        metadata,
    ) = extract_document_fields(
        document
    )

    document_id = metadata.get(
        "document_id"
    )

    if not document_id:

        document_id = generate_document_id(

            source=source,

            text=text,

        )

    return chunk_document(

        text=text,

        source=source,

        filename=filename,

        page=page,

        section=section,

        document_id=document_id,

        config=config,

        document_metadata=metadata,

    )


# ============================================================
# CHUNK LOADER RESULT
# ============================================================

def chunk_loader_result(
    result: Any,
    config: Optional[
        ChunkConfig
    ] = None,
) -> ChunkingResult:

    documents = getattr(
        result,
        "documents",
        None,
    )

    if documents is None:

        raise ValueError(

            "Loader result must contain a 'documents' attribute."

        )

    all_chunks = []

    source = ""

    document_ids = []

    warnings = []

    success = True

    errors = []

    for document in documents:

        chunk_result = chunk_loader_document(

            document,

            config=config,

        )

        all_chunks.extend(
            chunk_result.chunks
        )

        if chunk_result.source:

            source = chunk_result.source

        if chunk_result.document_id:

            document_ids.append(
                chunk_result.document_id
            )

        warnings.extend(
            chunk_result.warnings
        )

        if not chunk_result.success:

            success = False

            if chunk_result.error:

                errors.append(
                    chunk_result.error
                )

    # --------------------------------------------------------
    # Global deduplication
    # --------------------------------------------------------

    if config is None:

        config = ChunkConfig()

    if config.deduplicate:

        all_chunks = deduplicate_chunks(
            all_chunks
        )

    all_chunks = update_chunk_indices(
        all_chunks
    )

    total_characters = sum(

        chunk.character_count

        for chunk
        in all_chunks

    )

    total_words = sum(

        chunk.word_count

        for chunk
        in all_chunks

    )

    average_size = (

        total_characters
        /
        len(all_chunks)

        if all_chunks

        else 0.0

    )

    return ChunkingResult(

        chunks=all_chunks,

        source=source,

        document_id=(

            document_ids[0]
            if len(document_ids) == 1
            else ""

        ),

        total_chunks=len(
            all_chunks
        ),

        total_characters=total_characters,

        total_words=total_words,

        average_chunk_size=round(
            average_size,
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
# BATCH CHUNK DOCUMENTS
# ============================================================

def batch_chunk_documents(
    documents: Iterable[Any],
    config: Optional[
        ChunkConfig
    ] = None,
) -> List[ChunkingResult]:

    results = []

    for document in documents:

        try:

            results.append(

                chunk_loader_document(

                    document,

                    config=config,

                )

            )

        except Exception as exc:

            logger.exception(
                "Batch chunking failed."
            )

            results.append(

                ChunkingResult(

                    success=False,

                    error=str(
                        exc
                    ),

                )

            )

    return results


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# LANGCHAIN + ADVANCED UTILITIES
# ============================================================


# ============================================================
# OPTIONAL LANGCHAIN
# ============================================================

try:

    from langchain_core.documents import Document as LangChainDocument

except ImportError:

    LangChainDocument = None


# ============================================================
# CHUNK → DICT
# ============================================================

def chunk_to_dict(
    chunk: TextChunk,
) -> Dict[str, Any]:

    metadata = dict(
        chunk.metadata
    )

    metadata.update({

        "chunk_id":
            chunk.chunk_id,

        "document_id":
            chunk.parent_document_id,

        "source":
            chunk.source,

        "filename":
            chunk.filename,

        "page":
            chunk.page,

        "section":
            chunk.section,

        "chunk_index":
            chunk.chunk_index,

        "total_chunks":
            chunk.total_chunks,

        "start_char":
            chunk.start_char,

        "end_char":
            chunk.end_char,

        "word_count":
            chunk.word_count,

        "character_count":
            chunk.character_count,

        "token_count":
            chunk.token_count,

        "chunking_method":
            chunk.chunking_method,

    })

    return {

        "page_content":
            chunk.text,

        "metadata":
            metadata,

    }


# ============================================================
# CHUNK → LANGCHAIN
# ============================================================

def chunk_to_langchain(
    chunk: TextChunk,
) -> Any:

    if LangChainDocument is None:

        raise ImportError(

            "langchain-core is required. "
            "Install using: pip install langchain-core"

        )

    return LangChainDocument(

        page_content=chunk.text,

        metadata=dict(
            chunk_to_dict(
                chunk
            )[
                "metadata"
            ]
        ),

    )


# ============================================================
# CHUNKS → LANGCHAIN
# ============================================================

def to_langchain_documents(
    chunks: Sequence[TextChunk],
) -> List[Any]:

    return [

        chunk_to_langchain(
            chunk
        )

        for chunk
        in chunks

    ]


# ============================================================
# CHUNKS → DICTS
# ============================================================

def to_document_dicts(
    chunks: Sequence[TextChunk],
) -> List[Dict[str, Any]]:

    return [

        chunk_to_dict(
            chunk
        )

        for chunk
        in chunks

    ]


# ============================================================
# CHUNK SEARCH TEXT
# ============================================================

def build_search_text(
    chunk: TextChunk,
    include_metadata: bool = True,
) -> str:

    if not include_metadata:

        return chunk.text

    parts = []

    if chunk.filename:

        parts.append(

            f"Document: "
            f"{chunk.filename}"

        )

    if chunk.page is not None:

        parts.append(

            f"Page: "
            f"{chunk.page}"

        )

    if chunk.section:

        parts.append(

            f"Section: "
            f"{chunk.section}"

        )

    parts.append(
        chunk.text
    )

    return "\n".join(
        parts
    )


# ============================================================
# FILTER LOW-QUALITY CHUNKS
# ============================================================

def filter_chunks(
    chunks: Sequence[TextChunk],
    min_characters: int = DEFAULT_MIN_CHUNK_SIZE,
    min_words: int = 3,
) -> List[TextChunk]:

    output = []

    for chunk in chunks:

        if (
            chunk.character_count
            <
            min_characters
        ):

            continue

        if (
            chunk.word_count
            <
            min_words
        ):

            continue

        output.append(
            chunk
        )

    return update_chunk_indices(
        output
    )


# ============================================================
# MERGE SMALL CHUNKS
# ============================================================

def merge_small_chunks(
    chunks: Sequence[TextChunk],
    min_size: int = DEFAULT_MIN_CHUNK_SIZE,
) -> List[TextChunk]:

    if not chunks:

        return []

    output = []

    buffer = None

    for chunk in chunks:

        if buffer is None:

            buffer = chunk

            continue

        if (

            buffer.character_count
            <
            min_size

        ):

            merged_text = (

                buffer.text
                +
                "\n\n"
                +
                chunk.text

            ).strip()

            buffer.text = merged_text

            buffer.character_count = len(
                merged_text
            )

            buffer.word_count = word_count(
                merged_text
            )

            buffer.token_count = approximate_token_count(
                merged_text
            )

            buffer.end_char = (
                chunk.end_char
            )

            buffer.metadata[
                "character_count"
            ] = buffer.character_count

            buffer.metadata[
                "word_count"
            ] = buffer.word_count

            buffer.metadata[
                "token_count"
            ] = buffer.token_count

        else:

            output.append(
                buffer
            )

            buffer = chunk

    if buffer is not None:

        output.append(
            buffer
        )

    return update_chunk_indices(
        output
    )


# ============================================================
# CHUNK QUALITY SCORE
# ============================================================

def chunk_quality_score(
    chunk: TextChunk,
) -> float:

    if not chunk.text:

        return 0.0

    score = 0.0

    # Text length.
    if chunk.character_count >= 100:

        score += 0.25

    if chunk.character_count >= 300:

        score += 0.15

    # Word count.
    if chunk.word_count >= 20:

        score += 0.20

    # Sentence-like structure.
    if re.search(
        r"[.!?]",
        chunk.text,
    ):

        score += 0.15

    # Metadata.
    if chunk.source:

        score += 0.10

    if chunk.section:

        score += 0.10

    if chunk.page is not None:

        score += 0.05

    return round(
        min(
            score,
            1.0,
        ),
        3,
    )


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# STATISTICS + PRESETS + EXPORTS + SELF TEST
# ============================================================


# ============================================================
# CHUNK STATISTICS
# ============================================================

def chunk_statistics(
    chunks: Sequence[TextChunk],
) -> Dict[str, Any]:

    if not chunks:

        return {

            "chunk_count":
                0,

            "total_characters":
                0,

            "total_words":
                0,

            "average_characters":
                0.0,

            "average_words":
                0.0,

            "average_tokens":
                0.0,

            "min_characters":
                0,

            "max_characters":
                0,

        }

    characters = [

        chunk.character_count

        for chunk
        in chunks

    ]

    words = [

        chunk.word_count

        for chunk
        in chunks

    ]

    tokens = [

        chunk.token_count

        for chunk
        in chunks

    ]

    return {

        "chunk_count":
            len(chunks),

        "total_characters":
            sum(characters),

        "total_words":
            sum(words),

        "total_tokens":
            sum(tokens),

        "average_characters":
            round(
                sum(characters)
                /
                len(chunks),
                2,
            ),

        "average_words":
            round(
                sum(words)
                /
                len(chunks),
                2,
            ),

        "average_tokens":
            round(
                sum(tokens)
                /
                len(chunks),
                2,
            ),

        "min_characters":
            min(characters),

        "max_characters":
            max(characters),

    }


# ============================================================
# RAG PRESET
# ============================================================

def rag_chunk_config() -> ChunkConfig:

    return ChunkConfig(

        chunk_size=1000,

        chunk_overlap=150,

        min_chunk_size=50,

        max_chunk_size=1500,

        method="recursive",

        separator="\n\n",

        preserve_sentences=True,

        preserve_paragraphs=True,

        preserve_headings=True,

        deduplicate=True,

        normalize_whitespace=True,

        include_metadata=True,

    )


# ============================================================
# CURRICULUM PRESET
# ============================================================

def curriculum_chunk_config() -> ChunkConfig:

    return ChunkConfig(

        chunk_size=1200,

        chunk_overlap=200,

        min_chunk_size=80,

        max_chunk_size=1600,

        method="heading",

        separator="\n\n",

        preserve_sentences=True,

        preserve_paragraphs=True,

        preserve_headings=True,

        deduplicate=True,

        normalize_whitespace=True,

        include_metadata=True,

    )


# ============================================================
# JOB DESCRIPTION PRESET
# ============================================================

def jd_chunk_config() -> ChunkConfig:

    return ChunkConfig(

        chunk_size=800,

        chunk_overlap=120,

        min_chunk_size=40,

        max_chunk_size=1200,

        method="recursive",

        separator="\n\n",

        preserve_sentences=True,

        preserve_paragraphs=True,

        preserve_headings=True,

        deduplicate=True,

        normalize_whitespace=True,

        include_metadata=True,

    )


# ============================================================
# OCR PRESET
# ============================================================

def ocr_chunk_config() -> ChunkConfig:

    return ChunkConfig(

        chunk_size=900,

        chunk_overlap=150,

        min_chunk_size=40,

        max_chunk_size=1300,

        method="sentence",

        separator="\n\n",

        preserve_sentences=True,

        preserve_paragraphs=True,

        preserve_headings=True,

        deduplicate=True,

        normalize_whitespace=True,

        include_metadata=True,

    )


# ============================================================
# SUMMARY
# ============================================================

def chunking_summary(
    result: ChunkingResult,
) -> Dict[str, Any]:

    return {

        "chunker_version":
            CHUNKER_VERSION,

        "success":
            result.success,

        "document_id":
            result.document_id,

        "source":
            result.source,

        "total_chunks":
            result.total_chunks,

        "total_characters":
            result.total_characters,

        "total_words":
            result.total_words,

        "average_chunk_size":
            result.average_chunk_size,

        "warnings":
            result.warnings,

        "error":
            result.error,

    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "CHUNKER_VERSION",

    # Models
    "TextChunk",

    "ChunkingResult",

    "ChunkConfig",

    # Utilities
    "clean_text",

    "normalize_whitespace",

    "word_count",

    "approximate_token_count",

    "generate_document_id",

    "generate_chunk_id",

    "normalize_source",

    # Splitters
    "split_sentences",

    "split_paragraphs",

    "split_lines",

    "split_words",

    "join_parts",

    # Chunking methods
    "chunk_by_characters",

    "chunk_by_words",

    "chunk_by_sentences",

    "chunk_by_paragraphs",

    "chunk_by_headings",

    "recursive_split",

    "chunk_text",

    "chunk_document",

    # Configuration
    "validate_config",

    "build_chunk_metadata",

    "create_chunk",

    # Deduplication
    "deduplicate_chunks",

    "update_chunk_indices",

    # Loader integration
    "extract_document_fields",

    "chunk_loader_document",

    "chunk_loader_result",

    "batch_chunk_documents",

    # Conversion
    "chunk_to_dict",

    "chunk_to_langchain",

    "to_langchain_documents",

    "to_document_dicts",

    "build_search_text",

    # Quality
    "filter_chunks",

    "merge_small_chunks",

    "chunk_quality_score",

    # Statistics
    "chunk_statistics",

    "chunking_summary",

    # Presets
    "rag_chunk_config",

    "curriculum_chunk_config",

    "jd_chunk_config",

    "ocr_chunk_config",

]


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n"
        "============================================"
    )

    print(
        "CHUNKER SELF TEST"
    )

    print(
        "============================================"
    )

    sample_text = """

    Generative AI

    Generative AI is transforming software engineering.
    Large language models can generate code, summarize
    documents, answer questions and support developers.

    Retrieval Augmented Generation

    RAG combines document retrieval with language models.
    Documents are loaded, cleaned, chunked and embedded.
    The embeddings are stored in a vector database.

    Agentic AI

    Agentic AI systems use tools, memory and reasoning
    workflows to solve complex tasks.

    """

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    config = rag_chunk_config()

    print(
        "\nConfiguration:"
    )

    print(
        config
    )

    # --------------------------------------------------------
    # Chunk
    # --------------------------------------------------------

    result = chunk_document(

        text=sample_text,

        source="demo.txt",

        filename="demo.txt",

        section="AI",

        config=config,

    )

    print(
        "\nChunking Summary:"
    )

    print(
        chunking_summary(
            result
        )
    )

    # --------------------------------------------------------
    # Chunks
    # --------------------------------------------------------

    print(
        "\nGenerated Chunks:"
    )

    for chunk in result.chunks:

        print(
            "\n--------------------------------------------"
        )

        print(
            f"Chunk ID: "
            f"{chunk.chunk_id}"
        )

        print(
            f"Index: "
            f"{chunk.chunk_index + 1}/"
            f"{chunk.total_chunks}"
        )

        print(
            f"Words: "
            f"{chunk.word_count}"
        )

        print(
            f"Characters: "
            f"{chunk.character_count}"
        )

        print(
            f"Tokens: "
            f"{chunk.token_count}"
        )

        print(
            f"Quality: "
            f"{chunk_quality_score(chunk)}"
        )

        print(
            chunk.text
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print(
        "\nStatistics:"
    )

    print(
        chunk_statistics(
            result.chunks
        )
    )

    # --------------------------------------------------------
    # Dict conversion
    # --------------------------------------------------------

    if result.chunks:

        print(
            "\nFirst Chunk Dictionary:"
        )

        print(
            chunk_to_dict(
                result.chunks[0]
            )
        )

    # --------------------------------------------------------
    # Sentence splitting
    # --------------------------------------------------------

    print(
        "\nSentences:"
    )

    for sentence in split_sentences(
        sample_text
    ):

        print(
            f"- {sentence}"
        )

    # --------------------------------------------------------
    # Paragraph splitting
    # --------------------------------------------------------

    print(
        "\nParagraphs:"
    )

    for paragraph in split_paragraphs(
        sample_text
    ):

        print(
            f"- {paragraph}"
        )

    print(
        "\n============================================"
    )

    print(
        "CHUNKER TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF rag/chunker.py
# ============================================================
