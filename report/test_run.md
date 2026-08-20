# SEO Audit Report: https://httpbin.org/html

**Overall Health Score**: `88/100`  
**Pages Crawled**: 1  
**Links Analyzed**: 0  
**Crawl Duration**: 2.41s  

---

## Category Scores

| Category | Score | Status |
| :--- | :---: | :---: |
| Technical SEO | 75/100 | WARNING |
| On-Page SEO | 100/100 | PASSED |
| Content Quality | 100/100 | PASSED |
| Performance | 90/100 | PASSED |
| Structured Data | 75/100 | WARNING |
| Local SEO | 100/100 | PASSED |

---

## Top Priority Action Items

### 1. [Technical] 5xx Server Errors Detected (Priority 1)
- **Action**: Investigate web server error logs, database connections, and application crashes immediately.
- **Estimated Effort**: `Medium` | **Impact Score**: `10/10` | **Affected Pages**: `1`

### 2. [Performance] Severe Server Response Delay (> 1.5s) (Priority 1)
- **Action**: Optimize database queries, enable server-side caching (Redis/Varnish), and use a CDN.
- **Estimated Effort**: `Medium` | **Impact Score**: `10/10` | **Affected Pages**: `1`

### 3. [Technical] No XML Sitemap Discovered (Priority 3)
- **Action**: Generate an XML sitemap, place it in the root directory, and specify its URL in robots.txt.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `0`

### 4. [Schema] No Structured Data (Schema.org) Detected (Priority 3)
- **Action**: Implement JSON-LD structured data (e.g. Organization, WebSite, BreadcrumbList) in the `<head>`.
- **Estimated Effort**: `Low` | **Impact Score**: `6/10` | **Affected Pages**: `0`

### 5. [Local] LocalBusiness Schema Not Detected (Priority 5)
- **Action**: If this is a physical business or local service, implement LocalBusiness schema with address and telephone.
- **Estimated Effort**: `Low` | **Impact Score**: `2/10` | **Affected Pages**: `0`

