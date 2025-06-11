from flask import Flask, request, jsonify
import boto3
import json
import base64

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    message = data.get('message')
    image = data.get('image')

    # Initialize the Bedrock runtime client
    brt = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

    # Prepare the body for the request
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": []
    }

    if image:
        body["messages"].append({
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image
                    }
                },
                {
                    "type": "text",
                    "text": message
                }
            ]
        })
    else:
        body["messages"].append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        })

    # Define the model ID and content type
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    content_type = "application/json"
    accept = "application/json"

    # Send the request
    response = brt.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType=content_type,
        accept=accept
    )

    # Parse the response
    response_body = json.loads(response['body'].read())
    text_content = response_body['content'][0]['text']
    print(jsonify({'reply': text_content}))
    return jsonify({'reply': text_content})

if __name__ == '__main__':
    app.run(port=8000, debug=True)