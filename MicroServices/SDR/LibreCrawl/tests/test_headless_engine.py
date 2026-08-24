"""
Comprehensive Tests for LibreCrawl Headless Engine & SEO Agent
Runs an in-process mock HTTP server and tests:
1. Programmatic `crawl_website`
2. Normalized JSON schema conformance
3. CLI interactive/non-interactive execution & exit codes
4. SEO Agent LangGraph end-to-end execution
"""

import http.server
import json
import os
import subprocess
import sys
import threading
import time
import unittest

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from LibreCrawl.engine import crawl_website, validate_url
from seo.seo_agent import run_seo_audit

TEST_PORT = 8990


class MockSiteHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype="text/html"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <title>Example Corp - Leading Innovation</title>
                <meta name="description" content="Example Corp provides enterprise solutions and industry insights for modern businesses." />
                <link rel="canonical" href="http://127.0.0.1:8990/" />
            </head>
            <body>
                <h1>Welcome to Example Corp</h1>
                <p>Example Corp delivers high quality software and SEO auditing services across the globe.</p>
                <a href="/about.html">About Us</a>
                <a href="/broken.html">Broken Link</a>
                <img src="/logo.png" alt="Company Logo" />
            </body>
            </html>"""
            self._send(200, html)
        elif self.path == "/about.html":
            html = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <title>About Us</title>
                <link rel="canonical" href="http://127.0.0.1:8990/about.html" />
            </head>
            <body>
                <h1>About Our Mission</h1>
                <p>Short page description.</p>
                <a href="/">Home</a>
            </body>
            </html>"""
            self._send(200, html)
        elif self.path == "/broken.html":
            self._send(404, "Page Not Found")
        else:
            self._send(404, "Not Found")


class TestHeadlessEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", TEST_PORT), MockSiteHandler
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_url_validation(self):
        ok, _ = validate_url("http://127.0.0.1:8990/")
        self.assertTrue(ok)

        bad, msg = validate_url("not-a-url")
        self.assertFalse(bad)

    def test_programmatic_crawl(self):
        result = crawl_website(
            f"http://127.0.0.1:{TEST_PORT}/",
            max_depth=2,
            max_pages=10,
            delay=0.01,
            concurrency=2,
            respect_robots=False,
            discover_sitemaps=False,
        )

        self.assertEqual(result.get("status"), "completed")
        self.assertIn("pages", result)
        self.assertIn("links", result)
        self.assertIn("issues", result)
        self.assertIn("summary", result)
        self.assertTrue(len(result["pages"]) >= 2)

        # Verify page normalized schema
        home_page = next((p for p in result["pages"] if p["url"].endswith("/")), None)
        self.assertIsNotNone(home_page)
        self.assertEqual(home_page["status_code"], 200)
        self.assertEqual(home_page["h1"], "Welcome to Example Corp")
        self.assertEqual(home_page["title"], "Example Corp - Leading Innovation")

    def test_cli_execution_and_exit_code(self):
        output_file = os.path.join(root_dir, "test_output.json")
        if os.path.exists(output_file):
            os.remove(output_file)

        # 1. Successful CLI crawl
        cmd = [
            sys.executable,
            "-m",
            "LibreCrawl",
            "--url",
            f"http://127.0.0.1:{TEST_PORT}/",
            "--depth",
            "2",
            "--max-pages",
            "5",
            "--output",
            output_file,
            "--no-respect-robots",
            "--no-discover-sitemaps",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=root_dir)
        self.assertEqual(proc.returncode, 0, f"CLI stderr: {proc.stderr}")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data.get("status"), "completed")
            self.assertTrue(len(data.get("pages", [])) >= 2)

        if os.path.exists(output_file):
            os.remove(output_file)

        # 2. Invalid URL CLI exit code (Must be 2)
        bad_cmd = [
            sys.executable,
            "-m",
            "LibreCrawl",
            "--url",
            "ftp://invalid-url",
            "--json",
        ]
        bad_proc = subprocess.run(bad_cmd, capture_output=True, text=True, cwd=root_dir)
        self.assertEqual(bad_proc.returncode, 2)
        err_data = json.loads(bad_proc.stdout)
        self.assertEqual(err_data.get("status"), "failed")
        self.assertEqual(err_data.get("error", {}).get("code"), "INVALID_URL")

    def test_seo_agent_end_to_end(self):
        audit_state = run_seo_audit(
            f"http://127.0.0.1:{TEST_PORT}/",
            crawl_options={
                "max_depth": 2,
                "max_pages": 5,
                "respect_robots": False,
                "discover_sitemaps": False,
                "delay": 0.01,
            },
        )

        self.assertEqual(audit_state.get("status"), "completed")
        self.assertIn("overall_seo_score", audit_state)
        self.assertIn("technical_audit", audit_state)
        self.assertIn("onpage_audit", audit_state)
        self.assertIn("priority_action_items", audit_state)
        self.assertIn("detailed_report_markdown", audit_state)
        self.assertTrue(len(audit_state.get("priority_action_items", [])) > 0)


if __name__ == "__main__":
    unittest.main()
