"""Transcreve o áudio dos brutos com mlx-whisper (timestamps por palavra).

Uso: uv run --python 3.12 --with mlx-whisper tools/sinais/transcribe.py <WORKDIR> [arquivo ...]
Lê <WORKDIR>/audio/<nome>.wav e grava <WORKDIR>/asr/<nome>.json.
"""
import json
import sys
from pathlib import Path

import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"

work = Path(sys.argv[1])
names = sys.argv[2:] or sorted(p.stem for p in (work / "audio").glob("[!.]*.wav"))
prompts = json.loads((Path(__file__).parent / "prompts.json").read_text()) if (Path(__file__).parent / "prompts.json").exists() else {}

for name in names:
    wav = work / "audio" / f"{name}.wav"
    out = work / "asr" / f"{name}.json"
    res = mlx_whisper.transcribe(
        str(wav),
        path_or_hf_repo=MODEL,
        language="pt",
        word_timestamps=True,
        condition_on_previous_text=False,
        initial_prompt=prompts.get(name),
        no_speech_threshold=0.5,
    )
    words = [
        {"w": w["word"].strip(), "s": round(w["start"], 3), "e": round(w["end"], 3), "p": round(w.get("probability", 0), 3)}
        for seg in res["segments"]
        for w in seg.get("words", [])
    ]
    segs = [{"s": round(s["start"], 3), "e": round(s["end"], 3), "t": s["text"].strip()} for s in res["segments"]]
    out.write_text(json.dumps({"segments": segs, "words": words}, ensure_ascii=False, indent=1))
    print(f"{name}: {len(segs)} segmentos, {len(words)} palavras", flush=True)
