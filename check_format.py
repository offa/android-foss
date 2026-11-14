"""Verify that the app entries in README.md match the formats

Prints one "<file>:<line>: <message>" per finding and exits with 1 if any
finding was produced, 2 if the file cannot be read or no known section was
recognized, and 0 otherwise.
"""

import argparse
import re
import sys

SECTIONS = (
    "App Store",
    "Apps",
    "Games",
    "Rooting and Recovery",
    "Tools",
    "Tutorials and Guides",
    "Getting more …",
)

# Sections that are plain link lists rather than app entries: link targets
# may be relative (e.g. "doc/*.md") and one line may carry several links.
LINK_LIST_SECTIONS = ("Tutorials and Guides", "Getting more …")

HEADING_RE = re.compile(r"^## – (.+?) –\s*$")
CATEGORY_RE = re.compile(r"^### • (.+?)\s*$")
SEPARATOR_RE = re.compile(r"^\s*-{3,}\s*$")

# * [**Name**](URL)  +  everything that follows (store badges / garbage)
ENTRY_HEAD_RE = re.compile(r"^\s*\* \[\*\*(.+?)\*\*\]\(([^)]*)\)(.*)$")

# An extra link on a link-list entry line:  / [**Name**](URL)
SECOND_LINK_RE = re.compile(r"^ / \[\*\*(.+?)\*\*\]\(([^)]*)\)(.*)$")

# The only acceptable badge markup (without leading space, matched from "<sup>")
CANON_BADGE_RE = re.compile(
    r"^<sup>\*\*\[\[(F-Droid|IzzyOnDroid)\]\(([^)]*)\)\]\*\*</sup>"
)

LINK_RE = re.compile(r"\[([^\[\]]*)\]\(([^)]*)\)")
STORE_URL_RE = {
    "F-Droid": re.compile(r"^https://f-droid\.org/packages/(.+)$"),
    "IzzyOnDroid": re.compile(r"^https://apt\.izzysoft\.de/packages/(.+)$"),
}
STORE_URL_HINT = {
    "F-Droid": "https://f-droid.org/packages/<app-id>",
    "IzzyOnDroid": "https://apt.izzysoft.de/packages/<app-id>",
}
APP_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def check_store_url(lineno, ctx, name, store, url):
    """Return findings for the URL of a single store badge."""
    m = STORE_URL_RE[store].match(url)
    if m is None:
        return [
            (
                lineno,
                (
                    f"{ctx} [{name}]: invalid {store} URL '{url}' "
                    f"(must be exactly {STORE_URL_HINT[store]})"
                ),
            )
        ]
    app_id = m.group(1)
    if not APP_ID_RE.match(app_id):
        return [
            (
                lineno,
                (
                    f"{ctx} [{name}]: invalid app id '{app_id}' in {store} link "
                    "(only letters, digits, '.', '_' and '-' are allowed)"
                ),
            )
        ]
    return []


def check_entry(lineno, line, section, ctx):
    """Validate one entry line. Returns (findings, entry name or None)."""
    findings = []
    m = ENTRY_HEAD_RE.match(line)
    if m is None:
        # main() only passes lines matching r"^\s*\* " to check_entry().
        rest = re.match(r"^\s*\* (.*)$", line).group(1).strip()
        if rest.startswith("[**"):
            findings.append(
                (
                    lineno,
                    f"{ctx}: malformed entry (expected '[**Name**](URL)'), got: {rest[:60]}",
                )
            )
        else:
            findings.append(
                (
                    lineno,
                    f"{ctx}: entry must start with '[**Name**](URL)', got: {rest[:60]}",
                )
            )
        return findings, None

    name, url, tail = m.groups()
    if not name.strip():
        findings.append((lineno, f"{ctx}: empty entry name"))
    if section in LINK_LIST_SECTIONS:
        if not url:
            findings.append((lineno, f"{ctx} [{name}]: empty link target"))
    elif not re.match(r"^https?://", url):
        findings.append(
            (
                lineno,
                f"{ctx} [{name}]: project URL must be an absolute http(s) URL, got: '{url}'",
            )
        )

    # Link lists may carry extra " / [**Name**](URL)" links on one line.
    if section in LINK_LIST_SECTIONS:
        while True:
            sm = SECOND_LINK_RE.match(tail)
            if sm is None:
                break
            sub_name, sub_url, tail = sm.groups()
            if not sub_name.strip():
                findings.append(
                    (lineno, f"{ctx} [{name}]: extra link has an empty name")
                )
            if not sub_url:
                findings.append(
                    (lineno, f"{ctx} [{name}]: extra link has an empty target")
                )

    pos = 0
    stores = []
    while True:
        i = tail.find("<sup>", pos)
        if i == -1:
            break

        gap = tail[pos:i]
        where = "before the store badges" if pos == 0 else "between store badges"
        if gap.strip():
            findings.append(
                (
                    lineno,
                    f"{ctx} [{name}]: unexpected text {where}: '{gap.strip()[:60]}'",
                )
            )
        elif gap != " ":
            findings.append(
                (
                    lineno,
                    f"{ctx} [{name}]: expected exactly one space {where} (got {len(gap)})",
                )
            )

        cm = CANON_BADGE_RE.match(tail[i:])
        if cm:
            store, badge_url = cm.groups()
            findings.extend(check_store_url(lineno, ctx, name, store, badge_url))
            stores.append(store)
            pos = i + cm.end()
            continue

        # Non-canonical badge: salvage the store name/URL for a precise message.
        inner = tail[i + len("<sup>") :]
        close = inner.find("</sup>")
        closed = close != -1
        content = inner[:close] if closed else inner
        lm = LINK_RE.search(content)
        store = lm.group(1) if lm else None
        if store in ("F-Droid", "IzzyOnDroid"):
            if not closed:
                findings.append(
                    (
                        lineno,
                        f"{ctx} [{name}]: {store} badge is not closed (missing '</sup>')",
                    )
                )
            elif not re.fullmatch(r"\*\*\[\[.*\]\(.*\)\]\*\*", content):
                findings.append(
                    (
                        lineno,
                        (
                            f"{ctx} [{name}]: non-canonical {store} badge markup: '{tail[i : i + 70]}' "
                            f"(expected '<sup>**[[{store}](URL)]**</sup>')"
                        ),
                    )
                )
            if lm:
                findings.extend(check_store_url(lineno, ctx, name, store, lm.group(2)))
            stores.append(store)
        elif store is None:
            findings.append(
                (
                    lineno,
                    f"{ctx} [{name}]: unparseable store badge: '{tail[i : i + 70]}'",
                )
            )
        else:
            findings.append(
                (
                    lineno,
                    (
                        f"{ctx} [{name}]: store badge '{store}' not allowed "
                        "(only 'F-Droid' and 'IzzyOnDroid' may be linked)"
                    ),
                )
            )
        if closed:
            pos = i + len("<sup>") + close + len("</sup>")
        else:
            pos = len(tail)

    leftover = tail[pos:]
    if leftover.strip():
        findings.append(
            (
                lineno,
                f"{ctx} [{name}]: unexpected content after store badges: '{leftover.strip()[:60]}'",
            )
        )
    elif leftover:
        findings.append((lineno, f"{ctx} [{name}]: trailing whitespace on entry line"))

    allowed = [s for s in ("F-Droid", "IzzyOnDroid") if s in stores]
    if stores and stores != allowed:
        if len(stores) != len(set(stores)):
            msg = f"duplicate store badge(s), found: {', '.join(stores)}"
        else:
            msg = f"store badges must appear with F-Droid before IzzyOnDroid, found: {', '.join(stores)}"
        findings.append((lineno, f"{ctx} [{name}]: {msg}"))

    return findings, name


