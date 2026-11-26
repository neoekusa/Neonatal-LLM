"""Canonical score-sheet labels, including spellings from earlier data exports."""
import re


MODEL_LABELS = (
    "ChatGPT-5", "Gemini 3 Pro", "Claude Sonnet 4.5", "ChatGPT-5.2",
    "Claude Sonnet 3.5", "Gemini 2.5 Pro", "DeepSeek-V3", "ChatGPT-4o",
    "Claude Sonnet 4.6", "DeepSeek-V3.2", "Gemini 3.1 Pro", "ChatGPT-5.4 Thinking",
    "Grok 4.2", "Llama 4", "ChatGPT-5.4", "Llama 3.3", "Grok 4", "Gemma 4",
    "ChatGPT-5.5 Thinking", "DeepSeek-V4",
)


def _compact(label: str) -> str:
    return re.sub(r"[\s-]+", "", label.casefold())


LABELS = {_compact(label): label for label in MODEL_LABELS}
LABELS.update({
    "chat5.4thinking": "ChatGPT-5.4 Thinking",
    "chat5.4": "ChatGPT-5.4",
    "chagpt5.4": "ChatGPT-5.4",
    "chagptt5.4": "ChatGPT-5.4",
    "deepseek3.2": "DeepSeek-V3.2",
    "gpt5.5thinking": "ChatGPT-5.5 Thinking",
})


def standardize_model_label(label: str) -> str:
    compact = _compact(label)
    # The original study header omitted the 'o'. Apply only to this exact version.
    if re.fullmatch(r"chatgpt4o?", compact):
        return "ChatGPT-4o"
    return LABELS.get(compact, label.strip())
