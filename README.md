# MexaHackathon

Post-Natal Depression Analysis Prototype

Overview:

The Post-Natal Depression Analysis Tool is a Streamlit-based web application designed to assist in identifying and analyzing signs of postnatal depression through audio input. Users can upload an audio recording, which is then transcribed into text, analyzed using the Edinburgh Postnatal Depression Scale (EPDS) via Google’s Generative AI (Gemini API), and accompanied by a supportive chatbot interface to provide empathetic responses and suggestions.

Features:
	
  •	Audio Upload and Transcription
	
 •	Upload .wav audio files of spoken responses.
	
 •	Automatically transcribe audio to text using the speech_recognition library.
	
 •	EPDS-Based Analysis
  
  •	Analyze transcribed text based on the Edinburgh Postnatal Depression Scale (EPDS).
  
  •	Calculate a total score (0-30) to assess the likelihood and severity of postnatal depression.
  
  •	Identify emotions, cognitive distortions, and behavioral patterns from the transcribed text.
	
 •	Supportive Chatbot Interface
  
  •	Engage with a chatbot that provides empathetic and supportive responses based on the analysis.
	
 •	Offers suggestions and encourages seeking professional help if necessary.
	
 •	Note: The chatbot does not retain memory of past conversations.


Installation:

Add the Gemini API Key

Important: For security reasons, the Gemini API key is not included in the code. You must provide the API key to enable the application’s functionality on line 15.

Prerequisites:

•	Python 3.9 or higher: Ensure Python is installed on your system. You can download it from Python’s official website.

•	pip: Python’s package installer. It typically comes bundled with Python.

Step-by-Step Installation:
	
1.	Clone or Download the Project
Navigate to your desired directory and clone the repository or download the project files.

cd path/to/your/project

3.	Install Required Packages


Explanation of packages required:

•	streamlit: Framework for building interactive web applications in Python.

•	speechrecognition: Library for performing speech recognition, enabling audio transcription.

•	google-generativeai: Interface to interact with Google’s Generative AI (Gemini API) for text analysis.

•	pandas: Data manipulation and analysis library

•	numpy: Fundamental package for scientific computing with Python
	
 •	json5: A JSON extension that allows more human-friendly data structures.

Running the Application:

To launch the Streamlit application locally, follow these steps:
	1.	Navigate to the Project Directory in your terminal:
cd path/to/your/project
	2.	Run the Streamlit App
streamlit run Gemini.py

This command will start the Streamlit server and automatically open the application in your default web browser. If it doesn’t open automatically, you can access it by navigating to the URL provided in the terminal output (usually http://localhost:8501).

Usage:

1. Launch the Application:
   
Run the Streamlit app using the command mentioned above. Ensure your terminal is pointed to the project directory where Gemini.py resides.

2. Upload an Audio File:
   
	•	On the Streamlit webpage, locate the “Upload an audio file” section.

	•	Click the “Browse files” button and select a .wav audio file from your device.

•	(An example audio file is already present in the project directory for demonstration purposes.)

3. Process and Analyze:
   
  •	Once the audio is uploaded, the application will automatically transcribe the audio into text using the speech_recognition library.
  
  •	The transcribed text will be analyzed based on the EPDS criteria using Google’s Generative AI (Gemini API).
  
  •	Results, including emotions identified, cognitive distortions detected, behavioral patterns highlighted, and the total EPDS score, will be displayed in structured tables.

4. Interact with the Chatbot:

	•	Scroll down to the “ChatBot” section.

  •	Type your messages into the input field to receive supportive responses tailored to your analysis.
  
  (Note: The chatbot does not retain memory of past interactions and responses still need to be tailored with healthcare professionals and fine-tuning)

Example Audio: 
An example audio file named example_audio.wav is included in the project directory. This audio serves as a demonstration of how a parent experiencing postpartum depression might express their feelings and thoughts. Users can use this file to familiarize themselves with the application’s functionality before uploading their own recordings.

Chatbot Details:

Supportive Chatbot Features:

•	Empathetic Responses: Provides understanding and non-judgmental feedback based on the user’s EPDS score.

•	Resource Suggestions: Offers recommendations and encourages users to seek professional help if necessary.

•	Dynamic Configuration: Tailors responses according to the severity of depression indicated by the EPDS score.

Limitations: 
	•	No Memory: The chatbot does not retain information from past conversations, ensuring user privacy but limiting continuity.
	
 •	Not a Replacement for Professional Help: While the chatbot provides support and suggestions, it is not a substitute for medical advice or therapy.

Future Enhancements:

•	Implement Memory in Chatbot: Enhance the chatbot to retain conversation history, providing more personalized and context-aware interactions.

•	Support for Direct Audio Recording: Enhance the application to include a feature that allows users to record audio directly within the interface, which will then be automatically transcribed into text for analysis.

•	User Authentication in an App: Introduce user login features to secure sensitive data and personalize user experiences.

•	Data Visualization: Incorporate visual representations of the analysis results for better user comprehension.













Contact
For questions about the project, please reach out to:
	•	Email: thibaud.delavy@bluewin.ch
