#!/usr/bin/env python3
"""braille: 一级英文盲文翻译器。

把 ASCII 英文/数字转成 Unicode 盲文点字（U+2800 区），也可反向解码。
纯标准库实现，终端直接运行。
"""

import argparse
import sys

# 一级盲文字母表（a-z），来自 Unicode 盲文点字区公开编码
LETTERS = {
    "a": "\u2801", "b": "\u2803", "c": "\u2809", "d": "\u2819",
    "e": "\u2811", "f": "\u280b", "g": "\u281b", "h": "\u2813",
    "i": "\u280a", "j": "\u281a", "k": "\u2805", "l": "\u2807",
    "m": "\u280d", "n": "\u281d", "o": "\u2815", "p": "\u280f",
    "q": "\u281f", "r": "\u2817", "s": "\u280e", "t": "\u281e",
    "u": "\u2825", "v": "\u2827", "w": "\u283a", "x": "\u282d",
    "y": "\u283d", "z": "\u2835",
}
REVERSE_LETTERS = {v: k for k, v in LETTERS.items()}

NUMBER_SIGN = "\u283c"   # ⠼ 数字符
CAPITAL_SIGN = "\u2820"  # ⠠ 大写符
LETTER_SIGN = "\u2828"    # ⠰ 字母符：数字后紧跟 a-j 时用它消歧
DIGIT_MAP = {  # 数字用 a-j 表示
    "1": "a", "2": "b", "3": "c", "4": "d", "5": "e",
    "6": "f", "7": "g", "8": "h", "9": "i", "0": "j",
}
REVERSE_DIGITS = {LETTERS[v]: k for k, v in DIGIT_MAP.items()}


def encode(text):
    """文本 -> 盲文。未知字符原样透传（见 README 已知局限）。"""
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isdigit():
            out.append(NUMBER_SIGN)
            while i < n and text[i].isdigit():
                out.append(LETTERS[DIGIT_MAP[text[i]]])
                i += 1
            # 数字后紧跟 a-j 会产生歧义（a-j 的点字兼作数字），用字母符消歧
            if i < n and text[i].lower() in "abcdefghij" and text[i].isalpha():
                out.append(LETTER_SIGN)
            continue
        if ch.isalpha() and ch.lower() in LETTERS:
            if ch.isupper():
                out.append(CAPITAL_SIGN)
            out.append(LETTERS[ch.lower()])
        else:
            out.append(ch)  # 空格/标点/中文等：原样透传
        i += 1
    return "".join(out)


def decode(text):
    """盲文 -> 文本。未知点字原样透传。"""
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == NUMBER_SIGN:
            i += 1
            while i < n and text[i] in REVERSE_DIGITS:
                out.append(REVERSE_DIGITS[text[i]])
                i += 1
            continue
        if ch == CAPITAL_SIGN:
            i += 1
            if i < n and text[i] in REVERSE_LETTERS:
                out.append(REVERSE_LETTERS[text[i]].upper())
                i += 1
            continue
        if ch == LETTER_SIGN:
            i += 1
            if i < n and text[i] in REVERSE_LETTERS:
                out.append(REVERSE_LETTERS[text[i]])
                i += 1
            continue
        if ch in REVERSE_LETTERS:
            out.append(REVERSE_LETTERS[ch])
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="braille",
        description="一级英文盲文翻译器：文本 <-> Unicode 盲文点字",
    )
    ap.add_argument("text", nargs="?", help="要翻译的文本（省略则从 stdin 读）")
    ap.add_argument("--decode", action="store_true", help="反向：盲文 -> 文本")
    args = ap.parse_args(argv)

    if args.text is not None:
        text = args.text
    elif sys.stdin.isatty():
        ap.error("请给出文本或通过管道输入")
        return 2
    else:
        text = sys.stdin.read()

    print(decode(text) if args.decode else encode(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
