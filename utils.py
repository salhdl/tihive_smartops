# utils.py
import time
import json
import re

def pretty(content):
    """Nettoie et affiche du JSON joliment formaté."""
    if not content:
        return "⚠️ No content."
    cleaned = str(content).replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        return json.dumps(parsed, indent=4, ensure_ascii=False)
    except Exception:
        return cleaned


def safe_run(agent, prompt, retries=2):
    """
    Exécute un agent Agno en gérant les erreurs 429 (quota dépassé).
    Attend le délai suggéré avant de relancer.
    """
    for attempt in range(retries):
        try:
            result = agent.run(prompt)
            return getattr(result, "get_content_text", lambda: result.content or "")()
        except Exception as e:
            msg = str(e)
            if "429" in msg:
                match = re.search(r"retryDelay[^0-9]*([0-9]+)", msg)
                delay = int(match.group(1)) if match else 30
                print(f"⚠️ Quota Gemini atteint. Attente de {delay}s avant nouvel essai...")
                time.sleep(delay + 5)
            else:
                raise e
    raise RuntimeError("🚫 Échec après plusieurs tentatives. Vérifie ton quota API Gemini.")
