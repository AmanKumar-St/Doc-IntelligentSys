import json
import re
from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import httpx
from app.models.chunk import Chunk
from app.providers.reranking.base import RerankerProvider
from app.core.logging import logger


class OpenRouterRerankerProvider(RerankerProvider):
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", model: str = "mistralai/mistral-7b-instruct:free"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={"HTTP-Referer": "https://github.com/doc-intelligence", "X-Title": "Document Intelligence"},
        )
        self.model = model

    async def rerank(self, query: str, chunks: list[Chunk], top_k: int = 6) -> list[Chunk]:
        if not chunks:
            return []
        if len(chunks) <= top_k:
            return chunks

        # Prompt LLM to score relevance of each candidate chunk [0..10]
        chunk_snippets = "\n".join(
            f"ID [{i+1}]: {c.text[:300]}..." for i, c in enumerate(chunks)
        )
        
        system_prompt = (
            "You are a relevance scoring engine for a Document Retrieval system. "
            "Given a query and numbered document snippets, rank the snippets by semantic relevance to the query. "
            "Return a JSON array of the most relevant snippet IDs in descending order of relevance, e.g. [3, 1, 5, 2]."
        )
        user_prompt = f"Query: {query}\n\nSnippets:\n{chunk_snippets}\n\nReturn JSON array only:"

        try:
            response = await self._call_llm(system_prompt, user_prompt)
            match = re.search(r"\[[0-9,\s]+\]", response)
            if match:
                indices = json.loads(match.group(0))
                reranked: list[Chunk] = []
                seen = set()
                for idx in indices:
                    chunk_idx = idx - 1
                    if 0 <= chunk_idx < len(chunks) and chunk_idx not in seen:
                        reranked.append(chunks[chunk_idx])
                        seen.add(chunk_idx)
                # Append any remainder up to top_k
                for i, c in enumerate(chunks):
                    if i not in seen:
                        reranked.append(c)
                return reranked[:top_k]
        except Exception as e:
            logger.warning(f"Reranking model failed, falling back to initial vector ranking: {e}")

        # Default fallback: return top_k preserving vector similarity order
        return sorted(chunks, key=lambda c: c.score or 0.0, reverse=True)[:top_k]

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError, TimeoutError)),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=200,
        )
        return completion.choices[0].message.content or ""
