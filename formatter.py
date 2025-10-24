def format_markdown(source_name, items, translated):
    lines = [f"### {source_name}"]
    for item, cn_title in zip(items, translated):
        line = f'- <a href="{item["url"]}" target="_blank">{item["title"]}</a>'
        if 'created_at' in item:
            line += f"  (news from {item['created_at']})"
        line += f"<br/>  {cn_title}"
        lines.append(line)
    return "\n".join(lines)