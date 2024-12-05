#cd /Users/thib/Desktop/Hackathon
#streamlit run Gemini.py

import streamlit as st
import speech_recognition as sr
import google.generativeai as genai
import json
import pandas as pd 
import re
import json5

st.set_page_config(layout="wide")

# Configure the Gemini API key
genai.configure(api_key="ADD GEMINI API KEY")
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Define the questionnaire and scoring instructions as variables
questionnaire = """
The Edinburgh Postnatal Depression Scale (EPDS) includes the following questions. Each question has four possible answers, scored from 0 to 3 based on severity:
    1. I have been able to laugh and see the funny side of things:
        • As much as I always could (0)
        • Not quite so much now (1)
        • Definitely not so much now (2)
        • Not at all (3)
    2. I have looked forward with enjoyment to things:
        • As much as I ever did (0)
        • Rather less than I used to (1)
        • Definitely less than I used to (2)
        • Hardly at all (3)
    3. I have blamed myself unnecessarily when things went wrong:
        • No, never (0)
        • Not very often (1)
        • Yes, some of the time (2)
        • Yes, most of the time (3)
    4. I have felt anxious or worried for no good reason:
        • No, not at all (0)
        • Hardly ever (1)
        • Yes, sometimes (2)
        • Yes, very often (3)
    5. I have felt scared or panicked for no good reason:
        • No, not at all (0)
        • Yes, but not very often (1)
        • Yes, sometimes (2)
        • Yes, quite a lot (3)
    6. Things have been getting to me:
        • Yes, most of the time I haven’t been able to cope at all (3)
        • Yes, sometimes I haven’t been coping as well as usual (2)
        • No, most of the time I have coped quite well (1)
        • No, I have been coping as well as ever (0)
	7.	I have felt so unhappy that I have had difficulty sleeping:
        • No, not at all (0)
        • Only occasionally (1)
        • Yes, sometimes (2)
        • Yes, most of the time (3)
    8. I have felt sad or miserable:
        • No, not at all (0)
        • Not very often (1)
        • Yes, quite often (2)
        • Yes, most of the time (3)
    9. I have been so unhappy that I have been crying:
        • No, never (0)
        • Only occasionally (1)
        • Yes, quite often (2)
        • Yes, most of the time (3)
    10. The thought of harming myself has occurred to me:
        • Never (0)
        • Hardly ever (1)
        • Sometimes (2)
        • Yes, quite often (3)
"""

instructions = """
INSTRUCTIONS:
Based on the responses in the input text, calculate the total score (0-30). Interpret the score as follows:
  - 0–9: Scores in this range may indicate the presence of some symptoms of distress that may be shortlived and are less likely to interfere with day to day ability to function at home or at work. However if these symptoms have persisted more than a week or two further enquiry is warranted.
  - 10–12:  Scores within this range indicate presence of symptoms of distress that may be discomforting. Repeat the EDS in 2 weeks time and continue monitoring progress regularly. If the scores increase to above 12 assess further and consider referral as needed.
  - 13–30: Scores above 12 require further assessment and appropriate management as the likelihood of depression is high. Referral to a psychiatrist/psychologist may be necessary.
"""

# Function to analyze text with Gemini
def analyze_text_with_prompt(input_text):
    prompt = """
    The following scale is used to evaluate post-natal depression. Interpret the input text according to this scale:

    SCALE DESCRIPTION:
    {questionnaire}

    {instructions}

    TASK:
    Analyze the following text:
    "{input_text}"

    Your task is to:
    1. Identify the emotions.
    2. Detect cognitive distortions.
    3. Highlight problematic behavioral patterns.
    4. For each of the 10 questions in the scale:
       - Identify the participant's response based on the input text.
       - Assign the corresponding score (0 to 3) for each response as defined in the scale.
       - Provide a brief rationale for the assigned score.
    5. Return a structured summary in the following JSON format, enclosed in triple backticks and labeled as 'json':

    ```json
    {{
      "emotions": ["list of emotions"],
      "cognitive_distortions": ["list of distortions"],
      "behavioral_patterns": ["list of patterns"],
      "question_scores": {{
        "1": {{"score": X, "rationale": "Your rationale for question 1"}},
        "2": {{"score": X, "rationale": "Your rationale for question 2"}},
        ...
        "10": {{"score": X, "rationale": "Your rationale for question 10"}}
      }}
    }}
    ```

    **Important**:
    - Ensure all JSON keys and string values use double quotes (`"`), not single quotes (`'`), to adhere to proper JSON formatting.
    - Do not make interpretation.
    - Escape any double quotes inside string values with a backslash (`\\`), e.g., `He said, \\\"Hello\\\".`
    - **Avoid using apostrophes in contractions (use "cannot" instead of "can't").**
    - Do not include any additional text within the JSON code block.
    - All explanations should be provided **after** the JSON code block.

    6. After the JSON code block, provide a plain text explanation summarizing the findings.
    """.format(questionnaire=questionnaire, instructions=instructions, input_text=input_text)
    response = model.generate_content(prompt)
    return response

