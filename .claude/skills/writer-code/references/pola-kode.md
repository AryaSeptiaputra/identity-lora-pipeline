# Pola Kode

Contoh chatbot RAG kecil yang menerapkan semua aturan Bagian 2 `SKILL.md`. Dipakai sebagai acuan bentuk, bukan untuk disalin apa adanya.

## Daftar isi

- Susunan file
- Config, error, dan pembantu: `config.py`, `errors.py`, `utils/logger.py`, `utils/text.py`
- Bentuk data dan prompt: `models/retrieval.py`, `models/chat.py`, `prompts/chat.py`
- Pengakses luar: `storage/vector_store.py`, `providers/llm_client.py`
- Proses: `services/rag_service.py`
- Pembentuk dan titik masuk: `factory.py`, `api/chat/schemas.py`, `api/chat/routes.py`, `api/main.py`
- Test: `tests/services/test_rag_service.py`
- Peta peran

---

## Susunan file

```
app/
├── config.py
├── errors.py
├── factory.py
├── prompts/chat.py
├── models/
│   ├── retrieval.py
│   └── chat.py
├── storage/vector_store.py
├── providers/llm_client.py
├── services/rag_service.py
├── api/
│   ├── main.py
│   └── chat/
│       ├── schemas.py
│       └── routes.py
└── utils/
    ├── logger.py
    └── text.py
tests/services/test_rag_service.py
```

---

## Config, error, dan pembantu

```python
# file: app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Setting aplikasi yang dibaca dari `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:7b-instruct"
    vector_store_path: str = "data/processed/chroma"
    collection_name: str = "documents"
    top_k: int = 5
    min_score: float = 0.3
    log_format: str = "text"


settings = Settings()
```

```python
# file: app/errors.py
class RetrievalError(Exception):
    """Pencarian dokumen gagal."""


class GenerationError(Exception):
    """Pembuatan jawaban oleh model gagal."""
```

```python
# file: app/utils/logger.py
import logging
import sys

from pythonjsonlogger import jsonlogger

from app.config import settings

# Contoh: 2026-01-15 10:30:00,123 | INFO     | app.services.rag_service | Menjawab pertanyaan
# levelname dilebarkan 8 karakter supaya kolom pesan sejajar antar-level
TEXT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# Field yang sama dengan TEXT_FORMAT, dikeluarkan sebagai JSON satu baris per log
JSON_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def setup_logger(name: str) -> logging.Logger:
    """Membuat logger dengan format sesuai `LOG_FORMAT`.

    Args:
        name: Nama logger, biasanya `__name__`.

    Returns:
        Logger yang siap dipakai.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    if settings.log_format == "json":
        handler.setFormatter(jsonlogger.JsonFormatter(JSON_FORMAT))
    else:
        handler.setFormatter(logging.Formatter(TEXT_FORMAT))

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
```

```python
# file: app/utils/text.py
import re

# Satu atau lebih karakter spasi, tab, atau baris baru berturut-turut
WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    """Merapikan spasi berlebih menjadi satu spasi.

    Args:
        text: Teks masukan.

    Returns:
        Teks tanpa spasi ganda di awal, tengah, dan akhir.
    """
    return WHITESPACE_PATTERN.sub(" ", text).strip()
```

---

## Bentuk data dan prompt

```python
# file: app/models/retrieval.py
from pydantic import BaseModel


class Chunk(BaseModel):
    """Potongan dokumen hasil pencarian."""

    chunk_id: str
    content: str
    source_url: str
    score: float

    def to_context_block(self, number: int) -> str:
        """Mengubah chunk menjadi blok konteks bernomor untuk prompt.

        Args:
            number: Nomor urut chunk di dalam konteks.

        Returns:
            Blok teks berisi nomor, sumber, dan isi chunk.
        """
        return f"[{number}] {self.source_url}\n{self.content}"
```

```python
# file: app/models/chat.py
from pydantic import BaseModel

from app.models.retrieval import Chunk


class Answer(BaseModel):
    """Jawaban akhir beserta sumbernya."""

    text: str
    sources: list[str]

    @classmethod
    def from_generation(cls, text: str, chunks: list[Chunk]) -> "Answer":
        """Membentuk jawaban dari teks model dan chunk yang dipakai.

        Args:
            text: Teks jawaban dari model.
            chunks: Chunk yang menjadi konteks jawaban.

        Returns:
            Jawaban dengan daftar sumber tanpa duplikat.
        """
        sources = list(dict.fromkeys(chunk.source_url for chunk in chunks))
        return cls(text=text, sources=sources)
```

```python
# file: app/prompts/chat.py
SYSTEM_PROMPT = """Jawab hanya berdasarkan konteks di bawah.
Kalau jawabannya tidak ada di konteks, katakan bahwa informasinya tidak tersedia.
Jangan mengarang.

