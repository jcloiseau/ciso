"""Core translation logic for Russian → German translator."""

from translator.dictionary import DICTIONARY, GENDER_ARTICLE


def _normalize(text: str) -> str:
    """Lowercase and strip whitespace."""
    return text.lower().strip()


def _format_noun(entry: dict) -> str:
    """Format a noun translation with its article and gender label.

    Example output: "der Tisch (maskulin)" or "die Katze (feminin, Pl. Katzen)"
    """
    gender = entry["gender"]
    article = GENDER_ARTICLE[gender]
    word = entry["translation"]
    plural = entry.get("plural")

    result = f"{article} {word} ({gender}"
    if plural:
        result += f", Pl. {plural}"
    result += ")"
    return result


def _format_non_noun(entry: dict) -> str:
    """Format a non-noun translation with its part of speech."""
    return f"{entry['translation']} [{entry['pos']}]"


def translate_word(word: str) -> str:
    """Translate a single Russian word to German.

    Returns a formatted string with the translation.
    For nouns, includes the article and gender.
    """
    normalized = _normalize(word)
    entry = DICTIONARY.get(normalized)

    if entry is None:
        return f"'{word}' — nicht im Wörterbuch (not in dictionary)"

    if entry["pos"] == "noun":
        return _format_noun(entry)
    return _format_non_noun(entry)


def translate_text(text: str) -> list[dict]:
    """Translate a sequence of Russian words.

    Tries to match multi-word phrases first (e.g. "до свидания"),
    then falls back to single words.

    Returns a list of dicts:
        {"source": <russian>, "result": <formatted german>}
    """
    words = text.strip().split()
    results = []
    i = 0

    while i < len(words):
        # Try two-word phrase first
        if i + 1 < len(words):
            phrase = _normalize(f"{words[i]} {words[i + 1]}")
            entry = DICTIONARY.get(phrase)
            if entry is not None:
                source = f"{words[i]} {words[i + 1]}"
                if entry["pos"] == "noun":
                    result = _format_noun(entry)
                else:
                    result = _format_non_noun(entry)
                results.append({"source": source, "result": result})
                i += 2
                continue

        # Single word
        w = words[i]
        results.append({"source": w, "result": translate_word(w)})
        i += 1

    return results


def format_translation_output(results: list[dict]) -> str:
    """Format translation results into a readable string."""
    if not results:
        return "Nothing to translate."

    lines = []
    for item in results:
        lines.append(f"  {item['source']}  →  {item['result']}")
    return "\n".join(lines)
