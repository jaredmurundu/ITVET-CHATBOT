import streamlit as st
import fitz  # PyMuPDF
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

st.set_page_config(page_title="ITVET Results Bot", page_icon="📧")

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
    sender_email = "your_email@example.com"
    sender_password = "your_app_password"
    subject = "Your ITVET Results Slip"

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

st.title("📄 ITVET Student Results Chatbot")

with st.expander("📥 Upload the results PDF"):
    uploaded_file = st.file_uploader("Upload results PDF", type=["pdf"])
    if uploaded_file:
        with open("results.pdf", "wb") as f:
            f.write(uploaded_file.read())
        st.success("PDF uploaded successfully.")

st.markdown("---")

reg_no = st.text_input("🎓 Enter your Registration Number (e.g. DCSC01/4296/2022)")
student_email = st.text_input("📧 Enter your Email Address")

if st.button("Get My Result Slip"):
    if not reg_no:
        st.warning("Please enter your Registration Number.")
    elif not student_email:
        st.warning("Please enter your Email Address.")
    elif not os.path.exists("results.pdf"):
        st.error("Please upload the results PDF first.")
    else:
        result_text, result_pdf = extract_result_page("results.pdf", reg_no)
        if result_text and result_pdf:
            st.text_area("📄 Result Found", result_text, height=300)
            sent = send_result_email_with_attachment(student_email, result_text, result_pdf)
            if sent:
                st.success(f"✅ Result slip sent to {student_email}")
            else:
                st.error("❌ Failed to send email. Check credentials or internet.")
        else:
            st.warning("No results found for that Registration Number.")
