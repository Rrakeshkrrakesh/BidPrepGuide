import streamlit as st
from utils import (
    process_uploaded_file,
    extract_entities_with_gemini,
    check_eligibility,
    generate_bid_document,
)

# Title and Sidebar Navigation
st.title("Bid Preparation App")
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Upload Document", "Eligibility Checker", "Pricing", "Generate Bid"])

# Initialize State
if "uploaded_text" not in st.session_state:
    st.session_state["uploaded_text"] = ""

if page == "Upload Document":
    st.header("Upload Bid Document")
    uploaded_file = st.file_uploader("Upload your bid document", type=["pdf", "docx", "txt"])
    if uploaded_file:
        text = process_uploaded_file(uploaded_file)
        st.session_state["uploaded_text"] = text
        st.write("Extracted Text:")
        st.text(text)

elif page == "Eligibility Checker":
    st.header("Eligibility Checker")
    if st.session_state["uploaded_text"]:
        user_profile = {"certifications": "ISO 9001", "financial_threshold": 1000000}
        criteria = extract_entities_with_gemini(st.session_state["uploaded_text"])
        eligibility = check_eligibility(user_profile, criteria)
        st.write("Eligibility Check Results:")
        st.json(eligibility)
    else:
        st.warning("Please upload a document first.")

elif page == "Pricing":
    st.header("Pricing and Financial Planning")
    labor_cost = st.number_input("Enter labor cost", min_value=0.0)
    material_cost = st.number_input("Enter material cost", min_value=0.0)
    total_cost = labor_cost + material_cost
    st.write(f"Estimated Total Cost: {total_cost}")

elif page == "Generate Bid":
    st.header("Generate Bid Document")
    if st.session_state["uploaded_text"]:
        data = {
            "name": "Your Company",
            "eligibility": "Eligible",
            "cost": 100000,
        }
        generate_bid_document(data)
        st.success("Bid document generated! Check your project directory.")
    else:
        st.warning("Please upload a document first.")
