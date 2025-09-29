"""
feedback_analytics.py
Tracks test failures, lint errors, and code quality trends over time.
Appends results to feedback_analytics.log for continuous improvement.
Usage:
    python scripts/feedback_analytics.py
"""
import subprocess
import datetime
import os

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def log_feedback(message):
    # Ensure log file exists
    if not os.path.exists('feedback_analytics.log'):
        with open('feedback_analytics.log', 'w') as f:
            f.write('')
    with open('feedback_analytics.log', 'a') as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def main():
    # Run pytest
    out, err, code = run_command('pytest --maxfail=5 --disable-warnings')
    log_feedback(f"Pytest exit code: {code}\n{out}\n{err}")
    # Run flake8
    out, err, code = run_command('flake8 .')
    log_feedback(f"Flake8 exit code: {code}\n{out}\n{err}")
    # Run mypy
    out, err, code = run_command('mypy .')
    log_feedback(f"Mypy exit code: {code}\n{out}\n{err}")
    print('Feedback analytics complete. See feedback_analytics.log for details.')

if __name__ == '__main__':
    main()
