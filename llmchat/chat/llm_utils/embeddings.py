"""
Functions copied from GCP examples:
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/language/examples/langchain-intro/intro_langchain_palm_api.ipynb
"""

import time
from typing import List
from pydantic import BaseModel
from langchain.embeddings import VertexAIEmbeddings
from pgvector.django import CosineDistance

from chat.models import Message, User, Chat, DocumentChunk, Document


# Utility functions for Embeddings API with rate limiting
def rate_limit(max_per_minute):
    period = 60 / max_per_minute
    print("Waiting")
    while True:
        before = time.time()
        yield
        after = time.time()
        elapsed = after - before
        sleep_time = max(0, period - elapsed)
        if sleep_time > 0:
            print(".", end="")
            time.sleep(sleep_time)


class CustomVertexAIEmbeddings(VertexAIEmbeddings, BaseModel):
    requests_per_minute: int
    num_instances_per_batch: int

    # Overriding embed_documents method
    def embed_documents(self, texts: List[str]):
        limiter = rate_limit(self.requests_per_minute)
        results = []
        docs = list(texts)

        while docs:
            # Working in batches because the API accepts maximum 5
            # documents per request to get embeddings
            head, docs = (
                docs[: self.num_instances_per_batch],
                docs[self.num_instances_per_batch :],
            )
            chunk = self.client.get_embeddings(head)
            results.extend(chunk)
            next(limiter)

        return [r.values for r in results]


# Embedding
EMBEDDING_QPM = 100
EMBEDDING_NUM_BATCH = 5
gcp_embeddings = CustomVertexAIEmbeddings(
    requests_per_minute=EMBEDDING_QPM,
    num_instances_per_batch=EMBEDDING_NUM_BATCH,
)

def get_docs_chunks_by_embedding(request, query):
    query_embedding = gcp_embeddings.embed_documents([query])[0]
    user_docs = Document.objects.filter(user=request.user)
    # documents_by_mean = user_docs.order_by(
    #     CosineDistance("mean_embedding", query_embedding)
    # )[:3]
    documents_by_summary = user_docs.order_by(
        CosineDistance("summary_embedding", query_embedding)
    )[:3]
    chunks_by_embedding = DocumentChunk.objects.filter(document__in=user_docs).order_by(
        CosineDistance("embedding", query_embedding)
    )[:10]
    return documents_by_summary, chunks_by_embedding
