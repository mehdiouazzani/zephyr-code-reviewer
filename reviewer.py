#!/usr/bin/env python3
"""
Zephyr C Code Review Agent
Usage: python3 reviewer.py <file.c> [--output report.pdf]
"""

import sys
import os
import argparse
from rules import ALL_RULES
from report import generate_report


def review_file(source_path):
    """Run all rules on a C source file and return findings."""
    with open(source_path, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    lines = source.splitlines()
    findings = []

    for rule_fn in ALL_RULES:
        results = rule_fn(lines)
        findings.extend(results)

    return findings, lines


def print_summary(findings, source_file):
    n_crit = sum(1 for f in findings if f["severity"] == "CRITICAL")
    n_warn = sum(1 for f in findings if f["severity"] == "WARNING")
    n_info = sum(1 for f in findings if f["severity"] == "INFO")

    print(f"\n{'='*60}")
    print(f"  Zephyr Code Review — {os.path.basename(source_file)}")
    print(f"{'='*60}")
    print(f"  CRITICAL : {n_crit}")
    print(f"  WARNING  : {n_warn}")
    print(f"  INFO     : {n_info}")
    print(f"  TOTAL    : {len(findings)}")
    print(f"{'='*60}\n")

    for f in sorted(findings, key=lambda x: (
        0 if x["severity"]=="CRITICAL" else 1 if x["severity"]=="WARNING" else 2, x["line"])):
        print(f"  [{f['severity']:<8}] Line {f['line']:>3} | {f['rule']:<25} | {f['message'][:60]}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Zephyr C Code Review Agent")
    parser.add_argument("file", help="C source file to review")
    parser.add_argument("--output", default=None, help="Output PDF report path")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    print(f"Analyzing {args.file}...")
    findings, lines = review_file(args.file)
    print_summary(findings, args.file)

    output_path = args.output or args.file.replace(".c", "_review_report.pdf")
    generate_report(output_path, args.file, findings, lines)
    print(f"PDF report generated: {output_path}")


if __name__ == "__main__":
    main()
