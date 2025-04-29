5163610235294665## How to set up CLI tool for AI chat

### Shell GPT

1. Install python `sudo apt install pipx`
2. Ensure pipx executables are in your PATH `pipx ensurepath`
3. Install shell-gpt with pipx `pipx install shell-gpt`
4. Logout/Log back in
5. Run shell gpt with `sgpt`
6. Authenticate with an LLM backend using a token


### Using LiteLLM for Gemini
Use this to inject litellm module into the pipx installation of shell-gpt
```
pipx inject shell-gpt litellm
```


### API Keys
1. Gemini / Google
   - https://aistudio.google.com/
2. ChatGPT / OpenAI
   - https://platform.openai.com/

