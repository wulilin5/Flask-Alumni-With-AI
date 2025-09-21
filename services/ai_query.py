# services/ai_query.py
import json
from .llm_client import LLMClient   # ← 这里改成 .llm_client

_PROMPT = """把下面的中文查询扩写为若干相关关键词，输出 JSON 数组，例如：
["分布式存储","对象存储","一致性","副本","CAP"]
只输出 JSON，不要解释。
查询：{q}
"""

def ai_expand_query(q: str):
    client = LLMClient()
    try:
        text = client.ask(_PROMPT.format(q=q))
        left, right = text.find("["), text.rfind("]")
        if left != -1 and right != -1 and left < right:
            arr = json.loads(text[left:right+1])
            seen, out = set(), []
            for w in arr:
                w = (w or "").strip()
                if 1 < len(w) <= 12 and w not in seen:
                    seen.add(w); out.append(w)
            return out[:8]
    except Exception:
        pass
    q = (q or "").strip()
    return [q] if q else []
