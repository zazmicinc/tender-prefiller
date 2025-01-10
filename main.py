import base64
import streamlit as st
import google.generativeai as genai
if 'API_KEY' not in st.session_state:
    st.session_state['API_KEY'] = ''

def encode_file_to_base64(file):
    """
    Encodes an uploaded file to Base64 format for model input.
    
    :param file: Uploaded file (BytesIO)
    :return: Base64-encoded string of the file content
    """
    return base64.standard_b64encode(file.read()).decode("utf-8")

# Streamlit App Layout
st.title("Tender Document Automation")
st.write("Upload a Request for Tender (RFT) document and a Tender Response Document (TRD). The app will prefill the TRD using the information from the RFT.")

if not st.session_state['API_KEY']:
    st.text_input("Enter API Key first", key="API_KEY")
else:
    genai.configure(api_key=st.session_state['API_KEY'])
    model = genai.GenerativeModel("gemini-1.5-flash")

    # File upload widgets
    rft_file = st.file_uploader("Upload Request for Tender (RFT) Document", type=["pdf"])
    trd_file = st.file_uploader("Upload Tender Response Document (TRD) Template", type=["pdf"])
    company_info_file = st.file_uploader("Upload Company Information (TXT)", type=["txt"])

    # Process button
    if st.button("Generate Prefilled Document"):
        if not rft_file or not trd_file:
            st.error("Please upload both the RFT and TRD documents.")
        else:
            try:
                # Encode files to Base64
                rft_base64 = encode_file_to_base64(rft_file)
                trd_base64 = encode_file_to_base64(trd_file)

                company_info = company_info_file.read().decode("utf-8")

                # Define the prompt
                prompt = f"""
                You are a document automation assistant. You are provided with three inputs:
                1. A Request for Tender (RFT) document (Base64-encoded) containing details about the tender, including requirements, scope, and evaluation criteria.
                2. A Tender Response Document (TRD) template (Base64-encoded) that needs to be filled based on the RFT and the company's information.
                3. Company information in plain text, which includes general details about the company's expertise, certifications, solutions, and experience.

                Your task is to:
                - Extract relevant information from the RFT document.
                - Use the company information to prefill fields in the TRD wherever applicable.
                - For fields that require specific or detailed information (e.g., technical specifications), provide a general response based on common practices. For example:
                  - **Data Residency:** Prefill with a generic statement like "Our solution ensures that all data is stored within the EU/EEA, meeting residency requirements."
                  - **Data Protection Requirements:** Prefill with a statement like "Our solution complies with GDPR and ensures robust data security measures as outlined in the RFT."
                  - **Project Archtecture:** Prefill fileds that require Project or Solution Archtecture with general soultion based on your knowledge
                - Try to fill as much fileds as possible, information will be corrected after you, this is just to have prefilled informaiton.

                Here is the company information provided:
                {company_info}
                """

                print(len(rft_base64))
                print(len(trd_base64))

                # Prepare model input
                model_input = [
                    {'mime_type': 'application/pdf', 'data': rft_base64},
                    {'mime_type': 'application/pdf', 'data': trd_base64},
                    prompt
                ]

                print("Waiting for response...")
                # Generate response
                response = model.generate_content(model_input)

                if hasattr(response, "text") and isinstance(response.text, str):
                    st.success("The TRD document has been prefilled successfully!")
                    st.markdown("### Prefilled Tender Response Document")
                    st.markdown(response.text)
                else:
                    st.error("Unexpected response format from the AI model.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")