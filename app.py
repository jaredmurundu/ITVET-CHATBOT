import streamlit as st
import fitz  # PyMuPDF
import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

# ------------------- Admin Setup -------------------
ADMIN_EMAIL = "jmurundu@cuk.ac.ke"
ADMIN_PASSWORD = "34262059"
RAW_GITHUB_PDF = "https://raw.githubusercontent.com/jaredmurundu/ITVET-CHATBOT/main/sample_results.pdf"
PDF_FILE = "sample_results.pdf"
SMTP_USER = ADMIN_EMAIL
SMTP_PASSWORD = "ylnf zlwk dvnr bqns"

# ------------------- Session Data -------------------
if "admin" not in st.session_state:
    st.session_state["admin"] = False

# ------------------- PDF Downloader -------------------
def download_pdf_from_github():
    try:
        if not os.path.exists(PDF_FILE):
            response = requests.get(RAW_GITHUB_PDF)
            with open(PDF_FILE, "wb") as f:
                f.write(response.content)
            print("✅ Downloaded latest results from GitHub.")
    except Exception as e:
        st.error(f"❌ Could not fetch results PDF: {e}")

# ------------------- PDF Extractor -------------------
def extract_result_page(pdf_path, reg_no):
    try:
        doc = fitz.open(pdf_path)
        cleaned_reg = reg_no.replace("/", "").replace(" ", "").strip().lower()
        for i, page in enumerate(doc):
            text = page.get_text("text")
            check_text = text.replace(" ", "").replace("\n", "").lower()
            if cleaned_reg in check_text:
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
    username = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            st.session_state["admin"] = True
            st.success("✅ Logged in successfully!")
        else:
            st.error("❌ Invalid credentials")

# ------------------- App UI -------------------
st.set_page_config(page_title="ITVET Chatbot", page_icon="🤖")
st.markdown("<h1 style='text-align: center;'>🤖 ITVET-CUK Smart Chatbot</h1>", unsafe_allow_html=True)

mode = st.radio("Select User Type", ["User", "Admin"], horizontal=True)

if mode == "Admin":
    if not st.session_state["admin"]:
        login()
        st.stop()

# ------------------- Result Slip Section -------------------
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>1️⃣ Get Your Result Slip</h3>", unsafe_allow_html=True)

reg_no = st.text_input("🎓 Registration Number")
student_email = st.text_input("📧 Your Email")

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
            st.warning("❌ No results found for that Registration Number.")

# ------------------- Chatbot Section -------------------
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>2️⃣ Ask About ITVET</h3>", unsafe_allow_html=True)

user_question = st.text_input("❓ Your Question")
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
    "departments": "📚 ITVET has two departments:\n- Department of Computing & Mathematical Sciences\n- Department of Co-operatives, Business & Management Studies",
    "admission": "📝 Admission:\n- Certificate: KCSE D plain\n- Diploma: KCSE C-\n- Fee: Ksh 500\n- Issued within 8 weeks after advert",
    "results": "📄 Result slips: Issued free 15 minutes post-approval\nTranscripts and certificates: Within 30 working days",
    "service charter": "📋 Charter:\n- Inquiries: Verbal (1 day), Email (2 days)\n- Missing Marks: 2 weeks\n- Certificates: 30 days\n- Disciplinary: 30 days\n- Clearance: 2 days"
}

if st.button("🔍 Get Answer"):
    reply = None
    for key, text in faq_response_rules.items():
        if key in user_question.lower():
            reply = text
            break
    if reply:
        st.text_area("🤖 Answer", reply, height=200)
    else:
        st.warning("🤔 We could not find an answer. Please enter your email for admin follow-up.")
        email = st.text_input("📧 Your Email")
        if email and "@" in email:
            if "user_queries" not in st.session_state:
                st.session_state["user_queries"] = []
            st.session_state["user_queries"].append({
                "email": email,
                "question": user_question,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success("✅ Your query has been submitted. You will receive a response soon.")
        elif email:
            st.warning("⚠️ Please enter a valid email address.")

# ------------------- Footer -------------------
st.markdown("""
<div style='text-align: center;'>
👨‍💻 Developed for <strong>ITVET-CUK</strong> by <strong><a href='https://www.linkedin.com/in/jared-murundu-07738b23a/' target='_blank'>Jared Murundu</a></strong><br>
📊 Data Scientist | 💻 Software Developer
</div>
""", unsafe_allow_html=True)
