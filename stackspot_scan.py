import os
import json
import sys
import requests

CLIENT_ID = os.getenv("STACKSPOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("STACKSPOT_CLIENT_SECRET")
REALM = os.getenv("STACKSPOT_REALM", "stackspot-freemium")

# Se existir, reaproveita a mesma conversa
CONVERSATION_ID = os.getenv("STACKSPOT_CONVERSATION_ID")

AGENT_ID = "01KK5J9CFDZ9BP92YYHTC71Q8G"
AUTH_URL = f"https://idm.stackspot.com/{REALM}/oidc/oauth/token"
AGENT_URL = f"https://genai-inference-app.stackspot.com/v1/agent/{AGENT_ID}/chat"

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERRO: STACKSPOT_CLIENT_ID ou STACKSPOT_CLIENT_SECRET não encontrados.")
    sys.exit(1)

print("Autenticando na StackSpot...")

auth_response = requests.post(
    AUTH_URL,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
    timeout=60,
)

print("Status autenticação:", auth_response.status_code)
print("Resposta autenticação:", auth_response.text[:500])

auth_response.raise_for_status()
jwt = auth_response.json()["access_token"]

print("Lendo arquivos do projeto...")

code_parts = []

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", ".venv", "node_modules"]]

    for file in files:
        if file.endswith((".py", ".java", ".yaml", ".yml")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                code_parts.append(f"\n### FILE: {path}\n{content}")
            except Exception as e:
                code_parts.append(f"\n### FILE: {path}\n[erro ao ler arquivo: {e}]")

project_code = "\n".join(code_parts)

prompt = f"""
Você é um especialista em segurança de aplicações e DevSecOps.

Analise o código abaixo e gere um relatório em português com:
1. Resumo executivo
2. Vulnerabilidades encontradas
3. Severidade
4. Arquivo afetado
5. Explicação do risco
6. Sugestão de correção

Código:
{project_code}
"""

payload = {
    "streaming": False,
    "user_prompt": prompt,
    "use_conversation": True,
    "stackspot_knowledge": False,
    "return_ks_in_response": True,
    "deep_search_ks": False,
}

if CONVERSATION_ID:
    payload["conversation_id"] = CONVERSATION_ID
    print("Usando conversation_id existente:", CONVERSATION_ID)
else:
    print("Nenhum conversation_id informado. A API deve criar um novo.")

print("Chamando agente CodeGuard...")

response = requests.post(
    AGENT_URL,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}",
    },
    json=payload,
    timeout=180,
)

print("Status agente:", response.status_code)
print("Resposta bruta agente:", response.text[:4000])

response.raise_for_status()

result = response.json()

print("\n===== RESPOSTA COMPLETA =====\n")
print(json.dumps(result, indent=2, ensure_ascii=False))

# tenta capturar o conversation_id retornado
conversation_id = (
    result.get("conversation_id")
    or result.get("conversationId")
    or result.get("metadata", {}).get("conversation_id")
    or result.get("metadata", {}).get("conversationId")
)

if conversation_id:
    print("\n===== CONVERSATION ID =====")
    print(conversation_id)

    with open("conversation_id.txt", "w", encoding="utf-8") as f:
        f.write(conversation_id)

report_text = json.dumps(result, indent=2, ensure_ascii=False)

with open("security_report.json", "w", encoding="utf-8") as f:
    f.write(report_text)