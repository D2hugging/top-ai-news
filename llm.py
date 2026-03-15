from config import LOCAL_LLM_URL, GOOGLE_API_KEY, CONFIG


def get_llm():
    llm_cfg = CONFIG.get("llm", {})
    if LOCAL_LLM_URL:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            base_url=LOCAL_LLM_URL,
            api_key="not-needed",
            model=llm_cfg.get("local_model", "qwen3-4b"),
            extra_body={"chat_template_kwargs": {"enable_thinking": llm_cfg.get("enable_thinking", False)}},
        )
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=llm_cfg.get("gemini_model", "gemini-2.5-flash"),
        google_api_key=GOOGLE_API_KEY,
    )
