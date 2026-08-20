# SEO Audit Report: https://httpbin.org/html

**Overall Health Score**: `87/100`  
**Pages Crawled**: 1  
**Links Analyzed**: 0  
**Crawl Duration**: 4.01s  

---

## Category Scores

| Category | Score | Status |
| :--- | :---: | :---: |
| Technical SEO | 88/100 | PASSED |
| On-Page SEO | 77/100 | WARNING |
| Content Quality | 100/100 | PASSED |
| Performance | 90/100 | PASSED |
| Structured Data | 75/100 | WARNING |
| Local SEO | 100/100 | PASSED |

---

## Top Priority Action Items

### 1. [On-Page] Missing Title Tags (Priority 1)
- **Action**: Provide unique, compelling title tags between 50-60 characters for all pages.
- **Estimated Effort**: `Medium` | **Impact Score**: `10/10` | **Affected Pages**: `1`

### 2. [Performance] Severe Server Response Delay (> 1.5s) (Priority 1)
- **Action**: Optimize database queries, enable server-side caching (Redis/Varnish), and use a CDN.
- **Estimated Effort**: `Medium` | **Impact Score**: `10/10` | **Affected Pages**: `1`

### 3. [Technical] Missing Canonical Tags (Priority 3)
- **Action**: Add a self-referential `<link rel='canonical' href='...' />` tag in the `<head>` of each page.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `1`

### 4. [Technical] No XML Sitemap Discovered (Priority 3)
- **Action**: Generate an XML sitemap, place it in the root directory, and specify its URL in robots.txt.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `0`

### 5. [On-Page] Missing Meta Descriptions (Priority 3)
- **Action**: Write unique, persuasive meta descriptions (120-160 characters) with a clear call to action.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `1`

### 6. [Schema] No Structured Data (Schema.org) Detected (Priority 3)
- **Action**: Implement JSON-LD structured data (e.g. Organization, WebSite, BreadcrumbList) in the `<head>`.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `1`

### 7. [On-Page] Missing OpenGraph Metadata (Priority 4)
- **Action**: Implement OpenGraph meta tags on all public landing pages and articles.
- **Estimated Effort**: `Low` | **Impact Score**: `4/10` | **Affected Pages**: `1`

### 8. [Local] LocalBusiness Schema Not Detected (Priority 5)
- **Action**: If this is a physical business or local service, implement LocalBusiness schema with address and telephone.
- **Estimated Effort**: `Low` | **Impact Score**: `2/10` | **Affected Pages**: `1`

