#!/usr/bin/env python3
"""Regression tests for clean_srt.split_sentence_text and split_long_segments.

Run standalone:
    python3 scripts/test_clean_srt.py

Or via pytest:
    pytest scripts/test_clean_srt.py

Covers the two historical bugs:
  1. CJK regex missed sentences that concatenated without whitespace
     ("A。B。C。" used to stay as one chunk because the regex required
     \\s+|$ after the punctuation — English-only assumption).
  2. A single long-but-punctuated sentence got hard-split mid-word when
     it barely exceeded the length cap. Cap must only apply to non-sentences.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clean_srt import split_sentence_text, split_long_segments  # noqa: E402


def check(name, got, expected):
    ok = got == expected
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}")
    if not ok:
        print(f"         expected: {expected}")
        print(f"         got:      {got}")
    return ok


def test_split_sentence_text():
    print("split_sentence_text:")
    results = []

    # 1. Simple English with ". " separators.
    results.append(check(
        "english multi-sentence",
        split_sentence_text("Hello world. This is a test. Great."),
        ["Hello world.", "This is a test.", "Great."],
    ))

    # 2. CJK multi-sentence with NO whitespace between. This is the bug
    #    that produced the crammed caption on entry #33.
    results.append(check(
        "cjk multi-sentence no spaces",
        split_sentence_text("他们的处境当然很不一样。所以他们会继续升级。我认为谈判最终会发生。"),
        ["他们的处境当然很不一样。", "所以他们会继续升级。", "我认为谈判最终会发生。"],
    ))

    # 3. Single long sentence — 23 CJK chars, one `。`, over the 22-char cap.
    #    Must stay intact (this was the second regression). Use a sentence
    #    whose character count is exactly at the boundary.
    long_sentence = "他们一年三百六十五天、每天二十四小时都在打这场仗。"
    results.append(check(
        "long single cjk sentence stays intact",
        split_sentence_text(long_sentence),
        [long_sentence],
    ))

    # 4. Trailing fragment with comma, no terminal punctuation — passes
    #    through when under the length cap (don't force-split fragments).
    fragment = "那是一个教派分治的政府，"
    results.append(check(
        "short cjk fragment passes through",
        split_sentence_text(fragment),
        [fragment],
    ))

    # 5. Mixed punctuation — English `?` and `!` and CJK `。`.
    results.append(check(
        "mixed punctuation",
        split_sentence_text("Are you ready? I am ready! 我准备好了。"),
        ["Are you ready?", "I am ready!", "我准备好了。"],
    ))

    # 6. Truly unpunctuated long English run-on falls through to word cap.
    run_on = " ".join(["word"] * 40)
    chunks = split_sentence_text(run_on)
    results.append(check(
        "unpunctuated english run-on hard-split",
        len(chunks) >= 2 and all(len(c.split()) <= 15 for c in chunks),
        True,
    ))

    # 7. Short single sentence — returns as one chunk.
    results.append(check(
        "short sentence one chunk",
        split_sentence_text("Yes."),
        ["Yes."],
    ))

    # 8. Empty input.
    results.append(check("empty input", split_sentence_text(""), []))
    results.append(check("whitespace only", split_sentence_text("   "), []))

    # 9. CJK compound sentence: ASR joined multiple clauses with `,` and
    #    only put one `。` at the end. Must be split on commas.
    compound = "京剧张军秋在演出后场时喜欢吃东西,曾一次吃了40个饺子,罪名是贪图口腹养尊处优,与普通群众生活脱节。"
    chunks = split_sentence_text(compound)
    results.append(check("cjk compound sentence splits on commas",
                         len(chunks) == 4, True))
    results.append(check("cjk compound first clause",
                         chunks[0].startswith("京剧张军秋") and chunks[0].endswith(","),
                         True))
    results.append(check("cjk compound last clause ends with 。",
                         chunks[-1].endswith("。"), True))

    # 10. Short English sentence WITH commas — must stay whole (regression
    #     guard: do not over-split short compound sentences).
    short_en_compound = "I went to the store, bought some milk, and came home."
    results.append(check("short english compound stays whole",
                         split_sentence_text(short_en_compound),
                         [short_en_compound]))

    # 11. Long English compound sentence — should comma-split when over cap.
    long_en_compound = (
        "I went to the store on Monday morning, "
        "bought a loaf of bread and some milk for breakfast, "
        "and then walked back home through the park slowly."
    )
    chunks = split_sentence_text(long_en_compound)
    results.append(check("long english compound splits",
                         len(chunks) >= 2, True))

    return all(results)


def test_split_long_segments():
    """End-to-end: full SRT block with a multi-sentence CJK entry."""
    print("split_long_segments:")
    srt_in = (
        "1\n"
        "00:00:00,000 --> 00:00:10,000\n"
        "他们的处境当然很不一样。所以他们会继续升级。我认为谈判最终会发生。\n"
    )
    out = split_long_segments(srt_in)
    blocks = [b for b in out.strip().split("\n\n") if b.strip()]
    ok1 = check("splits 1 block into 3", len(blocks), 3)

    # Each block should be a valid SRT entry.
    ok2 = all(
        len(b.split("\n")) >= 3 and " --> " in b.split("\n")[1]
        for b in blocks
    )
    ok2 = check("each output block is valid srt", ok2, True)

    # Times should be monotonically increasing and cover [0, 10].
    def parse_ts(ts):
        h, m, rest = ts.split(":")
        s, ms = rest.replace(",", ".").split(".")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

    starts_ends = []
    for b in blocks:
        lines = b.split("\n")
        a, c = lines[1].split(" --> ")
        starts_ends.append((parse_ts(a), parse_ts(c)))

    ok3 = check("first block starts at 0.0", starts_ends[0][0], 0.0)
    ok4 = check("last block ends at 10.0", starts_ends[-1][1], 10.0)
    ok5 = check(
        "blocks are contiguous",
        all(starts_ends[i + 1][0] == starts_ends[i][1] for i in range(len(starts_ends) - 1)),
        True,
    )

    return all([ok1, ok2, ok3, ok4, ok5])


def main():
    ok_a = test_split_sentence_text()
    ok_b = test_split_long_segments()
    if ok_a and ok_b:
        print("\nAll clean_srt tests passed.")
        return 0
    print("\nSOME TESTS FAILED.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
