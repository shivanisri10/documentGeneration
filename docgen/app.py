from utils.file_utils import extract_text
from classifier.classify import classify_document
from schema import DOCUMENT_SCHEMAS
from utils.latex_writer import render_latex
import re

TEMPLATE_MAP = {
    "Onboarding_Letter": "templates/onboarding_template.tex",
    "Acknowledgement_of_Debt": "templates/acknowledgement_of_debt_template.tex",
    "Gift_Deed": "templates/gift_deed_template.tex"
}

def validate_inputs(doc_type, user_inputs):
    schema = DOCUMENT_SCHEMAS.get(doc_type)
    if not schema:
        raise ValueError(f"Unsupported document type: {doc_type}")

    missing = [
        f for f in schema["required"]
        if f not in user_inputs or not user_inputs[f]
    ]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

def generate_document(file_path, user_inputs):
    # Extract text only for classification
    extracted_text = extract_text(file_path)

    # Detect document type
    doc_type = classify_document(extracted_text)

    # Validate inputs
    validate_inputs(doc_type, user_inputs)

    # Select LaTeX template
    template_path = TEMPLATE_MAP.get(doc_type)
    if not template_path:
        raise ValueError(f"No template found for {doc_type}")

    # ✅ Dynamic file naming (from your old code)
    name_field = (
        user_inputs.get("Debtor_Name")
        or user_inputs.get("Employee_Name")
        or user_inputs.get("Donor_Name")
        or user_inputs.get("Name")
        or "document"
    )

    safe_name = re.sub(r'\W+', '_', name_field)

    output_tex = f"{doc_type}_{safe_name}.tex"
    output_pdf = f"{doc_type}_{safe_name}.pdf"

    # Render PDF via LaTeX
    render_latex(
        template_path,
        output_tex,
        output_pdf,
        user_inputs
    )

    return doc_type, output_pdf


if __name__ == "__main__":
    file_path = r"C:\Users\shiva\Downloads\3500+ Legal Drafts\3500+ Legal Drafts\Gift Deed\GIFT DEED WITH RESPECT TO MONEY.docx"

    user_inputs = {
        "Donor_Name": "Ramesh Kumar",
        "Donee_Name": "Suresh Kumar",
        "Donor_Address": "42, MG Road, Bengaluru, Karnataka - 560001",
        "Donee_Address": "18, Anna Nagar, Chennai, Tamil Nadu - 600040",
        "Gift_Amount_Figures": "Rs. 5,00,000",
        "Gift_Amount_Words": "Five Lakhs Rupees",
        "Deed_Date": "19 April 2026",
        "Day": "19th",
        "Month_Year": "April 2026",
        "Relationship": "brother",
        "Witness1_Name": "Anita Sharma",
        "Witness2_Name": "Vikram Nair"
    }

    doc_type, pdf_path = generate_document(file_path, user_inputs)
    print("Detected:", doc_type)
    print("Saved as:", pdf_path)