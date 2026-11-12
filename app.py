"""Assignment submission portal."""

import json
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, redirect, render_template_string, request, url_for


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Assignment Submission Portal</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <main class="page-shell">
    <header class="hero">
      <p class="eyebrow">DEVOPS LAB MID</p>
      <h1>Assignment Submission Portal</h1>
      <p>Submit your assignment link securely and keep track of saved submissions.</p>
    </header>

    <section class="card" aria-labelledby="form-heading">
      <h2 id="form-heading">New submission</h2>
      <p class="helper-text">All fields are required. Use a complete HTTP or HTTPS link.</p>
      {% if errors %}
      <div class="alert" role="alert">
        <strong>Please fix the following:</strong>
        <ul>{% for error in errors %}<li>{{ error }}</li>{% endfor %}</ul>
      </div>
      {% endif %}
      <form method="post" action="{{ url_for('submit') }}">
        <div class="field">
          <label for="name">Student name</label>
          <input id="name" name="name" value="{{ form.name }}" placeholder="e.g. Ayesha Khan" required>
        </div>
        <div class="field">
          <label for="registration_number">Registration number</label>
          <input id="registration_number" name="registration_number" value="{{ form.registration_number }}" placeholder="e.g. FA22-BCS-001" required>
        </div>
        <div class="field">
          <label for="assignment_title">Assignment title</label>
          <input id="assignment_title" name="assignment_title" value="{{ form.assignment_title }}" placeholder="e.g. DevOps Lab Mid" required>
        </div>
        <div class="field">
          <label for="submission_url">Submission URL</label>
          <input id="submission_url" type="url" name="submission_url" value="{{ form.submission_url }}" placeholder="https://example.com/submission" required>
        </div>
        <button type="submit">Submit assignment <span aria-hidden="true">→</span></button>
      </form>
    </section>

    <section class="card submissions" aria-labelledby="submissions-heading">
      <div class="section-heading">
        <div>
          <h2 id="submissions-heading">Saved submissions</h2>
          <p>Submissions received through this portal.</p>
        </div>
        <span class="count">{{ submissions|length }}</span>
      </div>
      <div id="submission-list">
      {% for item in submissions %}
        <article class="submission-item">
          <div class="student-avatar">{{ item.name[0]|upper }}</div>
          <div class="submission-details">
            <h3>{{ item.assignment_title }}</h3>
            <p>{{ item.name }} <span>•</span> {{ item.registration_number }}</p>
            <a href="{{ item.submission_url }}" target="_blank" rel="noopener">Open submission ↗</a>
          </div>
        </article>
      {% else %}
        <div class="empty-state">
          <div class="empty-icon">⌁</div>
          <p>No submissions yet.</p>
          <span>Your saved submissions will appear here.</span>
        </div>
      {% endfor %}
      </div>
    </section>
  </main>
</body>
</html>
"""


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(DATA_FILE=Path(app.root_path) / "submissions.json")
    if test_config:
        app.config.update(test_config)

    def load_submissions():
        data_file = Path(app.config["DATA_FILE"])
        if not data_file.exists():
            return []
        return json.loads(data_file.read_text(encoding="utf-8"))

    def save_submissions(submissions):
        data_file = Path(app.config["DATA_FILE"])
        data_file.parent.mkdir(parents=True, exist_ok=True)
        data_file.write_text(json.dumps(submissions, indent=2), encoding="utf-8")

    @app.get("/")
    def index():
        return render_template_string(PAGE, errors=[], form={}, submissions=load_submissions())

    @app.post("/submit")
    def submit():
        form = {field: request.form.get(field, "").strip() for field in (
            "name", "registration_number", "assignment_title", "submission_url"
        )}
        labels = {
            "name": "Name", "registration_number": "Registration number",
            "assignment_title": "Assignment title", "submission_url": "Submission URL",
        }
        errors = [f"{labels[field]} is required." for field, value in form.items() if not value]
        parsed = urlparse(form["submission_url"])
        if form["submission_url"] and (parsed.scheme not in {"http", "https"} or not parsed.netloc):
            errors.append("Submission URL must be a valid http:// or https:// URL.")
        if errors:
            return render_template_string(PAGE, errors=errors, form=form, submissions=load_submissions()), 400

        submissions = load_submissions()
        submissions.append(form)
        save_submissions(submissions)
        return redirect(url_for("index"))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
