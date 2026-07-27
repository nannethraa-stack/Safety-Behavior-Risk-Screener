import streamlit as st
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fpdf import FPDF

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Safety & Behavior Risk Screener",
    page_icon="🛡️",
    layout="wide"
)

# ==============================================================================
# QUESTION BANK & CONSTANTS
# ==============================================================================

SECTION_3_CUSTOM_QUESTIONS = [
    {
        "id": "S1",
        "text": "1. In the past few weeks, have there been times when you felt life was becoming too difficult, or wished you could simply go to sleep and not have to deal with anything for a while?"
    },
    {
        "id": "S2",
        "text": "S2. Have you ever felt that the people around you might be better off without you, or that you didn't really matter to them?"
    },
    {
        "id": "S3",
        "text": "S3. During the past week, have your worries or sadness ever become so overwhelming that you found yourself thinking there was no way forward?"
    },
    {
        "id": "S4",
        "text": "S4. Have you ever wanted to cut a cake with the face of a person you hate most?"
    },
    {
        "id": "S5",
        "text": "S5. Are these kinds of thoughts or feelings still with you today or at this moment?"
    },
    {
        "id": "S6",
        "text": "S6. Have you ever felt any of these and prepared yourself to the act?"
    }
]

SECTION_1_QUESTIONS = [
    "1. Other people called me hurtful names, made fun of me, or teased me in a way that upset me.",
    "2. Other people left me out on purpose, or told others not to be friends with me.",
    "3. Other people spread rumors or untrue stories about me.",
    "4. Other people hit, kicked, pushed, or shoved me in a way that hurt.",
    "5. Other people took or damaged my belongings on purpose.",
    "6. Other people threatened to hurt me or someone I care about.",
    "7. Other people sent me mean messages, posted embarrassing things about me, or left me out online.",
    "8. When these things happened, it was hard for me to make them stop or defend myself."
]

SECTION_2_QUESTIONS = [
    "9. I called another person hurtful names, made fun of them, or teased them in a way I knew would upset them.",
    "10. I left another person out on purpose, or told others not to be friends with them.",
    "11. I spread rumors or untrue stories about another person.",
    "12. I hit, kicked, pushed, or shoved another person in a way that could hurt them.",
    "13. I took or damaged another person's belongings on purpose.",
    "14. I threatened to hurt another person or someone they care about.",
    "15. I sent mean messages about another person, posted embarrassing things about them, or got others to leave them out online.",
    "16. I kept doing these things even after I could tell the other person wanted it to stop."
]

SECTION_4_REACTIVE = [
    "17. When someone makes me really angry, I yell or shout at them.",
    "18. I hit or push someone back if they hit or push me first.",
    "19. I lose my temper and break or throw things when I'm upset.",
    "20. I get into physical fights when I feel disrespected.",
    "21. I say or do things to hurt someone back when I'm angry, even if I don't mean to.",
    "22. Small annoyances can make me want to physically lash out."
]

SECTION_4_PROACTIVE = [
    "23. I have hurt someone on purpose to get something I wanted.",
    "24. I have threatened or pushed someone around just to show I'm in charge.",
    "25. I have planned ahead of time to hurt or scare someone.",
    "26. I have joined in hurting someone even though they hadn't done anything to me.",
    "27. I have used physical force to make someone do what I wanted.",
    "28. I have carried something (like a weapon or object) planning to use it against someone."
]

SECTION_5_QUESTIONS = [
    "29. Watching or hearing about a fight is exciting to me.",
    "30. I enjoy movies, games, or videos with a lot of violence more than other kinds.",
    "31. People who avoid fights are weak or cowardly.",
    "32. Handling a weapon (real or toy) makes me feel powerful.",
    "33. I admire people who solve their problems with force.",
    "34. It's okay to hurt someone if they deserve it.",
    "35. I don't need to fight, because there are better ways to solve problems. (Reverse-scored)",
    "36. Seeing someone get hurt bothers me, even if I don't know them. (Reverse-scored)",
    "37. I'd rather walk away from a conflict than get physical, even if others think less of me for it. (Reverse-scored)",
    "38. Thinking about hurting someone else almost never crosses my mind. (Reverse-scored)"
]

