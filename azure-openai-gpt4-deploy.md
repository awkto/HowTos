## Deploy GPT 4o on Azure OpenAI

<br>

1. Log in to [portal.azure.com](https://portal.azure.com "https://portal.azure.com")
2. Go to **Azure OpenAI** via search
3. Click **Ceate Azure OpenAI**
4. Click Next, Next, Create
5. Go to the Resource once it has finished creating
6. Go into **Azure AI Foundry Portal**
7. Click **Create Deployment**
8. Select model **GPT 4o** which should be on the [supported model list](https://docs.gitlab.com/administration/gitlab_duo_self_hosted/supported_models_and_hardware_requirements/ "https://docs.gitlab.com/administration/gitlab_duo_self_hosted/supported_models_and_hardware_requirements/")
9. Click **Deploy**
10. Go to Deployments > Select the newly Deployed model to see the URL and key
11. Truncate the URL just after `.../completions` for Gitlab Duo
12. For Gitlab Duo, use model identifier `openai/gpt-4o` 

<br>

<br>

### Test Endpoint

For the Test query script you will need
- Endpoint URL
- Key / Token

#### Test with Token

```
#!/bin/bash

API_URL="[ADD URL HERE]"
TOKEN="[ADD TOKEN HERE"
QUESTION="What is gravel made of"

# Make the API request using curl
curl -X POST "$API_URL" \
    -H "api-key: $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "messages": [
            {
                "role": "user",
                "content": "'"$QUESTION"'"
            }
        ],
        "model": "openai/gpt-4o"
    }'
```

<br>
