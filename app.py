"""
Sistem Pendukung Keputusan (SPK) - Rekomendasi Program Studi
Metode: AHP (Analytic Hierarchy Process)
Framework: Streamlit

Membantu siswa SMA/SMK dalam memilih jurusan kuliah berdasarkan:
- Nilai Akademik (Exam Score)
- Minat (Input Dinamis)
- Bakat (Input Dinamis)
- Hasil Psikologi (Peer Influence)
- Motivasi (Motivation Level)
- Family Income (dari dataset — bukan input dinamis)
"""

import streamlit as st
import pandas as pd
import numpy as np
import os

from ahp import (
    create_pairwise_matrix,
    calculate_priority_vector,
    calculate_consistency_ratio,
    calculate_final_scores,
    rank_alternatives,
    get_local_priority_tables,
)
from data_processing import (
    load_dataset,
    preprocess_data,
    get_student_data,
    get_student_label,
    get_summary_statistics,
    save_dataset,
    PEER_INFLUENCE_MAP,
    MOTIVATION_LEVEL_MAP,
    FAMILY_INCOME_MAP,
)
from program_studi import (
    DAFTAR_PRODI,
    MINAT_OPTIONS,
    BAKAT_OPTIONS,
    PRODI_DESCRIPTIONS,
    get_all_prodi_scores,
)

