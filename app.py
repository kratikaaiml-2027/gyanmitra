from datetime import date

import pandas as pd
import streamlit as st

import ai

st.set_page_config(page_title="GyanMitra - AI Tutor", page_icon="📚", layout="centered")

# ---------- Session state ----------
st.session_state.setdefault("history", [])  # [{"topic", "score", "total", "date"}]
st.session_state.setdefault("quiz", None)

# ---------- Sidebar ----------
st.sidebar.title("📚 GyanMitra")
st.sidebar.caption("Your AI tutor, in your language")
nickname = st.sidebar.text_input("Nickname (optional)", "Student")
language = st.sidebar.selectbox("Language", ["Hindi", "English"])
class_level = st.sidebar.selectbox("Class", [f"Class {i}" for i in range(6, 13)])
subject = st.sidebar.selectbox("Subject", ["Maths", "Science", "Social Science", "English", "Hindi"])

st.title("GyanMitra: AI Tutor for Rural Students")
st.caption("SDG 4: Quality Education")
st.write(f"Namaste, **{nickname}**! Ask a doubt, take a quiz, or check your progress.")
if not ai.has_key():
    st.info("Demo mode: no GEMINI_API_KEY found, so sample answers are shown. See README to add your key.")

tab1, tab2, tab3 = st.tabs(["❓ Ask a Doubt", "📝 Quiz", "📊 My Progress"])

# ---------- Feature 1: Ask a Doubt ----------
with tab1:
    question = st.text_area("Type your doubt here", placeholder="e.g. What is photosynthesis?")
    if st.button("Explain"):
        if not question.strip():
            st.warning("Please type a question first.")
        else:
            with st.spinner("Thinking..."):
                try:
                    st.markdown(ai.explain(question, language, class_level, subject))
                    st.caption("Tip: check important answers with your teacher.")
                except Exception as e:
                    st.error(f"Could not get an answer. Check your API key and internet. ({e})")

# ---------- Feature 2: Quiz ----------
with tab2:
    topic = st.text_input("Quiz topic", placeholder="e.g. Fractions")
    if st.button("Generate Quiz"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            weak = topic.strip().lower() in [
                h["topic"].lower() for h in st.session_state.history if h["score"] / h["total"] < 0.6
            ]
            with st.spinner("Creating your quiz..."):
                try:
                    qs = ai.make_quiz(topic.strip(), language, class_level, subject, weak)
                    st.session_state.quiz = {"topic": topic.strip(), "questions": qs}
                except Exception as e:
                    st.session_state.quiz = None
                    st.error(f"Quiz could not be created. Please try again. ({e})")

    quiz = st.session_state.quiz
    if quiz:
        st.subheader(f"Quiz: {quiz['topic']}")
        with st.form("quiz_form"):
            answers = []
            for i, q in enumerate(quiz["questions"]):
                st.markdown(f"**Q{i + 1}. {q['question']}**")
                answers.append(st.radio("Choose one", q["options"], index=None, key=f"q{i}", label_visibility="collapsed"))
                st.caption(f"Hint: {q.get('hint', '')}")
            submitted = st.form_submit_button("Submit Quiz")

        if submitted:
            score = 0
            for q, a in zip(quiz["questions"], answers):
                correct = q["options"][q["answer_index"]]
                if a == correct:
                    score += 1
                    st.success(f"✅ {q['question']}\n\n{q.get('explanation', '')}")
                else:
                    st.error(f"❌ {q['question']}\n\nCorrect answer: **{correct}**\n\n{q.get('explanation', '')}")
            total = len(quiz["questions"])
            st.session_state.history.append(
                {"topic": quiz["topic"], "score": score, "total": total, "date": str(date.today())}
            )
            st.info(f"Your score: {score}/{total}. Open the My Progress tab to see what to revise next.")

# ---------- Feature 3: Progress & weak topics ----------
with tab3:
    if not st.session_state.history:
        st.write("Take a quiz first, then your progress will appear here.")
    else:
        df = pd.DataFrame(st.session_state.history)
        df["percent"] = (df["score"] / df["total"] * 100).round(0)
        by_topic = df.groupby("topic")["percent"].mean().round(0)

        st.subheader("Scores by topic (%)")
        st.bar_chart(by_topic)
        st.dataframe(df[["date", "topic", "score", "total", "percent"]], use_container_width=True)

        weak_topics = by_topic[by_topic < 60]
        if len(weak_topics):
            st.warning("Revise these topics next: " + ", ".join(weak_topics.index))
        else:
            st.success("Great work! No weak topics right now. Try a new topic.")
