"""Tests for the Russian → German translator."""

import pytest

from translator.core import translate_word, translate_text, format_translation_output
from translator.dictionary import DICTIONARY, GENDER_ARTICLE, lookup


class TestDictionary:
    def test_lookup_existing_word(self):
        entry = lookup("кошка")
        assert entry is not None
        assert entry["translation"] == "Katze"
        assert entry["gender"] == "feminin"

    def test_lookup_missing_word(self):
        assert lookup("абракадабра") is None

    def test_lookup_case_insensitive(self):
        entry = lookup("Кошка")
        assert entry is not None
        assert entry["translation"] == "Katze"

    def test_lookup_strips_whitespace(self):
        entry = lookup("  кошка  ")
        assert entry is not None

    def test_all_nouns_have_gender(self):
        for word, entry in DICTIONARY.items():
            if entry["pos"] == "noun":
                assert entry["gender"] in ("maskulin", "feminin", "neutrum"), (
                    f"Noun '{word}' missing valid gender"
                )

    def test_all_non_nouns_have_none_gender(self):
        for word, entry in DICTIONARY.items():
            if entry["pos"] != "noun":
                assert entry["gender"] is None, (
                    f"Non-noun '{word}' ({entry['pos']}) should have gender=None"
                )

    def test_gender_articles_complete(self):
        assert set(GENDER_ARTICLE.keys()) == {"maskulin", "feminin", "neutrum"}


class TestTranslateWord:
    def test_masculine_noun(self):
        result = translate_word("стол")
        assert "der" in result
        assert "Tisch" in result
        assert "maskulin" in result

    def test_feminine_noun(self):
        result = translate_word("кошка")
        assert "die" in result
        assert "Katze" in result
        assert "feminin" in result

    def test_neuter_noun(self):
        result = translate_word("окно")
        assert "das" in result
        assert "Fenster" in result
        assert "neutrum" in result

    def test_noun_with_plural(self):
        result = translate_word("дом")
        assert "Häuser" in result
        assert "Pl." in result

    def test_verb(self):
        result = translate_word("читать")
        assert "lesen" in result
        assert "[verb]" in result

    def test_adjective(self):
        result = translate_word("большой")
        assert "groß" in result
        assert "[adjective]" in result

    def test_unknown_word(self):
        result = translate_word("абракадабра")
        assert "nicht im Wörterbuch" in result

    def test_pronoun(self):
        result = translate_word("я")
        assert "ich" in result
        assert "[pronoun]" in result

    def test_preposition(self):
        result = translate_word("в")
        assert "in" in result
        assert "[preposition]" in result


class TestTranslateText:
    def test_single_word(self):
        results = translate_text("кошка")
        assert len(results) == 1
        assert results[0]["source"] == "кошка"
        assert "Katze" in results[0]["result"]

    def test_multiple_words(self):
        results = translate_text("большой дом")
        assert len(results) == 2
        assert results[0]["source"] == "большой"
        assert results[1]["source"] == "дом"

    def test_multi_word_phrase(self):
        results = translate_text("до свидания")
        assert len(results) == 1
        assert results[0]["source"] == "до свидания"
        assert "Wiedersehen" in results[0]["result"]

    def test_empty_string(self):
        results = translate_text("")
        assert results == []

    def test_mixed_known_unknown(self):
        results = translate_text("кошка абракадабра")
        assert len(results) == 2
        assert "Katze" in results[0]["result"]
        assert "nicht im Wörterbuch" in results[1]["result"]


class TestFormatOutput:
    def test_empty_results(self):
        assert format_translation_output([]) == "Nothing to translate."

    def test_single_result(self):
        results = [{"source": "кошка", "result": "die Katze (feminin)"}]
        output = format_translation_output(results)
        assert "кошка" in output
        assert "→" in output
        assert "die Katze" in output

    def test_multiple_results(self):
        results = [
            {"source": "я", "result": "ich [pronoun]"},
            {"source": "читать", "result": "lesen [verb]"},
        ]
        output = format_translation_output(results)
        lines = output.strip().split("\n")
        assert len(lines) == 2