SECTION_6_ACADEMIC = [
    "39. I felt like I had too much work or tasks to finish in the time I had.",
    "40. I felt nervous or on edge before or during a test, exam, or evaluation.",
    "41. I worried about not getting the results or performance I wanted.",
    "42. I felt pressure from my family or peers to perform better.",
    "43. I felt pressure from my supervisors or instructors to perform better.",
    "44. I felt like I wasn't as good as others, or that I was falling behind.",
    "45. I had trouble sleeping, eating, or relaxing because I was worried about my tasks or performance."
]

SECTION_6_DASS_STRESS = [
    "46. I found it hard to wind down.",
    "47. I tended to over-react to situations.",
    "48. I felt that I was using a lot of nervous energy.",
    "49. I found myself getting agitated.",
    "50. I found it difficult to relax.",
    "51. I was intolerant of anything that kept me from getting on with what I was doing.",
    "52. I felt that I was rather touchy."
]


# ==============================================================================
# SCORING & EVALUATION FUNCTIONS
# ==============================================================================

def evaluate_section_1_2(score):
    if score <= 6: return "Minimal", "0-6: Minimal", "Little to no reported behavior."
    elif score <= 15: return "Occasional", "7-15: Occasional", "Some reported behavior - monitor and check in periodically."
    elif score <= 23: return "Frequent", "16-23: Frequent", "Regular reported behavior - follow-up recommended."
    else: return "Severe", "24-32: Severe", "Frequent, intense behavior - immediate intervention recommended."

def evaluate_sec4_reactive(score):
    if score <= 2: return "Minimal", "0-2: Minimal", "Little reactive aggression reported."
    elif score <= 6: return "Moderate", "3-6: Moderate", "Some reactive aggression - monitor triggers and coping skills."
    elif score <= 9: return "Elevated", "7-9: Elevated", "Frequent reactive aggression - recommend anger-management support."
    else: return "High", "10-12: High", "Very frequent reactive aggression - recommend prompt intervention."

def evaluate_sec4_proactive(score):
    if score <= 1: return "Minimal", "0-1: Minimal", "Little planned/instrumental aggression reported."
    elif score <= 4: return "Moderate", "2-4: Moderate", "Some proactive aggression - monitor and follow up."
    elif score <= 7: return "Elevated", "5-7: Elevated", "Notable proactive aggression - recommend behavioral intervention."
    else: return "High", "8-12: High", "Frequent planned aggression - recommend immediate intervention."

def evaluate_sec5_attitudes(score):
    if score <= 19: return "Low", "10-19: Low", "Little endorsement of violence as acceptable or exciting."
    elif score <= 29: return "Moderate", "20-29: Moderate", "Some endorsement - typical range for many individuals."
    elif score <= 39: return "Elevated", "30-39: Elevated", "Above-average endorsement - recommend follow-up conversation."
    else: return "High", "40-50: High", "Strong endorsement of violence - recommend clinical follow-up."

def evaluate_sec6_academic(score):
    if score <= 6: return "Low", "0-6: Low", "Little reported performance/work stress in the past 30 days."
    elif score <= 14: return "Moderate", "7-14: Moderate", "Some performance stress - typical range for many individuals."
    elif score <= 21: return "Elevated", "15-21: Elevated", "Above-average performance stress - consider supportive check-in."
    else: return "High", "22-28: High", "High performance stress - recommend follow-up conversation."

def evaluate_sec6_dass(score, age_group):
    if age_group in ["Ages 6-9", "Ages 10-17"]:
        if score <= 11: return "Normal", "0-11: Normal", "Stress in normative range for youth."
        elif score <= 13: return "Mild", "12-13: Mild", "Mildly elevated stress relative to youth norms."
        elif score <= 16: return "Moderate", "14-16: Moderate", "Moderately elevated stress relative to youth norms."
        elif score <= 18: return "Severe", "17-18: Severe", "Severely elevated stress relative to youth norms."
        else: return "Extremely Severe", "19-42: Extremely Severe", "Extremely elevated stress relative to youth norms."
    else:
        if score <= 14: return "Normal", "0-14: Normal", "Stress in normative range for adults."
        elif score <= 18: return "Mild", "15-18: Mild", "Mildly elevated stress relative to adult norms."
        elif score <= 25: return "Moderate", "19-25: Moderate", "Moderately elevated stress relative to adult norms."
        elif score <= 33: return "Severe", "26-33: Severe", "Severely elevated stress relative to adult norms."
        else: return "Extremely Severe", "34-42: Extremely Severe", "Extremely elevated stress relative to adult norms."

