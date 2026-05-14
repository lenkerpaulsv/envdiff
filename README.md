# envdiff

A Python utility to diff and reconcile `.env` files across staging and production environments.

---

## Installation

```bash
pip install envdiff
```

---

## Usage

Compare two `.env` files and highlight missing or mismatched keys:

```bash
envdiff staging.env production.env
```

**Example output:**

```
[MISSING IN PRODUCTION]  DATABASE_URL
[MISSING IN STAGING]     NEW_RELIC_KEY
[VALUE MISMATCH]         LOG_LEVEL  staging=debug  production=info
```

Reconcile by copying missing keys from staging to production:

```bash
envdiff staging.env production.env --reconcile --target production.env
```

### Options

| Flag | Description |
|------|-------------|
| `--reconcile` | Merge missing keys into the target file |
| `--target` | Specify the output file for reconciliation |
| `--ignore-values` | Compare keys only, ignore value differences |
| `--quiet` | Suppress output, exit code only |

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).