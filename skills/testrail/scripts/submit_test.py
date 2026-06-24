#!/usr/bin/env python3
"""
Submit a test result with per-step outcomes.

Combines add_result.py's functionality into a convenient single command.
For attaching screenshots, use attach_step_screenshots.py separately.

Per-step results JSON format (file or inline):
    [
        {
            "content":   "Step action description",
            "expected":  "Expected outcome",
            "actual":    "What actually happened",
            "status_id": 1
        }
    ]

Status IDs: 1=Passed, 2=Blocked, 4=Retest, 5=Failed

Requires: pip install testrail-api
Env vars: TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD

Usage:
    python submit_test.py --run-id 201 --case-id 301 --status passed \
        --comment "All steps verified" --elapsed "1m 30s"

    python submit_test.py --run-id 201 --case-id 301 --status failed \
        --comment "Failed at step 2" \
        --step-results-file /tmp/step_results.json
"""

import argparse
import json
from testrail_api import TestRailAPI

STATUS_MAP = {'passed': 1, 'blocked': 2, 'retest': 4, 'failed': 5}


def main():
    parser = argparse.ArgumentParser(
        description='Submit a TestRail test result'
    )
    parser.add_argument('--run-id',   type=int, required=True, help='Test run ID')
    parser.add_argument('--case-id',  type=int, required=True, help='Test case ID')
    parser.add_argument('--status',   choices=list(STATUS_MAP.keys()), required=True,
                        help='Overall result: passed / blocked / retest / failed')
    parser.add_argument('--comment',  default='', help='Actual result description / comment')
    parser.add_argument('--elapsed',  help='Time elapsed e.g. "1m 30s" or "45s"')
    parser.add_argument('--version',  help='App/build version under test')
    parser.add_argument('--defects',  help='Comma-separated defect IDs e.g. "BUG-101,BUG-102"')
    parser.add_argument('--step-results',
                        help='JSON array of per-step result objects (inline string)')
    parser.add_argument('--step-results-file',
                        help='Path to JSON file containing per-step result objects')
    parser.add_argument('--json', action='store_true', help='Output raw JSON')
    args = parser.parse_args()

    # Resolve step results
    step_results = None
    if args.step_results:
        step_results = json.loads(args.step_results)
    elif args.step_results_file:
        with open(args.step_results_file) as f:
            step_results = json.load(f)

    # Build kwargs
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

    print(f'Submitting result: run={args.run_id}, case={args.case_id}, status={args.status}')
    result = api.results.add_result_for_case(
        run_id=args.run_id,
        case_id=args.case_id,
        status_id=STATUS_MAP[args.status],
        **kwargs,
    )
    result_id = result['id']
    print(f'  Result created: id={result_id}')

    if args.json:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
