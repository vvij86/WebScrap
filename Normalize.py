def normalize_markdown(text):
    lines = [line.strip() for line in text.splitlines()]
    # Remove empty lines
    lines = [line for line in lines if line]
    return '\n'.join(lines)
