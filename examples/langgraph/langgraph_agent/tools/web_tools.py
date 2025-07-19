"""
Web access tools for the LangGraph Agent System
Adapted to use LangChain's @tool decorator for compatibility with LangGraph
"""

import requests
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any
from langchain_core.tools import tool


@tool
def web_search_tool(query: str, num_results: int = 5) -> str:
    """
    Search the web for information (simulated - would integrate with real search API).
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        Search results summary
    """
    try:
        # This is a placeholder for actual web search implementation
        # In production, you would integrate with Google Custom Search API, 
        # Bing Search API, or similar service
        
        # For demonstration, return a formatted response
        return f"""
Web Search Results for: "{query}"
Note: This is a demonstration implementation. In production, integrate with:
- Google Custom Search API
- Bing Search API  
- DuckDuckGo API
- Or other search service

To implement real web search:
1. Sign up for a search API service
2. Get API credentials
3. Replace this function with actual API calls
4. Parse and return real search results

Search query: {query}
Requested results: {num_results}
Status: Demo mode - replace with real implementation
"""
    
    except Exception as e:
        return f"Error performing web search: {str(e)}"


@tool
def read_url_tool(url: str, timeout: int = 30) -> str:
    """
    Read content from a URL.
    
    Args:
        url: URL to read from
        timeout: Request timeout in seconds
        
    Returns:
        URL content or error message
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return f"Error: Invalid URL format: '{url}'"
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Get content type
        content_type = response.headers.get('content-type', '').lower()
        
        # Handle different content types
        if 'text/html' in content_type:
            # For HTML, extract text content (basic parsing)
            content = response.text
            
            # Remove script and style elements
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', '', content)
            
            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Limit content length for output
            if len(content) > 5000:
                content = content[:5000] + "... [Content truncated]"
            
            return f"Successfully read from URL: {url}\nContent-Type: {content_type}\n\nContent:\n{content}"
        
        elif 'application/json' in content_type:
            return f"Successfully read JSON from URL: {url}\n\nContent:\n{response.text}"
        
        elif 'text/' in content_type:
            content = response.text
            if len(content) > 5000:
                content = content[:5000] + "... [Content truncated]"
            return f"Successfully read text from URL: {url}\nContent-Type: {content_type}\n\nContent:\n{content}"
        
        else:
            return f"Successfully accessed URL: {url}\nContent-Type: {content_type}\nContent-Length: {len(response.content)} bytes\nNote: Binary content not displayed"
    
    except requests.exceptions.Timeout:
        return f"Error: Request to '{url}' timed out after {timeout} seconds"
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to '{url}'"
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP error {e.response.status_code} when accessing '{url}'"
    except requests.exceptions.RequestException as e:
        return f"Error: Request failed for '{url}': {str(e)}"
    except Exception as e:
        return f"Error reading URL '{url}': {str(e)}"


@tool
def download_file_tool(url: str, local_path: str, timeout: int = 60) -> str:
    """
    Download a file from URL to local path.
    
    Args:
        url: URL to download from
        local_path: Local path to save the file
        timeout: Download timeout in seconds
        
    Returns:
        Download status
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return f"Error: Invalid URL format: '{url}'"
        
        # Set headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Make request with streaming
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Get file size if available
        file_size = response.headers.get('content-length')
        if file_size:
            file_size = int(file_size)
            file_size_mb = file_size / (1024 * 1024)
            
            # Safety check for large files
            if file_size_mb > 100:  # 100MB limit
                return f"Error: File too large ({file_size_mb:.1f} MB). Maximum allowed: 100 MB"
        
        # Create directory if it doesn't exist
        from pathlib import Path
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        downloaded_bytes = 0
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_bytes += len(chunk)
        
        # Format file size
        if downloaded_bytes > 1024 * 1024:
            size_str = f"{downloaded_bytes / (1024 * 1024):.1f} MB"
        elif downloaded_bytes > 1024:
            size_str = f"{downloaded_bytes / 1024:.1f} KB"
        else:
            size_str = f"{downloaded_bytes} bytes"
        
        return f"Successfully downloaded file from '{url}' to '{local_path}'\nSize: {size_str}"
    
    except requests.exceptions.Timeout:
        return f"Error: Download from '{url}' timed out after {timeout} seconds"
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to '{url}'"
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP error {e.response.status_code} when downloading from '{url}'"
    except PermissionError:
        return f"Error: Permission denied to write file '{local_path}'"
    except Exception as e:
        return f"Error downloading file from '{url}': {str(e)}" 