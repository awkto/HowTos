## AI Gateway Flags

## <br>

## Deploy Gateway disabling Auth

#### Add AIGW\_AUTH\_\_BYPASS\_EXTERNAL 

Add `-e AIGW_AUTH__BYPASS_EXTERNAL=true`  to docker run command

```
docker run --name gateway17.11.1 -d -p 5052:5052 \
 -e AIGW_AUTH__BYPASS_EXTERNAL=true -e AIGW_GITLAB_URL=https://gitlab.example.com \
 -e AIGW_GITLAB_API_URL=https://gitlab.example.com/api/v4/ \
registry.gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/model-gateway:self-hosted-v17.11.0-ee
```

<br>

<br>

## Deploy Gateway disable streaming

#### Add AIGW\_CUSTOM\_MODELS\_\_DISABLE\_STREAMING  

Add `-e AIGW_CUSTOM_MODELS__DISABLE_STREAMING=true`  to docker run command

```
docker run --name gateway17.11.1 -d -p 5052:5052 \
 -e AIGW_AUTH__BYPASS_EXTERNAL=true -e AIGW_GITLAB_URL=https://gitlab.example.com \
 -e AIGW_GITLAB_API_URL=https://gitlab.example.com/api/v4/ \
 -e AIGW_CUSTOM_MODELS__DISABLE_STREAMING=true \
registry.gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/model-gateway:self-hosted-v17.11.0-ee.0
```

<br>

<br>
