# ============================================================
# rag/embeddings.py
# CHUNK 1/10
#
# EMBEDDING ENGINE
#
# Purpose:
#   Convert RAG TextChunks into vector embeddings.
#
# Supports:
#   - SentenceTransformers
#   - Hugging Face models
#   - OpenAI-compatible embedding APIs
#   - Local embedding models
#   - Batch embedding
#   - Query embedding
#   - Similarity calculation
#   - Embedding cache
#   - Metadata preservation
#   - NumPy vectors
#   - RAG-ready records
#
# Recommended:
#
#   pip install sentence-transformers
#   pip install numpy
#
# Optional:
#
#   pip install openai
#
# ============================================================

from __future__ import annotations

import hashlib
import json
import logging
import math
import os

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

EMBEDDINGS_VERSION = "1.0.0"


# ============================================================
# DEFAULT MODELS
# ============================================================

DEFAULT_SENTENCE_TRANSFORMER_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

DEFAULT_HUGGINGFACE_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_BATCH_SIZE = 32

DEFAULT_NORMALIZE = True

DEFAULT_SIMILARITY_THRESHOLD = 0.30


# ============================================================
# OPTIONAL NUMPY
# ============================================================

try:

    import numpy as np

except ImportError:

    np = None


# ============================================================
# OPTIONAL SENTENCE TRANSFORMERS
# ============================================================

try:

    from sentence_transformers import SentenceTransformer

except ImportError:

    SentenceTransformer = None


# ============================================================
# OPTIONAL OPENAI
# ============================================================

try:

    from openai import OpenAI

except ImportError:

    OpenAI = None


# ============================================================
# EMBEDDING RECORD
# ============================================================

@dataclass
class EmbeddingRecord:

    chunk_id: str = ""

    document_id: str = ""

    text: str = ""

    vector: List[float] = field(
        default_factory=list
    )

    dimension: int = 0

    model: str = ""

    provider: str = ""

    source: str = ""

    filename: str = ""

    page: Optional[int] = None

    section: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EMBEDDING RESULT
# ============================================================

@dataclass
class EmbeddingResult:

    records: List[EmbeddingRecord] = field(
        default_factory=list
    )

    model: str = ""

    provider: str = ""

    dimension: int = 0

    total_documents: int = 0

    successful_documents: int = 0

    failed_documents: int = 0

    success: bool = True

    error: Optional[str] = None

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# EMBEDDING CONFIGURATION
# ============================================================

@dataclass
class EmbeddingConfig:

    provider: str = "sentence-transformers"

    model_name: str = DEFAULT_SENTENCE_TRANSFORMER_MODEL

    batch_size: int = DEFAULT_BATCH_SIZE

    normalize_embeddings: bool = DEFAULT_NORMALIZE

    device: Optional[str] = None

    cache_enabled: bool = True

    cache_dir: Optional[str] = None

    show_progress: bool = False

    api_key: Optional[str] = None

    api_base: Optional[str] = None


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# DEPENDENCY CHECKS + VECTOR UTILITIES
# ============================================================


# ============================================================
# AVAILABILITY
# ============================================================

def is_numpy_available() -> bool:

    return np is not None


def is_sentence_transformers_available() -> bool:

    return SentenceTransformer is not None


def is_openai_available() -> bool:

    return OpenAI is not None


# ============================================================
# REQUIRE NUMPY
# ============================================================

def require_numpy() -> None:

    if np is None:

        raise ImportError(

            "numpy is required for embedding operations. "
            "Install using: pip install numpy"

        )


# ============================================================
# REQUIRE SENTENCE TRANSFORMERS
# ============================================================

def require_sentence_transformers() -> None:

    if SentenceTransformer is None:

        raise ImportError(

            "sentence-transformers is required. "
            "Install using: pip install sentence-transformers"

        )


# ============================================================
# REQUIRE OPENAI
# ============================================================

def require_openai() -> None:

    if OpenAI is None:

        raise ImportError(

            "openai is required for API embeddings. "
            "Install using: pip install openai"

        )


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(
    text: Any,
) -> str:

    if text is None:

        return ""

    return str(
        text
    ).strip()


# ============================================================
# L2 NORMALIZE
# ============================================================

def normalize_vector(
    vector: Sequence[float],
) -> List[float]:

    if not vector:

        return []

    magnitude = math.sqrt(

        sum(
            float(value) ** 2
            for value
            in vector
        )

    )

    if magnitude == 0:

        return [
            0.0
            for _ in vector
        ]

    return [

        float(value)
        /
        magnitude

        for value
        in vector

    ]


# ============================================================
# DOT PRODUCT
# ============================================================

