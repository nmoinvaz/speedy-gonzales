#!/usr/bin/env python3
"""List sections (folders) in a TestRail project/suite."""

import argparse
import json
import sys

from testrail_api import TestRailAPI


def main():
    parser = argparse.ArgumentParser(description="List sections in a project/suite")
    parser.add_argument("--project-id", type=int, required=True, help="Project ID")
    parser.add_argument("--suite-id", type=int, help="Suite ID (required for multi-suite projects)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--names-only", action="store_true", help="Only show section names and IDs")
    parser.add_argument("--tree", action="store_true", help="Show as indented tree")
    args = parser.parse_args()

    api = TestRailAPI()
    kwargs = {"project_id": args.project_id}
    if args.suite_id:
        kwargs["suite_id"] = args.suite_id

    sections = api.sections.get_sections(**kwargs)
    if isinstance(sections, dict):
        sections = sections.get("sections", [])

    if args.json:
        print(json.dumps(sections, indent=2))
    elif args.tree:
        # Build parent-child map
        by_id = {s["id"]: s for s in sections}
        def depth(s):
            d = 0
            while s.get("parent_id") and s["parent_id"] in by_id:
                d += 1
                s = by_id[s["parent_id"]]
            return d
        for s in sections:
            indent = "  " * depth(s)
            print(f"{indent}[{s['id']}] {s['name']}")
    elif args.names_only:
        for s in sections:
            parent = f" (parent: {s['parent_id']})" if s.get("parent_id") else ""
            print(f"[{s['id']}] {s['name']}{parent}")
    else:
        for s in sections:
            parent = f"Parent: {s['parent_id']}" if s.get("parent_id") else "Top-level"
            print(f"[{s['id']}] {s['name']}")
            if s.get("description"):
                print(f"     Description: {s['description'][:100]}")
            print(f"     {parent} | Depth: {s.get('depth', 0)}")
            print()


if __name__ == "__main__":
    main()
