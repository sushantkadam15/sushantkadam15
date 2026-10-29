#!/usr/bin/env python3
"""Generate the animated profile SVG with Toronto weekday and weather."""
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import json

ROOT = Path(__file__).resolve().parent
TZ = ZoneInfo("America/Toronto")
CONDITIONS = {
    0: ("☀️", "clear"), 1: ("🌤", "mainly clear"), 2: ("⛅", "partly cloudy"),
    3: ("☁️", "cloudy"), 45: ("🌫️", "foggy"), 48: ("🌫️", "foggy"),
    51: ("🌦️", "light drizzle"), 53: ("🌦️", "drizzle"),
    55: ("🌧️", "drizzle"), 56: ("🌧️", "freezing drizzle"),
    57: ("🌧️", "freezing drizzle"), 61: ("🌧️", "light rain"),
    63: ("🌧️", "rainy"), 65: ("🌧️", "heavy rain"),
    66: ("🌧️", "freezing rain"), 67: ("🌧️", "freezing rain"),
    71: ("🌨️", "light snow"), 73: ("🌨️", "snowy"),
    75: ("❄️", "heavy snow"), 77: ("🌨️", "snow grains"),
    80: ("🌦️", "showers"), 81: ("🌦️", "showers"),
    82: ("⛈️", "heavy showers"), 85: ("🌨️", "snow showers"),
    86: ("❄️", "snow showers"), 95: ("⛈️", "thunderstorms"),
    96: ("⛈️", "thunderstorms"), 99: ("⛈️", "thunderstorms"),
}
DELAYS = [0.9, 2.1, 3.5, 5.2, 6.9, 8.8, 10.9]
WIDTHS = [245, 150, 435, 435, 435, 350, 445]


def toronto_weather():
    params = urlencode({
        "latitude": 43.6532, "longitude": -79.3832,
        "current": "temperature_2m,weather_code",
        "timezone": "America/Toronto",
    })
    url = "https://api.open-meteo.com/v1/forecast?" + params
    req = Request(url, headers={"User-Agent": "sushant-github-readme/1.0"})
    try:
        with urlopen(req, timeout=15) as response:
            data = json.load(response)
        observation = data["current"]
        temp = round(float(observation["temperature_2m"]))
        emoji, condition = CONDITIONS.get(
            int(observation["weather_code"]), ("🌡️", "changing conditions")
        )
        return f"{emoji} {temp}°C, {condition}"
    except (OSError, KeyError, ValueError, TypeError) as exc:
        print(f"Weather unavailable: {exc}")
        return "🌡️ Weather unavailable"


def render():
    day = datetime.now(TZ).strftime("%A")
    messages = [
        [f"Happy {day}! 👋"],
        ["I'm Sushant."],
        ["I have a habit of turning simple questions", "into entire projects. 😄"],
        ["I build software, work with AI, and like", "making complicated things feel simple."],
        ['The best part? Turning "what if..." into', '"hey, this actually works!"'],
        ["Currently in Toronto 🇨🇦 —", toronto_weather()],
        ["Have an idea or tricky problem? Let's talk!"],
    ]

    heights = [42 + (len(lines) - 1) * 24 for lines in messages]
    tops, y = [], 0
    for height in heights:
        tops.append(y)
        y += height + 6
    height = y + 4

    styles = [
        ".bubble { fill: #e9e9eb; }",
        "text { fill: #242424; font-size: 18px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; letter-spacing: -0.02em; }",
        ".dots { fill: #999999; }",
        "@keyframes wait { 0%, 100% { opacity: 0; } }",
        "@keyframes fade-in-out { 0%, 100% { opacity: 0; } 25%, 90% { opacity: 1; } }",
    ]
    for i, (delay, top) in enumerate(zip(DELAYS, tops), 1):
        start = max(0, delay - .95)
        styles += [
            f".typing-{i} {{ opacity: 0; animation: wait {start:.2f}s, fade-in-out .95s {start:.2f}s; }}",
            f".msg-{i} {{ animation: wait {delay:.2f}s, msg-{i} .22s {delay:.2f}s forwards; }}",
            f"@keyframes msg-{i} {{ 0% {{ opacity: 0; transform: translate(10px, {top + 5}px); }} 100% {{ opacity: 1; transform: translate(10px, {top}px); }} }}",
        ]
    styles += [
        "@media (prefers-color-scheme: dark) { .bubble { fill: #3b3b3d; } text { fill: #dcdcdc; } }",
        "@media (prefers-reduced-motion: reduce) { g[class^='msg-'] { animation: none; opacity: 1; } g[class^='typing-'] { display: none; } }",
    ]

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="550" height="{height}" viewBox="0 0 550 {height}" fill="none">',
        '<title>Sushant’s introduction</title>',
        '<style>' + "\n".join(styles) + '</style>',
    ]
    for i, (lines, top, bubble_height, width) in enumerate(
        zip(messages, tops, heights, WIDTHS), 1
    ):
        out.append(f'<g transform="translate(10, {top})" class="typing-{i}">')
        out += [
            '<rect x="8.27246" width="69.7276" height="42" rx="20.9774" class="bubble" />',
            '<circle cx="13.591" cy="33.091" r="7.68185" class="bubble" />',
            '<circle cx="3.54547" cy="41.9547" r="3.54547" class="bubble" />',
        ]
        for j, x in enumerate([27.4778, 42.8411, 58.2054]):
            out.append(
                f'<circle cx="{x}" cy="20.9773" r="5.02275" class="dots">'
                f'<animate attributeName="opacity" values="0.5;1;0.5" dur="1s" '
                f'begin="{j * .2:.1f}s" repeatCount="indefinite" /></circle>'
            )
        out.append('</g>')
        out.append(f'<g transform="translate(10, {top})" class="msg-{i}">')
        out.append(f'<rect width="{width}" height="{bubble_height}" rx="18" class="bubble" />')
        for line_index, line in enumerate(lines):
            out.append(f'<text x="15" y="{27 + line_index * 24}">{escape(line)}</text>')
        out.append('</g>')
    out.append('</svg>')
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    output = ROOT / "chat.svg"
    output.write_text(render(), encoding="utf-8")
    print(f"Generated {output}")
