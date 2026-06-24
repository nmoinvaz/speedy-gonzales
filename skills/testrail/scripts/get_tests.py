#!/usr/bin/env python3
"""
Get all tests (case instances) in a TestRail test run.

A "test" in TestRail is a live instance of a case within a specific run.
Every case included in a run gets a unique test_id. Use test_id for add_result,
and case_id for add_result_for_case.

Status IDs: 1=Passed, 2=Blocked, 3=Untested, 4=Retest, 5=Failed

Requires: pip install testrail-api
Env vars: TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD

Usage:
    python get_tests.py --run-id 201
    python get_tests.py --run-id 201 --status failed
    python get_tests.py --run-id 201 --status untested --names-only
"""

import argparse
import json
import sys
from testrail_api import TestRailAPI

STATUS_MAP = {
    'passed': 1, 'blocked': 2, 'untested': 3, 'retest': 4, 'failed': 5
}
STATUS_LABEL = {v: k for k, v in STATUS_MAP.items()}


def main():
    parser = argparse.ArgumentParser(description='Get all tests in a TestRail run')
    parser.add_argument('--run-id', type=int, required=True, help='Test run ID')
    parser.add_argument('--status', choices=list(STATUS_MAP.keys()), help='Filter by status')
    parser.add_argument('--names-only', action='store_true',
                        help='Print test_id, case_id, status, title on one line each')
    args = parser.parse_args()

    api = TestRailAPI()
    kwargs = {}
    if args.status:
        kwargs['status_id'] = [STATUS_MAP[args.status]]

    tests = api.tests.get_tests_bulk(run_id=args.run_id, **kwargs)

    if not tests:
        print(f'No tests found in run {args.run_id}', file=sys.stderr)
        sys.exit(1)

    if args.names_only:
        for t in tests:
            status = STATUS_LABEL.get(t.get('status_id', 3), 'unknown')
            print(f"test_id={t['id']}\tcase_id={t['case_id']}\t[{status}]\t{t['title']}")
    else:
        print(json.dumps(tests, indent=2))


if __name__ == '__main__':
    main()
