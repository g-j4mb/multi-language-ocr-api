from typing import Dict

from langdetect import DetectorFactory, detect_langs

DetectorFactory.seed = 0


class LanguageDetector:
    def detect(self, text: str) -> Dict[str, object]:
        text = (text or "").strip()
        if not text:
            return {"language": "und", "confidence": 0.0}

        try:
            candidates = detect_langs(text)
            if not candidates:
                return {"language": "und", "confidence": 0.0}
            best = candidates[0]
            return {"language": best.lang, "confidence": float(best.prob)}
        except Exception:
            return {"language": "und", "confidence": 0.0}
