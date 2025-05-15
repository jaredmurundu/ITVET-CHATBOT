import streamlit as st
import fitz  # PyMuPDF
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# —————— App Configuration ——————
st.markdown(
    "<h1 style='text-align: center;'>🤖 THE ITVET-CUK </h1>",
    unsafe_allow_html=True
)

PDF_FILE = "sample_results.pdf"
ADMIN_EMAIL = "jmurundu@cuk.ac.ke"
SMTP_USER = "jmurundu@cuk.ac.ke"       # your bot’s SMTP-enabled account
SMTP_PASSWORD = "ylnf zlwk dvnr bqns"   # your Gmail app password

# —————— Helper Functions ——————

def extract_result_page(pdf_path, reg_no):
    try:
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            text = doc[i].get_text()
            if reg_no.lower() in text.lower():
                out_pdf = f"Result_{reg_no.replace('/', '_')}.pdf"
                result_doc = fitz.open()
                result_doc.insert_pdf(doc, from_page=i, to_page=i)
                result_doc.save(out_pdf)
                return text, out_pdf
        return None, None
    except:
        return None, None

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

def send_unanswered_question_to_admin(question, user_email):
    subject = f"❓ Unanswered Chatbot Question from [{user_email}]"
    body = (
        f"A student asked a question the bot could not answer:\n\n"
        f"Question: {question}\n"
        f"Student Email: {user_email}\n\n"
        f"Please reply directly to the student."
    )
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ADMIN_EMAIL
    msg["Subject"] = subject
    msg["Reply-To"] = user_email
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.sendmail(SMTP_USER, ADMIN_EMAIL, msg.as_string())
        st.success("✅ Your question has been sent to the admin. You will receive a reply via email.")
    except Exception as e:
        st.error(f"❌ Failed to notify admin: {e}")

# —————— UI ——————

st.markdown("#### 1. Get Your Result Slip")
col1, col2 = st.columns(2)
with col1:
    reg_no = st.text_input("🎓 Registration Number", key="reg")
with col2:
    student_email = st.text_input("📧 Your Email", key="email")
if st.button("📬 Send My Result"):
    if not os.path.exists(PDF_FILE):
        st.error("Result file not found on server.")
    elif not reg_no:
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

st.markdown("---")
st.markdown("#### 2. Ask About ITVET (general inquiries)")
user_question = st.text_input("❓ Welcome to the ITVET-CUK: How may i help you?", key="faq")

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
        st.warning("🤔 Will it be okay if we responded to this later?. Please enter your email so that the admin can reply:")
        ua = st.text_input("📧 Please enter your Email address for Admin Reply", key="faq_email")
        if ua and "@" in ua:
            send_unanswered_question_to_admin(user_question, ua)
        elif ua:
            st.warning("⚠️ Please enter a valid email address.")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; margin-top: 30px; font-size: 14px;'>
      👨‍💻 Developed for ITVET-CUK by <strong>Jared Murundu</strong><br>
      📊 Data Scientist | 💻 Software Developer
    </div>
    """,
    unsafe_allow_html=True
)
