
#!/usr/bin/env python3
"""Import public YouTube recordings for Grace Chapel.

Requires YOUTUBE_API_KEY.
Uses the public YouTube Data API v3.
Preserves manually curated sermon overrides.
"""

import os
import json
import re
import urllib.parse
import urllib.request
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

KEY = os.getenv("YOUTUBE_API_KEY")
HANDLE = os.getenv("YOUTUBE_HANDLE", "goodnews4folkestone")

if not KEY:
    sys.exit("Set YOUTUBE_API_KEY (Google Cloud YouTube Data API v3).")


def api(path, **params):
    url = (
        "https://www.googleapis.com/youtube/v3/"
        + path
        + "?"
        + urllib.parse.urlencode(dict(params, key=KEY))
    )

    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


BIBLE_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
    "Ezra", "Nehemiah", "Esther", "Job", "Psalms",
    "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea",
    "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum",
    "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians",
    "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus",
    "Philemon", "Hebrews", "James", "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John", "Jude", "Revelation"
]

ALIASES = {
    "Psalm": "Psalms",
    "Song of Songs": "Song of Solomon",
    "Canticles": "Song of Solomon"
}

MEETING_TYPES = {
    "gospel": "Gospel",
    "gospel service": "Gospel",
    "teaching": "Teaching",
    "teaching service": "Teaching",
    "bible study": "Bible Study",
    "bible studies": "Bible Study",
    "bible study meeting": "Bible Study"
}

BOOK_NAMES = sorted(
    BIBLE_BOOKS + list(ALIASES),
    key=len,
    reverse=True
)

BOOK_PATTERN = "|".join(
    re.escape(name).replace(r"\ ", r"\s+")
    for name in BOOK_NAMES
)

# Recognise references such as:
# Ephesians 6v18
# Luke 9v28-36
# 2 Kings 5v1-14
# John 18v28-19v12
# Ephesians 6:18
# Psalm 23
#
# A chapter number is required, preventing names such
# as Joshua Oliver or John Wycliffe from matching.

REFERENCE_PATTERN = re.compile(
    r"(?<!\w)(?P<book>" + BOOK_PATTERN + r")"
    r"\s+(?P<chapter>\d{1,3})"
    r"(?:\s*(?:[:vV]|\bverses?\b)\s*\d{1,3})?"
    r"(?:\s*[-–]\s*(?:\d{1,3}\s*[:vV]\s*)?\d{1,3})?"
    r"\b",
    re.IGNORECASE
)

PASSAGE_FIELD = re.compile(
    r"^\s*(?:Bible\s+Passage|Scripture(?:\s+Reading)?|"
    r"Bible\s+Reading|Passage|Text)\s*:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE
)

MEETING_FIELD = re.compile(
    r"^\s*(?:Meeting\s+Type|Service\s+Type)\s*:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE
)


def canonical_book(value):
    for name in BOOK_NAMES:
        if name.lower() == value.lower():
            return ALIASES.get(name, name)

    return None


def extract_book(title, description):
    # Explicit Bible Passage or Scripture metadata
    # takes priority over the video title.

    for field in PASSAGE_FIELD.finditer(description):
        match = REFERENCE_PATTERN.search(field.group(1))

        if match:
            return canonical_book(match.group("book"))

    # Check the title for a proper Scripture reference.

    match = REFERENCE_PATTERN.search(title)

    if match:
        return canonical_book(match.group("book"))

    # Finally, examine description lines for references.

    for line in description.splitlines():
        match = REFERENCE_PATTERN.search(line)

        if match:
            return canonical_book(match.group("book"))

    # Do not guess if no valid reference is found.

    return None


def extract_meeting_type(title, description):
    # Prefer explicitly labelled YouTube metadata.

    match = MEETING_FIELD.search(description)

    if match:
        value = match.group(1).strip().lower()
        value = re.sub(r"\s+", " ", value)

        return MEETING_TYPES.get(value)

    # Recognise clear meeting labels in video titles.

    patterns = [
        (r"\bBible\s+Study\b", "Bible Study"),
        (r"\bGospel\s+Service\b", "Gospel"),
        (r"\bTeaching\s+Service\b", "Teaching")
    ]

    for pattern, category in patterns:
        if re.search(pattern, title, re.IGNORECASE):
            return category

    return None


