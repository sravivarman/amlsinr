"""
Check source consistency that is easy to miss during content edits.

Usage:
    uv run python tools/check_consistency.py
"""

import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "content" / "blog"
THEME_DIR = ROOT / "static" / "css" / "themes"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def check_blog_posts() -> list[str]:
    errors = []
    template_path = BLOG_DIR / "post_template.yaml"
    template_keys = set(load_yaml(template_path))

    for path in sorted(BLOG_DIR.glob("*.yaml")):
        if path == template_path:
            continue

        keys = set(load_yaml(path))
        missing = sorted(template_keys - keys)
        extra = sorted(keys - template_keys)
        if missing:
            errors.append(f"{path.relative_to(ROOT)} is missing template key(s): {', '.join(missing)}")
        if extra:
            errors.append(f"{path.relative_to(ROOT)} has non-template key(s): {', '.join(extra)}")

    return errors


def css_selectors(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    selector_re = re.compile(r"(?s)(^|})\s*([^{}@][^{}]+?)\s*\{")
    return [" ".join(match.group(2).split()) for match in selector_re.finditer(text)]


def check_themes() -> list[str]:
    errors = []
    theme_paths = sorted(THEME_DIR.glob("*.css"))
    if not theme_paths:
        return ["No theme CSS files found."]

    reference = css_selectors(theme_paths[0])
    reference_name = theme_paths[0].name

    for path in theme_paths[1:]:
        selectors = css_selectors(path)
        if selectors != reference:
            missing = [selector for selector in reference if selector not in selectors]
            extra = [selector for selector in selectors if selector not in reference]
            if missing:
                errors.append(f"{path.name} is missing selector(s) from {reference_name}: {', '.join(missing)}")
            if extra:
                errors.append(f"{path.name} has extra selector(s) not in {reference_name}: {', '.join(extra)}")
            if not missing and not extra:
                errors.append(f"{path.name} has the same selectors as {reference_name}, but in a different order.")

    return errors


def main() -> int:
    errors = check_blog_posts() + check_themes()
    if errors:
        print("Consistency check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Consistency check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
