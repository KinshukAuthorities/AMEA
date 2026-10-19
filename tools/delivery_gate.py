"""Read-only acceptance-record checks; this tool never performs perceptual review."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from common import sha256


METHODS = {"visual", "playback", "listening", "reopen", "mechanical", "document"}


class GateError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise GateError(message)


def words(value):
    return isinstance(value, str) and bool(value.strip())


def records(value, label, nonempty=False):
    require(isinstance(value, list) and (value or not nonempty), f"{label}: expected a list")
    result = {}
    for item in value:
        require(isinstance(item, dict), f"{label}: expected object records")
        key = item.get("id")
        require(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", key),
                f"{label}: invalid ID")
        require(key not in result, f"{label}: duplicate ID {key}")
        result[key] = item
    return result


def names(value, label, allowed=None, nonempty=True):
    require(isinstance(value, list) and (value or not nonempty), f"{label}: expected a list")
    require(all(words(item) for item in value), f"{label}: expected nonempty strings")
    require(len(value) == len(set(value)), f"{label}: duplicate entries")
    if allowed is not None:
        require(set(value) <= set(allowed), f"{label}: unknown entries")
    return value


def actual_file(base, value):
    require(words(value) and not Path(value).is_absolute(), "Expected a project-relative file path")
    path = (base / value).resolve()
    require(path.is_relative_to(base), f"File escapes the project: {value}")
    require(path.is_file() and path.stat().st_size > 0, f"Missing or empty file: {value}")
    return path


def frame_ranges(value, label):
    require(isinstance(value, list) and value, f"{label}: expected nonempty frame ranges")
    for span in value:
        require(isinstance(span, list) and len(span) == 2
                and all(type(frame) is int for frame in span) and 0 <= span[0] < span[1],
                f"{label}: use nonnegative, end-exclusive integer frame ranges")
    return value


def covers(required, inspected):
    for first, last in required:
        cursor = first
        for start, end in sorted(inspected):
            if start > cursor:
                break
            if end > cursor:
                cursor = end
            if cursor >= last:
                break
        if cursor < last:
            return False
    return True


class Acceptance:
    def __init__(self, manifest):
        self.path = Path(manifest).resolve()
        self.base = self.path.parent
        self.data = json.loads(self.path.read_text(encoding="utf-8-sig"))
        data = self.data
        require(isinstance(data, dict), "Manifest must be an object")
        require(type(data.get("schema_version")) is int and data["schema_version"] == 1,
                "Unsupported acceptance schema")
        require(words(data.get("stage")), "The requested deliverable stage is required")
        names(data.get("request_files"), "request_files")
        self.requirements = records(data.get("requirements"), "requirements", True)
        self.artifacts = records(data.get("artifacts"), "artifacts", True)
        self.reviews = records(data.get("reviews"), "reviews", True)
        self.issues = records(data.get("issues"), "issues")
        for path in data["request_files"]:
            actual_file(self.base, path)
        for key, requirement in self.requirements.items():
            require(words(requirement.get("text")) and words(requirement.get("acceptance")),
                    f"{key}: requirement text and acceptance criteria are required")
            names(requirement.get("checks"), f"{key}/checks", METHODS)
            if "frame_ranges" in requirement:
                frame_ranges(requirement["frame_ranges"], f"{key}/frame_ranges")
        for key, artifact in self.artifacts.items():
            file = actual_file(self.base, artifact.get("path"))
            require(file != self.path, f"{key}: the mutable acceptance record cannot be its own evidence")
        for key, review in self.reviews.items():
            require(review.get("method") in METHODS, f"{key}: unknown review method")
            require(review.get("status") in {"pending", "revise", "pass"}, f"{key}: invalid review status")
            names(review.get("requirement_ids"), f"{key}/requirement_ids", self.requirements)
            names(review.get("artifact_ids"), f"{key}/artifact_ids", self.artifacts)
            names(review.get("issue_ids", []), f"{key}/issue_ids", self.issues, False)
            if "frame_ranges" in review:
                frame_ranges(review["frame_ranges"], f"{key}/frame_ranges")
            require(isinstance(review.get("observations", []), list)
                    and all(words(item) for item in review.get("observations", [])),
                    f"{key}: observations must be a list of nonempty strings")
        for key, issue in self.issues.items():
            require(words(issue.get("description")), f"{key}: issue description is required")
            require(issue.get("state") in {"open", "resolved"}, f"{key}: invalid issue state")
            names(issue.get("requirement_ids"), f"{key}/requirement_ids", self.requirements)
            names(issue.get("checks"), f"{key}/checks", METHODS)
            names(issue.get("artifact_ids"), f"{key}/artifact_ids", self.artifacts)
            if "frame_ranges" in issue:
                frame_ranges(issue["frame_ranges"], f"{key}/frame_ranges")
            if issue["state"] == "resolved":
                names(issue.get("resolution_review_ids"), f"{key}/resolution_review_ids", self.reviews)

    def identity(self, value, cache):
        file = actual_file(self.base, value)
        if file not in cache:
            cache[file] = sha256(file)
        return {"path": value, "sha256": cache[file]}

    def fingerprint(self, review_id):
        # Independent operations use the current manifest, even on a reused object.
        return Acceptance(self.path)._fingerprint(review_id, {})

    def _fingerprint(self, review_id, cache):
        require(review_id in self.reviews, f"Unknown review ID: {review_id}")
        review = self.reviews[review_id]
        payload = {
            "schema_version": self.data["schema_version"], "stage": self.data["stage"],
            "requests": [self.identity(path, cache) for path in self.data["request_files"]],
            "review_id": review_id, "method": review["method"],
            "frame_ranges": review.get("frame_ranges"),
            "requirements": [self.requirements[key] for key in sorted(review["requirement_ids"])],
            "artifacts": [{"id": key, **self.identity(self.artifacts[key]["path"], cache)}
                          for key in sorted(review["artifact_ids"])],
            "issues": [{field: self.issues[key].get(field) for field in
                        ("id", "description", "requirement_ids", "checks", "artifact_ids", "frame_ranges")}
                       for key in sorted(review.get("issue_ids", []))],
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def check(self):
        return Acceptance(self.path)._check()

    def _check(self):
        errors, current = [], set()
        cache = {}
        for key, review in self.reviews.items():
            if review["status"] != "pass":
                errors.append(f"{key}: review is {review['status']}")
            elif not review.get("observations"):
                errors.append(f"{key}: a pass needs actual observations")
            elif review.get("fingerprint") != self._fingerprint(key, cache):
                errors.append(f"{key}: review is stale or has no matching input fingerprint")
            else:
                current.add(key)
        for key, requirement in self.requirements.items():
            covered = {self.reviews[item]["method"] for item in current
                       if key in self.reviews[item]["requirement_ids"]}
            for method in requirement["checks"]:
                if method not in covered:
                    errors.append(f"{key}: missing current {method} review")
                elif "frame_ranges" in requirement:
                    inspected = [span for item in current if self.reviews[item]["method"] == method
                                 and key in self.reviews[item]["requirement_ids"]
                                 for span in self.reviews[item].get("frame_ranges", [])]
                    if not covers(requirement["frame_ranges"], inspected):
                        errors.append(f"{key}: incomplete current {method} frame coverage")
        for key, issue in self.issues.items():
            if issue["state"] != "resolved":
                errors.append(f"{key}: material issue remains open")
                continue
            closing = [self.reviews[item] for item in issue["resolution_review_ids"]
                       if item in current and key in self.reviews[item].get("issue_ids", [])
                       and set(issue["requirement_ids"]) <= set(self.reviews[item]["requirement_ids"])
                       and set(issue["artifact_ids"]) <= set(self.reviews[item]["artifact_ids"])]
            for method in issue["checks"]:
                matching = [review for review in closing if review["method"] == method]
                if not matching:
                    errors.append(f"{key}: resolution lacks a current {method} retest of its required artifacts")
                elif "frame_ranges" in issue and not covers(issue["frame_ranges"],
                        [span for review in matching for span in review.get("frame_ranges", [])]):
                    errors.append(f"{key}: incomplete {method} retest frame coverage")
        return {
            "stage": self.data["stage"], "recorded_acceptance_current": not errors,
            "requirements": len(self.requirements), "current_reviews": len(current), "errors": errors,
            "requirements_with_frame_scope": sum("frame_ranges" in item for item in self.requirements.values()),
            "artistic_quality": "not certified; actual appropriate visual/audio/native review is required",
            "request_completeness": "not inferred; compare the requirement list with the original request",
        }


def check(manifest):
    try:
        return Acceptance(manifest)._check()
    except (GateError, OSError, ValueError, TypeError, KeyError) as error:
        return {"recorded_acceptance_current": False, "errors": [str(error)],
                "artistic_quality": "not certified", "request_completeness": "not inferred"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    fingerprint = commands.add_parser("fingerprint", help="Calculate input identity; never writes a review")
    fingerprint.add_argument("manifest", type=Path)
    fingerprint.add_argument("--review", required=True)
    checker = commands.add_parser("check", help="Check declared acceptance records, not artistic quality")
    checker.add_argument("manifest", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        report = check(args.manifest)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["recorded_acceptance_current"] else 2
    try:
        result = Acceptance(args.manifest).fingerprint(args.review)
    except (GateError, OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, str(error) + "\n")
    print(json.dumps({"review_id": args.review, "fingerprint": result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
