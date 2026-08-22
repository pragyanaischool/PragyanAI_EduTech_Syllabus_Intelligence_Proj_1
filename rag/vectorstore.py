# ============================================================
# rag/vectorstore.py
# CHUNK 1/10
#
# VECTOR STORE
#
# Purpose:
#   Persistent vector storage and semantic retrieval for the
#   PragyanAI RAG pipeline.
#
# Supports:
#   - FAISS
#   - Chroma
#   - NumPy/Python fallback
#   - Similarity search
#   - Metadata filtering
#   - MMR retrieval
#   - Persistent storage
#   - Save / load
#   - Delete documents
#   - Delete chunks
#   - RAG context generation
#
# Works with:
#   rag/chunker.py
#   rag/embeddings.py
#
# Recommended:
#
#   pip install numpy
#   pip install faiss-cpu
#
# Optional:
#
#   pip install chromadb
#
# ============================================================

from __future__ import annotations

import json
import logging
import math
import os
import pickle

from dataclasses import dataclass, field

from pathlib import Path

from typing import (
    Any,
    Callable,
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
# LOCAL IMPORTS
# ============================================================

try:

    from .embeddings import (
        EmbeddingEngine,
        EmbeddingRecord,
        SimilarityResult,
        cosine_similarity,
    )

except ImportError:

    from embeddings import (
        EmbeddingEngine,
        EmbeddingRecord,
        SimilarityResult,
        cosine_similarity,
    )


# ============================================================
# OPTIONAL NUMPY
# ============================================================

try:

    import numpy as np

except ImportError:

    np = None


# ============================================================
# OPTIONAL FAISS
# ============================================================

try:

    import faiss

except ImportError:

    faiss = None


# ============================================================
# OPTIONAL CHROMA
# ============================================================

try:

    import chromadb

except ImportError:

    chromadb = None


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# VERSION
# ============================================================

VECTORSTORE_VERSION = "1.0.0"


# ============================================================
# DEFAULTS
# ============================================================

DEFAULT_TOP_K = 5

DEFAULT_SCORE_THRESHOLD = 0.30

DEFAULT_COLLECTION_NAME = "pragyanai_rag"

DEFAULT_BACKEND = "auto"


# ============================================================
# VECTOR STORE RECORD
# ============================================================

@dataclass
class VectorRecord:

    id: str = ""

    vector: List[float] = field(
        default_factory=list
    )

    text: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    document_id: str = ""

    chunk_id: str = ""

    source: str = ""

    filename: str = ""

    page: Optional[int] = None

    section: str = ""

    score: float = 0.0


# ============================================================
# RETRIEVAL RESULT
# ============================================================

@dataclass
class RetrievalResult:

    records: List[VectorRecord] = field(
        default_factory=list
    )

    query: str = ""

    top_k: int = DEFAULT_TOP_K

    total_candidates: int = 0

    backend: str = ""

    success: bool = True

    error: Optional[str] = None

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# VECTOR STORE CONFIG
# ============================================================

@dataclass
class VectorStoreConfig:

    backend: str = DEFAULT_BACKEND

    persist_directory: str = "./data/vectorstore"

    collection_name: str = DEFAULT_COLLECTION_NAME

    dimension: Optional[int] = None

    metric: str = "cosine"

    top_k: int = DEFAULT_TOP_K

    score_threshold: float = DEFAULT_SCORE_THRESHOLD

    normalize_vectors: bool = True

    allow_duplicates: bool = False

    metadata_filter_enabled: bool = True


# ============================================================
# END CHUNK 1
# ============================================================
# ============================================================
# CHUNK 2/10
#
# BACKEND DETECTION + VECTOR UTILITIES
# ============================================================


# ============================================================
# AVAILABILITY
# ============================================================

def is_numpy_available() -> bool:

    return np is not None


def is_faiss_available() -> bool:

    return faiss is not None


def is_chroma_available() -> bool:

    return chromadb is not None


# ============================================================
# BACKEND DETECTION
# ============================================================

def detect_backend(
    requested: str = "auto",
) -> str:

    requested = (
        requested
        or
        "auto"
    ).lower().strip()

    if requested != "auto":

        supported = {
            "faiss",
            "chroma",
            "numpy",
            "memory",
        }

        if requested not in supported:

            raise ValueError(

                f"Unsupported vector store backend: "
                f"{requested}. "
                f"Supported: {sorted(supported)}"

            )

        if requested == "faiss" and faiss is None:

            raise ImportError(

                "FAISS is not installed. "
                "Install using: pip install faiss-cpu"

            )

        if requested == "chroma" and chromadb is None:

            raise ImportError(

                "ChromaDB is not installed. "
                "Install using: pip install chromadb"

            )

        return requested

    # Prefer FAISS.
    if faiss is not None:

        return "faiss"

    # Then Chroma.
    if chromadb is not None:

        return "chroma"

    # Then NumPy.
    if np is not None:

        return "numpy"

    # Pure Python fallback.
    return "memory"


# ============================================================
# REQUIRE NUMPY
# ============================================================

def require_numpy() -> None:

    if np is None:

        raise ImportError(

            "numpy is required for vector operations. "
            "Install using: pip install numpy"

        )


# ============================================================
# NORMALIZE VECTOR
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

            for _
            in vector

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
    a: Sequence[float],
    b: Sequence[float],
) -> float:

    if len(a) != len(b):

        raise ValueError(

            "Vector dimensions do not match."

        )

    return sum(

        float(x)
        *
        float(y)

        for x, y
        in zip(
            a,
            b,
        )

    )


# ============================================================
# COSINE
# ============================================================

def cosine(
    a: Sequence[float],
    b: Sequence[float],
) -> float:

    if not a or not b:

        return 0.0

    if len(a) != len(b):

        return 0.0

    return cosine_similarity(
        a,
        b,
    )


# ============================================================
# END CHUNK 2
# ============================================================
# ============================================================
# CHUNK 3/10
#
# METADATA FILTERING
# ============================================================


# ============================================================
# GET NESTED VALUE
# ============================================================