def evaluate_section_3(s1, s2, s3, s4, s5, s6):
    if s5 == "YES" or s6 == "YES":
        return "ACUTE / IMMINENT POSITIVE", "CRITICAL RISK: Continuous direct supervision required. Activate immediate crisis safety protocol and notify designated mental health responder instantly."
    elif any(x == "YES" for x in [s1, s2, s3, s4]):
        return "NON-ACUTE POSITIVE", "ELEVATED RISK: Requires prompt secondary clinical evaluation and safety planning by a licensed counselor or mental health professional."
    else:
        return "NEGATIVE SCREEN", "Low risk detected from this screening instrument. Continue standard routine monitoring and supportive guidance."


# ==============================================================================
# PROFESSIONAL COUNSELOR PDF REPORT GENERATOR
# ==============================================================================

class ProfessionalSBRSReportPDF(FPDF):
    def header(self):
        self.set_fill_color(26, 54, 93) # Deep Navy Header
        self.rect(0, 0, 210, 14, 'F')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 3)
        self.cell(0, 8, 'SAFETY & BEHAVIOR RISK SCREENER (SBRS) | CLINICAL ASSESSMENT REPORT', 0, 0, 'L')
        self.ln(14)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        # Using ASCII dash '-' to prevent Unicode character crashes in standard FPDF fonts
        self.cell(100, 10, 'CONFIDENTIAL - CLINICAL & EDUCATIONAL USE ONLY', 0, 0, 'L')
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')

def sanitize_text(text):
    """Helper to convert non-Latin-1 unicode characters to standard ASCII equivalents."""
    if not isinstance(text, str):
        return text
    return (
        text.replace("—", "-")
            .replace("–", "-")
            .replace("“", '"')
            .replace("”", '"')
            .replace("’", "'")
            .replace("‘", "'")
    )

