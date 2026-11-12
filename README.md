# DevOps Lab Mid - Assignment Submission Portal

A small Flask portal where students enter their name, registration number, assignment title, and a submission link. Valid submissions are saved in `submissions.json` and shown on the page. File uploads are deliberately not included.

## Local setup

All project dependencies stay in `.venv` (nothing is installed globally):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest --json-report --json-report-file=test-results.json
```

The three required cases cover a valid submission, missing registration number, and an invalid URL. A non-zero pytest exit code means the CI job fails.

## Local report receiver

In a second PowerShell window, start this before pushing:

```powershell
.\.venv\Scripts\python.exe receiver.py
```

It accepts `POST /report` at `http://127.0.0.1:5001/report` and automatically overwrites `test-report.json` with the received JSON.

## GitHub Actions setup

The workflow in `.github/workflows/ci.yml` runs on **every push** using a self-hosted Windows runner. This is intentional: a GitHub-hosted runner's `localhost` is not your computer. Register a Windows self-hosted runner for this repository, keep `receiver.py` running, then push. The workflow creates its own `.venv`, runs pytest, generates a report from the actual pytest result, posts it to the receiver even after test failures, and finally marks the job failed when tests failed.

By default the receiver URL is `http://127.0.0.1:5001/report`. To use a relay/tunnel instead, create a GitHub repository variable named `RECEIVER_URL` with that endpoint.

## Bonus: GitHub Pages deployment

The workflow also deploys the static browser-only demo in `static-demo/` to GitHub Pages after a push to `main` **only when the complete test-and-report job succeeds**. A failed test prevents the deployment job from running, so the previously published page remains unchanged. In repository **Settings -> Pages**, select **GitHub Actions** as the build and deployment source. The deployed URL will be shown in the successful `Deploy static demo to GitHub Pages` job.

## Bonus: email report

The workflow can email `ci-test-report.json` after both passing and failing runs. Add these repository secrets in **Settings -> Secrets and variables -> Actions**:

- `SMTP_HOST` - SMTP server, for example `smtp.gmail.com`
- `SMTP_PORT` - usually `587`
- `SMTP_USERNAME` - sender email address
- `SMTP_PASSWORD` - SMTP password; for Gmail, use an App Password, not the account password
- `REPORT_EMAIL_TO` - recipient email address

When all five secrets are present, the workflow sends a report summary and attaches the complete JSON report. Secrets are never committed to the repository.

## Demonstration checklist

1. Push the working project and show the successful Actions run and `test-report.json` (`status: passed`).
2. Introduce a small defect in an assertion or validation rule, push, and show the failed Actions run plus the automatically updated report (`status: failed` with its failure message).
3. Fix the defect, push again, and show the passing run and updated report.

Commit this project to a GitHub repository and submit that repository URL with screenshots/evidence of the three runs.
