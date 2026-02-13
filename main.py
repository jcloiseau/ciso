#!/usr/bin/env python3
"""Russian → German Translator with noun gender annotations.

Usage:
    Interactive mode:  python main.py
    Single word:       python main.py кошка
    Sentence:          python main.py большой дом
"""

from translator.cli import main

if __name__ == "__main__":
    main()
