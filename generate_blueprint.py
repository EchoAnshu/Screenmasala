#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_blueprint.py
=====================
Generates "Complete_Project_Blueprint.pdf" -- a full study guide for the
ScreenMasala project (Flask + vanilla HTML/CSS/JS movie browser).

The PDF contains three masterclass sections:
    1. THE ELI5 OVERVIEW          -- plain-English, kid-friendly metaphors
    2. THE LINE-BY-LINE STUDY     -- every file, code blocks + breakdowns
    3. THE CONNECTIVITY PIPELINE  -- how data flows browser <-> Flask <-> TMDB

Requires:
    pip install reportlab

Run:
    python generate_blueprint.py

Output:
    Complete_Project_Blueprint.pdf (same folder as this script)
"""

import os
import textwrap
import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    XPreformatted, KeepTogether, HRFlowable,
)

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_NAME = "Complete_Project_Blueprint.pdf"
OUTPUT_PATH = os.path.join(BASE, OUTPUT_NAME)
CODE_WRAP = 100          # characters per wrapped code line
PAGE_W, PAGE_H = A4
MARGIN = 18 * mm

ACCENT = colors.HexColor("#8a6d1f")      # warm gold, readable on white
INK = colors.HexColor("#1c1c1e")
DIM = colors.HexColor("#555555")
CODE_BG = colors.HexColor("#f4f2ec")
RULE = colors.HexColor("#d8d2c4")

# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------
S = {}
S["cover_title"] = ParagraphStyle(
    "cover_title", fontName="Helvetica-Bold", fontSize=27, leading=33,
    alignment=TA_CENTER, textColor=INK, spaceAfter=8)
S["cover_sub"] = ParagraphStyle(
    "cover_sub", fontName="Helvetica", fontSize=12.5, leading=18,
    alignment=TA_CENTER, textColor=DIM, spaceAfter=4)
S["h1"] = ParagraphStyle(
    "h1", fontName="Helvetica-Bold", fontSize=19, leading=24,
    textColor=ACCENT, spaceBefore=6, spaceAfter=4)
S["h2"] = ParagraphStyle(
    "h2", fontName="Helvetica-Bold", fontSize=13.5, leading=18,
    textColor=INK, spaceBefore=12, spaceAfter=5)
S["h3"] = ParagraphStyle(
    "h3", fontName="Helvetica-Bold", fontSize=11, leading=15,
    textColor=INK, spaceBefore=9, spaceAfter=3)
S["body"] = ParagraphStyle(
    "body", fontName="Helvetica", fontSize=10, leading=14.5,
    alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6)
S["bullet"] = ParagraphStyle(
    "bullet", parent=S["body"], leftIndent=14, bulletIndent=4, spaceAfter=3)
S["note"] = ParagraphStyle(
    "note", fontName="Helvetica-Oblique", fontSize=9, leading=12.5,
    textColor=DIM, spaceAfter=6)
S["code"] = ParagraphStyle(
    "code", fontName="Courier", fontSize=7.4, leading=9.6,
    textColor=INK, backColor=CODE_BG, borderColor=RULE, borderWidth=0.5,
    borderPadding=6, leftIndent=0, spaceBefore=3, spaceAfter=5)
S["explain"] = ParagraphStyle(
    "explain", fontName="Helvetica", fontSize=9.4, leading=13,
    textColor=colors.HexColor("#2f2f33"), leftIndent=12, spaceAfter=6)
S["filetag"] = ParagraphStyle(
    "filetag", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
    textColor=colors.white, backColor=ACCENT, borderPadding=4,
    spaceBefore=4, spaceAfter=6)
S["mono_inline"] = ParagraphStyle(
    "mono_inline", fontName="Courier", fontSize=9.2, leading=13,
    textColor=INK, leftIndent=12, spaceAfter=5)

# ---------------------------------------------------------------------------
# Flowable helpers
# ---------------------------------------------------------------------------
story = []


def h1(text):
    story.append(Paragraph(text, S["h1"]))
    story.append(HRFlowable(width="100%", thickness=1.1, color=ACCENT,
                            spaceBefore=1, spaceAfter=9))


def h2(text):
    story.append(Paragraph(text, S["h2"]))


def h3(text):
    story.append(Paragraph(text, S["h3"]))


def p(text):
    story.append(Paragraph(text, S["body"]))


def bullet(text):
    story.append(Paragraph(text, S["bullet"], bulletText="•"))


def note(text):
    story.append(Paragraph(text, S["note"]))


def spacer(h=6):
    story.append(Spacer(1, h))


def escape_code(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def wrap_code(text, width=CODE_WRAP):
    out = []
    for line in text.replace("\t", "    ").split("\n"):
        if len(line) <= width:
            out.append(line)
            continue
        indent = len(line) - len(line.lstrip(" "))
        wrapped = textwrap.wrap(
            line, width=width,
            subsequent_indent=" " * min(indent + 4, 60),
            drop_whitespace=False, replace_whitespace=False,
            break_long_words=True, break_on_hyphens=False)
        out.extend(wrapped if wrapped else [line])
    return "\n".join(out)


def code(text):
    wrapped = escape_code(wrap_code(text.rstrip("\n")))
    story.append(XPreformatted(wrapped if wrapped else " ", S["code"]))


def explain(text):
    story.append(Paragraph(text, S["explain"]))


# ---------------------------------------------------------------------------
# SECTION 1 -- THE ELI5 OVERVIEW
# ---------------------------------------------------------------------------
ELI5 = [
    ("h2", "The Big Picture: A Tiny Restaurant Called ScreenMasala"),
    ("p",
     "Imagine your whole project folder is a little restaurant. Each file has a "
     "job, exactly like the people and rooms in a restaurant. Nobody does "
     "everything alone -- they pass notes, plates and tickets to each other all "
     "day long. Once you see the roles, the whole codebase stops looking scary."),
    ("p",
     "<b>index.html is the front door and dining room.</b> It is the first room a "
     "visitor walks into. It has a big sign (the hero banner), a menu of movies, "
     "and little name plates that say things like 'Trending Now'. When your "
     "browser opens index.html, it is literally walking into the dining room."),
    ("p",
     "<b>The other .html files are the other rooms.</b> movies.html is the "
     "movies room, tvshows.html is the TV room, search.html is the help desk, "
     "login.html and register.html are the front counter, profile.html is your "
     "own locker, watchlist.html is the shelf where you keep the movies you want "
     "to watch later, and details.html is the room you enter to look closely at "
     "one single movie. Every room has the same doorway (the navbar), so you can "
     "always walk between rooms."),
    ("p",
     "<b>css/style.css is the paint, wallpaper and lighting.</b> It is one shared "
     "box of decorations used by every room. The HTML files only say 'this is a "
     "movie card'; the CSS says 'a movie card is this wide, has rounded corners, "
     "big white text, and lifts up a little when you point at it'. Because the "
     "decoration box is shared, change the colour once here and every room "
     "changes colour at the same time."),
    ("p",
     "<b>js/script.js is the waiter.</b> The waiter is the only one who moves "
     "around. When you click a movie poster, the waiter writes a little note "
     "('take this person to details.html and show movie number 603'), carries "
     "you there, and then phones the kitchen to ask for the real information. "
     "The waiter never changes the walls of the restaurant (that is CSS) and "
     "never cooks (that is Python). The waiter just carries things back and "
     "forth and places them on your table."),
    ("p",
     "<b>app.py is the kitchen manager with the recipe book.</b> It is written in "
     "Python and it runs on your computer, not in the browser. The recipe book "
     "is a list of instructions, and each instruction has a name like "
     "'/api/movies' or '/api/details'. When a request arrives, the manager flips "
     "to the matching page of the book and follows that recipe exactly."),
    ("p",
     "<b>.env is the locked safe.</b> Inside the safe are two very secret things: "
     "a membership card for the giant movie library across town (the TMDB API "
     "token) and the key to the back-room filing cabinet (the database "
     "password). The kitchen manager is the only one who opens the safe. Nobody "
     "in the dining room ever sees what is inside -- and that is exactly why the "
     "safe is never shown on screen or in this blueprint."),
    ("p",
     "<b>PostgreSQL is the filing cabinet in the back room.</b> It remembers "
     "things forever: which customers exist (the users table) and which movies "
     "each customer saved for later (the watchlist table). The kitchen manager "
     "walks to the cabinet, pulls out the right drawer, and reads or writes one "
     "card at a time."),
    ("p",
     "<b>TMDB is the giant public movie library across town.</b> It knows every "
     "movie, every poster picture, every rating and every actor. Your kitchen "
     "does not try to memorise all those movies. Instead, when someone asks for "
     "a movie, the manager walks over to the library, shows the membership card "
     "from the safe, and comes back with a lunchbox full of information."),
    ("h2", "The Journey of One Click, Told as a Story"),
    ("p",
     "You are standing in the dining room (index.html). You point at a movie "
     "poster. Here is everything that happens next, translated into restaurant "
     "words:"),
    ("bullet",
     "<b>Step 1 -- you point.</b> You click a card. The card is not a real link; "
     "it is a puzzle piece the waiter built earlier, and the waiter secretly "
     "pasted a sticky note on it: 'if someone points at me, take them to "
     "details.html?id=603&amp;type=movie'."),
    ("bullet",
     "<b>Step 2 -- the waiter carries you.</b> The browser opens the details.html "
     "room. The room looks almost empty, because the walls only have empty "
     "frames (Loading...) waiting for pictures."),
    ("bullet",
     "<b>Step 3 -- the waiter reads the sticky note.</b> script.js sees "
     "'id=603' and 'type=movie' in the address bar and phones the kitchen with "
     "a text message (fetch). A text message is special: nobody leaves the room, "
     "and the page does not reload. The waiter just waits near the door."),
    ("bullet",
     "<b>Step 4 -- the kitchen manager takes the order.</b> app.py hears a knock "
     "on the door marked '/api/details'. It checks that the order makes sense "
     "(is the id really a number? is the type really 'movie' or 'tv'?)."),
    ("bullet",
     "<b>Step 5 -- the manager visits the library.</b> app.py shows the secret "
     "membership card from the safe and asks the TMDB library about movie 603. "
     "The manager is clever: it first checks a small notepad of recent answers "
     "(the cache), and if the library's phone line is busy, it patiently tries "
     "again two more times before giving up."),
    ("bullet",
     "<b>Step 6 -- the lunchbox comes back.</b> The library returns a packed "
     "lunchbox written in a language both sides understand (JSON): title, year, "
     "rating, poster path, description."),
    ("bullet",
     "<b>Step 7 -- the waiter unpacks it on your table.</b> script.js takes the "
     "lunchbox, puts the title into the heading, the rating into the About box, "
     "the poster into the frame, and the description into the paragraph. All of "
     "this happens in place, in the same room, without a reload."),
    ("bullet",
     "<b>Step 8 -- the painter makes it pretty.</b> style.css makes sure the "
     "newly filled frames look right: gold accent text, soft borders, the "
     "poster with rounded corners."),
    ("h2", "The Puzzle-Piece Rule"),
    ("p",
     "Think of the four front-end files as puzzle pieces with tabs and holes: "
     "HTML is the picture printed on the pieces, CSS is the paint, JavaScript "
     "is the hands that snap pieces together while you watch, and Python is the "
     "machine in the next room that manufactures new pieces on demand. If you "
     "ever feel lost while reading the code, ask yourself one question: <b>is "
     "this file decorating, carrying, cooking, or remembering?</b> Decorate = "
     "CSS. Carry = JS. Cook = app.py. Remember = Postgres."),
    ("note",
     "The .env file is deliberately NOT printed line-by-line in this document. "
     "It contains live secrets (the TMDB token and the database password). "
     "Section 2 shows its structure with the values redacted instead."),
]

# @@PART2@@
