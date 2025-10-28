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
        path = PROJECT_ROOT / fname
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
    - 'prompt' should already include chat history and the latest user message.
    - 'shared_dfs' is the dict returned by load_shared_datasets().
    Returns: (response_text, dataset_used)
    """
    # 1) Decide which dataset is relevant from the prompt
    dataset_name = select_relevant_dataset(prompt)

    # 2) Build a dataset context snippet (small) to include if available
    dataset_context, dataset_used = _build_dataset_context(dataset_name, shared_dfs)

    # 3) Construct final prompt that includes dataset snippet (if any) + chat prompt
    if dataset_context:
        final_prompt = (
            "You are a helpful medical assistant chatbot. Use the dataset below (if relevant) and the chat history "
            "to answer the user's question accurately. Do NOT assume the dataset represents the user's personal health report.\n\n"
            f"Dataset Preview ({dataset_used}):\n{dataset_context}\n\n"
            f"Conversation and question:\n{prompt}\n\nAnswer concisely and accurately based on the dataset and conversation."
        )
    else:
        final_prompt = (
            "You are a helpful medical assistant chatbot. Use the conversation below to answer the user's question.\n\n"
            f"{prompt}\n\nAnswer concisely and accurately."
        )

    # 4) Call local Ollama LLM
    llm = OllamaLLM(model="llama3.2", temperature=0)
    try:
        response = llm.invoke(final_prompt)
        # response may be text or may be dict-like depending on wrapper
        if isinstance(response, dict):
            # try some possible keys
            response_text = response.get("content") or response.get("text") or str(response)
        else:
            response_text = str(response)
    except Exception as e:
        response_text = f"Error generating response: {e}"

    return response_text, dataset_used