def extract_preacher(description):
    # Recognise explicit preacher attributions.

    match = re.search(
        r"\b(?:"
        r"preached\s+by|"
        r"preached\s+at\b[^.]{0,150}?\bby|"
        r"preacher\s*:?\s*|"
        r"speaker\s*:?\s*|"
        r"(?:ministry|message|sermon|preaching)\s+by"
        r")\s+"
        r"(?:(?:Pastor|Rev\.?|Elder|Deacon)\s+)?"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b",
        description,
        re.IGNORECASE
    )

    preacher = match.group(1) if match else None

    if preacher:
        preacher = re.split(
            r"\s+(?:on|at|and|the|with|from|in|for|Hymn)\b",
            preacher,
            maxsplit=1,
            flags=re.IGNORECASE
        )[0].strip()

        preacher = re.sub(
            r"^(?:Pastor|Rev\.?|Ptr|Elder|Deacon)\s+",
            "",
            preacher,
            flags=re.IGNORECASE
        )

    return preacher


def extract_preached_date(description):
    match = re.search(
        r"\b(?:Sunday\s+(?:the\s+)?)?"
        r"(\d{1,2})(?:st|nd|rd|th)?\s+"
        r"(?:of\s+)?"
        r"(January|February|March|April|May|June|July|"
        r"August|September|October|November|December)\s+"
        r"(20\d\d|19\d\d)\b",
        description,
        re.IGNORECASE
    )

    if match:
        try:
            return datetime.datetime.strptime(
                f"{match.group(1)} {match.group(2)} {match.group(3)}",
                "%d %B %Y"
            ).date().isoformat()

        except ValueError:
            pass

    return None


def classify(title, description):
    return {
        "book": extract_book(title, description),
        "preacher": extract_preacher(description),
        "preached": extract_preached_date(description),
        "meeting_type": extract_meeting_type(title, description)
    }


# Find the YouTube channel's uploads playlist.

channel = api(
    "channels",
    part="contentDetails",
    forHandle=HANDLE
).get("items", [])

if not channel:
    sys.exit("YouTube channel not found; check handle.")

playlist = channel[0]["contentDetails"]["relatedPlaylists"]["uploads"]


# Retrieve every uploaded video ID.

ids = []
token = None

while True:
    args = {
        "part": "contentDetails",
        "playlistId": playlist,
        "maxResults": 50
    }

    if token:
        args["pageToken"] = token

    page = api("playlistItems", **args)

    ids.extend(
        item["contentDetails"]["videoId"]
        for item in page.get("items", [])
        if item.get("contentDetails", {}).get("videoId")
    )

    token = page.get("nextPageToken")

    if not token:
        break


# Retrieve details for public videos.

records = []

for offset in range(0, len(ids), 50):
    page = api(
        "videos",
        part="snippet,status",
        id=",".join(ids[offset:offset + 50]),
        maxResults=50
    )

    for video in page.get("items", []):
        if video.get("status", {}).get("privacyStatus") != "public":
            continue

        snippet = video["snippet"]

        title = snippet.get("title", "Untitled sermon")
        description = snippet.get("description", "")

        metadata = classify(title, description)

        records.append({
            "id": video["id"],
            "title": title,
            "book": metadata["book"],
            "preacher": metadata["preacher"],
            "preached": metadata["preached"],
            "meeting_type": metadata["meeting_type"],
            "series": None,
            "description": description,
            "uploaded": snippet.get("publishedAt", ""),
            "source": "youtube"
        })


# Preserve editor-curated overrides.
# These take priority over automatically detected metadata.

overrides_file = ROOT / "data" / "sermon-overrides.json"

if overrides_file.exists():
    overrides = json.loads(
        overrides_file.read_text(encoding="utf-8")
    )

    for item in records:
        item.update(overrides.get(item["id"], {}))


# Sort recordings by preaching date.

records.sort(
    key=lambda item: (
        item.get("preached") or item.get("uploaded") or ""
    ),
    reverse=True
)


# Write the updated sermon catalogue.

output_file = ROOT / "data" / "sermons.json"

output_file.write_text(
    json.dumps(
        {
            "updated": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "sermons": records
        },
        indent=2,
        ensure_ascii=False
    ) + "\n",
    encoding="utf-8"
)

print("Saved", len(records), "public videos")
