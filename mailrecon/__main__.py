from __future__ import annotations

import argparse
import json
import sys

from .core import validate


def _load_emails(args: argparse.Namespace) -> list[str]:
    emails = list(args.emails or [])
    if args.file:
        with open(args.file, "r", encoding="utf-8") as handle:
            for line in handle:
                email = line.strip()
                if email:
                    emails.append(email)
    return emails


def _print_results(results: list[dict[str, str]], as_json: bool) -> None:
    if as_json:
        print(json.dumps(results, indent=2))
        return

    for result in results:
        print(f"{result['email']} → {result['status']}")


def _exit_code(results: list[dict[str, str]]) -> int:
    statuses = [result["status"] for result in results]
    if any(status == "unknown" for status in statuses):
        return 2
    if any(status == "exists" for status in statuses):
        return 0
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mailrecon")
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("emails", nargs="*")
    validate_parser.add_argument("--file")
    validate_parser.add_argument("--json", action="store_true", dest="as_json")

    raw_args = list(sys.argv[1:] if argv is None else argv)
    if raw_args and raw_args[0] != "validate":
        raw_args = ["validate"] + raw_args

    args = parser.parse_args(raw_args)
    if args.command != "validate":
        parser.print_usage()
        return 1

    emails = _load_emails(args)
    if not emails:
        validate_parser.error("provide at least one email or use --file")

    results = []
    for email in emails:
        status = validate(email)
        results.append({
            "email": email,
            "status": status,
        })
    _print_results(results, args.as_json)
    return _exit_code(results)


if __name__ == "__main__":
    raise SystemExit(main())
