#!/usr/bin/env python3
"""Check effective gh identity; apply readiness only to that user's own issue."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from urllib.parse import urlsplit


class GuardError(Exception):
    pass


def issue_address(url: str) -> tuple[str, str, str]:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port is not None
        or not re.fullmatch(r"[A-Za-z0-9.-]+", parsed.hostname)
    ):
        raise GuardError("Use an HTTPS GitHub issue URL without credentials or a port")
    match = re.fullmatch(
        r"/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)/?",
        parsed.path,
    )
    if match is None or any(part in (".", "..") for part in match.groups()[:2]):
        raise GuardError("Expected https://HOST/OWNER/REPO/issues/NUMBER (not a pull request)")
    owner, repo, number = match.groups()
    return parsed.hostname, f"repos/{owner}/{repo}/issues/{number}", (
        f"https://{parsed.hostname}/{owner}/{repo}/issues/{number}"
    )


def api(host: str, endpoint: str, env: dict[str, str], payload: dict | None = None):
    command = ["gh", "api", "--hostname", host, endpoint]
    if payload is not None:
        command.extend(["--method", "POST", "--input", "-"])
    try:
        result = subprocess.run(
            command,
            input=json.dumps(payload) if payload is not None else None,
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise GuardError("gh request failed or timed out; inspect GitHub state before retrying") from error
    if result.returncode:
        raise GuardError(f"gh request failed for {endpoint}; check authentication and permissions")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise GuardError("GitHub returned an invalid JSON response") from error


def identity(value) -> tuple[int, str]:
    if not isinstance(value, dict):
        raise GuardError("GitHub user identity is missing")
    user_id, login = value.get("id"), value.get("login")
    if type(user_id) is not int or user_id <= 0 or not isinstance(login, str) or not login:
        raise GuardError("GitHub user identity is incomplete")
    return user_id, login


def checked_issue(host: str, endpoint: str, env: dict[str, str]):
    actor = identity(api(host, "user", env))
    issue = api(host, endpoint, env)
    if not isinstance(issue, dict) or "pull_request" in issue:
        raise GuardError("The target is not an issue")
    author = identity(issue.get("user"))
    return actor, author, issue


def guard(url: str, label: str, apply: bool) -> int:
    if not label.strip():
        raise GuardError("The ready-for-agent label cannot be empty")
    host, endpoint, canonical_url = issue_address(url)
    env = dict(os.environ)
    actor, author, issue = checked_issue(host, endpoint, env)
    owned = actor[0] == author[0]
    report = {
        "issue": canonical_url,
        "authenticated_login": actor[1],
        "author_login": author[1],
        "same_author": owned,
        "label": label,
        "applied": False,
    }
    if not owned:
        report["next_step"] = "create_separate_implementation_issue"
        print(json.dumps(report))
        return 3
    if apply:
        current_actor, current_author, issue = checked_issue(host, endpoint, env)
        if current_actor[0] != actor[0] or current_author[0] != actor[0]:
            raise GuardError("Identity or author changed; readiness was not applied")
        if issue.get("state") != "open":
            raise GuardError("Readiness can only be applied to an open issue")
        labels = api(host, f"{endpoint}/labels", env, {"labels": [label]})
        if not isinstance(labels, list) or not any(
            isinstance(item, dict) and item.get("name") == label for item in labels
        ):
            raise GuardError("Readiness was not confirmed; inspect GitHub before retrying")
        report["applied"] = True
    print(json.dumps(report))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue_url")
    parser.add_argument("--label", default="ready-for-agent")
    parser.add_argument("--apply", action="store_true", help="apply the label after rechecking ownership")
    args = parser.parse_args()
    try:
        return guard(args.issue_url, args.label, args.apply)
    except (GuardError, ValueError) as error:
        print(f"triage-to-owned: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
