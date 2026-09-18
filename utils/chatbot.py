# utils/chatbot.py
from langchain_ollama import OllamaLLM
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple

BASE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BASE_DIR.parent.resolve()  # assumes utils/ is inside project root


def load_shared_datasets() -> Dict[str, Optional[pd.DataFrame]]:
    """
    Load the global medical CSV datasets from the project root.
    Returns a dict mapping filename -> DataFrame (or None if load failed).
    Call this once at app startup.
    """
    files = [
        "Symptom_severity.csv",
        "symptom_Description.csv",
        "symptom_precaution.csv",
        "dataset.csv",
        "Diseases_Symptoms.csv"
    ]
    dfs: Dict[str, Optional[pd.DataFrame]] = {}
    for fname in files:
        path = BASE_DIR / fname  # CSVs live inside utils/, alongside this file
        try:
            dfs[fname] = pd.read_csv(path)
        except Exception:
            dfs[fname] = None
    return dfs


def select_relevant_dataset(text: str) -> Optional[str]:
    """
    Heuristic to pick a dataset name based on keywords found in 'text'.
    Works on both single user messages and multi-line prompts (chat history + message).
    """
    text_lower = (text or "").lower()
    symptom_keywords = ["symptom", "feel", "pain", "ache", "discomfort", "nausea", "vomit",
                        "fever", "cold", "cough", "diagnosis", "disease", "infection", "headache"]
    precaution_keywords = ["prevent", "precaution", "care", "avoid", "treatment",
                          "medicine", "cure", "remedy", "recover", "what should i do"]
    severity_keywords = ["severe", "mild", "intense", "critical", "level", "scale", "serious"]

    if any(k in text_lower for k in symptom_keywords):
        return "symptom_Description.csv"
    if any(k in text_lower for k in precaution_keywords):
        return "symptom_precaution.csv"
    if any(k in text_lower for k in severity_keywords):
        return "Symptom_severity.csv"
    return None


def _build_dataset_context(dataset_name: Optional[str], shared_dfs: Dict[str, Optional[pd.DataFrame]]) -> Tuple[str, str]:
    """
    Return (context_string, dataset_used_name)
    If dataset_name specified and available, return its head as context.
    Otherwise concatenate small previews of all available dataframes.
    """
    if dataset_name and dataset_name in shared_dfs and shared_dfs[dataset_name] is not None:
        df = shared_dfs[dataset_name]
        context = df.head(50).to_string(index=False)
        return context, dataset_name
    # fallback: combine previews from all loaded datasets (limit to avoid huge prompts)
    parts = []
    for name, df in (shared_dfs.items() if shared_dfs else []):
        if df is not None:
            try:
                parts.append(f"--- {name} ---\n{df.head(20).to_string(index=False)}")
            except Exception:
                continue
    if parts:
        return "\n\n".join(parts), "All Datasets"
    return "", "None"


def generate_response(prompt: str, shared_dfs: Dict[str, Optional[pd.DataFrame]]) -> Tuple[str, str]:
    """
    Generate a response using the local Ollama model.
    - 'prompt' should already include chat history and the latest user message,
      ending exactly with "...\\nUser: <message>\\nBot:" (no trailing text after "Bot:").
    - 'shared_dfs' is the dict returned by load_shared_datasets().
    Returns: (response_text, dataset_used)
    """
    # 1) Decide which dataset is relevant from the prompt
    dataset_name = select_relevant_dataset(prompt)

    # 2) Build a dataset context snippet (small) to include if available
    dataset_context, dataset_used = _build_dataset_context(dataset_name, shared_dfs)

    # 3) Build instructions. Everything the model needs to know goes BEFORE the
    # conversation history — the prompt must end exactly at "Bot:" with nothing
    # after it, or completion-style models get confused about where their turn
    # starts and may echo/continue the whole transcript instead of answering.
    instructions = (
        "You are a helpful medical assistant chatbot in an ongoing conversation. "
        "Respond with ONLY your reply as the Bot for the latest User message below — "
        "plain text, no 'User:' or 'Bot:' labels, no restating or listing earlier turns, "
        "no meta-commentary like 'Here's a concise response'. Just answer naturally, "
        "as if speaking directly to the user in a single turn.\n"
        "Do not open with or repeat generic disclaimers such as 'I'm not a medical professional' "
        "or 'I am an AI' — the user already knows this. "
        "Only mention seeing a doctor if the symptoms described sound genuinely serious or urgent, "
        "and keep that note brief and specific rather than a blanket caveat. "
        "Never repeat a previous answer word-for-word. If the user's latest message is a short "
        "acknowledgement or filler (like 'ok', 'thanks', 'got it', 'alright'), respond briefly and "
        "naturally — do not restate earlier information."
    )

    if dataset_context:
        instructions += (
            f"\n\nRelevant dataset preview ({dataset_used}) — use it only if relevant, and do NOT "
            f"assume it represents the user's personal health report:\n{dataset_context}"
        )

    final_prompt = f"{instructions}\n\nConversation so far:\n{prompt}"

    # 4) Call local Ollama LLM. stop sequences are a hard backstop: if the model
    # tries to hallucinate a new "User:" turn instead of stopping, cut it off there.
    llm = OllamaLLM(model="llama3.2", temperature=0.4, stop=["\nUser:", "\nUser :", "\nuser:"])
    try:
        response = llm.invoke(final_prompt)
        if isinstance(response, dict):
            response_text = response.get("content") or response.get("text") or str(response)
        else:
            response_text = str(response)

        # Safety net in case the model still echoes a transcript-style reply
        # despite the stop sequence (some models don't honor it reliably).
        for marker in ("\nUser:", "\nUser :", "User:"):
            idx = response_text.find(marker)
            if idx != -1:
                response_text = response_text[:idx]
        response_text = response_text.strip()
        if response_text[:4].lower() == "bot:":
            response_text = response_text[4:].strip()
    except Exception as e:
        response_text = f"Error generating response: {e}"

    return response_text, dataset_used
