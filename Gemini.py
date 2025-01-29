#cd /Users/thib/Desktop/Hackathon
#streamlit run Gemini.py

import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
import google.generativeai as genai
import json
import pandas as pd 
import re
import json5
import os
import subprocess
import time
import tempfile
import platform
import sys
import base64
import io

st.set_page_config(layout="wide", page_title="Analysis & Chatbot", page_icon="🤖")

# Configure the Gemini API key
genai.configure(api_key="AIzaSyD2d-LH2uLMRQwNFBiN9AQwLpO1CgiDfRw")

# Questionnaire and scoring instructions
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
    - Do not make interpretations. If a question is not answered, provide a rationale for the score of 0.
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

def refine_recognized_text(recognized_text, user_message):
    """
    Combine the recognized text with user-provided additional information.
    """
    return f"{recognized_text.strip()} {user_message.strip()}"

# Initialize the chat messages if not already done
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'additional_info' not in st.session_state:
    st.session_state['additional_info'] = ""

if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = {}

if 'explanation' not in st.session_state:
    st.session_state['explanation'] = None  # No explanation yet

if 'new_user_messages' not in st.session_state:
    st.session_state['new_user_messages'] = []  # Will only store user inputs after analysis


# Streamlit UI
st.title("Post-Natal Depression 🤖")
st.write("Upload an audio file, and this app will analyze the emotions, cognitive distortions, and behavioral patterns.")

# Dropdown for Gemini model selection
available_models = ["gemini-2.0-flash-exp", "gemini-1.5-pro"]
selected_model = st.selectbox("Select the Gemini model to use:", available_models)
model = genai.GenerativeModel(selected_model)

if selected_model == "gemini-2.0-flash-exp":
    st.success("Note: This model processes data significantly faster but may occasionally produce formatting errors in responses. If you experience any issues, please reload the page.")
elif selected_model == "gemini-1.5-pro":
    st.warning("Note: This model takes more time to process.")

# File Upload Widget
uploaded_file = st.file_uploader("Upload an audio file (.wav format)", type=["wav"])
if uploaded_file is not None:
    uploaded_filename = uploaded_file.name 

    st.info("Processing audio file...")

    # A horizontal line to separate sections
    st.markdown("---")
    
    # Process the audio file
    recognized_text = process_audio_file(uploaded_file)

    if recognized_text:
        st.subheader("Recognized Text")
        st.write(recognized_text)

        st.info("Analyzing text with Gemini...")

        if "analysis_result" not in st.session_state or not st.session_state['analysis_result']:
            response = analyze_text_with_prompt(recognized_text)
            
            if response and hasattr(response, 'text'):
                try:
                    # Extract the JSON code block
                    json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response.text)
                    if json_match:
                        json_str = json_match.group(1)
                        parsed_response = json5.loads(json_str)
                        explanation = response.text[json_match.end():].strip()
                        
                        # Save to session state
                        st.session_state['analysis_result'] = parsed_response
                        st.session_state['explanation'] = explanation
                    else:
                        st.error("Could not find JSON data in the response.")
                        parsed_response = {}
                        explanation = ""
                except json.JSONDecodeError as e:
                    st.error(f"Could not parse the JSON data: {e}")
                    st.write("Response from the model:")
                    st.code(response.text)
        else:
            # If already analyzed, use the saved results
            parsed_response = st.session_state['analysis_result']
            explanation = st.session_state['explanation']    

                        # Use the saved analysis result
        parsed_response = st.session_state.analysis_result
        explanation = st.session_state.explanation

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

        # Debug: Print scores list and total score
        print(f"Debug: Scores List: {scores_list}")
        print(f"Debug: Calculated Total Score: {total_score}")

        # Prepare question scores string
        question_scores_str = "\n".join(
            f"Question {q}: Score: {details['score']}, Rationale: {details['rationale']}"
            for q, details in question_scores.items()
        )

        # Debug: Print question scores string
        print(f"Debug: Question Scores String:\n{question_scores_str}")

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

        # Ensure the first chatbot message is always present
        if not any(msg['content'] == "How have you been feeling about your baby and parenting recently?" for msg in st.session_state['messages']):
            st.session_state['messages'].insert(0, {'role': 'bot', 'content': "How have you been feeling about your baby and parenting recently?"})


        # Generate a summary of the analysis at the beginning of the chatbot
        if 'summary_generated' not in st.session_state:
            # Create a prompt to send to Gemini for summary generation
            summary_prompt = f"""
            You are a **compassionate, non-judgmental chatbot** assisting someone who has completed an assessment for postnatal depression.
            ---
            Based on the analysis provided below:

            - Total Score: {total_score}
            - Interpretation: {interpretation}
            - Emotions Identified: {', '.join(emotions_list)}
            - Cognitive Distortions Detected: {', '.join(distortions_list)}
            - Behavioral Patterns Noted: {', '.join(behaviors_list)}

            generate a concise and brief summary in a empathetic, comprehensive and non-judgmental tone asking the user if this accurately reflects their situation. 

            You should use a flexible conversation based on the five areas model of emotional distress (emotions, thoughts, behaviors, physical sensations, and environment) and the user's explanation after the analysis if there is any.
            Make sure you ask questions in order to understand the user's situation better and shape a summary that reflects their problems back to them accurately.

            Important:
                - You should always provide a little summary for each area of the five areas model based on the user's explanation. 
                - Maintain an understanding, non-judgmental tone.
                - Do not provide medical diagnoses, recommandations or specific treatment. You try to understand the user's situation.
            
            """
