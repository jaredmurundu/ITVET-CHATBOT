import streamlit as st
import fitz  # PyMuPDF
import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import pandas as pd

# ------------------- Admin Setup -------------------
ADMIN_EMAIL = "jmurundu@cuk.ac.ke"
ADMIN_PASSWORD = "34262059"
RAW_GITHUB_PDF = "https://raw.githubusercontent.com/jaredmurundu/ITVET-CHATBOT/main/sample_results.pdf"
PDF_FILE = "sample_results.pdf"
SMTP_USER = ADMIN_EMAIL
SMTP_PASSWORD = "ylnf zlwk dvnr bqns"

if "admin" not in st.session_state:
    st.session_state["admin"] = False

# ------------------- Download PDF -------------------
def download_pdf_from_github():
    try:
        if not os.path.exists(PDF_FILE):
            response = requests.get(RAW_GITHUB_PDF)
            with open(PDF_FILE, "wb") as f:
                f.write(response.content)
    except Exception as e:
        st.error(f"❌ Could not fetch results PDF: {e}")

# ------------------- PDF Extractor -------------------
def extract_result_page(pdf_path, reg_no):
    try:
        doc = fitz.open(pdf_path)
        cleaned_input = reg_no.replace(" ", "").replace("/", "").lower()
        for i, page in enumerate(doc):
            text = page.get_text("text")
            cleaned_page = text.replace(" ", "").replace("\n", "").replace("/", "").lower()
            if cleaned_input in cleaned_page:
                out_pdf = f"Result_{reg_no.replace('/', '_')}.pdf"
                result_doc = fitz.open()
                result_doc.insert_pdf(doc, from_page=i, to_page=i)
                result_doc.save(out_pdf)
                return text, out_pdf
        return None, None
    except Exception as e:
        st.error(f"Error extracting result: {e}")
        return None, None

# ------------------- Email Sender -------------------
def send_result_email(to_email, body_text, attachment_path):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "Your ITVET Result Slip"
    msg.attach(MIMEText(body_text, "plain"))
    with open(attachment_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.sendmail(SMTP_USER, to_email, msg.as_string())
        st.success(f"✅ Result sent to {to_email}")
    except Exception as e:
        st.error(f"❌ Failed to send result: {e}")

# ------------------- Admin Login -------------------
def login():
    st.sidebar.subheader("🔐 Admin Login")
    username = st.sidebar.text_input("Email", key="admin_email")
    password = st.sidebar.text_input("Password", type="password", key="admin_password")
    if st.sidebar.button("Login"):
        if username == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            st.session_state["admin"] = True
            st.success("✅ Logged in successfully!")
        else:
            st.error("❌ Invalid credentials")

# ------------------- App Layout -------------------
st.set_page_config(page_title="ITVET Chatbot", page_icon="🤖")
st.markdown("<h1 style='text-align: center;'>🤖 ITVET-CUK Smart Chatbot</h1>", unsafe_allow_html=True)

mode = st.radio("Select User Type", ["User", "Admin"], horizontal=True)

if mode == "Admin":
    if not st.session_state["admin"]:
        login()
        st.stop()
    st.subheader("📥 Unanswered Questions Log")
    if "user_queries" in st.session_state and st.session_state["user_queries"]:
        st.dataframe(pd.DataFrame(st.session_state["user_queries"]))
    else:
        st.info("✅ No unanswered questions yet.")

    st.subheader("📛 Failed Result Lookup Log")
    if "failed_results" in st.session_state and st.session_state["failed_results"]:
        st.dataframe(pd.DataFrame(st.session_state["failed_results"]))
    else:
        st.info("✅ No failed result requests.")

# ------------------- Result Section -------------------
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>1️⃣ Get Your Result Slip</h3>", unsafe_allow_html=True)

reg_no = st.text_input("🎓 Registration Number", key="reg_number_input")
student_email = st.text_input("📧 Your Email", key="results_email_input")

if st.button("📬 Send My Result"):
    download_pdf_from_github()
    if not reg_no:
        st.warning("Please enter your Registration Number.")
    elif not student_email or "@" not in student_email:
        st.warning("Please enter a valid email address.")
    else:
        text, pdf_path = extract_result_page(PDF_FILE, reg_no)
        if text and pdf_path:
            st.text_area("📄 Result Preview", text, height=300)
            send_result_email(student_email, text, pdf_path)
        else:
            if "failed_results" not in st.session_state:
                st.session_state["failed_results"] = []
            st.session_state["failed_results"].append({
                "reg_no": reg_no,
                "email": student_email,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.warning("❌ No results found for that Registration Number.")

# ------------------- Chatbot Section -------------------
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>2️⃣ Ask About ITVET</h3>", unsafe_allow_html=True)

user_question = st.text_input("❓ Your Question", key="general_query")
user_followup_email = st.text_input("📧 Your Email", key="unanswered_email_input")

faq_response_rules = {
    "entry": "📌 Entry Requirements:\n- Diploma: KCSE C- and above\n- Certificate: KCSE D plain and above",
    "certificate": "🎓 Certificate Courses:\n- Cooperative Management\n- Business Management",
    "diploma": "🎓 Diploma Courses:\n- Accounting & Finance, HR, IT, CS, Cyber Security, Tourism, Social Work, Supply Chain, PM, Cooperative Management…",
    "mission": "🎯 Mission: To provide quality education in business and economics through training, research, consultancy and linkages for sustainable economic empowerment.",
    "vision": "👁️ Vision: To be the school of choice in business and economics in Kenya.",
    "objective": "🎯 Objectives:\n• Offer market-oriented programs\n• Promote research\n• Equip students with skills\n• Enhance innovation & partnerships",
    "service": "🛎️ Service Charter Highlights:\n• Missing Marks: 2 weeks\n• Result Slip: 15 minutes post-approval\n• Academic Certificates: 30 working days",
    "missing marks": "🛎️ Kindly use the Results tab to submit a missing marks request.",
    "location": "📍 Campus: Karen, 20km from Nairobi CBD, on a 50-acre serene environment.",
    "events": "📅 Events: TVET Reforms, Career Fairs, CDAAC Exams, Apprenticeship Program.",
    "courses": "🎓 ITVET Offers:\n- Diploma in Computer Science, Applied Statistics, Cyber Security, Information Technology\n- Diploma in Cooperative Management, Agribusiness, Credit Management, Project Management, Supply Chain, Tourism, Catering, Social Work and more.",
    "school": "🏫 ITVET is part of The Co-operative University of Kenya, located in Karen, Nairobi — a serene 50-acre learning environment about 20km from the CBD.",
    "departments": "📚 ITVET has two departments:\n- Department of Computing & Mathematical Sciences\n- Department of Co-operatives, Business & Manageme
