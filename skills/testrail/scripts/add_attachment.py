#!/usr/bin/env python3
"""
Attach a screenshot, log file, or any other file to a TestRail test result.

The attachment is uploaded via multipart/form-data. You can attach to:
  --result-id   : A test result (most common — attach evidence to a specific run result)
  --run-id      : A test run overall
  --case-id     : A test case template

Requires: pip install testrail-api
Env vars: TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD

Usage:
    python add_attachment.py --result-id 9001 --file /tmp/screenshot.png
    python add_attachment.py --result-id 9001 --file /tmp/test_output.log
    python add_attachment.py --run-id 201 --file /tmp/summary.png
    python add_attachment.py --case-id 301 --file /tmp/spec.pdf
"""

import argparse
import json
import os
import sys
from testrail_api import TestRailAPI


def main():
    parser = argparse.ArgumentParser(description='Attach a file to a TestRail result, run, or case')
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--result-id', type=int, help='Test result ID (attach to a specific result)')
    target.add_argument('--run-id',    type=int, help='Test run ID (attach to the run overall)')
    target.add_argument('--case-id',   type=int, help='Test case ID (attach to the case template)')
    parser.add_argument('--file', required=True, help='Path to file to upload')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f'File not found: {args.file}', file=sys.stderr)
        sys.exit(1)

    api = TestRailAPI()

    if args.result_id:
        response = api.attachments.add_attachment_to_result(
            result_id=args.result_id, path=args.file
        )
        target_desc = f'result {args.result_id}'
    elif args.run_id:
        response = api.attachments.add_attachment_to_run(
            run_id=args.run_id, path=args.file
        )
        target_desc = f'run {args.run_id}'
    else:
        response = api.attachments.add_attachment_to_case(
            case_id=args.case_id, path=args.file
        )
        target_desc = f'case {args.case_id}'

    attachment_id = response.get('attachment_id')
    print(f"Attached '{os.path.basename(args.file)}' to {target_desc}  →  attachment_id={attachment_id}")
    print(json.dumps(response, indent=2))


if __name__ == '__main__':
    main()
