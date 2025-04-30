## Set Up Shell-GPT CLI tool for AI chat

### Shell GPT
1. Install python `apt install python3`
2. Install pipx `sudo apt install pipx`
3. Ensure pipx executables are in your PATH `pipx ensurepath`
4. Install shell-gpt with pipx `pipx install shell-gpt`
5. Logout/Log back in
6. Run shell gpt with `sgpt`
7. Authenticate with an LLM backend using a token


### Shell GPT on Windows
1. Install python `winget install Python.Python.3.11`
2. Install pipx `python -m pip install --user pipx`
3. Ensure path is added `python -m pipx ensurepath`
4. Install shell-gpt with pipx `pipx install shell-gpt`
5. Logout/Log back in
6. Run shell gpt with `sgpt`
7. Authenticate with an LLM backend using a token


### LiteLLM (Optional)
Use this to inject litellm module into the pipx installation of shell-gpt
```
pipx inject shell-gpt litellm
```


### API Keys
1. Gemini / Google
   - https://aistudio.google.com/
2. ChatGPT / OpenAI
   - https://platform.openai.com/


### Wrapper for Quotes
sgpt requires your query to be wrapped in quotes every time. for example
```
sgpt "what is a kernel panic"
```

You can use a wrapper function to make this easier and not have to enter quotes

Create this function in your `.bashrc`
```
ask() {
  sgpt "$*"
}
```

Reload your session or run `bash`

Now just use **ask** binary your query without quotes
```
ask what is a kernel panic"
``` 


### Use Ctrl+I hotkey

1. Install with
```
sgpt --install-integration
```

2. Relaunch shell
3. To use it, type in a human readable command like "revert last 3 commits in git"
4. Hit `Ctrl + l` hotkey to convert that line to a command