def dot_product(
    vector_a: Sequence[float],
    vector_b: Sequence[float],
) -> float:

    if len(vector_a) != len(vector_b):

        raise ValueError(

            "Vectors must have identical dimensions."

        )

    return sum(

        float(a)
        *
        float(b)

        for a, b
        in zip(
            vector_a,
            vector_b,
        )

    )


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    vector_a: Sequence[float],
    vector_b: Sequence[float],
) -> float:

    if len(vector_a) != len(vector_b):

        raise ValueError(

            "Vectors must have identical dimensions."

        )

    if not vector_a:

        return 0.0

    norm_a = math.sqrt(

        sum(
            float(value) ** 2
            for value
            in vector_a
        )

    )

    norm_b = math.sqrt(

        sum(
            float(value) ** 2
            for value
            in vector_b
        )

    )

    if norm_a == 0 or norm_b == 0:

        return 0.0

    return (

        dot_product(
            vector_a,
            vector_b,
        )
        /
        (
            norm_a
            *
            norm_b
        )

    )


# ============================================================
# VECTOR DIMENSION
# ============================================================

def vector_dimension(
    vector: Sequence[float],
) -> int:

    return len(
        vector
    )


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# SENTENCE TRANSFORMER ENGINE
# ============================================================


# ============================================================
# EMBEDDING PROVIDER BASE
# ============================================================

class BaseEmbeddingProvider:

    provider_name = "base"

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> List[List[float]]:

        raise NotImplementedError

    def embed_query(
        self,
        text: str,
    ) -> List[float]:

        raise NotImplementedError


# ============================================================
# SENTENCE TRANSFORMER PROVIDER
# ============================================================

class SentenceTransformerProvider(
    BaseEmbeddingProvider
):

    provider_name = "sentence-transformers"

    def __init__(
        self,
        model_name: str = DEFAULT_SENTENCE_TRANSFORMER_MODEL,
        batch_size: int = DEFAULT_BATCH_SIZE,
        normalize_embeddings: bool = DEFAULT_NORMALIZE,
        device: Optional[str] = None,
        show_progress: bool = False,
    ) -> None:

        require_sentence_transformers()

        self.model_name = model_name

        self.batch_size = batch_size

        self.normalize_embeddings = (
            normalize_embeddings
        )

        self.device = device

        self.show_progress = show_progress

        logger.info(

            "Loading embedding model: %s",

            model_name,

        )

        kwargs = {}

        if device:

            kwargs["device"] = device

        self.model = SentenceTransformer(

            model_name,

            **kwargs,

        )

    # --------------------------------------------------------
    # Embed documents
    # --------------------------------------------------------

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> List[List[float]]:

        if not texts:

            return []

        cleaned = [

            clean_text(
                text
            )

            for text
            in texts

        ]

        embeddings = self.model.encode(

            cleaned,

            batch_size=self.batch_size,

            show_progress_bar=self.show_progress,

            normalize_embeddings=self.normalize_embeddings,

        )

        if hasattr(
            embeddings,
            "tolist",
        ):

            embeddings = embeddings.tolist()

        return [

            [
                float(value)
                for value
                in vector
            ]

            for vector
            in embeddings

        ]

    # --------------------------------------------------------
    # Embed query
    # --------------------------------------------------------

    def embed_query(
        self,
        text: str,
    ) -> List[float]:

        embeddings = self.embed_documents(
            [text]
        )

        if not embeddings:

            return []

        return embeddings[0]

    # --------------------------------------------------------
    # Dimension
    # --------------------------------------------------------

    def dimension(self) -> int:

        try:

            return int(
                self.model.get_sentence_embedding_dimension()
            )

        except Exception:

            vector = self.embed_query(
                "dimension test"
            )

            return len(
                vector
            )


# ============================================================
# PROVIDER FACTORY
# ============================================================

def create_embedding_provider(
    config: Optional[
        EmbeddingConfig
    ] = None,
) -> BaseEmbeddingProvider:

    if config is None:

        config = EmbeddingConfig()

    provider = (
        config.provider
        or
        "sentence-transformers"
    ).lower().strip()

    if provider in {

        "sentence-transformers",

        "sentence_transformers",

        "huggingface",

        "hugging-face",

        "hf",

    }:

        return SentenceTransformerProvider(

            model_name=config.model_name,

            batch_size=config.batch_size,

            normalize_embeddings=config.normalize_embeddings,

            device=config.device,

            show_progress=config.show_progress,

        )

    if provider in {

        "openai",

        "openai-compatible",

    }:

        return OpenAIEmbeddingProvider(

            model_name=config.model_name,

            api_key=config.api_key,

            api_base=config.api_base,

        )

    raise ValueError(

        f"Unsupported embedding provider: {provider}"

    )


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# OPENAI-COMPATIBLE EMBEDDING PROVIDER
# ============================================================


