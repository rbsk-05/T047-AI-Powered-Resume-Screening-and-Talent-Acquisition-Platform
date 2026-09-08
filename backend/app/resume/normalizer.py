"""Skill and Date normalizer."""

import re

# Centralized canonical skill alias map
_SKILL_ALIASES: dict[str, str] = {
    # Node
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node js": "Node.js",
    "node": "Node.js",
    # Express
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "express js": "Express.js",
    "express": "Express.js",
    # React
    "reactjs": "React.js",
    "react.js": "React.js",
    "react js": "React.js",
    "react": "React.js",
    # React Native
    "reactnative": "React Native",
    "react native": "React Native",
    "react-native": "React Native",
    # Vanilla JS
    "vanillajs": "Vanilla JS",
    "vanilla js": "Vanilla JS",
    # GitHub
    "github": "GitHub",
    "git hub": "GitHub",
    # Next.js / Nuxt.js
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "next js": "Next.js",
    "nuxtjs": "Nuxt.js",
    "nuxt.js": "Nuxt.js",
    "nuxt js": "Nuxt.js",
    # Vue
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "vue js": "Vue.js",
    "vue": "Vue.js",
    # Nest
    "nestjs": "Nest.js",
    "nest.js": "Nest.js",
    "nest js": "Nest.js",
    # Spring
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    # Database
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo db": "MongoDB",
    "mongo": "MongoDB",
    "mysql": "MySQL",
    "my sql": "MySQL",
    # REST API
    "rest api": "REST API",
    "restful api": "REST API",
    "rest apis": "REST API",
    "rest": "REST API",
    # HTML / CSS
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
}


class Normalizer:
    """Centralized normalization services for skills, names, and text."""

    @staticmethod
    def normalize_skill(skill: str) -> str:
        """Return the canonical representation of a skill string."""
        cleaned = skill.strip()
        lowered = cleaned.lower()
        if lowered in _SKILL_ALIASES:
            return _SKILL_ALIASES[lowered]
        return cleaned

    @classmethod
    def normalize_skills(cls, skills: list[str]) -> list[str]:
        """Normalize, de-duplicate, and preserve clean canonical display order."""
        seen: set[str] = set()
        result: list[str] = []
        for s in skills:
            norm = cls.normalize_skill(s)
            key = norm.lower()
            if key and key not in seen:
                seen.add(key)
                result.append(norm)
        return result
