import streamlit as st
import gemini
from PyPDF2 import PdfReader  # For PDF parsing
import docx2txt #For docx file parsing
import re
import datetime


# Initialize Gemini API client
gemini_client = gemini.Client(api_key="AIzaSyDsO43WG0w0Y9bOCahrgwgMjMlkT9pYFWg") #Replace YOUR_API_KEY with your api key



st.title("Bid Preparation Prototype")

uploaded_file = st.file_uploader("Upload Bid Document", type=["pdf","docx"])


if uploaded_file is not None:
    bid_text = ""
    try:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                bid_text += page.extract_text()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                bid_text = docx2txt.process(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a PDF.")
            

        if bid_text:


            with st.spinner("Analyzing Bid Document..."):

                # Key Information Extraction (using regular expressions for now)
                key_dates = extract_key_dates(bid_text)
                eligibility_criteria = extract_eligibility_criteria(bid_text)
                # ... (add more extraction functions as needed) ...

                st.header("Key Information")
                st.write(key_dates)
                st.write(eligibility_criteria)
                # ... (display other extracted information) ...

                # Basic Eligibility Check (placeholder)
                st.header("Eligibility Check")
                user_input = st.text_area("Enter your company details (briefly)")
                if st.button("Check Eligibility"):
                    # This is a placeholder; replace with actual logic later.
                    st.write("Eligibility check logic will be implemented here. For now, checking if user input exists:")
                    if user_input:
                        st.write("User input provided. More detailed checks will be added.")
                    else:
                        st.write("Please provide your company details.")
    except Exception as e:
        st.error(f"An error occurred during document processing: {e}")





# Helper functions for information extraction (using regular expressions)
def extract_key_dates(text):
    dates = {}
    date_patterns = [
        r"(\d{2}\.\d{2}\.\d{4})",  # DD.MM.YYYY
        r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
        # ... Add more date patterns as needed
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:

                date_obj = datetime.datetime.strptime(match, "%d.%m.%Y").date() #converting date to DD.MM.YYYY format
            except ValueError:
                pass #Ignore if some other format is passed
            else:
                dates[match] = match
                

    return dates


def extract_eligibility_criteria(text):
     # Placeholder for now. Replace with Gemini API or more robust extraction.
    criteria = []

    try:
        # Define keywords or phrases related to eligibility criteria.
        keywords = ["eligibility criteria", "minimum requirements", "qualifications", "must meet"]

        # Split the text into sentences.
        sentences = text.split(". ")

        # Iterate through the sentences and check for keywords.
        for sentence in sentences:
            for keyword in keywords:
                if keyword in sentence.lower():
                    criteria.append(sentence)
    except Exception as e:
         st.error(f"An error occurred during eligibility criteria extraction: {e}")       
    return criteria





# ... (Add more extraction functions as needed)
