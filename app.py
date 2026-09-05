import io
import re
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Page configuration
st.set_page_config(
    page_title="Resume Job Match Scorer",
    page_icon="📄",
    layout="wide",
)

# Skill library
SKILLS = [
    "python", "java", "c", "c++", "c#", "javascript", "typescript",
    "html", "css", "react", "angular", "vue", "node.js", "express",
    "django", "flask", "fastapi", "streamlit",
    "sql", "mysql", "postgresql", "mongodb", "oracle", "sqlite",
    "excel", "power bi", "tableau", "pandas", "numpy", "matplotlib",
    "scikit-learn", "tensorflow", "pytorch", "keras",
    "machine learning", "deep learning", "data analysis",
    "data analytics", "data visualization", "statistics",
    "natural language processing", "nlp", "computer vision",
    "artificial intelligence", "ai", "generative ai",
    "git", "github", "docker", "kubernetes", "aws", "azure", "gcp",
    "rest api", "api", "linux", "agile", "scrum",
    "communication", "leadership", "problem solving", "teamwork",
]

# Text processing
def extract_text_from_pdf(uploaded_file):
    """Extract text from a text-based PDF."""
    try:
        uploaded_file.seek(0)
        reader = PdfReader(uploaded_file)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)

        return "\n".join(text_parts).strip()
    except Exception as error:
        st.error(f"Error reading PDF: {error}")
        return ""

def clean_text(text):
    """Normalize text while preserving common technical skill symbols."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def calculate_similarity(resume_text, job_description):
    """Calculate TF-IDF cosine similarity as a percentage."""
    resume_processed = clean_text(resume_text)
    job_processed = clean_text(job_description)

    if not resume_processed or not job_processed:
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(
            [resume_processed, job_processed]
        )
    except ValueError:
        return 0.0

    score = cosine_similarity(
        tfidf_matrix[0:1], tfidf_matrix[1:2]
    )[0][0] * 100

    return round(float(score), 2)


def contains_skill(text, skill):
    """Check a skill as a complete phrase instead of a loose substring."""
    pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
    return bool(re.search(pattern, text.lower()))


def extract_skills(text):
    """Return skills from the skill library that appear in text."""
    return sorted({
        skill for skill in SKILLS
        if contains_skill(text, skill)
    })


def extract_keywords(text, num_keywords=15):
    """Extract frequent meaningful words from the job description."""
    cleaned = clean_text(text)
    words = re.findall(r"\b[a-z][a-z0-9+#.-]{2,}\b", cleaned)

    stop_words = {
        "the", "and", "for", "with", "that", "this", "from", "your",
        "you", "our", "are", "will", "have", "has", "job", "role",
        "work", "working", "candidate", "required", "requirements",
        "preferred", "responsibilities", "skills", "experience",
        "years", "using", "ability", "knowledge", "strong", "good",
        "team", "including", "into", "about", "who", "but", "not",
        "all", "can", "should", "their", "they", "them",
    }

    filtered_words = [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

    return Counter(filtered_words).most_common(num_keywords)


def generate_suggestions(score, matched_skills, missing_skills, keywords):
    """Generate practical, rule-based resume improvement suggestions."""
    suggestions = []

    if score < 40:
        suggestions.append(
            "Tailor your summary and project descriptions more closely "
            "to the target job description."
        )
    elif score < 70:
        suggestions.append(
            "The resume has a moderate match. Strengthen relevant "
            "experience with specific achievements and job-related terms."
        )
    else:
        suggestions.append(
            "The resume has a strong text match. Review it manually for "
            "accuracy, clarity, and evidence of achievements."
        )

    if missing_skills:
        suggestions.append(
            "If you genuinely have these skills, add evidence of them in "
            "your Skills, Projects, or Experience sections: "
            + ", ".join(missing_skills[:8])
            + "."
        )

    if matched_skills:
        suggestions.append(
            "Keep the strongest matched skills visible near relevant "
            "projects or experience: "
            + ", ".join(matched_skills[:8])
            + "."
        )

    top_terms = [word for word, _ in keywords[:6]]
    if top_terms:
        suggestions.append(
            "Review these important job-description terms and use them "
            "naturally where they accurately describe your background: "
            + ", ".join(top_terms)
            + "."
        )

    suggestions.append(
        "Use measurable results where possible, such as percentages, "
        "time saved, model accuracy, users served, or business impact."
    )

    return suggestions


def create_report(
    score,
    matched_skills,
    missing_skills,
    keywords,
    suggestions,
):
    """Create a downloadable plain-text analysis report."""
    keyword_text = ", ".join(word for word, _ in keywords) or "None found"
    matched_text = ", ".join(matched_skills) or "None found"
    missing_text = ", ".join(missing_skills) or "None found"

    suggestion_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(suggestions, start=1)
    )

    return f"""RESUME JOB MATCH ANALYSIS
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

MATCH SCORE
{score:.2f}%

