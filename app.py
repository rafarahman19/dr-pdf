import streamlit as st
import json
import time
import random
import os
from style import load_custom_css
from utils import extract_text_from_pdf, ask_gemini, clean_json

# --- SETUP PAGE ---
tab_icon = "logo.png" if os.path.exists("logo.png") else "🩺"
st.set_page_config(page_title="dr.PdF", page_icon=tab_icon, layout="centered")
load_custom_css()

# --- SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'pdf_text' not in st.session_state: st.session_state.pdf_text = ""
if 'mode' not in st.session_state: st.session_state.mode = "ringkasan"
if 'fc_phase' not in st.session_state: st.session_state.fc_phase = "setup"
# Tambahan state buat simpen nilai sementara
if 'fc_score' not in st.session_state: st.session_state.fc_score = 0

# ==========================================
# HEADER & LOGO AREA
# ==========================================
c_left, c_center, c_right = st.columns([1, 2, 1])
with c_center:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown('<div class="gradient-text">dr.PdF 🩺</div>', unsafe_allow_html=True)

st.markdown("<p style='text-align: center; opacity: 0.7; color: #ccc; margin-top: -10px;'>Asisten Cerdas Analisis Dokumen & Pembelajaran.</p>", unsafe_allow_html=True)

# ==========================================
# LOGIC APLIKASI
# ==========================================

# --- STATE 1: BELUM UPLOAD ---
if st.session_state.pdf_text == "":
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 📂 Unggah Dokumen")
        uploaded_file = st.file_uploader("Format PDF (Maksimal 200MB)", type="pdf")
        
        if uploaded_file:
            with st.spinner("⏳ Sedang memproses dokumen..."):
                text = extract_text_from_pdf(uploaded_file)
                if text:
                    st.session_state.pdf_text = text
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Gagal membaca dokumen. Pastikan fail tidak rusak atau terkunci.")

