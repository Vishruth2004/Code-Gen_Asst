import os
import json
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Crucial for allowing requests from your frontend

# Initialize Bedrock client once globally rather than inside every request
brt = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
)

SYSTEM_PROMPT = """You are an expert Principal Software Engineer and Code Assistant.
Follow these engineering guidelines:
1. Provide production-ready, clean, modular, and idiomatic code.
2. Include type hints, edge-case validation, and concise docstrings.
3. Keep conversational filler to a minimum: present the solution, explain key architectural decisions briefly, and mention time/space complexity if algorithmic.
4. If an image (diagram, error screenshot, UI mockup) is provided, diagnose the visual contents directly before writing the implementation."""

@app.route('/process', methods=['POST'])
def process():
    data = request.json or {}
    message = data.get('message', '')
    image = data.get('image')  # Expects base64-encoded string

    # Assemble user content blocks
    user_content = []
    if image:
        user_content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image
            }
        })
    user_content.append({"type": "text", "text": message})

    # High-quality few-shot examples demonstrating typing, docstrings, and edge handling
    few_shot_messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "Write a Python function to check if a number is prime."}]
        },
        {
            "role": "assistant",
            "content": [{
                "type": "text",
                "text": (
                    "```python\n"
                    "def is_prime(n: int) -> bool:\n"
                    "    \"\"\"Determine whether an integer is prime using 6k +/- 1 trial division.\"\"\"\n"
                    "    if n <= 1:\n"
                    "        return False\n"
                    "    if n <= 3:\n"
                    "        return True\n"
                    "    if n % 2 == 0 or n % 3 == 0:\n"
                    "        return False\n\n"
                    "    i = 5\n"
                    "    while i * i <= n:\n"
                    "        if n % i == 0 or n % (i + 2) == 0:\n"
                    "            return False\n"
                    "        i += 6\n"
                    "    return True\n"
                    "```\n\n"
                    "**Complexity:** Time: $O(\\sqrt{n})$ | Space: $O(1)$"
                )
            }]
        }
    ]

    # Use the native 'system' parameter in the Anthropic payload
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "temperature": 0.2,  # Lower temperature produces tighter, more deterministic code
        "system": SYSTEM_PROMPT,
        "messages": few_shot_messages + [{"role": "user", "content": user_content}]
    }

    try:
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        response = brt.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response['body'].read())
        text_content = response_body['content'][0]['text']
        return jsonify({'reply': text_content})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
