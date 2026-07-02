"""Skill extraction via a spaCy PhraseMatcher over a curated skills taxonomy.

Uses spacy.blank("en") - a tokenizer only, no statistical model - since
PhraseMatcher only needs tokenisation, not POS tagging or NER. This avoids
requiring a spaCy model download.
"""

import json
from functools import lru_cache
from pathlib import Path

import spacy
from spacy.matcher import PhraseMatcher

from app.config import settings


class SkillExtractor:
    def __init__(self, taxonomy_path: Path):
        self.nlp = spacy.blank("en")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self._alias_to_skill: dict[str, str] = {}

        taxonomy = json.loads(taxonomy_path.read_text())
        for entry in taxonomy:
            skill = entry["skill"]
            phrases = {skill.lower(), *[a.lower() for a in entry.get("aliases", [])]}
            patterns = [self.nlp.make_doc(phrase) for phrase in phrases]
            self.matcher.add(skill, patterns)
            for phrase in phrases:
                self._alias_to_skill[phrase] = skill

    def extract(self, text: str) -> list[str]:
        if not text:
            return []
        doc = self.nlp(text)
        matches = self.matcher(doc)
        matched_skills: set[str] = set()
        for match_id, _start, _end in matches:
            canonical_skill = self.nlp.vocab.strings[match_id]
            matched_skills.add(canonical_skill)
        return sorted(matched_skills)


@lru_cache(maxsize=1)
def get_skill_extractor() -> SkillExtractor:
    return SkillExtractor(settings.skills_taxonomy_path)
