#!/usr/bin/env python3
"""Draw the make.fun news-image entry: a 1024x1024 broadsheet front page.

Covers the world news of Wednesday 25 November 2026.

Fully deterministic: fixed layout, fixed fonts, no randomness, no clock reads.
Output: entry.png (RGB, 1024x1024) in the repository root.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 44
CONTENT_W = W - 2 * M

PAPER = (250, 247, 239)
INK = (26, 24, 21)
GREY = (92, 88, 80)
LIGHT = (172, 166, 154)
HAIR = (203, 197, 185)
RED = (158, 32, 38)
TINT = (243, 238, 227)
WHITE = (252, 250, 245)

FONT_DIR = "/usr/share/fonts/truetype/liberation/"
SERIF_BOLD = FONT_DIR + "LiberationSerif-Bold.ttf"
SERIF = FONT_DIR + "LiberationSerif-Regular.ttf"
SERIF_IT = FONT_DIR + "LiberationSerif-Italic.ttf"
SANS_BOLD = FONT_DIR + "LiberationSans-Bold.ttf"
SANS = FONT_DIR + "LiberationSans-Regular.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def tracked_w(draw, text, fnt, tracking):
    if not text:
        return 0
    return sum(text_w(draw, ch, fnt) for ch in text) + tracking * (len(text) - 1)


def draw_tracked(draw, x, y, text, fnt, fill, tracking):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += text_w(draw, ch, fnt) + tracking


def draw_tracked_center(draw, y, text, fnt, fill, tracking):
    x = (W - tracked_w(draw, text, fnt, tracking)) / 2
    draw_tracked(draw, x, y, text, fnt, fill, tracking)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_headline(draw, text, path, max_w, max_lines, hi, lo):
    """Largest size whose wrapped headline fits the width in max_lines."""
    for size in range(hi, lo - 1, -1):
        fnt = F(path, size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines, size
    size = lo
    fnt = F(path, size)
    lines = wrap(draw, text, fnt, max_w)
    while len(lines) > max_lines and size > 8:
        size -= 1
        fnt = F(path, size)
        lines = wrap(draw, text, fnt, max_w)
    return fnt, lines, size


def rule(draw, x0, y, x1, fill=HAIR, width=1):
    draw.rectangle([x0, y, x1, y + width - 1], fill=fill)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Page frame ------------------------------------------------------------
    d.rectangle([16, 16, W - 17, H - 17], outline=HAIR, width=1)

    # Masthead --------------------------------------------------------------
    kicker_f = F(SANS_BOLD, 11)
    draw_tracked_center(
        d, 29, "THE GLOBAL EDITION  ·  WEDNESDAY, NOVEMBER 25, 2026", kicker_f, RED, 2.2
    )

    mast_f = F(SERIF_BOLD, 100)
    mast = "THE WORLD"
    d.text(((W - text_w(d, mast, mast_f)) / 2, 34), mast, font=mast_f, fill=INK)
    rule(d, M, 132, W - M, INK, 2)

    # Dateline strip --------------------------------------------------------
    d.rectangle([M, 140, W - M, 182], fill=TINT)
    date_f = F(SANS_BOLD, 26)
    d.text((M + 12, 147), "WEDNESDAY 25 NOVEMBER 2026", font=date_f, fill=INK)

    box_x1 = W - M - 4
    box_x0 = box_x1 - 164
    d.rectangle([box_x0, 143, box_x1, 179], fill=RED)
    banner_f = F(SANS_BOLD, 22)
    banner = "25 NOV 2026"
    draw_tracked(
        d,
        box_x0 + (box_x1 - box_x0 - tracked_w(d, banner, banner_f, 1.5)) / 2,
        150,
        banner,
        banner_f,
        WHITE,
        1.5,
    )

    meta_f = F(SANS, 11)
    meta = "VOL. 1  ·  NO. 336"
    draw_tracked(d, box_x0 - 12 - tracked_w(d, meta, meta_f, 0.8), 153,
                 meta, meta_f, GREY, 0.8)
    rule(d, M, 182, W - M, INK, 2)
    rule(d, M, 187, W - M, HAIR, 1)

    # Lead story ------------------------------------------------------------
    lab_f = F(SANS_BOLD, 11)
    draw_tracked(d, M, 201, "LEAD STORY  ·  WASHINGTON  ·  TRADE", lab_f, RED, 1.6)

    lead_f, lead_lines, lead_size = fit_headline(
        d,
        "US IMPOSES SWEEPING NEW TARIFFS ON CHINA AND DOZENS OF TRADING PARTNERS",
        SERIF_BOLD,
        CONTENT_W,
        2,
        44,
        32,
    )
    y = 219
    lead_lh = int(lead_size * 1.08)
    for line in lead_lines:
        d.text((M, y), line, font=lead_f, fill=INK)
        y += lead_lh

    y += 6
    deck_f = F(SERIF_IT, 17)
    deck_text = (
        "The new duties cover China and a long list of other trading partners. "
        "The move sharply widens US tariffs on imported goods."
    )
    for line in wrap(d, deck_text, deck_f, 600):
        d.text((M, y), line, font=deck_f, fill=GREY)
        y += 21

    lead_bottom = y + 6
    rule(d, M, lead_bottom, W - M, INK, 2)

    # Story grid: 2 columns x 3 rows ---------------------------------------
    stories = [
        ("EUROPE  ·  WAR",
         "RUSSIA'S OWN FIGURES SHOW NEARLY 500,000 LOST IN UKRAINE WAR",
         "Moscow's published toll nears half a million, as Ukraine says five Russian jets were hit in an airfield strike."),
        ("MIDDLE EAST  ·  GAZA",
         "ISRAELI STRIKE KILLS HAMAS SECURITY CHIEF AND FAMILY IN GAZA CITY",
         "The senior official died with relatives in the strike, Palestinian officials and medics said."),
        ("TECHNOLOGY  ·  LAW",
         "US COURT FINDS HUAWEI GUILTY OF STEALING TRADE SECRETS",
         "The verdict in a long-running case covers technology taken from US firms."),
        ("AMERICAS  ·  COLOMBIA",
         "POLICE STORM SIEGE AND FREE ALL 76 HOSTAGES AFTER 17 HOURS",
         "Police ended the supermarket siege and freed every hostage after 17 hours."),
        ("ASIA  ·  SPACE",
         "CHINA LAUNCHES MISSION WITH FIRST PAKISTANI ASTRONAUT ABOARD",
         "The Chinese crewed flight carries Pakistan's first astronaut, a landmark for the country's space programme."),
        ("AFRICA  ·  SOUTH AFRICA",
         "COURT LIFTS IMPEACHMENT THREAT AGAINST PRESIDENT RAMAPHOSA",
         "The court rejected the move tied to the farmgate affair, easing pressure on the president."),
    ]

    grid_top = lead_bottom + 12
    grid_bottom = 848
    col_gap = 38
    col_w = (CONTENT_W - col_gap) // 2
    col_x = [M, M + col_w + col_gap]
    rows = 3
    row_h = (grid_bottom - grid_top) // rows

    s_lab_f = F(SANS_BOLD, 11)
    s_deck_f = F(SERIF, 15)

    for idx, (label, headline, deck_text) in enumerate(stories):
        col = idx % 2
        row = idx // 2
        x = col_x[col]
        top = grid_top + row * row_h

        if row > 0:
            rule(d, M, top - 7, W - M, HAIR, 1)
        if col > 0:
            d.rectangle([M + col_w + col_gap // 2 - 1, top, M + col_w + col_gap // 2, top + row_h - 14], fill=HAIR)

        h_f, h_lines, h_size = fit_headline(
            d, headline, SERIF_BOLD, col_w, 2, 24, 17
        )
        h_lh = int(h_size * 1.12)
        body_lines = wrap(d, deck_text, s_deck_f, col_w)
        block_h = 18 + len(h_lines) * h_lh + 7 + len(body_lines) * 18
        y = top + max(2, (row_h - block_h) // 2 - 4)

        draw_tracked(d, x, y, label, s_lab_f, RED, 1.5)
        y += 18

        for line in h_lines:
            d.text((x, y), line, font=h_f, fill=INK)
            y += h_lh
        y += 7

        for line in body_lines:
            d.text((x, y), line, font=s_deck_f, fill=GREY)
            y += 18

    # Bottom briefs strip ---------------------------------------------------
    strip_top = 860
    rule(d, M, strip_top, W - M, INK, 2)

    brief_f = F(SANS_BOLD, 9)
    draw_tracked(d, M, strip_top + 7, "ALSO ON 25 NOVEMBER 2026", brief_f, RED, 1.6)

    briefs = [
        ("SCIENCE", "Asteroid-defence test images reveal a stadium-sized impact crater."),
        ("MARKETS", "US stocks fall further on renewed fears over artificial intelligence."),
        ("DIPLOMACY", "A sanctions feud with North Korea closes Switzerland's Pyongyang office."),
        ("SPACE", "A Canadian astronaut welcomes a baby born while she was aboard the space station."),
    ]
    b_gap = 22
    b_w = (CONTENT_W - 3 * b_gap) // 4
    b_lab_f = F(SANS_BOLD, 9)
    b_f = F(SERIF, 13)

    for i, (label, text) in enumerate(briefs):
        x = M + i * (b_w + b_gap)
        if i > 0:
            d.rectangle([x - b_gap // 2, strip_top + 6, x - b_gap // 2, 956], fill=HAIR)
        draw_tracked(d, x, strip_top + 25, label, b_lab_f, RED, 1.4)
        by = strip_top + 39
        for line in wrap(d, text, b_f, b_w):
            d.text((x, by), line, font=b_f, fill=INK)
            by += 15

    # Footer ----------------------------------------------------------------
    rule(d, M, 966, W - M, INK, 2)
    foot_f = F(SANS_BOLD, 9)
    draw_tracked_center(
        d, 975,
        "THE WORLD  ·  WEDNESDAY 25 NOVEMBER 2026  ·  PAGE 1",
        foot_f, GREY, 1.6,
    )

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.mode, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
