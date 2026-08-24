"""
LibreCrawl CLI - Headless command-line entry point for SEO crawling.
Supports both interactive prompts and non-interactive scripted arguments.
"""

import argparse
import csv
import json
import os
import sys
from typing import Any

# Ensure correct module resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from LibreCrawl.engine import crawl_website, format_error_result, validate_url


def print_banner():
    """Print clean ASCII header."""
    print("=" * 60)
    print("   LibreCrawl - Headless SEO Crawling Engine")
    print("=" * 60)


def prompt_interactive() -> dict[str, Any]:
    """Run interactive question prompt when no URL is passed via CLI."""
    print_banner()
    print("Interactive Configuration:\n")

    # 1. URL
    while True:
        url = input("Website URL (e.g. https://example.com): ").strip()
        if not url:
            print("Error: URL cannot be empty.")
            continue
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        is_valid, err = validate_url(url)
        if is_valid:
            break
        print(f"Error: {err}")

    # 2. Max Depth
    depth_str = input("Maximum crawl depth [3]: ").strip()
    try:
        depth = int(depth_str) if depth_str else 3
    except ValueError:
        depth = 3

    # 3. Enable JavaScript
    js_str = input("Enable JavaScript rendering? (y/n) [n]: ").strip().lower()
    javascript = js_str in ("y", "yes", "true", "1")

    # 4. Enable PageSpeed
    ps_str = input("Enable PageSpeed analysis? (y/n) [n]: ").strip().lower()
    pagespeed = ps_str in ("y", "yes", "true", "1")

    # 5. Respect robots.txt
    robots_str = input("Respect robots.txt? (y/n) [y]: ").strip().lower()
    respect_robots = robots_str not in ("n", "no", "false", "0")

    # 6. Max Pages
    pages_str = input("Maximum pages [100]: ").strip()
    try:
        max_pages = int(pages_str) if pages_str else 100
    except ValueError:
        max_pages = 100

    # 7. Output File
    output = input("Output file [seo-result.json]: ").strip()
    if not output:
        output = "seo-result.json"

    return {
        "url": url,
        "depth": depth,
        "max_pages": max_pages,
        "javascript": javascript,
        "pagespeed": pagespeed,
        "respect_robots": respect_robots,
        "discover_sitemaps": True,
        "output": output,
        "json_stdout": False,
        "quiet": False,
    }


