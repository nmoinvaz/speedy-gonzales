#!/usr/bin/env python3
"""List test suites in a TestRail project."""

import argparse
import json
import sys

from testrail_api import TestRailAPI


def main():
    parser = argparse.ArgumentParser(description="List test suites in a project")
    parser.add_argument("--project-id", type=int, required=True, help="Project ID")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--names-only", action="store_true", help="Only show suite names and IDs")
    args = parser.parse_args()

    api = TestRailAPI()
    suites = api.suites.get_suites(project_id=args.project_id)
    if isinstance(suites, dict):
        suites = suites.get("suites", [suites])

    if args.json:
        print(json.dumps(suites, indent=2))
    elif args.names_only:
        for s in suites:
            print(f"[{s['id']}] {s['name']}")
    else:
        for s in suites:
            completed = "Yes" if s.get("is_completed") else "No"
            print(f"[{s['id']}] {s['name']}")
            if s.get("description"):
                print(f"     Description: {s['description'][:100]}")
            print(f"     Completed: {completed} | URL: {s.get('url', 'N/A')}")
            print()


if __name__ == "__main__":
    main()
