import asyncio
import os
import re

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, BestFirstCrawlingStrategy # Import deep crawl strategies
from crawl4ai.deep_crawling.filters import FilterChain, DomainFilter, URLPatternFilter # Import filters for exclusion/inclusion

OUTPUT_DIR = "output_markdown"

async def deep_crawl_gitlab_docs_with_exclusion_and_markdown():
    print("\n--- Starting Deep Crawl of docs.gitlab.com ---")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    browser_config = BrowserConfig(headless=True, java_script_enabled=True)

    # Define the deep crawl strategy with filters
    # The BFSDeepCrawlStrategy takes max_depth, include_external, and filter_chain
    # as parameters.
    deep_crawl_strategy = BFSDeepCrawlStrategy(
        max_depth=30, # Limit the crawl depth
        max_pages=5000, # Limit the total number of pages
        include_external=False, # Stay within the domain
        filter_chain=FilterChain([ # Use FilterChain for inclusions and exclusions
            DomainFilter(
                allowed_domains=["docs.gitlab.com"],
                blocked_domains=["archives.docs.gitlab.com"] # Exclude archives domain
            ),
            #URLPatternFilter(
            #    exclude_patterns=[r"https://docs\.gitlab\.com/development/.*"], # Exclude development URLs
            #    include_patterns=[r"https://docs\.gitlab\.com/.*"] # Include all docs.gitlab.com URLs
            #)
        ])
    )

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.48,
                threshold_type="fixed"
            )
        ),
        deep_crawl_strategy=deep_crawl_strategy, # Pass the defined deep crawl strategy here
        # The following were removed as they are handled by deep_crawl_strategy's filter_chain
        # exclude_patterns=crawl_exclude_patterns,
        # include_patterns=crawl_include_patterns,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        print(f"Starting deep crawl from https://docs.gitlab.com/")

        # Use crawler.arun and pass the start_url and the run_config
        crawl_generator = await crawler.arun(
            url="https://docs.gitlab.com/",
            config=run_config,
            stream=True # Set stream to True if you want to process results as they come
        )

        pages_crawled = 0
        # If stream=True, iterate directly over the async generator
        async for result in crawl_generator:
            if result.success:
                print(f"[OK] Crawled: {result.url} (Depth: {result.metadata.get('depth', 'N/A')})")

                markdown_content = result.markdown.fit_markdown if result.markdown else None

                if markdown_content:
                    cleaned_url = result.url.replace("https://", "").replace("http://", "")
                    cleaned_url = re.sub(r'[^\w\-_\. ]', '_', cleaned_url)
                    cleaned_url = cleaned_url.strip('_').strip('.')
                    filename = f"{cleaned_url}.md"
                    filepath = os.path.join(OUTPUT_DIR, filename)

                    try:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(markdown_content)
                        print(f"Saved markdown to {filepath}")
                    except Exception as e:
                        print(f"Error saving markdown for {result.url}: {e}")
                else:
                     print(f"[INFO] No fit_markdown content for {result.url}")

                pages_crawled += 1
            else:
                print(f"[FAIL] URL: {result.url}, Error: {result.error_message}")

        print(f"\nDeep crawl finished. Total pages successfully crawled and processed: {pages_crawled}")

if __name__ == "__main__":
    asyncio.run(deep_crawl_gitlab_docs_with_exclusion_and_markdown())
