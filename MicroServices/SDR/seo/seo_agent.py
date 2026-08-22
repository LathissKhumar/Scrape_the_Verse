"""
SEO Agent - LangGraph Orchestrator & Node Execution Pipeline
Connects LibreCrawl headless engine with modular SEO domain analyzers.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List

# Ensure workspace root (for LibreCrawl) and WebAuditAgent dir (for seo package) are in sys.path
_seo_dir = os.path.dirname(os.path.abspath(__file__))          # .../WebAuditAgent/seo
_webaudit_dir = os.path.dirname(_seo_dir)                       # .../WebAuditAgent
_workspace_root = os.path.dirname(_webaudit_dir)                # .../Scrape_the_Verse
for _p in (_webaudit_dir, _workspace_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from seo.state import SEOState, ActionItem, CategoryAuditResult, AuditFinding
from seo.tools.crawl import crawl_target_tool
from seo.analyzers.technical import run_technical_audit
from seo.analyzers.onpage import run_onpage_audit
from seo.analyzers.content import run_content_audit
from seo.analyzers.schema import run_schema_audit
from seo.analyzers.local import run_local_audit
from seo.analyzers.performance import run_performance_audit


# -----------------------------------------------------------------------------
# LangGraph Node Handlers
# -----------------------------------------------------------------------------

def crawl_node(state: SEOState) -> SEOState:
    """Executes the headless crawl using LibreCrawl tool."""
    url = state.get('url', '')
    config = state.get('crawl_config', {})
    
    crawl_result = crawl_target_tool(
        url=url,
        max_depth=config.get('max_depth', 3),
        max_pages=config.get('max_pages', 100),
        javascript=config.get('javascript', False),
        pagespeed=config.get('pagespeed', False),
        respect_robots=config.get('respect_robots', True),
        discover_sitemaps=config.get('discover_sitemaps', True),
        crawl_external=config.get('crawl_external', False),
        crawl_images=config.get('crawl_images', False),
        delay=config.get('delay', 0.05),
        concurrency=config.get('concurrency', 5),
        timeout=config.get('timeout', 30)
    )

    if crawl_result.get('status') == 'failed':
        return {
            **state,
            "status": "failed",
            "errors": [crawl_result.get('error', {}).get('message', 'Crawl failed')],
            "raw_crawl_data": crawl_result
        }

    return {
        **state,
        "status": "analyzing",
        "raw_crawl_data": crawl_result,
        "job_id": crawl_result.get('crawl_id', ''),
        "pages": crawl_result.get('pages', []),
        "links": crawl_result.get('links', []),
        "issues": crawl_result.get('issues', []),
        "sitemaps": crawl_result.get('sitemaps', {}),
        "pagespeed": crawl_result.get('pagespeed', []),
        "crawl_summary": crawl_result.get('summary', {})
    }


def technical_audit_node(state: SEOState) -> SEOState:
    """Executes Technical SEO audit."""
    if state.get('status') == 'failed':
        return state
    
    pages = state.get('pages', [])
    links = state.get('links', [])
    issues = state.get('issues', [])
    sitemaps = state.get('sitemaps', {})
    
    result = run_technical_audit(pages, links, issues, sitemaps)
    return {**state, "technical_audit": result}


def onpage_audit_node(state: SEOState) -> SEOState:
    """Executes On-Page SEO audit."""
    if state.get('status') == 'failed':
        return state
    
    pages = state.get('pages', [])
    issues = state.get('issues', [])
    
    result = run_onpage_audit(pages, issues)
    return {**state, "onpage_audit": result}


def content_audit_node(state: SEOState) -> SEOState:
    """Executes Content Quality audit."""
    if state.get('status') == 'failed':
        return state
    
    pages = state.get('pages', [])
    result = run_content_audit(pages)
    return {**state, "content_audit": result}


def schema_audit_node(state: SEOState) -> SEOState:
    """Executes Schema.org structured data audit."""
    if state.get('status') == 'failed':
        return state
    
    pages = state.get('pages', [])
    result = run_schema_audit(pages)
    return {**state, "schema_audit": result}


def local_audit_node(state: SEOState) -> SEOState:
    """Executes Local SEO audit."""
    if state.get('status') == 'failed':
        return state
    
    pages = state.get('pages', [])
    result = run_local_audit(pages)
    return {**state, "local_audit": result}


def performance_audit_node(state: SEOState) -> SEOState:
    """Executes Performance audit."""
    if state.get('status') == 'failed':
        return state
    
    pages = state.get('pages', [])
    pagespeed = state.get('pagespeed', [])
    
    result = run_performance_audit(pages, pagespeed)
    return {**state, "performance_audit": result}


def synthesis_node(state: SEOState) -> SEOState:
    """Aggregates all audit results, calculates scores, and prioritizes action items."""
    if state.get('status') == 'failed':
        return state

    tech = state.get('technical_audit', {})
    onpage = state.get('onpage_audit', {})
    content = state.get('content_audit', {})
    schema = state.get('schema_audit', {})
    local = state.get('local_audit', {})
    perf = state.get('performance_audit', {})

    category_scores = {
        "Technical SEO": tech.get('score', 100),
        "On-Page SEO": onpage.get('score', 100),
        "Content Quality": content.get('score', 100),
        "Performance": perf.get('score', 100),
        "Structured Data": schema.get('score', 100),
        "Local SEO": local.get('score', 100)
    }

    # Calculate weighted overall score
    overall_score = round(
        (category_scores["Technical SEO"] * 0.30) +
        (category_scores["On-Page SEO"] * 0.25) +
        (category_scores["Content Quality"] * 0.20) +
        (category_scores["Performance"] * 0.15) +
        (category_scores["Structured Data"] * 0.10)
    )

    # Gather all findings & build priority action items
    all_findings: List[AuditFinding] = (
        tech.get('findings', []) +
        onpage.get('findings', []) +
        content.get('findings', []) +
        schema.get('findings', []) +
        local.get('findings', []) +
        perf.get('findings', [])
    )

    action_items: List[ActionItem] = []
    for finding in all_findings:
        sev = finding.get('severity', 'medium')
        if sev == 'critical':
            prio = 1
            effort = 'medium'
            impact = 10
        elif sev == 'high':
            prio = 2
            effort = 'medium'
            impact = 8
        elif sev == 'medium':
            prio = 3
            effort = 'low'
            impact = 6
        elif sev == 'low':
            prio = 4
            effort = 'low'
            impact = 4
        else:
            prio = 5
            effort = 'low'
            impact = 2

        action_items.append({
            "priority": prio,
            "category": finding.get('category', 'General'),
            "title": finding.get('title', ''),
            "action": finding.get('recommendation', ''),
            "estimated_effort": effort,
            "impact_score": impact,
            "affected_count": len(finding.get('affected_urls', []))
        })

    action_items.sort(key=lambda x: (x['priority'], -x['impact_score']))

    # Executive Summary Text
    summary_text = (
        f"SEO Audit completed for {state.get('url')} across {len(state.get('pages', []))} crawled pages. "
        f"Overall SEO Health Score: {overall_score}/100. "
        f"Identified {len(all_findings)} key findings with {len([a for a in action_items if a['priority'] <= 2])} high-priority action items."
    )

    # Detailed Markdown Report
    summary_dict = state.get('crawl_summary', {})
    report_md = f"""# SEO Audit Report: {state.get('url')}

