#!/usr/bin/env python3
"""
Find a TestRail test plan by name or ID, or list all plans in a project.

Requires: pip install testrail-api
Env vars: TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD

Usage:
    # Get a specific plan by ID (full detail, includes entries and runs)
    python get_plan.py --id 42

    # Search by exact name (project-id required)
    python get_plan.py --project-id 1 --name "Sprint 14 Regression"

    # List all plans in a project
    python get_plan.py --project-id 1 --list
    python get_plan.py --project-id 1 --list --active-only
"""

import argparse
import json
import sys
from testrail_api import TestRailAPI


def main():
    parser = argparse.ArgumentParser(description='Get TestRail test plan(s)')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--id', type=int, help='Test plan ID (direct lookup, includes runs)')
    group.add_argument('--name', help='Search for plan by exact/partial name (requires --project-id)')
    group.add_argument('--list', action='store_true', help='List all plans (requires --project-id)')
    parser.add_argument('--project-id', type=int, help='Project ID (required for --name and --list)')
    parser.add_argument('--active-only', action='store_true', help='Skip completed plans')
    args = parser.parse_args()

    api = TestRailAPI()

    if args.id:
        # Direct lookup — response includes entries[].runs[]
        plan = api.plans.get_plan(plan_id=args.id)
        print(json.dumps(plan, indent=2))

    elif args.list:
        if not args.project_id:
            parser.error('--project-id is required with --list')
        kwargs = {}
        if args.active_only:
            kwargs['is_completed'] = False
        plans = api.plans.get_plans_bulk(project_id=args.project_id, **kwargs)
        for p in plans:
            status = 'COMPLETED' if p.get('is_completed') else 'active'
            print(f"id={p['id']}\t[{status}]\t{p['name']}")

    else:
        # Search by name
        if not args.project_id:
            parser.error('--project-id is required with --name')
        kwargs = {}
        if args.active_only:
            kwargs['is_completed'] = False
        all_plans = api.plans.get_plans_bulk(project_id=args.project_id, **kwargs)

        # Try exact match first, then partial
        match = next((p for p in all_plans if p['name'] == args.name), None)
        if not match:
            matches = [p for p in all_plans if args.name.lower() in p['name'].lower()]
            if len(matches) == 1:
                match = matches[0]
            elif len(matches) > 1:
                print(f"Multiple partial matches for '{args.name}':", file=sys.stderr)
                for p in matches:
                    print(f"  id={p['id']}\t{p['name']}", file=sys.stderr)
                print("Re-run with --id or a more specific --name.", file=sys.stderr)
                sys.exit(1)

        if match:
            # Fetch full plan to include entries[] and runs[]
            full_plan = api.plans.get_plan(plan_id=match['id'])
            print(json.dumps(full_plan, indent=2))
        else:
            print(f"No plan found matching: '{args.name}'", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
