import requests
from urllib.parse import urljoin

def trace_url(url):
    chain = []
    current_url = url
    session = requests.Session()
    # Masking as a browser prevents sites from blocking your tool
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    # Limit to 10 hops to prevent getting stuck in infinite redirect loops
    for hop in range(10): 
        try:
            # allow_redirects=False is the key: it stops at the first hop so we can record it
            response = session.get(current_url, allow_redirects=False, timeout=10)
            
            chain.append({
                "hop": hop + 1,
                "url": current_url,
                "status": response.status_code
            })

            # If it's a 3xx status, there is a "Location" header pointing to the next page
            if 300 <= response.status_code < 400:
                next_url = response.headers.get('Location')
                if not next_url:
                    break
                # Handle relative paths (e.g., /home) by joining them with the base URL
                current_url = urljoin(current_url, next_url)
            else:
                # We hit a 200, 404, or 500—this is the end of the line
                break
        except Exception as e:
            return chain, f"Error: {str(e)}"
    
    return chain, chain[-1]['status']