# --- STATE 2: SUDAH UPLOAD ---
else:
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    def nav_btn(label, key_mode, col):
        type_btn = "primary" if st.session_state.mode == key_mode else "secondary"
        if col.button(label, key=f"nav_{key_mode}", type=type_btn, use_container_width=True):
            st.session_state.mode = key_mode
            st.session_state.fc_phase = "setup"
            st.rerun()

    nav_btn("📝 Ringkasan", "ringkasan", col1)
    nav_btn("🧠 Ujian", "ujian", col2)
    nav_btn("🎮 Hafalan", "hafalan", col3)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # === MODE: RINGKASAN ===
    if st.session_state.mode == "ringkasan":
        with st.container(border=True):
            st.subheader("📝 Parameter Ringkasan")
            col_r1, col_r2 = st.columns([1, 2])
            with col_r1:
                fmt = st.selectbox("Format Keluaran", ["Paragraf Singkat", "Poin-Poin (Bullet Points)", "Tabel Perbandingan", "Analogi Sederhana"])
            with col_r2:
                custom_instruction = st.text_input("Instruksi Tambahan", placeholder="Contoh: Fokuskan pada aspek sejarah...")

            if st.button("✨ Buat Ringkasan", type="primary", use_container_width=True):
                with st.spinner("Sedang menyusun ringkasan..."):
                    extra = f"Instruksi: {custom_instruction}" if custom_instruction else ""
                    prompt = f"Buatkan ringkasan materi ini. Format: {fmt}. {extra}. Gunakan Bahasa Indonesia Baku."
                    res = ask_gemini(prompt, st.session_state.pdf_text)
                    if res and "ERROR" in res:
                        st.error(res)
                    else:
                        st.session_state.result_summary = res
        
        if 'result_summary' in st.session_state:
            st.markdown("### 📖 Hasil Ringkasan")
            with st.container(border=True):
                st.markdown(st.session_state.result_summary)
            
            st.download_button(
                label="📥 Unduh Ringkasan (.txt)",
                data=st.session_state.result_summary,
                file_name="drpdf_ringkasan.txt",
                mime="text/plain",
                type="secondary",
                use_container_width=True
            )

    # === MODE: UJIAN ===
    elif st.session_state.mode == "ujian":
        with st.container(border=True):
            st.subheader("🧠 Konfigurasi Ujian")
            col_q1, col_q2 = st.columns(2)
            jml = col_q1.number_input("Jumlah Soal", 1, 20, 5, key="exam_num")
            lvl = col_q2.selectbox("Tingkat Kesulitan", ["Mudah", "Menengah", "Sulit (HOTS)"], key="exam_diff")
            
            if st.button("📝 Susun Soal Ujian", type="primary", use_container_width=True):
                with st.spinner("Sedang menyusun soal..."):
                    p = f"""
                    Buat {jml} soal pilihan ganda ({lvl}) dari teks.
                    WAJIB 5 opsi (A-E).
                    Format JSON Valid: [{{"question": "...", "options": ["A. ..", "B. ..", "C. ..", "D. ..", "E. .."], "answer": "A. .."}}]
                    """
                    raw = ask_gemini(p, st.session_state.pdf_text)
                    cleaned = clean_json(raw)
                    if cleaned:
                        st.session_state.quiz_db = json.loads(cleaned)
                        st.session_state.quiz_ans = {}
                        st.rerun()
                    else:
                        st.error("Gagal. Coba lagi.")
        
        if 'quiz_db' in st.session_state:
            st.markdown("---")
            for i, q in enumerate(st.session_state.quiz_db):
                with st.container(border=True):
                    st.markdown(f"**{i+1}. {q['question']}**")
                    st.session_state.quiz_ans[i] = st.radio("Jawab:", q['options'], key=f"q_{i}", index=None, label_visibility="collapsed")
            
            if st.button("✅ Periksa Hasil", type="primary", use_container_width=True):
                score = 0
                for i, q in enumerate(st.session_state.quiz_db):
                    if st.session_state.quiz_ans.get(i, "").startswith(q['answer'][0]):
                        score += 1
                final = (score / len(st.session_state.quiz_db)) * 100
                
                if final > 80: st.success(f"🎉 Luar Biasa! Nilai: {int(final)}")
                else: st.warning(f"Nilai: {int(final)}. Belajar lagi!")
                
                quiz_text = f"NILAI ANDA: {int(final)}\n\n"
                for i, q in enumerate(st.session_state.quiz_db):
                    user_jwb = st.session_state.quiz_ans.get(i, "Tidak Dijawab")
                    quiz_text += f"{i+1}. {q['question']}\n   Jawaban Anda: {user_jwb}\n   Kunci Benar: {q['answer']}\n\n"
                
                st.download_button(
                    label="📥 Unduh Hasil Ujian (.txt)",
                    data=quiz_text,
                    file_name="drpdf_ujian_hasil.txt",
                    mime="text/plain",
                    use_container_width=True
                )

    # === MODE: HAFALAN (FLASHCARD FIX) ===
    elif st.session_state.mode == "hafalan":
        
        # FASE 1: SETUP (Bikin Kartu)
        if st.session_state.fc_phase == "setup":
            with st.container(border=True):
                st.subheader("🎮 Konfigurasi Flashcard")
                col_fc1, col_fc2 = st.columns(2)
                num = col_fc1.number_input("Jumlah Kartu", 3, 20, 5, key="fc_num")
                diff = col_fc2.selectbox("Level", ["Pemula", "Menengah", "Lanjut"], key="fc_diff")

                if st.button("🔄 Buat Flashcard", type="primary", use_container_width=True):
                    with st.spinner("Menyiapkan kartu..."):
                        p = f"""Buat {num} flashcard (Istilah & Definisi) difficulty {diff}. JSON: [{{"term":"..","definition":".."}}]"""
                        raw = ask_gemini(p, st.session_state.pdf_text)
                        cleaned = clean_json(raw)
                        if cleaned:
                            st.session_state.flashcards = json.loads(cleaned)
                            st.session_state.fc_phase = "study"
                            st.rerun()

        # FASE 2: STUDY (Belajar Dulu)
        elif st.session_state.fc_phase == "study":
            st.success(f"✅ {len(st.session_state.flashcards)} kartu siap. Hafalkan!")
            flash_text = "DAFTAR KARTU HAFALAN DR.PDF\n\n"
            
            for card in st.session_state.flashcards:
                with st.container(border=True):
                    st.markdown(f"**Istilah:** {card['term']}")
                    st.caption(f"**Definisi:** {card['definition']}")
                flash_text += f"{card['term']} : {card['definition']}\n"
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tombol ke Ujian
            if st.button("🚀 MULAI UJIAN HAFALAN", type="primary", use_container_width=True):
                st.session_state.fc_phase = "test"
                st.session_state.fc_answers = {}
                # Siapkan opsi jawaban dari semua istilah yang ada
                st.session_state.fc_options = [c['term'] for c in st.session_state.flashcards]
                st.rerun()
            
            # Tombol Bikin Ulang
            if st.button("🔄 Buat Ulang", type="secondary", use_container_width=True): 
                st.session_state.fc_phase = "setup"
                st.rerun()
            
            # Download Kartu
            st.download_button(
                label="📥 Unduh Materi Hafalan (.txt)",
                data=flash_text,
                file_name="drpdf_flashcard.txt",
                mime="text/plain",
                type="secondary",
                use_container_width=True
            )

        # FASE 3: TEST (Ujiannya)
        elif st.session_state.fc_phase == "test":
            st.markdown("### 📝 Evaluasi Hafalan")
            st.info("Pasangkan definisi berikut dengan istilah yang tepat!")
            
            with st.form("fc_test_form"):
                for i, card in enumerate(st.session_state.flashcards):
                    st.markdown(f"**Soal {i+1}:** {card['definition']}")
                    opts = list(st.session_state.fc_options)
                    random.shuffle(opts)
                    st.session_state.fc_answers[i] = st.selectbox("Jawab:", opts, key=f"fc_{i}", index=None, label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Pas Submit, kita hitung nilai terus pindah ke fase RESULT
                if st.form_submit_button("✅ Periksa Nilai", type="primary", use_container_width=True):
                    score = 0
                    for i, card in enumerate(st.session_state.flashcards):
                        if st.session_state.fc_answers.get(i) == card['term']: score += 1
                    
                    # Simpan nilai ke session state
                    st.session_state.fc_score = (score / len(st.session_state.flashcards)) * 100
                    st.session_state.fc_phase = "result" # Pindah ke fase Hasil
                    st.rerun()

        # FASE 4: RESULT (Hasil & Ulangi) - INI YANG BARU
        elif st.session_state.fc_phase == "result":
            final = st.session_state.fc_score
            st.markdown("### 📊 Hasil Ujian Hafalan")
            
            col_res1, col_res2 = st.columns([1, 2])
            with col_res1:
                 st.metric("Skor Kamu", f"{int(final)}")
            with col_res2:
                if final == 100:
                    st.success("🔥 SEMPURNA! Ingatan Tajam!")
                    st.balloons()
                elif final >= 70:
                    st.warning("😎 Cukup Baik. Tingkatkan lagi!")
                else:
                    st.error("😭 Perlu banyak latihan lagi.")

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tombol Ulangi Latihan (Balik ke STUDY)
            if st.button("🔄 Ulangi Hafalan (Balik ke Istilah)", type="primary", use_container_width=True):
                st.session_state.fc_phase = "study"
                st.rerun()
            
            # Tombol Bikin Baru (Balik ke SETUP)
            if st.button("📂 Buat Kartu Baru", type="secondary", use_container_width=True):
                st.session_state.fc_phase = "setup"
                st.rerun()

    # FOOTER: GANTI FILE
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("📂 Unggah Dokumen Baru", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.rerun()