def get_metadata_value(
    metadata: Mapping[str, Any],
    key: str,
) -> Any:

    if key in metadata:

        return metadata[key]

    # Support nested keys:
    #
    # "document.course.name"
    #
    current: Any = metadata

    for part in key.split("."):

        if not isinstance(
            current,
            Mapping,
        ):

            return None

        if part not in current:

            return None

        current = current[part]

    return current


# ============================================================
# MATCH CONDITION
# ============================================================

def match_condition(
    value: Any,
    expected: Any,
) -> bool:

    # Equality.
    if not isinstance(
        expected,
        Mapping,
    ):

        if isinstance(
            value,
            str,
        ):

            return (

                value.lower()
                ==
                str(
                    expected
                ).lower()

            )

        return value == expected

    # --------------------------------------------------------
    # Operators
    # --------------------------------------------------------

    if "$eq" in expected:

        if value != expected["$eq"]:

            return False

    if "$ne" in expected:

        if value == expected["$ne"]:

            return False

    if "$in" in expected:

        if value not in expected["$in"]:

            return False

    if "$nin" in expected:

        if value in expected["$nin"]:

            return False

    if "$contains" in expected:

        if value is None:

            return False

        if (
            str(
                expected["$contains"]
            ).lower()
            not in
            str(
                value
            ).lower()
        ):

            return False

    if "$gt" in expected:

        try:

            if not value > expected["$gt"]:

                return False

        except Exception:

            return False

    if "$gte" in expected:

        try:

            if not value >= expected["$gte"]:

                return False

        except Exception:

            return False

    if "$lt" in expected:

        try:

            if not value < expected["$lt"]:

                return False

        except Exception:

            return False

    if "$lte" in expected:

        try:

            if not value <= expected["$lte"]:

                return False

        except Exception:

            return False

    return True


# ============================================================
# MATCH METADATA
# ============================================================

def metadata_matches(
    metadata: Mapping[str, Any],
    filters: Optional[
        Mapping[str, Any]
    ] = None,
) -> bool:

    if not filters:

        return True

    # --------------------------------------------------------
    # Logical AND
    # --------------------------------------------------------

    if "$and" in filters:

        conditions = filters[
            "$and"
        ]

        if not all(

            metadata_matches(
                metadata,
                condition,
            )

            for condition
            in conditions

        ):

            return False

    # --------------------------------------------------------
    # Logical OR
    # --------------------------------------------------------

    if "$or" in filters:

        conditions = filters[
            "$or"
        ]

        if not any(

            metadata_matches(
                metadata,
                condition,
            )

            for condition
            in conditions

        ):

            return False

    # --------------------------------------------------------
    # Individual fields
    # --------------------------------------------------------

    for key, expected in filters.items():

        if key.startswith(
            "$"
        ):

            continue

        value = get_metadata_value(

            metadata,

            key,

        )

        if not match_condition(

            value,

            expected,

        ):

            return False

    return True


# ============================================================
# FILTER RECORDS
# ============================================================

def filter_records(
    records: Sequence[VectorRecord],
    filters: Optional[
        Mapping[str, Any]
    ] = None,
) -> List[VectorRecord]:

    if not filters:

        return list(
            records
        )

    return [

        record

        for record
        in records

        if metadata_matches(

            record.metadata,

            filters,

        )

    ]


# ============================================================
# END CHUNK 3
# ============================================================
# ============================================================
# CHUNK 4/10
#
# BASE BACKEND + NUMPY/MEMORY BACKEND
# ============================================================


# ============================================================
# BASE BACKEND
# ============================================================

