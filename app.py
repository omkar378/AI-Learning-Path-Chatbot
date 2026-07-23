import streamlit as st

from utils import (
    GeminiQuotaError,
    generate_fallback_learning_path,
    generate_learning_path,
)


# ---------------- Page Configuration ----------------

st.set_page_config(
    page_title="AI Learning Path Generator",
    page_icon="🧠",
    layout="wide",
)


# ---------------- Header ----------------

st.title("🧠 AI Learning Path Generator")

st.caption(
    "Generate a personalized learning roadmap using Google Gemini "
    "and get recommended YouTube videos."
)


# ---------------- Session State ----------------

if "generated_path" not in st.session_state:
    st.session_state.generated_path = None


# ---------------- Sidebar ----------------

with st.sidebar:

    st.header("⚙ Configuration")

    gemini_api_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        help="Required to generate learning paths",
    )


    youtube_api_key = st.text_input(
        "▶️ YouTube API Key (Optional)",
        type="password",
        help="Required for video recommendations",
    )


    st.divider()


    st.info(
        """
Examples:

• Learn Python in 7 days

• Become a Web Developer

• Learn Machine Learning

• Learn Android Development
"""
    )


# ---------------- User Input ----------------

st.subheader("🎯 What do you want to learn?")


user_goal = st.text_area(
    "Learning Goal",
    placeholder="Example: Learn Python in 7 days",
    height=120,
)


# ---------------- Generate Button ----------------

if st.button(
    "🚀 Generate Learning Path",
    type="primary"
):

    if not gemini_api_key:

        st.error(
            "❌ Please enter your Gemini API Key."
        )

        st.stop()


    if not user_goal.strip():

        st.warning(
            "⚠️ Please enter your learning goal."
        )

        st.stop()


    progress = st.empty()


    try:

        result = generate_learning_path(

            google_api_key=gemini_api_key,

            user_goal=user_goal,

            youtube_api_key=youtube_api_key,

            progress_callback=lambda message:
                progress.info(message),

        )


        progress.empty()


        st.session_state.generated_path = result


        st.success(
            "✅ Learning Path Generated Successfully!"
        )


    except GeminiQuotaError:
        result = generate_fallback_learning_path(
            user_goal=user_goal,
            youtube_api_key=youtube_api_key,
            progress_callback=lambda message: progress.info(message),
        )
        progress.empty()
        st.session_state.generated_path = result
        st.warning(
            "Gemini is currently unavailable for this API key, so a built-in "
            "roadmap was generated instead. Add quota or try again later for a "
            "Gemini-personalized plan."
        )
    except Exception as e:

        progress.empty()

        st.error(
            "❌ Could not generate the learning path. Please verify your Gemini "
            "API key and try again."
        )


# ---------------- Display Result ----------------

if st.session_state.generated_path:


    result = st.session_state.generated_path


    st.divider()


    st.download_button(

        label="📥 Download Learning Path",

        data=result["download_text"],

        file_name="learning_path.txt",

        mime="text/plain",

    )


    st.divider()


    st.header("📚 Your Learning Roadmap")


    for item in result["topics"]:


        with st.container():

            st.subheader(
                item["day"]
            )


            st.write(
                f"**Topic:** {item['topic']}"
            )


            if item["videos"]:


                st.write(
                    "### 📺 Recommended Videos"
                )


                for video in item["videos"]:


                    st.markdown(
                        f"""
▶ [{video['title']}]({video['url']})
"""
                    )


            else:


                st.caption(
                    "No YouTube API Key provided. "
                    "Only roadmap generated."
                )


            st.divider()
