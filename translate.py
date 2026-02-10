"""
srt_translate.py

Translate an SRT subtitle file using OpenAI gpt-4o.
Splits into safe chunks and rebuilds final translated SRT.

Output file name format:
    [lang].originalfilename.out.srt

Example:
    translate("video.srt", target_lang="es")
"""

import os
import time
from typing import Optional
from pathlib import Path
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

# ---- CONFIG ----
MODEL = "gpt-4o"
MAX_CHARS_PER_CHUNK = 4500  # safe size for stability
SLEEP_BETWEEN_CALLS = 0.5  # be nice to API


client = OpenAI()  # uses OPENAI_API_KEY from environment


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write_file(path: str, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _chunk_text(text: str, max_chars: int):
    """
    Splits text into chunks without breaking subtitle blocks.
    """
    chunks = []
    current = ""

    lines = text.splitlines(keepends=True)

    for line in lines:
        if len(current) + len(line) > max_chars:
            chunks.append(current)
            current = ""

        current += line

    if current:
        chunks.append(current)

    return chunks


def _translate_chunk(chunk: str, target_lang: str) -> str:
    """
    Sends one chunk to OpenAI and returns translated SRT text.
    """

    # pylint: disable=line-too-long
    system_prompt = f"""Translate the following SRT subtitles into the language corresponding to the international language code: '{target_lang}'.

IMPORTANT RULES:
- Translate this SRT into natural, neutral, professional '{target_lang}'
- Keep SRT format EXACTLY
- Do NOT change timestamps
- Do NOT merge or split subtitle numbers
- Do NOT translate Linux system commands, file paths, file names, nor code snippets. Example: this/is/a/path.
- do NOT translate code terms, product names, commands, or file names. Examples: Keep: 'pip install django', Keep: 'python manage.py runserver', Only translate the explanation around these.
- Only translate spoken text
- Keep line breaks

Return ONLY the translated SRT.
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": chunk},
        ],
    )

    if (
        response
        and response.choices
        and len(response.choices) > 0
        and response.choices[0].message
        and response.choices[0].message.content
    ):
        content = response.choices[0].message.content
        if isinstance(content, str):
            # Remove triple backticks and 'srt' language markers
            return content.strip().replace("```srt", "").replace("```", "").strip()
    raise ValueError("No response from OpenAI")


def translate(srt_path: str, target_lang: Optional[str] = None) -> str:
    """
    Translate an SRT file into target language.

    Args:
        srt_path: path to .srt file
        target_lang: language code (default 'es-419')

    Returns:
        output file path
    """

    if not os.path.exists(srt_path):
        raise FileNotFoundError(srt_path)

    if not target_lang:
        raise ValueError("target_lang is required")

    print("Reading file...")
    original_text = _read_file(srt_path)

    print("Chunking...")
    chunks = _chunk_text(original_text, MAX_CHARS_PER_CHUNK)
    print(f"Total chunks: {len(chunks)}")

    translated_chunks: list[str] = []

    for i, chunk in enumerate(chunks, start=1):
        print(f"Translating chunk {i}/{len(chunks)} into {target_lang}...")

        try:
            translated = _translate_chunk(chunk, target_lang)
            translated_chunks.append(translated)
        # pylint: disable=broad-except
        except Exception as e:
            print(f"Error on chunk {i}: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            translated = _translate_chunk(chunk, target_lang)
            translated_chunks.append(translated)

        time.sleep(SLEEP_BETWEEN_CALLS)

    print("Rebuilding file...")
    # Remove code block markers from each chunk
    cleaned_chunks = []
    for chunk in translated_chunks:
        chunk = chunk.strip()
        cleaned_chunks.append(chunk)
    final_text = "\n".join(cleaned_chunks)

    input_path = Path(srt_path)
    output_name = f"{target_lang}.{input_path.stem}.srt"
    output_path = str(input_path.with_name(output_name))

    _write_file(output_path, final_text)

    print(f"Done. Saved to: {output_path}")
    return output_path


def translate_batch(file_path: str):
    """
    Translates the given SRT file into multiple languages.

    Primary languages:
    1.English en
    2.Spanish (LatAm) es-419
    3.Spanish (Spain) es-ES
    4.Portuguese (Brazil) pt-BR
    5.Portuguese (Portugal) pt-PT
    6.French fr
    7.German de
    8.Arabic ar
    9.Hindi hi
    10.Bengali bn
    11.Urdu ur
    12.Indonesian id
    13.Vietnamese vi
    14.Turkish tr
    15.Chinese Simplified zh-Hans

    Secondary languages:
    16.Italian it
    17.Japanese ja
    18.Korean ko
    19.Thai th
    20.Polish pl
    21.Dutch nl

    """
    languages = [
        "en",
        "es-419",
        "es-ES",
        "pt-BR",
        "pt-PT",
        "fr",
        "de",
        "ar",
        "hi",
        "bn",
        "ur",
        "id",
        "vi",
        "tr",
        "zh-Hans",
    ]

    secondary_langs = ["it", "ja", "ko", "th", "pl", "nl"]

    all_langs = languages + secondary_langs

    for lang in all_langs:
        print(f"Translating to {lang}...")
        translate(file_path, lang)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python translate.py input.srt [lang]")
        sys.exit(1)

    file_path = sys.argv[1]
    translate_batch(file_path)
