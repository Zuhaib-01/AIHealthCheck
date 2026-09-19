# utils/chatbot.py
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BASE_DIR.parent.resolve()  # assumes utils/ is inside project root


def load_shared_datasets() -> Dict[str, Optional[pd.DataFrame]]:
    """
    Load the global medical CSV datasets.
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
    """
    if dataset_name and dataset_name in shared_dfs and shared_dfs[dataset_name] is not None:
        df = shared_dfs[dataset_name]
        context = df.head(50).to_string(index=False)
        return context, dataset_name
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


def generate_response(
    user_input: str,
    history: List[Dict[str, str]],
    shared_dfs: Dict[str, Optional[pd.DataFrame]]
) -> Tuple[str, str]:
    """
    Generate a response using the local Ollama model, via its proper chat
    interface (role-tagged messages) rather than a hand-formatted text blob.

    - 'user_input': the latest message from the user.
    - 'history': prior turns only (NOT including user_input), oldest first,
      each a dict with 'message' and 'response' keys.
    - 'shared_dfs': the dict returned by load_shared_datasets().

    Using real message roles (system/human/ai) instead of a "User: ...\\nBot: ..."
    text transcript matters: a raw text blob that *looks like* a document
    invites the model to summarize or continue it as one, rather than treating
    it as a live conversation and answering only the latest turn.
    """
    # 1) Decide which dataset is relevant, using the latest message + recent history as signal
    lookup_text = user_input + " " + " ".join(
        f"{h.get('message', '')} {h.get('response', '')}" for h in history[-3:]
    )
    dataset_name = select_relevant_dataset(lookup_text)
    dataset_context, dataset_used = _build_dataset_context(dataset_name, shared_dfs)

    # 2) System instructions
    system_text = (
        "You are a helpful medical assistant chatbot having an ongoing conversation with a user. "
        "Respond naturally to only the user's latest message, shown as the final message below. "
        "Do not summarize, review, recap, or list out the conversation so far, and do not use phrases "
        "like 'This conversation demonstrates' — just answer the current message directly, in one "
        "natural reply, the way a person would in a live chat. "
        "Do not open with or repeat generic disclaimers such as 'I'm not a medical professional' or "
        "'I am an AI' — the user already knows this. Only mention seeing a doctor if the symptoms "
        "described sound genuinely serious or urgent, and keep that note brief and specific rather "
        "than a blanket caveat. Never repeat a previous answer word-for-word. If the user's latest "
        "message is a short acknowledgement or filler (like 'ok', 'thanks', 'got it', 'alright', "
        "'im feeling better now'), respond briefly and warmly — do not restate earlier information."
    )
    if dataset_context:
        system_text += (
            f"\n\nRelevant dataset preview ({dataset_used}) — use it only if relevant to the current "
            f"message, and do NOT assume it represents the user's personal health report:\n{dataset_context}"
        )

    # 3) Build the actual message list — this is what makes the model treat
    # each turn as a discrete turn instead of one block of text to react to.
    messages = [SystemMessage(content=system_text)]
    for turn in history:
        if turn.get("message"):
            messages.append(HumanMessage(content=turn["message"]))
        if turn.get("response"):
            messages.append(AIMessage(content=turn["response"]))
    messages.append(HumanMessage(content=user_input))

    # 4) Call local Ollama chat model
    llm = ChatOllama(model="llama3.2", temperature=0.4)
    try:
        result = llm.invoke(messages)
        response_text = getattr(result, "content", None) or str(result)
        response_text = response_text.strip()
    except Exception as e:
        response_text = f"Error generating response: {e}"

    return response_text, dataset_used
