# envdiff audit

The `audit` subcommand inspects one or more `.env` files for common security
and hygiene issues **without** requiring a full diff reconciliation step.

## Usage

```bash
python -m envdiff audit staging.env production.env [OPTIONS]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--format text\|json` | `text` | Output format |
| `--fail-on-warning` | off | Exit with code `1` when warnings are present |

### Exit codes

| Code | Meaning |
|---|---|
| `0` | No issues found (or only warnings when `--fail-on-warning` is not set) |
| `1` | Warnings found and `--fail-on-warning` is active |
| `2` | One or more **errors** found |

## Checks performed

### Placeholder values (`ERROR`)

Keys whose names suggest they hold sensitive data (containing words such as
`secret`, `password`, `token`, `key`, `api`, `auth`) but whose values look
like placeholders (`changeme`, `todo`, `your_*`, `<…>`, etc.) are flagged as
errors because they indicate the file was never properly filled in.

### Missing sensitive keys (`WARNING`)

A sensitive key that exists in one environment but is absent from the other
is flagged as a warning — it may indicate a misconfiguration or a forgotten
secret.

### Non-uppercase keys (`WARNING`)

By convention, environment variable names should be `UPPER_SNAKE_CASE`.
Keys that are entirely lowercase alphabetic characters are flagged.

## Example output

```
[ERROR] SECRET_KEY: Sensitive key appears to have a placeholder value: 'changeme'.
[WARNING] API_TOKEN: Sensitive key present in staging but missing in production.
```

## JSON output

```json
[
  {
    "key": "SECRET_KEY",
    "severity": "error",
    "message": "Sensitive key appears to have a placeholder value: 'changeme'."
  }
]
```
