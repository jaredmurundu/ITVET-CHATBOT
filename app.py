import streamlit as st
import fitz  # PyMuPDF
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import pandas as pd

# ------------------- In-Memory Admin Setup -------------------
ADMIN_EMAIL = "jmurundu@cuk.ac.ke"
ADMIN_PASSWORD = "34262059"
PDF_FILE = os.path.join(os.getcwd(), "sample_results.pdf")
SMTP_USER = ADMIN_EMAIL
SMTP_PASSWORD = "ylnf zlwk dvnr bqns"

# ------------------- Session Data -------------------
if "admin" not in st.session_state:
    st.session_state["admin"] = False
if "unanswered_queries" not in st.session_state:
    st.session_state["unanswered_queries"] = [
        {"email": "student1@example.com", "question": "What is the deadline for fee payment?", "timestamp": "2024-05-01 10:23:45"},
        {"email": "student2@example.com", "question": "How do I register for resits?", "timestamp": "2024-05-02 11:15:30"},
        {"email": "student3@example.com", "question": "Is there weekend learning?", "timestamp": "2024-05-03 14:05:10"}
    ]

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

# ------------------- Function: Extract PDF Page -------------------
def extract_result_page(pdf_path, reg_no):
    try:
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            text = doc[i].get_text("text")
            cleaned_text = text.replace(" ", "").replace("\n", "").lower()
            cleaned_reg = reg_no.replace("/", "").replace(" ", "").lower()
            if cleaned_reg in cleaned_text:
                out_pdf = f"Result_{reg_no.replace('/', '_')}.pdf"
                result_doc = fitz.open()
                result_doc.insert_pdf(doc, from_page=i, to_page=i)
                result_doc.save(out_pdf)
                return text, out_pdf
        return None, None
    except Exception as e:
        st.error(f"Error extracting result: {e}")
        return None, None

# ------------------- Function: Send Email -------------------
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

# ------------------- Main App -------------------
st.set_page_config(page_title="ITVET Chatbot", page_icon="🤖")
st.title("🤖 ITVET-CUK Smart Chatbot")

mode = st.radio("Select User Type", ["User", "Admin"], horizontal=True)

if mode == "Admin":
    if not st.session_state["admin"]:
        login()
        st.stop()
    else:
        st.title("🛡️ ITVET Admin Dashboard")

        st.markdown("### 📬 Unanswered Queries")
        if st.session_state["unanswered_queries"]:
            df = pd.DataFrame(st.session_state["unanswered_queries"])
            st.dataframe(df)
        else:
            st.success("✅ No unanswered questions at the moment.")

        st.markdown("---")
        st.markdown("### 📊 BI Dashboard: Query Insights")
        total_queries = len(st.session_state["unanswered_queries"])
        sent_requests = st.session_state.get("sent_results", [])
        total_sent = len(sent_requests)

        col1, col2 = st.columns(2)
        col1.metric("Total Unanswered Queries", total_queries)
        col2.metric("Total Sent Result Requests", total_sent)

        if total_queries > 0:
            query_df = pd.DataFrame(st.session_state["unanswered_queries"])
            st.bar_chart(query_df["timestamp"].str[:10].value_counts().sort_index())

        st.markdown("---")
        st.markdown("### 📄 Log of Sent Result Requests")
        if "sent_results" not in st.session_state:
            st.session_state["sent_results"] = []  # Placeholder for future logging logic
        if st.session_state["sent_results"]:
            result_df = pd.DataFrame(st.session_state["sent_results"])
            st.dataframe(result_df)
        else:
            st.info("📭 No result emails sent yet.")

        st.stop()
    else:
                st.title("🛡️ ITVET Admin Dashboard")

        st.markdown("### 📬 Unanswered Queries")
        if st.session_state["unanswered_queries"]:
            df = pd.DataFrame(st.session_state["unanswered_queries"])
            st.dataframe(df)
        else:
            st.success("✅ No unanswered questions at the moment.")

        st.markdown("---")
        st.markdown("### 📊 BI Dashboard: Query Insights")
        total_queries = len(st.session_state["unanswered_queries"])
        sent_requests = st.session_state.get("sent_results", [])
        total_sent = len(sent_requests)

        col1, col2 = st.columns(2)
        col1.metric("Total Unanswered Queries", total_queries)
        col2.metric("Total Sent Result Requests", total_sent)

        if total_queries > 0:
            query_df = pd.DataFrame(st.session_state["unanswered_queries"])
            st.bar_chart(query_df["timestamp"].str[:10].value_counts().sort_index())

        st.markdown("---")
        st.markdown("### 📄 Log of Sent Result Requests")
        if "sent_results" not in st.session_state:
            st.session_state["sent_results"] = []  # Placeholder for future logging logic
        if st.session_state["sent_results"]:
            result_df = pd.DataFrame(st.session_state["sent_results"])
            st.dataframe(result_df)
        else:
            st.info("📭 No result emails sent yet.")

        st.stop()

# ------------------- Public Result Slip Section -------------------
st.markdown("---")
st.subheader("1️⃣ Get Your Result Slip")
reg_no = st.text_input("🎓 Registration Number")
student_email = st.text_input("📧 Your Email")

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
            if "sent_results" not in st.session_state:
                st.session_state["sent_results"] = []
            st.session_state["sent_results"].append({
                "registration_number": reg_no,
                "email": student_email,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            st.warning("❌ No results found for that Registration Number.")

# ------------------- Public FAQ Section -------------------
st.markdown("---")
st.subheader("2️⃣ Ask About ITVET")
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
            st.session_state["unanswered_queries"].append({
                "email": email,
                "question": user_question,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success("✅ Your query has been submitted. You will receive a response soon.")
        elif email:
            st.warning("⚠️ Please enter a valid email address.")
