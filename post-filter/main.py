from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

BASE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_NAME = "AWCO/llm-text-classifier"

class TextInput(BaseModel):
    text: str

class ClassificationOutput(BaseModel):
    label: str
    score: float

try:
    print(f"Loading Hugging Face model: {MODEL_NAME}...")
    # Specify device=-1 to force CPU usage. Remove for automatic detection (or set to 0 for GPU).
    classifier = pipeline(
        "text-classification",
        model=MODEL_NAME,
        tokenizer=BASE_MODEL,
    )
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    classifier = None

# --- 3. Create the FastAPI App ---
app = FastAPI(
    title="LLM Post Classifier API",
    description=f"An API to classify text using the {MODEL_NAME} model.",
    version="1.0.0"
)

# --- 4. Define API Endpoints ---
@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Classifier API is running."}

@app.post("/classify", response_model=ClassificationOutput, tags=["Classification"])
def classify_text(request: TextInput):
    """
    Receives text and returns a binary classification.
    """
    if not classifier:
        raise HTTPException(
            status_code=500,
            detail="Model is not loaded. Please reload the model.")

    # The pipeline returns a list of dictionaries, e.g., [{'label': 'LABEL_1', 'score': 0.9...}]
    # We take the first result as it's a single-text classification.
    result = classifier(request.text)
    return result[0]