#!/usr/bin/env python3
"""Generate Sushant's animated GitHub profile with a Toronto weekday greeting."""

from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
TORONTO = ZoneInfo("America/Toronto")

# Original Jason Long-style bubbles; no phone frame, weather, or extra UI.
MESSAGES = [
    ["I have a habit of turning simple questions", "into entire projects. 😄"],
    ["I build software, work with AI, and like", "making complicated things feel simple."],
    ['The best part? Turning "what if..." into', '"hey, this actually works!"'],
    ["Currently in Toronto 🇨🇦"],
    ["Have an idea or tricky problem? Let's talk!"],
]
WIDTHS = [390, 435, 435, 435, 300, 445]
BUBBLE_GAP = 12
BETWEEN_MESSAGES = 0.38  # brief pause after each bubble appears


def message_content(day):
    return [[f"Happy {day}! 👋 I'm Sushant."]] + MESSAGES


def message_timing(messages):
    """Keep short-message typing brief and longer-message typing noticeably longer."""
    spans = []
    next_start = 0.0
    for lines in messages:
        characters = len(" ".join(lines))
        typing_duration = max(0.72, min(2.4, characters / 32))
        reveal_at = next_start + typing_duration
        spans.append((next_start, typing_duration, reveal_at))
        next_start = reveal_at + BETWEEN_MESSAGES
    return spans


def render(now=None):
    now = now or datetime.now(TORONTO)
    messages = message_content(now.strftime("%A"))
    timing = message_timing(messages)

    heights = [42 + (len(lines) - 1) * 24 for lines in messages]
    tops = []
    y = 0
    for height in heights:
        tops.append(y)
        y += height + BUBBLE_GAP
    canvas_height = y + 4

    css = [
        ".bubble { fill: #e9e9eb; }",
        "text { fill: #242424; font-size: 18px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; letter-spacing: -0.02em; }",
        ".dots { fill: #999999; }",
        "@keyframes hidden { from, to { opacity: 0; } }",
        "@keyframes typing { 0%,100% { opacity: 0; } 17%,86% { opacity: 1; } }",
    ]
    for i, ((start, duration, reveal_at), top) in enumerate(zip(timing, tops), 1):
        css += [
            f".typing-{i} {{ opacity: 0; animation: hidden {start:.2f}s, typing {duration:.2f}s {start:.2f}s; }}",
            f".msg-{i} {{ animation: hidden {reveal_at:.2f}s, pop-{i} .24s {reveal_at:.2f}s forwards; }}",
            f"@keyframes pop-{i} {{ 0% {{ opacity: 0; transform: translate(10px, {top + 5}px); }} 100% {{ opacity: 1; transform: translate(10px, {top}px); }} }}",
        ]
    css += [
        "@media (prefers-color-scheme: dark) { .bubble { fill: #3b3b3d; } text { fill: #dcdcdc; } }",
        "@media (prefers-reduced-motion: reduce) { g[class^='msg-'] { animation: none; opacity: 1; } g[class^='typing-'] { display: none; } }",
    ]

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="550" height="{canvas_height}" viewBox="0 0 550 {canvas_height}" fill="none">',
        '<title>Sushant’s introduction</title>',
        "<style>" + "\n".join(css) + "</style>",
    ]
    for i, (lines, top, bubble_height, width) in enumerate(
        zip(messages, tops, heights, WIDTHS), 1
    ):
        svg.append(f'<g transform="translate(10, {top})" class="typing-{i}">')
        svg += [
            '<rect x="8.27246" width="69.7276" height="42" rx="20.9774" class="bubble" />',
            '<circle cx="13.591" cy="33.091" r="7.68185" class="bubble" />',
            '<circle cx="3.54547" cy="41.9547" r="3.54547" class="bubble" />',
        ]
        for j, x in enumerate([27.4778, 42.8411, 58.2054]):
            svg.append(
                f'<circle cx="{x}" cy="20.9773" r="5.02275" class="dots">'
                f'<animate attributeName="opacity" values="0.5;1;0.5" dur="1s" '
                f'begin="{j * .2:.1f}s" repeatCount="indefinite" /></circle>'
            )
        svg.append("</g>")
        svg.append(f'<g transform="translate(10, {top})" class="msg-{i}">')
        svg.append(
            f'<rect width="{width}" height="{bubble_height}" rx="18" class="bubble" />'
        )
        for line_index, line in enumerate(lines):
            svg.append(
                f'<text x="15" y="{27 + line_index * 24}">{escape(line)}</text>'
            )
        svg.append("</g>")
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


if __name__ == "__main__":
    output = ROOT / "intro.svg"
    output.write_text(render(), encoding="utf-8")
    print(f"Generated {output}")
