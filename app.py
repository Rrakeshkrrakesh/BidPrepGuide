import streamlit as st
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import json
import os
from PyPDF2 import PdfReader
from docx import Document
from pytesseract import image_to_string
from PIL import Image

# Access the API key from Streamlit secrets
api_key = st.secrets["API_KEY"]

# Initialize Gemini client
genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# --- Function definitions ---

def process_uploaded_file(uploaded_file):
    try:
        file_content = uploaded_file.read()
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(file_content)
            extracted_text = " ".join(page.extract_text() for page in reader.pages)
        elif uploaded_file.name.endswith(".docx"):
            doc = Document(file_content)
            extracted_text = " ".join([p.text for p in doc.paragraphs])
        elif uploaded_file.name.endswith(".txt"):
            extracted_text = file_content.decode("utf-8")
        else:  # Assume it's an image
            image = Image.open(uploaded_file)
            extracted_text = image_to_string(image)
        return extracted_text
    except Exception as e:
        st.error(f"An error occurred during file processing: {e}")
        return None

def extract_entities_with_gemini(text):
    try:
        response = gemini_model.generate_content(
            f"""Extract the following entities from this text, providing them in a structured JSON format:\n
            * Dates (submission deadlines, important dates)\n
            * Eligibility Criteria\n
            * Technical Specifications\n
            * Pricing and Financial information\n
            * Scope of Work\n
            * Penalty Clauses\n
            * Contact Information\n\n
            Text: {text}""",
            generation_config=GenerationConfig(
                temperature=0.0,
                candidate_count=1
            )
        )
        response_text = response.text
        try:
            extracted_entities = json.loads(response_text)
            return extracted_entities
        except json.JSONDecodeError:
            st.warning("Gemini's response could not be parsed as JSON. Returning raw text.")
            return response_text
    except Exception as e:
        st.error(f"An error occurred during entity extraction: {e}")
        return None

def determine_eligibility(extracted_info):
    # Placeholder for eligibility logic
    return "Eligible"  # Replace with actual logic

def chat_with_document(text, user_message):
    try:
        chat = gemini_model.start_chat(
            history=[{"role": "system", "parts": [text]}]
        )
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        st.error(f"An error occurred during chat: {e}")
        return None

def generate_bid_document(data, output_file="Generated_Bid_Document.docx"):
    try:
        doc = Document()
        doc.add_heading("Bid Submission", level=1)
        doc.add_paragraph(f"Bidder Name: {data.get('name', 'N/A')}")
        doc.add_paragraph(f"Eligibility Status: {data.get('eligibility', 'N/A')}")
        doc.add_paragraph(f"Estimated Cost: ${data.get('cost', 'N/A')}")
        # Add other bid data here
        doc.save(output_file)

        with open(output_file, "rb") as file:
            st.download_button(
                label="Download Bid Document",
                data=file,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    except Exception as e:
        st.error(f"An error occurred during bid document generation: {e}")

# --- Streamlit UI ---

st.title("Bid Preparation App")

uploaded_file = st.file_uploader("Upload Bid Document", type=["pdf", "docx", "txt", "jpg", "png"])

if uploaded_file is not None:
    extracted_text = process_uploaded_file(uploaded_file)
    if extracted_text:
        with st.spinner("Analyzing document..."):
            extracted_info = extract_entities_with_gemini(extracted_text)
            if extracted_info:
                st.header("Extracted Information")
                st.write(extracted_info)

                st.header("Bid Preparation")
                bidder_name = st.text_input("Enter your name/company:")
                estimated_cost = st.number_input("Enter estimated cost (in USD):", value=0.0, step=1.0)

                if st.button("Generate Bid Document"):
                    bid_data = {
                        "name": bidder_name,
                        "eligibility": determine_eligibility(extracted_info),
                        "cost": estimated_cost
                    }
                    generate_bid_document(bid_data)
                    st.success("Bid document generated!")

                st.header("Chat with the Document")
                user_message = st.text_input("Enter your question:")
                if st.button("Ask"):
                    response = chat_with_document(extracted_text, user_message)
                    if response:
                        st.write("Gemini's Response:")
                        st.write(response)
    else:
        st.error("Could not extract text from the document.")