# Function to process audio files
def process_audio_file(file_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language="en-US")  # English audio
            return text
    except sr.UnknownValueError:
        return "Sorry, the audio was not clear enough to understand."
    except sr.RequestError as e:
        return f"Error with the Speech Recognition service: {e}"

def generate_bot_response(user_message, total_score, interpretation, emotions_list, distortions_list, behaviors_list):
    # Define the severity level based on the total score
    if total_score <= 9:
        severity = "low"
    elif 10 <= total_score <= 12:
        severity = "moderate"
    elif 13 <= total_score <= 19:
        severity = "moderate"
    else:
        severity = "high"

    # Construct a prompt for the language model
    prompt = f"""
    You are a compassionate support chatbot assisting someone who has just completed an assessment for postnatal depression with a {severity} severity level.

    The assessment revealed the following:
    - Total Score: {total_score}
    - Interpretation: {interpretation}
    - Emotions Identified: {', '.join(emotions_list)}
    - Cognitive Distortions Detected: {', '.join(distortions_list)}
    - Behavioral Patterns Noted: {', '.join(behaviors_list)}

    The user has provided the following statement:
    "{user_message}"

    Based on the severity level and the user's statement, provide a supportive, empathetic response. Offer appropriate advice or resources, encouraging them to seek professional help if necessary.

    Important:
    - Do not provide medical diagnoses.
    - Avoid giving specific medical advice.
    - Use a tone that is understanding and non-judgmental.
    - Encourage the user to consult a healthcare professional.
    """

    # Generate the response using the language model
    response = model.generate_content(prompt)
    bot_reply = response.text.strip()

    return bot_reply

