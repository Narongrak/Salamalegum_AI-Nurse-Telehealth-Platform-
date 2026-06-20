import streamlit as st 
import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader

load_dotenv()
client = OpenAI(api_key=os.getenv("Mykey"))

def encode_image(upload_file):
  return base64.b64encode(upload_file.read()).decode("utf-8")

def extract_text(uploaded_file):
  read = PdfReader(uploaded_file)
  text = ""
  for page in read.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
  return text
def analyze_risk(symptom_text):
    symptom = symptom_text.lower()

    high_risk_keywords = [
        "chest pain", "can't breathe", "difficulty breathing",
        "severe pain", "unconscious", "bleeding heavily"
    ]

    medium_risk_keywords = [
        "fever", "rash", "headache", "cough",
        "sore throat", "vomiting", "dizziness"
    ]

    if any(word in symptom for word in high_risk_keywords):
        return {
            "level": "HIGH RISK",
            "message": "⚠️ This may be a serious condition. You should seek immediate medical attention."
        }

    elif any(word in symptom for word in medium_risk_keywords):
        return {
            "level": "MEDIUM RISK",
            "message": "🩺 It is recommended to consult a doctor for further check-up."
        }

    else:
        return {
            "level": "LOW RISK",
            "message": "✅ This seems not urgent, but monitor your symptoms and rest."
        }

with st.sidebar:
  st.image("catai.png", width=100)
  st.header("🧩Navigation Menu")
  page = st.sidebar.radio(
     "Select Feature:",
     ["🏡 Home Dashboard\n",
       "👩‍⚕️ AI Nurse Chatbot\n",
        "🤓 Smart Diagnosis Form"]
  )
  st.write("---")
  st.caption("⚠️ **Medical Disclaimer:**")
  st.caption(
            "This AI system provides preliminary screenings for educational and triage "
            "guidance only. It is **NOT** a substitute for professional medical advice, "
            "diagnosis, or treatment. Always consult a qualified healthcare provider "
            "for medical concerns."
    )
if page =="🏡 Home Dashboard\n":
    st.title("🏥 Nurse AI Telehealth Platform")
    st.subheader("Intelligent AI assistant system")
    st.write("---")
    
    st.markdown("""
    ### 💡 About the Platform
    This application is designed to address the issues of **"hospital overcrowding"** and **"limited healthcare access in remote areas"** by leveraging the power of a **Multimodal LLM (gpt-4o-mini)**.

    ### 📖 Quick User Guide
    * **👩‍⚕️ AI Nurse Chatbot:** An intelligent triage chatbot capable of answering health queries, analyzing images of wounds, rashes, or medications, and processing medical history documents.
                
    * **📊 Smart Diagnosis Form:** A comprehensive health screening form that analyzes symptoms, assesses health risks in percentages (%), and generates a downloadable summary report.
    """)
elif page == "👩‍⚕️ AI Nurse Chatbot\n":
    with st.sidebar:
       st.write("---")
       st.header("⚙️ Chat Controls")
       if st.button("🗑️ Clear Chat History",use_container_width=True):
          st.session_state.messages=[]
          st.rerun()
          
       uploaded_file = st.file_uploader(
         "Attach medical files/images",
        type=["png", "jpg", "jpeg", "pdf"]
        )
       
    st.title("👩‍⚕️ AI Nurse Chatbot")
    st.caption("AI Nurse Interactive Consultation")
    st.write("---")

    SYSTEMPROPT ="""
                Role: You are a friendly, cheerful, and kind nurse who provides helpful medical guidance. You always speak in polite and professional English.
Key Features:
- Provide clear recommendations on what the user should do next.
- Estimate possible diseases with percentage-based likelihood (%).
- Suggest appropriate over-the-counter medications when relevant.
- Analyze uploaded images (such as wounds or rashes) and PDF medical documents if provided.
Always respond in English.
                """
    if"messages" not in st.session_state:
        st.session_state.messages = []
    if"is_thinking" not in st.session_state:
        st.session_state.is_thinking = False

    user_input = st.chat_input("text",disabled = st.session_state.is_thinking)

    if user_input:
        st.session_state.messages = st.session_state.messages[-10:]
        content_list = [{"type":"text","text":user_input}]
        display_suffix = ""
    
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension == "pdf":
                extrated_text = extract_text(uploaded_file)
                content_list.append({"type": "text", "text": f"\n[Attached PDF Content]:\n{extrated_text}"})
                display_suffix = " 📄 [PDF Uploaded]"
            elif file_extension in ["png","jpg","jpeg"]:
                base64_image = encode_image(uploaded_file)
                content_list.append({"type":"image_url","image_url":{"url":f"data:image/{file_extension};base64,{base64_image}"}})
                display_suffix="📷 [Image Uploaded]"
      
        st.session_state.messages.append({
            "role":"user",
            "content":content_list,
            "display_text":user_input + display_suffix
            })
    
        try:
            with st.spinner("Ai is thinking..."):
                api_messages = [{"role":"system","content":SYSTEMPROPT}] + st.session_state.messages
            response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = api_messages,
                temperature = 0.7,
                max_tokens = 500
                )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = "Try again. An error occurred."
            print(e)
                
        st.session_state.messages.append({"role":"assistant","content":reply,"display_text":reply})
        st.rerun()
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            col1, col2 = st.columns([8,1])
            with col2 : st.image("patian.png",width = 70)
            with col1 : st.markdown(f'<div style = "background-color:#DCF6;padding:10px;border-radius:10px;margin-bottom:10px;text-align:right; color:black;">{msg["display_text"]}</div>',unsafe_allow_html = True)
        
        elif msg["role"] == "assistant":
            col1, col2 = st.columns([1,8])
            with col1 : st.image("catai.png",width = 70)
            with col2 : st.markdown(f'<div style = "background-color:#E8F0FE;padding:10px;border-radius:10px;margin-bottom:10px;text-align:left; color:black;">{msg["display_text"]}</div>',unsafe_allow_html = True)
                
