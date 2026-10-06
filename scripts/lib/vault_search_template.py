#!/usr/bin/env python3
"""
Ars Arcanum Vault Search Presentation & Report Templates
(scripts/lib/vault_search_template.py)
========================================================
Formatters for Markdown reports, LLM context synthesis, and standalone
100% offline HTML retrieval viewer for the vault search engine.
"""

from __future__ import annotations

import html
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lib.vault_search import RetrievalResult
else:
    RetrievalResult = Any


def synthesize_llm_context(
    query: str,
    results: list[RetrievalResult],
    system_instructions: str | None = None,
) -> str:
    """Synthesizes a secure reference context block from retrieved chunks."""
    default_instructions = (
        "You are the Ars Arcanum Sovereign Lore Inquisitor. Answer the author's inquiry\n"
        "using strictly the verified canonical context chunks provided below. If the context\n"
        "does not provide sufficient information, state what is known and identify lore gaps."
    )
    instructions = system_instructions or default_instructions

    lines = [
        "<system_instructions>",
        instructions.strip(),
        "</system_instructions>",
        "",
        "<canonical_lore_context>",
    ]

    if not results:
        lines.append("No canonical lore records matched the inquiry.")
    else:
        for idx, res in enumerate(results, 1):
            c = res.chunk
            lines.append(f"--- [RECORD #{idx} | Relevance: {res.score:.2f} | Category: {c.category}] ---")
            lines.append(f"Document: {c.doc_title} (ID: {c.doc_id})")
            if c.doc_path:
                lines.append(f"Source Path: {c.doc_path}")
            if c.heading:
                lines.append(f"Section: {c.heading}")
            if c.entities:
                lines.append(f"Entities: {', '.join(c.entities)}")
            lines.append("Content:")
            lines.append(c.text.strip())
            lines.append("")

    lines.append("</canonical_lore_context>")
    lines.append("")
    lines.append("<user_query>")
    lines.append(query.strip())
    lines.append("</user_query>")

    return "\n".join(lines)


