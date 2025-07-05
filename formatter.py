def format_markdown(source_name, items, translated):
    lines = [f"### {source_name}"]
    for item, cn_title in zip(items, translated):
        lines.append(f"- [{cn_title}]({item['url']})")
    return "\n".join(lines)
