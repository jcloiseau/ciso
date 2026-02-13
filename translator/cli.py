"""Command-line interface for the Russian → German translator."""

import sys

from translator.core import format_translation_output, translate_text, translate_word


BANNER = r"""
╔══════════════════════════════════════════════╗
║   Русско-Немецкий Переводчик                 ║
║   Russisch → Deutsch Übersetzer              ║
║                                              ║
║   Nouns always show gender:                  ║
║     der = maskulin  (masculine)              ║
║     die = feminin   (feminine)               ║
║     das = neutrum   (neuter)                 ║
║                                              ║
║   Type a Russian word or sentence.           ║
║   Commands: /help  /list  /quit              ║
╚══════════════════════════════════════════════╝
"""

HELP_TEXT = """
Commands:
  /help        Show this help message
  /list        List all available words in the dictionary
  /list nouns  List only nouns (with genders)
  /quit        Exit the translator

Usage:
  Type any Russian word or several words separated by spaces.
  Nouns will be shown with their German article and gender.

Examples:
  > кошка
    die Katze (feminin, Pl. Katzen)

  > большой дом
    groß [adjective]
    das Haus (neutrum, Pl. Häuser)
"""


def _list_words(filter_pos: str | None = None) -> None:
    """Print dictionary entries, optionally filtered by part of speech."""
    from translator.dictionary import DICTIONARY, GENDER_ARTICLE

    entries = []
    for rus, entry in sorted(DICTIONARY.items()):
        if filter_pos and entry["pos"] != filter_pos:
            continue
        if entry["pos"] == "noun":
            article = GENDER_ARTICLE[entry["gender"]]
            line = f"  {rus:20s} → {article} {entry['translation']} ({entry['gender']})"
        else:
            line = f"  {rus:20s} → {entry['translation']} [{entry['pos']}]"
        entries.append(line)

    print(f"\n  {len(entries)} entries:\n")
    for line in entries:
        print(line)
    print()


def _handle_command(cmd: str) -> bool:
    """Handle a slash command. Returns True if the app should exit."""
    parts = cmd.strip().split()
    command = parts[0].lower()

    if command == "/quit":
        print("\nAuf Wiedersehen! До свидания!\n")
        return True
    elif command == "/help":
        print(HELP_TEXT)
    elif command == "/list":
        pos_filter = parts[1] if len(parts) > 1 else None
        if pos_filter == "nouns":
            pos_filter = "noun"
        _list_words(pos_filter)
    else:
        print(f"  Unknown command: {command}. Type /help for available commands.\n")

    return False


def run_interactive() -> None:
    """Run the translator in interactive (REPL) mode."""
    print(BANNER)

    while True:
        try:
            user_input = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nАuf Wiedersehen! До свидания!\n")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            if _handle_command(user_input):
                break
            continue

        results = translate_text(user_input)
        output = format_translation_output(results)
        print(output)
        print()


def run_single(text: str) -> None:
    """Translate a single input passed as a CLI argument and print result."""
    results = translate_text(text)
    print(format_translation_output(results))


def main() -> None:
    """Entry point for the CLI."""
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        run_single(text)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
