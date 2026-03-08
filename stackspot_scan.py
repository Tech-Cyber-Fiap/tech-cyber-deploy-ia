import os
import requests

CLIENT_ID = os.getenv("STACKSPOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("STACKSPOT_CLIENT_SECRET")

auth = requests.post(
    "https://idm.stackspot.com/stackspot-freemium/oidc/oauth/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
)

auth.raise_for_status()
token = auth.json()["access_token"]

code = ""

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py") or file.endswith(".java"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                code += f.read() + "\n"

prompt = f"""
You are a cybersecurity expert.
Analyze the following source code and generate a security vulnerability report with:
- vulnerability name
- severity
- affected file
- explanation
- recommendation

Code:
{code}
"""

response = requests.post(
    "https://genai-inference-app.stackspot.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "streaming": False,
        "user_prompt": prompt
    }
)

response.raise_for_status()
print(response.json())