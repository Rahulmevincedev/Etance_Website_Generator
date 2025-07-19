from langchain_core.tools import tool
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
from typing import Union
import re

@tool
def replace_html_content(file_path: str, selector: str, new_content: str) -> str:
    """
    Surgically replaces the content of an HTML element identified by a CSS selector.
    This is highly reliable for editing specific parts of a webpage template.
    
    Args:
        file_path (str): The path to the HTML file to edit.
        selector (str): The CSS selector to find the target element (e.g., 'h1.title', 'p#email', '.navbar-brand').
        new_content (str): The new inner HTML or text to place inside the element.
    
    Returns:
        str: Success/failure message with details.
    """
    try:
        html_path = Path(file_path)
        if not html_path.is_file():
            return f"Error: File not found at {file_path}"

        # Read and parse the file
        content = html_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(content, 'html.parser')

        # Find the target element
        element = soup.select_one(selector)

        if element:
            # Replace the element's content
            element.clear()
            element.append(NavigableString(new_content))
            
            # Write the modified HTML back to the file
            html_path.write_text(str(soup), encoding='utf-8')
            return f"Success: Replaced content for selector '{selector}' in {file_path} with: '{new_content}'"
        else:
            # Try to find similar elements for debugging
            all_elements = soup.select('*')
            similar_selectors = []
            for elem in all_elements[:10]:  # Check first 10 elements
                if elem.name and (elem.get('class') or elem.get('id')):
                    if elem.get('class'):
                        similar_selectors.append(f"{elem.name}.{' '.join(elem.get('class'))}")
                    if elem.get('id'):
                        similar_selectors.append(f"{elem.name}#{elem.get('id')}")
            
            suggestion = f" Similar selectors found: {', '.join(similar_selectors[:5])}" if similar_selectors else ""
            return f"Error: Could not find any element matching the selector '{selector}' in {file_path}.{suggestion}"

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

@tool
def replace_html_attribute(file_path: str, selector: str, attribute: str, new_value: str) -> str:
    """
    Replaces an attribute value of an HTML element identified by a CSS selector.
    Useful for updating href links, src attributes, etc.
    
    Args:
        file_path (str): The path to the HTML file to edit.
        selector (str): The CSS selector to find the target element.
        attribute (str): The attribute name to update (e.g., 'href', 'src', 'class').
        new_value (str): The new value for the attribute.
    
    Returns:
        str: Success/failure message with details.
    """
    try:
        html_path = Path(file_path)
        if not html_path.is_file():
            return f"Error: File not found at {file_path}"

        # Read and parse the file
        content = html_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(content, 'html.parser')

        # Find the target element
        element = soup.select_one(selector)

        if element:
            # Update the attribute
            element[attribute] = new_value
            
            # Write the modified HTML back to the file
            html_path.write_text(str(soup), encoding='utf-8')
            return f"Success: Updated {attribute}='{new_value}' for selector '{selector}' in {file_path}"
        else:
            return f"Error: Could not find any element matching the selector '{selector}' in {file_path}"

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

@tool
def find_html_elements(file_path: str, search_text: str = "") -> str:
    """
    Finds HTML elements containing specific text or lists all major elements.
    Useful for discovering the correct CSS selectors to use.
    
    Args:
        file_path (str): The path to the HTML file to analyze.
        search_text (str): Optional text to search for within elements.
    
    Returns:
        str: List of found elements with their selectors and content.
    """
    try:
        html_path = Path(file_path)
        if not html_path.is_file():
            return f"Error: File not found at {file_path}"

        # Read and parse the file
        content = html_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(content, 'html.parser')

        results = []
        
        if search_text:
            # Search for elements containing the text
            elements = soup.find_all(string=re.compile(search_text, re.I))
            for elem in elements:
                parent = elem.parent
                if parent and parent.name:
                    selector = parent.name
                    if parent.get('class'):
                        selector += f".{' '.join(parent.get('class'))}"
                    if parent.get('id'):
                        selector += f"#{parent.get('id')}"
                    
                    results.append(f"Selector: '{selector}' - Content: '{str(elem).strip()[:100]}...'")
        else:
            # List major structural elements
            major_elements = soup.select('h1, h2, h3, h4, h5, h6, .title, .brand, .navbar-brand, .header, .footer, #brand, #title')
            for elem in major_elements[:20]:  # Limit to first 20
                selector = elem.name
                if elem.get('class'):
                    selector += f".{' '.join(elem.get('class'))}"
                if elem.get('id'):
                    selector += f"#{elem.get('id')}"
                
                text_content = elem.get_text().strip()[:50]
                results.append(f"Selector: '{selector}' - Content: '{text_content}...'")

        if results:
            return f"Found elements in {file_path}:\n" + "\n".join(results[:15])
        else:
            return f"No elements found in {file_path}" + (f" containing '{search_text}'" if search_text else "")

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

HTML_TOOLS = [replace_html_content, replace_html_attribute, find_html_elements] 