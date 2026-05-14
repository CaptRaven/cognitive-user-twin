import torch
print(f"Torch version: {torch.__version__}")
import numpy as np
print(f"NumPy version: {np.__version__}")
from sentence_transformers import SentenceTransformer
print("SentenceTransformer imported successfully")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded successfully")
emb = model.encode("Hello world")
print(f"Embedding shape: {emb.shape}")