def check_sort(items, ctx):
    """Return findings for every alphabetical inversion among top-level entries."""
    findings = []
    for idx in range(1, len(items)):
        prev_line, prev_name = items[idx - 1]
        this_line, this_name = items[idx]
        if this_name.lower() < prev_name.lower():
            findings.append(
                (
                    this_line,
                    (
                        f"{ctx}: entries not sorted alphabetically — '{this_name}' comes after '{prev_name}' "
                        f"(line {prev_line})"
                    ),
                )
            )
    return findings


def main():
    parser = argparse.ArgumentParser(
        description="Verify that the app entries in README.md match the formats from CONTRIBUTING.md.",
    )
    parser.add_argument(
        "readme",
        nargs="?",
        default="README.md",
        help="path to the README (default: README.md)",
    )
    parser.add_argument(
        "--no-sort", action="store_true", help="skip the alphabetical-order check"
    )
    args = parser.parse_args()

    try:
        with open(args.readme, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        print(f"error: cannot read {args.readme}: {exc}", file=sys.stderr)
        return 2

    section = None
    category = None
    items = []  # (lineno, name) of the top-level entries of the current category
    findings = []
    entries_checked = 0
    sections_found = 0

    def ctx():
        return section if category is None else f"{section} > {category}"

    def flush():
        if not args.no_sort and items:
            findings.extend(check_sort(items, ctx()))

    for lineno, line in enumerate(lines, 1):
        hm = HEADING_RE.match(line)
        if hm:
            flush()
            heading = hm.group(1)
            if heading in SECTIONS:
                section = heading
                sections_found += 1
            else:
                section = None
                findings.append(
                    (
                        lineno,
                        f"unknown section '{heading}' (expected one of: {', '.join(SECTIONS)})",
                    )
                )
            category = None
            items = []
            continue
        cm = CATEGORY_RE.match(line)
        if cm and section is not None:
            flush()
            category = cm.group(1)
            items = []
            continue
        if section is None:
            continue
        if not line.strip() or SEPARATOR_RE.match(line):
            continue
        if re.match(r"^\s*\* ", line):
            top_level = line.startswith("*")
            entry_findings, entry_name = check_entry(lineno, line, section, ctx())
            findings.extend(entry_findings)
            entries_checked += 1
            if top_level and entry_name:
                items.append((lineno, entry_name))
        else:
            stripped = line.strip()
            if "<sup>" in line:
                findings.append(
                    (
                        lineno,
                        (
                            f"{ctx()}: store badge outside an entry line — entries must be "
                            f"'* [**Name**](URL) <sup>…</sup>', got: '{stripped[:60]}'"
                        ),
                    )
                )
            else:
                findings.append(
                    (
                        lineno,
                        f"{ctx()}: unexpected line in app section: '{stripped[:60]}'",
                    )
                )
    flush()

    if findings:
        for ln, msg in sorted(findings):
            print(f"{args.readme}:{ln}: {msg}")
        print(f"\n{len(findings)} issue(s) found ({entries_checked} entries checked).")
        return 1

    if sections_found == 0:
        print(
            f"error: no known section found in {args.readme} "
            f"(expected a heading like '## – {SECTIONS[0]} –')",
            file=sys.stderr,
        )
        return 2

    print(
        f"{args.readme}: OK — {entries_checked} entries match the CONTRIBUTING.md format."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
