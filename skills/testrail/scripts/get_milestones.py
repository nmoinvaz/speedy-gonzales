#!/usr/bin/env python3
"""List milestones in a TestRail project."""

import argparse
import json
import sys
from datetime import datetime

from testrail_api import TestRailAPI


def ts_to_date(ts):
    if not ts:
        return "N/A"
    return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(description="List milestones in a project")
    parser.add_argument("--project-id", type=int, required=True, help="Project ID")
    parser.add_argument("--id", type=int, help="Get a single milestone by ID")
    parser.add_argument("--active-only", action="store_true", help="Only show active milestones")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--names-only", action="store_true", help="Only show milestone names and IDs")
    args = parser.parse_args()

    api = TestRailAPI()

    if args.id:
        milestone = api.milestones.get_milestone(milestone_id=args.id)
        if args.json:
            print(json.dumps(milestone, indent=2))
        else:
            print_milestone(milestone)
        return

    milestones = api.milestones.get_milestones(project_id=args.project_id)
    if isinstance(milestones, dict):
        milestones = milestones.get("milestones", [])

    if args.active_only:
        milestones = [m for m in milestones if not m.get("is_completed")]

    if args.json:
        print(json.dumps(milestones, indent=2))
    elif args.names_only:
        for m in milestones:
            status = "✅" if not m.get("is_completed") else "🏁"
            print(f"{status} [{m['id']}] {m['name']}")
    else:
        for m in milestones:
            print_milestone(m)


def print_milestone(m):
    status = "Completed" if m.get("is_completed") else "Active"
    print(f"[{m['id']}] {m['name']} ({status})")
    if m.get("description"):
        print(f"     Description: {m['description'][:100]}")
    start = ts_to_date(m.get("start_on"))
    due = ts_to_date(m.get("due_on"))
    print(f"     Start: {start} | Due: {due}")
    if m.get("url"):
        print(f"     URL: {m['url']}")
    # Sub-milestones
    subs = m.get("milestones", [])
    if subs:
        print(f"     Sub-milestones: {len(subs)}")
        for s in subs:
            sub_status = "Completed" if s.get("is_completed") else "Active"
            print(f"       [{s['id']}] {s['name']} ({sub_status})")
    print()


if __name__ == "__main__":
    main()
