"""
Link Checker - Validate dataset/report links
"""
import requests
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


# Common NISR domains
VALID_DOMAINS = [
    "nisr.rw",
    "statistics.gov.rw",
    "mineduc.gov.rw",
    "minigender.gov.rw",
    "labor.gov.rw",
    "gov.rw"
]


def is_valid_domain(url: str) -> bool:
    """Check if URL has a valid domain."""
    if not url or not url.startswith("http"):
        return False
    
    url_lower = url.lower()
    return any(domain in url_lower for domain in VALID_DOMAINS)


def check_url_accessibility(url: str, timeout: int = 10) -> Tuple[str, bool, str]:
    """
    Check if a URL is accessible.
    
    Returns:
        Tuple of (url, is_accessible, status_message)
    """
    if not url or not url.startswith("http"):
        return url, False, "Invalid URL format"
    
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        if response.status_code == 200:
            return url, True, "OK"
        elif response.status_code == 301:
            return url, True, f"Redirect (Status: {response.status_code})"
        elif response.status_code == 302:
            return url, True, f"Redirect (Status: {response.status_code})"
        elif response.status_code == 404:
            return url, False, f"Not Found (Status: {response.status_code})"
        elif response.status_code == 403:
            return url, False, f"Forbidden (Status: {response.status_code})"
        else:
            return url, False, f"Status: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return url, False, "Connection timeout"
    except requests.exceptions.ConnectionError:
        return url, False, "Connection error"
    except requests.exceptions.RequestException as e:
        return url, False, f"Request failed: {str(e)}"


def check_urls_batch(urls: List[str], max_workers: int = 5) -> List[Dict]:
    """
    Check multiple URLs in parallel.
    
    Returns:
        List of dictionaries with URL check results
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(check_url_accessibility, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url, is_accessible, status = future.result()
            results.append({
                "url": url,
                "accessible": is_accessible,
                "status": status
            })
    
    return results


def validate_resource_links(resources_df) -> Dict[str, List]:
    """
    Validate all links in resources dataframe.
    
    Returns:
        Dictionary with valid and invalid links
    """
    if resources_df.empty or "url" not in resources_df.columns:
        return {"valid": [], "invalid": [], "unchecked": []}
    
    urls = resources_df["url"].dropna().unique().tolist()
    
    if not urls:
        return {"valid": [], "invalid": [], "unchecked": []}
    
    results = check_urls_batch(urls)
    
    valid = [r for r in results if r["accessible"]]
    invalid = [r for r in results if not r["accessible"]]
    
    return {
        "valid": valid,
        "invalid": invalid,
        "total_checked": len(results)
    }


def get_link_validation_summary(resources_df) -> str:
    """Get a summary string of link validation results."""
    validation = validate_resource_links(resources_df)
    
    total = validation["total_checked"]
    valid_count = len(validation["valid"])
    invalid_count = len(validation["invalid"])
    
    if total == 0:
        return "No URLs to validate"
    
    summary = f"Validated {total} URLs:\n"
    summary += f"- Valid: {valid_count}\n"
    summary += f"- Invalid: {invalid_count}\n"
    
    if invalid_count > 0:
        summary += "\nInvalid URLs:\n"
        for item in validation["invalid"]:
            summary += f"- {item['url']}: {item['status']}\n"
    
    return summary
