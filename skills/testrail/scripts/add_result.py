#!/usr/bin/env python3
"""
Submit a test result to TestRail, with optional per-step outcomes.

Status IDs: 1=Passed, 2=Blocked, 4=Retest, 5=Failed
(3=Untested cannot be submitted — it is the default before execution)

Per-step results JSON format:
    [
        {
            "content":   "Step action text",
            "expected":  "Expected result",
            "actual":    "What actually happened",
            "status_id": 1
        },
        ...
    ]

Requires: pip install testrail-api
Env vars: TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD

Usage:
    # Simple pass/fail
    python add_result.py --run-id 201 --case-id 301 --status passed --comment "All steps passed"

    # With timing and version
    python add_result.py --run-id 201 --case-id 301 --status passed \
        --comment "Login test passed" --elapsed "1m 30s" --version "2.1.0"

    # With per-step results inline
    python add_result.py --run-id 201 --case-id 301 --status failed \
        --comment "Failed at step 2" \
        --step-results '[{"content":"Open app","expected":"App opens","actual":"App opened","status_id":1},{"content":"Click submit","expected":"Dialog shows","actual":"Nothing happened","status_id":5}]'

    # With per-step results from file
    python add_result.py --run-id 201 --case-id 301 --status failed \
        --step-results-file /tmp/step_results.json
"""

import argparse
import json
import sys
from testrail_api import TestRailAPI

STATUS_MAP = {'passed': 1, 'blocked': 2, 'retest': 4, 'failed': 5}


def main():
    parser = argparse.ArgumentParser(description='Submit a TestRail test result')
    parser.add_argument('--run-id',   type=int, required=True, help='Test run ID')
    parser.add_argument('--case-id',  type=int, required=True, help='Test case ID')
    parser.add_argument('--status',   choices=list(STATUS_MAP.keys()), required=True,
                        help='Overall result status')
    parser.add_argument('--comment',  default='', help='Actual result description / comment')
    parser.add_argument('--elapsed',  help='Time elapsed e.g. "1m 30s" or "45s"')
    parser.add_argument('--version',  help='App/build version under test')
    parser.add_argument('--defects',  help='Comma-separated defect/bug IDs e.g. "BUG-101,BUG-102"')
    parser.add_argument('--step-results',
                        help='JSON array of per-step result objects (inline string)')
    parser.add_argument('--step-results-file',
                        help='Path to JSON file containing per-step result objects')
    args = parser.parse_args()

    # Resolve step results from inline JSON or file
    step_results = None
    if args.step_results:
        step_results = json.loads(args.step_results)
    elif args.step_results_file:
        with open(args.step_results_file) as f:
            step_results = json.load(f)

    # Build keyword args for the API call
    kwargs = {'comment': args.comment}
    if args.elapsed:
        kwargs['elapsed'] = args.elapsed
    if args.version:
        kwargs['version'] = args.version
    if args.defects:
        kwargs['defects'] = args.defects
    if step_results:
        kwargs['custom_step_results'] = step_results

    api = TestRailAPI()
    result = api.results.add_result_for_case(
        run_id=args.run_id,
        case_id=args.case_id,
        status_id=STATUS_MAP[args.status],
        **kwargs,
    )

    print(f"Result created: id={result['id']}  status={args.status}")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
