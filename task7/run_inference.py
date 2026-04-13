import os
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# --- MODULE IMPORTS & FALLBACKS ---
try:
    # Attempt to load custom parsers for different document types
    from parsers import PARSERS
except ImportError:
    # Standard mock parsers if the external module is missing
    PARSERS = {
        "docx": lambda path: f"Fake extracted text for {path}",
        "pymupdf": lambda path: f"Fake extracted text for {path}",
        "ocr": lambda path: f"Fake OCR text for {path}"
    }

class FastTopicPredictor:
    """
    Handles 'Inference Phase' logic: Classifies new documents by comparing their 
    mathematical embeddings against pre-calculated topic centroids.
    """
    def __init__(self, models_dir="models"):
        print("Loading Fast Inference Assets...")
        
        # 1. LOAD THE BRAIN: Load the transformer model (Phase 1: Embedding)
        self.embedding_model = SentenceTransformer("all-mpnet-base-v2")
        
        # 2. PATH SETUP: Locate the 'models' folder and artifact files
        task7_dir = Path(__file__).resolve().parent
        models_path = task7_dir / models_dir
        mapping_path = models_path / "topic_mapping.json"
        centroids_path = models_path / "topic_centroids.json"
        
        # 3. VALIDATION: Ensure training has been completed successfully
        if not models_path.exists():
            raise FileNotFoundError(f"Directory not found: {models_path}")

        if not mapping_path.exists() or not centroids_path.exists():
            raise FileNotFoundError(f"Missing model files in {models_path}! Run train_topic_model.py first.")

        # 4. DATA LOADING: Load Human Labels and Mathematical Centroids
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.topic_mapping = json.load(f)
            
        with open(centroids_path, "r", encoding="utf-8") as f:
            centroids_dict = json.load(f)
            # Convert list vectors back into NumPy arrays for fast math operations
            self.centroids = {k: np.array(v) for k, v in centroids_dict.items()}
            
        print(f"Ready! Loaded {len(self.centroids)} topic centroids from {models_path.name}.")

    def cosine_similarity(self, vec1, vec2):
        """
        Calculates the semantic distance between two vectors.
        Higher score (closer to 1.0) = smaller angle = more similar meaning.
        """
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def predict(self, text):
        """
        Core Inference Logic:
        1. Encodes input text into a high-dimensional vector.
        2. Loops through saved centroids to find the best mathematical match.
        """
        if not text.strip():
            return "Unknown", "Unknown", 0.0

        # Step 1: Vectorization - Turn the new text into a semantic coordinate
        new_embedding = self.embedding_model.encode([text])[0]
        
        best_topic_id = None
        highest_score = -1.0 

        # Step 2: Comparison - Compare the new vector against every trained topic center
        for topic_id, centroid_vector in self.centroids.items():
            score = self.cosine_similarity(new_embedding, centroid_vector)
            
            # Keep track of the topic with the highest similarity score
            if score > highest_score:
                highest_score = score
                best_topic_id = topic_id

        # Step 3: Mapping - Convert the winning ID into a human-friendly label
        predicted_label = self.topic_mapping.get(str(best_topic_id), f"Topic {best_topic_id}")
        return best_topic_id, predicted_label, float(highest_score)

def main():
    # SETUP: Define input (dataset) and output (results) paths
    current_dir = Path(__file__).parent
    dataset_dir = current_dir / "dataset"
    results_dir = current_dir / "results"
    
    # Ensure the output directory exists
    results_dir.mkdir(parents=True, exist_ok=True)

    if not dataset_dir.exists():
        print(f"Error: Cannot find the dataset folder at {dataset_dir}")
        return

    # INITIALIZE: Load the predictor engine
    predictor = FastTopicPredictor()
    classification_output = []

    print(f"\nProcessing .txt and .md files in: {dataset_dir.name}/...")

    # MAIN LOOP: Iterate through files in the dataset folder
    for file_path in dataset_dir.iterdir():
        if not file_path.is_file():
            continue  # Ignore sub-directories

        file_name = file_path.name
        ext = file_path.suffix.lower()
        text = ""

        # FILTER: Only process standard text-based files
        if ext in ['.txt', '.md']:
            print(f"Reading {file_name}...")
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    text = file.read()
            except Exception as e:
                print(f"  -> Failed to read {file_name}: {e}")
                continue
        else:
            # Silently skip non-target extensions
            continue

        # PREDICTION: Execute the classification if text exists
        if text.strip():
            topic_id, label, confidence = predictor.predict(text)
            print(f"  -> Label: [{label}] (Confidence: {confidence*100:.1f}%)")

            # Collect results for the final JSON export
            classification_output.append({
                "file": file_name,
                "topic_id": str(topic_id),
                "label": label,
                "confidence_score": round(float(confidence), 3)
            })
        else:
            print(f"  -> {file_name} is empty.")

    # EXPORT: Save all findings to a structured JSON for the frontend/API
    if classification_output:
        results_path = results_dir / "classification_results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(classification_output, f, indent=4)
        print(f"\nFinished! Processed {len(classification_output)} files. Results saved to {results_path}")
    else:
        print("\nFinished! No valid .txt or .md files were found/processed.")

if __name__ == "__main__":
    main()