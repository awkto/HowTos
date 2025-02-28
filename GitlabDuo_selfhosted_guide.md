# GitLab with Self Hosted LLM 
This example deploys Mistral or similar LLM on **DigitalOcean GPU 1-Click Droplet** and connects it with a self hosted **GitLab EE 17.9**
or later using the required **AI Gateway** in a Docker instance.

## GitLab and License 
1. Install GitLab version 17.9 or later
2. Add License or Subscription for GitLab Duo and Ultimate

## Deploy AI Gateway in Docker
1. Deploy the AI Gateway matching the same version as Gitlab
   ```
   docker run -d -p 5052:5052 \
     -e AIGW_GITLAB_URL=https://gitlab01.example.com \
     -e AIGW_GITLAB_API_URL=https://gitlab01.example.com/api/v4/ \
      registry.gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/model-gateway:self-hosted-v17.9.0-ee
   ```
   _Update the Gitlab URL, API URL, and image tag version for yours_
2. Go back to **Gitlab > Admin > GitLab Duo > Change Configuration**
3. Add the local AI gateway at the bottom such as `http://gateway.example.com:5052`
![image](https://github.com/user-attachments/assets/7f585895-9a7e-4ba1-8ff9-14d57c216b4c)

## Deploy an LLM on DigitalOcean
1. Deploy a supported LLM such as **Mistral-7B-Instruct-v0.3** on DigitalOcean GPU Droplets
2. SSH into the Droplet to see the API Key in the login message
3. Test the AI API endpoint with this curl/shell script
   ```
   #!/bin/bash
   curl -X 'POST' \
     'http://[DROPLET-IP-HERE]/v1/chat/completions' \
     -H 'accept: application/json' \
     -H 'Content-Type: application/json' \
     -H 'Authorization: Bearer '[BEARER-TOKEN-HERE]'' \
     -d '{
       "model": "<model_name>",
       "messages": [{"role":"user", "content":"What is Deep Learning?"}],
       "max_tokens": 64,
       "stream": false
   }'
   ```
   _Update the DROPLET-IP and the BEARER-TOKEN_
4. You may need to run OS updates and reboot if the endpoint doesn't start serving
5. You can also monitor the logs with `docker logs [container name]`

## Add LLM Endpoint in GitLab
1. Back in GitLab, go to **Admin > Self Hosted Duo > Add Self Hosted Model**
2. Add a name, the specific endpoint such as `http://232.50.60.2:80/v1` and the bearer token
3. Hit save, and then hit Test Connection. If the test fails, go back to step 6 and test with curl.
![image](https://github.com/user-attachments/assets/9111f501-84cb-40e9-be94-691d14747c01)
