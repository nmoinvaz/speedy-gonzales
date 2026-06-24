#!/usr/bin/env python3
"""
Get all steps for a TestRail test case or test instance.

Steps come from the custom_steps_separated field (structured array of step objects)
or custom_steps (legacy plain-text format). Always prefer custom_steps_separated.

You can pass either:
  --case-id  : a case template ID (not tied to any run)
  --test-id  : a test instance ID (the live version inside a run — same steps)

Requires: pip install testrail-api
Env vars: TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD

Usage:
    python get_steps.py --case-id 301
    python get_steps.py --test-id 5001
    python get_steps.py --case-id 301 --json       # raw JSON output
"""

import argparse
import json
import sys
from testrail_api import TestRailAPI


def extract_steps(obj):
    """
    Extract steps from a case or test dict.
    Returns a list of dicts: {number, action, expected, additional_info, refs}
    """
    separated = obj.get('custom_steps_separated')
    if separated:
        return [
            {
                'number': i + 1,
                'action': step.get('content', ''),
                'expected': step.get('expected', ''),
                'additional_info': step.get('additional_info'),
                'refs': step.get('refs'),
            }
            for i, step in enumerate(separated)
        ]
    # Fall back to plain-text single field
    plain = obj.get('custom_steps', '')
    if plain:
        return [{'number': 1, 'action': plain, 'expected': obj.get('custom_expected', '')}]
    return []


def main():
    parser = argparse.ArgumentParser(description='Get steps for a TestRail case or test')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--case-id', type=int, help='Case template ID')
    group.add_argument('--test-id', type=int, help='Test instance ID (from a run)')
    parser.add_argument('--json', dest='as_json', action='store_true', help='Output raw JSON')
    args = parser.parse_args()

    api = TestRailAPI()

    if args.case_id:
        obj = api.cases.get_case(case_id=args.case_id)
        label = f"Case [{obj['id']}] {obj['title']}"
    else:
        obj = api.tests.get_test(test_id=args.test_id)
        label = f"Test [{obj['id']}] {obj['title']}  (case_id={obj['case_id']})"

    steps = extract_steps(obj)

    if args.as_json:
        print(json.dumps(steps, indent=2))
        return

    print(label)
    print(f"Total steps: {len(steps)}\n")
    for step in steps:
        print(f"Step {step['number']}:")
        print(f"  Action:   {step['action']}")
        print(f"  Expected: {step['expected']}")
        if step.get('additional_info'):
            print(f"  Notes:    {step['additional_info']}")
        print()


if __name__ == '__main__':
    main()
