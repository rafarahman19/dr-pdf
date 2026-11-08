import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
        /* Import Font */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* --- 1. ANIMATED BACKGROUND (GACOR DISINI!) --- */
        .stApp {
            /* Kombinasi: Hitam Utama - Hijau Gelap Misterius - Abu Gelap - Hitam lagi */
            background: linear-gradient(-45deg, #0E1117, #002b15, #121212, #0E1117);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }

        @keyframes gradientBG {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }

        /* --- 2. HEADER GRADIENT --- */
        .gradient-text {
            background: linear-gradient(to right, #00E676, #69F0AE);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 3rem;
            text-align: center;
        }

        /* --- 3. TOMBOL NAVIGASI (PILL SHAPE) --- */
        div.stButton > button {
            width: 100%;
            border-radius: 50px;
            height: 55px;
            font-weight: 600;
            border: 1px solid transparent;
            transition: all 0.3s ease;
        }

        /* Primary (Aktif) */
        button[kind="primary"] {
            background: linear-gradient(90deg, #00E676 0%, #00C853 100%);
            border: none;
            box-shadow: 0 4px 15px rgba(0, 230, 118, 0.4);
        }
        button[kind="primary"] p {
            color: #000000 !important;
            font-weight: 800;
        }
        button[kind="primary"]:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 20px rgba(0, 230, 118, 0.6);
        }

        /* Secondary (Mati) */
        button[kind="secondary"] {
            background-color: rgba(255, 255, 255, 0.05) !important; /* Semi transparan biar nyatu sama bg gerak */
            border: 2px solid #555 !important;
            color: #ccc !important;
            backdrop-filter: blur(5px); /* Efek kaca buram */
        }
        button[kind="secondary"]:hover {
            border-color: #00E676 !important;
            color: #00E676 !important;
        }

        /* --- 4. CONTAINER CARD (GLASSMORPHISM) --- */
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            border: 1px solid rgba(255, 255, 255, 0.1);
            background-color: rgba(30, 30, 30, 0.7); /* Transparan dikit biar background geraknya kelihatan */
            border-radius: 15px;
            backdrop-filter: blur(10px); /* Efek Blur di belakang card */
        }

        /* --- 5. SAFETY NET LABEL --- */
        label p {
            color: #FFFFFF !important;
            font-size: 14px;
        }

        /* --- 6. LOGO GLOW EFFECT --- */
        [data-testid="stImage"] img {
            filter: drop-shadow(0 0 15px rgba(0, 230, 118, 0.6)); 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
        }
        [data-testid="stImage"] img:hover {
            filter: drop-shadow(0 0 30px rgba(0, 230, 118, 1.0));
            transform: scale(1.03);
            cursor: pointer;
        }

        /* HIDE ELEMENTS */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
    </style>
    """, unsafe_allow_html=True)