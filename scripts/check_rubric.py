"""Check the rubric's worked examples and generated reference."""

import argparse
import json
import sys
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "skills" / "is-local-first"
DATA = SKILL / "assets" / "rubric.json"
REFERENCE = SKILL / "references" / "rubric.md"

sys.path.insert(0, str(SKILL / "scripts"))
from rubric import classify


def check_examples(rubric):
    expected_categories = {
        "Local-first", "Not local-first yet", "Marketed as local-first",
        "Offline-first", "Sync engine",
    }
    if {row["expected"] for row in rubric["examples"]} != expected_categories:
        raise ValueError("Worked examples must cover all five categories")
    calibration = rubric["calibration"]
    if len(calibration) != len(expected_categories) or {
        row["expected"] for row in calibration
    } != expected_categories:
        raise ValueError("Use one Evolu calibration tool per category")
    for example in rubric["examples"]:
        ratings = dict.fromkeys(rubric["criteria"], "meets") | example["overrides"]
        result = classify(
            rubric, ratings, example["claim"], example["maturity"], example["version"]
        )
        if result != example["expected"]:
            raise ValueError(
                f'{example["name"]}: expected {example["expected"]}, got {result}'
            )


def render(rubric):
    source = rubric["source"]
    upstream = f'{source["repository"]}/blob/{source["commit"]}'
    lines = [
        "<!-- Generated from assets/rubric.json by scripts/check_rubric.py --write. -->",
        "# Local-first rubric",
        "",
        f'Based on [Evolu’s comparison]({source["comparisonUrl"]}) at commit',
        f'`{source["commit"]}` ({source["commitDate"]}).',
        f'Adopted on {source["adoptedOn"]}. Evolu checked the comparison on '
        f'{source["comparisonCheckedOn"]}.',
        "",
        "The definitions below paraphrase Evolu’s criteria and rating rules.",
        f'[Rating rules]({upstream}/{source["criteriaPath"]}) · '
        f'[Category code]({upstream}/{source["categoryPath"]}) · '
        f'[Comparison data]({upstream}/{source["dataPath"]}) · '
        f'[Evolu repository license ({source["license"]})]({upstream}/{source["licensePath"]})',
        "",
        "## Criteria",
        "",
    ]
    for number, (criterion, entry) in enumerate(rubric["criteria"].items(), 1):
        lines.extend([
            f'### {number}. {entry["title"]} (`{criterion}`)',
            "",
            entry["definition"],
            "",
            entry["guidance"],
            "",
        ])

    lines.extend(["## Ratings", ""])
    for value, entry in rubric["statuses"].items():
        outcome = "Passes." if entry["passes"] else "Fails the all-criteria check."
        restriction = (
            f' Allowed only for `{entry["onlyCriterion"]}`.'
            if "onlyCriterion" in entry else ""
        )
        lines.append(
            f'- {entry["symbol"]} `{value}`. {entry["description"]} {outcome}{restriction}'
        )

    lines.extend(["", "## Evidence, claim, and maturity", ""])
    lines.extend(f"- {rule}" for rule in rubric["evidenceRules"])
    labels = ", ".join(f"`{label}`" for label in rubric["maturityLabels"])
    lines.extend(["", f"Maturity labels are {labels}.", "", "## Category", ""])

    rules = rubric["categoryRules"]
    unfinished = rules["unfinished"]
    labels = ", ".join(f"`{label}`" for label in unfinished["maturityLabels"])
    release = ".".join(map(str, unfinished["prereleaseOf"]))
    all_passing = rules["allPassing"]
    lines.append(
        f'1. If every criterion passes, assign **{all_passing["finished"]}**. '
        f'Assign **{all_passing["unfinished"]}** when maturity is one of {labels}, '
        f'or the release has major version {unfinished["majorVersion"]} or is a '
        f'prerelease of {release}. A missing version uses the recorded maturity.'
    )
    for number, (rule_name, condition) in enumerate([
        ("withClaim", "the project claims local-first"),
        ("withoutClaim", "the project makes no local-first claim"),
    ], 2):
        rule = rules[rule_name]
        required = ", ".join(
            f"`{criterion}` in " + " or ".join(f"`{value}`" for value in values)
            for criterion, values in rule["required"].items()
        )
        lines.append(
            f'{number}. Otherwise, if {condition}, assign **{rule["matches"]}** '
            f'when all of these checks pass ({required}). Otherwise assign **{rule["otherwise"]}**.'
        )

    lines.extend([
        "", "## Worked examples", "",
        "Criteria start as `meets` except for the overrides shown.",
        "",
        "| Example | Claim | Maturity | Version | Overrides | Category |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for row in rubric["examples"]:
        overrides = ", ".join(f"`{key}={value}`" for key, value in row["overrides"].items())
        claim = "Yes" if row["claim"] else "No"
        lines.append(
            f'| {row["name"]} | {claim} | `{row["maturity"]}` | '
            f'{row["version"] or "—"} | {overrides or "—"} | {row["expected"]} |'
        )

    lines.extend([
        "", "## Applications", "",
        *(f"- {rule}" for rule in rubric["applicationRules"]),
        "", "## Calibration targets", "",
        "These are expected categories from the pinned Evolu comparison.",
        "",
        "| Tool | Version in the source | Expected category |",
        "| --- | --- | --- |",
    ])
    lines.extend(
        f'| {row["name"]} | {row["version"] or "—"} | {row["expected"]} |'
        for row in rubric["calibration"]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the Markdown reference")
    args = parser.parse_args()

    rubric = json.loads(DATA.read_text(encoding="utf-8"))
    check_examples(rubric)
    expected = render(rubric)
    if args.write:
        REFERENCE.write_text(expected, encoding="utf-8")
    elif not REFERENCE.exists() or REFERENCE.read_bytes() != expected.encode("utf-8"):
        parser.exit(1, "Rubric reference differs. Run python scripts/check_rubric.py --write.\n")
    print(f'Rubric reference and {len(rubric["examples"])} worked examples match.')


if __name__ == "__main__":
    main()