elif page == "🤓 Smart Diagnosis Form":
    if "risk_level" not in st.session_state:
        st.session_state.risk_level = "UNKNOWN"

    if "risk_message" not in st.session_state:
        st.session_state.risk_message = ""
    if "latest_report" not in st.session_state:
        st.session_state.latest_report = ""
    st.title("📊 Smart Medical Diagnosis Form")
    st.subheader("Personalized Patient Triage and Symptom Analysis System")
    with st.form("diagosis_from"):
        st.write("📋 **Patient Profiles**")
        col_f1,col_f2 = st.columns(2)
        with col_f1:
           age = st.number_input("Age",min_value = 0, max_value = 120, value = 25)
        with col_f2:
           gender = st.selectbox("Gender",["Male","Female","other"])
        st.write("---")
        st.write("🩺 **Symptom Assessment**")
        main_symptom = st.text_area("Describe your current symptoms:")
        duration = st.slider("Days with Symptoms", min_value = 1, max_value = 30 , value = 1)
        medical_history = st.text_input("Underlying Medical Condition...")
    
        submit_button = st.form_submit_button("🔎Analyze")
    if submit_button:
      if not main_symptom:
       st.warning("Please describe")
      else:
        risk_result = analyze_risk(main_symptom)
        st.session_state.risk_level = risk_result["level"] 
        st.session_state.risk_message = risk_result["message"]

        risk_level = st.session_state.get("risk_level", "UNKNOWN")
        risk_message = st.session_state.get("risk_message", "")
        with st.spinner("AI is thinking..."):
            try:
                prompt_from = f"""
                Patient Risk Level: {risk_level}
                Advice: {risk_message}

                Please provide a structured medical screening based on this data.
                    Format the output with Clear Sections: 1. Possible Diseases with %, 2. Recommended Next Steps, 3. Suggested Medications.
                    - Age: {age} | Gender: {gender}
                    - Symptoms: {main_symptom} | Duration: {duration} days
                    - Medical History: {medical_history if medical_history else "None"}
                    """
                response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an expert triage nurse providing structured preliminary health assessments in polite English."},
                            {"role": "user", "content": prompt_from}
                        ],
                        temperature=0.4
                    )
                result_text = response.choices[0].message.content
                st.session_state.latest_report = result_text
            except Exception as e:
                st.error("An error occurred during analysis.")
                print(e)


    if "latest_report" in st.session_state and st.session_state.latest_report:
        if st.session_state.risk_level == "HIGH RISK":
            st.error(f"🔴 {st.session_state.risk_level}")
        elif st.session_state.risk_level == "MEDIUM RISK":
            st.warning(f"🟡 {st.session_state.risk_level}")
        else:
            st.success(f"🟢 {st.session_state.risk_level}")

        st.write(st.session_state.risk_message)

        st.write("---")
        st.write(st.session_state.latest_report)
        st.write("---")
    
        st.download_button(
            label = "Download",
            data = st.session_state.latest_report,
            file_name = "AI_Nurse_medical_report.txt",
            mime = "text/plain",
            use_container_width = True
            )
