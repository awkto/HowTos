import os
import asyncio
import re # Added for sanitizing filenames
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    DomainFilter,
    URLPatternFilter,
    ContentTypeFilter
)
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

# Define the base directory for saving markdown files
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
OUTPUT_DIR = os.path.join(__location__, "gitlab_docs_crawled_markdown")

# Function to sanitize URLs into valid filenames
def sanitize_filename(url):
    # Remove protocol (http/https), replace slashes with hyphens, and remove query params/fragments
    filename = url.replace("https://", "").replace("http://", "")
    filename = re.sub(r'[?#].*$', '', filename) # Remove query parameters and fragments
    filename = filename.replace("/", "_").replace(":", "_").replace(".", "_")
    # Limit length and ensure it's not empty
    if not filename:
        return "root_page"
    return filename[:200] + ".md" # Limit length for very long URLs and add .md extension

async def crawl_gitlab_docs_recursively_to_markdown():
    print("\n--- Starting Recursive Crawl of docs.gitlab.com for Markdown ---")

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Define BrowserConfig separately, it will be passed to AsyncWebCrawler
    browser_config = BrowserConfig(headless=True, java_script_enabled=True)

    # 1. Define Filters
    filter_chain = FilterChain([
        DomainFilter(
            allowed_domains=["docs.gitlab.com"]
        ),
        #URLPatternFilter(
        #    patterns=[
        #        "https://docs.gitlab.com/**" # This pattern includes all URLs under docs.gitlab.com
        #    ]
        #),
        #ContentTypeFilter(allowed_types=["text/html"]) # Only crawl HTML pages
    ])

    # 2. Define Scorer (Optional but good for prioritizing content)
    keyword_scorer = KeywordRelevanceScorer(
        keywords=["GitLab", "CI/CD", "Kubernetes", "DevOps", "security", "administration", "installation", "pipeline"],
        weight=0.5
    )

    # 3. Configure the CrawlerRunConfig for Deep Crawling
    # Removed 'output_dir' from here
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS, # Use BYPASS for testing, ENABLED for production to save time/requests
        max_range=200, # Set a reasonable limit to avoid infinite crawls.
        page_timeout=60000, # 60 seconds timeout per page
        deep_crawl_strategy=BestFirstCrawlingStrategy(
            max_depth=5, # How many levels deep to crawl.
            include_external=False, # VERY IMPORTANT: Stay within docs.gitlab.com
            filter_chain=filter_chain,
            url_scorer=keyword_scorer,
            # wait_for="networkidle0",
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.48,
                threshold_type="fixed",
                min_word_threshold=0
            ),
            options={"ignore_links": True}
        ),
        stream=True,
        verbose=True
    )

    results_count = 0
    async with AsyncWebCrawler(config=browser_config) as crawler:
        async for result in await crawler.arun("https://docs.gitlab.com", config=config):
            results_count += 1
            score = result.metadata.get("score", "N/A")
            depth = result.metadata.get("depth", "N/A")
            print(f"Crawled ({results_count} pages) | Depth: {depth} | Score: {score:.2f} | URL: {result.url}")

            # Manually save the markdown content to a file
            if result.markdown and result.markdown.raw_markdown:
                filename = sanitize_filename(result.url)
                filepath = os.path.join(OUTPUT_DIR, filename)
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(result.markdown.raw_markdown) # You can choose raw_markdown or fit_markdown
                    print(f"  Saved: {filename}")
                except Exception as e:
                    print(f"  Error saving {filename}: {e}")
            else:
                print(f"  No markdown content to save for {result.url}")

    print(f"\nRecursive crawl completed. Total pages crawled: {results_count}")
    print(f"All Markdown content saved to: {OUTPUT_DIR}")

# Main execution block
if __name__ == "__main__":
    asyncio.run(crawl_gitlab_docs_recursively_to_markdown())
