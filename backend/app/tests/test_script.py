import boto3
import json
from dotenv import load_dotenv

load_dotenv()

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="eu-central-1"
)

def get_embedding(text, dimensions=1024, normalize=True):
    body = json.dumps({
        "inputText": text,
        "dimensions": dimensions,
        "normalize": normalize
    })

    response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        contentType="application/json",
        accept="application/json",
        body=body
    )

    result = json.loads(response["body"].read())
    return result["embedding"]

vector = get_embedding("my name is samarth")
print("Embedding length:", len(vector))
print("First 5 values:", vector[:5])