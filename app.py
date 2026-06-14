import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import base64
import datetime
import random
from audio_recorder_streamlit import audio_recorder

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CryingCare Analysis", page_icon="logo.png", layout="wide", initial_sidebar_state="expanded")

# --- INISIALISASI DATABASE MEMORI ---
if 'baby_name' not in st.session_state:
    st.session_state['baby_name'] = "Baby Rayyan"
if 'baby_age' not in st.session_state:
    st.session_state['baby_age'] = "3 Bulan"
if 'history' not in st.session_state:
    st.session_state['history'] = [] 
if 'last_audio_hash' not in st.session_state:
    st.session_state['last_audio_hash'] = None 

TIPS_REKOMENDASI = {
    "Tidak Nyaman": "Periksa popok (apakah penuh/kotor?), pakaian (apakah bahannya gatal/sempit?), atau suhu ruangan (apakah bayi berkeringat/kedinginan?).",
    "Lapar": "Bayi sepertinya membutuhkan susu. Segera berikan ASI atau susu botol.",
    "Ngantuk": "Bayi kelelahan. Bawa ke ruangan yang redup dan tenang. Ayun-ayun perlahan.",
    "Sakit Perut": "Coba pijat lembut perut bayi dengan gerakan melingkar, atau tekuk kakinya perlahan."
}

# --- FUNGSI MENGAMBIL ICON ---
def get_image_base64(base_name):
    for ext in ['png', 'jpeg', 'jpg']:
        file_path = f"{base_name}.{ext}"
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                mime = "image/png" if ext == "png" else "image/jpeg"
                return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
    return ""

icon_overview = get_image_base64("overview")
icon_analisis = get_image_base64("analytic")
icon_pengaturan = get_image_base64("setting")
logo_utama = get_image_base64("logo")

