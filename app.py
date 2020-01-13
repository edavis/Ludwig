import json
import base64
import pandoc # pip install pyandoc
from flask import Flask, request # pip install flask
from builders import *

app = Flask(__name__)

def find_node_index(ast, location):
    """
    Given a URL, return the index of the Header in the blocks list.
    """
    parts = location.split('/')
    blocks = iter(ast['blocks'])
    found = False

    for index, block in enumerate(blocks):
        block_type = block['t']
        if block_type != 'Header': continue

        (block_idx, block_attrs, block_content) = block['c']
        (block_name, block_args, block_kwargs) = block_attrs

        if block_idx == 1:
            breadcrumbs = [block_name]

        elif block_idx > len(breadcrumbs):
            breadcrumbs.append(block_name)

        elif block_idx == len(breadcrumbs):
            breadcrumbs[-1] = block_name

        elif block_idx < len(breadcrumbs):
            del breadcrumbs[block_idx - 1:]
            breadcrumbs.append(block_name)

        if breadcrumbs == parts:
            found = True
            break

    if not found:
        return None

    return index

def build_node_content(ast, index):
    """
    Process blocks starting at index, building HTML.
    """
    html = []
    blocks = ast['blocks']

    start_block = blocks[index]
    start_block_idx = start_block['c'][0]

    # the adjustment needed to make whatever level we're on a h1
    # which is also applied to all children header nodes
    html_heading_adjustment = 1 - start_block_idx

    # add the start block as a header
    html.append(build_heading(start_block, html_heading_adjustment))

    for block in blocks[index + 1:]:
        block_type = block['t']
        block_content = ''

        if block_type == 'Header':
            (block_idx, block_attrs, block_content) = block['c']
            (block_name, block_args, block_kwargs) = block_attrs

            # stop once we hit a header above where we started
            if block_idx <= start_block_idx:
                break
            else:
                html.append(build_heading(block, html_heading_adjustment))

        elif block_type == 'Para':
            html.append(build_paragraph(block))

        elif block_type == 'CodeBlock':
            html.append(build_code_block(block))

    return ''.join(html)

def build_index(ast):
    """
    Render the entire file. Used if there is no _index node.
    """
    html = []

    blocks = ast['blocks']
    for block in blocks:
        block_type = block['t']

        if block_type == 'Header':
            html.append(build_heading(block))
        elif block_type == 'Para':
            html.append(build_paragraph(block))

    return ''.join(html)

@app.route('/<path:location>/')
def main(location):
    doc = pandoc.Document()
    doc.org = open('states.org').read()
    json_obj = json.loads(doc.json)

    index = find_node_index(json_obj, location)
    if index is None:
        return ('HTTP 404 -- Could not find any node at that location.', 404)

    return build_node_content(json_obj, index)

@app.route('/')
def index():
    doc = pandoc.Document()
    doc.org = open('states.org').read()
    json_obj = json.loads(doc.json)

    # Use _index, if possible
    index = find_node_index(json_obj, '_index')
    if index is not None:
        return build_node_content(json_obj, index)

    return build_index(json_obj)

@app.route('/dump')
def dump():
    doc = pandoc.Document()
    doc.org = open('states.org').read()
    json_obj = json.loads(doc.json)
    return (json_obj, {'Content-Type': 'application/json'})

@app.route('/favicon.ico')
def favicon():
    icon = 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQEAYAAABPYyMiAAAABmJLR0T///////8JWPfcAAAACXBIWXMAAABIAAAASABGyWs+AAAAF0lEQVRIx2NgGAWjYBSMglEwCkbBSAcACBAAAeaR9cIAAAAASUVORK5CYII='
    return (base64.b64decode(icon), {'Content-Type': 'image/x-icon'})