class BaseVectorBackend:

    backend_name = "base"

    def add_records(
        self,
        records: Sequence[VectorRecord],
    ) -> int:

        raise NotImplementedError

    def delete(
        self,
        ids: Optional[
            Sequence[str]
        ] = None,
        document_ids: Optional[
            Sequence[str]
        ] = None,
    ) -> int:

        raise NotImplementedError

    def search(
        self,
        query_vector: Sequence[float],
        top_k: int = DEFAULT_TOP_K,
        threshold: float = DEFAULT_SCORE_THRESHOLD,
        filters: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> List[VectorRecord]:

        raise NotImplementedError

    def count(self) -> int:

        raise NotImplementedError

    def clear(self) -> None:

        raise NotImplementedError


# ============================================================
# MEMORY BACKEND
# ============================================================

class MemoryVectorBackend(
    BaseVectorBackend
):

    backend_name = "memory"

    def __init__(
        self,
        normalize_vectors: bool = True,
    ) -> None:

        self.normalize_vectors = (
            normalize_vectors
        )

        self.records: Dict[
            str,
            VectorRecord
        ] = {}

    # --------------------------------------------------------
    # Add
    # --------------------------------------------------------

    def add_records(
        self,
        records: Sequence[VectorRecord],
    ) -> int:

        added = 0

        for record in records:

            vector = list(
                record.vector
            )

            if self.normalize_vectors:

                vector = normalize_vector(
                    vector
                )

            record.vector = vector

            self.records[
                record.id
            ] = record

            added += 1

        return added

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    def delete(
        self,
        ids: Optional[
            Sequence[str]
        ] = None,
        document_ids: Optional[
            Sequence[str]
        ] = None,
    ) -> int:

        ids = set(
            ids
            or
            []
        )

        document_ids = set(
            document_ids
            or
            []
        )

        removed = 0

        for record_id in list(
            self.records.keys()
        ):

            record = self.records[
                record_id
            ]

            should_delete = False

            if record_id in ids:

                should_delete = True

            if (
                record.document_id
                in document_ids
            ):

                should_delete = True

            if should_delete:

                del self.records[
                    record_id
                ]

                removed += 1

        return removed

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    def search(
        self,
        query_vector: Sequence[float],
        top_k: int = DEFAULT_TOP_K,
        threshold: float = DEFAULT_SCORE_THRESHOLD,
        filters: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> List[VectorRecord]:

        candidates = filter_records(

            list(
                self.records.values()
            ),

            filters,

        )

        results = []

        for record in candidates:

            score = cosine(

                query_vector,

                record.vector,

            )

            if score < threshold:

                continue

            record.score = score

            results.append(
                record
            )

        results.sort(

            key=lambda item:
            item.score,

            reverse=True,

        )

        return results[
            :top_k
        ]

    # --------------------------------------------------------
    # Count
    # --------------------------------------------------------

    def count(self) -> int:

        return len(
            self.records
        )

    # --------------------------------------------------------
    # Clear
    # --------------------------------------------------------

    def clear(self) -> None:

        self.records.clear()


# ============================================================
# NUMPY BACKEND
# ============================================================

class NumpyVectorBackend(
    MemoryVectorBackend
):

    backend_name = "numpy"

    # The inherited implementation is deliberately retained.
    #
    # For moderate-sized RAG collections this provides a simple
    # zero-dependency fallback. FAISS should be preferred for
    # very large collections.


# ============================================================
# END CHUNK 4
# ============================================================
# ============================================================
# CHUNK 5/10
#
# FAISS BACKEND
# ============================================================


# ============================================================
# FAISS BACKEND
# ============================================================

class FAISSVectorBackend(
    BaseVectorBackend
):

    backend_name = "faiss"

    def __init__(
        self,
        dimension: Optional[int] = None,
        normalize_vectors: bool = True,
        index_path: Optional[
            Union[
                str,
                Path,
            ]
        ] = None,
        metadata_path: Optional[
            Union[
                str,
                Path,
            ]
        ] = None,
    ) -> None:

        if faiss is None:

            raise ImportError(

                "FAISS is not installed. "
                "Install using: pip install faiss-cpu"

            )

        if np is None:

            raise ImportError(

                "NumPy is required by FAISS."

            )

        self.dimension = dimension

        self.normalize_vectors = (
            normalize_vectors
        )

        self.index_path = (

            Path(index_path)
            if index_path
            else None

        )

        self.metadata_path = (

            Path(metadata_path)
            if metadata_path
            else None

        )

        self.index = None

        self.records: Dict[
            str,
            VectorRecord
        ] = {}

        self.id_order: List[
            str
        ] = []

        if (
            self.index_path
            and
            self.metadata_path
            and
            self.index_path.exists()
            and
            self.metadata_path.exists()
        ):

            self.load()

    # --------------------------------------------------------
    # Create index
    # --------------------------------------------------------

    def _create_index(
        self,
        dimension: int,
    ) -> None:

        self.dimension = dimension

        # Inner product on normalized vectors =
        # cosine similarity.
        self.index = faiss.IndexFlatIP(
            dimension
        )

    # --------------------------------------------------------
    # Add
    # --------------------------------------------------------

    def add_records(
        self,
        records: Sequence[VectorRecord],
    ) -> int:

        if not records:

            return 0

        vectors = []

        new_records = []

        for record in records:

            vector = list(
                record.vector
            )

            if not vector:

                continue

            if self.dimension is None:

                self._create_index(
                    len(vector)
                )

            if len(vector) != self.dimension:

                raise ValueError(

                    f"Vector dimension "
                    f"{len(vector)} does not match "
                    f"FAISS dimension "
                    f"{self.dimension}."

                )

            if self.normalize_vectors:

                vector = normalize_vector(
                    vector
                )

            # Avoid duplicate IDs.
            if record.id in self.records:

                continue

            vectors.append(
                vector
            )

            new_records.append(
                record
            )

        if not vectors:

            return 0

        matrix = np.asarray(

            vectors,

            dtype="float32",

        )

        self.index.add(
            matrix
        )

        for record in new_records:

            self.records[
                record.id
            ] = record

            self.id_order.append(
                record.id
            )

        self.save()

        return len(
            new_records
        )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    def search(
        self,
        query_vector: Sequence[float],
        top_k: int = DEFAULT_TOP_K,
        threshold: float = DEFAULT_SCORE_THRESHOLD,
        filters: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> List[VectorRecord]:

        if self.index is None:

            return []

        if not query_vector:

            return []

        vector = list(
            query_vector
        )

        if self.normalize_vectors:

            vector = normalize_vector(
                vector
            )

        if len(vector) != self.dimension:

            raise ValueError(

                "Query vector dimension does not "
                "match FAISS index dimension."

            )

        # Search more candidates because metadata
        # filtering happens after FAISS retrieval.
        search_k = min(

            max(
                top_k * 10,
                top_k,
            ),

            len(
                self.id_order
            ),

        )

        if search_k <= 0:

            return []

        matrix = np.asarray(

            [vector],

            dtype="float32",

        )

        scores, indices = self.index.search(

            matrix,

            search_k,

        )

        results = []

        for score, index in zip(

            scores[0],

            indices[0],

        ):

            if index < 0:

                continue

            if index >= len(
                self.id_order
            ):

                continue

            record_id = self.id_order[
                index
            ]

            record = self.records.get(
                record_id
            )

            if record is None:

                continue

            if not metadata_matches(

                record.metadata,

                filters,

            ):

                continue

            score = float(
                score
            )

            if score < threshold:

                continue

            record.score = score

            results.append(
                record
            )

            if len(results) >= top_k:

                break

        return results

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    def delete(
        self,
        ids: Optional[
            Sequence[str]
        ] = None,
        document_ids: Optional[
            Sequence[str]
        ] = None,
    ) -> int:

        ids = set(
            ids
            or
            []
        )

        document_ids = set(
            document_ids
            or
            []
        )

        delete_ids = []

        for record_id, record in self.records.items():

            if record_id in ids:

                delete_ids.append(
                    record_id
                )

                continue

            if (
                record.document_id
                in document_ids
            ):

                delete_ids.append(
                    record_id
                )

        if not delete_ids:

            return 0

        for record_id in delete_ids:

            self.records.pop(
                record_id,
                None,
            )

        # Rebuild index.
        self._rebuild()

        self.save()

        return len(
            delete_ids
        )

    # --------------------------------------------------------
    # Rebuild
    # --------------------------------------------------------

    def _rebuild(self) -> None:

        records = list(
            self.records.values()
        )

        self.index = None

        self.id_order = []

        if not records:

            return

        first_vector = records[0].vector

        self._create_index(
            len(first_vector)
        )

        vectors = []

        for record in records:

            vector = list(
                record.vector
            )

            if self.normalize_vectors:

                vector = normalize_vector(
                    vector
                )

            vectors.append(
                vector
            )

            self.id_order.append(
                record.id
            )

        matrix = np.asarray(

            vectors,

            dtype="float32",

        )

        self.index.add(
            matrix
        )

    # --------------------------------------------------------
    # Count
    # --------------------------------------------------------

    def count(self) -> int:

        return len(
            self.records
        )

    # --------------------------------------------------------
    # Clear
    # --------------------------------------------------------

    def clear(self) -> None:

        self.records.clear()

        self.id_order.clear()

        self.index = None

        self.save()

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    def save(self) -> None:

        if not self.index_path:

            return

        self.index_path.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        self.metadata_path.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        if self.index is not None:

            faiss.write_index(

                self.index,

                str(
                    self.index_path
                ),

            )

        payload = {

            "dimension":
                self.dimension,

            "id_order":
                self.id_order,

            "records": [

                record_to_dict(
                    record
                )

                for record
                in self.records.values()

            ],

        }

        self.metadata_path.write_text(

            json.dumps(

                payload,

                ensure_ascii=False,

            ),

            encoding="utf-8",

        )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    def load(self) -> None:

        if self.index_path is None:

            return

        if self.metadata_path is None:

            return

        try:

            self.index = faiss.read_index(

                str(
                    self.index_path
                )

            )

            payload = json.loads(

                self.metadata_path.read_text(

                    encoding="utf-8"

                )

            )

            self.dimension = payload.get(
                "dimension"
            )

            self.id_order = list(

                payload.get(
                    "id_order",
                    [],
                )

            )

            self.records = {

                record.id:
                record

                for record
                in (

                    dict_to_record(
                        item
                    )

                    for item
                    in payload.get(
                        "records",
                        [],
                    )

                )

            }

        except Exception as exc:

            logger.warning(

                "FAISS load failed: %s",

                exc,

            )

            self.index = None

            self.records = {}

            self.id_order = []


# ============================================================
# END CHUNK 5
# ============================================================
# ============================================================
# CHUNK 6/10
#
# CHROMA BACKEND
# ============================================================


# ============================================================
# CHROMA BACKEND
# ============================================================

class ChromaVectorBackend(
    BaseVectorBackend
):

    backend_name = "chroma"

    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
    ) -> None:

        if chromadb is None:

            raise ImportError(

                "ChromaDB is not installed. "
                "Install using: pip install chromadb"

            )

        self.persist_directory = str(
            persist_directory
        )

        self.collection_name = (
            collection_name
        )

        Path(
            self.persist_directory
        ).mkdir(

            parents=True,

            exist_ok=True,

        )

        self.client = chromadb.PersistentClient(

            path=self.persist_directory

        )

        self.collection = (

            self.client.get_or_create_collection(

                name=self.collection_name,

                metadata={

                    "hnsw:space":
                        "cosine",

                },

            )

        )

    # --------------------------------------------------------
    # Metadata sanitization
    # --------------------------------------------------------

    @staticmethod
    def _sanitize_metadata(
        metadata: Mapping[str, Any],
    ) -> Dict[str, Any]:

        output = {}

        for key, value in metadata.items():

            if value is None:

                continue

            if isinstance(

                value,

                (
                    str,
                    int,
                    float,
                    bool,
                ),

            ):

                output[str(key)] = value

            else:

                output[str(key)] = str(
                    value
                )

        return output

    # --------------------------------------------------------
    # Add
    # --------------------------------------------------------

    def add_records(
        self,
        records: Sequence[VectorRecord],
    ) -> int:

        if not records:

            return 0

        ids = []

        embeddings = []

        documents = []

        metadatas = []

        for record in records:

            ids.append(
                record.id
            )

            embeddings.append(
                record.vector
            )

            documents.append(
                record.text
            )

            metadata = dict(
                record.metadata
            )

            metadata.update({

                "document_id":
                    record.document_id,

                "chunk_id":
                    record.chunk_id,

                "source":
                    record.source,

                "filename":
                    record.filename,

                "section":
                    record.section,

            })

            if record.page is not None:

                metadata["page"] = (
                    record.page
                )

            metadatas.append(

                self._sanitize_metadata(
                    metadata
                )

            )

        self.collection.upsert(

            ids=ids,

            embeddings=embeddings,

            documents=documents,

            metadatas=metadatas,

        )

        return len(
            records
        )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    def search(
        self,
        query_vector: Sequence[float],
        top_k: int = DEFAULT_TOP_K,
        threshold: float = DEFAULT_SCORE_THRESHOLD,
        filters: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> List[VectorRecord]:

        if not query_vector:

            return []

        kwargs = {

            "query_embeddings":
                [list(query_vector)],

            "n_results":
                top_k,

            "include":
                [
                    "documents",
                    "metadatas",
                    "distances",
                ],

        }

        # Basic Chroma-compatible equality filters.
        if filters:

            where = {}

            for key, value in filters.items():

                if not key.startswith(
                    "$"
                ) and not isinstance(
                    value,
                    Mapping,
                ):

                    where[key] = value

            if where:

                if len(where) == 1:

                    kwargs["where"] = where

                else:

                    kwargs["where"] = {

                        "$and": [

                            {
                                key:
                                value
                            }

                            for key, value
                            in where.items()

                        ]

                    }

        result = self.collection.query(
            **kwargs
        )

        ids = (
            result.get(
                "ids",
                [[]],
            )[0]
        )

        documents = (
            result.get(
                "documents",
                [[]],
            )[0]
        )

        metadatas = (
            result.get(
                "metadatas",
                [[]],
            )[0]
        )

        distances = (
            result.get(
                "distances",
                [[]],
            )[0]
        )

        output = []

        for index, record_id in enumerate(
            ids
        ):

            metadata = (

                dict(
                    metadatas[index]
                    or
                    {}
                )

                if index < len(
                    metadatas
                )

                else {}

            )

            text = (

                documents[index]

                if index < len(
                    documents
                )

                else ""

            )

            distance = (

                float(
                    distances[index]
                )

                if index < len(
                    distances
                )

                else 0.0

            )

            # Chroma cosine distance:
            #
            # distance = 1 - cosine similarity
            #
            score = 1.0 - distance

            if score < threshold:

                continue

            if not metadata_matches(

                metadata,

                filters,

            ):

                continue

            record = VectorRecord(

                id=record_id,

                vector=[],

                text=text,

                metadata=metadata,

                document_id=str(

                    metadata.get(
                        "document_id",
                        "",
                    )

                ),

                chunk_id=str(

                    metadata.get(
                        "chunk_id",
                        record_id,
                    )

                ),

                source=str(

                    metadata.get(
                        "source",
                        "",
                    )

                ),

                filename=str(

                    metadata.get(
                        "filename",
                        "",
                    )

                ),

                page=metadata.get(
                    "page"
                ),

                section=str(

                    metadata.get(
                        "section",
                        "",
                    )

                ),

                score=score,

            )

            output.append(
                record
            )

        output.sort(

            key=lambda item:
            item.score,

            reverse=True,

        )

        return output[
            :top_k
        ]

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    def delete(
        self,
        ids: Optional[
            Sequence[str]
        ] = None,
        document_ids: Optional[
            Sequence[str]
        ] = None,
    ) -> int:

        ids = list(
            ids
            or
            []
        )

        if ids:

            self.collection.delete(
                ids=ids
            )

            return len(
                ids
            )

        if document_ids:

            count_before = self.count()

            where = {

                "document_id": {

                    "$in":
                    list(
                        document_ids
                    )

                }

            }

            self.collection.delete(
                where=where
            )

            return max(

                0,

                count_before
                -
                self.count(),

            )

        return 0

    # --------------------------------------------------------
    # Count
    # --------------------------------------------------------

    def count(self) -> int:

        return int(
            self.collection.count()
        )

    # --------------------------------------------------------
    # Clear
    # --------------------------------------------------------

    def clear(self) -> None:

        try:

            self.client.delete_collection(

                self.collection_name

            )

        except Exception:

            pass

        self.collection = (

            self.client.get_or_create_collection(

                name=self.collection_name,

                metadata={

                    "hnsw:space":
                        "cosine",

                },

            )

        )


# ============================================================
# END CHUNK 6
# ============================================================
# ============================================================
# CHUNK 7/10
#
# SERIALIZATION + BACKEND FACTORY
# ============================================================


# ============================================================
# RECORD → DICT
# ============================================================

def record_to_dict(
    record: VectorRecord,
) -> Dict[str, Any]:

    return {

        "id":
            record.id,

        "vector":
            record.vector,

        "text":
            record.text,

        "metadata":
            record.metadata,

        "document_id":
            record.document_id,

        "chunk_id":
            record.chunk_id,

        "source":
            record.source,

        "filename":
            record.filename,

        "page":
            record.page,

        "section":
            record.section,

        "score":
            record.score,

    }


# ============================================================
# DICT → RECORD
# ============================================================

def dict_to_record(
    data: Mapping[str, Any],
) -> VectorRecord:

    return VectorRecord(

        id=str(
            data.get(
                "id",
                "",
            )
        ),

        vector=[

            float(value)

            for value
            in data.get(
                "vector",
                [],
            )

        ],

        text=str(
            data.get(
                "text",
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

        document_id=str(
            data.get(
                "document_id",
                "",
            )
        ),

        chunk_id=str(
            data.get(
                "chunk_id",
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

        score=float(

            data.get(
                "score",
                0.0,
            )

        ),

    )


# ============================================================
# CREATE BACKEND
# ============================================================

def create_backend(
    config: VectorStoreConfig,
) -> BaseVectorBackend:

    backend = detect_backend(
        config.backend
    )

    persist_directory = Path(
        config.persist_directory
    )

    persist_directory.mkdir(

        parents=True,

        exist_ok=True,

    )

    # --------------------------------------------------------
    # FAISS
    # --------------------------------------------------------

    if backend == "faiss":

        index_path = (

            persist_directory
            /
            f"{config.collection_name}.faiss"

        )

        metadata_path = (

            persist_directory
            /
            f"{config.collection_name}.json"

        )

        return FAISSVectorBackend(

            dimension=config.dimension,

            normalize_vectors=config.normalize_vectors,

            index_path=index_path,

            metadata_path=metadata_path,

        )

    # --------------------------------------------------------
    # Chroma
    # --------------------------------------------------------

    if backend == "chroma":

        return ChromaVectorBackend(

            persist_directory=str(
                persist_directory
            ),

            collection_name=config.collection_name,

        )

    # --------------------------------------------------------
    # NumPy
    # --------------------------------------------------------

    if backend == "numpy":

        return NumpyVectorBackend(

            normalize_vectors=config.normalize_vectors

        )

    # --------------------------------------------------------
    # Memory
    # --------------------------------------------------------

    return MemoryVectorBackend(

        normalize_vectors=config.normalize_vectors

    )


# ============================================================
# END CHUNK 7
# ============================================================
# ============================================================
# CHUNK 8/10
#
# VECTOR STORE CLASS
# ============================================================


# ============================================================
# VECTOR STORE
# ============================================================

class VectorStore:

    def __init__(
        self,
        config: Optional[
            VectorStoreConfig
        ] = None,
        embedding_engine: Optional[
            EmbeddingEngine
        ] = None,
    ) -> None:

        self.config = (

            config
            or
            VectorStoreConfig()

        )

        self.embedding_engine = (
            embedding_engine
        )

        self.backend = create_backend(
            self.config
        )

        self.backend_name = (
            self.backend.backend_name
        )

    # --------------------------------------------------------
    # Ensure embedding engine
    # --------------------------------------------------------

    def _ensure_embedding_engine(
        self,
    ) -> EmbeddingEngine:

        if self.embedding_engine is None:

            self.embedding_engine = (
                EmbeddingEngine()
            )

        return self.embedding_engine

    # --------------------------------------------------------
    # Convert embedding record
    # --------------------------------------------------------

    def _embedding_to_vector_record(
        self,
        record: EmbeddingRecord,
    ) -> VectorRecord:

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

        })

        return VectorRecord(

            id=(

                record.chunk_id
                or
                f"{record.document_id}:"
                f"{record.source}"

            ),

            vector=list(
                record.vector
            ),

            text=record.text,

            metadata=metadata,

            document_id=record.document_id,

            chunk_id=record.chunk_id,

            source=record.source,

            filename=record.filename,

            page=record.page,

            section=record.section,

        )

    # --------------------------------------------------------
    # Add embedding records
    # --------------------------------------------------------

    def add_embeddings(
        self,
        records: Sequence[EmbeddingRecord],
    ) -> int:

        vector_records = [

            self._embedding_to_vector_record(
                record
            )

            for record
            in records

            if record.vector

        ]

        if not self.config.allow_duplicates:

            vector_records = (
                self._remove_existing_ids(
                    vector_records
                )
            )

        if not vector_records:

            return 0

        # Infer dimension.
        if self.config.dimension is None:

            self.config.dimension = len(

                vector_records[0].vector

            )

        return self.backend.add_records(

            vector_records

        )

    # --------------------------------------------------------
    # Remove existing IDs
    # --------------------------------------------------------

    def _remove_existing_ids(
        self,
        records: Sequence[VectorRecord],
    ) -> List[VectorRecord]:

        if not records:

            return []

        # Memory/FAISS expose records.
        backend_records = getattr(

            self.backend,

            "records",

            None,

        )

        if isinstance(
            backend_records,
            dict,
        ):

            existing = set(
                backend_records.keys()
            )

            return [

                record

                for record
                in records

                if record.id not in existing

            ]

        # For Chroma, simply upsert is safe.
        return list(
            records
        )

    # --------------------------------------------------------
    # Add chunks
    # --------------------------------------------------------

    def add_chunks(
        self,
        chunks: Sequence[Any],
    ) -> int:

        engine = (
            self._ensure_embedding_engine()
        )

        embedding_result = (
            engine.embed_chunks(
                chunks
            )
        )

        if not embedding_result.success:

            raise RuntimeError(

                embedding_result.error
                or
                "Failed to generate embeddings."

            )

        return self.add_embeddings(

            embedding_result.records

        )

    # --------------------------------------------------------
    # Add texts
    # --------------------------------------------------------

    def add_texts(
        self,
        texts: Sequence[str],
        metadatas: Optional[
            Sequence[
                Mapping[str, Any]
            ]
        ] = None,
        ids: Optional[
            Sequence[str]
        ] = None,
    ) -> int:

        if not texts:

            return 0

        engine = (
            self._ensure_embedding_engine()
        )

        vectors = engine.embed_texts(
            texts
        )

        records = []

        for index, (
            text,
            vector,
        ) in enumerate(
            zip(
                texts,
                vectors,
            )
        ):

            metadata = (

                dict(
                    metadatas[index]
                )

                if metadatas
                and
                index < len(
                    metadatas
                )

                else {}

            )

            record_id = (

                ids[index]

                if ids
                and
                index < len(
                    ids
                )

                else f"text-{index}"

            )

            records.append(

                VectorRecord(

                    id=record_id,

                    vector=vector,

                    text=str(
                        text
                    ),

                    metadata=metadata,

                    document_id=str(

                        metadata.get(
                            "document_id",
                            "",
                        )

                    ),

                    chunk_id=str(

                        metadata.get(
                            "chunk_id",
                            record_id,
                        )

                    ),

                    source=str(

                        metadata.get(
                            "source",
                            "",
                        )

                    ),

                    filename=str(

                        metadata.get(
                            "filename",
                            "",
                        )

                    ),

                    page=metadata.get(
                        "page"
                    ),

                    section=str(

                        metadata.get(
                            "section",
                            "",
                        )

                    ),

                )

            )

        if self.config.dimension is None:

            for record in records:

                if record.vector:

                    self.config.dimension = len(
                        record.vector
                    )

                    break

        return self.backend.add_records(
            records
        )

    # --------------------------------------------------------
    # Search by vector
    # --------------------------------------------------------

    def search_by_vector(
        self,
        query_vector: Sequence[float],
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        filters: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> RetrievalResult:

        top_k = (

            top_k
            if top_k is not None
            else
            self.config.top_k

        )

        threshold = (

            threshold
            if threshold is not None
            else
            self.config.score_threshold

        )

        try:

            records = self.backend.search(

                query_vector=query_vector,

                top_k=top_k,

                threshold=threshold,

                filters=filters,

            )

            return RetrievalResult(

                records=records,

                top_k=top_k,

                total_candidates=self.count(),

                backend=self.backend_name,

                success=True,

            )

        except Exception as exc:

            logger.exception(
                "Vector search failed."
            )

            return RetrievalResult(

                records=[],

                top_k=top_k,

                total_candidates=0,

                backend=self.backend_name,

                success=False,

                error=str(
                    exc
                ),

            )

    # --------------------------------------------------------
    # Search by text
    # --------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        filters: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> RetrievalResult:

        engine = (
            self._ensure_embedding_engine()
        )

        query_vector = engine.embed_query(
            query
        )

        result = self.search_by_vector(

            query_vector=query_vector,

            top_k=top_k,

            threshold=threshold,

            filters=filters,

        )

        result.query = query

        return result

    # --------------------------------------------------------
    # Count
    # --------------------------------------------------------

    def count(self) -> int:

        return self.backend.count()

    # --------------------------------------------------------
    # Clear
    # --------------------------------------------------------

    def clear(self) -> None:

        self.backend.clear()

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    def delete(
        self,
        ids: Optional[
            Sequence[str]
        ] = None,
        document_ids: Optional[
            Sequence[str]
        ] = None,
    ) -> int:

        return self.backend.delete(

            ids=ids,

            document_ids=document_ids,

        )


# ============================================================
# END CHUNK 8
# ============================================================
# ============================================================
# CHUNK 9/10
#
# MMR + RAG CONTEXT + DOCUMENT MANAGEMENT
# ============================================================


# ============================================================
# MAXIMAL MARGINAL RELEVANCE
# ============================================================

def maximal_marginal_relevance(
    query_vector: Sequence[float],
    records: Sequence[VectorRecord],
    top_k: int = 5,
    lambda_mult: float = 0.7,
) -> List[VectorRecord]:

    if not records:

        return []

    if top_k <= 0:

        return []

    lambda_mult = max(

        0.0,

        min(
            1.0,
            lambda_mult,
        ),

    )

    remaining = list(
        records
    )

    selected = []

    while remaining and len(
        selected
    ) < top_k:

        best_record = None

        best_score = -float(
            "inf"
        )

        for record in remaining:

            relevance = cosine(

                query_vector,

                record.vector,

            )

            if not selected:

                diversity_penalty = 0.0

            else:

                diversity_penalty = max(

                    cosine(

                        record.vector,

                        selected_record.vector,

                    )

                    for selected_record
                    in selected

                )

            mmr_score = (

                lambda_mult
                *
                relevance

                -
                (
                    1
                    -
                    lambda_mult
                )
                *
                diversity_penalty

            )

            if mmr_score > best_score:

                best_score = mmr_score

                best_record = record

        if best_record is None:

            break

        selected.append(
            best_record
        )

        remaining.remove(
            best_record
        )

    return selected


# ============================================================
# MMR SEARCH
# ============================================================

def mmr_search(
    store: VectorStore,
    query: str,
    top_k: int = 5,
    fetch_k: int = 20,
    lambda_mult: float = 0.7,
    threshold: float = 0.0,
    filters: Optional[
        Mapping[str, Any]
    ] = None,
) -> RetrievalResult:

    engine = (
        store._ensure_embedding_engine()
    )

    query_vector = engine.embed_query(
        query
    )

    initial = store.search_by_vector(

        query_vector=query_vector,

        top_k=fetch_k,

        threshold=threshold,

        filters=filters,

    )

    if not initial.success:

        initial.query = query

        return initial

    selected = maximal_marginal_relevance(

        query_vector=query_vector,

        records=initial.records,

        top_k=top_k,

        lambda_mult=lambda_mult,

    )

    return RetrievalResult(

        records=selected,

        query=query,

        top_k=top_k,

        total_candidates=initial.total_candidates,

        backend=initial.backend,

        success=True,

        warnings=initial.warnings,

    )


# ============================================================
# FORMAT CONTEXT
# ============================================================

def format_context(
    records: Sequence[VectorRecord],
    include_scores: bool = True,
    include_source: bool = True,
) -> str:

    sections = []

    for index, record in enumerate(

        records,

        start=1,

    ):

        header = [
            f"[Context {index}]"
        ]

        if include_scores:

            header.append(

                f"Relevance: "
                f"{record.score:.4f}"

            )

        if include_source:

            if record.source:

                header.append(

                    f"Source: "
                    f"{record.source}"

                )

            if record.page is not None:

                header.append(

                    f"Page: "
                    f"{record.page}"

                )

            if record.section:

                header.append(

                    f"Section: "
                    f"{record.section}"

                )

        sections.append(

            "\n".join(

                header
                +
                [
                    record.text
                ]

            )

        )

    return "\n\n".join(
        sections
    )


# ============================================================
# RETRIEVE CONTEXT
# ============================================================

def retrieve_context(
    store: VectorStore,
    query: str,
    top_k: int = 5,
    threshold: float = 0.30,
    filters: Optional[
        Mapping[str, Any]
    ] = None,
) -> str:

    result = store.search(

        query=query,

        top_k=top_k,

        threshold=threshold,

        filters=filters,

    )

    if not result.success:

        return ""

    return format_context(
        result.records
    )


# ============================================================
# DOCUMENT IDS
# ============================================================

def list_document_ids(
    store: VectorStore,
) -> List[str]:

    backend_records = getattr(

        store.backend,

        "records",

        None,

    )

    if isinstance(
        backend_records,
        dict,
    ):

        return sorted(

            set(

                record.document_id

                for record
                in backend_records.values()

                if record.document_id

            )

        )

    # Chroma fallback.
    if store.backend_name == "chroma":

        try:

            result = store.backend.collection.get(

                include=[
                    "metadatas"
                ]

            )

            document_ids = []

            for metadata in (

                result.get(
                    "metadatas",
                    []
                )

            ):

                if metadata:

                    document_id = metadata.get(
                        "document_id"
                    )

                    if document_id:

                        document_ids.append(
                            str(
                                document_id
                            )
                        )

            return sorted(
                set(
                    document_ids
                )
            )

        except Exception:

            return []

    return []


# ============================================================
# DOCUMENT COUNT
# ============================================================

def document_count(
    store: VectorStore,
) -> int:

    return len(
        list_document_ids(
            store
        )
    )


# ============================================================
# END CHUNK 9
# ============================================================
# ============================================================
# CHUNK 10/10
#
# PRESETS + VALIDATION + EXPORTS + SELF TEST
# ============================================================


# ============================================================
# FAISS CONFIG
# ============================================================

def faiss_config(
    persist_directory: str = "./data/vectorstore/faiss",
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> VectorStoreConfig:

    return VectorStoreConfig(

        backend="faiss",

        persist_directory=persist_directory,

        collection_name=collection_name,

        metric="cosine",

        top_k=5,

        score_threshold=0.30,

        normalize_vectors=True,

        allow_duplicates=False,

        metadata_filter_enabled=True,

    )


# ============================================================
# CHROMA CONFIG
# ============================================================

def chroma_config(
    persist_directory: str = "./data/vectorstore/chroma",
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> VectorStoreConfig:

    return VectorStoreConfig(

        backend="chroma",

        persist_directory=persist_directory,

        collection_name=collection_name,

        metric="cosine",

        top_k=5,

        score_threshold=0.30,

        normalize_vectors=True,

        allow_duplicates=False,

        metadata_filter_enabled=True,

    )


# ============================================================
# DEVELOPMENT CONFIG
# ============================================================

def development_config() -> VectorStoreConfig:

    return VectorStoreConfig(

        backend="numpy",

        persist_directory="./data/vectorstore/dev",

        collection_name="pragyanai_dev",

        metric="cosine",

        top_k=5,

        score_threshold=0.20,

        normalize_vectors=True,

        allow_duplicates=False,

        metadata_filter_enabled=True,

    )


# ============================================================
# VALIDATE STORE
# ============================================================

def validate_store(
    store: VectorStore,
) -> Dict[str, Any]:

    errors = []

    warnings = []

    count = store.count()

    if count == 0:

        warnings.append(

            "Vector store is empty."

        )

    backend_records = getattr(

        store.backend,

        "records",

        None,

    )

    if isinstance(
        backend_records,
        dict,
    ):

        dimensions = set()

        for record in backend_records.values():

            if record.vector:

                dimensions.add(

                    len(
                        record.vector
                    )

                )

        if len(dimensions) > 1:

            errors.append(

                "Vector dimensions are inconsistent."

            )

        if (
            store.config.dimension
            and
            dimensions
            and
            store.config.dimension
            not in
            dimensions
        ):

            errors.append(

                "Configured vector dimension does not "
                "match stored vectors."

            )

    return {

        "valid":
            len(errors) == 0,

        "backend":
            store.backend_name,

        "count":
            count,

        "document_count":
            document_count(
                store
            ),

        "errors":
            errors,

        "warnings":
            warnings,

    }


# ============================================================
# STORE SUMMARY
# ============================================================

def store_summary(
    store: VectorStore,
) -> Dict[str, Any]:

    validation = validate_store(
        store
    )

    return {

        "vectorstore_version":
            VECTORSTORE_VERSION,

        "backend":
            store.backend_name,

        "collection":
            store.config.collection_name,

        "persist_directory":
            store.config.persist_directory,

        "metric":
            store.config.metric,

        "dimension":
            store.config.dimension,

        "vector_count":
            store.count(),

        "document_count":
            document_count(
                store
            ),

        "validation":
            validation,

    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Version
    "VECTORSTORE_VERSION",

    # Models
    "VectorRecord",

    "RetrievalResult",

    "VectorStoreConfig",

    # Backend utilities
    "is_numpy_available",

    "is_faiss_available",

    "is_chroma_available",

    "detect_backend",

    "require_numpy",

    # Vector utilities
    "normalize_vector",

    "dot_product",

    "cosine",

    # Metadata
    "get_metadata_value",

    "match_condition",

    "metadata_matches",

    "filter_records",

    # Backends
    "BaseVectorBackend",

    "MemoryVectorBackend",

    "NumpyVectorBackend",

    "FAISSVectorBackend",

    "ChromaVectorBackend",

    "create_backend",

    # Serialization
    "record_to_dict",

    "dict_to_record",

    # Store
    "VectorStore",

    # Retrieval
    "maximal_marginal_relevance",

    "mmr_search",

    "format_context",

    "retrieve_context",

    # Documents
    "list_document_ids",

    "document_count",

    # Validation
    "validate_store",

    "store_summary",

    # Presets
    "faiss_config",

    "chroma_config",

    "development_config",

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
        "VECTOR STORE SELF TEST"
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
        "\nFAISS available:"
    )

    print(
        is_faiss_available()
    )

    print(
        "\nChroma available:"
    )

    print(
        is_chroma_available()
    )

    # --------------------------------------------------------
    # Development store
    # --------------------------------------------------------

    config = development_config()

    store = VectorStore(
        config=config
    )

    # --------------------------------------------------------
    # Demo records
    # --------------------------------------------------------

    records = [

        VectorRecord(

            id="chunk-001",

            vector=[
                1.0,
                0.0,
                0.0,
            ],

            text=(
                "Generative AI uses "
                "large language models."
            ),

            metadata={

                "skill":
                    "Generative AI",

                "document_id":
                    "doc-001",

                "section":
                    "GenAI",

            },

            document_id="doc-001",

            chunk_id="chunk-001",

            source="curriculum.pdf",

            filename="curriculum.pdf",

            page=1,

            section="GenAI",

        ),

        VectorRecord(

            id="chunk-002",

            vector=[
                0.8,
                0.6,
                0.0,
            ],

            text=(
                "Python is widely used "
                "for machine learning."
            ),

            metadata={

                "skill":
                    "Python",

                "document_id":
                    "doc-001",

                "section":
                    "Python",

            },

            document_id="doc-001",

            chunk_id="chunk-002",

            source="curriculum.pdf",

            filename="curriculum.pdf",

            page=2,

            section="Python",

        ),

        VectorRecord(

            id="chunk-003",

            vector=[
                0.0,
                1.0,
                0.0,
            ],

            text=(
                "Machine learning models "
                "learn patterns from data."
            ),

            metadata={

                "skill":
                    "Machine Learning",

                "document_id":
                    "doc-002",

                "section":
                    "ML",

            },

            document_id="doc-002",

            chunk_id="chunk-003",

            source="industry.pdf",

            filename="industry.pdf",

            page=5,

            section="ML",

        ),

    ]

    # --------------------------------------------------------
    # Add records directly
    # --------------------------------------------------------

    added = store.backend.add_records(
        records
    )

    print(
        "\nRecords added:"
    )

    print(
        added
    )

    # --------------------------------------------------------
    # Count
    # --------------------------------------------------------

    print(
        "\nVector count:"
    )

    print(
        store.count()
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    result = store.search_by_vector(

        query_vector=[
            1.0,
            0.0,
            0.0,
        ],

        top_k=3,

        threshold=0.0,

    )

    print(
        "\nSearch results:"
    )

    for record in result.records:

        print(

            record.score,

            record.chunk_id,

            record.text,

        )

    # --------------------------------------------------------
    # Metadata filtering
    # --------------------------------------------------------

    filtered = store.search_by_vector(

        query_vector=[
            1.0,
            0.0,
            0.0,
        ],

        top_k=5,

        threshold=0.0,

        filters={

            "skill":
                "Generative AI",

        },

    )

    print(
        "\nFiltered results:"
    )

    for record in filtered.records:

        print(

            record.chunk_id,

            record.metadata,

        )

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    print(
        "\nRAG Context:"
    )

    print(
        format_context(
            result.records
        )
    )

    # --------------------------------------------------------
    # MMR
    # --------------------------------------------------------

    mmr = maximal_marginal_relevance(

        query_vector=[
            1.0,
            0.0,
            0.0,
        ],

        records=result.records,

        top_k=2,

        lambda_mult=0.7,

    )

    print(
        "\nMMR results:"
    )

    for record in mmr:

        print(

            record.chunk_id,

            record.score,

        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\nStore Summary:"
    )

    print(
        store_summary(
            store
        )
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print(
        "\nValidation:"
    )

    print(
        validate_store(
            store
        )
    )

    print(
        "\n============================================"
    )

    print(
        "VECTOR STORE TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# END OF rag/vectorstore.py
# ============================================================
