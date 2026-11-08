import streamlit as st
import google.generativeai as genai
import PyPDF2
import re
import json
import time

# --- CONFIG ---
# Mengambil API Key dengan aman dari Streamlit Secrets atau Environment Variable
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- FUNGSI BACA PDF ---
@st.cache_data(show_spinner=False)
def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return None

# --- CLEANING JSON ---
def clean_json(text_response):
    if not text_response: return None
    text_response = text_response.replace("```json", "").replace("```", "")
    match_array = re.search(r'\[.*\]', text_response, re.DOTALL)
    if match_array: return match_array.group(0)
    match_obj = re.search(r'\{.*\}', text_response, re.DOTALL)
    if match_obj: return match_obj.group(0)
    return None

# --- AI ENGINE (ANTI-LIMIT & RETRY) ---
def ask_gemini(prompt, text_data):
    if not API_KEY or "PASTE" in API_KEY: 
        return "ERROR: API Key belum diisi di utils.py!"
    
    genai.configure(api_key=API_KEY)
    
    # Gunakan model Flash Latest (Biasanya lebih longgar kuotanya)
    model_name = 'gemini-flash-latest' 
    
    try:
        model = genai.GenerativeModel(model_name=model_name)
        
        # Limit token input biar aman
        safe_text = text_data[:15000] 
        
        final_prompt = f"""
        {prompt}
        
        Konteks Materi:
        {safe_text}
        """
        
        # Retry Logic (3x Percobaan kalo server sibuk)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(final_prompt)
                if response.text:
                    return response.text
            except Exception as e:
                if "429" in str(e): # Kena Limit
                    time.sleep(4) # Istirahat bentar
                    continue
                else:
                    return f"ERROR SYSTEM: {str(e)}"
        
        return "ERROR: Server Google sibuk. Coba lagi nanti."

    except Exception as e:
        return f"ERROR SYSTEM: {str(e)}"
