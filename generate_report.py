import sys
import os
import json
from fpdf import FPDF
import matplotlib.pyplot as plt
import re
import google.generativeai as genai

# Initialize Gemini
genai.configure(api_key="AIzaSyD2d-LH2uLMRQwNFBiN9AQwLpO1CgiDfRw")
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Ensure the "Reports" folder exists in the current directory
reports_dir = "Reports"
if not os.path.exists(reports_dir):
    os.makedirs(reports_dir)
    print(f"The 'Reports' folder has been created at {os.path.abspath(reports_dir)}")
else:
    print(f"The 'Reports' folder already exists at {os.path.abspath(reports_dir)}")

def clean_text_for_pdf(text):
    """
    Replace unsupported Unicode characters with their 'latin-1' equivalents or safe substitutes.
    """
    replacements = {
        "\u2019": "'",  # Right single quotation mark
        "\u2018": "'",  # Left single quotation mark
        "\u201C": '"',  # Left double quotation mark
        "\u201D": '"',  # Right double quotation mark
        "\u2013": "-",  # En dash
        "\u2014": "-",  # Em dash
        # Add more replacements as needed
    }
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    return text

# Debug: Check the input JSON file path
print(f"Debug: Input JSON file path: {sys.argv[1]}")

# Load data from JSON file
try:
    with open(sys.argv[1], "r") as file:
        data = json.load(file)
except Exception as e:
    print(f"Error loading JSON file: {e}")
    sys.exit(1)

# Debug: Print the loaded JSON data
print(f"Debug: Loaded JSON data:\n{json.dumps(data, indent=4)}")

# Extract data
try:
    total_score = data["total_score"]
    interpretation = data["interpretation"]
    emotions = data["emotions"]
    distortions = data["distortions"]
    behaviors = data["behaviors"]
    question_scores_str = data["question_scores"]
    full_context = data["full_context"]
    audio_filename = data.get("audio_filename", "default.wav") 
except KeyError as e:
    print(f"Error: Missing key in JSON data: {e}")
    sys.exit(1)

# Extract user folder name from audio_filename
user_folder_name = audio_filename.split("_")[1].replace(".wav", "")  # Extract "User1" or similar

# Extract user-added information
added_info = data.get("added_info", "")

# Call Gemini to extract keywords
if added_info:
    prompt = f"""
    The user has provided the following additional information:
    "{added_info}"

    Your task is to extract relevant keywords under the following categories:
    - Emotions
    - Cognitive Distortions
    - Behaviors

    Provide the result in the following JSON format:
    ```json
    {{
        "emotions": ["list of emotion keywords"],
        "cognitive_distortions": ["list of cognitive distortion keywords"],
        "behaviors": ["list of behavior keywords"]
    }}
    ```

    If there is no additional information or the user has not provided any new input, respond with the following JSON format:
    ```json
    {{
        "message": "The user didn't add any other information."
    }}
    ```
    """

    response = model.generate_content(prompt)
    try:
        json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response.text)
        if json_match:
            json_str = json_match.group(1)
            added_keywords = json.loads(json_str)

            # Check if the "message" field exists
            if "message" in added_keywords:
                print(f"Gemini response: {added_keywords['message']}")
                added_keywords = {"emotions": [], "cognitive_distortions": [], "behaviors": []}
        else:
            added_keywords = {"emotions": [], "cognitive_distortions": [], "behaviors": []}
    except json.JSONDecodeError:
        added_keywords = {"emotions": [], "cognitive_distortions": [], "behaviors": []}
else:
    # Default case where added_info is empty
    added_keywords = {
        "message": "The user didn't add any other information.",
        "emotions": [],
        "cognitive_distortions": [],
        "behaviors": [],
    }

# Create the user-specific folder inside "Reports"
reports_dir = "Reports"
user_folder_path = os.path.join(reports_dir, user_folder_name)
os.makedirs(user_folder_path, exist_ok=True)


# Call Gemini to identify and explain possible causes
if full_context:
    prompt = f"""
    This is the interaction between a potential post-partum depression patient and a chatbot. The following full discussion context:
    "{full_context}"

    Your task is to identify possible causes (maximum 3) for postnatal depression mentioned by the user. For each cause, explain why it might contribute to depression by referencing specific statements or ideas shared by the user. Do not interpret. Only provide explanations based on the user's input.

    Return the result in the following JSON format:
    ```json
    {{
        "causes": [
            {{
                "cause": "brief description of the cause",
                "explanation": "reason why this might contribute to depression, based on user input"
            }},
            ...
        ]
    }}
    ```

    If no causes are explicitly or implicitly mentioned, respond with the following JSON format:
    ```json
    {{
        "message": "No specific causes mentioned by the user."
    }}
    ```
    """

    response = model.generate_content(prompt)
    try:
        json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response.text)
        if json_match:
            json_str = json_match.group(1)
            cause_data = json.loads(json_str)

            # Check if the "message" field exists
            if "message" in cause_data:
                print(f"Gemini response: {cause_data['message']}")
                possible_causes = []
            else:
                possible_causes = cause_data.get("causes", [])
        else:
            possible_causes = []
    except json.JSONDecodeError:
        possible_causes = []
else:
    # Default case where full_context is empty
    possible_causes = []
    print("No full context provided.")