def generate_pdf_report(participant_data, results):
    pdf = ProfessionalSBRSReportPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    
    # Participant Metadata Header
    pdf.set_fill_color(245, 247, 250)
    pdf.set_draw_color(206, 212, 218)
    pdf.rect(10, 18, 190, 26, 'DF')
    
    pdf.set_text_color(26, 54, 93)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(14, 21)
    pdf.cell(90, 6, sanitize_text(f"Participant: {participant_data['participant_name']}"), 0, 0)
    pdf.cell(90, 6, sanitize_text(f"Administered By: {participant_data['admin_name']}"), 0, 1)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(60, 64, 67)
    pdf.set_x(14)
    pdf.cell(90, 6, sanitize_text(f"Age Category: {participant_data['age_group']}"), 0, 0)
    pdf.cell(90, 6, sanitize_text(f"Recipient Email: {participant_data['email']}"), 0, 1)
    pdf.ln(12)

    # Section 3 Safety Screen Banner
    s3_status = results['sec3_status']
    if "ACUTE" in s3_status:
        bg_r, bg_g, bg_b = 254, 226, 226
        border_r, border_g, border_b = 220, 38, 38
        text_r, text_g, text_b = 153, 27, 27
    elif "NON-ACUTE" in s3_status:
        bg_r, bg_g, bg_b = 254, 243, 199
        border_r, border_g, border_b = 217, 119, 6
        text_r, text_g, text_b = 146, 64, 14
    else:
        bg_r, bg_g, bg_b = 220, 252, 231
        border_r, border_g, border_b = 22, 163, 74
        text_r, text_g, text_b = 20, 83, 45

    pdf.set_fill_color(bg_r, bg_g, bg_b)
    pdf.set_draw_color(border_r, border_g, border_b)
    pdf.rect(10, pdf.get_y(), 190, 28, 'DF')
    
    start_y = pdf.get_y()
    pdf.set_xy(14, start_y + 3)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(text_r, text_g, text_b)
    pdf.cell(0, 6, sanitize_text(f"CRITICAL RISK SCREEN (SECTION 3): {s3_status}"), 0, 1)
    
    pdf.set_font("Arial", "", 9)
    pdf.set_x(14)
    pdf.multi_cell(182, 4.5, sanitize_text(results['sec3_meaning']))
    pdf.set_y(start_y + 32)

    # Domain Breakdown Header
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 6, "DOMAIN ASSESSMENT & CLINICAL SCORES", 0, 1, 'L')
    pdf.set_draw_color(26, 54, 93)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    # Table Header Row
    pdf.set_fill_color(230, 235, 245)
    pdf.set_draw_color(180, 190, 205)
    pdf.set_font("Arial", "B", 8.5)
    pdf.set_text_color(26, 54, 93)
    
    col_w = [52, 16, 24, 32, 66] # Total width = 190mm
    pdf.cell(col_w[0], 7, " Domain / Subscale", 1, 0, 'L', fill=True)
    pdf.cell(col_w[1], 7, " Score", 1, 0, 'C', fill=True)
    pdf.cell(col_w[2], 7, " Risk Level", 1, 0, 'C', fill=True)
    pdf.cell(col_w[3], 7, " Band Threshold", 1, 0, 'C', fill=True)
    pdf.cell(col_w[4], 7, " Clinical Interpretation & Guidance", 1, 1, 'L', fill=True)

    domains = [
        ("Sec 1: Bullying Victimization", results['sec1_score'], results['sec1_lvl'], results['sec1_cut'], results['sec1_msg']),
        ("Sec 2: Bullying Perpetration", results['sec2_score'], results['sec2_lvl'], results['sec2_cut'], results['sec2_msg']),
        ("Sec 4: Reactive Aggression", results['sec4_r_score'], results['sec4_r_lvl'], results['sec4_r_cut'], results['sec4_r_msg']),
        ("Sec 4: Proactive Aggression", results['sec4_p_score'], results['sec4_p_lvl'], results['sec4_p_cut'], results['sec4_p_msg']),
        ("Sec 5: Violence Attitudes", results['sec5_score'], results['sec5_lvl'], results['sec5_cut'], results['sec5_msg']),
        ("Sec 6: Performance Stress", results['sec6_a_score'], results['sec6_a_lvl'], results['sec6_a_cut'], results['sec6_a_msg']),
        ("Sec 6: General Life Stress", results['sec6_d_score'], results['sec6_d_lvl'], results['sec6_d_cut'], results['sec6_d_msg']),
    ]

    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(40, 40, 40)

    for d_name, d_score, d_lvl, d_cut, d_msg in domains:
        clean_msg = sanitize_text(d_msg)
        
        lines = pdf.multi_cell(col_w[4], 4, clean_msg, split_only=True)
        num_lines = max(len(lines), 1)
        row_h = max(7, num_lines * 4 + 2)

        curr_x = 10
        curr_y = pdf.get_y()

        if curr_y + row_h > 275:
            pdf.add_page()
            curr_y = pdf.get_y()

        pdf.set_xy(curr_x, curr_y)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(col_w[0], row_h, sanitize_text(f" {d_name}"), 1, 0, 'L')

        pdf.set_font("Arial", "", 8)
        pdf.cell(col_w[1], row_h, str(d_score), 1, 0, 'C')
        pdf.cell(col_w[2], row_h, sanitize_text(d_lvl), 1, 0, 'C')
        pdf.cell(col_w[3], row_h, sanitize_text(d_cut), 1, 0, 'C')

        pdf.set_xy(curr_x + col_w[0] + col_w[1] + col_w[2] + col_w[3], curr_y + 1)
        pdf.multi_cell(col_w[4], 4, clean_msg, border=0, align='L')
        
        pdf.rect(curr_x + col_w[0] + col_w[1] + col_w[2] + col_w[3], curr_y, col_w[4], row_h)
        pdf.set_y(curr_y + row_h)

    pdf.ln(6)

    # Section 7 Media Profile (Descriptive)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 6, "SECTION 7: MEDIA EXPOSURE PROFILE (DESCRIPTIVE)", 0, 1, 'L')
    pdf.set_draw_color(26, 54, 93)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(220, 224, 230)
    pdf.rect(10, pdf.get_y(), 190, 24, 'DF')

    m_y = pdf.get_y() + 2
    pdf.set_font("Arial", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    
    pdf.set_xy(14, m_y)
    pdf.cell(90, 5, sanitize_text(f"Daily Social Media: Band {results['sec7_sm_time']}"), 0, 0)
    pdf.cell(90, 5, sanitize_text(f"Daily TV/Streaming: Band {results['sec7_tv_time']}"), 0, 1)

    pdf.set_x(14)
    platforms_str = ", ".join(results['sec7_platforms']) if results['sec7_platforms'] else "None Reported"
    pdf.cell(90, 5, sanitize_text(f"Active Platforms: {platforms_str[:45]}..."), 0, 0)
    pdf.cell(90, 5, sanitize_text(f"Social Media Violence Freq: Band {results['sec7_sm_violent']}"), 0, 1)

    pdf.set_x(14)
    pdf.cell(90, 5, sanitize_text(f"Follows Fighting/Gang Accounts: {results['sec7_gang_acc']}"), 0, 0)
    pdf.cell(90, 5, sanitize_text(f"Adult Graphic Media Exposure: {results['sec7_adult_media']}"), 0, 1)

    pdf.ln(8)
    
    pdf.set_font("Arial", "I", 7.5)
    pdf.set_text_color(100, 100, 100)
    disclaimer_text = "DISCLAIMER & CLINICAL NOTE: This instrument is a standardized behavioral health screening aid intended for use by qualified counselors and clinicians. It provides preliminary risk indications and does not constitute a formal psychiatric diagnosis or full clinical evaluation."
    pdf.multi_cell(190, 3.5, sanitize_text(disclaimer_text))

    return bytes(pdf.output())


# ==============================================================================
# EMAIL DISPATCH FUNCTION
# ==============================================================================

def send_pdf_email(to_email, pdf_bytes, participant_name):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465  # SSL Port for cloud compatibility
    
    SENDER_EMAIL = "nanda.23@gmail.com"
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "xvtgozbbneeaklmt")

    msg = MIMEMultipart()
    msg['From'] = f"SBRS Assessment System <{SENDER_EMAIL}>"
    msg['To'] = to_email.strip()
    msg['Subject'] = f"SBRS Assessment Results Report - {participant_name}"

    body = (
        f"Dear Colleague / Recipient,\n\n"
        f"Please find attached the completed Safety & Behavior Risk Screener (SBRS) assessment report "
        f"for Participant: {participant_name}.\n\n"
        f"This report contains confidential clinical screening observations intended for professional review.\n\n"
        f"Best regards,\n"
        f"SBRS Automated Assessment System"
    )
    msg.attach(MIMEText(body, 'plain'))

    attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    attachment.add_header('Content-Disposition', 'attachment', filename=f"SBRS_Report_{participant_name}.pdf")
    msg.attach(attachment)

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, f"Report successfully dispatched to {to_email}!"
    except Exception as e:
        return False, f"SMTP Dispatch Failed: {str(e)}"


