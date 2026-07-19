#!/usr/bin/env python3
"""Проверка относительных markdown-ссылок в репозитории.

Использование:
    python3 experiments/check_links.py [каталог ...]

Без аргументов проверяет весь репозиторий. Внешние ссылки (http/https/mailto)
и якоря (#...) пропускаются — проверяются только ссылки на файлы, включая
percent-encoded пробелы вида `Тема%201.%20...md`.

Код возврата: 0 — все ссылки разрешились, 1 — есть битые ссылки.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

# CommonMark допускает сбалансированные скобки внутри адреса ссылки,
# поэтому имя вида `Тема 3. ... (Digital Thread).md` — корректная цель.
LINK_RE = re.compile(r"\[[^\]]*\]\(((?:[^()\s]|\([^()\s]*\))+)\)")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def markdown_files(roots):
    for root in roots:
        root = Path(root)
        if root.is_file() and root.suffix == ".md":
            yield root
            continue
        for path in sorted(root.rglob("*.md")):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            yield path


def check(roots):
    broken = []
    checked = 0
    for md in markdown_files(roots):
        for line_no, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for target in LINK_RE.findall(line):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_part = unquote(target.split("#", 1)[0])
                if not path_part:
                    continue
                checked += 1
                if not (md.parent / path_part).exists():
                    broken.append((md, line_no, target))
    return checked, broken


def main():
    roots = sys.argv[1:] or ["."]
    checked, broken = check(roots)
    for md, line_no, target in broken:
        print(f"БИТАЯ ССЫЛКА  {md}:{line_no}  ->  {target}")
    print(f"\nПроверено внутренних ссылок: {checked}; битых: {len(broken)}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
