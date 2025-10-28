from langchain_ollama import OllamaLLM
import pandas as pd

def load_datasets():
    files = [
        "Symptom_severity.csv",
        "symptom_Description.csv",
        "symptom_precaution.csv",
        "dataset.csv",
        "Diseases_Symptoms.csv"
    ]
    dfs = {}
    for file in files:
        try:
            dfs[file] = pd.read_csv(file)
        except Exception:
            pass
    return dfs


def select_relevant_dataset(query: str):
    query_lower = query.lower()
    symptom_keywords = ["symptom", "pain", "fever", "diagnosis", "infection"]
    precaution_keywords = ["prevent", "care", "avoid", "medicine", "cure"]
    severity_keywords = ["severe", "mild", "critical", "level", "scale"]

    if any(word in query_lower for word in symptom_keywords):
        return "symptom_Description.csv"
    elif any(word in query_lower for word in precaution_keywords):
        return "symptom_precaution.csv"
    elif any(word in query_lower for word in severity_keywords):
        return "Symptom_severity.csv"
    else:
        return None


def generate_response(user_input: str, dfs: dict):
    dataset_used = select_relevant_dataset(user_input)

    if dataset_used and dataset_used in dfs:
        df = dfs[dataset_used]
        context = df.head(50).to_string(index=False)
    else:
        context = "\n\n".join(
            [df.head(50).to_string(index=False) for df in dfs.values() if df is not None]
        )
        dataset_used = "All Datasets"

    prompt = f"""
You are a helpful medical assistant chatbot.
Use the dataset provided to answer user queries accurately.
Do NOT assume this data represents the user's personal health report — it's a general medical dataset.

Dataset Source: {dataset_used}

Data Preview:
{context}

Question: {user_input}

Answer clearly using only reliable dataset information.
    """

    llm = OllamaLLM(model="llama3.2", temperature=0)
    try:
        response = llm.invoke(prompt)
        response_text = str(response) if not isinstance(response, dict) else response.get("content", str(response))
    except Exception as e:
        response_text = f"Error generating response: {e}"

    return response_text, dataset_used
