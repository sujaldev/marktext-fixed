from mistune import markdown as parse_markdown_to_html_string
from html5_parser import parse as html_string_to_tree


def parse(markdown):
    html_string = parse_markdown_to_html_string(markdown)
    lxml_tree = html_string_to_tree(html_string)
    return lxml_tree


def parse_file(file_name):
    with open(file_name) as file:
        markdown = file.read()
        return parse(markdown)