def display_chat(messages, container):
    with container:
        for msg in messages:
            if msg['role'] == 'user':
                # User message: right-aligned, justified text with a light grey background
                st.markdown(
                    f"""
                    <div style='text-align: right;'>
                        <strong style='color: white;'>You:</strong>
                    </div>
                    <div style='text-align: justify; background-color: #f5f5f5; padding: 10px; margin: 10px; border-radius: 10px; max-width: 70%; float: right; color: black;'>
                        {msg['content']}
                    </div>
                    <div style='clear: both;'></div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                # Bot message: left-aligned, justified text with a dark grey background
                st.markdown(
                    f"""
                    <div style='text-align: left;'>
                        <strong style='color: #ddd;'>ChatBot:</strong>
                    </div>
                    <div style='text-align: justify; background-color: #3a3a3a; color: white; padding: 10px; margin: 10px; border-radius: 10px; max-width: 70%; float: left;'>
                        {msg['content']}
                    </div>
                    <div style='clear: both;'></div>
                    """,
                    unsafe_allow_html=True,
                )

# Initialize session state for chat messages
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Streamlit UI
st.title("Post-Natal Depression Analysis")
st.write("Upload an audio file, and this app will analyze the emotions, cognitive distortions, and behavioral patterns.")

# File Upload Widget
uploaded_file = st.file_uploader("Upload an audio file (.wav format)", type=["wav"])
if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open("uploaded_audio.wav", "wb") as f:
        f.write(uploaded_file.read())

    st.info("Processing audio file...")

    # A horizontal line to separate sections
    st.markdown("---")
    
    # Process the audio file
    recognized_text = process_audio_file("uploaded_audio.wav")

    if recognized_text:
        st.subheader("Recognized Text")
        st.write(recognized_text)

        st.info("Analyzing text with Gemini...")
        response = analyze_text_with_prompt(recognized_text)

        if response and hasattr(response, 'text'):
            try:
                # Extract the JSON code block
                json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response.text)
                if json_match:
                    json_str = json_match.group(1)

                    parsed_response = json5.loads(json_str)
                    explanation = response.text[json_match.end():].strip()
                else:
                    st.error("Could not find JSON data in the response.")
                    parsed_response = {}
                    explanation = ""

                # Extract individual components from the parsed response
                emotions_list = parsed_response.get("emotions", [])
                distortions_list = parsed_response.get("cognitive_distortions", [])
                behaviors_list = parsed_response.get("behavioral_patterns", [])

                # Extract question scores and calculate total score
                question_scores = parsed_response.get("question_scores", {})
                total_score = 0
                scores_list = []
                for q_num in range(1, 11):
                    q_key = str(q_num)
                    q_data = question_scores.get(q_key, {"score": 0, "rationale": "No response"})
                    score = q_data.get("score", 0)
                    rationale = q_data.get("rationale", "No rationale provided.")
                    total_score += score
                    scores_list.append({"Question": q_num, "Score": score, "Rationale": rationale})

                # A horizontal line to separate sections
                st.markdown("---")

                # Display the combined analysis
                st.subheader("Symptoms")

                # Find the maximum length among the lists
                max_length = max(len(emotions_list), len(distortions_list), len(behaviors_list))

                # Pad the lists with empty strings to make them the same length
                emotions_list += [''] * (max_length - len(emotions_list))
                distortions_list += [''] * (max_length - len(distortions_list))
                behaviors_list += [''] * (max_length - len(behaviors_list))

                # Now create the DataFrame
                combined_df = pd.DataFrame({
                    'Emotions': emotions_list,
                    'Cognitive Distortions': distortions_list,
                    'Behavioral Patterns': behaviors_list
                })

                # Display the table
                st.table(combined_df)
                
                # Display the scoring rationale table
                st.subheader("Edinburgh Postnatal Depression Scale (EPDS): Scoring and Rationale for Responses")
                st.markdown("[Click here to view the EPDS questionnaire](https://med.stanford.edu/content/dam/sm/ppc/documents/DBP/EDPS_text_added.pdf)")
                scores_df = pd.DataFrame(scores_list)
                st.table(scores_df)

                # Display the total score and interpretation
                st.subheader("Total Score / 30")
                st.metric(label="EPDS Score", value=total_score)

                # Interpretation based on the total score
                if total_score <= 9:
                    interpretation = "Low likelihood of postnatal depression. No immediate concerns, but continued monitoring may be appropriate."
                elif 10 <= total_score <= 12:
                    interpretation = "Possible mild symptoms of postnatal depression. Professional consultation recommended."
                elif 13 <= total_score <= 30:
                    interpretation = "High likelihood of postnatal depression. Immediate professional help is strongly advised to ensure appropriate support and treatment."                
                st.write(f"Interpretation: {interpretation}")

                # Display explanation
                if explanation:
                    st.subheader("Explanation")
                    st.markdown(explanation)
                else:
                    st.warning("No explanation available.")

                # A horizontal line to separate sections
                st.markdown("---")

                # --- Chat Interface ---
                st.header("ChatBot")
                chat_container = st.container()

                # A horizontal line to separate sections
                st.markdown("---")

                # Initialize the chat messages if not already done
                if 'messages' not in st.session_state:
                    st.session_state['messages'] = []

                # Generate an initial bot response to the audio input if not already done
                if 'initial_response_generated' not in st.session_state:
                    # Generate a bot response to the recognized text (audio input)
                    initial_bot_response = generate_bot_response(
                        recognized_text, 
                        total_score, 
                        interpretation, 
                        emotions_list, 
                        distortions_list, 
                        behaviors_list
                    )
                    # Append the user's initial input (recognized text) and the bot's response to the conversation
                    st.session_state['messages'].append({'role': 'user', 'content': recognized_text})
                    st.session_state['messages'].append({'role': 'bot', 'content': initial_bot_response})
                    st.session_state['initial_response_generated'] = True

                # Display existing chat messages
                display_chat(st.session_state['messages'], chat_container)

                # Callback function for handling user input
                def handle_user_input():
                    user_message = st.session_state['user_input']
                    if user_message:
                        # Append the user's message to the conversation
                        st.session_state['messages'].append({'role': 'user', 'content': user_message})

                        # Create a conversation history for the prompt
                        past_messages = "\n".join(
                            f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state['messages']
                        )

                        # Determine severity level based on total score
                        if total_score <= 9:
                            severity = "low"
                        elif 10 <= total_score <= 12:
                            severity = "moderate"
                        elif 13 <= total_score <= 19:
                            severity = "moderate"
                        else:
                            severity = "high"

                        # Generate a response from the bot
                        bot_response = generate_bot_response(
                            user_message,
                            total_score,
                            interpretation,
                            emotions_list,
                            distortions_list,
                            behaviors_list
                        )
                        # Append the bot's response to the conversation
                        st.session_state['messages'].append({'role': 'bot', 'content': bot_response})

                        # Clear the input field
                        st.session_state['user_input'] = ''

                # Text input for the user to send a message
                st.text_input("Type your message here:", key='user_input', on_change=handle_user_input)
                # --- End of Chat Interface ---

            except json.JSONDecodeError as e:
                st.error(f"Could not parse the JSON data: {e}")
                st.write("Response from the model:")
                st.code(response.text)
        else:
            st.error("No response generated by Gemini. Please try again.")
    else:
        st.error("Could not recognize any text from the audio. Please upload a clearer audio file.")
