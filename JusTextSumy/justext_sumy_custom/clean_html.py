import re
import urllib.request

def fetch_html_content(url):
    response = urllib.request.urlopen(url)
    html_content = response.read().decode('utf-8')
    return html_content


def clean_html_content(html_content):
    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)  # remove the JavaScript code
    html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL)  # remove the CSS code
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)  # remove the HTML comments
    html_content = re.sub(r'<header.*?</header>', '', html_content, flags=re.DOTALL)  # remove the header
    html_content = re.sub(r'<footer.*?</footer>', '', html_content, flags=re.DOTALL)  # remove the footer
    html_content = re.sub(r'<nav.*?</nav>', '', html_content, flags=re.DOTALL)  # remove the navigation bar

    html_content = re.sub(r'<(a|span|em|strong).*?>', r'', html_content)  # remove the HTML tags for links and spans
    html_content = re.sub(r'</(a|span|em|strong)>', r'', html_content)  # remove the HTML tags for links and spans
    html_content = re.sub(r'<.*?>', '\n', html_content, flags=re.DOTALL)  # remove the HTML tags and add a newline
    html_content = re.sub(r'</.*?>', '\n', html_content, flags=re.DOTALL)  # remove the HTML tags and add a newline
    html_content = re.sub(r'(?<=\n)\s+', '', html_content,
                          flags=re.DOTALL)  # remove the extra spaces after each newline
    return html_content


def get_text_content(html_content):
    text_content = re.sub(r'\[[0-9]*\]', ' ', html_content)  # remove the numbers in the square brackets
    text_content = re.sub(r'[^\w\s.,?!@$%&()+{}[\]-]', ' ', text_content)  # remove the special characters
    text_content = text_content.strip()  # remove the leading and trailing spaces
    return text_content


def segment_blocks(text_content):
    blocks = re.split(r'[;\n]+', text_content)  # split the text content into blocks
    return [block.strip() for block in blocks if block.strip()]  # remove the leading and trailing spaces


