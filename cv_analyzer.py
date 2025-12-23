def analyze_resume(text: str):
    text_lower = text.lower()
    word_count = len(text.split())

    # ---- ATS SCORE ----
    ats_score = min(90, int(word_count / 5))

    # ---- KEYWORD MATCH ----
    keywords = ["python", "java", "sql", "machine learning", "react", "api"]
    matched = sum(1 for k in keywords if k in text_lower)
    keyword_score = int((matched / len(keywords)) * 100)

    # ---- FORMATTING ----
    formatting_score = 90 if "\n" in text else 50

    # ---- CLARITY ----
    clarity_score = 80 if word_count > 300 else 55

    suggestions = []
    if keyword_score < 70:
        suggestions.append("Improve keyword alignment with job roles")
    if clarity_score < 70:
        suggestions.append("Shorten long bullet points")
    if ats_score < 70:
        suggestions.append("Add measurable achievements")

    return {
        "ats": ats_score,
        "keywords": keyword_score,
        "formatting": formatting_score,
        "clarity": clarity_score,
        "suggestions": suggestions
    }
