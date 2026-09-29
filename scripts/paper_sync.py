#!/usr/bin/env python3
"""Weekly paper check for the MINDS Lab website.

What it does (run by .github/workflows/paper-sync.yml, results arrive as a pull request):
  1. Lists KyuJung Jun's works from OpenAlex (by ORCID) and arXiv (by name).
  2. Adds works that are not yet in src/data/papers.bib (BibTeX fetched from doi.org).
  3. If a new journal article has the same title as an arXiv-only entry, updates that entry
     (journal, year, DOI) instead of adding a duplicate. If an entry's DOI matches but the
     published title differs, replaces the title with the published one.
  4. Writes one news item per paper published within the last N days (default 180) that does
     not have a news item yet. News items are linked to papers by the `paper:` field.
  5. Writes a summary to pr-body.md for the pull request.

Nothing is merged automatically: review the pull request, edit if needed, and merge.

Local run:  python3 scripts/paper_sync.py --since-days 180 --dry-run
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ORCID = "0000-0003-1974-028X"
ARXIV_NAME = "KyuJung Jun"
PI_LAST, PI_FIRST = "Jun", "KyuJung"
MAILTO = "kyujung@korea.ac.kr"  # OpenAlex asks for a contact address in the polite pool

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "src/data/papers.bib"
NEWS = ROOT / "src/content/news"
UA = f"minds-lab-paper-sync (mailto:{MAILTO})"


# ---------------------------------------------------------------- helpers
def http_get(url: str, accept: str = "application/json", timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def norm_title(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "")
    t = re.sub(r"<[^>]+>|[{}$\\]", "", t)
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def norm_doi(d: str | None) -> str:
    if not d:
        return ""
    d = d.strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


def slugify(t: str, n: int = 6) -> str:
    words = re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", t).lower())
    return "-".join(words[:n]) or "paper"


# ---------------------------------------------------------------- local state
def read_bib() -> tuple[str, list[dict]]:
    text = BIB.read_text(encoding="utf-8")
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", text, re.S):
        body = m.group(3)

        def field(name: str) -> str:
            f = re.search(rf"(?im)^\s*{name}\s*=\s*\{{(.*?)\}}\s*,?\s*$", body, re.S)
            return re.sub(r"[{}]", "", f.group(1)).strip() if f else ""

        entries.append({
            "key": m.group(2), "start": m.start(), "end": m.end(),
            "doi": norm_doi(field("doi")), "title": field("title"),
            "journal": field("journal"), "arxiv": field("arxiv") or field("eprint"),
        })
    return text, entries


def news_papers() -> set[str]:
    linked = set()
    for f in NEWS.glob("*.md"):
        m = re.search(r"(?m)^paper:\s*['\"]?([^'\"\n]+)", f.read_text(encoding="utf-8"))
        if m:
            linked.add(norm_doi(m.group(1)))
    return linked


# ---------------------------------------------------------------- remote sources
def openalex_works(years: int = 2) -> list[dict]:
    since = (dt.date.today() - dt.timedelta(days=365 * years)).isoformat()
    params = {
        "filter": f"author.orcid:{ORCID},from_publication_date:{since}",
        "per-page": "100", "sort": "publication_date:desc", "mailto": MAILTO,
    }
    data = json.loads(http_get("https://api.openalex.org/works?" + urllib.parse.urlencode(params)))
    out = []
    for w in data.get("results", []):
        src = ((w.get("primary_location") or {}).get("source") or {})
        doi = norm_doi(w.get("doi"))
        journal = src.get("display_name") or ""
        is_arxiv = "arxiv" in doi or "arxiv" in journal.lower()
        out.append({
            "title": w.get("title") or w.get("display_name") or "",
            "doi": doi,
            "date": w.get("publication_date") or "",
            "journal": "arXiv" if is_arxiv else journal,
            "authors": [a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author")],
            "arxiv": doi.split("arxiv.")[-1] if "arxiv." in doi else "",
            "type": w.get("type") or "",
        })
    return out


def arxiv_works(n: int = 25) -> list[dict]:
    q = urllib.parse.quote(f'au:"{ARXIV_NAME}"')
    xml = http_get(f"https://export.arxiv.org/api/query?search_query={q}&sortBy=submittedDate&sortOrder=descending&max_results={n}",
                   accept="application/atom+xml")
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    out = []
    for e in ET.fromstring(xml).findall("a:entry", ns):
        aid = e.findtext("a:id", "", ns).rsplit("/abs/", 1)[-1]
        aid = re.sub(r"v\d+$", "", aid)
        authors = [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)]
        # the name query can match other people; keep only entries with this exact author name
        if not any(re.sub(r"\s+", "", x).lower() == re.sub(r"\s+", "", ARXIV_NAME).lower() for x in authors):
            continue
        out.append({
            "title": re.sub(r"\s+", " ", e.findtext("a:title", "", ns)).strip(),
            "doi": f"10.48550/arxiv.{aid}".lower(),
            "date": e.findtext("a:published", "", ns)[:10],
            "journal": "arXiv", "authors": authors, "arxiv": aid, "type": "preprint",
        })
    return out


def bibtex_for(work: dict) -> str:
    """BibTeX from doi.org content negotiation; falls back to one built from the metadata."""
    key = work["doi"] or f"{slugify(work['title'], 3)}{work['date'][:4]}"
    raw = ""
    if work["doi"] and "arxiv" not in work["doi"]:
        try:
            raw = http_get(f"https://doi.org/{work['doi']}", accept="application/x-bibtex; charset=utf-8").strip()
        except Exception as ex:  # noqa: BLE001
            print(f"  doi.org failed for {work['doi']}: {ex}", file=sys.stderr)
    if raw.startswith("@"):
        raw = re.sub(r"^@(\w+)\{[^,]*,", lambda m: "@" + m.group(1).lower() + "{" + key + ",", raw, count=1)
        raw = re.sub(r",\s*(\w+)\s*=", r",\n  \1 =", raw)
        raw = re.sub(r"\s*\}\s*$", "\n}", raw)
    else:
        def last_first(n: str) -> str:
            parts = n.split()
            return f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else n
        fields = [
            ("author", " and ".join(last_first(a) for a in work["authors"])),
            ("title", work["title"]),
            ("journal", work["journal"]),
            ("year", work["date"][:4]),
        ]
        if work["doi"]:
            fields.append(("doi", work["doi"]))
        if work["arxiv"]:
            fields.append(("arxiv", work["arxiv"]))
        raw = "@article{" + key + ",\n" + ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v) + "\n}"
    if work["arxiv"] and "arxiv =" not in raw:
        raw = raw[:-1].rstrip() + f",\n  arxiv = {{{work['arxiv']}}}\n}}"
    return raw


# ---------------------------------------------------------------- news
def short_authors(authors: list[str]) -> str:
    def is_pi(a: str) -> bool:
        return PI_LAST.lower() in a.lower() and PI_FIRST.lower().replace("-", "") in a.lower().replace("-", "").replace(" ", "")
    if len(authors) <= 4:
        return ", ".join(authors)
    shown = authors[:3]
    if not any(is_pi(a) for a in shown):
        shown.append("…")
        shown.append(next((a for a in authors if is_pi(a)), ""))
    return ", ".join([a for a in shown if a]) + ", et al."


def write_news(work: dict, dry: bool) -> Path:
    date = work["date"] or dt.date.today().isoformat()
    path = NEWS / f"{date}-paper-{slugify(work['title'])}.md"
    link = f"https://arxiv.org/abs/{work['arxiv']}" if work["journal"] == "arXiv" else f"https://doi.org/{work['doi']}"
    if work["journal"] == "arXiv":
        lead = f'New preprint: "{work["title"]}"'
        where = f"[arXiv:{work['arxiv']}]({link})"
    else:
        lead = f'New paper in *{work["journal"]}*: "{work["title"]}"'
        where = f"[DOI]({link})"
    body = f"---\ndate: {date}\npaper: \"{work['doi']}\"\n---\n\n{lead} ({short_authors(work['authors'])}). {where}\n"
    if not dry:
        path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since-days", type=int, default=int(os.environ.get("SINCE_DAYS", "180")),
                    help="write news only for papers published within this many days")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    text, entries = read_bib()
    by_doi = {e["doi"]: e for e in entries if e["doi"]}
    by_title = {norm_title(e["title"]): e for e in entries if e["title"]}
    linked = news_papers()
    cutoff = (dt.date.today() - dt.timedelta(days=args.since_days)).isoformat()

    works: list[dict] = []
    for fetch in (openalex_works, arxiv_works):
        try:
            works += fetch()
        except Exception as ex:  # noqa: BLE001
            print(f"{fetch.__name__} failed: {ex}", file=sys.stderr)

    # de-duplicate: prefer journal versions over preprints with the same title
    seen: dict[str, dict] = {}
    for w in sorted(works, key=lambda w: (w["journal"] == "arXiv", w["date"])):
        t = norm_title(w["title"])
        if t and t not in seen:
            seen[t] = w
        elif t in seen and w["journal"] == "arXiv" and not seen[t]["arxiv"]:
            seen[t]["arxiv"] = w["arxiv"]

    added, updated, retitled, news = [], [], [], []
    new_text = text
    for t, w in seen.items():
        if w["type"] in ("peer-review", "erratum", "paratext", "dataset"):
            continue
        existing = by_doi.get(w["doi"]) or by_title.get(t)
        if existing is None:
            new_text = new_text.rstrip() + "\n\n" + bibtex_for(w) + "\n"
            added.append(w)
        elif existing["doi"] == w["doi"] and w["journal"] != "arXiv" and w["title"] and norm_title(existing["title"]) != t:
            # same DOI but the published title differs (e.g. changed during review): use the journal title
            seg_start = new_text.find("{" + existing["key"] + ",")
            seg_end = new_text.find("\n}", seg_start) + 2
            entry = new_text[seg_start:seg_end]
            upd = re.sub(r"(?im)^(\s*)title\s*=.*$", lambda m: f"{m.group(1)}title = {{{w['title']}}},", entry, count=1)
            new_text = new_text[:seg_start] + upd + new_text[seg_end:]
            retitled.append((existing["title"], w))
        elif w["journal"] != "arXiv" and existing["journal"].lower() in ("arxiv", "chemrxiv", "") and existing["doi"] != w["doi"]:
            # journal version of an entry that is still a preprint on the site
            seg = new_text[new_text.find("{" + existing["key"] + ","):]
            end = seg.find("\n}") + 2
            entry = seg[:end]
            upd = entry
            for k, v in (("journal", w["journal"]), ("doi", w["doi"]), ("year", w["date"][:4])):
                if re.search(rf"(?im)^\s*{k}\s*=", upd):
                    upd = re.sub(rf"(?im)^(\s*){k}\s*=.*$", lambda m, k=k, v=v: f"{m.group(1)}{k} = {{{v}}},", upd, count=1)
                else:
                    upd = upd.replace(",", f",\n{k} = {{{v}}},", 1)
            if existing["arxiv"] == "" and "arxiv." in existing["doi"]:
                upd = upd.replace(",", f",\narxiv = {{{existing['doi'].split('arxiv.')[-1]}}},", 1)
            new_text = new_text.replace(entry, upd, 1)
            updated.append((existing["key"], w))
        if w["date"] >= cutoff and w["doi"] not in linked and (existing is None or existing["doi"] == w["doi"] or w["journal"] != "arXiv"):
            news.append(write_news(w, args.dry_run))
            linked.add(w["doi"])

    if not args.dry_run and new_text != text:
        BIB.write_text(new_text, encoding="utf-8")

    lines = ["Automatic weekly check of OpenAlex (ORCID " + ORCID + ") and arXiv.", ""]
    if added:
        lines += ["### Added to papers.bib"] + [f"- {w['title']} — *{w['journal']}* ({w['date']}) {w['doi']}" for w in added] + [""]
    if updated:
        lines += ["### Preprints updated to their journal version"] + [f"- `{k}` → *{w['journal']}* {w['doi']}" for k, w in updated] + [""]
    if retitled:
        lines += ["### Titles updated to the published title"] + [f"- {old} → **{w['title']}** ({w['journal']})" for old, w in retitled] + [""]
    if news:
        lines += ["### News items written"] + [f"- `{p.relative_to(ROOT)}`" for p in news] + [""]
    lines += [
        "Before merging, check:",
        "- the author is really KyuJung Jun (other people share the name);",
        "- no paper appears twice (preprint and journal version);",
        "- set `selected = {true}` for papers that should appear under Selected;",
        "- edit or delete any news item.",
    ]
    (ROOT / "pr-body.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            fh.write(f"changes={'true' if (added or updated or retitled or news) else 'false'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
