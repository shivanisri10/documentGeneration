import streamlit as st
import sys
import os
import tempfile

# ── Path fix so we can import backend modules ──────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from schema import DOCUMENT_SCHEMAS
from app import generate_document

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Document Generator · Turn2Law",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import font ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #1a1a2e;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 780px;
}

/* ── Top wordmark bar ── */
.wordmark {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.25rem;
}
.wordmark-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #0a4f6e;
}
.wordmark-text {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #0a4f6e;
}

/* ── Page title ── */
.page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    font-weight: 400;
    color: #0d0d1a;
    line-height: 1.15;
    margin-bottom: 0.4rem;
}
.page-subtitle {
    font-size: 0.97rem;
    color: #6b7280;
    font-weight: 400;
    margin-bottom: 0;
}

/* ── Divider ── */
.section-divider {
    border: none;
    border-top: 1px solid #e8eaed;
    margin: 1.8rem 0 1.5rem 0;
}

/* ── Section label ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 0.9rem;
}

/* ── Field label override ── */
label {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
}

/* ── Required star ── */
.req { color: #c0392b; margin-left: 2px; }
.opt-tag {
    font-size: 0.7rem;
    font-weight: 400;
    color: #9ca3af;
    margin-left: 6px;
    font-style: italic;
}

/* ── Input fields ── */
input[type="text"],
input[type="date"],
textarea,
.stSelectbox > div > div {
    border-radius: 6px !important;
    border: 1px solid #d1d5db !important;
    font-size: 0.93rem !important;
    background: #ffffff !important;
    transition: border-color 0.15s;
}
input[type="text"]:focus,
textarea:focus {
    border-color: #0a4f6e !important;
    box-shadow: 0 0 0 3px rgba(10,79,110,0.08) !important;
}

/* ── Generate button ── */
.stButton > button {
    width: 100%;
    background: #0a4f6e !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.65rem 1.5rem !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    font-family: 'DM Sans', sans-serif !important;
    cursor: pointer;
    transition: background 0.15s !important;
    margin-top: 0.5rem;
}
.stButton > button:hover {
    background: #083d56 !important;
}

/* ── Success box ── */
.success-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin-top: 1.5rem;
}
.success-box .success-title {
    font-weight: 600;
    color: #166534;
    font-size: 1rem;
    margin-bottom: 0.3rem;
}
.success-box .success-sub {
    font-size: 0.88rem;
    color: #4b7a5c;
}

/* ── Error box ── */
.error-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 1rem 1.4rem;
    margin-top: 1rem;
    font-size: 0.88rem;
    color: #991b1b;
}

/* ── Upload zone ── */
.uploadedFile {
    border-radius: 6px !important;
}
section[data-testid="stFileUploadDropzone"] {
    border: 1.5px dashed #d1d5db !important;
    border-radius: 8px !important;
    background: #fafafa !important;
}

/* ── Detected type pill ── */
.doc-pill {
    display: inline-block;
    background: #eff6ff;
    color: #1d4ed8;
    font-size: 0.8rem;
    font-weight: 600;
    border-radius: 20px;
    padding: 3px 12px;
    border: 1px solid #bfdbfe;
    margin-left: 8px;
}

