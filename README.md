# KKLC OCR

A search site for the entries of KKLC, most notably including mnemonics. You can enter either multiple kanji, comma/space separated IDs (entry numbers), 音読み or 訓読み readings (either カタカナ or ひらがな), or search by keywords.

The source code for the transcription process lives here too - namely API calls to `gemini-flash-2.0` and some prompt engineering. Thanks to <https://kanjiapi.dev/> for providing the readings and JLPT levels.

I would appreciate pull requests for any mnemonic mistranscriptions (usually radicals); I've manually fixed some, but I'm sure there are more.

### Notes
- Only up to 3 readings are displayed for brevity. Use a dictionary if you want more readings.
- The JLPT levels correspond to the [old levels](https://en.wikipedia.org/wiki/Japanese-Language_Proficiency_Test#Previous_format_(1984%E2%80%932009)) (from 1-4), not the [new levels](https://en.wikipedia.org/wiki/Japanese-Language_Proficiency_Test#) (from 1-5).
