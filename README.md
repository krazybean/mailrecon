[![PyPI version](https://img.shields.io/pypi/v/mailrecon)](https://pypi.org/project/mailrecon/)
![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mailrecon)

# mailrecon

Detect whether an email account exists using real provider validation flows (CLI tool)

## Features

- Fast CLI-based validation
- Real signal detection, not regex or MX-only checks
- Provider-specific validation logic for supported providers such as Yahoo

## Installation

```bash
pip install mailrecon
```

## Usage

### Single email

```bash
mailrecon validate user@yahoo.com
mailrecon validate user@gmail.com
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
mailrecon validate --json user@gmail.com
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
    "email": "user@gmail.com",
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
- Different providers use different validation strategies. Some providers, like Yahoo, use deeper validation flows, while others may return results more directly.
- Live validation can return `unknown` when a provider changes behavior or blocks requests.
