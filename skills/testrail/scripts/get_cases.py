#!/usr/bin/env python3
"""List test cases in a TestRail project/suite with optional filters."""

import argparse
import json
import sys

from testrail_api import TestRailAPI


STATUS_MAP = {1: "Passed", 2: "Blocked", 3: "Untested", 4: "Retest", 5: "Failed"}
PRIORITY_MAP = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
TYPE_MAP = {}  # Populated at runtime if needed


def main():
    parser = argparse.ArgumentParser(description="List test cases in a project")
    parser.add_argument("--project-id", type=int, required=True, help="Project ID")
    parser.add_argument("--suite-id", type=int, help="Suite ID (required for multi-suite projects)")
    parser.add_argument("--section-id", type=int, help="Filter by section ID")
    parser.add_argument("--priority", type=int, action="append", help="Filter by priority ID (repeatable)")
    parser.add_argument("--type", type=int, action="append", help="Filter by type ID (repeatable)")
    parser.add_argument("--created-after", type=int, help="Filter by creation date (Unix timestamp)")
    parser.add_argument("--updated-after", type=int, help="Filter by update date (Unix timestamp)")
    parser.add_argument("--limit", type=int, help="Max cases to return")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--names-only", action="store_true", help="Only show case titles and IDs")
    parser.add_argument("--with-steps", action="store_true", help="Include step count")
    args = parser.parse_args()

    api = TestRailAPI()
    kwargs = {"project_id": args.project_id}
    if args.suite_id:
        kwargs["suite_id"] = args.suite_id
    if args.section_id:
        kwargs["section_id"] = args.section_id
    if args.priority:
        kwargs["priority_id"] = args.priority
    if args.type:
        kwargs["type_id"] = args.type
    if args.created_after:
        kwargs["created_after"] = args.created_after
    if args.updated_after:
        kwargs["updated_after"] = args.updated_after

    cases = api.cases.get_cases(**kwargs)
    if isinstance(cases, dict):
        cases = cases.get("cases", [])

    if args.limit:
        cases = cases[:args.limit]

    if args.json:
        print(json.dumps(cases, indent=2))
    elif args.names_only:
        for c in cases:
            print(f"C{c['id']} | {c['title']}")
    else:
        for c in cases:
            priority = PRIORITY_MAP.get(c.get("priority_id"), str(c.get("priority_id", "?")))
            section = c.get("section_id", "?")
            print(f"C{c['id']} | {c['title']}")
            print(f"     Priority: {priority} | Section: {section} | Type: {c.get('type_id', '?')}")
            if args.with_steps:
                steps = c.get("custom_steps_separated", [])
                step_count = len(steps) if steps else 0
                has_plain = bool(c.get("custom_steps"))
                fmt = f"{step_count} separated steps" if steps else ("plain text" if has_plain else "none")
                print(f"     Steps: {fmt}")
            if c.get("refs"):
                print(f"     Refs: {c['refs']}")
            print()


if __name__ == "__main__":
    main()
