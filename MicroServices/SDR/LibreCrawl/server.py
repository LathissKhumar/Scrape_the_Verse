"""
LibreCrawl Headless Server - Lightweight JSON REST API for microservice integration.
Does NOT serve any HTML or frontend assets. Pure JSON endpoints only.
"""

import os
import sys
import threading
from typing import Dict
from flask import Flask, request, jsonify

# Ensure correct module resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from LibreCrawl.engine import CrawlJob, validate_url, format_error_result

app = Flask(__name__)

# In-memory registry of active crawl jobs
jobs: Dict[str, CrawlJob] = {}
jobs_lock = threading.Lock()


@app.route('/health', methods=['GET'])
def health_check():
    """Service health probe."""
    return jsonify({"status": "ok", "service": "LibreCrawl Headless Engine"})


@app.route('/api/crawl', methods=['POST'])
def start_crawl_endpoint():
    """
    Start a new headless crawl job.
    Expects JSON payload with 'url' and optional parameters.
    """
    data = request.get_json(silent=True) or {}
    url = data.get('url')
    
    if not url:
        return jsonify(format_error_result("MISSING_PARAMETER", "Field 'url' is required.")), 400

    is_valid, err_msg = validate_url(url)
    if not is_valid:
        return jsonify(format_error_result("INVALID_URL", err_msg, {"url": url})), 400

    max_depth = int(data.get('max_depth', data.get('depth', 3)))
    max_pages = int(data.get('max_pages', 100))
    javascript = bool(data.get('javascript', False))
    pagespeed = bool(data.get('pagespeed', False))
    respect_robots = bool(data.get('respect_robots', True))
    discover_sitemaps = bool(data.get('discover_sitemaps', True))
    crawl_external = bool(data.get('crawl_external', False))
    crawl_images = bool(data.get('crawl_images', False))
    delay = float(data.get('delay', 0.05))
    concurrency = int(data.get('concurrency', 5))
    timeout = int(data.get('timeout', 30))

    job = CrawlJob()
    with jobs_lock:
        jobs[job.job_id] = job

    ok, msg = job.start(
        url=url,
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
        timeout=timeout
    )

    if not ok:
        with jobs_lock:
            jobs.pop(job.job_id, None)
        return jsonify(format_error_result("CRAWL_START_FAILED", msg, {"url": url})), 500

    return jsonify({
        "job_id": job.job_id,
        "status": "running",
        "url": url,
        "message": "Crawl job started successfully"
    }), 202


@app.route('/api/crawl/<job_id>', methods=['GET'])
def get_crawl_status(job_id: str):
    """Get the current progress and light status of a crawl job."""
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify(format_error_result("JOB_NOT_FOUND", f"No crawl job found with ID {job_id}")), 404

    return jsonify(job.get_status())


@app.route('/api/crawl/<job_id>/result', methods=['GET'])
def get_crawl_result(job_id: str):
    """Retrieve full normalized JSON results for a crawl job."""
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify(format_error_result("JOB_NOT_FOUND", f"No crawl job found with ID {job_id}")), 404

    return jsonify(job.get_results())


@app.route('/api/crawl/<job_id>/issues', methods=['GET'])
def get_crawl_issues(job_id: str):
    """Get detected SEO issues with optional severity or category filters."""
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify(format_error_result("JOB_NOT_FOUND", f"No crawl job found with ID {job_id}")), 404

    result = job.get_results()
    issues = result.get('issues', [])

    severity = request.args.get('severity')
    category = request.args.get('category')

    if severity:
        issues = [i for i in issues if i.get('severity', '').lower() == severity.lower()]
    if category:
        issues = [i for i in issues if i.get('category', '').lower() == category.lower()]

    return jsonify({
        "job_id": job_id,
        "total_issues": len(issues),
        "issues": issues
    })


@app.route('/api/crawl/<job_id>/pages', methods=['GET'])
def get_crawl_pages(job_id: str):
    """Get crawled pages for a crawl job."""
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify(format_error_result("JOB_NOT_FOUND", f"No crawl job found with ID {job_id}")), 404

    result = job.get_results()
    pages = result.get('pages', [])
    return jsonify({
        "job_id": job_id,
        "total_pages": len(pages),
        "pages": pages
    })


@app.route('/api/crawl/<job_id>/links', methods=['GET'])
def get_crawl_links(job_id: str):
    """Get links discovered during a crawl job."""
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify(format_error_result("JOB_NOT_FOUND", f"No crawl job found with ID {job_id}")), 404

    result = job.get_results()
    links = result.get('links', [])
    return jsonify({
        "job_id": job_id,
        "total_links": len(links),
        "links": links
    })


@app.route('/api/crawl/<job_id>/stop', methods=['POST'])
def stop_crawl_endpoint(job_id: str):
    """Stop an ongoing crawl job."""
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify(format_error_result("JOB_NOT_FOUND", f"No crawl job found with ID {job_id}")), 404

    ok, msg = job.stop()
    return jsonify({"job_id": job_id, "stopped": ok, "message": msg})


def run_server(host: str = "0.0.0.0", port: int = 5000):
    """Start the headless REST API server."""
    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    run_server()
