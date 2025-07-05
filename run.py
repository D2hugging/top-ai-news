from graph_runner import build_graph

if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke({})
    print("\n🎯 最终 Markdown 输出:\n")
    print(result["markdown"])
