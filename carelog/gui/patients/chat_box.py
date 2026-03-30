import streamlit as st
import google.generativeai as genai
from streamlit_chatbox import ChatBox, Markdown

# Call Gemini API and configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "temperature": 0.5,
        "top_p": 0.9,
        "max_output_tokens": 500
    }
    )

# Main function
def chatbox(manager, mode):
    # Init chatbox safely
    chat_box = ChatBox(
        use_rich_markdown=True,
        user_theme="green",
        assistant_theme="blue",
    )

    # Init session states
    username = st.session_state.username
    CHAT_NAME = f"chat_with_{username}"
    chat_box.use_chat_name(CHAT_NAME)
    chat_box.init_session()
    chat_box.output_messages()

    # User input
    query = st.chat_input("How are you feeling today?")
    if not query:
        return

    # Add user message
    chat_box.user_say(query)

    # AI Mode
    if mode == "Supportive":
        mode_prompt = "Be empathetic and supportive. "
    elif mode == "Strict Medical":
        mode_prompt = "Provide concise evidence-based advice based on user's condition."
    else:
        mode_prompt = "Provide helpful medical guidance."

    system_prompt = " Act like a medical profession and give concise medical advice based on user_prompt. Be emphatic and care about them. You should assume the user doesn't know anything about medicine or biology, give some explanations"

    prompt = (
        f"""
        Mode: {mode}

        System prompt: {system_prompt} 

        Username: {username} and user prompt: {query}

        Explain clearly in a few sentences.
        """
    )

    # Avoid bypassing
    blocked_words = ["suicide", "kill myself", "overdose", "hacker", "kill"]

    if any(word in query.lower() for word in blocked_words):
        reply_text = "If this is an emergency, please seek professional medical help immediately."
        chat_box.ai_say(reply_text)
        return

    try:
        with st.spinner("Generating reply... 🤖"):
            response = model.generate_content(f"{prompt}")
            reply_text = response.text.strip()
    except Exception as e:
        reply_text = f"(Error from Gemini: {e})"
        st.error(reply_text)

    # Output assistant reply
    chat_box.ai_say(Markdown(
        reply_text, in_expander=True, 
        expanded=True, 
        title="Assistant"
        )
    )

    # Extra: Clear cache
    clear = st.button("Clear Chat 🧹")
    if clear:
        st.session_state.pop(CHAT_NAME, None)
        st.session_state.pop("gemini_chat", None)

        for key in list(st.session_state.keys()):
            if key.startswith("chat_with_"):
                del st.session_state[key]

        st.rerun()

# --- WHAT TO DO ---
# 1. Upgrade architecture
# 2. Add rate limiting to avoid prompt abuse
# 3. Strengthen security and avoid bypassing