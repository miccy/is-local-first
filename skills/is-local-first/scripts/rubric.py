"""Category calculation for the pinned Evolu rubric."""

import re


VERSION = re.compile(r"([0-9]+)\.([0-9]+)(?:\.([0-9]+))?(-.+)?")


def classify(rubric, ratings, claim, maturity, version):
    if ratings.keys() != rubric["criteria"].keys():
        raise ValueError("Expected exactly the eight criterion IDs")
    if maturity not in rubric["maturityLabels"]:
        raise ValueError(f"Unknown maturity {maturity!r}")

    statuses = rubric["statuses"]
    for criterion, rating in ratings.items():
        if rating not in statuses:
            raise ValueError(f"Unknown status {rating!r} for {criterion}")
        if statuses[rating].get("onlyCriterion", criterion) != criterion:
            raise ValueError(f"Status {rating!r} is invalid for {criterion}")

    rules = rubric["categoryRules"]
    unfinished_rule = rules["unfinished"]
    unfinished = maturity in unfinished_rule["maturityLabels"]
    if version is not None:
        match = VERSION.fullmatch(version)
        if match is None:
            raise ValueError(f"Invalid release version {version!r}")
        major, minor, patch = (int(part or 0) for part in match.groups()[:3])
        unfinished |= major == unfinished_rule["majorVersion"] or (
            [major, minor, patch] == unfinished_rule["prereleaseOf"]
            and match[4] is not None
        )

    if all(statuses[rating]["passes"] for rating in ratings.values()):
        return rules["allPassing"]["unfinished" if unfinished else "finished"]
    rule = rules["withClaim" if claim else "withoutClaim"]
    matches = all(
        ratings[criterion] in allowed
        for criterion, allowed in rule["required"].items()
    )
    return rule["matches" if matches else "otherwise"]