def format_markdown_report(query: str, results: list[RetrievalResult]) -> str:
    """Formats retrieved results into a readable Markdown report."""
    lines = [
        "# Ars Arcanum Vault Search Report",
        "",
        f"**Query**: `{query}`  ",
        f"**Results Found**: {len(results)} chunks  ",
        "",
        "## Top Canonical Matches",
        "",
    ]

    if not results:
        lines.append("*No matching canonical lore found for this query.*")
        return "\n".join(lines)

    lines.append("| Rank | Score | Title | Category | Section | Entities |")
    lines.append("| :--- | :---: | :--- | :--- | :--- | :--- |")

    for i, res in enumerate(results, 1):
        c = res.chunk
        entities_str = ", ".join(c.entities[:3]) if c.entities else "—"
        sec = c.heading if c.heading else "—"
        lines.append(f"| #{i} | **{res.score:.2f}** | `{c.doc_title}` | {c.category} | {sec} | {entities_str} |")

    lines.append("")
    lines.append("## Retrieved Chunk Excerpts")
    lines.append("")

    for i, res in enumerate(results, 1):
        c = res.chunk
        lines.append(f"### #{i}. {c.doc_title} — *{c.heading or 'General'}* (Score: {res.score:.2f})")
        lines.append(f"- **Document ID**: `{c.doc_id}` | **Category**: `{c.category}` | **Words**: {c.word_count}")
        if c.entities:
            lines.append(f"- **Referenced Entities**: {', '.join(f'`{e}`' for e in c.entities)}")
        lines.append("")
        lines.append("> " + c.text.replace("\n", "\n> "))
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def generate_html_retrieval_viewer(query: str, results: list[RetrievalResult]) -> str:
    """Generates a standalone, 100% offline interactive HTML search dashboard."""
    cards_html = []
    for i, res in enumerate(results, 1):
        c = res.chunk
        score_pct = round(res.score * 100)
        score_color = "#10b981" if score_pct >= 60 else "#3b82f6" if score_pct >= 35 else "#f59e0b"

        entities_badges = "".join(f'<span class="badge badge-entity">{html.escape(e)}</span>' for e in c.entities)

        card = f"""
        <div class="result-card">
            <div class="card-header">
                <div class="card-title">
                    <span class="rank-badge">#{i}</span>
                    <h3>{html.escape(c.doc_title)}</h3>
                    <span class="category-tag">{html.escape(c.category)}</span>
                </div>
                <div class="score-badge" style="background: {score_color}22; color: {score_color}; border: 1px solid {score_color}55;">
                    {score_pct}% Match
                </div>
            </div>
            {f'<div class="section-header"><strong>Section:</strong> {html.escape(c.heading)}</div>' if c.heading else ''}
            <div class="card-body">
                <p>{html.escape(c.text)}</p>
            </div>
            <div class="card-footer">
                <div class="meta-item"><span>Path:</span> <code>{html.escape(c.doc_path or c.doc_id)}</code></div>
                <div class="meta-item"><span>Words:</span> {c.word_count}</div>
                <div class="entities-wrap">{entities_badges}</div>
            </div>
        </div>
        """
        cards_html.append(card)

    results_container = "\n".join(cards_html) if cards_html else "<div class='empty-state'>No matching lore chunks found.</div>"
    raw_context = synthesize_llm_context(query, results)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:;">
    <title>Ars Arcanum Vault Search — {html.escape(query)}</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --border: #334155;
            --accent: #8b5cf6;
            --accent-glow: rgba(139, 92, 246, 0.2);
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --font: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --code-font: "Fira Code", "Cascadia Code", Consolas, monospace;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--font);
            line-height: 1.6;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
        }}
        h1 {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #c084fc;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .query-box {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin-top: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .query-text {{
            font-family: var(--code-font);
            color: #38bdf8;
            font-size: 1.1rem;
        }}
        .stats-badge {{
            background: #0284c722;
            color: #38bdf8;
            border: 1px solid #0284c755;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
        }}
        .results-list {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            margin-top: 1.5rem;
        }}
        .result-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: border-color 0.2s;
        }}
        .result-card:hover {{
            border-color: var(--accent);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }}
        .card-title {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .rank-badge {{
            background: #334155;
            color: #cbd5e1;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 700;
        }}
        .category-tag {{
            background: #4c1d95;
            color: #ddd6fe;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 600;
        }}
        .score-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 700;
        }}
        .section-header {{
            font-size: 0.9rem;
            color: #a78bfa;
            margin-bottom: 0.75rem;
        }}
        .card-body {{
            background: #0f172a88;
            padding: 1rem;
            border-radius: 6px;
            border-left: 3px solid var(--accent);
            font-size: 0.95rem;
            color: #e2e8f0;
            white-space: pre-wrap;
            margin-bottom: 0.75rem;
        }}
        .card-footer {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 1rem;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border);
            padding-top: 0.75rem;
        }}
        .badge-entity {{
            background: #065f46;
            color: #a7f3d0;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-right: 0.35rem;
        }}
        .context-export {{
            margin-top: 2.5rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
        }}
        .context-export h2 {{
            font-size: 1.2rem;
            color: #f1f5f9;
            margin-bottom: 0.5rem;
        }}
        textarea {{
            width: 100%;
            height: 200px;
            background: #090d16;
            color: #a5f3fc;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.75rem;
            font-family: var(--code-font);
            font-size: 0.85rem;
            resize: vertical;
        }}
        button {{
            background: var(--accent);
            color: #fff;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 0.5rem;
        }}
        button:hover {{ background: #7c3aed; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>✦ Ars Arcanum Sovereign Vault Search</h1>
            <p style="color: var(--text-muted);">100% Offline Hybrid Vector Space &amp; Canonical Lore Query Engine</p>
            <div class="query-box">
                <div class="query-text">"{html.escape(query)}"</div>
                <div class="stats-badge">{len(results)} chunks retrieved</div>
            </div>
        </header>

        <main>
            <div class="results-list">
                {results_container}
            </div>

            <div class="context-export">
                <h2>Prompt Context for Offline Lore Systems</h2>
                <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.75rem;">
                    Copy this formatted context block directly into your offline drafting studio.
                </p>
                <textarea id="promptContext" readonly>{html.escape(raw_context)}</textarea>
                <button onclick="navigator.clipboard.writeText(document.getElementById('promptContext').value); this.innerText='✓ Copied Context!';">
                    Copy Prompt Context
                </button>
            </div>
        </main>
    </div>
</body>
</html>
"""

__all__ = [
    "format_markdown_report",
    "generate_html_retrieval_viewer",
    "synthesize_llm_context",
]
