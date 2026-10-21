
import re
from io import BytesIO

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="WhatsApp Information Extractor",
    layout="wide"
)

st.title("WhatsApp Information Extractor")
st.write(
    "Upload a WhatsApp chat exported as a .txt file "
    "to find jobs, business leads, advertisements, "
    "phone numbers, and links."
)

CATEGORIES = {
    "Job Vacancy": [
        "job", "vacancy", "hiring", "internship",
        "recruitment", "career", "employment"
    ],
    "Business Lead": [
        "business", "client", "customer", "project",
        "freelancer", "deal", "service required"
    ],
    "Advertisement": [
        "advertisement", "promotion", "discount",
        "admission open", "register now", "offer"
    ]
}

uploaded = st.file_uploader(
    "Upload WhatsApp chat (.txt)",
    type=["txt"]
)

custom_text = st.text_input(
    "Additional keywords (separate with commas)",
    placeholder="scholarship, tender, event"
)

if uploaded is not None:
    chat_text = uploaded.getvalue().decode(
        "utf-8-sig", errors="replace"
    )

    custom_keywords = [
        word.strip().lower()
        for word in custom_text.split(",")
        if word.strip()
    ]

    results = []

    for line in chat_text.splitlines():
        lower_line = line.lower()

        matched = [
            category
            for category, words in CATEGORIES.items()
            if any(word in lower_line for word in words)
        ]

        if any(word in lower_line for word in custom_keywords):
            matched.append("Custom Keyword")

        phones = re.findall(
            r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)",
            line
        )
        links = re.findall(
            r"https?://[^\s]+|www\.[^\s]+",
            line
        )

        if matched or phones or links:
            results.append({
                "Category": ", ".join(matched) or "Other",
                "Message": line,
                "Phone Numbers": ", ".join(phones),
                "Links": ", ".join(links)
            })

    df = pd.DataFrame(
        results,
        columns=[
            "Category", "Message", "Phone Numbers", "Links"
        ]
    )

    st.subheader(f"Found {len(df)} matching messages")
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        excel_file = BytesIO()

        with pd.ExcelWriter(
            excel_file, engine="openpyxl"
        ) as writer:
            df.to_excel(
                writer, index=False, sheet_name="Extracted Data"
            )

        st.download_button(
            "Download results as Excel",
            data=excel_file.getvalue(),
            file_name="WhatsApp_Extracted_Information.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )
    else:
        st.info("No matching information was found.")
