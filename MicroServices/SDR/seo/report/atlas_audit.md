# SEO Audit Report: https://www.atlaskliniek.nl/en/dentist-amsterdam/

**Overall Health Score**: `72/100`  
**Pages Crawled**: 112  
**Links Analyzed**: 4895  
**Crawl Duration**: 297.92s  

---

## Category Scores

| Category | Score | Status |
| :--- | :---: | :---: |
| Technical SEO | 86/100 | PASSED |
| On-Page SEO | 43/100 | FAILED |
| Content Quality | 80/100 | WARNING |
| Performance | 70/100 | WARNING |
| Structured Data | 90/100 | PASSED |
| Local SEO | 100/100 | PASSED |

---

## Top Priority Action Items

### 1. [Performance] Severe Server Response Delay (> 1.5s) (Priority 1)
- **Action**: Optimize database queries, enable server-side caching (Redis/Varnish), and use a CDN.
- **Estimated Effort**: `Medium` | **Impact Score**: `10/10` | **Affected Pages**: `10`

### 2. [On-Page] Missing H1 Headings (Priority 2)
- **Action**: Ensure every page has exactly one descriptive `<h1>` matching the page intent.
- **Estimated Effort**: `Medium` | **Impact Score**: `8/10` | **Affected Pages**: `4`

### 3. [Content] Duplicate Page Titles Detected (Priority 2)
- **Action**: Assign distinct, specific titles reflecting the unique value proposition of each URL.
- **Estimated Effort**: `Medium` | **Impact Score**: `8/10` | **Affected Pages**: `10`

### 4. [Technical] Missing Canonical Tags (Priority 3)
- **Action**: Add a self-referential `<link rel='canonical' href='...' />` tag in the `<head>` of each page.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `2`

### 5. [Technical] No XML Sitemap Discovered (Priority 3)
- **Action**: Generate an XML sitemap, place it in the root directory, and specify its URL in robots.txt.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `0`

### 6. [On-Page] Title Tags Truncated in SERP (>60 chars) (Priority 3)
- **Action**: Trim title tags to 50-60 characters and move primary keywords to the beginning.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `10`

### 7. [On-Page] Missing Meta Descriptions (Priority 3)
- **Action**: Write unique, persuasive meta descriptions (120-160 characters) with a clear call to action.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `9`

### 8. [On-Page] Images Missing Alt Text (Priority 3)
- **Action**: Add meaningful `alt='...'` descriptions to all informational images.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `10`

### 9. [Schema] Missing Brand / Organization Schema (Priority 4)
- **Action**: Add Organization schema on the homepage detailing company name, logo, social profiles, and contact points.
- **Estimated Effort**: `Low` | **Impact Score**: `4/10` | **Affected Pages**: `5`

### 10. [Technical] Noindex Directives Present (Priority 5)
- **Action**: Verify that no crucial landing pages or revenue-generating content are blocked by noindex tags.
- **Estimated Effort**: `Low` | **Impact Score**: `2/10` | **Affected Pages**: `2`

