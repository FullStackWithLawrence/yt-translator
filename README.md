# YouTube SRT File Translator

Translates an original SRT timed subtitle file into 21 other languages.


## Usage

Initialize:

```console
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

create a .env file in the root of the repo:

```console
OPENAI_API_KEY=YOUR-API-KEY
```

Translate your file:

```console
python translate.py input.srt
```
