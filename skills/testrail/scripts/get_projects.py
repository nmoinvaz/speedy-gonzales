#!/usr/bin/env python3
"""List all projects in TestRail."""

import argparse
import json
import os
import sys

from testrail_api import TestRailAPI


def main():
    parser = argparse.ArgumentParser(description="List TestRail projects")
    parser.add_argument("--active-only", action="store_true", help="Only show active (non-completed) projects")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--names-only", action="store_true", help="Only show project names and IDs")
    args = parser.parse_args()

    api = TestRailAPI()
    projects = api.projects.get_projects()
    if isinstance(projects, dict):
        projects = projects.get("projects", [])

    if args.active_only:
        projects = [p for p in projects if not p.get("is_completed")]

    if args.json:
        print(json.dumps(projects, indent=2))
    elif args.names_only:
        for p in projects:
            status = "✅" if not p.get("is_completed") else "🏁"
            print(f"{status} [{p['id']}] {p['name']}")
    else:
        for p in projects:
            status = "Completed" if p.get("is_completed") else "Active"
            print(f"[{p['id']}] {p['name']} ({status})")
            if p.get("announcement"):
                print(f"     {p['announcement'][:100]}")
            print(f"     Suite mode: {p.get('suite_mode', '?')} | URL: {p.get('url', 'N/A')}")
            print()


if __name__ == "__main__":
    main()
