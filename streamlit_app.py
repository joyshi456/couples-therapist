import os
import streamlit as st
import json
from openai import OpenAI  # Import OpenAI package

# Load prompt database from JSON file
with open("attributes.json", "r", encoding="utf-8") as f:
    therapist = json.load(f)

# Initialize OpenAI client with your API key and custom base URL (for Gemini)
client = OpenAI(
    api_key="EMPTY",
    base_url='http://34.28.33.252:6001'
)

st.set_page_config(page_title="Couples Therapist")

def create_system_prompt(rational, humor, directness, warmth):
    # Fetch the corresponding narrative text from JSON
    rational_text = therapist["therapist_attributes"]["rational"][str(rational)]
    humor_text = therapist["therapist_attributes"]["humor"][str(humor)]
    directness_text = therapist["therapist_attributes"]["directness"][str(directness)]
    warmth_text = therapist["therapist_attributes"]["warmth"][str(warmth)]
    
    # Build the system prompt
    system_prompt = f"""
**Role & Core Principles**\n
You are **Dr. [Name]**, an AI couples therapist specializing in fostering communication, resolving conflicts, and rebuilding emotional intimacy. Your core principles are:\n
1. **Neutrality**: Never take sides.\n
2. **Empathy**: Acknowledge both partners’ feelings.\n
3. **Active Listening**: Reflect and clarify statements.\n
4. **Solution-Focused**: Guide couples toward actionable steps.\n\n

---\n\n

**Therapist Style**\n
In terms of your rationality: {rational_text}\n\n
In terms of your humor: {humor_text}\n\n
In terms of your directness: {directness_text}\n\n
In terms of your warmth: {warmth_text}\n\n

---\n\n

**Therapeutic Techniques**\n
*(Include 3-5 of these in sessions)*\n
1. **Active Listening Loops**: *“Partner A, can you rephrase what Partner B just said to confirm understanding?”*\n
2. **Conflict De-escalation**: Identify triggers (e.g., *“When [action] happens, it makes you feel [emotion], yes?”*).\n
3. **Emotional Needs Mapping**: Help partners articulate unmet needs (security, validation, etc.).\n
4. **Future-Building Exercises**: *“Describe a perfect day together in 5 years—what would you both do differently now?”*\n
5. **Fair Fighting Rules**: Teach non-blaming language (e.g., *“Use ‘I feel’ statements instead of ‘You always…’”*).\n\n

---\n\n

**Session Framework**\n
1. **Opening**: *“What would you both like to focus on today?”*\n
2. **Assessment**: Ask each partner to rate their emotional state (1-10).\n
3. **Guided Discussion**: Use techniques above to explore a specific conflict.\n
4. **Intervention**: Assign a customized exercise (e.g., *“Try a 10-minute daily check-in without problem-solving this week.”*).\n
5. **Closing**: Summarize progress and set goals.\n\n

---\n\n

**Response Guidelines**\n
- **Avoid**: Judgmental language, diagnosing disorders, or favoring one partner.\n
- **Prioritize**: Equal speaking time, identifying patterns (e.g., *“This reminds me of what you said about [past issue]—is this a cycle?”*).\n
- **Escalate**: If abuse is mentioned, respond with, *“Your safety is vital. Let me share resources for professional support.”*\n
"""
    return system_prompt


# Sidebar: Credentials and Prompt Selection
with st.sidebar:
    st.title('Couples Therapist')
    
    mode = st.radio("Choose Mode", ["Therapy", "Role Play"])

    if mode == "Therapy":

        st.subheader('Customize Me!')
        rational = st.slider('How rational should I be?', min_value=1, max_value=3, value=2, step=1)
        humor = st.slider('How much humor should I incorporate?', min_value=1, max_value=3, value=2, step=1)
        directness = st.slider('How direct should I be?', min_value=1, max_value=3, value=2, step=1)
        warmth = st.slider('Warmth: 1 = formal/professional, 3 = gentle/nurturing', min_value=1, max_value=3, value=2, step=1)
        # sex = st.checkbox("Sex Therapy?")
        system_prompt = create_system_prompt(rational, humor, directness, warmth)

        
    elif mode == "Role Play":

        st.subheader('Partner Details')
        character_name = st.text_input('Partner Name')
        character_background = st.text_input('Describe your Partner')

        st.write(f"Partner Name: {character_name}")
        st.write(f"Description: {character_background}")

        system_prompt = f"You're the partner."

    
# Initialize or load chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


# Helper function to generate responses using the Gemini model
def generate_gemini_response(prompt_input):
    """
    Build the conversation history, append the user's prompt, then call the Gemini model.
    """
    # Build conversation history with system prompt first
    conversation = [{"role": "system", "content": system_prompt}]
    
    # Add user's current prompt
    conversation.append({"role": "user", "content": prompt_input})

    try:
        # API call using custom base URL (Gemini model)
        response = client.chat.completions.create(
            model="gemini-1.5-flash",  # Your Gemini model
            messages=conversation,  # List of messages
            temperature=1.4,
            top_p=0.8,
            max_tokens=1500,
            timeout=60,
            stream=True  # Enable streaming
        )
        
        content = ""
        
        # Process chunks of the streamed response
        for chunk in response:
            # Check if reasoning_content exists in the chunk
                # Add the content to the result
                content += chunk.choices[0].delta.content

        # Return the complete content
        return content

    except Exception as e:
        return f"Error contacting Gemini model: {e}"

# Handle user prompt input via Streamlit's chat input
if prompt := st.chat_input("Enter your prompt here"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a response if the last message is from the user
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = generate_gemini_response(prompt)  # Synchronous call to Gemini API
            placeholder = st.empty()
            full_response = ''
            # For non-streaming, simply display the full response
            full_response = response_text
            placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})