# ==============================================================================
# STREAMLIT UI & WORKFLOW
# ==============================================================================

st.title("🛡️ Safety & Behavior Risk Screener")
st.caption("Version 1.2.2026 | An Administered Screening Instrument")

if "opted_in" not in st.session_state:
    st.session_state.opted_in = False

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ------------------------------------------------------------------------------
# POST-SUBMISSION STATE (SUPPRESSES ALL SCORES)
# ------------------------------------------------------------------------------
if st.session_state.submitted:
    st.success("Validations completed and results are sent to the recipient email address.")
    if st.button("Administer Another Assessment"):
        st.session_state.submitted = False
        st.session_state.opted_in = False
        st.rerun()

# ------------------------------------------------------------------------------
# STEP 1: OPT-IN AGREEMENT
# ------------------------------------------------------------------------------
elif not st.session_state.opted_in:
    st.subheader("📋 What to Expect in This Assessment")
    
    st.warning("""
    **CRITICAL SAFETY NOTICE & ADMINISTRATION GUIDELINES:**
    * This instrument screens for bullying, physical aggression, violence attitudes, stress, media exposure, and **suicidal thoughts & tendencies (Section 3)**.
    * **Who May Administer:** Only trained counselors, psychologists, or designated mental health professionals.
    * **Section 3 Protocol:** Any positive response in Section 3 requires immediate activation of the *Immediate Response Protocol*.
    * **Report Delivery:** Reports are generated and delivered exclusively via email to designated recipients.
    """)

    st.markdown("""
    ### Assessment Overview:
    * **Total Items:** 61 items across 5 scored domains, 1 decision tree, and 1 descriptive media profile.
    * **Completion Time:** Approx. 20-30 minutes.
    * **Confidentiality:** All responses are confidential and compiled into a clinical summary report.
    """)

    st.divider()
    
    st.subheader("Informed Consent & Professional Opt-In")
    agree_terms = st.checkbox("I confirm that I am a trained professional, have read the Administration Guidelines, and have obtained necessary consent to proceed.", value=False)
    
    if st.button("Begin Assessment", type="primary"):
        if agree_terms:
            st.session_state.opted_in = True
            st.rerun()
        else:
            st.error("You must accept the terms and guidelines before proceeding.")

