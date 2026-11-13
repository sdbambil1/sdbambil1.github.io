"""Verify the generated site before GitHub Pages deployment.

Checks local links and assets, PDF availability and document structure.
Reports large images without changing the original files.
"""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys

ROOT = Path(__file__).resolve().parent.parent / "_site"
REQUIRED_PAGES = (
    "index.html", "academic.html", "research.html", "teaching.html",
    "conferences.html", "professional-cv.html", "projects.html",
    "cv.html", "contact.html",
)
REQUIRED_PDFS = (
    "files/Silas_Bambil_PhD_CV.pdf",
    "files/Silas_Bambil_Professional_CV.pdf",
)
ERRORS = []
WARNINGS = []
GOOGLE_VERIFICATION = "6XrEP0ZZI6fcSM1jNiHozH8qzM0hfNafOX5ED7T8OHE"
SITE_URL = "https://sdbambil1.github.io/"
MAIN_STYLESHEET = "styles-tex-academic.css"


class PageInspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.has_main = False
        self.has_title = False
        self.in_title = False
        self.has_h1 = False
        self.google_verified_tag = False
        self.skip_links = []
        self.jump_links = []
        self.in_jump_nav = False
        self.canonical_urls = []
        self.in_json_ld = False
        self.json_ld_blocks = []
        self._json_ld = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "meta" and attrs.get("name") == "google-site-verification":
            self.google_verified_tag = attrs.get("content") == GOOGLE_VERIFICATION
        if tag == "link" and attrs.get("rel", "").lower() == "canonical":
            self.canonical_urls.append(attrs.get("href", ""))
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.in_json_ld = True
            self._json_ld = []
        if tag == "nav" and "jump-links" in attrs.get("class", "").split():
            self.in_jump_nav = True
        if tag == "a" and self.in_jump_nav:
            self.jump_links.append(attrs.get("href", ""))
        if tag == "a" and "skip-to-content" in attrs.get("class", "").split():
            self.skip_links.append(attrs.get("href", ""))
        if tag == "main":
            self.has_main = True
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.has_h1 = True
        if tag in ("a", "link") and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag in ("img", "script", "source") and attrs.get("src"):
            self.links.append(attrs["src"])

    def handle_endtag(self, tag):
        if tag == "nav" and self.in_jump_nav:
            self.in_jump_nav = False
        if tag == "script" and self.in_json_ld:
            self.json_ld_blocks.append("".join(self._json_ld))
            self.in_json_ld = False
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_json_ld:
            self._json_ld.append(data)
        if self.in_title and data.strip():
            self.has_title = True


def check_local_reference(page, raw, ids_by_file):
    raw = raw.strip()
    if not raw or raw.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
        if raw.startswith("#") and len(raw) > 1:
            frag = unquote(raw[1:])
            if frag not in ids_by_file.get(page, set()):
                # Quarto/JS may create dynamic fragments; report rather than fail.
                WARNINGS.append(f"{page.relative_to(ROOT)}: unverified fragment {raw}")
        return
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return
    relative = unquote(parsed.path)
    if not relative:
        target = page
    elif relative.startswith("/"):
        target = ROOT / relative.lstrip("/")
    else:
        target = page.parent / relative
    if relative.endswith("/") or target.is_dir():
        target = target / "index.html"
    try:
        normalized = target.resolve(strict=False)
        normalized.relative_to(ROOT.resolve())
    except ValueError:
        ERRORS.append(f"{page.relative_to(ROOT)}: link escapes site: {raw}")
        return
    if not normalized.is_file():
        ERRORS.append(f"{page.relative_to(ROOT)}: missing asset or page: {raw}")
        return
    # Check only anchors explicitly authored in the rendered target.
    if parsed.fragment and normalized.suffix.lower() == ".html":
        fragment = unquote(parsed.fragment)
        if normalized in ids_by_file and fragment not in ids_by_file[normalized]:
            WARNINGS.append(f"{page.relative_to(ROOT)}: unverified target anchor: {raw}")


