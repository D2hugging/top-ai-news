def format_markdown(source_name, items, translated):
    lines = [f"### {source_name}"]
    for item, cn_title in zip(items, translated):
        line = f'- <a href="{item["url"]}" target="_blank">{cn_title}</a>'
        if 'created_at' in item:
            line += f"  ({item['created_at']})"
        lines.append(line)
    return "\n".join(lines)