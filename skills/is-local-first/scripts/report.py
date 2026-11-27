"""Render audits of one project snapshot as a portrait-friendly Markdown report."""

import re

from audit_sources import AuditError, parse_repository, parse_source


WORDS = {
    "meets": "Meets", "partial": "Partial", "misses": "Misses",
    "n/a": "Not applicable", "unclear": "Unclear",
}
KINDS = {"application": "application", "database": "database", "sync-engine": "sync engine"}
SHARED = ("project", "version", "commit", "maturity", "rubricVersion")
MARKUP = re.compile(r"([\\`*_\[\]<>~&])")
LINK_UNSAFE = str.maketrans({"(": "%28", ")": "%29", "<": "%3C", ">": "%3E"})


def inline(text):
    """Return audit text as one line of literal Markdown."""
    return MARKUP.sub(r"\\\1", " ".join(text.split()))


def source_link(url, audit):
    citation = parse_source(url)
    label = citation.file.path[-1]
    if citation.first is not None:
        label += f" L{citation.first}"
        if citation.last != citation.first:
            label += f"-L{citation.last}"
    project = parse_repository(audit["project"]["repository"])
    if citation.file.repository == project and citation.file.commit != audit["commit"]:
        # Documentation that the release tree leaves out comes from another commit.
        label += f" at {citation.file.commit[:12]}"
    return f"[{inline(label)}]({url.translate(LINK_UNSAFE)})"


def fenced(text):
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def render_flow(audit, category, rubric, verified):
    scope = audit["scope"]
    heading = category if verified else f"{category} (provisional)"
    blocks = [
        f"## {heading}",
        " · ".join([
            f"**{inline(scope['dataFlow'])}**", KINDS[scope["kind"]],
            inline(audit["platform"]), inline(audit["syncMode"]),
        ]),
    ]
    if not verified:
        blocks.append("**Not machine-verified.** The citations were not checked against the source.")

    claim = audit["localFirstClaim"]
    if claim is None:
        blocks.append("No local-first claim found in the reviewed primary sources.")
    else:
        text = f"Claims local-first: “{inline(claim['quote'])}”"
        if "translation" in claim:
            text += f" (“{inline(claim['translation'])}”)"
        blocks.append(f"{text} {source_link(claim['source'], audit)}")

    evidence = ["### Evidence"]
    for key, criterion in rubric["criteria"].items():
        entry = audit["criteria"][key]
        status = rubric["statuses"][entry["value"]]
        title = criterion["title"]
        link = source_link(entry["source"], audit)
        blocks.append(
            f"{status['symbol']} **{WORDS[entry['value']]}: {title}.** "
            f"{inline(entry['evidence'])} {link}"
        )
        evidence.append(f"**{title}** · {link}")
        evidence.append(fenced(entry["quote"].replace("\r\n", "\n")))
    return blocks + evidence


def render_report(audits, categories, rubric, verified):
    """Return the report for audits that share one project snapshot."""
    first = audits[0]
    for audit in audits[1:]:
        for field in SHARED:
            if audit[field] != first[field]:
                raise AuditError(f"render one project snapshot at a time: {field} differs")

    version = first["version"]
    title = inline(first["project"]["name"])
    blocks = [f"# {title} {version}" if version else f"# {title}"]
    for audit, category in zip(audits, categories):
        blocks += render_flow(audit, category, rubric, verified)

    source = rubric["source"]
    blocks.append(
        f"Rated against the [Evolu criteria]({source['comparisonUrl']}) · "
        f"rubric `{source['commit'][:12]}` revision {source['revision']}, adopted {source['adoptedOn']}"
    )
    blocks.append(" · ".join([
        f"Version {version}" if version else "No release version",
        first["maturity"],
        f"commit `{first['commit'][:12]}`",
        "static audit",
        "citations machine-verified" if verified else "not machine-verified",
    ]))
    return "\n\n".join(blocks) + "\n"