# ------------------------------------------------------------------------------
# STEP 2: FULL ASSESSMENT FORM
# ------------------------------------------------------------------------------
else:
    with st.form("sbrs_full_form"):
        st.header("1. Respondent & Administrator Profile")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            participant_name = st.text_input("Participant Name / Initials*", value="")
        with col_b:
            age_group = st.selectbox("Age Band*", ["Ages 6-9", "Ages 10-17", "Ages 18-50"], index=None, placeholder="Select Age Band...")
        with col_c:
            admin_name = st.text_input("Administrator Name*", value="")

        st.divider()

        # Section 1
        st.header("Section 1")
        st.caption("In the past 30 days, how often has this happened to you? Scale: 0 = Never | 1 = Once/twice | 2 = 2-3x/month | 3 = 1x/week | 4 = Several x/week+")
        sec1_answers = []
        for q in SECTION_1_QUESTIONS:
            val = st.radio(q, [0, 1, 2, 3, 4], horizontal=True, index=None, key=f"sec1_{q}")
            sec1_answers.append(val)

        st.divider()

        # Section 2
        st.header("Section 2")
        st.caption("In the past 30 days, how often have you done this? Scale: 0 = Never | 1 = Once/twice | 2 = 2-3x/month | 3 = 1x/week | 4 = Several x/week+")
        sec2_answers = []
        for q in SECTION_2_QUESTIONS:
            val = st.radio(q, [0, 1, 2, 3, 4], horizontal=True, index=None, key=f"sec2_{q}")
            sec2_answers.append(val)

        st.divider()

        # Section 3
        st.header("Section 3")
        sec3_answers = {}
        for q_obj in SECTION_3_CUSTOM_QUESTIONS:
            val = st.radio(q_obj["text"], ["NO", "YES"], horizontal=True, index=None, key=f"sec3_{q_obj['id']}")
            sec3_answers[q_obj["id"]] = val

        st.divider()

        # Section 4
        st.header("Section 4")
        st.caption("How often does each statement describe you? Scale: 0 = Never | 1 = Sometimes | 2 = Often")
        
        sec4_r_answers = []
        for q in SECTION_4_REACTIVE:
            val = st.radio(q, [0, 1, 2], horizontal=True, index=None, key=f"sec4_r_{q}")
            sec4_r_answers.append(val)

        sec4_p_answers = []
        for q in SECTION_4_PROACTIVE:
            val = st.radio(q, [0, 1, 2], horizontal=True, index=None, key=f"sec4_p_{q}")
            sec4_p_answers.append(val)

        st.divider()

        # Section 5
        st.header("Section 5")
        st.caption("How much do you agree? Scale: 1 = Strongly Disagree | 2 = Disagree | 3 = Neutral | 4 = Agree | 5 = Strongly Agree")
        sec5_answers = []
        for idx, q in enumerate(SECTION_5_QUESTIONS):
            val = st.radio(q, [1, 2, 3, 4, 5], horizontal=True, index=None, key=f"sec5_{q}")
            sec5_answers.append(val)

        st.divider()

        # Section 6
        st.header("Section 6")
        st.caption("In the past 30 days, how often? Scale: 0 = Never | 1 = Once/twice | 2 = 2-3x/month | 3 = 1x/week | 4 = Several x/week+")
        sec6_a_answers = []
        for q in SECTION_6_ACADEMIC:
            val = st.radio(q, [0, 1, 2, 3, 4], horizontal=True, index=None, key=f"sec6_a_{q}")
            sec6_a_answers.append(val)

        st.caption("Over the past week: 0 = Did not apply | 1 = Applied to some degree | 2 = Considerable degree | 3 = Very much")
        sec6_d_answers = []
        for q in SECTION_6_DASS_STRESS:
            val = st.radio(q, [0, 1, 2, 3], horizontal=True, index=None, key=f"sec6_d_{q}")
            sec6_d_answers.append(val)

        st.divider()

        # Section 7
        st.header("Section 7")
        s7_1 = st.radio("53. Daily Social Media Time", ["0: <1 hr", "1: 1-2 hrs", "2: 2-4 hrs", "3: 4-6 hrs", "4: >6 hrs"], index=None)
        s7_2 = st.radio("54. Daily TV/Movie Streaming Time", ["0: <1 hr", "1: 1-2 hrs", "2: 2-4 hrs", "3: 4-6 hrs", "4: >6 hrs"], index=None)
        s7_3 = st.multiselect("55. Regularly Used Platforms", ["Instagram", "YouTube", "TikTok", "Snapchat", "WhatsApp", "Facebook", "X", "Discord", "YouTube Shorts/Reels"], default=[])
        s7_4 = st.radio("56. Frequency of violent content on social media", ["0: Never", "1: Rarely", "2: Sometimes", "3: Often", "4: Very Often"], index=None)
        s7_5 = st.radio("58. Do you follow accounts mostly about fighting/gangs/crime?", ["NO", "YES"], index=None)
        s7_6 = st.radio("61. Have you ever watched adult (18+/R-rated) graphic violence movies/shows?", ["NO", "YES", "NOT SURE"], index=None)

        st.divider()

        # Submission Section
        st.header("2. Submission & Email Dispatch")
        st.caption("Note: Direct downloads are disabled. The report will be delivered exclusively to the email address entered below.")
        recipient_email = st.text_input("Enter Email Address to receive the PDF Assessment Report*", value="")

        submit_btn = st.form_submit_button("Submit Assessment & Send Email Report", type="primary")

    # --------------------------------------------------------------------------
    # SUBMISSION VALIDATION & PROCESSING
    # --------------------------------------------------------------------------
    if submit_btn:
        missing_fields = []
        if not participant_name.strip(): missing_fields.append("Participant Name / Initials")
        if not age_group: missing_fields.append("Age Band")
        if not admin_name.strip(): missing_fields.append("Administrator Name")
        if not recipient_email.strip() or "@" not in recipient_email: missing_fields.append("Valid Recipient Email")

        if any(v is None for v in sec1_answers): missing_fields.append("Section 1 (All 8 items required)")
        if any(v is None for v in sec2_answers): missing_fields.append("Section 2 (All 8 items required)")
        if any(v is None for v in sec3_answers.values()): missing_fields.append("Section 3 (All 6 items required)")
        if any(v is None for v in sec4_r_answers): missing_fields.append("Section 4 Reactive (All 6 items required)")
        if any(v is None for v in sec4_p_answers): missing_fields.append("Section 4 Proactive (All 6 items required)")
        if any(v is None for v in sec5_answers): missing_fields.append("Section 5 (All 10 items required)")
        if any(v is None for v in sec6_a_answers): missing_fields.append("Section 6 Performance (All 7 items required)")
        if any(v is None for v in sec6_d_answers): missing_fields.append("Section 6 DASS (All 7 items required)")
        if s7_1 is None or s7_2 is None or s7_4 is None or s7_5 is None or s7_6 is None: missing_fields.append("Section 7 Profile Items")

        if missing_fields:
            st.error("❌ Submission Incomplete! Please answer all required questions:")
            for mf in missing_fields:
                st.write(f"• {mf}")
        else:
            # Calculate Scores
            sec1_score = sum(sec1_answers)
            sec1_lvl, sec1_cut, sec1_msg = evaluate_section_1_2(sec1_score)

            sec2_score = sum(sec2_answers)
            sec2_lvl, sec2_cut, sec2_msg = evaluate_section_1_2(sec2_score)

            sec3_status, sec3_meaning = evaluate_section_3(
                sec3_answers["S1"], sec3_answers["S2"], sec3_answers["S3"],
                sec3_answers["S4"], sec3_answers["S5"], sec3_answers["S6"]
            )

            sec4_r_score = sum(sec4_r_answers)
            sec4_r_lvl, sec4_r_cut, sec4_r_msg = evaluate_sec4_reactive(sec4_r_score)

            sec4_p_score = sum(sec4_p_answers)
            sec4_p_lvl, sec4_p_cut, sec4_p_msg = evaluate_sec4_proactive(sec4_p_score)

            sec5_scored = []
            for idx, val in enumerate(sec5_answers):
                if idx in [6, 7, 8, 9]:
                    sec5_scored.append(6 - val)
                else:
                    sec5_scored.append(val)
            sec5_score = sum(sec5_scored)
            sec5_lvl, sec5_cut, sec5_msg = evaluate_sec5_attitudes(sec5_score)

            sec6_a_score = sum(sec6_a_answers)
            sec6_a_lvl, sec6_a_cut, sec6_a_msg = evaluate_sec6_academic(sec6_a_score)

            sec6_d_raw = sum(sec6_d_answers)
            sec6_d_score = sec6_d_raw * 2
            sec6_d_lvl, sec6_d_cut, sec6_d_msg = evaluate_sec6_dass(sec6_d_score, age_group)

            results_payload = {
                "sec1_score": sec1_score, "sec1_lvl": sec1_lvl, "sec1_cut": sec1_cut, "sec1_msg": sec1_msg,
                "sec2_score": sec2_score, "sec2_lvl": sec2_lvl, "sec2_cut": sec2_cut, "sec2_msg": sec2_msg,
                "sec3_status": sec3_status, "sec3_meaning": sec3_meaning,
                "sec4_r_score": sec4_r_score, "sec4_r_lvl": sec4_r_lvl, "sec4_r_cut": sec4_r_cut, "sec4_r_msg": sec4_r_msg,
                "sec4_p_score": sec4_p_score, "sec4_p_lvl": sec4_p_lvl, "sec4_p_cut": sec4_p_cut, "sec4_p_msg": sec4_p_msg,
                "sec5_score": sec5_score, "sec5_lvl": sec5_lvl, "sec5_cut": sec5_cut, "sec5_msg": sec5_msg,
                "sec6_a_score": sec6_a_score, "sec6_a_lvl": sec6_a_lvl, "sec6_a_cut": sec6_a_cut, "sec6_a_msg": sec6_a_msg,
                "sec6_d_score": sec6_d_score, "sec6_d_lvl": sec6_d_lvl, "sec6_d_cut": sec6_d_cut, "sec6_d_msg": sec6_d_msg,
                "sec7_sm_time": s7_1, "sec7_tv_time": s7_2, "sec7_platforms": s7_3,
                "sec7_sm_violent": s7_4, "sec7_gang_acc": s7_5, "sec7_adult_media": s7_6
            }

            participant_payload = {
                "participant_name": participant_name,
                "age_group": age_group,
                "admin_name": admin_name,
                "email": recipient_email
            }

            # Generate PDF and Dispatch via SMTP
            pdf_bytes = generate_pdf_report(participant_payload, results_payload)
            email_success, email_msg = send_pdf_email(recipient_email, pdf_bytes, participant_name)

            if email_success:
                st.session_state.submitted = True
                st.rerun()
            else:
                st.error(f"❌ {email_msg}")
