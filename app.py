import streamlit as st
import fitz  # PyMuPDF
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

st.set_page_config(page_title="ITVET Result Bot", page_icon="📄")

PDF_FILE = "sample_results.pdf"

def extract_result_page(pdf_path, reg_no):
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if reg_no.lower() in text.lower():
                output_pdf_path = f"Result_{reg_no.replace('/', '_')}.pdf"
                result_doc = fitz.open()
                result_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                result_doc.save(output_pdf_path)
                return text, output_pdf_path
        return None, None
    except Exception as e:
        return None, None

def send_result_email_with_attachment(to_email, body_text, attachment_path):
    sender_email = "jmurundu@cuk.ac.ke"
    sender_password = "ylnf zlwk dvnr bqns"
    subject = "Your ITVET Result Slip"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body_text, "plain"))

    with open(attachment_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        message.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        return True
    except Exception as e:
        return False

st.title("📄 ITVET Results Slip Request")

reg_no = st.text_input("🎓 Enter your Registration Number (e.g. DCSC01/4296/2022)")
student_email = st.text_input("📧 Enter your Email Address")

if st.button("📬 Send My Result"):
    if not os.path.exists(PDF_FILE):
        st.error("Result file not found.")
    elif not reg_no:
        st.warning("Please enter your Registration Number.")
    elif not student_email:
        st.warning("Please enter your Email Address.")
    else:
        result_text, result_pdf = extract_result_page(PDF_FILE, reg_no)
        if result_text and result_pdf:
            st.text_area("📄 Result Preview", result_text, height=300)
            sent = send_result_email_with_attachment(student_email, result_text, result_pdf)
            if sent:
                st.success(f"✅ Result sent to {student_email}")
            else:
                st.error("❌ Email failed. Check credentials or network.")
        else:
            st.warning("❌ No result found for that Registration Number.")
# 📘 General Questions Section with Admin Follow-Up
st.markdown("### 💬 Ask About ITVET")
user_question = st.text_input("❓ Type your question here (e.g., 'What are the diploma courses?')")

faq_response_rules = {
    "entry": "📌 *Entry Requirements:*\n- Diploma: KCSE C- (minus) and above\n- Certificate: KCSE D plain and above",
    "certificate": "🎓 *Certificate Courses Offered:*\n- Cooperative Management\n- Business Management",
    "diploma": "🎓 *Diploma Courses Offered:*\n- Accounting & Finance, HR, IT, Cyber Security, Computer Science, Tourism, Social Work, Supply Chain, Project Management, Cooperative Management and more.",
    "mission": "🎯 *Our Mission:*\nTo provide quality education in business and economics that nurtures creativity and innovation through training, research, consultancy and linkages for sustainable economic empowerment.",
    "vision": "👁️ *Our Vision:*\nTo be the school of choice in business and economics in Kenya.",
    "objective": "🎯 *Our Objectives:*\n- Develop market-oriented academic programmes\n- Promote research and knowledge sharing\n- Equip students with startup/management skills\n- Enhance innovation and partnerships",
    "service": "🛎️ *Service Delivery Timeline Highlights:*\n- Missing Marks: 2 weeks\n- Academic Certificates: Within 30 working days\n- Result Slip: 15 minutes post-approval\n- Admission: 8 weeks after advert closure",
    "location": "📍 *Institute Location:*\nThe campus is located in Karen, about 20km from Nairobi CBD, on a serene 50-acre parcel.",
    "events": "📅 *Upcoming Events:*\n- TVET Curriculum Reforms\n- RPL Implementation\n- TVET Fairs (Mar–Apr 2025)\n- CDAAC Exam Series\n- Apprenticeship Program\n- Digitization & Private Sector Partnerships"
}

def notify_admin_unanswered_question(question, user_email):
    sender_email = "jmurundu@cuk.ac.ke"
    sender_password = "ylnf zlwk dvnr bqns"
    admin_email = "jmurundu@cuk.ac.ke"
    subject = f"❓ Unanswered Question from Chatbot - [{user_email}]"
    body = f"A user asked a question that the chatbot could not answer:\n\nQuestion: {question}\nUser Email: {user_email}\n\nYou can reply directly to the user."

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = admin_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.sendmail(sender_email, admin_email, msg.as_string())
    except Exception as e:
        st.error("⚠️ Failed to notify the admin.")

if st.button("🔍 Get Answer"):
    match_found = False
    for keyword, reply in faq_response_rules.items():
        if keyword in user_question.lower():
            st.text_area("🤖 ITVET Answer", reply, height=200)
            match_found = True
            break

    if not match_found:
        user_email = st.text_input("📧 Enter your email to receive a reply from the admin")
        if st.button("📨 Submit to Admin"):
            if user_email:
                notify_admin_unanswered_question(user_question, user_email)
                st.success("✅ Your question has been sent. You'll get a reply from the admin via email.")
            else:
                st.warning("⚠️ Please enter your email to complete the request.")

# Developer credit (centered)
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; margin-top: 50px; font-size: 15px;'>
        👨‍💻 Developed for ITVET-CUK by <strong>Jared Murundu</strong><br>
        📊 Data Scientist | 💻 Software Developer
    </div>
    """,
    unsafe_allow_html=True
)

