import os

file = open("app.py").read()

issues = []

if "SELECT * FROM" in file and "f\"" in file:
    issues.append("Possible SQL Injection vulnerability detected")

if "password" in file and "hash" not in file:
    issues.append("Password may be stored or compared in plain text")

print("\nSecurity Scan Results\n")

if issues:
    for issue in issues:
        print("-", issue)
else:
    print("No vulnerabilities detected")