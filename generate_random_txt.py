#!/usr/bin/env python3
"""Generate a text file with random text content of a target size."""

from __future__ import annotations

import argparse
import os
import random
import re
from pathlib import Path

UNITS = {
    "b": 1,
    "kb": 1024,
    "mb": 1024**2,
    "gb": 1024**3,
}

# Weighted toward letters with occasional spaces/newlines so output looks text-like.
CHARSET = b"abcdefghijklmnopqrstuvwxyz      \n"
TRANSLATION_TABLE = bytes(CHARSET[i % len(CHARSET)] for i in range(256))

# Common English words used in meaningful mode.
DEFAULT_WORDS = [
    "time", "person", "year", "way", "day", "thing", "man", "world", "life", "hand",
    "part", "child", "eye", "woman", "place", "work", "week", "case", "point", "government",
    "company", "number", "group", "problem", "fact", "home", "water", "room", "mother", "area",
    "money", "story", "issue", "side", "kind", "head", "house", "service", "friend", "father",
    "power", "hour", "game", "line", "end", "member", "law", "car", "city", "community",
    "name", "president", "team", "minute", "idea", "kid", "body", "information", "back", "parent",
    "face", "others", "level", "office", "door", "health", "art", "war", "history", "party",
    "result", "change", "morning", "reason", "research", "girl", "guy", "moment", "air", "teacher",
    "force", "education", "food", "process", "music", "market", "sense", "nation", "plan", "college",
    "interest", "death", "experience", "effect", "use", "class", "control", "care", "field", "development",
    "role", "effort", "rate", "heart", "drug", "show", "leader", "light", "voice", "wife",
    "police", "mind", "price", "report", "decision", "son", "view", "relationship", "town", "road",
    "drive", "arm", "difference", "value", "building", "action", "model", "season", "society", "tax",
    "director", "position", "player", "record", "paper", "space", "ground", "form", "event", "official",
    "matter", "center", "couple", "site", "project", "activity", "star", "table", "need", "court",
    "oil", "situation", "cost", "industry", "figure", "street", "image", "phone", "data", "picture",
    "practice", "piece", "land", "product", "doctor", "wall", "patient", "worker", "news", "test",
    "movie", "north", "love", "support", "technology", "step", "baby", "computer", "type", "attention",
    "film", "tree", "source", "organization", "hair", "look", "century", "evidence", "window", "culture",
    "chance", "brother", "energy", "period", "course", "summer", "plant", "opportunity", "term", "letter",
    "condition", "choice", "rule", "south", "floor", "campaign", "unit", "pain", "strategy", "bit",
    "science", "memory", "machine", "purpose", "customer", "sound", "series", "quality", "nature", "factor",
    "career", "region", "ability", "station", "population", "success", "training", "performance", "security", "manager",
    "player", "message", "goal", "future", "conversation", "language", "library", "internet", "analysis", "query",
]

SEPARATORS = [".\n", ".\n", ". ", ", ", "; ", "\n"]


def parse_size(size_arg: str, default_unit: str) -> int:
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([kmg]?b?)?\s*", size_arg.lower())
    if not match:
        raise ValueError(
            "Invalid size format. Examples: 2, 1.5, 500mb, 1024kb"
        )

    number_text, suffix = match.groups()
    amount = float(number_text)
    if amount <= 0:
        raise ValueError("Size must be greater than 0.")

    unit = suffix or default_unit
    if unit == "":
        unit = default_unit
    if len(unit) == 1 and unit in {"k", "m", "g"}:
        unit = f"{unit}b"
    if unit not in UNITS:
        raise ValueError("Unit must be one of: b, kb, mb, gb.")

    return int(amount * UNITS[unit])


def build_default_filename(size_arg: str, default_unit: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z._-]", "", size_arg.lower())
    if cleaned and cleaned[-1].isdigit():
        cleaned = f"{cleaned}{default_unit}"
    if not cleaned:
        cleaned = f"output_{default_unit}"
    return f"{cleaned}.txt"


def load_words(word_list_path: str | None) -> list[str]:
    if word_list_path is None:
        return DEFAULT_WORDS

    path = Path(word_list_path).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"Word list file not found: {path}")

    words: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            cleaned = re.sub(r"[^a-zA-Z']", "", raw_line.strip().lower())
            if cleaned:
                words.append(cleaned)

    if not words:
        raise ValueError("Word list file is empty or has no valid words.")

    return words


def build_sentence_block(words: list[str], target_bytes: int = 64 * 1024) -> bytes:
    parts: list[str] = []
    generated = 0

    while generated < target_bytes:
        sentence_length = random.randint(7, 15)
        chosen_words = random.choices(words, k=sentence_length)
        chosen_words[0] = chosen_words[0].capitalize()
        sentence = " ".join(chosen_words) + random.choice(SEPARATORS)
        parts.append(sentence)
        generated += len(sentence)

    return "".join(parts).encode("ascii", errors="ignore")


def write_meaningful_text_file(
    output_path: Path, size_bytes: int, chunk_size: int, words: list[str]
) -> None:
    remaining = size_bytes

    with output_path.open("wb", buffering=1024 * 1024) as handle:
        while remaining > 0:
            current = min(chunk_size, remaining)
            chunk = bytearray()
            while len(chunk) < current:
                block = build_sentence_block(words)
                need = current - len(chunk)
                chunk.extend(block[:need])
            handle.write(chunk)
            remaining -= current


def write_gibberish_text_file(output_path: Path, size_bytes: int, chunk_size: int) -> None:
    randbytes = random.randbytes if hasattr(random, "randbytes") else os.urandom
    remaining = size_bytes

    with output_path.open("wb", buffering=1024 * 1024) as handle:
        while remaining > 0:
            current = min(chunk_size, remaining)
            random_chunk = randbytes(current)
            text_chunk = random_chunk.translate(TRANSLATION_TABLE)
            handle.write(text_chunk)
            remaining -= current


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create a .txt file filled with random text of a requested size."
        )
    )
    parser.add_argument(
        "size",
        help=(
            "Target size. If unit is omitted, --default-unit is used. "
            "Examples: 2, 1.5, 500mb, 2048kb"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path. Default: derived from size (e.g. 2gb.txt)",
    )
    parser.add_argument(
        "--default-unit",
        choices=sorted(UNITS.keys()),
        default="gb",
        help="Unit used when size has no suffix. Default: gb.",
    )
    parser.add_argument(
        "--chunk-mb",
        type=int,
        default=4,
        help="Chunk size in MB used while writing (default: 4).",
    )
    parser.add_argument(
        "--mode",
        choices=["meaningful", "gibberish"],
        default="meaningful",
        help="Text style to generate (default: meaningful).",
    )
    parser.add_argument(
        "--word-list",
        help=(
            "Path to a file with one word per line. Used in meaningful mode "
            "to control generated vocabulary."
        ),
    )
    args = parser.parse_args()

    if args.chunk_mb <= 0:
        raise SystemExit("--chunk-mb must be greater than 0.")

    try:
        size_bytes = parse_size(args.size, args.default_unit)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    output_file = args.output or build_default_filename(args.size, args.default_unit)
    output_path = Path(output_file).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    chunk_size = args.chunk_mb * UNITS["mb"]
    if args.mode == "meaningful":
        try:
            words = load_words(args.word_list)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        write_meaningful_text_file(output_path, size_bytes, chunk_size, words)
    else:
        write_gibberish_text_file(output_path, size_bytes, chunk_size)

    print(f"Created: {output_path}")
    print(f"Size:    {size_bytes} bytes")


if __name__ == "__main__":
    main()
