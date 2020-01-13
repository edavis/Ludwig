def build_heading(block, adjustment=None):
    (block_idx, block_attrs, block_content) = block['c']
    (block_name, block_args, block_kwargs) = block_attrs

    if adjustment is None:
        return '<h%s>%s</h%s>' % (block_idx, build_string(block_content), block_idx)
    else:
        level = block_idx + adjustment
        return '<h%d>%s</h%d>' % (level, build_string(block_content), level)

def build_paragraph(block):
    return '<p>' + build_string(block['c'])

def build_code_block(block):
    args, content = block['c'] # TODO(ejd): include language args
    return '<pre><code>%s</code></pre>' % content

def build_string(sequence):
    rv = []

    for seq in sequence:
        content_type = seq['t']

        if content_type == 'Str':
            rv.append(seq['c'])
        elif content_type == 'Space':
            rv.append(' ')
        elif content_type == 'Code':
            (_, c) = seq['c']
            rv.append(r'<code>%s</code>' % c)

    return ''.join(rv)
