#!/usr/bin/env python3
"""Build the LBoL strategy notebook into a dependency-free static website."""
from __future__ import annotations

from datetime import date, datetime
from urllib.parse import urlsplit, urlunsplit
from html import unescape
from pathlib import Path
from shutil import copytree, rmtree
import json
import re

import mistune
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "dist"
SITE_NAME = "LBoL 攻略ノート"
SITE_DESCRIPTION = "結論だけでなく、判断の理由まで。LBoLの上級者向け個人攻略・考察サイト。"
SECTIONS = {
    "cards": {"label": "カード解説", "singular": "カード", "eyebrow": "CARD LIBRARY", "description": "採用条件、相性、評価が変わる場面まで。カード単位で判断の根拠を残す。"},
    "bosses": {"label": "ボス攻略", "singular": "ボス", "eyebrow": "BOSS FIELD GUIDE", "description": "脅威、準備、立ち回りを整理し、戦闘中の判断につなげる。"},
    "characters": {"label": "キャラ別攻略", "singular": "キャラ", "eyebrow": "CHARACTER NOTES", "description": "キャラクターごとの攻略方針やピック基準。構成は考察を重ねながら育てる。"},
}

markdown = mistune.create_markdown(escape=True, plugins=["table", "strikethrough", "url"])


def localize_article_links(html: str) -> str:
    """Keep CMS-generated root-relative links working in file:// previews too.

    Decap inserts media paths such as /assets/uploads/figure.png, and users
    can link to /cards/example-card/.  A generated article is always two
    directory levels below the published site root.
    """
    def replace(match: re.Match[str]) -> str:
        attribute, raw_url = match.group(1), match.group(2)
        parts = urlsplit(raw_url)
        path = parts.path
        if attribute == "href" and path.endswith("/"):
            path += "index.html"
        new_url = urlunsplit(("", "", "../../" + path.lstrip("/"), parts.query, parts.fragment))
        return f'{attribute}="{new_url}"'

    return re.sub(r'\b(src|href)="(/(?:assets|cards|bosses|characters)/[^"<>]*)"', replace, html)


def normalize_image(raw: str) -> str:
    """Resolve known CMS uploads relative to the published site root."""
    value = str(raw or "").strip()
    if value.startswith("/assets/uploads/"):
        return value.lstrip("/")
    if value.startswith("assets/uploads/"):
        return value
    if value.startswith("https://"):
        return value
    return ""
env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html", "xml"]))


def load_article(path: Path, section: str) -> dict | None:
    raw = path.read_text(encoding="utf-8-sig")
    parts = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", raw, flags=re.S)
    if not parts:
        raise ValueError(f"Missing YAML frontmatter: {path}")
    metadata = yaml.safe_load(parts.group(1)) or {}
    if metadata.get("draft", False):
        return None
    slug = str(metadata.get("slug") or path.stem).strip()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError(f"Invalid slug: {slug} ({path}) — use lowercase ASCII and hyphens")
    if slug != path.stem:
        raise ValueError(
            f"Article slug {slug!r} does not match filename {path.stem!r} ({path}). "
            "Please change the filename or restore the original slug."
        )
    title = str(metadata.get("title") or "").strip()
    if not title:
        raise ValueError(f"Missing title: {path}")
    html = localize_article_links(markdown(parts.group(2)))
    toc = []

    def attach_anchor(match):
        level, inner = match.group(1), match.group(2)
        text = unescape(re.sub(r"<[^>]*>", "", inner)).strip()
        anchor = f"section-{len(toc) + 1}"
        toc.append({"title": text, "anchor": anchor, "level": int(level)})
        return f'<h{level} id="{anchor}">{inner}</h{level}>'

    html = re.sub(r"<h([23])>(.*?)</h\1>", attach_anchor, html, flags=re.S)
    updated = metadata.get("updated") or ""
    if isinstance(updated, (date, datetime)):
        updated = updated.isoformat()
    tags = metadata.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    return {
        "section": section,
        "slug": slug,
        "url": f"/{section}/{slug}/",
        "title": title,
        "summary": str(metadata.get("summary") or ""),
        "tags": list(map(str, tags)),
        "status": str(metadata.get("status") or "検討中"),
        "version": str(metadata.get("version") or ""),
        "updated": str(updated),
        "character": str(metadata.get("character") or ""),
        "rarity": str(metadata.get("rarity") or ""),
        "cost": str(metadata.get("cost") or ""),
        "stage": str(metadata.get("stage") or ""),
        "sample": bool(metadata.get("sample", False)),
        "image": normalize_image(metadata.get("image", "")),
        "image_alt": str(metadata.get("image_alt") or title),
        "html": html,
        "toc": toc,
        "file": str(path.relative_to(ROOT)),
    }


def render(filename: str, outfile: Path, **context):
    outfile.parent.mkdir(parents=True, exist_ok=True)
    html = env.get_template(filename).render(
        site_name=SITE_NAME,
        site_description=SITE_DESCRIPTION,
        root_url="../" * len(outfile.parent.relative_to(OUTPUT).parts) or "./",
        sections=SECTIONS,
        **context,
    )
    outfile.write_text(html, encoding="utf-8")


def main():
    if OUTPUT.exists():
        rmtree(OUTPUT)
    OUTPUT.mkdir()
    copytree(ROOT / "assets", OUTPUT / "assets")
    # The CMS must be part of the published site, not only the source repo.
    copytree(ROOT / "admin", OUTPUT / "admin")
    all_articles = {}
    for section in SECTIONS:
        articles = []
        for path in sorted((ROOT / "content" / section).glob("*.md")):
            if path.name.startswith("_"):
                continue
            article = load_article(path, section)
            if article:
                articles.append(article)
        articles.sort(key=lambda a: (a["sample"], a["title"]))
        all_articles[section] = articles
        for article in articles:
            render("article.html", OUTPUT / section / article["slug"] / "index.html", section=section, current_section=section, article=article, page_title=article["title"])
        render("listing.html", OUTPUT / section / "index.html", section=section, current_section=section, articles=articles, page_title=SECTIONS[section]["label"])
    render("home.html", OUTPUT / "index.html", all_articles=all_articles, latest=[a for group in all_articles.values() for a in group][:4], current_section="home", page_title="トップ")
    (OUTPUT / "search-index.json").write_text(json.dumps([
        {k: a[k] for k in ("section", "url", "title", "summary", "tags", "status", "character", "stage", "sample")}
        for group in all_articles.values() for a in group
    ], ensure_ascii=False, indent=2), encoding="utf-8")
    print("Build complete:", OUTPUT)
    for section, articles in all_articles.items():
        print(f"  {section}: {len(articles)} published entries")


if __name__ == "__main__":
    main()
