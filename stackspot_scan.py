import os
import json
import requests

CLIENT_ID = os.getenv("STACKSPOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("STACKSPOT_CLIENT_SECRET")
REALM = os.getenv("STACKSPOT_REALM", "stackspot-freemium")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("STACKSPOT_CLIENT_ID e STACKSPOT_CLIENT_SECRET precisam estar definidos.")

# 1) autenticar
auth_url = f"https://idm.stackspot.com/{REALM}/oidc/oauth/token"

auth_response = requests.post(
    auth_url,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
    timeout=60,
)

auth_response.raise_for_status()
jwt = auth_response.json()["access_token"]

# 2) juntar código do projeto
code_parts = []

for root, dirs, files in os.walk("."):
    # ignorar diretórios desnecessários
    dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", ".venv", "node_modules"]]

    for file in files:
        if file.endswith(".py") or file.endswith(".java") or file.endswith(".yaml") or file.endswith(".yml"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                code_parts.append(f"\n### FILE: {path}\n{content}")
            except Exception as e:
                code_parts.append(f"\n### FILE: {path}\n[erro ao ler arquivo: {e}]")

project_code = "\n".join(code_parts)

# 3) montar prompt
prompt = f"""
Você é um especialista em segurança de aplicações e DevSecOps.

Analise o código abaixo e gere um relatório de segurança em português com esta estrutura:

1. Resumo executivo
2. Vulnerabilidades encontradas
3. Severidade de cada vulnerabilidade
4. Arquivo afetado
5. Explicação do risco
6. Sugestão de correção
7. Exemplo de correção quando possível

Considere especialmente:
- SQL Injection
- credenciais hardcoded
- senhas em texto claro
- autenticação insegura
- más práticas em Java e Python
- problemas de configuração em arquivos YAML

Código do projeto:
{project_code}
"""

# 4) chamar o agente oficial
agent_url = "https://genai-inference-app.stackspot.com/v1/agent/01KK5J9CFDZ9BP92YYHTC71Q8G/chat"

payload = {
    "streaming": False,
    "user_prompt": prompt,
    "stackspot_knowledge": False,
    "return_ks_in_response": True,
    "deep_search_ks": False
}

response = requests.post(
    agent_url,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}",
    },
    json=payload,
    timeout=180,
)

response.raise_for_status()

result = response.json()

print("\n===== STACKSPOT AI SECURITY REPORT =====\n")
print(json.dumps(result, indent=2, ensure_ascii=False))