MATCHED SKILLS
{matched_text}

MISSING JOB SKILLS
{missing_text}

IMPORTANT JOB KEYWORDS
{keyword_text}

IMPROVEMENT SUGGESTIONS
{suggestion_text}

NOTE
This is an automated text-matching aid. A higher score does not guarantee
selection, and missing terms should only be added when they truthfully
represent your skills or experience.
"""

def show_score_chart(score):
    """Display a horizontal match-score chart."""
    fig, ax = plt.subplots(figsize=(8, 1.2))

    if score < 40:
        bar_color = "#ff4b4b"
    elif score < 70:
        bar_color = "#ffa726"
    else:
        bar_color = "#0f9d58"

    ax.barh([0], [100], color="#e8e8e8")
    ax.barh([0], [score], color=bar_color)
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel("Match percentage")
    ax.set_title("Resume–Job Match")
    ax.text(
        min(score + 2, 94),
        0,
        f"{score:.1f}%",
        va="center",
        fontweight="bold",
    )

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# Application UI
def main():
    st.title("📄 Resume Job Match Scorer")
    st.write(
        "Upload a text-based PDF resume and paste a job description. "
        "The app analyzes text similarity, skills, keywords, and "
        "resume improvement opportunities."
    )

    with st.sidebar:
        st.header("About")
        st.info(
            "This tool uses TF-IDF and cosine similarity for text matching, "
            "plus rule-based skill and keyword analysis."
        )

        st.header("How it works")
        st.write(
            "1. Upload your resume PDF\n"
            "2. Paste the job description\n"
            "3. Click **Analyze Match**\n"
            "4. Review score, skills, keywords, and suggestions\n"
            "5. Download the analysis report"
        )

        st.caption(
            "Tip: Scanned/image-only PDFs may need OCR before text can "
            "be extracted."
        )

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"],
    )

    job_description = st.text_area(
        "Paste the job description",
        height=250,
        placeholder="Paste the complete job description here...",
    )

    if st.button("🔍 Analyze Match", type="primary"):
        if uploaded_file is None:
            st.warning("Please upload your resume.")
            return

        if not job_description.strip():
            st.warning("Please paste the job description.")
            return

        with st.spinner("Analyzing your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)

            if not resume_text:
                st.error(
                    "No readable text was extracted. Please use a "
                    "text-based PDF or run OCR on a scanned resume."
                )
                return

            score = calculate_similarity(
                resume_text,
                job_description,
            )

            resume_skills = set(extract_skills(resume_text))
            job_skills = set(extract_skills(job_description))

            matched_skills = sorted(resume_skills & job_skills)
            missing_skills = sorted(job_skills - resume_skills)
            keywords = extract_keywords(job_description)

            suggestions = generate_suggestions(
                score,
                matched_skills,
                missing_skills,
                keywords,
            )

        st.success("Analysis completed.")

        st.subheader("Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Match Score", f"{score:.2f}%")
        col2.metric("Matched Skills", len(matched_skills))
        col3.metric("Missing Job Skills", len(missing_skills))

        show_score_chart(score)

        if score < 40:
            st.warning(
                "Low match: tailor the resume more closely to the job."
            )
        elif score < 70:
            st.info(
                "Good match: improve relevant keywords and evidence."
            )
        else:
            st.success(
                "Excellent text match: verify relevance and accuracy."
            )

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "✅ Matched Skills",
                "⚠️ Missing Skills",
                "🔑 Job Keywords",
                "💡 Suggestions",
            ]
        )

        with tab1:
            if matched_skills:
                st.write(", ".join(matched_skills))
            else:
                st.info(
                    "No predefined skills were matched. "
                    "You can expand the SKILLS list in the source code."
                )

        with tab2:
            if missing_skills:
                st.write(", ".join(missing_skills))
                st.caption(
                    "Only add a missing skill to your resume if you "
                    "actually have that skill or experience."
                )
            else:
                st.success(
                    "No missing skills were found from the predefined "
                    "skill library."
                )

        with tab3:
            if keywords:
                keyword_data = {
                    "Keyword": [word for word, _ in keywords],
                    "Frequency": [count for _, count in keywords],
                }
                st.dataframe(
                    keyword_data,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No meaningful keywords were found.")

        with tab4:
            for suggestion in suggestions:
                st.write(f"• {suggestion}")

        report = create_report(
            score,
            matched_skills,
            missing_skills,
            keywords,
            suggestions,
        )

        st.download_button(
            label="⬇️ Download Analysis Report",
            data=report,
            file_name="resume_job_match_report.txt",
            mime="text/plain",
        )

        with st.expander("Preview extracted resume text"):
            st.text_area(
                "Extracted text",
                resume_text[:10000],
                height=250,
                disabled=True,
            )

    st.divider()
    st.caption(
        "This tool is an automated screening aid and should not be used "
        "as the sole basis for hiring decisions."
    )


if __name__ == "__main__":
    main()