# --- CUSTOM CSS (100% CENTER FIX) ---
st.markdown(f"""
    <style>
    .stApp, [data-testid="stHeader"] {{ background-color: #F8F5EE !important; }}
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {{ background-color: #F8F5EE !important; border-right: none !important; }}
    
    /* 1. KUNCI UTAMA: MEMAKSA SELURUH ISI SIDEBAR MENJADI FLEX CENTER */
    [data-testid="stSidebarUserContent"] {{ 
        display: flex !important; 
        flex-direction: column !important; 
        align-items: center !important; /* Memaksa semua elemen rata tengah */
        padding-left: 0 !important; 
        padding-right: 0 !important; 
        width: 100% !important; 
    }}

    /* 2. MENGHANCURKAN WRAPPER BAWAAN STREAMLIT */
    div[data-testid="stRadio"] {{ 
        width: 100% !important; 
        display: flex !important; 
        justify-content: center !important; 
    }}
    div[role="radiogroup"] {{ 
        width: 100% !important; 
        display: flex !important; 
        flex-direction: column !important; 
        align-items: center !important; /* MEMAKSA ICON RATA TENGAH */
    }}

    div[role="radiogroup"] label div:first-of-type, div[role="radiogroup"] label p {{ display: none !important; }}

    /* 3. SETTING ICON MUTLAK TENGAH */
    div[role="radiogroup"] label {{
        display: block !important;
        background-repeat: no-repeat !important; 
        background-size: contain !important; 
        background-position: center !important;
        height: 60px !important; 
        width: 60px !important; 
        margin: 0 auto 35px auto !important; /* Auto Kiri-Kanan membuat letaknya diam di tengah */
        cursor: pointer; 
        transition: transform 0.2s; 
        padding: 0 !important; 
        border: none !important; 
        background-color: transparent !important; 
    }}
    
    div[role="radiogroup"] label:hover {{ transform: scale(1.15) !important; }}

    div[role="radiogroup"] label:nth-child(1) {{ background-image: url("{icon_overview}"); }}
    div[role="radiogroup"] label:nth-child(2) {{ background-image: url("{icon_analisis}"); }}
    div[role="radiogroup"] label:nth-child(3) {{ background-image: url("{icon_pengaturan}"); }}

    /* STYLING KARTU UI */
    .pastel-card {{ background-color: #FFFFFF; border-radius: 15px; padding: 20px; box-shadow: 0 4px 20px rgba(124, 163, 204, 0.12); margin-bottom: 20px;}}
    .card-title {{ color: #5C7C99; font-size: 18px; font-weight: 700; margin-bottom: 15px; font-family: 'Segoe UI', sans-serif;}}
    .status-alert {{ background-color: #F0F8F7; border-left: 5px solid #8CD1C6; padding: 15px; border-radius: 8px;}}
    .status-text {{ color: #4A6B8C; font-size: 24px; font-weight: bold; margin: 0;}}
    .status-sub {{ color: #7CA3CC; font-size: 14px; margin: 0;}}
    .empty-state {{ text-align: center; padding: 60px 20px; background-color: #FFFFFF; border-radius: 15px; border: 2px dashed #C4E4DF; }}
    .empty-title {{ color: #7CA3CC; font-size: 24px; font-weight: bold; margin-bottom: 10px;}}
    .empty-desc {{ color: #5C7C99; font-size: 16px;}}
    .tips-box {{ background-color: #F3F8FC; border-radius: 10px; padding: 15px; border: 1px solid #DCE8F4;}}
    .tips-title {{ color: #7CA3CC; font-weight: bold; font-size: 16px; margin-bottom:5px;}}
    .tips-content {{ color: #5C7C99; font-size: 14px;}}
    
    .stTextInput label {{ color: #5C7C99 !important; font-weight: 600; }}
    .audio-recorder {{ display: flex; justify-content: center; margin-bottom: 20px; }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGASI KIRI ---
with st.sidebar:
    
    # LOGO DIPAKSA RATA TENGAH DENGAN MARGIN AUTO
    if logo_utama != "":
        st.markdown(f'''
            <div style="display: flex; justify-content: center; width: 100%; margin-bottom: 40px;">
                <img src="{logo_utama}" style="width: 85%; max-width: 180px; background-color: transparent;">
            </div>
        ''', unsafe_allow_html=True)
    
    # NAVIGASI
    menu = st.radio("Navigasi", ["overview", "analisis", "pengaturan"], label_visibility="collapsed")
    
    # PROFIL BAYI (Rata Tengah)
    st.markdown("<hr style='border-color: #EAF0F6; width:80%; margin: 10px auto 20px auto;'>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; color: #5C7C99; width: 100%;">
            <p style="margin: 0; font-size: 14px;">Bayi:</p>
            <p style="margin: 0; font-size: 18px; font-weight: bold;">{st.session_state['baby_name']}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px;">Usia: {st.session_state['baby_age']}</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# HALAMAN 1: DASHBOARD UTAMA
# ==========================================
if menu == "overview":
    st.markdown("<h2 style='color: #4A6B8C; margin-bottom: 20px;'>Rekapitulasi & Riwayat Tangisan</h2>", unsafe_allow_html=True)

    if len(st.session_state['history']) == 0:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-title">Belum Ada Data Analisis Hari Ini</div>
                <div class="empty-desc">Sistem belum mencatat tangisan apapun. Silakan rekam terlebih dahulu di menu Analisis Suara.</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        df_history = pd.DataFrame(st.session_state['history'])

        col_left, col_right = st.columns([1.2, 1]) 
        
        with col_left:
            st.markdown("<div class='pastel-card'><div class='card-title'>Pola Tangisan Hari Ini</div>", unsafe_allow_html=True)
            df_history['Jam'] = df_history['Waktu'].apply(lambda x: x.split(":")[0] + ":00")
            df_trend = df_history.groupby('Jam').size().reset_index(name='Intensitas')
            
            fig_bar = px.bar(df_trend, x="Jam", y="Intensitas", template="plotly_white", height=250, color_discrete_sequence=['#7CA3CC']) 
            fig_bar.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(dtick=1), xaxis=dict(type='category'))
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='pastel-card'><div class='card-title'>Riwayat Lengkap</div>", unsafe_allow_html=True)
            table_html = '<table style="width:100%; text-align:left; font-size:14px; color:#5C7C99;">'
            table_html += '<tr style="border-bottom: 2px solid #DCE8F4;"><th style="padding:5px;">Waktu</th><th>Hasil Deteksi</th><th>Durasi</th><th>Akurasi</th></tr>'
            for idx, row in df_history.iterrows():
                table_html += f'<tr style="border-bottom: 1px solid #EAF0F6;"><td style="padding:5px;">{row["Waktu"]}</td><td>{row["Hasil"]}</td><td>{row["Durasi"]}</td><td>{row["Keyakinan"]}</td></tr>'
            table_html += '</table><br></div>'
            st.markdown(table_html, unsafe_allow_html=True)

        with col_right:
            st.markdown("<div class='pastel-card'><div class='card-title'>Distribusi Penyebab Tangisan</div>", unsafe_allow_html=True)
            df_pie = df_history.groupby('Hasil').size().reset_index(name='Jumlah')
            warna_logo = ['#7CA3CC', '#8CD1C6', '#A0C4E2', '#C4E4DF']
            fig_pie = px.pie(df_pie, values='Jumlah', names='Hasil', hole=0.6, height=300, color_discrete_sequence=warna_logo)
            fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=True, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# HALAMAN 2: ANALISIS SUARA
# ==========================================
elif menu == "analisis":
    st.markdown("<h2 style='color: #4A6B8C; margin-bottom: 10px;'>Analisis Suara Langsung</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #5C7C99;'>Tekan ikon mikrofon untuk merekam. Sistem akan langsung memproses dan menampilkan hasil serta solusinya di sini.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        st.markdown("<div class='audio-recorder'>", unsafe_allow_html=True)
        audio_bytes = audio_recorder(text="", recording_color="#7CA3CC", neutral_color="#8CD1C6", icon_size="3x")
        st.markdown("</div>", unsafe_allow_html=True)
    
    if audio_bytes:
        current_audio_hash = hash(audio_bytes)
        if st.session_state['last_audio_hash'] != current_audio_hash:
            st.session_state['last_audio_hash'] = current_audio_hash
            
            kategori_prediksi = ["Tidak Nyaman", "Lapar", "Ngantuk", "Sakit Perut"]
            hasil_prediksi = random.choice(kategori_prediksi)
            waktu_sekarang = datetime.datetime.now().strftime("%H:%M")
            durasi_acak = f"{random.randint(5, 15)} Detik"
            keyakinan_acak = f"{random.randint(85, 98)}%"
            
            st.session_state['history'].insert(0, {"Waktu": waktu_sekarang, "Hasil": hasil_prediksi, "Durasi": durasi_acak, "Keyakinan": keyakinan_acak})
        
        data_terakhir = st.session_state['history'][0]
        
        st.audio(audio_bytes, format="audio/wav")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_res1, col_res2 = st.columns([1, 1])
        with col_res1:
            st.markdown(f"""
                <div class="pastel-card">
                    <div class="card-title">Hasil Deteksi</div>
                    <div class="status-alert">
                        <p class="status-text">{data_terakhir['Hasil']}</p>
                        <p class="status-sub">Akurasi: <b>{data_terakhir['Keyakinan']}</b> | Durasi: {data_terakhir['Durasi']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            x_wave = np.linspace(0, 10, 500)
            y_wave = np.sin(x_wave * 5) * np.exp(-x_wave * 0.2) + np.random.normal(0, 0.1, 500)
            fig_wave = px.line(x=x_wave, y=y_wave, template="plotly_white", height=130)
            fig_wave.update_traces(line_color='#8CD1C6', line_width=2) 
            fig_wave.update_layout(margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_wave, use_container_width=True)

        with col_res2:
            tips_terkini = TIPS_REKOMENDASI.get(data_terakhir['Hasil'], "Tetap tenang dan perhatikan kebutuhan bayi.")
            st.markdown(f"""
                <div class="pastel-card" style="height: 100%;">
                    <div class="card-title">Rekomendasi Tindakan</div>
                    <div class="tips-box">
                        <p class="tips-title">Merespons "{data_terakhir['Hasil']}"</p>
                        <div class="tips-content" style="font-size: 16px; line-height: 1.6;">{tips_terkini}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# ==========================================
# HALAMAN 3: PENGATURAN
# ==========================================
elif menu == "pengaturan":
    st.markdown("<h2 style='color: #4A6B8C; margin-bottom: 20px;'>Pengaturan Profil</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='color: #5C7C99;'>Silakan ubah data profil bayi di bawah ini:</p>", unsafe_allow_html=True)
    
    input_nama = st.text_input("Nama Bayi", value=st.session_state['baby_name'])
    input_usia = st.text_input("Usia Bayi", value=st.session_state['baby_age'])
    
    st.markdown("""
        <style>
        div.stButton > button:first-child { background-color: #7CA3CC; color: white; border-radius: 8px; border: none; margin-top: 15px;}
        div.stButton > button:first-child:hover { background-color: #8CD1C6; color: white; }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("Simpan Perubahan", use_container_width=True):
        st.session_state['baby_name'] = input_nama
        st.session_state['baby_age'] = input_usia
        st.rerun()
        
    st.markdown("<hr style='margin: 30px 0; border-color: #EAF0F6;'>", unsafe_allow_html=True)
    
    if st.button("Reset Semua Riwayat Dashboard", use_container_width=True):
        st.session_state['history'] = []
        st.session_state['last_audio_hash'] = None
        st.rerun()