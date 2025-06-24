import json
import os
import subprocess
from sentence_transformers import SentenceTransformer
import transformers
import torch
import torch.nn.functional as F
from huggingface_hub import login
from std_queries import STANDARD_QUERIES
# ── Login to Hugging Face Hub (uses token for private models or faster pulls) ──
HUGGINGFACEHUB_API = "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"  # replace if needed
login(HUGGINGFACEHUB_API)
transformers.logging.set_verbosity_info()#for logging information about model

# ── Configuration ───────────────────────────────────────────────────
MODEL_NAME = "gemma3:1b"       # Ollama model identifier, mistral:7b-instruct
TABLE_JSON = "tables_data.json"
MAX_NEW_TOKENS = 32
OLLAMA_CMD = "ollama"        # Assumes 'ollama' is in PATH
TOP_K = 5          # Number of chunks to retrieve

# ── Load JSON table data ────────────────────────────────────────────
with open(TABLE_JSON, "r") as f:
    table_data = json.load(f)
    print("Table data loaded")

# ── Prepare embedding model and vectorize JSON chunks ────────────────
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Flatten JSON into chunks
chunks = []
if isinstance(table_data, list):
    for item in table_data:
        chunks.append(json.dumps(item))
elif isinstance(table_data, dict):
    for k, v in table_data.items():
        chunks.append(f"{k}: {v}")
else:
    chunks.append(json.dumps(table_data))


# Compute embeddings for chunks
chunk_embeddings = embed_model.encode(chunks, convert_to_tensor=True)


# ── Prompt builder with RAG retrieval ─────────────────────────────────
def build_prompt(question: str, relevant_chunks: list[str]) -> str:
    context = "\n".join(relevant_chunks)
    return (
        "You are an assistant that extracts key values from a structured JSON credit report.\n\n"
        f"Relevant Data:\n{context}\n\n"
        f"Q: {question}\nA:"  
    )

# ── Run inference via Ollama CLI ────────────────────────────────────
def ask_balance_sheet(question: str) -> str:
    # Embed question & retrieve top-k chunks
    q_emb = embed_model.encode(question, convert_to_tensor=True)
    scores = F.cosine_similarity(q_emb.unsqueeze(0), chunk_embeddings, dim=1)
    top_indices = torch.topk(scores, k=min(TOP_K, len(chunks))).indices.tolist()
    relevant = [chunks[i] for i in top_indices]

    # Build prompt with only relevant chunks
    prompt = build_prompt(question, relevant)

    # Invoke Ollama CLI
    process = subprocess.Popen(
        [OLLAMA_CMD, "run", MODEL_NAME], #"--max-tokens", str(MAX_NEW_TOKENS)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        text=True
    )
    stdout, stderr = process.communicate(prompt)
    if process.returncode != 0:
        raise RuntimeError(f"Ollama call failed: {stderr.strip()}")

    response = stdout.strip()
    # Parse answer after last 'A:'
    if 'A:' in response:
        answer = response.split('A:')[-1].strip()
    else:
        answer = response
    return answer #.split()[0] if answer else ""

# ── Example usage ───────────────────────────────────────────────────
if __name__ == "__main__":
    qa_output = []
    questions = STANDARD_QUERIES["questions"]

    for q in questions:
        try:
            answer = ask_balance_sheet(q)
        except Exception as e:
            answer = f"Error: {e}"
        print(f"Q: {q}\nA: {answer}\n")
        qa_output.append({"question": q, "answer": answer})
    with open("output_file.json", "w", encoding="utf-8") as outfile:
        json.dump(qa_output, outfile, indent=2, ensure_ascii=False)
    print("Results saved to output_file.json")


