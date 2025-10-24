def format_markdown(source_name, items, translated):
    lines = [f"### {source_name}"]
    for i, (item, cn_title) in enumerate(zip(items, translated), 1):
        # [text](url)
        line = f'{i}. [{item["title"]}]({item["url"]})'
        if 'created_at' in item:
            line += f" ({item['created_at']})"
        line += f"\n> {cn_title}"  # display translated title as blockquote
        lines.append(line)

    return "\n".join(lines)
