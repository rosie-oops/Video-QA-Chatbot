
import os

from langchain_groq import ChatGroq

import config

_llm = None


def _get_llm() -> ChatGroq:

    global _llm
    if _llm is None:
        if not os.environ.get(config.GROQ_API_KEY_ENV_VAR):
            raise RuntimeError(
                f"{config.GROQ_API_KEY_ENV_VAR} is not set. "
                "Set it as an environment variable before asking questions."
            )
        _llm = ChatGroq(model=config.GROQ_MODEL_NAME)
    return _llm


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        parts.append(
            f"Timestamp: {c['start']} - {c['end']}\n\nContent:\n{c['text']}"
        )
    return "\n\n".join(parts)


def generate_answer(query: str, top_chunks: list[dict]) -> str:
    if not top_chunks:
        return "I could not find this in the video."

    context = _build_context(top_chunks)

    prompt = f"""You are a helpful AI tutor.

Answer ONLY using the given context.

If the answer is not present, say:
"I could not find this in the video."

Always include timestamps in your answer.

Context:
{context}

Question:
{query}
"""

    response = _get_llm().invoke(prompt)
    return response.content
