from flask import Flask, request, jsonify
import boto3
import json

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    message = data.get('message')
    image = data.get('image')

    # Initialize Bedrock client
    brt = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

    # Combine system prompt + user message
    system_instruction = "You're a senior developer assistant. Always respond with clean, well-commented code."

    # Add instruction to consider image
    if image:
        message = f"{system_instruction}\n\n{message}\n\nPlease refer to the attached image and consider it while answering."
    else:
        message = f"{system_instruction}\n\n{message}"

    # Build user prompt with optional image
    user_prompt = {
        "role": "user",
        "content": []
    }

    if image:
        user_prompt["content"].append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image
            }
        })

    user_prompt["content"].append({
        "type": "text",
        "text": message
    })

    # Few-shot examples to help Claude understand the style
    few_shot_messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "Write a Python function to check if a number is prime."}]
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text":
                '''
                ```python
def is_prime(n):
    """
    Check if a number is prime.
    A prime number is greater than 1 and only divisible by 1 and itself.
    """
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```'''}]
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": "Create a Flask endpoint to return current server time in JSON."}]
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text":
                '''```python
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/time')
def get_time():
    # Return current server time in JSON
    return jsonify({"server_time": datetime.now().isoformat()})
```'''}]
        }
    ]

    # Compose the final body for the API call
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": few_shot_messages + [user_prompt]
    }

    # Model call
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    response = brt.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    # Parse the response
    response_body = json.loads(response['body'].read())
    text_content = response_body['content'][0]['text']
    return jsonify({'reply': text_content})

if __name__ == '__main__':
    app.run(port=8000, debug=True)