def main():
    if not ROOT.is_dir():
        ERRORS.append("Missing rendered _site directory")
        print("\n".join(ERRORS))
        return 1

    for name in (*REQUIRED_PAGES, *REQUIRED_PDFS):
        candidate = ROOT / name
        if not candidate.is_file() or candidate.stat().st_size == 0:
            ERRORS.append(f"Required output is absent or empty: {name}")

    pages = sorted(ROOT.rglob("*.html"))
    ids_by_file = {}
    inspected = {}
    for page in pages:
        parser = PageInspector()
        parser.feed(page.read_text(encoding="utf-8"))
        ids_by_file[page.resolve()] = parser.ids
        inspected[page] = parser
        expected_canonical = (SITE_URL if page == ROOT / "index.html"
                              else SITE_URL + page.relative_to(ROOT).as_posix())
        if parser.canonical_urls != [expected_canonical]:
            ERRORS.append(
                f"{page.relative_to(ROOT)}: canonical URL mismatch: "
                f"expected {expected_canonical}, got {parser.canonical_urls}"
            )
        if page.name == "index.html":
            if not any(MAIN_STYLESHEET in url for url in parser.links):
                ERRORS.append("index.html: required stylesheet reference missing")
            person_blocks = []
            for raw_block in parser.json_ld_blocks:
                try:
                    obj = json.loads(raw_block)
                except json.JSONDecodeError as exc:
                    ERRORS.append(f"index.html: invalid JSON-LD: {exc}")
                    continue
                if isinstance(obj, dict) and obj.get("@type") == "Person":
                    person_blocks.append(obj)
            if len(person_blocks) != 1:
                ERRORS.append("index.html: expected exactly one Person JSON-LD block")
            elif person_blocks[0].get("url") != SITE_URL or not {
                "https://orcid.org/0009-0002-5110-8102",
                "https://github.com/sdbambil1",
            }.issubset(set(person_blocks[0].get("sameAs", []))):
                ERRORS.append("index.html: Person JSON-LD identity links are incomplete")
        if page.name == "index.html" and not parser.google_verified_tag:
            ERRORS.append("index.html: missing Google Search Console verification meta tag")
        if not parser.has_title:
            ERRORS.append(f"{page.relative_to(ROOT)}: missing page title")
        if parser.skip_links != ["#quarto-document-content"] or "quarto-document-content" not in parser.ids:
            ERRORS.append(f"{page.relative_to(ROOT)}: missing or invalid skip-to-content link")
        for href in parser.jump_links:
            if not href.startswith("#") or len(href) == 1:
                ERRORS.append(f"{page.relative_to(ROOT)}: section navigation must use a local fragment: {href}")
            elif unquote(href[1:]) not in parser.ids:
                ERRORS.append(f"{page.relative_to(ROOT)}: broken section navigation target: {href}")
        if not parser.has_main:
            ERRORS.append(f"{page.relative_to(ROOT)}: missing main landmark")
        if not parser.has_h1:
            WARNINGS.append(f"{page.relative_to(ROOT)}: no h1 heading detected")

    for page, parser in inspected.items():
        for link in parser.links:
            check_local_reference(page, link, ids_by_file)

    images = sorted(
        (p for p in ROOT.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")),
        key=lambda p: p.stat().st_size,
        reverse=True,
    )
    print(f"Checked {len(pages)} HTML pages and {len(images)} raster image files.")
    print("Largest raster images:")
    for img in images[:8]:
        size_kib = img.stat().st_size / 1024
        print(f"  {img.relative_to(ROOT)}: {size_kib:.0f} KiB")
        if size_kib > 750:
            WARNINGS.append(f"Large image (>750 KiB): {img.relative_to(ROOT)} ({size_kib:.0f} KiB)")
    for warning in WARNINGS:
        print("WARNING:", warning)
    for error in ERRORS:
        print("ERROR:", error)
    if ERRORS:
        print(f"Validation failed: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s).")
        return 1
    print(f"Validation passed: {len(pages)} pages; {len(WARNINGS)} non-blocking warnings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