# ============================================================
# OPENAI PROVIDER
# ============================================================

class OpenAIEmbeddingProvider(
    BaseEmbeddingProvider
):

    provider_name = "openai"

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ) -> None:

        require_openai()

        self.model_name = model_name

        self.api_key = (

            api_key
            or
            os.getenv(
                "OPENAI_API_KEY"
            )

        )

        if not self.api_key:

            raise ValueError(

                "OPENAI_API_KEY is not configured."

            )

        kwargs = {

            "api_key":
                self.api_key,

        }

        if api_base:

            kwargs["base_url"] = api_base

        self.client = OpenAI(
            **kwargs
        )

    # --------------------------------------------------------
    # Embed documents
    # --------------------------------------------------------

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> List[List[float]]:

        if not texts:

            return []

        cleaned = [

            clean_text(
                text
            )

            for text
            in texts

        ]

        response = self.client.embeddings.create(

            model=self.model_name,

            input=cleaned,

        )

        # API returns records with an index.
        ordered = sorted(

            response.data,

            key=lambda item:
            item.index,

        )

        return [

            [
                float(value)
                for value
                in item.embedding
            ]

            for item
            in ordered

        ]

    # --------------------------------------------------------
    # Embed query
    # --------------------------------------------------------

    def embed_query(
        self,
        text: str,
    ) -> List[float]:

        embeddings = self.embed_documents(
            [text]
        )

        if not embeddings:

            return []

        return embeddings[0]


# ============================================================
# API KEY RESOLUTION
# ============================================================

def resolve_api_key(
    provider: str,
    explicit_key: Optional[str] = None,
) -> Optional[str]:

    if explicit_key:

        return explicit_key

    provider = (
        provider
        or
        ""
    ).lower()

    if provider == "openai":

        return os.getenv(
            "OPENAI_API_KEY"
        )

    # Compatible APIs may use a generic key.
    return (

        os.getenv(
            "EMBEDDING_API_KEY"
        )
        or
        os.getenv(
            "OPENAI_API_KEY"
        )

    )


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# EMBEDDING CACHE
# ============================================================


# ============================================================
# CACHE
# ============================================================