# ============================================================
# PAGE CONFIG & CUSTOM STYLING
# ============================================================
st.set_page_config(
    page_title="SPK Rekomendasi Jurusan | AHP",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: #e0e0ff !important;
    }

    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .hero-container h1 { color: #ffffff !important; font-size: 2.2rem !important; font-weight: 700 !important; margin-bottom: 0.5rem !important; }
    .hero-container p { color: rgba(255,255,255,0.85) !important; font-size: 1.05rem !important; }

    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 14px;
        padding: 1.3rem 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
    .metric-card .metric-value { font-size: 2rem; font-weight: 700; color: #302b63; }
    .metric-card .metric-label { font-size: 0.85rem; color: #666; margin-top: 0.3rem; }

    .rank-card {
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: transform 0.2s ease;
    }
    .rank-card:hover { transform: translateX(5px); }
    .rank-gold { background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%); box-shadow: 0 4px 20px rgba(247,151,30,0.3); }
    .rank-silver { background: linear-gradient(135deg, #bdc3c7 0%, #e8e8e8 100%); box-shadow: 0 4px 20px rgba(189,195,199,0.3); }
    .rank-bronze { background: linear-gradient(135deg, #c47a3b 0%, #e8a87c 100%); box-shadow: 0 4px 20px rgba(196,122,59,0.3); }
    .rank-normal { background: linear-gradient(135deg, #f0f2f5 0%, #e4e7eb 100%); box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
    .rank-number { font-size: 1.8rem; font-weight: 800; min-width: 50px; text-align: center; }
    .rank-gold .rank-number { color: #7c4a00; }
    .rank-silver .rank-number { color: #4a4a4a; }
    .rank-bronze .rank-number { color: #5a2d0c; }
    .rank-normal .rank-number { color: #888; }
    .rank-info h3 { margin: 0 !important; font-size: 1.1rem !important; font-weight: 600 !important; }
    .rank-gold .rank-info h3 { color: #5c3600 !important; }
    .rank-silver .rank-info h3 { color: #333 !important; }
    .rank-bronze .rank-info h3 { color: #3d1a00 !important; }
    .rank-normal .rank-info h3 { color: #444 !important; }
    .rank-score { font-size: 0.9rem; margin-top: 2px; }

    .cr-consistent {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white; padding: 1rem 1.5rem; border-radius: 12px;
        text-align: center; font-weight: 600;
        box-shadow: 0 4px 15px rgba(17,153,142,0.3);
    }
    .cr-inconsistent {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white; padding: 1rem 1.5rem; border-radius: 12px;
        text-align: center; font-weight: 600;
        box-shadow: 0 4px 15px rgba(235,51,73,0.3);
    }

    .profile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px; padding: 2rem; color: white; text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .profile-card h2 { color: #fff !important; margin-bottom: 0.5rem !important; }
    .profile-card p { color: rgba(255,255,255,0.85) !important; }

    .info-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #d6eaf8 100%);
        border-left: 5px solid #667eea;
        border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
    }
    .info-box h4 { color: #302b63 !important; margin: 0 0 0.5rem 0 !important; }
    .info-box p { color: #444 !important; margin: 0 !important; font-size: 0.95rem; }

    .step-card {
        background: white; border-radius: 14px; padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #eee; height: 100%;
    }
    .step-card h4 { color: #302b63 !important; }
    .step-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; width: 36px; height: 36px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.1rem; margin-bottom: 0.8rem;
    }

    .stDataFrame { border-radius: 12px; overflow: hidden; }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; border: none !important;
        border-radius: 12px !important; padding: 0.7rem 2rem !important;
        font-weight: 600 !important; font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }

    .custom-divider {
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        border-radius: 2px; margin: 1.5rem 0;
    }

    /* CRUD styling */
    .crud-card {
        background: white; border-radius: 14px; padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8; margin-bottom: 1rem;
    }
    .crud-add { border-left: 5px solid #11998e; }
    .crud-edit { border-left: 5px solid #667eea; }
    .crud-delete { border-left: 5px solid #eb3349; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATASET PATH
# ============================================================
DATASET_PATH = "StudentPerformanceFactors.csv"


# ============================================================
# LOAD DATA (dengan session_state untuk mendukung CRUD)
# ============================================================
def load_and_process_data():
    """Load dan preprocess dataset"""
    try:
        df = load_dataset(DATASET_PATH)
        df_processed = preprocess_data(df)
        return df, df_processed
    except FileNotFoundError:
        st.error("❌ File `StudentPerformanceFactors.csv` tidak ditemukan!")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error memuat dataset: {str(e)}")
        st.stop()


# Inisialisasi session state untuk dataset
if "df_raw" not in st.session_state or "df_processed" not in st.session_state:
    df_raw, df_processed = load_and_process_data()
    st.session_state.df_raw = df_raw
    st.session_state.df_processed = df_processed

df_raw = st.session_state.df_raw
df_processed = st.session_state.df_processed
stats = get_summary_statistics(df_processed)


def reload_data():
    """Reload data dari CSV dan simpan ke session_state"""
    df_raw, df_processed = load_and_process_data()
    st.session_state.df_raw = df_raw
    st.session_state.df_processed = df_processed


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown("## 🎓 SPK Jurusan")
    st.markdown("---")

    halaman = st.radio(
        "📍 Navigasi",
        ["🏠 Beranda", "📊 Data & Dataset", "✏️ Kelola Data (CRUD)", "🧮 Hitung SPK (AHP)", "👥 Profil Kelompok"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; opacity:0.7; font-size:0.8rem; color: #ccc;'>
        <p>Metode: AHP (Saaty)</p>
        <p>© 2025 Proyek Akhir SCPK</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HALAMAN 1: BERANDA
# ============================================================
if halaman == "🏠 Beranda":
    st.markdown("""
    <div class="hero-container">
        <h1>🎓 Sistem Perekomendasian Jurusan</h1>
        <p>Sistem Pendukung Keputusan berbasis AHP untuk membantu siswa SMA/SMK
        memilih program studi yang tepat berdasarkan nilai, minat, bakat, psikologi, motivasi, dan pendapatan keluarga</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_students']:,}</div>
            <div class="metric-label">📚 Total Data Siswa</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">6</div>
            <div class="metric-label">📋 Kriteria SPK</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">15</div>
            <div class="metric-label">🏫 Program Studi</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">AHP</div>
            <div class="metric-label">⚙️ Metode SPK</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📖 Cara Menggunakan Sistem")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">1</div>
            <h4>📊 Lihat Dataset</h4>
            <p style="font-size:0.9rem; color:#666;">Buka halaman <b>Data & Dataset</b> untuk melihat data siswa yang tersedia beserta statistik deskriptifnya.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">2</div>
            <h4>✏️ Kelola Data</h4>
            <p style="font-size:0.9rem; color:#666;">Gunakan halaman <b>Kelola Data (CRUD)</b> untuk menambah, mengubah, atau menghapus data siswa dari dataset.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">3</div>
            <h4>🧮 Input & Hitung</h4>
            <p style="font-size:0.9rem; color:#666;">Buka halaman <b>Hitung SPK</b>, pilih siswa, atur minat, bakat, dan bobot kriteria, lalu klik tombol hitung.</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">4</div>
            <h4>🏆 Lihat Rekomendasi</h4>
            <p style="font-size:0.9rem; color:#666;">Sistem akan menampilkan <b>perangkingan 15 program studi</b> dari yang paling sesuai hingga kurang sesuai.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📐 Tentang Metode AHP")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <h4>Analytic Hierarchy Process (AHP)</h4>
        <p>AHP dikembangkan oleh <b>Thomas L. Saaty</b> pada tahun 1970-an. Metode ini menggunakan
        <b>perbandingan berpasangan (pairwise comparison)</b> antar kriteria untuk menentukan bobot prioritas.
        Keunggulan AHP adalah kemampuannya mengukur <b>konsistensi</b> penilaian melalui <i>Consistency Ratio (CR)</i>,
        di mana CR harus < 0.1 agar penilaian dianggap konsisten.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Kriteria yang Digunakan")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    kriteria_df = pd.DataFrame({
        "No": [1, 2, 3, 4, 5, 6],
        "Kriteria": ["Nilai Akademik", "Minat", "Bakat", "Hasil Psikologi", "Motivasi", "Family Income"],
        "Sumber": ["Dataset (Exam Score)", "Input User", "Input User", "Dataset (Peer Influence)", "Dataset (Motivation Level)", "Dataset (Family_Income)"],
        "Tipe": ["Benefit ✅", "Benefit ✅", "Benefit ✅", "Benefit ✅", "Benefit ✅", "Benefit ✅"],
        "Keterangan": [
            "Skor ujian akhir siswa",
            "Bidang minat: Sains, Sosial, Bahasa, Seni, Teknologi",
            "Bakat siswa: Analitis, Komunikasi, Kreatif, Teknis, Leadership",
            "Pengaruh teman sebaya (Positive/Neutral/Negative)",
            "Tingkat motivasi siswa (High/Medium/Low)",
            "Pendapatan keluarga dari dataset (Low/Medium/High) — otomatis dari data siswa"
        ]
    })
    st.dataframe(kriteria_df, use_container_width=True, hide_index=True)


# ============================================================
# HALAMAN 2: DATA & DATASET
# ============================================================
elif halaman == "📊 Data & Dataset":
    st.markdown("""
    <div class="hero-container">
        <h1>📊 Data & Dataset</h1>
        <p>Dataset Student Performance Factors — berisi data performa siswa dan faktor-faktor yang memengaruhinya</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_students']:,}</div>
            <div class="metric-label">Total Data Siswa</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['avg_exam_score']}</div>
            <div class="metric-label">Rata-rata Skor Ujian</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['max_exam_score']}</div>
            <div class="metric-label">Skor Tertinggi</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['min_exam_score']}</div>
            <div class="metric-label">Skor Terendah</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📑 Dataset Mentah", "📈 Data Terproses", "📊 Statistik"])

    with tab1:
        st.markdown("#### Dataset Mentah (Raw Data)")
        st.markdown(f"Menampilkan seluruh **{len(df_raw)}** baris data dari file CSV.")
        # Highlight kolom yang dipakai AHP
        st.markdown("""
        <div class="info-box">
            <h4>Kolom yang digunakan dalam perhitungan AHP</h4>
            <p><b>Exam_Score</b> (Nilai Akademik) · <b>Peer_Influence</b> (Psikologi) · 
            <b>Motivation_Level</b> (Motivasi) · <b>Family_Income</b> (Kriteria Biaya/Income)</p>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(df_raw, use_container_width=True, height=450)

    with tab2:
        st.markdown("#### Dataset Terproses")
        st.markdown("Data yang sudah dikonversi ke numerik untuk perhitungan SPK.")
        display_cols = ['Exam_Score', 'Exam_Score_Normalized', 'Peer_Influence', 'Peer_Influence_Score',
                       'Motivation_Level', 'Motivation_Level_Score', 'Family_Income', 'Family_Income_Score',
                       'Hours_Studied']
        available_cols = [c for c in display_cols if c in df_processed.columns]
        st.dataframe(df_processed[available_cols], use_container_width=True, height=450)

    with tab3:
        st.markdown("#### Statistik Deskriptif")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 📊 Distribusi Tingkat Motivasi")
            motivation_data = stats['motivation_dist']
            motivation_df = pd.DataFrame({
                'Tingkat Motivasi': list(motivation_data.keys()),
                'Jumlah Siswa': list(motivation_data.values())
            })
            st.bar_chart(motivation_df.set_index('Tingkat Motivasi'))

        with col2:
            st.markdown("##### 📊 Distribusi Pengaruh Teman Sebaya")
            peer_data = stats['peer_influence_dist']
            peer_df = pd.DataFrame({
                'Peer Influence': list(peer_data.keys()),
                'Jumlah Siswa': list(peer_data.values())
            })
            st.bar_chart(peer_df.set_index('Peer Influence'))

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 📊 Distribusi Family Income")
            income_data = stats.get('family_income_dist', {})
            if income_data:
                income_df = pd.DataFrame({
                    'Family Income': list(income_data.keys()),
                    'Jumlah Siswa': list(income_data.values())
                })
                st.bar_chart(income_df.set_index('Family Income'))

        with col2:
            st.markdown("##### 📈 Statistik Exam Score")
            st.dataframe(
                df_processed['Exam_Score'].describe().to_frame().T,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# HALAMAN 3: KELOLA DATA (CRUD)
# ============================================================
elif halaman == "✏️ Kelola Data (CRUD)":
    st.markdown("""
    <div class="hero-container">
        <h1>✏️ Kelola Data (CRUD)</h1>
        <p>Tambah, ubah, atau hapus data siswa dari dataset — perubahan akan tersimpan ke file CSV</p>
    </div>
    """, unsafe_allow_html=True)

    # Info kolom AHP
    st.markdown("""
    <div class="info-box">
        <h4>ℹ️ Kolom yang dapat dikelola</h4>
        <p>Data yang dikelola di halaman ini adalah kolom-kolom yang digunakan dalam perhitungan AHP:
        <b>Exam_Score</b>, <b>Motivation_Level</b>, <b>Peer_Influence</b>, <b>Family_Income</b>, 
        <b>Hours_Studied</b>, dan data pendukung lainnya dari dataset.</p>
    </div>
    """, unsafe_allow_html=True)

    crud_tab1, crud_tab2, crud_tab3, crud_tab4 = st.tabs([
        "➕ Tambah Data", "✏️ Edit Data", "🗑️ Hapus Data", "📋 Lihat Semua Data"
    ])

    # ── TAB 1: TAMBAH DATA ──────────────────────────────────────────────
    with crud_tab1:
        st.markdown("#### ➕ Tambah Data Siswa Baru")
        st.markdown('<div class="crud-card crud-add">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📝 Data Akademik**")
            new_exam_score = st.number_input("Exam Score", min_value=0, max_value=100, value=70, key="add_exam")
            new_hours = st.number_input("Hours Studied (jam/minggu)", min_value=0, max_value=50, value=10, key="add_hours")
            new_attendance = st.number_input("Attendance (%)", min_value=0, max_value=100, value=85, key="add_attend")
            new_prev_scores = st.number_input("Previous Scores", min_value=0, max_value=100, value=70, key="add_prev")
            new_sleep = st.number_input("Sleep Hours", min_value=0, max_value=12, value=7, key="add_sleep")
            new_tutoring = st.number_input("Tutoring Sessions", min_value=0, max_value=20, value=1, key="add_tutor")
            new_physical = st.number_input("Physical Activity (jam/minggu)", min_value=0, max_value=20, value=3, key="add_phys")

        with col2:
            st.markdown("**🎯 Data Kriteria AHP**")
            new_motivation = st.selectbox("Motivation Level", ["High", "Medium", "Low"], key="add_motiv")
            new_peer = st.selectbox("Peer Influence", ["Positive", "Neutral", "Negative"], key="add_peer")
            new_family_income = st.selectbox("Family Income", ["Low", "Medium", "High"], key="add_income")

        with col3:
            st.markdown("**👤 Data Demografis**")
            new_parental_inv = st.selectbox("Parental Involvement", ["Low", "Medium", "High"], key="add_par_inv")
            new_resources = st.selectbox("Access to Resources", ["Low", "Medium", "High"], key="add_res")
            new_extracurr = st.selectbox("Extracurricular Activities", ["Yes", "No"], key="add_extra")
            new_internet = st.selectbox("Internet Access", ["Yes", "No"], key="add_inet")
            new_school = st.selectbox("School Type", ["Public", "Private"], key="add_school")
            new_gender = st.selectbox("Gender", ["Male", "Female"], key="add_gender")
            new_learning_dis = st.selectbox("Learning Disabilities", ["No", "Yes"], key="add_ld")
            new_teacher = st.selectbox("Teacher Quality", ["Low", "Medium", "High"], key="add_teacher")
            new_par_edu = st.selectbox("Parental Education Level", ["High School", "College", "Postgraduate"], key="add_par_edu")
            new_distance = st.selectbox("Distance from Home", ["Near", "Moderate", "Far"], key="add_dist")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("✅ Tambah Data Siswa", key="btn_add"):
            new_row = {
                "Hours_Studied": new_hours,
                "Attendance": new_attendance,
                "Parental_Involvement": new_parental_inv,
                "Access_to_Resources": new_resources,
                "Extracurricular_Activities": new_extracurr,
                "Sleep_Hours": new_sleep,
                "Previous_Scores": new_prev_scores,
                "Motivation_Level": new_motivation,
                "Internet_Access": new_internet,
                "Tutoring_Sessions": new_tutoring,
                "Family_Income": new_family_income,
                "Teacher_Quality": new_teacher,
                "School_Type": new_school,
                "Peer_Influence": new_peer,
                "Physical_Activity": new_physical,
                "Learning_Disabilities": new_learning_dis,
                "Parental_Education_Level": new_par_edu,
                "Distance_from_Home": new_distance,
                "Gender": new_gender,
                "Exam_Score": new_exam_score,
            }
            # Pastikan urutan kolom sesuai CSV asli
            new_df = pd.concat([st.session_state.df_raw, pd.DataFrame([new_row])], ignore_index=True)
            save_dataset(new_df, DATASET_PATH)
            reload_data()
            df_raw = st.session_state.df_raw
            df_processed = st.session_state.df_processed
            st.success(f"✅ Data siswa baru berhasil ditambahkan! Total data: {len(st.session_state.df_raw)}")
            st.rerun()

    # ── TAB 2: EDIT DATA ────────────────────────────────────────────────
    with crud_tab2:
        st.markdown("#### ✏️ Edit Data Siswa")

        total_students = len(df_processed)
        edit_idx = st.number_input(
            "Pilih nomor siswa yang ingin diedit (1 - {})".format(total_students),
            min_value=1, max_value=total_students, value=1, step=1, key="edit_idx"
        ) - 1

        actual_idx = df_processed.index[edit_idx]
        row = df_raw.loc[actual_idx]

        st.markdown(f"**Data Siswa #{edit_idx + 1} (Index: {actual_idx})**")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📝 Data Akademik**")
            e_exam = st.number_input("Exam Score", min_value=0, max_value=100,
                                      value=int(row.get("Exam_Score", 70)), key="e_exam")
            e_hours = st.number_input("Hours Studied", min_value=0, max_value=50,
                                       value=int(row.get("Hours_Studied", 10)), key="e_hours")
            e_attend = st.number_input("Attendance (%)", min_value=0, max_value=100,
                                        value=int(row.get("Attendance", 85)), key="e_attend")
            e_prev = st.number_input("Previous Scores", min_value=0, max_value=100,
                                      value=int(row.get("Previous_Scores", 70)), key="e_prev")
            e_sleep = st.number_input("Sleep Hours", min_value=0, max_value=12,
                                       value=int(row.get("Sleep_Hours", 7)), key="e_sleep")
            e_tutor = st.number_input("Tutoring Sessions", min_value=0, max_value=20,
                                       value=int(row.get("Tutoring_Sessions", 1)), key="e_tutor")
            e_phys = st.number_input("Physical Activity", min_value=0, max_value=20,
                                      value=int(row.get("Physical_Activity", 3)), key="e_phys")

        with col2:
            st.markdown("**🎯 Data Kriteria AHP**")
            motiv_opts = ["High", "Medium", "Low"]
            peer_opts = ["Positive", "Neutral", "Negative"]
            income_opts = ["Low", "Medium", "High"]

            cur_motiv = row.get("Motivation_Level", "Medium")
            cur_peer = row.get("Peer_Influence", "Neutral")
            cur_income = row.get("Family_Income", "Medium")

            e_motiv = st.selectbox("Motivation Level", motiv_opts,
                                    index=motiv_opts.index(cur_motiv) if cur_motiv in motiv_opts else 1,
                                    key="e_motiv")
            e_peer = st.selectbox("Peer Influence", peer_opts,
                                   index=peer_opts.index(cur_peer) if cur_peer in peer_opts else 1,
                                   key="e_peer")
            e_income = st.selectbox("Family Income", income_opts,
                                     index=income_opts.index(cur_income) if cur_income in income_opts else 1,
                                     key="e_income")

        with col3:
            st.markdown("**👤 Data Demografis**")
            par_opts = ["Low", "Medium", "High"]
            res_opts = ["Low", "Medium", "High"]
            yn_opts = ["Yes", "No"]
            school_opts = ["Public", "Private"]
            gender_opts = ["Male", "Female"]
            ld_opts = ["No", "Yes"]
            teacher_opts = ["Low", "Medium", "High"]
            par_edu_opts = ["High School", "College", "Postgraduate"]
            dist_opts = ["Near", "Moderate", "Far"]

            def safe_idx(opts, val, default=0):
                return opts.index(val) if val in opts else default

            e_par_inv = st.selectbox("Parental Involvement", par_opts, index=safe_idx(par_opts, row.get("Parental_Involvement", "Medium"), 1), key="e_par_inv")
            e_res = st.selectbox("Access to Resources", res_opts, index=safe_idx(res_opts, row.get("Access_to_Resources", "Medium"), 1), key="e_res")
            e_extra = st.selectbox("Extracurricular", yn_opts, index=safe_idx(yn_opts, row.get("Extracurricular_Activities", "No")), key="e_extra")
            e_inet = st.selectbox("Internet Access", yn_opts, index=safe_idx(yn_opts, row.get("Internet_Access", "Yes")), key="e_inet")
            e_school = st.selectbox("School Type", school_opts, index=safe_idx(school_opts, row.get("School_Type", "Public")), key="e_school")
            e_gender = st.selectbox("Gender", gender_opts, index=safe_idx(gender_opts, row.get("Gender", "Male")), key="e_gender")
            e_ld = st.selectbox("Learning Disabilities", ld_opts, index=safe_idx(ld_opts, row.get("Learning_Disabilities", "No")), key="e_ld")
            e_teacher = st.selectbox("Teacher Quality", teacher_opts, index=safe_idx(teacher_opts, row.get("Teacher_Quality", "Medium"), 1), key="e_teacher")
            e_par_edu = st.selectbox("Parental Education", par_edu_opts, index=safe_idx(par_edu_opts, row.get("Parental_Education_Level", "High School")), key="e_par_edu")
            e_dist = st.selectbox("Distance from Home", dist_opts, index=safe_idx(dist_opts, row.get("Distance_from_Home", "Near")), key="e_dist")

        if st.button("💾 Simpan Perubahan", key="btn_edit"):
            st.session_state.df_raw.at[actual_idx, "Exam_Score"] = e_exam
            st.session_state.df_raw.at[actual_idx, "Hours_Studied"] = e_hours
            st.session_state.df_raw.at[actual_idx, "Attendance"] = e_attend
            st.session_state.df_raw.at[actual_idx, "Previous_Scores"] = e_prev
            st.session_state.df_raw.at[actual_idx, "Sleep_Hours"] = e_sleep
            st.session_state.df_raw.at[actual_idx, "Tutoring_Sessions"] = e_tutor
            st.session_state.df_raw.at[actual_idx, "Physical_Activity"] = e_phys
            st.session_state.df_raw.at[actual_idx, "Motivation_Level"] = e_motiv
            st.session_state.df_raw.at[actual_idx, "Peer_Influence"] = e_peer
            st.session_state.df_raw.at[actual_idx, "Family_Income"] = e_income
            st.session_state.df_raw.at[actual_idx, "Parental_Involvement"] = e_par_inv
            st.session_state.df_raw.at[actual_idx, "Access_to_Resources"] = e_res
            st.session_state.df_raw.at[actual_idx, "Extracurricular_Activities"] = e_extra
            st.session_state.df_raw.at[actual_idx, "Internet_Access"] = e_inet
            st.session_state.df_raw.at[actual_idx, "School_Type"] = e_school
            st.session_state.df_raw.at[actual_idx, "Gender"] = e_gender
            st.session_state.df_raw.at[actual_idx, "Learning_Disabilities"] = e_ld
            st.session_state.df_raw.at[actual_idx, "Teacher_Quality"] = e_teacher
            st.session_state.df_raw.at[actual_idx, "Parental_Education_Level"] = e_par_edu
            st.session_state.df_raw.at[actual_idx, "Distance_from_Home"] = e_dist

            save_dataset(st.session_state.df_raw, DATASET_PATH)
            reload_data()
            st.success(f"✅ Data Siswa #{edit_idx + 1} berhasil diperbarui!")
            st.rerun()

    # ── TAB 3: HAPUS DATA ───────────────────────────────────────────────
    with crud_tab3:
        st.markdown("#### 🗑️ Hapus Data Siswa")

        total_students = len(df_processed)

        if total_students == 0:
            st.warning("⚠️ Tidak ada data siswa untuk dihapus.")
        else:
            del_idx = st.number_input(
                "Pilih nomor siswa yang ingin dihapus (1 - {})".format(total_students),
                min_value=1, max_value=total_students, value=1, step=1, key="del_idx"
            ) - 1

            actual_del_idx = df_processed.index[del_idx]
            del_row = df_raw.loc[actual_del_idx]

            st.markdown(f"**Preview data yang akan dihapus — Siswa #{del_idx + 1}:**")
            preview_df = pd.DataFrame([{
                "Exam Score": del_row.get("Exam_Score"),
                "Motivation": del_row.get("Motivation_Level"),
                "Peer Influence": del_row.get("Peer_Influence"),
                "Family Income": del_row.get("Family_Income"),
                "Hours Studied": del_row.get("Hours_Studied"),
            }])
            st.dataframe(preview_df, use_container_width=True, hide_index=True)

            st.warning("⚠️ Tindakan ini tidak dapat dibatalkan! Pastikan Anda memilih siswa yang benar.")

            col1, col2 = st.columns([1, 3])
            with col1:
                confirm_del = st.checkbox("Saya yakin ingin menghapus data ini", key="confirm_del")
            with col2:
                if st.button("🗑️ Hapus Data", key="btn_del", disabled=not confirm_del):
                    new_raw = st.session_state.df_raw.drop(index=actual_del_idx).reset_index(drop=True)
                    save_dataset(new_raw, DATASET_PATH)
                    reload_data()
                    st.success(f"✅ Data Siswa #{del_idx + 1} berhasil dihapus! Sisa data: {len(st.session_state.df_raw)}")
                    st.rerun()

    # ── TAB 4: LIHAT SEMUA DATA ─────────────────────────────────────────
    with crud_tab4:
        st.markdown("#### 📋 Semua Data Siswa")
        st.markdown(f"Total: **{len(df_raw)}** siswa")

        # Filter berdasarkan kolom AHP
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_motiv = st.multiselect("Filter Motivation Level", ["High", "Medium", "Low"], default=[], key="filter_motiv")
        with col2:
            filter_peer = st.multiselect("Filter Peer Influence", ["Positive", "Neutral", "Negative"], default=[], key="filter_peer")
        with col3:
            filter_income = st.multiselect("Filter Family Income", ["Low", "Medium", "High"], default=[], key="filter_income")

        filtered_df = df_raw.copy()
        if filter_motiv:
            filtered_df = filtered_df[filtered_df["Motivation_Level"].isin(filter_motiv)]
        if filter_peer:
            filtered_df = filtered_df[filtered_df["Peer_Influence"].isin(filter_peer)]
        if filter_income:
            filtered_df = filtered_df[filtered_df["Family_Income"].isin(filter_income)]

        st.markdown(f"Menampilkan **{len(filtered_df)}** data")

        # Highlight kolom AHP
        ahp_cols = ["Exam_Score", "Motivation_Level", "Peer_Influence", "Family_Income", "Hours_Studied"]
        available_ahp = [c for c in ahp_cols if c in filtered_df.columns]
        other_cols = [c for c in filtered_df.columns if c not in ahp_cols]
        ordered_cols = available_ahp + other_cols
        st.dataframe(filtered_df[ordered_cols], use_container_width=True, height=500)


# ============================================================
# HALAMAN 4: HITUNG SPK (AHP)
# ============================================================
elif halaman == "🧮 Hitung SPK (AHP)":
    st.markdown("""
    <div class="hero-container">
        <h1>🧮 Perhitungan SPK — Metode AHP</h1>
        <p>Tentukan parameter input dan bobot kriteria, lalu klik tombol hitung untuk mendapatkan rekomendasi program studi terbaik</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- INPUT SECTION ----
    st.markdown("### 📝 Input Parameter")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Row 1: Student selection + dynamic inputs (hanya minat & bakat, biaya sudah dari dataset)
    col1, col2, col3 = st.columns(3)

    with col1:
        student_labels = [get_student_label(df_processed, i) for i in range(len(df_processed))]
        selected_idx = st.selectbox(
            "👤 Pilih Data Siswa",
            range(len(df_processed)),
            format_func=lambda i: student_labels[i],
            help="Pilih siswa dari dataset untuk dianalisis"
        )

    with col2:
        selected_minat = st.selectbox(
            "💡 Pilih Minat",
            MINAT_OPTIONS,
            help="Bidang minat siswa"
        )

    with col3:
        selected_bakat = st.selectbox(
            "⭐ Pilih Bakat",
            BAKAT_OPTIONS,
            help="Bakat utama siswa"
        )

    # Show selected student info
    student_data = get_student_data(df_processed, df_processed.index[selected_idx])
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <h4>📋 Data Siswa Terpilih</h4>
        <p>Family Income diambil otomatis dari dataset — tidak perlu diinput secara manual</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Exam Score", f"{student_data['exam_score']}")
    with col2:
        st.metric("Peer Influence", student_data['peer_influence'])
    with col3:
        st.metric("Motivation Level", student_data['motivation_level'])
    with col4:
        st.metric("Family Income", student_data['family_income'])
    with col5:
        st.metric("Hours Studied", f"{student_data['hours_studied']} jam/minggu")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- BOBOT KRITERIA ----
    st.markdown("### ⚖️ Bobot Kepentingan Kriteria (Skala 1-9)")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <h4>Skala Saaty</h4>
        <p><b>1</b> = Sama penting &nbsp;|&nbsp; <b>3</b> = Sedikit lebih penting &nbsp;|&nbsp; <b>5</b> = Lebih penting &nbsp;|&nbsp; <b>7</b> = Sangat penting &nbsp;|&nbsp; <b>9</b> = Mutlak penting</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        w_nilai = st.slider("📝 Nilai Akademik", 1, 9, 5, key="w_nilai")
        w_minat = st.slider("💡 Minat", 1, 9, 7, key="w_minat")
    with col2:
        w_bakat = st.slider("⭐ Bakat", 1, 9, 6, key="w_bakat")
        w_psikologi = st.slider("🧠 Hasil Psikologi", 1, 9, 4, key="w_psikologi")
    with col3:
        w_motivasi = st.slider("🔥 Motivasi", 1, 9, 5, key="w_motivasi")
        w_family_income = st.slider("💰 Family Income", 1, 9, 3, key="w_family_income",
                                     help="Seberapa penting pertimbangan pendapatan keluarga")

    st.markdown("<br>", unsafe_allow_html=True)

    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        hitung_btn = st.button("🚀 Hitung Rekomendasi Program Studi", use_container_width=True)

    # ---- PROSES AHP ----
    if hitung_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        weights = [w_nilai, w_minat, w_bakat, w_psikologi, w_motivasi, w_family_income]
        criteria_names = ['nilai', 'minat', 'bakat', 'psikologi', 'motivasi', 'family_income']
        criteria_types = ['benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit']

        with st.spinner("⏳ Menghitung AHP..."):
            # Step 1: Pairwise Comparison Matrix
            st.markdown("### 📐 Langkah 1: Matriks Perbandingan Berpasangan")
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            pairwise = create_pairwise_matrix(weights)
            criteria_labels = ["Nilai", "Minat", "Bakat", "Psikologi", "Motivasi", "Family Income"]
            pairwise_df = pd.DataFrame(
                np.round(pairwise, 4),
                index=criteria_labels,
                columns=criteria_labels
            )
            st.dataframe(pairwise_df, use_container_width=True)

            # Step 2: Priority Vector & Consistency
            st.markdown("### 📊 Langkah 2: Bobot Prioritas & Konsistensi")
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            priority = calculate_priority_vector(pairwise)
            cr, ci, lambda_max, is_consistent = calculate_consistency_ratio(pairwise)

            if is_consistent:
                st.markdown(f"""
                <div class="cr-consistent">
                    ✅ KONSISTEN — CR = {cr:.4f} (< 0.10) &nbsp;|&nbsp; CI = {ci:.4f} &nbsp;|&nbsp; λmax = {lambda_max:.4f}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="cr-inconsistent">
                    ❌ TIDAK KONSISTEN — CR = {cr:.4f} (≥ 0.10) &nbsp;|&nbsp; CI = {ci:.4f} &nbsp;|&nbsp; λmax = {lambda_max:.4f}
                    <br><small>Silakan sesuaikan bobot agar lebih konsisten</small>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            priority_df = pd.DataFrame({
                'Kriteria': criteria_labels,
                'Bobot': np.round(priority, 4)
            })
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("##### 📋 Tabel Bobot Prioritas")
                st.dataframe(priority_df, use_container_width=True, hide_index=True)
            with col2:
                st.markdown("##### 📊 Grafik Bobot Prioritas")
                st.bar_chart(priority_df.set_index('Kriteria'))

            # Step 3: Scoring — AHP Murni
            st.markdown("### 🏆 Langkah 3: Prioritas Lokal Alternatif (AHP Murni)")
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            st.info(
                "**AHP Murni**: Setiap program studi dibandingkan secara berpasangan "
                "untuk setiap kriteria. Family Income diambil otomatis dari data siswa yang dipilih "
                f"(Family Income: **{student_data['family_income']}**)."
            )

            # Get scores — family_income sekarang dari student_data, bukan input user
            prodi_scores = get_all_prodi_scores(selected_minat, selected_bakat, student_data['family_income'])

            criteria_scores = {}
            for prodi in DAFTAR_PRODI:
                criteria_scores[prodi] = {
                    'nilai': student_data['exam_score_normalized'],
                    'minat': prodi_scores[prodi]['minat'],
                    'bakat': prodi_scores[prodi]['bakat'],
                    'psikologi': student_data['peer_influence_score'],
                    'motivasi': student_data['motivation_level_score'],
                    'family_income': prodi_scores[prodi]['family_income'],
                }

            local_tables = get_local_priority_tables(
                criteria_scores, criteria_names, criteria_types
            )
            criteria_labels_map = {
                'nilai': 'Nilai', 'minat': 'Minat', 'bakat': 'Bakat',
                'psikologi': 'Psikologi', 'motivasi': 'Motivasi', 'family_income': 'Family Income'
            }

            with st.expander("📊 Lihat Vektor Prioritas Lokal per Kriteria (Detail AHP Murni)", expanded=False):
                for crit_name in criteria_names:
                    tbl = local_tables[crit_name]
                    st.markdown(f"**Kriteria: {criteria_labels_map.get(crit_name, crit_name)}**")
                    pv_df = pd.DataFrame({
                        'Program Studi': tbl['alternative_names'],
                        'Prioritas Lokal': np.round(tbl['priority'], 4)
                    })
                    st.dataframe(pv_df, use_container_width=True, hide_index=True)
                    st.markdown("---")

            final_scores = calculate_final_scores(
                criteria_scores, priority, criteria_names, criteria_types
            )
            ranking = rank_alternatives(final_scores)

            # Step 4: Display ranking
            st.markdown("### 🏅 Langkah 4: Hasil Perangkingan Program Studi")
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            for rank, name, score in ranking:
                if rank == 1:
                    css_class = "rank-gold"
                    medal = "🥇"
                elif rank == 2:
                    css_class = "rank-silver"
                    medal = "🥈"
                elif rank == 3:
                    css_class = "rank-bronze"
                    medal = "🥉"
                else:
                    css_class = "rank-normal"
                    medal = ""

                desc = PRODI_DESCRIPTIONS.get(name, "")
                st.markdown(f"""
                <div class="rank-card {css_class}">
                    <div class="rank-number">#{rank}</div>
                    <div class="rank-info">
                        <h3>{medal} {name}</h3>
                        <div class="rank-score">Skor: {score:.4f} — {desc}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("### 📋 Tabel Hasil Perangkingan")
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            result_data = []
            for rank, name, score in ranking:
                scores = criteria_scores[name]
                result_data.append({
                    "Peringkat": rank,
                    "Program Studi": name,
                    "Skor Akhir": round(score, 4),
                    "Nilai": round(scores['nilai'], 2),
                    "Minat": scores['minat'],
                    "Bakat": scores['bakat'],
                    "Psikologi": scores['psikologi'],
                    "Motivasi": scores['motivasi'],
                    "Family Income": scores['family_income'],
                })

            result_df = pd.DataFrame(result_data)
            st.dataframe(result_df, use_container_width=True, hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)
            top3 = ranking[:3]
            st.markdown("""
            <div class="info-box">
                <h4>🎯 Ringkasan Rekomendasi</h4>
            </div>
            """, unsafe_allow_html=True)
            st.success(f"""
            **Top 3 Rekomendasi Program Studi untuk Siswa #{selected_idx + 1}:**

            🥇 **{top3[0][1]}** — Skor: {top3[0][2]:.4f}

            🥈 **{top3[1][1]}** — Skor: {top3[1][2]:.4f}

            🥉 **{top3[2][1]}** — Skor: {top3[2][2]:.4f}

            *Minat: {selected_minat} | Bakat: {selected_bakat} | Family Income: {student_data['family_income']}*
            """)


# ============================================================
# HALAMAN 5: PROFIL KELOMPOK
# ============================================================
elif halaman == "👥 Profil Kelompok":
    st.markdown("""
    <div class="hero-container">
        <h1>👥 Profil Kelompok</h1>
        <p>Proyek Akhir Praktikum SCPK 2025/2026</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="profile-card">
            <div style="font-size: 4rem; margin-bottom: 1rem;">👨‍💻</div>
            <h2>Iqbal Wahyu Pratama</h2>
            <p style="font-size: 1.2rem; font-weight: 500;">NIM: 123240265</p>
            <hr style="border-color: rgba(255,255,255,0.2); margin: 1.5rem 0;">
            <p>Proyek Akhir Praktikum SCPK</p>
            <p>Tahun Akademik 2025/2026</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📄 Deskripsi Proyek")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <h4>Sistem Perekomendasian Jurusan / Program Studi</h4>
        <p>Sistem untuk membantu siswa SMA/SMK sederajat dalam pemilihan jurusan kuliah yang tepat
        berdasarkan nilai raport, minat, bakat, dan hasil psikologi. Sistem ini menggunakan
        metode <b>Analytic Hierarchy Process (AHP)</b> sebagai metode Sistem Pendukung Keputusan (SPK).</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🛠️ Teknologi yang Digunakan")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">🐍</div>
            <h4>Python</h4>
            <p style="font-size:0.9rem; color:#666;">Bahasa pemrograman utama</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">📊</div>
            <h4>Streamlit</h4>
            <p style="font-size:0.9rem; color:#666;">Framework GUI interaktif</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">📐</div>
            <h4>AHP (Saaty)</h4>
            <p style="font-size:0.9rem; color:#666;">Metode Sistem Pendukung Keputusan</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📚 Sumber Dataset")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <h4>Student Performance Factors</h4>
        <p><b>Sumber:</b> Kaggle — <a href="https://www.kaggle.com/datasets/lainguyn123/student-performance-factors" target="_blank">https://www.kaggle.com/datasets/lainguyn123/student-performance-factors</a></p>
        <p><b>Lisensi:</b> CC0: Public Domain</p>
        <p><b>Deskripsi:</b> Dataset berisi faktor-faktor yang memengaruhi performa akademik siswa, termasuk kebiasaan belajar, kehadiran, keterlibatan orang tua, dan aspek lainnya.</p>
    </div>
    """, unsafe_allow_html=True)
