from google import genai
import json
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Gemini client with API key from environment variable
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def getQuestions(profession, age, gender, emotion_type):
    sample_outputs = {
        "stress": [
            "On a scale of 1 to 10, how stressed do you feel today?",
            "What specific events or thoughts are contributing to your stress right now?"
        ],
        "anxiety": [
            "How often do you feel anxious or worried about everyday situations?",
            "Can you identify any triggers that increase your anxiety levels?"
        ],
        "anger": [
            "How frequently do you find yourself feeling angry or frustrated?",
            "What situations tend to provoke your anger the most?"
        ]
    }

    if emotion_type not in sample_outputs:
        raise ValueError(f"Invalid emotion type: {emotion_type}")

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=f"""
            I want to track the mental health of my user whose profession is {profession}, age {age}, and gender {gender}.
            As a mental health doctor, please provide exactly 2 clear and concise questions in English to track {emotion_type}.
            Ensure that the questions are relevant and easy to understand remember the prefession, age and gender of user provided.
            Format the output as a JSON array of strings, without any additional text or explanations.  
            For example: ["question 1", "question 2"]
            follow the above syntax of above example strictly.
            """
        )

        response_text = response.text.strip()
        response_text = re.sub(r'```json\n|```', '', response_text).strip()

        questions = json.loads(response_text)
        if not isinstance(questions, list) or len(questions) != 2 or not all(isinstance(q, str) for q in questions):
            raise ValueError("Invalid JSON format or incorrect number of questions.")
        return questions

    except Exception as e:
        print(f"Error getting {emotion_type} questions: {str(e)}")
        return sample_outputs[emotion_type]

def calculateScore(emotion_type, answers):
    """Calculates a mental health score based on user answers."""
    if emotion_type not in ["stress", "anxiety", "anger"]:
        raise ValueError("Invalid emotion type.")
    if not isinstance(answers, dict) or len(answers) != 2:
        raise ValueError("Answers must be a dictionary with 2 key-value pairs.")
    
    # Format the input for better analysis
    formatted_qa = ""
    for question, answer in answers.items():
        # Skip if question or answer is None
        if not question or not answer:
            return False
        formatted_qa += f"Question: {question}\nAnswer: {answer}\n"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            You are a mental health expert. Analyze these answers for {emotion_type} assessment:

            {formatted_qa}

            Rules for scoring:
            1. Score should be between 0-100
            2. Higher score means MORE {emotion_type.upper()}
            3. Consider:
               - Language used
               - Severity of described situations
               - Frequency of symptoms
               - Impact on daily life
            4. If answers are unrelated to {emotion_type} or nonsensical, return 101
            5. Be consistent in scoring similar answers

            Provide only a number (0-100) as response. No explanation needed.
            """
        )
        
        try:
            score = int(response.text.strip())
            if score == 101:
                return False
            if 0 <= score <= 100:
                return score
            return False
        except ValueError:
            print(f"Invalid score format: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error calculating {emotion_type} score: {str(e)}")
        return False