**Overall Health Score**: `{overall_score}/100`  
**Pages Crawled**: {summary_dict.get('total_pages_crawled', len(state.get('pages', [])))}  
**Links Analyzed**: {summary_dict.get('total_links', len(state.get('links', [])))}  
**Crawl Duration**: {summary_dict.get('duration_seconds', 0)}s  

---

## Category Scores

| Category | Score | Status |
| :--- | :---: | :---: |
| Technical SEO | {category_scores['Technical SEO']}/100 | {tech.get('status', 'N/A').upper()} |
| On-Page SEO | {category_scores['On-Page SEO']}/100 | {onpage.get('status', 'N/A').upper()} |
| Content Quality | {category_scores['Content Quality']}/100 | {content.get('status', 'N/A').upper()} |
| Performance | {category_scores['Performance']}/100 | {perf.get('status', 'N/A').upper()} |
| Structured Data | {category_scores['Structured Data']}/100 | {schema.get('status', 'N/A').upper()} |
| Local SEO | {category_scores['Local SEO']}/100 | {local.get('status', 'N/A').upper()} |

---

## Top Priority Action Items

"""
    for i, item in enumerate(action_items[:10], 1):
        report_md += f"### {i}. [{item['category']}] {item['title']} (Priority {item['priority']})\n"
        report_md += f"- **Action**: {item['action']}\n"
        report_md += f"- **Estimated Effort**: `{item['estimated_effort'].title()}` | **Impact Score**: `{item['impact_score']}/10` | **Affected Pages**: `{item['affected_count']}`\n\n"

    return {
        **state,
        "status": "completed",
        "overall_seo_score": overall_score,
        "category_scores": category_scores,
        "priority_action_items": action_items,
        "executive_summary": summary_text,
        "detailed_report_markdown": report_md
    }


# -----------------------------------------------------------------------------
# LangGraph Workflow Construction
# -----------------------------------------------------------------------------

def create_seo_agent():
    """
    Constructs and compiles the LangGraph StateGraph.
    Falls back to a direct sequential pipeline executor if langgraph is not installed.
    """
    try:
        from langgraph.graph import StateGraph, END
        
        workflow = StateGraph(SEOState)
        
        # Register Nodes
        workflow.add_node("crawl", crawl_node)
        workflow.add_node("technical_audit", technical_audit_node)
        workflow.add_node("onpage_audit", onpage_audit_node)
        workflow.add_node("content_audit", content_audit_node)
        workflow.add_node("schema_audit", schema_audit_node)
        workflow.add_node("local_audit", local_audit_node)
        workflow.add_node("performance_audit", performance_audit_node)
        workflow.add_node("synthesis", synthesis_node)
        
        # Connect Edges
        workflow.set_entry_point("crawl")
        workflow.add_edge("crawl", "technical_audit")
        workflow.add_edge("technical_audit", "onpage_audit")
        workflow.add_edge("onpage_audit", "content_audit")
        workflow.add_edge("content_audit", "schema_audit")
        workflow.add_edge("schema_audit", "local_audit")
        workflow.add_edge("local_audit", "performance_audit")
        workflow.add_edge("performance_audit", "synthesis")
        workflow.add_edge("synthesis", END)
        
        return workflow.compile()
    
    except ImportError:
        # Fallback executor matching identical LangGraph state pipeline
        class FallbackAgent:
            def invoke(self, state: SEOState) -> SEOState:
                s = crawl_node(state)
                if s.get('status') == 'failed':
                    return s
                s = technical_audit_node(s)
                s = onpage_audit_node(s)
                s = content_audit_node(s)
                s = schema_audit_node(s)
                s = local_audit_node(s)
                s = performance_audit_node(s)
                s = synthesis_node(s)
                return s
        return FallbackAgent()


def run_seo_audit(url: str, crawl_options: Dict[str, Any] = None) -> SEOState:
    """Helper function to execute an end-to-end SEO audit."""
    agent = create_seo_agent()
    initial_state: SEOState = {
        "url": url,
        "crawl_config": crawl_options or {},
        "status": "initialized",
        "errors": []
    }
    return agent.invoke(initial_state)


from seo.exporter import export_to_excel, export_to_json
from seo.organizer import organize_website_crawl, WebsiteDataOrganizer

# -----------------------------------------------------------------------------
# CLI Entry Point for SEO Agent
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SEO Agent - LangGraph Powered SEO Audit Engine")
    parser.add_argument("--url", "-u", required=True, help="Website URL to audit")
    parser.add_argument("--depth", "-d", type=int, default=3, help="Max crawl depth")
    parser.add_argument("--max-pages", "-m", type=int, default=100, help="Max pages to crawl")
    parser.add_argument("--javascript", "--js", action=argparse.BooleanOptionalAction, default=False, help="Enable JavaScript rendering")
    parser.add_argument("--pagespeed", "--ps", action=argparse.BooleanOptionalAction, default=False, help="Enable PageSpeed analysis")
    parser.add_argument("--pagespeed-key", "-k", type=str, help="Google PageSpeed API Key (avoids public rate limits)")
    
    # Export options
    parser.add_argument("--output", "-o", type=str, help="Output file path (.md, .json, or .xlsx)")
    parser.add_argument("--excel", "-x", type=str, help="Export detailed multi-tab Excel file (.xlsx)")
    parser.add_argument("--json-output", "-j", type=str, help="Export complete structured JSON file (.json)")
    parser.add_argument("--export-all", type=str, help="Export all formats (Markdown, JSON, Excel) with the given filename prefix")
    parser.add_argument("--data-dir", default="report", help="Base directory for domain-partitioned normalized data (default: report)")
    parser.add_argument("--no-organize", action="store_true", help="Skip domain directory organization")
    parser.add_argument("--json", action="store_true", help="Output JSON result to stdout")

    args = parser.parse_args()

    options = {
        "max_depth": args.depth,
        "max_pages": args.max_pages,
        "javascript": args.javascript,
        "pagespeed": args.pagespeed,
        "google_api_key": args.pagespeed_key,
        "respect_robots": True,
        "discover_sitemaps": True
    }

    print(f"\n[SEO Agent] Starting automated audit for: {args.url}")
    final_state = run_seo_audit(args.url, options)

    if final_state.get('status') == 'failed':
        print(f"\nAudit failed: {', '.join(final_state.get('errors', []))}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(final_state, indent=2, default=str))
    else:
        print("\n" + final_state.get('detailed_report_markdown', ''))

    # Automatically organize normalized data into domain directory
    if not args.no_organize and final_state.get('status') == 'completed':
        try:
            master_idx = organize_website_crawl(final_state, base_dir=args.data_dir)
            val = master_idx.get("validation", {})
            dom = master_idx.get("domain", "")
            print(f"\n[Data Organizer] Successfully partitioned crawl data under: {os.path.join(args.data_dir, dom)}")
            print(f"  - Pages Normalized: {val.get('normalized_pages_count', 0)}")
            print(f"  - Issues Deduplicated: {val.get('normalized_issues_count', 0)} (removed {val.get('duplicate_issues_deduplicated', 0)} duplicates)")
            print(f"  - Links Analyzed: {val.get('normalized_links_count', 0)}")
            print(f"  - Unique Images: {val.get('unique_images_cataloged', 0)}")
            print(f"  - Master Index: {os.path.join(args.data_dir, dom, 'index.json')}")
            print(f"  - Validation: {'PASSED' if val.get('valid') else 'FAILED'} (Data Loss: {val.get('data_loss')})")
        except Exception as e:
            print(f"\n[Data Organizer] Notice: Could not organize domain folders: {e}", file=sys.stderr)

    # Handle Exports
    # 1. Export All Formats (--export-all prefix)
    if args.export_all:
        prefix = args.export_all.rstrip('._')
        md_path = f"{prefix}.md" if not prefix.endswith('.md') else prefix
        json_path = f"{prefix}.json" if not prefix.endswith('.json') else prefix
        xlsx_path = f"{prefix}.xlsx" if not prefix.endswith('.xlsx') else prefix

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(final_state.get('detailed_report_markdown', ''))
        export_to_json(final_state, json_path)
        export_to_excel(final_state, xlsx_path)

        print(f"\nAll audit reports successfully generated:")
        print(f"  - Markdown Summary: {md_path}")
        print(f"  - Detailed JSON Data: {json_path}")
        print(f"  - Clean Excel Workbook: {xlsx_path}")

    # 2. Individual --output flag
    elif args.output:
        out = args.output
        if out.lower().endswith('.xlsx'):
            export_to_excel(final_state, out)
            print(f"\nExcel workbook saved to: {out}")
        elif out.lower().endswith('.json'):
            export_to_json(final_state, out)
            print(f"\nJSON data saved to: {out}")
        else:
            with open(out, 'w', encoding='utf-8') as f:
                f.write(final_state.get('detailed_report_markdown', ''))
            print(f"\nReport saved to: {out}")

    # 3. Explicit --excel flag
    if args.excel:
        export_to_excel(final_state, args.excel)
        print(f"\nExcel workbook saved to: {args.excel}")

    # 4. Explicit --json-output flag
    if args.json_output:
        export_to_json(final_state, args.json_output)
        print(f"\nJSON data saved to: {args.json_output}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
