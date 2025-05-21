### Instructions: Running the `crawl4ai` GitLab Docs Crawler

This guide assumes you are on a Debian/Ubuntu.

**Goal:** Recursively crawl `docs.gitlab.com` and save all crawled pages as Markdown files.

**1. Install Python 3, pip, python-is-python3, and venv**

Install python, pip, and venv.

```bash
sudo apt update
sudo apt install python3 python3-pip python-is-python3 python3-venv -y
```

**2. Set up Python Virtual Environment**

Create project dir and python venv

```bash
# Navigate to your home dir
cd ~

# Create a directory for your project
mkdir gitlabdocs-crawl
cd gitlabdocs-crawl

# Create a virtual environment named 'venv'
python -m venv venv
```

**3. Activate Virtual Environment**

Activate the venv

```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt, indicating the virtual environment is active.

**4. Install `crawl4ai`**

With the virtual environment active, install the `crawl4ai` library using pip.

```bash
pip install crawl4ai
```

**5. Create Python Script**

Grab or copy this Python script  in your `gitlabdocs-crawl` dir.
- Script : [scripts/crawl_docs_site.py](scripts/crawl_docs_site.py)

**6. Run Crawler**

Make sure your virtual environment is still active (you should see `(venv)` in your terminal prompt). Then, execute the Python script:

```bash
python recursive_gitlab_crawler.py
```

The crawler will start, print its progress to the terminal, and save the Markdown files in the `gitlabdocs-crawl/gitlab_docs_crawled_markdown` directory.

-----

**Important Notes:**

  * **Deactivating venv:** When you're done working on this project, you can deactivate the virtual environment by typing `deactivate` in your terminal.
  * **Resource Usage:** Crawling a large site like `docs.gitlab.com` can consume significant network bandwidth, CPU, and disk space. Monitor your system's resources.
  * **`max_range` and `max_depth`:** I've increased these slightly in the script to `500` and `10` respectively, as GitLab's documentation is quite extensive. Adjust these values based on how many pages you ultimately want to crawl and how deep the structure goes.
  * **Ethical Crawling:** Always be mindful of the website's `robots.txt` file (though `crawl4ai` doesn't automatically obey it unless configured). For personal use and learning, this is generally fine, but for larger scale or commercial operations, respecting `robots.txt` and not overwhelming the server is crucial.
