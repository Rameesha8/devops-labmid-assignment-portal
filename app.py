"""Assignment submission portal."""

import json
import os
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, redirect, render_template_string, request, url_for


PAGE = """
<!doctype html>
<title>Assignment Submission Portal</title>
<h1>Assignment Submission Portal</h1>
{% if errors %}<ul class="errors">{% for error in errors %}<li>{{ error }}</li>{% endfor %}</ul>{% endif %}
<form method="post" action="{{ url_for('submit') }}">
  <label>Name <input name="name" value="{{ form.name }}"></label><br>
  <label>Registration number <input name="registration_number" value="{{ form.registration_number }}"></label><br>
  <label>Assignment title <input name="assignment_title" value="{{ form.assignment_title }}"></label><br>
  <label>Submission URL <input name="submission_url" value="{{ form.submission_url }}"></label><br>
  <button type="submit">Submit assignment</button>
</form>
<h2>Saved submissions</h2>
<ul id="submission-list">
{% for item in submissions %}
  <li>{{ item.name }} - {{ item.registration_number }} - {{ item.assignment_title }} - <a href="{{ item.submission_url }}">{{ item.submission_url }}</a></li>
{% else %}
  <li>No submissions yet.</li>
{% endfor %}
</ul>
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
