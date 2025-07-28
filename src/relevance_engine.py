from sentence_transformers import SentenceTransformer, util
import torch
import time

# REMOVE the hardcoded path from here

class RelevanceEngine:
    # ADD model_path as an argument to the constructor
    def __init__(self, model_path: str):
        """
        Initializes the RelevanceEngine by loading the sentence-transformer model.
        
        Args:
            model_path (str): The local or container path to the saved model.
        """
        print("Initializing Relevance Engine...")
        start_time = time.time()
        
        device = "cpu"
        
        # USE the provided model_path argument
        try:
            self.model = SentenceTransformer(model_path, device=device)
        except Exception as e:
            # The error message is now more informative
            print(f"FATAL: Could not load model from '{model_path}'. Error: {e}")
            raise e

        end_time = time.time()
        print(f"Model loaded successfully from '{model_path}' in {end_time - start_time:.2f} seconds.")

    # ... the rest of the file (rank_chunks method) remains unchanged ...
    def rank_chunks(self, chunks: list, persona: dict, job_to_be_done: dict) -> list:
        if not chunks:
            print("Warning: No chunks provided to rank.")
            return []

        query = f"As a {persona.get('role', '')} with expertise in {persona.get('expertise', '')}, I need to {job_to_be_done.get('task', '')}"
        print(f"\nGenerated Query for ranking: '{query}'")

        print(f"Generating embeddings for {len(chunks)} chunks...")
        start_time = time.time()
        
        chunk_texts = [chunk['text'] for chunk in chunks]
        
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        chunk_embeddings = self.model.encode(chunk_texts, convert_to_tensor=True)
        
        end_time = time.time()
        print(f"Embeddings generated in {end_time - start_time:.2f} seconds.")

        cosine_scores = util.cos_sim(query_embedding, chunk_embeddings)

        for i, chunk in enumerate(chunks):
            chunk['score'] = cosine_scores[0][i].item()

        sorted_chunks = sorted(chunks, key=lambda x: x['score'], reverse=True)
        
        print("Ranking complete.")
        return sorted_chunks