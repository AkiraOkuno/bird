import requests

def fetch_quote():
    try:
        res = requests.get("https://zenquotes.io/api/random")
        if res.status_code != 200:
            print(f"[QUOTE] Failed to fetch: {res.status_code}", flush=True)
            return None

        data = res.json()[0]
        quote = data.get("q")
        author = data.get("a", "Desconhecido")
        return f"💬 *Random daily quote:*\n_{quote}_\n— *{author}*"
    except Exception as e:
        print(f"[QUOTE] Exception: {e}", flush=True)
        return None

def generate():
    return fetch_quote() or "⚠️ Não foi possível obter uma citação hoje."
