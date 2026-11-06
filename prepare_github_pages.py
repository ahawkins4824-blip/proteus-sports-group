"""Export dist for GitHub Pages without changing the source build.

Example:
    python3 prepare_github_pages.py --base-path /proteus-sports-group \
        --site-url https://ahawkins4824-blip.github.io/proteus-sports-group
"""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
OLD_ORIGIN = "https://proteus-sports-group-redesign.quiet-cake-7330.chatgpt.site"
URL_ATTRIBUTES = {"href", "src", "poster", "action"}
ATTRIBUTE = re.compile(
    r"(?P<name>[A-Za-z_:][-\w:.]*)(?P<equals>\s*=\s*)"
    r"(?P<quote>[\"'])(?P<value>.*?)(?P=quote)",
    re.DOTALL,
)
CSS_URL = re.compile(
    r"(?P<prefix>\burl\(\s*)(?:(?P<quote>[\"'])(?P<quoted>.*?)(?P=quote)"
    r"|(?P<unquoted>[^)]*?))(?P<suffix>\s*\))",
    re.IGNORECASE | re.DOTALL,
)
# Only the known, generated contact routes need rewriting in JavaScript.
JS_CONTACT_PREFIX = re.compile(r"(?P<quote>[\"'`])(?P<path>/(?:approved-v[123]/)?contact/)")
JS_EXPORTED_CONTACT = re.compile(r"[\"'`](?P<path>/[^\"'`\n]*?contact/)")


def under_base(path: str, base_path: str) -> bool:
    return not base_path or path == base_path or path.startswith(base_path + "/")


def prefix_url(value: str, base_path: str) -> str:
    """Prefix a root URL once, retaining its query and fragment verbatim."""
    if not base_path or not value.startswith("/") or value.startswith("//"):
        return value
    boundary = re.split(r"[?#]", value, maxsplit=1)[0]
    return value if under_base(boundary, base_path) else base_path + value


