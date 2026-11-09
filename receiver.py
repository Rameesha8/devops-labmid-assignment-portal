"""Local HTTP receiver for GitHub Actions test reports."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


REPORT_PATH = Path(__file__).with_name("test-report.json")


class ReportHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/report":
            self.send_error(404, "Use POST /report")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            report = json.loads(self.rfile.read(length))
            required = {"repository", "branch", "commit_sha", "pipeline_run_id", "timestamp", "tests", "summary"}
            if not required.issubset(report):
                raise ValueError("Report is missing required fields")
            REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        except (ValueError, json.JSONDecodeError) as error:
            self.send_error(400, str(error))
            return
        self.send_response(201)
        self.end_headers()
        self.wfile.write(b"Report saved\n")

    def log_message(self, format, *args):
        print("Receiver:", format % args)


if __name__ == "__main__":
    print("Listening for reports at http://127.0.0.1:5001/report")
    HTTPServer(("127.0.0.1", 5001), ReportHandler).serve_forever()
