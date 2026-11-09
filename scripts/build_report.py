"""Convert pytest-json-report output to the report required by the lab."""

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path


def failure_message(test):
    call = test.get("call") or {}
    value = call.get("longrepr") or test.get("longrepr")
    return value if isinstance(value, str) else (json.dumps(value) if value else None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="test-results.json")
    parser.add_argument("--output", default="ci-test-report.json")
    args = parser.parse_args()
    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    tests = []
    for test in raw.get("tests", []):
        result = test.get("outcome", "error")
        tests.append({"name": test.get("nodeid", "unknown"), "result": result,
                      "failure_message": failure_message(test) if result != "passed" else None})
    passed = sum(test["result"] == "passed" for test in tests)
    failed = len(tests) - passed
    report = {
        "repository": os.getenv("GITHUB_REPOSITORY", "local"),
        "branch": os.getenv("GITHUB_REF_NAME", "local"),
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "pipeline_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.now(UTC).isoformat(),
        "tests": tests,
        "summary": {"total": len(tests), "passed": passed, "failed": failed,
                    "status": "passed" if failed == 0 else "failed"},
    }
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
