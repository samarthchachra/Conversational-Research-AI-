from app.services.retrieval.adaptive_rag_pipeline import (
    AdaptiveRagPipeline
)

pipeline = AdaptiveRagPipeline()

response = pipeline.invoke(
    "yolo architecture"
)

print(response)