class EmbeddingCache:

    def __init__(
        self,
        cache_dir: Optional[
            Union[
                str,
                Path,
            ]
        ] = None,
    ) -> None:

        if cache_dir is None:

            cache_dir = (

                Path.home()
                /
                ".pragyanai"
                /
                "embedding_cache"

            )

        self.cache_dir = Path(
            cache_dir
        )

        self.cache_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

    # --------------------------------------------------------
    # CACHE KEY
    # --------------------------------------------------------

    def make_key(
        self,
        text: str,
        model: str,
        provider: str,
    ) -> str:

        payload = {

            "text":
                text,

            "model":
                model,

            "provider":
                provider,

        }

        serialized = json.dumps(

            payload,

            sort_keys=True,

            ensure_ascii=False,

        )

        return hashlib.sha256(

            serialized.encode(
                "utf-8"
            )

        ).hexdigest()

    # --------------------------------------------------------
    # PATH
    # --------------------------------------------------------

    def path_for_key(
        self,
        key: str,
    ) -> Path:

        return (
            self.cache_dir
            /
            f"{key}.json"
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def get(
        self,
        text: str,
        model: str,
        provider: str,
    ) -> Optional[
        List[float]
    ]:

        key = self.make_key(

            text=text,

            model=model,

            provider=provider,

        )

        path = self.path_for_key(
            key
        )

        if not path.exists():

            return None

        try:

            payload = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            vector = payload.get(
                "vector"
            )

            if not isinstance(
                vector,
                list,
            ):

                return None

            return [

                float(value)

                for value
                in vector

            ]

        except Exception as exc:

            logger.warning(

                "Embedding cache read failed: %s",

                exc,

            )

            return None

    # --------------------------------------------------------
    # SET
    # --------------------------------------------------------

    def set(
        self,
        text: str,
        model: str,
        provider: str,
        vector: Sequence[float],
    ) -> None:

        key = self.make_key(

            text=text,

            model=model,

            provider=provider,

        )

        path = self.path_for_key(
            key
        )

        payload = {

            "model":
                model,

            "provider":
                provider,

            "vector": [

                float(value)

                for value
                in vector

            ],

        }

        try:

            path.write_text(

                json.dumps(
                    payload
                ),

                encoding="utf-8",

            )

        except Exception as exc:

            logger.warning(

                "Embedding cache write failed: %s",

                exc,

            )

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    def clear(self) -> int:

        count = 0

        for path in self.cache_dir.glob(
            "*.json"
        ):

            try:

                path.unlink()

                count += 1

            except Exception:

                continue

        return count


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# EMBEDDING ENGINE
# ============================================================


# ============================================================
# EMBEDDING ENGINE
# ============================================================

class EmbeddingEngine:

    def __init__(
        self,
        config: Optional[
            EmbeddingConfig
        ] = None,
        provider: Optional[
            BaseEmbeddingProvider
        ] = None,
    ) -> None:

        self.config = (

            config
            or
            EmbeddingConfig()

        )

        self.provider = (

            provider
            or
            create_embedding_provider(
                self.config
            )

        )

        self.cache = None

        if self.config.cache_enabled:

            self.cache = EmbeddingCache(

                cache_dir=self.config.cache_dir

            )

        self.model_name = (
            self.config.model_name
        )

        self.provider_name = getattr(

            self.provider,

            "provider_name",

            self.config.provider,

        )

        self._dimension = None

        # Try obtaining dimension immediately.
        try:

            if hasattr(
                self.provider,
                "dimension",
            ):

                self._dimension = int(
                    self.provider.dimension()
                )

        except Exception:

            self._dimension = None

    # --------------------------------------------------------
    # Dimension
    # --------------------------------------------------------

    @property
    def dimension_value(
        self,
    ) -> int:

        if self._dimension:

            return self._dimension

        vector = self.embed_query(
            "dimension"
        )

        self._dimension = len(
            vector
        )

        return self._dimension

    # --------------------------------------------------------
    # Embed query
    # --------------------------------------------------------

    def embed_query(
        self,
        text: str,
    ) -> List[float]:

        text = clean_text(
            text
        )

        if not text:

            return []

        # Cache.
        if self.cache:

            cached = self.cache.get(

                text=text,

                model=self.model_name,

                provider=self.provider_name,

            )

            if cached is not None:

                return cached

        vector = self.provider.embed_query(
            text
        )

        vector = [

            float(value)

            for value
            in vector

        ]

        if self.config.normalize_embeddings:

            vector = normalize_vector(
                vector
            )

        if self.cache:

            self.cache.set(

                text=text,

                model=self.model_name,

                provider=self.provider_name,

                vector=vector,

            )

        self._dimension = len(
            vector
        )

        return vector

    # --------------------------------------------------------
    # Embed texts
    # --------------------------------------------------------

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> List[List[float]]:

        cleaned = [

            clean_text(
                text
            )

            for text
            in texts

        ]

        if not cleaned:

            return []

        vectors = [
            None
            for _ in cleaned
        ]

        missing_indices = []

        missing_texts = []

        # ----------------------------------------------------
        # Cache lookup
        # ----------------------------------------------------

        for index, text in enumerate(
            cleaned
        ):

            if not text:

                vectors[index] = []

                continue

            cached = None

            if self.cache:

                cached = self.cache.get(

                    text=text,

                    model=self.model_name,

                    provider=self.provider_name,

                )

            if cached is not None:

                vectors[index] = cached

            else:

                missing_indices.append(
                    index
                )

                missing_texts.append(
                    text
                )

        # ----------------------------------------------------
        # Provider call
        # ----------------------------------------------------

        if missing_texts:

            generated = self.provider.embed_documents(

                missing_texts

            )

            if len(generated) != len(
                missing_texts
            ):

                raise RuntimeError(

                    "Embedding provider returned an "
                    "unexpected number of vectors."

                )

            for index, vector in zip(

                missing_indices,

                generated,

            ):

                vector = [

                    float(value)

                    for value
                    in vector

                ]

                if self.config.normalize_embeddings:

                    vector = normalize_vector(
                        vector
                    )

                vectors[index] = vector

                if self.cache:

                    self.cache.set(

                        text=cleaned[index],

                        model=self.model_name,

                        provider=self.provider_name,

                        vector=vector,

                    )

        output = [

            vector
            if vector is not None
            else []

            for vector
            in vectors

        ]

        non_empty = [

            vector

            for vector
            in output

            if vector

        ]

        if non_empty:

            self._dimension = len(
                non_empty[0]
            )

        return output

    # --------------------------------------------------------
    # Embed chunks
    # --------------------------------------------------------

    def embed_chunks(
        self,
        chunks: Sequence[Any],
    ) -> EmbeddingResult:

        try:

            if not chunks:

                return EmbeddingResult(

                    model=self.model_name,

                    provider=self.provider_name,

                    dimension=self._dimension or 0,

                    total_documents=0,

                    successful_documents=0,

                    failed_documents=0,

                    success=True,

                )

            texts = []

            for chunk in chunks:

                text = getattr(
                    chunk,
                    "text",
                    None,
                )

                if text is None:

                    text = getattr(
                        chunk,
                        "page_content",
                        "",
                    )

                texts.append(
                    clean_text(
                        text
                    )
                )

            vectors = self.embed_texts(
                texts
            )

            records = []

            failed = 0

            for chunk, vector in zip(

                chunks,
                vectors,

            ):

                if not vector:

                    failed += 1

                    continue

                metadata = dict(

                    getattr(
                        chunk,
                        "metadata",
                        {},
                    )
                    or
                    {}

                )

                chunk_id = getattr(

                    chunk,

                    "chunk_id",

                    metadata.get(
                        "chunk_id",
                        "",
                    ),

                )

                document_id = getattr(

                    chunk,

                    "parent_document_id",

                    metadata.get(
                        "document_id",
                        "",
                    ),

                )

                record = EmbeddingRecord(

                    chunk_id=chunk_id,

                    document_id=document_id,

                    text=texts[
                        len(records)
                    ]
                    if len(records) < len(texts)
                    else "",

                    vector=vector,

                    dimension=len(
                        vector
                    ),

                    model=self.model_name,

                    provider=self.provider_name,

                    source=getattr(

                        chunk,

                        "source",

                        metadata.get(
                            "source",
                            "",
                        ),

                    ),

                    filename=getattr(

                        chunk,

                        "filename",

                        metadata.get(
                            "filename",
                            "",
                        ),

                    ),

                    page=getattr(

                        chunk,

                        "page",

                        metadata.get(
                            "page"
                        ),

                    ),

                    section=getattr(

                        chunk,

                        "section",

                        metadata.get(
                            "section",
                            "",
                        ),

                    ),

                    metadata=metadata,

                )

                records.append(
                    record
                )

            successful = len(
                records
            )

            dimension = (

                len(
                    records[0].vector
                )

                if records

                else
                self._dimension
                or
                0

            )

            return EmbeddingResult(

                records=records,

                model=self.model_name,

                provider=self.provider_name,

                dimension=dimension,

                total_documents=len(
                    chunks
                ),

                successful_documents=successful,

                failed_documents=failed,

                success=failed == 0,

                warnings=(

                    [
                        "Some chunks could not be embedded."
                    ]

                    if failed

                    else []

                ),

            )

        except Exception as exc:

            logger.exception(
                "Chunk embedding failed."
            )

            return EmbeddingResult(

                model=self.model_name,

                provider=self.provider_name,

                success=False,

                error=str(
                    exc
                ),

            )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# SIMILARITY SEARCH
# ============================================================


# ============================================================
# SIMILARITY RESULT
# ============================================================

@dataclass
class SimilarityResult:

    chunk_id: str = ""

    score: float = 0.0

    text: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    record: Optional[
        EmbeddingRecord
    ] = None


# ============================================================
# SEARCH EMBEDDINGS
# ============================================================

def similarity_search(
    query_vector: Sequence[float],
    records: Sequence[EmbeddingRecord],
    top_k: int = 5,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> List[SimilarityResult]:

    if not query_vector:

        return []

    if top_k <= 0:

        return []

    results = []

    for record in records:

        if not record.vector:

            continue

        try:

            score = cosine_similarity(

                query_vector,

                record.vector,

            )

        except ValueError:

            logger.warning(

                "Skipping vector with incompatible dimension: %s",

                record.chunk_id,

            )

            continue

        if score < threshold:

            continue

        results.append(

            SimilarityResult(

                chunk_id=record.chunk_id,

                score=round(
                    score,
                    6,
                ),

                text=record.text,

                metadata=dict(
                    record.metadata
                ),

                record=record,

            )

        )

    results.sort(

        key=lambda item:
        item.score,

        reverse=True,

    )

    return results[
        :top_k
    ]


# ============================================================
# QUERY ENGINE
# ============================================================

def query_embeddings(
    query: str,
    engine: EmbeddingEngine,
    records: Sequence[EmbeddingRecord],
    top_k: int = 5,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> List[SimilarityResult]:

    query_vector = engine.embed_query(
        query
    )

    return similarity_search(

        query_vector=query_vector,

        records=records,

        top_k=top_k,

        threshold=threshold,

    )


# ============================================================
# BATCH SIMILARITY
# ============================================================

def batch_similarity_search(
    queries: Sequence[str],
    engine: EmbeddingEngine,
    records: Sequence[EmbeddingRecord],
    top_k: int = 5,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> Dict[
    str,
    List[SimilarityResult]
]:

    output = {}

    for query in queries:

        output[query] = query_embeddings(

            query=query,

            engine=engine,

            records=records,

            top_k=top_k,

            threshold=threshold,

        )

    return output


# ============================================================
# MAXIMUM SIMILARITY
# ============================================================

def maximum_similarity(
    vector: Sequence[float],
    records: Sequence[EmbeddingRecord],
) -> float:

    if not vector:

        return 0.0

    scores = []

    for record in records:

        if not record.vector:

            continue

        try:

            scores.append(

                cosine_similarity(

                    vector,

                    record.vector,

                )

            )

        except ValueError:

            continue

    if not scores:

        return 0.0

    return max(
        scores
    )


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# SERIALIZATION + PERSISTENCE
# ============================================================


# ============================================================
# RECORD → DICT
# ============================================================

def embedding_record_to_dict(
    record: EmbeddingRecord,
) -> Dict[str, Any]:

    metadata = dict(
        record.metadata
    )

    metadata.update({

        "chunk_id":
            record.chunk_id,

        "document_id":
            record.document_id,

        "source":
            record.source,

        "filename":
            record.filename,

        "page":
            record.page,

        "section":
            record.section,

        "model":
            record.model,

        "provider":
            record.provider,

        "dimension":
            record.dimension,

    })

    return {

        "chunk_id":
            record.chunk_id,

        "document_id":
            record.document_id,

        "text":
            record.text,

        "vector":
            record.vector,

        "dimension":
            record.dimension,

        "model":
            record.model,

        "provider":
            record.provider,

        "source":
            record.source,

        "filename":
            record.filename,

        "page":
            record.page,

        "section":
            record.section,

        "metadata":
            metadata,

    }


# ============================================================
# DICT → RECORD
# ============================================================

def dict_to_embedding_record(
    data: Mapping[str, Any],
) -> EmbeddingRecord:

    vector = data.get(
        "vector",
        [],
    )

    return EmbeddingRecord(

        chunk_id=str(
            data.get(
                "chunk_id",
                "",
            )
        ),

        document_id=str(
            data.get(
                "document_id",
                "",
            )
        ),

        text=str(
            data.get(
                "text",
                "",
            )
        ),

        vector=[

            float(value)

            for value
            in vector

        ],

        dimension=int(

            data.get(
                "dimension",
                len(vector),
            )

        ),

        model=str(
            data.get(
                "model",
                "",
            )
        ),

        provider=str(
            data.get(
                "provider",
                "",
            )
        ),

        source=str(
            data.get(
                "source",
                "",
            )
        ),

        filename=str(
            data.get(
                "filename",
                "",
            )
        ),

        page=data.get(
            "page"
        ),

        section=str(
            data.get(
                "section",
                "",
            )
        ),

        metadata=dict(

            data.get(
                "metadata",
                {},
            )
            or
            {}

        ),

    )


# ============================================================
# SAVE EMBEDDINGS
# ============================================================

def save_embeddings(
    records: Sequence[EmbeddingRecord],
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

    payload = [

        embedding_record_to_dict(
            record
        )

        for record
        in records

    ]

    path.write_text(

        json.dumps(

            payload,

            ensure_ascii=False,

        ),

        encoding="utf-8",

    )

    return path


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

def load_embeddings(
    file_path: Union[
        str,
        Path,
    ],
) -> List[EmbeddingRecord]:

    path = Path(
        file_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Embedding file does not exist: {path}"
        )

    payload = json.loads(

        path.read_text(
            encoding="utf-8"
        )

    )

    if not isinstance(
        payload,
        list,
    ):

        raise ValueError(

            "Embedding file must contain a JSON list."

        )

    return [

        dict_to_embedding_record(
            item
        )

        for item
        in payload

    ]


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# BATCH PROCESSING + RAG HELPERS
# ============================================================


# ============================================================
# EMBED CHUNK LIST
# ============================================================

def embed_chunks(
    chunks: Sequence[Any],
    config: Optional[
        EmbeddingConfig
    ] = None,
) -> EmbeddingResult:

    engine = EmbeddingEngine(
        config=config
    )

    return engine.embed_chunks(
        chunks
    )


# ============================================================
# EMBED TEXTS
# ============================================================

def embed_texts(
    texts: Sequence[str],
    config: Optional[
        EmbeddingConfig
    ] = None,
) -> List[List[float]]:

    engine = EmbeddingEngine(
        config=config
    )

    return engine.embed_texts(
        texts
    )


# ============================================================
# EMBED QUERY
# ============================================================

def embed_query(
    query: str,
    config: Optional[
        EmbeddingConfig
    ] = None,
) -> List[float]:

    engine = EmbeddingEngine(
        config=config
    )

    return engine.embed_query(
        query
    )


# ============================================================
# RESULT STATISTICS
# ============================================================

def embedding_statistics(
    records: Sequence[EmbeddingRecord],
) -> Dict[str, Any]:

    if not records:

        return {

            "record_count":
                0,

            "dimension":
                0,

            "models":
                [],

            "providers":
                [],

        }

    dimensions = [

        record.dimension

        for record
        in records

        if record.dimension > 0

    ]

    models = sorted(
        set(

            record.model

            for record
            in records

            if record.model

        )
    )

    providers = sorted(
        set(

            record.provider

            for record
            in records

            if record.provider

        )
    )

    return {

        "record_count":
            len(records),

        "dimension": (

            dimensions[0]
            if dimensions
            else 0

        ),

        "models":
            models,

        "providers":
            providers,

        "total_vector_values":
            sum(
                record.dimension
                for record
                in records
            ),

        "sources":
            len(
                set(

                    record.source

                    for record
                    in records

                    if record.source

                )
            ),

        "documents":
            len(
                set(

                    record.document_id

                    for record
                    in records

                    if record.document_id

                )
            ),

    }


# ============================================================
# VALIDATE EMBEDDINGS
# ============================================================

def validate_embeddings(
    records: Sequence[EmbeddingRecord],
) -> Dict[str, Any]:

    errors = []

    warnings = []

    if not records:

        warnings.append(
            "No embedding records found."
        )

        return {

            "valid":
                True,

            "errors":
                errors,

            "warnings":
                warnings,

        }

    dimensions = set()

    for index, record in enumerate(
        records
    ):

        if not record.vector:

            errors.append(

                f"Record {index} has no vector."

            )

            continue

        dimensions.add(
            len(
                record.vector
            )
        )

        if (
            record.dimension
            !=
            len(
                record.vector
            )
        ):

            errors.append(

                f"Record {index} dimension mismatch."

            )

        if not record.chunk_id:

            warnings.append(

                f"Record {index} has no chunk_id."

            )

    if len(dimensions) > 1:

        errors.append(

            "Embedding vectors have inconsistent dimensions."

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
# FORMAT RAG CONTEXT
# ============================================================

def format_rag_context(
    results: Sequence[SimilarityResult],
) -> str:

    sections = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        record = result.record

        source = (

            record.source

            if record

            else result.metadata.get(
                "source",
                "",
            )

        )

        page = (

            record.page

            if record

            else result.metadata.get(
                "page"
            )

        )

        section = (

            record.section

            if record

            else result.metadata.get(
                "section",
                "",
            )

        )

        header_parts = [

            f"[Source {index}]",

            f"Score: {result.score:.4f}",

        ]

        if source:

            header_parts.append(
                f"Source: {source}"
            )

        if page is not None:

            header_parts.append(
                f"Page: {page}"
            )

        if section:

            header_parts.append(
                f"Section: {section}"
            )

        sections.append(

            "\n".join(

                header_parts
                +
                [
                    result.text
                ]

            )

        )

    return "\n\n".join(
        sections
    )


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# PRESETS + SUMMARY + EXPORTS + SELF TEST
# ============================================================


# ============================================================
# LOCAL EMBEDDING CONFIG
# ============================================================

def local_embedding_config(
    model_name: str = DEFAULT_SENTENCE_TRANSFORMER_MODEL,
) -> EmbeddingConfig:

    return EmbeddingConfig(

        provider="sentence-transformers",

        model_name=model_name,

        batch_size=32,

        normalize_embeddings=True,

        cache_enabled=True,

        show_progress=False,

    )


# ============================================================
# OPENAI EMBEDDING CONFIG
# ============================================================

def openai_embedding_config(
    model_name: str = "text-embedding-3-small",
) -> EmbeddingConfig:

    return EmbeddingConfig(

        provider="openai",

        model_name=model_name,

        batch_size=32,

        normalize_embeddings=True,

        cache_enabled=True,

        api_key=os.getenv(
            "OPENAI_API_KEY"
        ),

    )


# ============================================================
# EMBEDDING SUMMARY
# ============================================================

def embedding_summary(
    result: EmbeddingResult,
) -> Dict[str, Any]:

    return {

        "embeddings_version":
            EMBEDDINGS_VERSION,

        "success":
            result.success,

        "model":
            result.model,

        "provider":
            result.provider,

        "dimension":
            result.dimension,

        "total_documents":
            result.total_documents,

        "successful_documents":
            result.successful_documents,

        "failed_documents":
            result.failed_documents,

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
    "EMBEDDINGS_VERSION",

    # Models
    "EmbeddingRecord",

    "EmbeddingResult",

    "EmbeddingConfig",

    "SimilarityResult",

    # Availability
    "is_numpy_available",

    "is_sentence_transformers_available",

    "is_openai_available",

    "require_numpy",

    "require_sentence_transformers",

    "require_openai",

    # Vector utilities
    "clean_text",

    "normalize_vector",

    "dot_product",

    "cosine_similarity",

    "vector_dimension",

    # Providers
    "BaseEmbeddingProvider",

    "SentenceTransformerProvider",

    "OpenAIEmbeddingProvider",

    "create_embedding_provider",

    "resolve_api_key",

    # Cache
    "EmbeddingCache",

    # Engine
    "EmbeddingEngine",

    # Similarity
    "similarity_search",

    "query_embeddings",

    "batch_similarity_search",

    "maximum_similarity",

    # Serialization
    "embedding_record_to_dict",

    "dict_to_embedding_record",

    "save_embeddings",

    "load_embeddings",

    # High-level
    "embed_chunks",

    "embed_texts",

    "embed_query",

    # Statistics
    "embedding_statistics",

    "validate_embeddings",

    "format_rag_context",

    "embedding_summary",

    # Presets
    "local_embedding_config",

    "openai_embedding_config",

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
        "EMBEDDINGS SELF TEST"
    )

    print(
        "============================================"
    )

    print(
        "\nNumPy available:"
    )

    print(
        is_numpy_available()
    )

    print(
        "\nSentenceTransformers available:"
    )

    print(
        is_sentence_transformers_available()
    )

    print(
        "\nOpenAI available:"
    )

    print(
        is_openai_available()
    )

    # --------------------------------------------------------
    # Vector test
    # --------------------------------------------------------

    vector_a = [
        1.0,
        0.0,
        0.0,
    ]

    vector_b = [
        0.8,
        0.6,
        0.0,
    ]

    print(
        "\nCosine Similarity:"
    )

    print(

        cosine_similarity(

            vector_a,

            vector_b,

        )

    )

    # --------------------------------------------------------
    # Normalization
    # --------------------------------------------------------

    print(
        "\nNormalized Vector:"
    )

    print(
        normalize_vector(
            [
                3.0,
                4.0,
            ]
        )
    )

    # --------------------------------------------------------
    # Embedding records
    # --------------------------------------------------------

    record_1 = EmbeddingRecord(

        chunk_id="chunk-001",

        document_id="doc-001",

        text=(
            "Generative AI and "
            "large language models."
        ),

        vector=[
            1.0,
            0.0,
            0.0,
        ],

        dimension=3,

        model="demo-model",

        provider="demo",

        source="curriculum.pdf",

        filename="curriculum.pdf",

        page=1,

        section="Generative AI",

        metadata={

            "skill":
                "Generative AI",

        },

    )

    record_2 = EmbeddingRecord(

        chunk_id="chunk-002",

        document_id="doc-001",

        text=(
            "Python programming "
            "and machine learning."
        ),

        vector=[
            0.8,
            0.6,
            0.0,
        ],

        dimension=3,

        model="demo-model",

        provider="demo",

        source="curriculum.pdf",

        filename="curriculum.pdf",

        page=2,

        section="Machine Learning",

        metadata={

            "skill":
                "Python",

        },

    )

    records = [

        record_1,

        record_2,

    ]

    # --------------------------------------------------------
    # Similarity
    # --------------------------------------------------------

    results = similarity_search(

        query_vector=[
            1.0,
            0.0,
            0.0,
        ],

        records=records,

        top_k=2,

        threshold=0.0,

    )

    print(
        "\nSimilarity Results:"
    )

    for result in results:

        print(

            result.chunk_id,

            result.score,

            result.text,

        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print(
        "\nEmbedding Statistics:"
    )

    print(
        embedding_statistics(
            records
        )
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print(
        "\nValidation:"
    )

    print(
        validate_embeddings(
            records
        )
    )

    # --------------------------------------------------------
    # RAG context
    # --------------------------------------------------------

    print(
        "\nRAG Context:"
    )

    print(
        format_rag_context(
            results
        )
    )

    # --------------------------------------------------------
    # Serialization test
    # --------------------------------------------------------

    payload = embedding_record_to_dict(
        record_1
    )

    restored = dict_to_embedding_record(
        payload
    )

    print(
        "\nSerialization Test:"
    )

    print(
        restored
    )

    print(
        "\n============================================"
    )

    print(
        "EMBEDDINGS TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF rag/embeddings.py
# ============================================================