def refresh_url(content: str) -> str | None:
    match = re.search(r"\burl\s*=\s*(.*)$", content, re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
        value = value[1:-1]
    return value


def rewrite_refresh(content: str, base_path: str) -> str:
    match = re.search(r"\burl\s*=\s*(.*)$", content, re.IGNORECASE)
    if not match:
        return content
    raw = match.group(1)
    stripped = raw.strip()
    quote = stripped[0] if len(stripped) >= 2 and stripped[0] in "\"'" and stripped[-1] == stripped[0] else ""
    target = stripped[1:-1] if quote else stripped
    leading = raw[: len(raw) - len(raw.lstrip())]
    trailing = raw[len(raw.rstrip()) :]
    return content[: match.start(1)] + leading + quote + prefix_url(target, base_path) + quote + trailing


class HTMLRewriter(HTMLParser):
    """Collect replacements for start tags; leave all other source bytes alone."""

    def __init__(self, source: str, base_path: str):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.base_path = base_path
        self.replacements: list[tuple[int, int, str]] = []
        self.line_offsets = [0]
        self.line_offsets.extend(match.end() for match in re.finditer("\n", source))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        raw = self.get_starttag_text()
        values = dict(attrs)
        is_refresh = tag == "meta" and values.get("http-equiv", "").lower() == "refresh"

        def replace_attribute(match: re.Match[str]) -> str:
            name = match.group("name").lower()
            value = match.group("value")
            if name in URL_ATTRIBUTES:
                value = prefix_url(value, self.base_path)
            elif name == "content" and is_refresh:
                value = rewrite_refresh(value, self.base_path)
            return match.group("name") + match.group("equals") + match.group("quote") + value + match.group("quote")

        rewritten = ATTRIBUTE.sub(replace_attribute, raw)
        if rewritten != raw:
            line, column = self.getpos()
            start = self.line_offsets[line - 1] + column
            self.replacements.append((start, start + len(raw), rewritten))

    handle_startendtag = handle_starttag

    def result(self) -> str:
        self.feed(self.source)
        self.close()
        result = self.source
        for start, end, replacement in reversed(self.replacements):
            result = result[:start] + replacement + result[end:]
        return result


def rewrite_css(source: str, base_path: str) -> str:
    def replace(match: re.Match[str]) -> str:
        quote = match.group("quote") or ""
        value = match.group("quoted") if quote else match.group("unquoted")
        return match.group("prefix") + quote + prefix_url(value, base_path) + quote + match.group("suffix")

    return CSS_URL.sub(replace, source)


def rewrite_javascript(source: str, base_path: str) -> str:
    return JS_CONTACT_PREFIX.sub(
        lambda match: match.group("quote") + prefix_url(match.group("path"), base_path),
        source,
    )


def rewrite_robots(source: str, base_path: str, site_url: str) -> str:
    lines = []
    for line in source.splitlines():
        rule = re.match(r"(\s*(?:Allow|Disallow)\s*:\s*)(/\S*)(\s*)$", line, re.IGNORECASE)
        if rule:
            line = rule.group(1) + prefix_url(rule.group(2), base_path) + rule.group(3)
        elif re.match(r"\s*Sitemap\s*:", line, re.IGNORECASE):
            line = "Sitemap: " + site_url + "/sitemap.xml"
        lines.append(line)
    return "\n".join(lines) + "\n"


class HTMLInventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        self.references.extend(value for name, value in attrs if name in URL_ATTRIBUTES and value)
        if tag == "meta" and values.get("http-equiv", "").lower() == "refresh":
            target = refresh_url(values.get("content", ""))
            if target:
                self.references.append(target)


def validate_export(output: Path, base_path: str, site_url: str) -> tuple[int, int]:
    documents = {}
    for path in sorted(output.rglob("*.html")):
        inventory = HTMLInventory()
        inventory.feed(path.read_text(encoding="utf-8"))
        inventory.close()
        documents[path.resolve()] = inventory

    origin = urlsplit(site_url)
    errors: list[str] = []
    checked = 0

    def check_reference(source: Path, value: str) -> None:
        nonlocal checked
        if value.startswith("//"):
            return
        parts = urlsplit(value)
        if parts.scheme or parts.netloc:
            if parts.scheme not in {"http", "https"} or parts.netloc != origin.netloc:
                return
        path = unquote(parts.path)
        if path.startswith("/"):
            if not under_base(path, base_path):
                errors.append(f"{source.relative_to(output)}: URL escapes base path: {value}")
                return
            target = output / path[len(base_path) :].lstrip("/")
        elif not path:
            target = source
        else:
            target = source.parent / path
        target = target.resolve()
        if not target.is_relative_to(output):
            errors.append(f"{source.relative_to(output)}: URL escapes export: {value}")
            return
        if target.is_dir():
            target /= "index.html"
        checked += 1
        if not target.is_file():
            errors.append(f"{source.relative_to(output)}: missing target: {value}")
        elif parts.fragment and target in documents and unquote(parts.fragment) not in documents[target].ids:
            errors.append(f"{source.relative_to(output)}: missing fragment: {value}")

    for path, document in documents.items():
        for value in document.references:
            check_reference(path, value)
    for path in sorted(output.rglob("*.css")):
        for match in CSS_URL.finditer(path.read_text(encoding="utf-8")):
            check_reference(path, match.group("quoted") if match.group("quote") else match.group("unquoted"))
    for path in sorted(output.rglob("*.js")):
        for match in JS_EXPORTED_CONTACT.finditer(path.read_text(encoding="utf-8")):
            check_reference(path, match.group("path"))
    for path in output.rglob("*"):
        if path.suffix.lower() in {".html", ".css", ".js", ".xml", ".txt"} and path.is_file():
            if OLD_ORIGIN in path.read_text(encoding="utf-8"):
                errors.append(f"{path.relative_to(output)}: old preview origin remains")
    if errors:
        raise ValueError("Export validation failed:\n" + "\n".join(errors))
    return len(documents), checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-path", required=True, help="GitHub project path, for example /proteus-sports-group")
    parser.add_argument("--site-url", required=True, help="Full public URL, including the project path")
    args = parser.parse_args()
    base_path = args.base_path.rstrip("/")
    if base_path and (not base_path.startswith("/") or "//" in base_path or
                      any(part in {".", ".."} for part in base_path.split("/")) or
                      any(character in base_path for character in "?#\\")):
        parser.error("--base-path must be an absolute URL path without a query, fragment or dot segments")
    site_url = args.site_url.rstrip("/")
    parts = urlsplit(site_url)
    if parts.scheme not in {"https", "http"} or not parts.netloc or parts.query or parts.fragment or parts.path != base_path:
        parser.error("--site-url must be an HTTP(S) origin followed by the same --base-path")

    source = ROOT / "dist"
    output = ROOT / "_site"
    if not (source / "index.html").is_file():
        parser.error("dist/index.html is missing; run python3 build.py first")
    if output.is_symlink():
        parser.error("refusing to replace a symbolic-link _site directory")
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(source, output, ignore=shutil.ignore_patterns("_redirects"))

    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".html", ".css", ".js", ".xml", ".txt"}:
            continue
        original = path.read_text(encoding="utf-8")
        content = original.replace(OLD_ORIGIN, site_url)
        if path.suffix.lower() == ".html":
            content = HTMLRewriter(content, base_path).result()
        elif path.suffix.lower() == ".css":
            content = rewrite_css(content, base_path)
        elif path.suffix.lower() == ".js":
            content = rewrite_javascript(content, base_path)
        elif path.name == "robots.txt":
            content = rewrite_robots(content, base_path, site_url)
        if content != original:
            path.write_text(content, encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    pages, references = validate_export(output.resolve(), base_path, site_url)
    print(f"Exported {pages} HTML pages to {output}; validated {references} local references.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
