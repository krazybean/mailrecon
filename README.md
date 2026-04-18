# mailrecon

Detect whether an email account exists across providers.

## Features

- Fast CLI-based validation
- Real signal detection, not regex or MX-only checks
- Provider-specific validation logic for supported providers such as Yahoo

## Installation

```bash
pip install mailrecon
```

## Usage

Validate a single email:

```bash
mailrecon validate email@yahoo.com
```

Validate multiple emails:

```bash
mailrecon validate a@yahoo.com b@yahoo.com
```

Validate from a file:

```bash
mailrecon validate --file emails.txt
```

Get JSON output:

```bash
mailrecon validate --json email@yahoo.com
```

Module execution is also supported:

```bash
python -m mailrecon validate email@yahoo.com
python -m mailrecon email@yahoo.com
```

## Output

Default output:

```text
email@yahoo.com → exists
```

JSON output:

```json
[
  {
    "email": "email@yahoo.com",
    "status": "exists"
  }
]
```

Possible statuses:

- `exists`
- `does_not_exist`
- `unknown`

## Python API

```python
from mailrecon import validate

status = validate("email@yahoo.com")
print(status)
```

## Notes

- Validation is provider-specific and only works for supported domains.
- Live validation can return `unknown` when a provider changes behavior or blocks requests.
