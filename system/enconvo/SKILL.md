---
name: enconvo
description: Interact with Enconvo, the agent runtime environment you are running in . Use when needing to control Enconvo , manage credentials (API keys).
---

# Enconvo Skills

Enconvo is the local agent runtime environment. It exposed all functions as Http-API at `http://localhost:54535`. All Enconvo features are exposed as **commands** callable via HTTP.

## Command System

### Command Key & Path

Every command has a **commandKey** in the format `extensionName|commandName`.

To call a command via HTTP, replace `|` with `/`:

```
commandKey:  writing_package|fix_spelling_and_grammar
URL:         http://localhost:54535/command/call/writing_package/fix_spelling_and_grammar
```

### Calling Commands

**Base URL**: `http://localhost:54535/command/call/{extensionName}/{commandName}`

Pass parameters as JSON body via POST:

```bash
# Fix grammar
curl -X POST "http://localhost:54535/command/call/writing_package/fix_spelling_and_grammar" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "hello wrold"}'

# Translate text
curl -X POST "http://localhost:54535/command/call/translate/translate" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "hello", "target_language": "zh"}'
```

### Response Format

Commands return JSON. Most AI-powered commands return:

```json
{
  "type": "messages",
  "messages": [
    {
      "role": "assistant",
      "content": [{ "type": "text", "text": "the result text", "id": "..." }],
      "id": "..."
    }
  ]
}
```

Data query commands return raw JSON arrays or objects.

## Credentials Management

Enconvo manages API keys and OAuth tokens for all supported providers (OpenAI, Anthropic, Google, etc.).

### List All Credential Providers

```bash
curl -X POST "http://localhost:54535/command/call/search/get_all_credentials_providers"
```

Returns an array of providers, each with:

- `providerName` - identifier (e.g., `open_ai`, `anthropic`, `enconvo_ai`)
- `title` - display name
- `description` - provider description
- `preferences` - array of configuration fields (apiKey, baseUrl, credentials_type, etc.)

### Load Credentials for a Provider

```bash
curl -X POST "http://localhost:54535/command/call/credentials/load_credentials" \
  -H "Content-Type: application/json" \
  -d '{"providerName": "anthropic"}'
```

Returns the provider's stored credential values:

- `access_token`, `refresh_token` - for OAuth2 providers
- `apiKey` - for API key providers
- `baseUrl` - API endpoint URL
- `credentials_type` - `apiKey` or `oauth2`
- `preferenceKey` - the full preference key (e.g., `credentials|anthropic`)

### Request User to Fill Credentials

When credentials are missing or invalid, prompt the user to fill them via a UI page:

```bash
curl -X POST "http://localhost:54535/command/call/credentials/request_user_fill_credentials" \
  -H "Content-Type: application/json" \
  -d '{"providerName": "anthropic"}'
```

This opens a credential configuration page in Enconvo for the user to enter their API key or complete OAuth. Wait for the user to finish filling in credentials before continuing the workflow.

### Common Providers

| providerName | Title         | Auth Type        |
| ------------ | ------------- | ---------------- |
| `open_ai`    | OpenAI        | API Key / OAuth2 |
| `anthropic`  | Anthropic     | API Key / OAuth2 |
| `gemini`     | Google Gemini | API Key / OAuth2 |

## Notes

- Enconvo must be running locally for API access
- All HTTP calls use POST method with JSON body
- Credentials contain sensitive data (API keys, tokens) - handle securely