KONTEKS:
{context}"""

EMPTY_CONTEXT = "(tidak ada konteks yang relevan)"
```

---

## Pengakses luar

```python
# file: app/storage/vector_store.py
import chromadb
from chromadb.api.types import QueryResult
from chromadb.errors import ChromaError

from app.errors import RetrievalError
from app.models.retrieval import Chunk
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class VectorStore:
    """Akses ke koleksi dokumen di Chroma."""

    def __init__(self, path: str, collection_name: str) -> None:
        self._client = chromadb.PersistentClient(path=path)
        self._collection_name = collection_name

    def _to_chunks(self, result: QueryResult) -> list[Chunk]:
        rows = zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
            strict=True,
        )
        return [
            Chunk(
                chunk_id=chunk_id,
                content=document,
                source_url=str(metadata["source_url"]),
                score=1 - distance,
            )
            for chunk_id, document, metadata, distance in rows
        ]

    def search(self, query: str, top_k: int) -> list[Chunk]:
        """Mencari chunk yang paling mirip dengan query.

        Args:
            query: Teks pencarian.
            top_k: Jumlah chunk maksimal yang dikembalikan.

        Returns:
            Chunk urut dari yang paling mirip.

        Raises:
            RetrievalError: Kalau koleksi tidak bisa dibuka atau pencarian gagal.
        """
        try:
            collection = self._client.get_collection(self._collection_name)
            result = collection.query(query_texts=[query], n_results=top_k)
        except ChromaError as e:
            logger.error(f"Pencarian gagal di koleksi {self._collection_name}: {e}", exc_info=True)
            raise RetrievalError(f"Pencarian dokumen gagal: {e}") from e
        return self._to_chunks(result)
```

```python
# file: app/providers/llm_client.py
import httpx
from ollama import Client, ResponseError

from app.errors import GenerationError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMClient:
    """Akses ke model bahasa melalui Ollama."""

    def __init__(self, base_url: str, model: str) -> None:
        self._client = Client(host=base_url)
        self._model = model

    def generate(self, system_prompt: str, question: str) -> str:
        """Meminta jawaban dari model.

        Args:
            system_prompt: Instruksi sistem beserta konteks.
            question: Pertanyaan pengguna.

        Returns:
            Teks jawaban dari model.

        Raises:
            GenerationError: Kalau model tidak bisa dihubungi atau mengembalikan error.
        """
        try:
            response = self._client.chat(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
            )
        except (ResponseError, httpx.HTTPError) as e:
            logger.error(f"Model {self._model} gagal menjawab: {e}", exc_info=True)
            raise GenerationError(f"Pembuatan jawaban gagal: {e}") from e
        return response.message.content
```

---

## Proses

Urutan: `__init__`, sub-proses paling dalam (`_is_relevant`), sub-proses sesuai urutan dipanggil, lalu proses publik (`answer`) di bawah. `answer()` memanggil `self._llm_client.generate()` langsung, tanpa sub-proses penerus.

```python
# file: app/services/rag_service.py
from app.models.chat import Answer
from app.models.retrieval import Chunk
from app.prompts.chat import EMPTY_CONTEXT, SYSTEM_PROMPT
from app.providers.llm_client import LLMClient
from app.storage.vector_store import VectorStore
from app.utils.text import normalize_whitespace


class RAGService:
    """Menjawab pertanyaan berdasarkan dokumen yang tersimpan."""

    def __init__(
        self,
        vector_store: VectorStore,
        llm_client: LLMClient,
        top_k: int,
        min_score: float,
    ) -> None:
        self._vector_store = vector_store
        self._llm_client = llm_client
        self._top_k = top_k
        self._min_score = min_score

    def _is_relevant(self, chunk: Chunk) -> bool:
        return chunk.score >= self._min_score

    def _retrieve(self, question: str) -> list[Chunk]:
        chunks = self._vector_store.search(question, self._top_k)
        return [chunk for chunk in chunks if self._is_relevant(chunk)]

    def _build_prompt(self, chunks: list[Chunk]) -> str:
        if not chunks:
            return SYSTEM_PROMPT.format(context=EMPTY_CONTEXT)
        blocks = [chunk.to_context_block(number) for number, chunk in enumerate(chunks, start=1)]
        return SYSTEM_PROMPT.format(context="\n\n".join(blocks))

    def answer(self, question: str) -> Answer:
        """Menjawab pertanyaan dengan konteks dari dokumen.

        Args:
            question: Pertanyaan pengguna.

        Returns:
            Jawaban beserta sumber yang dipakai.

        Raises:
            RetrievalError: Kalau pencarian dokumen gagal.
            GenerationError: Kalau model gagal membuat jawaban.
        """
        question = normalize_whitespace(question)
        chunks = self._retrieve(question)
        prompt = self._build_prompt(chunks)
        text = self._llm_client.generate(prompt, question)
        return Answer.from_generation(text, chunks)
```

---

## Pembentuk dan titik masuk

```python
# file: app/factory.py
from functools import lru_cache

from app.config import settings
from app.providers.llm_client import LLMClient
from app.services.rag_service import RAGService
from app.storage.vector_store import VectorStore


@lru_cache
def build_rag_service() -> RAGService:
    """Membuat `RAGService` beserta dependensinya, sekali per proses.

    Returns:
        Instance `RAGService` yang siap dipakai.
    """
    vector_store = VectorStore(settings.vector_store_path, settings.collection_name)
    llm_client = LLMClient(settings.llm_base_url, settings.llm_model)
    return RAGService(vector_store, llm_client, settings.top_k, settings.min_score)
```

```python
# file: app/api/chat/schemas.py
from pydantic import BaseModel, Field

from app.models.chat import Answer


class ChatRequest(BaseModel):
    """Pertanyaan dari pengguna."""

    question: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    """Jawaban yang dikirim ke pengguna."""

    answer: str
    sources: list[str]

    @classmethod
    def from_answer(cls, answer: Answer) -> "ChatResponse":
        """Membentuk respons dari jawaban service.

        Args:
            answer: Jawaban dari `RAGService`.

        Returns:
            Respons siap dikirim.
        """
        return cls(answer=answer.text, sources=answer.sources)
```

Endpoint memakai `def`, bukan `async def`, karena client Chroma dan Ollama di contoh ini sinkron.

```python
# file: app/api/chat/routes.py
from fastapi import APIRouter, Depends, HTTPException

from app.api.chat.schemas import ChatRequest, ChatResponse
from app.errors import GenerationError, RetrievalError
from app.factory import build_rag_service
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, service: RAGService = Depends(build_rag_service)) -> ChatResponse:
    """Menerima pertanyaan dan mengembalikan jawaban beserta sumbernya.

    Args:
        req: Pertanyaan dari pengguna.
        service: `RAGService` dari `build_rag_service`.

    Returns:
        Jawaban dan daftar sumber.

    Raises:
        HTTPException: 503 kalau pencarian atau model tidak tersedia.
    """
    try:
        answer = service.answer(req.question)
    except (RetrievalError, GenerationError) as e:
        raise HTTPException(status_code=503, detail="service_unavailable") from e
    return ChatResponse.from_answer(answer)
```

```python
# file: app/api/main.py
from fastapi import FastAPI

from app.api.chat.routes import router as chat_router

app = FastAPI(title="RAG Chatbot")
app.include_router(chat_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Menandakan server berjalan.

    Returns:
        Status server.
    """
    return {"status": "ok"}
