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

## Languages

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
