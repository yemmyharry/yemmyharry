"""Generate a language card from the primary language of each public repository."""

import json
import os
from collections import Counter
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

USERNAME = "yemmyharry"
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "languages.svg"
COLORS = {
    "Go": "#00ADD8",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Rust": "#dea584",
    "CSS": "#a78bfa",
    "HTML": "#e34c26",
    "Python": "#3572A5",
    "C": "#a8b9cc",
    "Shell": "#89e051",
}


def fetch_languages():
    counts = Counter()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "yemmyharry-profile",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    page = 1
    while True:
        request = Request(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}",
            headers=headers,
        )
        with urlopen(request, timeout=30) as response:
            repos = json.load(response)
        for repo in repos:
            if not repo["fork"] and not repo["archived"] and repo["language"]:
                counts[repo["language"]] += 1
        if len(repos) < 100:
            break
        page += 1
    if not counts:
        raise ValueError("No language data found; preserving the existing card")
    return counts


def render(counts):
    top = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:6]
    total = sum(counts.values())
    height = 112 + len(top) * 36
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="560" height="{height}" '
        f'viewBox="0 0 560 {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Languages across my public repositories</title>',
        '<desc id="desc">Primary language per original, non-archived public repository. '
        + escape("; ".join(f"{lang}: {count} repositories" for lang, count in top))
        + '.</desc>',
        '<rect x="1" y="1" width="558" height="' + str(height - 2)
        + '" rx="16" fill="#0d1117" stroke="#30363d"/>',
        '<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">',
        '<text x="24" y="35" fill="#f0f6fc" font-size="18" font-weight="600">'
        'Languages in the mix</text>',
        '<text x="24" y="58" fill="#9da7b3" font-size="12">'
        'Primary language per public repo · forks and archives excluded</text>',
    ]
    for index, (language, count) in enumerate(top):
        y = 91 + index * 36
        color = COLORS.get(language, "#8b949e")
        width = round(222 * count / top[0][1], 1)
        parts.extend([
            f'<circle cx="29" cy="{y - 4}" r="5" fill="{color}"/>',
            f'<text x="44" y="{y}" fill="#e6edf3" font-size="13">'
            f'{escape(language)}</text>',
            f'<rect x="158" y="{y - 12}" width="222" height="10" '
            'rx="5" fill="#21262d"/>',
            f'<rect x="158" y="{y - 12}" width="{width}" height="10" '
            f'rx="5" fill="{color}"/>',
            f'<text x="404" y="{y}" fill="#9da7b3" font-size="12">'
            f'{count} repos · {count / total:.0%}</text>',
        ])
    parts.extend([
        f'<text x="24" y="{height - 19}" fill="#9da7b3" font-size="11">'
        f'Top {len(top)} of {len(counts)} languages · {total} repos · refreshed weekly'
        '</text>',
        '</g></svg>\n',
    ])
    return "\n".join(parts)


if __name__ == "__main__":
    languages = fetch_languages()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(languages), encoding="utf-8")
    print(f"Updated {OUTPUT.name}: {sum(languages.values())} repositories")
