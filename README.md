# Post-Natal Depression Analysis Prototype and UI interface

## MexaHackathon

### Overview

The Post-Natal Depression Analysis Tool originated from our previous hackathon, where we developed a Streamlit-based web application to help identify and analyze postnatal depression through audio input. 

In this hackathon, we are taking this idea further by enhancing the chatbot with memory capabilities and structuring conversations based on the five areas model of emotional distress (emotions, thoughts, behaviors, physical sensations and environment) in order to better understand post-partum depression and create the best intervention using reports and experiences from the interaction between the user and the chatbot. By leveraging our application, we hope to better assess the needs of individuals experiencing post-natal depression and provide more effective interventions in the future.

### 🔗 User Interface (Figma)
We have designed an interactive UI for our project using Figma. This interface represents how users will interact with the tool visually.
👉 [Click here to explore the UI](https://tdelavy.github.io/MexaHackathon/)

### Features

*1. Memory-Enabled Chatbot*

- Tracks conversation history for context-aware interactions

- Helps the user explore specific areas of emotional distress

*2. Extended Data Collection Beyond EPDS*

- Patients can provide additional insights beyond the questionnaire

- Helps collect more comprehensive data on postnatal depression

*3. Automated Report Generation*

- Extracts emotions, cognitive distortions, and behaviors from user responses

- Demonstrates the impact of engaging with the chatbot

- Highlights the extra information that would be missed with only the questionnaire

*4. Accessible Web Application*

- No installation required! The prototype is available online: 

- Users can still install it manually if preferred (see instructions below)

*5. User Response and Analysis Report Generation*

- EPDS score assessed by Gemini AI

- Emotions, cognitive distortions and behaviors identified during the analysis

- Additional insights provided by the user while conversing with the chatbot

- Discussion transcript between the chatbot and the user


### To use the prototype

***Launch the app from this link:***

https://postpartumdepression.streamlit.app

***Or***

***Install in your local computer:***

**Prerequisites**

- Python 3.9 or higher: Ensure Python is installed on your system. You can download it from .

- pip: Python’s package installer. It typically comes bundled with Python.

**Step-by-Step Installation**


*1.	Download the Project*

Navigate to the directory you want to download the project files from. Then, download the project files. Next, navigate to the project directory from your terminal using the command « cd path/to/your/project ».


*2.	Install Required Packages*

Install all dependencies listed in the requirements.txt file (still in the terminal)

	pip install -r requirements.txt


**Explanation of Requirements**

- streamlit: Framework for building interactive web applications in Python.

- speechrecognition: Library for performing speech recognition, enabling audio transcription.

- google-generativeai: Interface to interact with Google’s Generative AI (Gemini API) for text analysis.

- pandas: Data manipulation and analysis library

- numpy: Fundamental package for scientific computing with Python

- fpdf : A Python library used to generate PDF documents programmatically

- json5: A JSON extension that allows more human-friendly data structures

- Matplotlib: A Python library that enables the creation of visualizations
  

*Running the Application*

To launch the Streamlit application locally, follow these steps:

1.	Navigate to the Project Directory in your terminal:

		cd path/to/your/project

2.	Run the Streamlit App

		streamlit run Gemini.py

This command will start the Streamlit server and automatically open the application in your default web browser. If it doesn’t open automatically, you can access it by navigating to the URL provided in the terminal output (usually http://localhost:8501).

### Usage

***1. Launch the Application***

Run the Streamlit app (from the link to the app or locally)

***2. Upload an Audio File***

- On the Streamlit webpage, locate the “Upload an audio file” section.

- Click the “Browse files” button and select a .wav audio file from your device.

- (6 example audio files are already present in the project directory in github for demonstration purposes.)

***3. Process and Analyze***

- Once the audio is uploaded, the application will automatically transcribe the audio into text using the speech_recognition library.

- The transcribed text will be analyzed based on the EPDS criteria using Google’s Generative AI (Gemini API).

- Results, including emotions identified, cognitive distortions detected, behavioral patterns highlighted, and the total EPDS score, will be displayed in structured tables.

***4. Interact with the Chatbot***

- Scroll down to the “ChatBot” section.

- Type your messages into the input field to receive supportive responses tailored to your analysis.

When you’ve finished interacting with the chatbot and answering its questions, click « Done » to generate a summary of the situation and the model’s understanding. This will also generate the user report.

(Note: The chatbot remembers the context of past interactions)

***Example Audios***

6 example audio files named “PostNatalDepression_UserX.wav” are included in the project directory. These audios serve as a demonstration of how a parent experiencing postpartum depression might express their feelings and thoughts. Users can use this file to familiarize themselves with the application’s functionality before uploading their own recordings.

***Chatbot Details***

*Supportive Chatbot Features*

- Empathetic Responses: Provides understanding and non-judgmental feedback based on the user’s EPDS score.

- Resource Suggestions: Offers recommendations and encourages users to seek professional help if urgent.

- Dynamic Configuration: Tailors responses according to the severity of depression indicated by the EPDS score.
  

***Limitations***

- Not a Replacement for Professional Help: While the chatbot provides support and suggestions, it is not a substitute for medical advice or therapy. But it will be beneficial to design and create the most appropriate intervention for these patients suffering from postpartum depression.

***Future Enhancements***

- Improved chatbot intelligence with deeper contextual understanding

- Support for Direct Audio Recording: Enhance the application to include a feature that allows users to record audio directly within the interface, which will then be automatically transcribed into text for analysis.

- User Authentication in an App: Introduce user login features to secure sensitive data and personalize user experiences.

***Contact***

For questions about the project, please reach out to:

		Email: thibaud.delavy@bluewin.ch