def save_csv_output(result: dict[str, Any], filepath: str):
    """Export pages and issues to CSV files."""
    pages = result.get("pages", [])
    if not pages:
        return

    fieldnames = [
        "url",
        "status_code",
        "title",
        "meta_description",
        "h1",
        "word_count",
        "canonical",
        "robots",
        "response_time_ms",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for p in pages:
            writer.writerow(p)


def main(args_list: list | None = None) -> int:
    """
    Main CLI entry point.
    Exit codes:
      0 = Crawl completed successfully
      1 = Crawl failed
      2 = Invalid input
      3 = Configuration error
      4 = Dependency/Runtime error
    """
    parser = argparse.ArgumentParser(
        description="LibreCrawl - Headless SEO Crawling & Audit Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--url", "-u", type=str, help="Target website URL to crawl")
    parser.add_argument(
        "--depth", "-d", type=int, default=3, help="Maximum crawl depth (default: 3)"
    )
    parser.add_argument(
        "--max-pages",
        "-m",
        type=int,
        default=100,
        help="Maximum pages to crawl (default: 100)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.05,
        help="Delay between requests in seconds (default: 0.05)",
    )
    parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=5,
        help="Number of concurrent crawl workers (default: 5)",
    )

    # Flags with positive/negative option pairs
    parser.add_argument(
        "--javascript",
        "--js",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable/disable JavaScript rendering via Playwright",
    )
    parser.add_argument(
        "--pagespeed",
        "--ps",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable/disable Google PageSpeed analysis",
    )
    parser.add_argument(
        "--respect-robots",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Respect/ignore robots.txt rules",
    )
    parser.add_argument(
        "--discover-sitemaps",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Discover and parse sitemaps",
    )
    parser.add_argument(
        "--external-links",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Include external links in link analysis",
    )
    parser.add_argument(
        "--images",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Crawl and check image URLs",
    )

    parser.add_argument(
        "--output", "-o", type=str, help="Path to output file (JSON or CSV)"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output machine JSON directly to stdout"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress non-essential terminal output",
    )
    parser.add_argument(
        "--serve", action="store_true", help="Start the headless JSON REST API server"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Port for the API server (default: 5000)"
    )

    args = parser.parse_args(args_list)

    # 1. Check if user requested starting the API server
    if args.serve:
        try:
            from LibreCrawl.server import run_server

            print(f"Starting LibreCrawl headless API server on port {args.port}...")
            run_server(port=args.port)
            return 0
        except Exception as e:
            if args.json:
                print(json.dumps(format_error_result("SERVER_START_ERROR", str(e))))
            else:
                print(f"Error starting server: {e}", file=sys.stderr)
            return 4

    # 2. If no URL is provided and not reading in pure JSON mode, run interactive prompt
    if not args.url:
        if args.json or not sys.stdin.isatty():
            err_json = format_error_result(
                "INVALID_URL", "Target URL is required. Provide --url <URL>."
            )
            print(json.dumps(err_json, indent=2))
            return 2

        config = prompt_interactive()
        target_url = config["url"]
        max_depth = config["depth"]
        max_pages = config["max_pages"]
        javascript = config["javascript"]
        pagespeed = config["pagespeed"]
        respect_robots = config["respect_robots"]
        discover_sitemaps = config["discover_sitemaps"]
        output_file = config["output"]
        json_stdout = config["json_stdout"]
        quiet = config["quiet"]
        crawl_external = False
        crawl_images = False
        delay = 0.05
        concurrency = 5
    else:
        target_url = args.url
        max_depth = args.depth
        max_pages = args.max_pages
        javascript = args.javascript
        pagespeed = args.pagespeed
        respect_robots = args.respect_robots
        discover_sitemaps = args.discover_sitemaps
        output_file = args.output
        json_stdout = args.json
        quiet = args.quiet
        crawl_external = args.external_links
        crawl_images = args.images
        delay = args.delay
        concurrency = args.concurrency

    # 3. Validate URL
    is_valid, err_msg = validate_url(target_url)
    if not is_valid:
        if json_stdout:
            print(
                json.dumps(
                    format_error_result("INVALID_URL", err_msg, {"url": target_url}),
                    indent=2,
                )
            )
        else:
            print(f"Error: {err_msg}", file=sys.stderr)
        return 2

    # 4. Progress tracker callback
    last_printed_crawled = [0]

    def on_progress(status_data: dict[str, Any]):
        if quiet or json_stdout:
            return
        crawled = status_data.get("stats", {}).get("crawled", 0)
        discovered = status_data.get("stats", {}).get("discovered", 0)
        if crawled > last_printed_crawled[0]:
            print(f"Crawled: {crawled} / {discovered or max_pages}")
            last_printed_crawled[0] = crawled

    # 5. Print initial status
    if not quiet and not json_stdout:
        print("\nStarting crawl...")
        print(f"URL: {target_url}")
        print(f"Depth: {max_depth}")
        print(f"Max Pages: {max_pages}")
        print(f"JavaScript: {'enabled' if javascript else 'disabled'}")
        print(f"PageSpeed: {'enabled' if pagespeed else 'disabled'}")
        print(f"Robots.txt: {'respected' if respect_robots else 'ignored'}\n")

    # 6. Execute crawl
    result = crawl_website(
        url=target_url,
        max_depth=max_depth,
        max_pages=max_pages,
        javascript=javascript,
        pagespeed=pagespeed,
        respect_robots=respect_robots,
        discover_sitemaps=discover_sitemaps,
        crawl_external=crawl_external,
        crawl_images=crawl_images,
        delay=delay,
        concurrency=concurrency,
        progress_callback=on_progress,
    )

    if result.get("status") == "failed":
        if json_stdout:
            print(json.dumps(result, indent=2))
        else:
            err = result.get("error", {})
            print(
                f"\nCrawl failed [{err.get('code', 'UNKNOWN')}]: {err.get('message', '')}",
                file=sys.stderr,
            )
        return 1

    # 7. Handle output
    summary = result.get("summary", {})

    if output_file:
        try:
            if output_file.lower().endswith(".csv") or args.format == "csv":
                save_csv_output(result, output_file)
            else:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
        except Exception as e:
            if json_stdout:
                print(
                    json.dumps(
                        format_error_result(
                            "FILE_WRITE_ERROR",
                            f"Could not write to output file: {e!s}",
                        ),
                        indent=2,
                    )
                )
            else:
                print(
                    f"Warning: Could not save output to {output_file}: {e}",
                    file=sys.stderr,
                )
            return 3

    if json_stdout:
        print(json.dumps(result, indent=2))
    elif not quiet:
        print("\n" + "=" * 40)
        print("Crawl completed successfully.")
        print(f"Pages: {summary.get('total_pages_crawled', 0)}")
        print(f"Links: {summary.get('total_links', 0)}")
        print(f"Issues: {summary.get('total_issues', 0)}")
        print(f"Duration: {summary.get('duration_seconds', 0)}s")
        if output_file:
            print(f"Output: {output_file}")
        print("=" * 40 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
