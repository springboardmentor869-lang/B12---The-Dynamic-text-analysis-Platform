# Chunk-Based Document Classification

This project classifies documents into topics using a chunk-based approach.

Pipeline:
Document → Chunking → Embedding → Cosine Similarity → Topic Classification

Technologies Used:
- Python
- BERTopic
- Sentence Transformers
- NumPy
- Scikit-learn

Features:
- Document chunking
- Topic classification
- Cosine similarity matching
- BERTopic model training

Run training:
python train_bertopic.py

Run inference:
python inference.py