# Ask flexible conversation based on the five areas model of emotional distress (emotions, thoughts, behaviors, physical sensations, and environment) and the user's explanation after the analysis if there is any.

            # Send the prompt to Gemini
            summary_response = model.generate_content(summary_prompt)
            summary_text = summary_response.text.strip()

            # Append the generated summary to the messages
            st.session_state['messages'].append({'role': 'user', 'content': recognized_text})
            st.session_state['messages'].append({'role': 'bot', 'content': summary_text})
            st.session_state['summary_generated'] = True

        # Display existing chat messages
        display_chat(st.session_state['messages'], chat_container)

        # Callback function for handling user input
        def handle_user_input():
            user_message = st.session_state['user_input']
            if user_message:
                # Append the user's message to the conversation
                st.session_state['messages'].append({'role': 'user', 'content': user_message})
                st.session_state['new_user_messages'].append(user_message)

                if user_message.lower() == "done":
                    # When the user finishes providing input, send everything to Gemini

                    added_info = "\n".join(st.session_state['new_user_messages'])  # Only new user messages

                    full_context = "\n".join(
                        f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state['messages']
                    )

                    final_prompt = f"""
                    You're doing research on postnatal depression and have been asked to provide a response to a user who has just completed an assessment for postnatal depression.
                    You're giving the user's final summary of all your understanding of the situation. Be empathetic and understanding in your response.
                    
                    Based on the analysis summary and the following conversation made by the user:
                    {full_context}

                    Generate a final, empathetic response that:
                    - Summarizes the situation based on the analysis using the patient's severity level ({interpretation}) and use the user's explanation after the analysis if there is any. 
                    - if some important symptoms are detected (like suicidal thougths, or harming themselves, ...), encourages the user to seek professional help. 
                    - Thanks the user for sharing their thoughts and feelings.

                    Important:
                    - Maintain an comprehensive, non-judgmental tone.
                    - Do not providing medical diagnoses or specific treatment recommendations.
                    """

                    final_response = model.generate_content(final_prompt)
                    st.session_state['messages'].append({'role': 'bot', 'content': final_response.text.strip()})

                                # Lock the chat by setting the flag
                    st.session_state['chat_locked'] = True

                    question_scores_str = "\n".join(
                        f"Question {q}: Score: {details['score']}, Rationale: {details['rationale']}"
                        for q, details in question_scores.items()
                    )

                    # Prepare data for the report
                    report_data = {
                        "total_score": total_score,
                        "interpretation": interpretation,
                        "emotions": emotions_list,
                        "distortions": distortions_list,
                        "behaviors": behaviors_list,
                        "question_scores": question_scores_str,
                        "full_context": full_context,
                        "added_info": added_info,  # Include added user input here
                        "audio_filename": uploaded_filename, 
                    }

                    # Debug: Print the data being saved
                    print(f"Debug: Report data:\n{json.dumps(report_data, indent=4)}")

                    # Save data to a temporary JSON file
			try:
			    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_json:
			        json.dump(report_data, temp_json, ensure_ascii=False, indent=4)
			        temp_json_path = temp_json.name
			
			    # Call `generate_report.py` and capture the output PDF bytes
			    process = subprocess.Popen(
			        [sys.executable, "generate_report.py", temp_json_path],
			        stdout=subprocess.PIPE, stderr=subprocess.PIPE  # Capture both stdout (PDF) and stderr (errors)
			    )
			    pdf_bytes, error_bytes = process.communicate()  # Wait for the process to finish
			
			    if process.returncode != 0:
			        raise subprocess.CalledProcessError(process.returncode, "generate_report.py", error_bytes)
			
			    # Create a download button for the generated PDF
			    st.download_button(
			        label="Download Report as PDF",
			        data=pdf_bytes,  # Raw PDF bytes
			        file_name="post_natal_analysis_report.pdf",
			        mime="application/pdf"
			    )
			
			    st.success("The analysis report has been successfully generated. Click the button above to download.")
			
			except subprocess.CalledProcessError as e:
			    st.error(f"Error generating the report: {e.stderr.decode()}")  # Show any errors
			except Exception as e:
			    st.error(f"Unexpected error: {str(e)}")

                    st.session_state['chat_locked'] = True

                else:
                    # Generate a response to the user's input
                    feedback_prompt = f"""
                    You are a **supportive, understanding chatbot** helping someone who is discussing their feelings about postnatal depression.  

                    **User's new input:**  
                    "{user_message}"  

                    **TASK:**  
                    - **Acknowledge** what they have said in a warm, non-judgmental way.  
                    - **Encourage** them to clarify, correct, or expand on anything.  
                    - **Make it conversational**, like a real human responding. You should help to user to delve deeper into their situation. Ask questions based on the user input using the five areas model of emotional distress (emotions, thoughts, behaviors, physical sensations, and environment) and the user's explanation after the analysis in order to gather more information
                    - **DO NOT** provide solutions, advice, or medical support.  
                    - **Limit response to 5.6 sentences max.**  

                    **FORMAT EXAMPLE:**  
                    *"Thank you for sharing that. It sounds like you’re feeling ____, and I can see why that would be difficult. I appreciate you opening up about this.
                    These are some characteristics that are often used as identifiers for people: ethnicity, gender, sexuality, disability religion and more. Are there any important areas you would like to highlight to me?"*

                    **Tips for your response:**  
                    - Keep it **empathetic and engaging** (avoid robotic responses).   
                    - If the user's message includes **specific concerns**, refer to them **naturally** in your response.  

                    **DO NOT:**  
                    - Use **bullet points** in your response.  
                    - Provide **advice** or **interpret their feelings**—just reflect back in a supportive way.  
                    """
                    feedback_response = model.generate_content(feedback_prompt)
                    st.session_state['messages'].append({'role': 'bot', 'content': feedback_response.text.strip()})

                # Clear the input field
                st.session_state['user_input'] = ''

        # Initialize the chat_locked flag in session state
        if 'chat_locked' not in st.session_state:
            st.session_state['chat_locked'] = False

        # Conditional text input field
        if not st.session_state['chat_locked']:
            st.text_input("Type your message here (type 'Done' when finished):", key='user_input', on_change=handle_user_input)
        else:
            st.info("The chat has ended. Thank you for sharing your thoughts.")

    else:
        st.error("No response generated by Gemini. Please try again.")
