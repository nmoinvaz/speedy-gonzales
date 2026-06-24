#!/usr/bin/env python3
"""
Get all test runs inside a TestRail test plan.

IMPORTANT: api.runs.get_runs() only returns standalone runs (NOT plan runs).
Runs inside a plan live in entries[].runs[] in the get_plan response.
This script extracts and flattens them correctly.

Requires: pip install testrail-api
Env vars: TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD

Usage:
    python get_runs.py --plan-id 42
    python get_runs.py --plan-id 42 --names-only
"""

import argparse
import json
import sys
from testrail_api import TestRailAPI


def get_runs_for_plan(api, plan_id):
    """Return a flat list of all runs across all entries in the plan."""
    plan = api.plans.get_plan(plan_id=plan_id)
    runs = []
    for entry in plan.get('entries', []):
        for run in entry.get('runs', []):
            # Attach entry name for context (prefixed with _ to distinguish from API fields)
            run['_entry_name'] = entry.get('name', '')
            runs.append(run)
    return runs


def main():
    parser = argparse.ArgumentParser(description='Get all test runs in a TestRail test plan')
    parser.add_argument('--plan-id', type=int, required=True, help='Test plan ID')
    parser.add_argument('--names-only', action='store_true', help='Print run_id, name, config only')
    args = parser.parse_args()

    api = TestRailAPI()
    runs = get_runs_for_plan(api, args.plan_id)

    if not runs:
        print(f'No runs found in plan {args.plan_id}', file=sys.stderr)
        sys.exit(1)

    if args.names_only:
        for r in runs:
            config = r.get('config') or '(no config)'
            passed = r.get('passed_count', 0)
            failed = r.get('failed_count', 0)
            untested = r.get('untested_count', 0)
            print(f"run_id={r['id']}\t{r['name']}\tconfig={config}\tp={passed} f={failed} u={untested}")
    else:
        print(json.dumps(runs, indent=2))


if __name__ == '__main__':
    main()