/* ── Download button ── */
.stDownloadButton > button {
    width: 100%;
    background: white !important;
    color: #0a4f6e !important;
    border: 1.5px solid #0a4f6e !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.5rem !important;
    font-size: 0.93rem !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    margin-top: 0.6rem;
}
.stDownloadButton > button:hover {
    background: #f0f7fb !important;
}
</style>
""", unsafe_allow_html=True)


# ── Field metadata ─────────────────────────────────────────────────────────
# Tells the UI how to render each field: type, placeholder, hint
FIELD_META = {
    # Onboarding_Letter
    "Employee_Name":        {"type": "text",     "placeholder": "e.g. Rahul Verma"},
    "Emp_ID":               {"type": "text",     "placeholder": "e.g. T2L-AI-041"},
    "Role":                 {"type": "text",     "placeholder": "e.g. Software Engineer Intern"},
    "Joining_Date":         {"type": "text",     "placeholder": "e.g. 1 July 2026"},
    "Document_Date":        {"type": "text",     "placeholder": "e.g. 10 June 2026"},
    # Acknowledgement_of_Debt
    "Debtor_Name":          {"type": "text",     "placeholder": "e.g. Arjun Mehta"},
    "Creditor_Name":        {"type": "text",     "placeholder": "e.g. Priya Sharma"},
    "Debt_Amount":          {"type": "text",     "placeholder": "e.g. Rs. 1,50,000"},
    "Acknowledgement_Date": {"type": "text",     "placeholder": "e.g. 19 April 2026"},
    "Day":                  {"type": "text",     "placeholder": "e.g. 19th"},
    "Month_Year":           {"type": "text",     "placeholder": "e.g. April 2026"},
    "Accrued_Interest_Note":{"type": "text",     "placeholder": "Optional note on interest"},
    # Gift_Deed
    "Donor_Name":           {"type": "text",     "placeholder": "e.g. Ramesh Kumar"},
    "Donee_Name":           {"type": "text",     "placeholder": "e.g. Suresh Kumar"},
    "Donor_Address":        {"type": "area",     "placeholder": "e.g. 42, MG Road, Bengaluru - 560001"},
    "Donee_Address":        {"type": "area",     "placeholder": "e.g. 18, Anna Nagar, Chennai - 600040"},
    "Gift_Amount_Figures":  {"type": "text",     "placeholder": "e.g. Rs. 5,00,000"},
    "Gift_Amount_Words":    {"type": "text",     "placeholder": "e.g. Five Lakhs Rupees"},
    "Deed_Date":            {"type": "text",     "placeholder": "e.g. 19 April 2026"},
    "Relationship":         {"type": "text",     "placeholder": "e.g. brother"},
    "Witness1_Name":        {"type": "text",     "placeholder": "e.g. Anita Sharma"},
    "Witness2_Name":        {"type": "text",     "placeholder": "e.g. Vikram Nair"},
}

SUPPORTED_DOC_TYPES = [
    "Onboarding_Letter",
    "Acknowledgement_of_Debt",
    "Gift_Deed",
]

def human_label(field_key: str) -> str:
    """Convert snake_case field key to a readable label."""
    return field_key.replace("_", " ")


def render_field(field_key: str, is_required: bool, col=None) -> str:
    """Render a single input field and return its value."""
    meta = FIELD_META.get(field_key, {"type": "text", "placeholder": ""})
    label_suffix = '<span class="req">*</span>' if is_required else '<span class="opt-tag">(optional)</span>'
    label_html = f'{human_label(field_key)}{label_suffix}'

    st.markdown(f'<div style="margin-bottom:4px; font-size:0.88rem; font-weight:500; color:#374151">{label_html}</div>', unsafe_allow_html=True)

    widget_key = f"field_{field_key}"
    placeholder = meta.get("placeholder", "")

    if meta["type"] == "area":
        val = st.text_area("", key=widget_key, placeholder=placeholder, height=80, label_visibility="collapsed")
    else:
        val = st.text_input("", key=widget_key, placeholder=placeholder, label_visibility="collapsed")

    return val


def collect_inputs(doc_type: str) -> dict:
    """Render all fields for the selected doc type and return collected values."""
    schema = DOCUMENT_SCHEMAS.get(doc_type, {"required": [], "optional": []})
    required_fields = schema["required"]
    optional_fields = schema["optional"]

    user_inputs = {}

    # ── Required fields ──────────────────────────────────────────────────
    if required_fields:
        st.markdown('<div class="section-label">Required Fields</div>', unsafe_allow_html=True)

        # Pair fields into rows of 2
        i = 0
        while i < len(required_fields):
            if i + 1 < len(required_fields):
                col1, col2 = st.columns(2, gap="medium")
                with col1:
                    user_inputs[required_fields[i]] = render_field(required_fields[i], is_required=True)
                with col2:
                    user_inputs[required_fields[i + 1]] = render_field(required_fields[i + 1], is_required=True)
                i += 2
            else:
                # Odd field — full width
                user_inputs[required_fields[i]] = render_field(required_fields[i], is_required=True)
                i += 1

    # ── Optional fields ──────────────────────────────────────────────────
    if optional_fields:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Optional Fields</div>', unsafe_allow_html=True)

        i = 0
        while i < len(optional_fields):
            if i + 1 < len(optional_fields):
                col1, col2 = st.columns(2, gap="medium")
                with col1:
                    user_inputs[optional_fields[i]] = render_field(optional_fields[i], is_required=False)
                with col2:
                    user_inputs[optional_fields[i + 1]] = render_field(optional_fields[i + 1], is_required=False)
                i += 2
            else:
                user_inputs[optional_fields[i]] = render_field(optional_fields[i], is_required=False)
                i += 1

    return user_inputs


# ══════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════

# ── Wordmark ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="wordmark">
  <div class="wordmark-dot"></div>
  <span class="wordmark-text">Turn2Law · Document Generator</span>
</div>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Generate a Legal Document</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Fill in the details below to produce a professional PDF in seconds.</div>', unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Section 1: Document Type ───────────────────────────────────────────────
st.markdown('<div class="section-label">Select Document Type</div>', unsafe_allow_html=True)

doc_type = st.selectbox(
    "",
    options=SUPPORTED_DOC_TYPES,
    format_func=lambda x: x.replace("_", " "),
    label_visibility="collapsed",
    key="doc_type_select",
)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Section 2: File Upload ─────────────────────────────────────────────────
st.markdown('<div class="section-label">Upload Reference Document</div>', unsafe_allow_html=True)
st.markdown('<p style="font-size:0.84rem; color:#6b7280; margin-bottom:0.6rem;">Upload a sample document so the system can auto-detect the type. Supports PDF, DOCX, PNG, JPG.</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "",
    type=["pdf", "docx", "png", "jpg", "jpeg"],
    label_visibility="collapsed",
    key="file_upload",
)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Section 3: Dynamic Form ────────────────────────────────────────────────
st.markdown('<div class="section-label">Enter Details</div>', unsafe_allow_html=True)

user_inputs = collect_inputs(doc_type)

st.markdown("<br>", unsafe_allow_html=True)

# ── Generate Button ────────────────────────────────────────────────────────
generate_clicked = st.button("Generate Document", key="generate_btn")

# ── Generation Logic ───────────────────────────────────────────────────────
if generate_clicked:
    schema = DOCUMENT_SCHEMAS.get(doc_type, {"required": [], "optional": []})
    required = schema["required"]

    # Client-side validation
    missing = [f for f in required if not user_inputs.get(f, "").strip()]
    if missing:
        missing_labels = ", ".join(human_label(f) for f in missing)
        st.markdown(f'<div class="error-box">⚠️ Please fill in all required fields: <strong>{missing_labels}</strong></div>', unsafe_allow_html=True)
    else:
        # Strip empty optional fields
        clean_inputs = {k: v for k, v in user_inputs.items() if v and v.strip()}

        # Resolve file path
        if uploaded_file is not None:
            suffix = "." + uploaded_file.name.split(".")[-1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(uploaded_file.read())
            tmp.flush()
            file_path = tmp.name
        else:
            # Fall back to bundled sample (classification only used for routing;
            # doc_type is already known from the dropdown)
            file_path = os.path.join(os.path.dirname(__file__), "sample.pdf")

        with st.spinner("Generating your document…"):
            try:
                # Change working dir so relative paths inside app.py work
                os.chdir(os.path.dirname(os.path.abspath(__file__)))

                detected_type, pdf_path = generate_document(file_path, clean_inputs)

                # Read PDF bytes for download
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                # ── Success UI ──────────────────────────────────────────
                st.markdown(f"""
                <div class="success-box">
                  <div class="success-title">✓ Document Generated Successfully</div>
                  <div class="success-sub">
                    Detected type: <span class="doc-pill">{detected_type.replace("_", " ")}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                st.download_button(
                    label="⬇ Download PDF",
                    data=pdf_bytes,
                    file_name=f"{detected_type}_{clean_inputs.get(list(clean_inputs.keys())[0], 'document')}.pdf",
                    mime="application/pdf",
                    key="download_pdf",
                )

            except ValueError as e:
                st.markdown(f'<div class="error-box">⚠️ {e}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ An error occurred: {e}</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; font-size:0.75rem; color:#d1d5db; letter-spacing:0.05em;">
  TURN2LAW · EFFIVIA LEGAL PRIVATE LIMITED · turntwolaw@gmail.com
</div>
""", unsafe_allow_html=True)
