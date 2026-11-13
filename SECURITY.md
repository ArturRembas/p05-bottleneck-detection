# Security and Data Handling

P05 may analyze operational event logs containing employee, shift, resource, machine or commercial information. Treat input logs and credentials as potentially sensitive until their classification is confirmed.

## Do not commit

- Passwords, tokens, API keys, `.env` files or private keys.
- Non-public industrial event logs without documented permission to redistribute.
- Raw personally identifiable or proprietary records.
- Generated indices/databases and retained AI prompts containing sensitive data.

## Architectural safeguards (to implement and test)

- Validate and constrain uploads; limit file size and accepted formats.
- Minimize and pseudonymize log samples sent to an LLM; avoid unnecessary third-party disclosure.
- Require human confirmation for semantic mappings and approval before publishing exchangeable results.
- Apply authorization consistently across REST and MCP read-only tools.
- Retain provenance, algorithm/model/rule versions and review evidence.
- Never interpret AI text as authorization to execute arbitrary code or modify quantitative evidence.

## Reporting a vulnerability

Do **not** post secrets or exploit details in a public Issue. Contact a project maintainer privately through the repository owner or GitHub's private vulnerability reporting feature if enabled. Do not assume private vulnerability reporting is configured.

Security controls listed here are design objectives; no security audit is claimed.