```

---

## Test

Class palsu cukup punya method yang dipakai; tidak perlu `interfaces.py`.

```python
# file: tests/services/test_rag_service.py
from app.models.retrieval import Chunk
from app.services.rag_service import RAGService


class FakeVectorStore:
    def __init__(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks

    def search(self, query: str, top_k: int) -> list[Chunk]:
        return self._chunks[:top_k]


class FakeLLMClient:
    def __init__(self) -> None:
        self.last_system_prompt = ""

    def generate(self, system_prompt: str, question: str) -> str:
        self.last_system_prompt = system_prompt
        return "Jawaban"


def test_answer_hanya_memakai_chunk_yang_relevan() -> None:
    chunks = [
        Chunk(chunk_id="a", content="Isi A", source_url="https://contoh.id/a", score=0.9),
        Chunk(chunk_id="b", content="Isi B", source_url="https://contoh.id/b", score=0.1),
    ]
    llm = FakeLLMClient()
    service = RAGService(FakeVectorStore(chunks), llm, top_k=5, min_score=0.3)

    answer = service.answer("Apa isi A?")

    assert answer.sources == ["https://contoh.id/a"]
    assert "Isi B" not in llm.last_system_prompt
```

---

## Peta peran

| Function | Peran alur | Peran pekerjaan | Jangkauan |
|---|---|---|---|
| `chat()`, `health()` | Titik masuk | — | Publik |
| `RAGService.answer()` | Proses | — | Publik |
| `RAGService._retrieve()` | Sub-proses | Pengakses luar (lewat `VectorStore`) | `_` |
| `RAGService._is_relevant()` | Sub-proses tingkat 2 | Pemeriksa | `_` |
| `RAGService._build_prompt()` | Sub-proses | Pengubah bentuk | `_` |
| `VectorStore.search()` | Proses class lain | Pengakses luar | Publik |
| `VectorStore._to_chunks()` | Sub-proses | Pengubah bentuk | `_` |
| `LLMClient.generate()` | Proses class lain | Pengakses luar | Publik |
| `Chunk.to_context_block()`, `Answer.from_generation()`, `ChatResponse.from_answer()` | — | Pengubah bentuk | Publik |
| `build_rag_service()` | — | Pembentuk | Publik |
| `normalize_whitespace()`, `setup_logger()` | — | Pembantu | Publik |
