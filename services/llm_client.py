import os, requests

class LLMClient:
    """OpenAI-compatible client for Volcengine Ark / Doubao / Qwen."""
    """
    __init__ 初始化方法：
    - base_url：大模型服务的基础地址。
      默认从环境变量 LLM_BASE_URL 读，如果没有，就用火山方舟的 v3 API。
      注意去掉结尾的 /。
    - api_key：认证用的 API key，从环境变量 LLM_API_KEY 读。
    - model：指定要用的模型，在火山 Ark 是接入点 ID（ep-xxxxxx）。
    - timeout：请求超时时间，默认 60 秒。
    """
    def __init__(self, base_url=None, api_key=None, model=None, timeout=60):
        # 正确 base_url：不要带 /v1，也不要再拼 /chat/completions
        self.base_url = (base_url or os.getenv("LLM_BASE_URL")
                         or "https://ark.cn-beijing.volces.com/api/v3").rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        # Ark 的 model 通常是接入点ID，形如 ep-xxxxxxxx
        self.model = model or os.getenv("LLM_MODEL", "ep-xxxxxxxx")
        self.timeout = timeout
    """
    ask 方法：
    - prompt：用户的问题或指令。
    - system：系统角色，默认是校友管理系统的助手。
    - temperature：温度参数，控制生成的随机性，默认 0.3。
    """
    def ask(self, prompt, system="你是校友管理系统的小助手。", temperature=0.3):
        if not self.base_url or not self.api_key:
            raise RuntimeError("LLM_BASE_URL / LLM_API_KEY 未配置")

        url = f"{self.base_url}/chat/completions"   # ← 正确路径
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            # 关键：禁用 gzip/deflate 协商，避免错误解压
            "Accept-Encoding": "identity",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,  # ep-...（方舟接入点ID）
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "stream": False,
        }

        r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
