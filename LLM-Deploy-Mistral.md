## Deploy Mistral on vLLM

1. Deploy GPU droplet
2. Ensure you have access to [Mistral model](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2 "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2") on huggingface.co
3. Generate **read** token from hugging face
4. Install pip `apt install python3-pip` 
5. Install venv `apt install python3.10-venv` 
6. Create venv `python3 -m venv ~/mistral-venv` 
7. Activate venv `source ~/mistral-venv/bin/activate`  
8. Install vllm and openai inside venv `pip install vllm openai` 
9. Install huggingface-cli `pip install -U "huggingface_hub[cli]"` 
10. Log in with `huggingface-cli login`
11. Deploy mistral

```
python -m vllm.entrypoints.openai.api_server \
    --model mistralai/Mistral-7B-Instruct-v0.2
```
12. Allow port 8000 through firewall `ufw allow 8000` 
13. Access on port 8000⁠ without a bearer token

<br>

<br>

### Test Query 

#### Shell script to test without token

```
#!/bin/bash
API_URL="http://llm1.example.com:8000/v1/chat/completions"
QUESTION="What is gravel made of"

curl -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{
        "messages": [
            {
                "role": "user",
                "content": "'"$QUESTION"'"
            }
        ],
        "model": "mistralai/Mistral-7B-Instruct-v0.2"
    }'
```

<br>

#### Shell script to test with bearer token

```
#!/bin/bash
API_URL="http://llm1.example.com:8000/v1/chat/completions"
TOKEN="SUMMERTIME"
QUESTION="What is gravel made of"

curl -X POST "$API_URL" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "messages": [
            {
                "role": "user",
                "content": "'"$QUESTION"'"
            }
        ],
        "model": "mistralai/Mistral-7B-Instruct-v0.2"
    }'
```

<br>
