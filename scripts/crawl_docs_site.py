import os
import asyncio
import re
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import FilterChain, DomainFilter
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
OUTPUT_DIR = os.path.join(__location__, "output_markdown")   # This specifies the output directory

def sanitize_filename(url):
    filename = url.replace("https://", "").replace("http://", "")
    filename = re.sub(r'[?#].*$', '', filename)
    filename = filename.replace("/", "_").replace(":", "_").replace(".", "_")
    if not filename:
        return "root_page"
    return filename[:200] + ".md"

async def crawl_gitlab_docs_v1_focused_cleaning():
    print("\n--- Starting Recursive Crawl of docs.gitlab.com (v1 - Focused Cleaning with fit_markdown) ---")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    browser_config = BrowserConfig(headless=True, java_script_enabled=True, verbose=False)

    filter_chain = FilterChain([
        DomainFilter(      # Use these next 2 lines to configure whitelist and blacklist domains
            allowed_domains=["docs.gitlab.com"],
            blocked_domains=["archives.docs.gitlab.com", "design.gitlab.com", "about.gitlab.com", "customers.gitlab.com", "partners.gitlab.com", "handbook.gitlab.com", "learn.gitlab.com", "ir.gitlab.com", "investors.gitlab.com", "status.gitlab.com", "blog.gitlab.com"]
        )
    ])

    keyword_scorer = KeywordRelevanceScorer(
        keywords=["GitLab", "CI/CD", "Kubernetes", "DevOps", "security", "administration", "installation", "pipeline"],
        weight=0.5
    )

    current_cleaning_threshold = 0.2    # Change this to experiment with cleaning aggression
    print(f"Using PruningContentFilter threshold: {current_cleaning_threshold}")

    cleaning_markdown_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(
            threshold=current_cleaning_threshold,
            threshold_type="fixed",
            min_word_threshold=1       # Change this to experiment with cleaning
        ),
        options={"ignore_links": True}
    )

    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        page_timeout=60000,
        deep_crawl_strategy=BestFirstCrawlingStrategy(
            max_depth=5,            # Change this value to crawl deeper
            max_pages=20,           # Change this value to save more pages
            include_external=False,
            filter_chain=filter_chain,
            url_scorer=keyword_scorer,
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        markdown_generator=cleaning_markdown_generator,
        stream=True,
        verbose=True
    )

    results_count = 0
    markdown_files_saved = 0
    async with AsyncWebCrawler(config=browser_config) as crawler:
        start_url = "https://docs.gitlab.com/18.0/"       # Change this to start on a different page
        print(f"Starting crawl from: {start_url}")

        async for result in await crawler.arun(start_url, config=config):
            results_count += 1
            score = result.metadata.get("score", 0)
            depth = result.metadata.get("depth", "N/A")
            print(f"Crawled ({results_count} pages) | Depth: {depth} | Score: {score:.2f} | URL: {result.url}")

            content_to_save = None
            markdown_type_saved = "none"

            if result.markdown and hasattr(result.markdown, 'fit_markdown') and result.markdown.fit_markdown:
                content_to_save = result.markdown.fit_markdown
                markdown_type_saved = "fit_markdown"
                print(f"  Using fit_markdown. Length: {len(content_to_save)}")
            elif result.markdown and hasattr(result.markdown, 'raw_markdown') and result.markdown.raw_markdown:
                content_to_save = result.markdown.raw_markdown
                markdown_type_saved = "raw_markdown (fallback)"
                print(f"  WARNING: fit_markdown was empty. Falling back to raw_markdown. Length: {len(content_to_save)}")
            else:
                print(f"  No markdown content (fit or raw) to save for {result.url}")

            if content_to_save:
                filename = sanitize_filename(result.url)
                filepath = os.path.join(OUTPUT_DIR, filename)
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content_to_save)
                    print(f"  Saved {markdown_type_saved} to: {filename}")
                    markdown_files_saved += 1
                except Exception as e:
                    print(f"  Error saving {filename}: {e}")

    print(f"\nRecursive crawl completed. Total pages processed: {results_count}")
    print(f"Total markdown files saved: {markdown_files_saved}")
    print(f"All Markdown content saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(crawl_gitlab_docs_v1_focused_cleaning())