# Ensure UTF-8 support in the PDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", size=12)
        self.cell(0, 10, "Post-Natal Depression Analysis Report", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

# Create the Reports folder if it doesn't exist
os.makedirs("Reports", exist_ok=True)

# Initialize PDF
# Initialize PDF
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Title
pdf.set_font("Arial", size=16, style="B")
pdf.cell(200, 10, clean_text_for_pdf(user_folder_name), ln=True, align="C")
pdf.ln(10)

# Summary Section
pdf.set_font("Arial", size=12, style="B")
pdf.cell(200, 10, clean_text_for_pdf("EPDS Score by Gemini"), ln=True)
pdf.ln(5)
pdf.set_font("Arial", size=10)
pdf.multi_cell(0, 10, clean_text_for_pdf(f"Total Score: {total_score}"))
pdf.multi_cell(0, 10, clean_text_for_pdf(f"Interpretation: {interpretation}"))
pdf.ln(5)

# Visualization Section
pdf.set_font("Arial", size=12, style="B")
pdf.cell(200, 10, clean_text_for_pdf("Results"), ln=True)
pdf.set_font("Arial", style="BI", size=8)  # BI = Bold + Italic
pdf.set_text_color(0, 0, 255)  # Blue color for the link
pdf.cell(200, 10, "Click here for the EPDS questionnaire", ln=True, link="https://med.stanford.edu/content/dam/sm/ppc/documents/DBP/EDPS_text_added.pdf")
pdf.set_text_color(0, 0, 0)
pdf.ln(5)

# Chart 1: EPDS Question Score Breakdown
try:
    # Extract the scores from the string using regex
    scores = [int(re.search(r"Score: (\d+)", line).group(1)) for line in question_scores_str.split("\n") if "Score" in line]
    print(f"Debug: Scores for chart: {scores}")
    # Calculate the total score as the sum of all scores
    total_score_from_scores = sum(scores)
    print(f"Debug: Total score calculated from scores: {total_score_from_scores}")
except Exception as e:
    print(f"Error extracting scores for chart: {e}")
    sys.exit(1)

questions = [f"Q{i}" for i in range(1, len(scores) + 1)]
plt.figure(figsize=(8, 5))
plt.bar(questions, scores, color="skyblue")
plt.title("EPDS Question Scored by Gemini")
plt.xlabel("Questions")
plt.ylabel("Scores")
plt.tight_layout()
chart_path = os.path.join(user_folder_path, "EPDS_score_Gemini.png")
plt.savefig(chart_path)
plt.close()

# Add Chart to PDF
pdf.image(chart_path, x=40, w=120)

# Emotional and Cognitive Insights Section
pdf.set_font("Arial", size=12, style="B")
pdf.cell(200, 10, clean_text_for_pdf("Emotions, Cognitive Distortions, and Behaviors"), ln=True)
pdf.ln(5)
pdf.set_font("Arial", size=10)
pdf.multi_cell(0, 10, clean_text_for_pdf(f"Emotions Identified: {', '.join(emotions)}"))
pdf.multi_cell(0, 10, clean_text_for_pdf(f"Cognitive Distortions Detected: {', '.join(distortions)}"))
pdf.multi_cell(0, 10, clean_text_for_pdf(f"Behavioral Patterns Noted: {', '.join(behaviors)}"))
pdf.ln(10)

# Add user-added keywords section
pdf.set_font("Arial", size=12, style="B")
pdf.cell(200, 10, "Info added by the user after the analysis", ln=True)
pdf.ln(5)
pdf.set_font("Arial", size=10)
pdf.multi_cell(0, 10, f"Emotions: {', '.join(added_keywords['emotions'])}")
pdf.multi_cell(0, 10, f"Cognitive Distortions: {', '.join(added_keywords['cognitive_distortions'])}")
pdf.multi_cell(0, 10, f"Behaviors: {', '.join(added_keywords['behaviors'])}")
pdf.ln(10)

# Add a section for Possible Causes with Explanations
pdf.set_font("Arial", size=12, style="B")
pdf.cell(200, 10, "Possible Causes of Depression", ln=True)
pdf.ln(5)

pdf.set_font("Arial", size=10)
if possible_causes:
    for cause in possible_causes:
        pdf.multi_cell(0, 10, f"- Cause: {cause['cause']}")
        pdf.multi_cell(0, 10, f"  Explanation: {cause['explanation']}")
        pdf.ln(5)
else:
    pdf.multi_cell(0, 10, "No specific causes mentioned by the user.")
pdf.ln(10)

# Question Scores Section
pdf.set_font("Arial", size=12, style="B")
pdf.cell(200, 10, clean_text_for_pdf("Question Scores and Rationales"), ln=True)
pdf.ln(5)
pdf.set_font("Arial", size=10)
for line in question_scores_str.split("\n"):
    print(f"Debug: Adding question score to PDF: {line}")
    pdf.multi_cell(0, 10, clean_text_for_pdf(line))
pdf.ln(10)

# Chat Context Section
pdf.set_font("Arial", size=12, style="B")
pdf.cell(200, 10, clean_text_for_pdf("Full Chat Context"), ln=True)
pdf.ln(5)
pdf.set_font("Arial", size=10)
pdf.multi_cell(0, 10, clean_text_for_pdf(full_context))
pdf.ln(10)

# Save PDF
output_path = os.path.join(user_folder_path, "post_natal_analysis_report.pdf")
try:
    pdf.output(output_path)
    print(f"PDF report successfully generated at {output_path}")
except Exception as e:
    print(f"Error saving PDF: {e}")
