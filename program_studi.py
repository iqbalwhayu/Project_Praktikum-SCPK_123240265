from typing import Dict
# =============================================================================
# 1. DAFTAR PROGRAM STUDI
# =============================================================================
# 15 program studi umum di universitas Indonesia
DAFTAR_PRODI: list[str] = [
    "Teknik Informatika",
    "Sistem Informasi",
    "Kedokteran",
    "Farmasi",
    "Hukum",
    "Manajemen",
    "Akuntansi",
    "Psikologi",
    "Teknik Sipil",
    "Teknik Elektro",
    "Ilmu Komunikasi",
    "Desain Komunikasi Visual (DKV)",
    "Pendidikan Guru (PGSD)",
    "Arsitektur",
    "Sastra Inggris",
]

# =============================================================================
# 2. OPSI MINAT (Kategori Ketertarikan)
# =============================================================================
MINAT_OPTIONS: list[str] = [
    "Sains",
    "Sosial",
    "Bahasa",
    "Seni",
    "Teknologi",
]

# =============================================================================
# 3. OPSI BAKAT (Kategori Kemampuan)
# =============================================================================
BAKAT_OPTIONS: list[str] = [
    "Analitis",
    "Komunikasi",
    "Kreatif",
    "Teknis",
    "Leadership",
]

# =============================================================================
# 4. OPSI BIAYA (Kisaran Anggaran)
# =============================================================================
BIAYA_OPTIONS: list[str] = [
    "Rendah",
    "Sedang",
    "Tinggi",
]

# =============================================================================
# 5. MATRIKS MINAT - PROGRAM STUDI (Skor 1-5)
# =============================================================================
# Setiap minat dipetakan ke skor kompatibilitas untuk masing-masing prodi.
# Skor 5 = sangat cocok, 1 = tidak cocok.
MINAT_PRODI_MATRIX: Dict[str, Dict[str, int]] = {
    "Teknologi": {
        "Teknik Informatika": 5,
        "Sistem Informasi": 5,
        "Kedokteran": 1,
        "Farmasi": 2,
        "Hukum": 1,
        "Manajemen": 2,
        "Akuntansi": 2,
        "Psikologi": 1,
        "Teknik Sipil": 4,
        "Teknik Elektro": 5,
        "Ilmu Komunikasi": 2,
        "Desain Komunikasi Visual (DKV)": 3,
        "Pendidikan Guru (PGSD)": 1,
        "Arsitektur": 3,
        "Sastra Inggris": 1,
    },
    "Sains": {
        "Teknik Informatika": 4,
        "Sistem Informasi": 3,
        "Kedokteran": 5,
        "Farmasi": 5,
        "Hukum": 1,
        "Manajemen": 1,
        "Akuntansi": 2,
        "Psikologi": 3,
        "Teknik Sipil": 3,
        "Teknik Elektro": 4,
        "Ilmu Komunikasi": 1,
        "Desain Komunikasi Visual (DKV)": 1,
        "Pendidikan Guru (PGSD)": 2,
        "Arsitektur": 2,
        "Sastra Inggris": 1,
    },
    "Sosial": {
        "Teknik Informatika": 1,
        "Sistem Informasi": 2,
        "Kedokteran": 2,
        "Farmasi": 1,
        "Hukum": 5,
        "Manajemen": 5,
        "Akuntansi": 4,
        "Psikologi": 5,
        "Teknik Sipil": 1,
        "Teknik Elektro": 1,
        "Ilmu Komunikasi": 5,
        "Desain Komunikasi Visual (DKV)": 2,
        "Pendidikan Guru (PGSD)": 5,
        "Arsitektur": 1,
        "Sastra Inggris": 3,
    },
    "Bahasa": {
        "Teknik Informatika": 1,
        "Sistem Informasi": 1,
        "Kedokteran": 1,
        "Farmasi": 1,
        "Hukum": 3,
        "Manajemen": 2,
        "Akuntansi": 1,
        "Psikologi": 3,
        "Teknik Sipil": 1,
        "Teknik Elektro": 1,
        "Ilmu Komunikasi": 4,
        "Desain Komunikasi Visual (DKV)": 2,
        "Pendidikan Guru (PGSD)": 4,
        "Arsitektur": 1,
        "Sastra Inggris": 5,
    },
    "Seni": {
        "Teknik Informatika": 1,
        "Sistem Informasi": 1,
        "Kedokteran": 1,
        "Farmasi": 1,
        "Hukum": 1,
        "Manajemen": 1,
        "Akuntansi": 1,
        "Psikologi": 2,
        "Teknik Sipil": 1,
        "Teknik Elektro": 1,
        "Ilmu Komunikasi": 4,
        "Desain Komunikasi Visual (DKV)": 5,
        "Pendidikan Guru (PGSD)": 2,
        "Arsitektur": 5,
        "Sastra Inggris": 3,
    },
}

# =============================================================================
# 6. MATRIKS BAKAT - PROGRAM STUDI (Skor 1-5)
# =============================================================================
# Setiap bakat dipetakan ke skor kompatibilitas untuk masing-masing prodi.
BAKAT_PRODI_MATRIX: Dict[str, Dict[str, int]] = {
    "Analitis": {
        "Teknik Informatika": 5,
        "Sistem Informasi": 4,
        "Kedokteran": 5,
        "Farmasi": 5,
        "Hukum": 3,
        "Manajemen": 3,
        "Akuntansi": 5,
        "Psikologi": 4,
        "Teknik Sipil": 4,
        "Teknik Elektro": 5,
        "Ilmu Komunikasi": 2,
        "Desain Komunikasi Visual (DKV)": 1,
        "Pendidikan Guru (PGSD)": 2,
        "Arsitektur": 3,
        "Sastra Inggris": 2,
    },
    "Komunikasi": {
        "Teknik Informatika": 2,
        "Sistem Informasi": 3,
        "Kedokteran": 3,
        "Farmasi": 2,
        "Hukum": 5,
        "Manajemen": 4,
        "Akuntansi": 2,
        "Psikologi": 5,
        "Teknik Sipil": 1,
        "Teknik Elektro": 1,
        "Ilmu Komunikasi": 5,
        "Desain Komunikasi Visual (DKV)": 3,
        "Pendidikan Guru (PGSD)": 5,
        "Arsitektur": 2,
        "Sastra Inggris": 4,
    },
    "Kreatif": {
        "Teknik Informatika": 3,
        "Sistem Informasi": 2,
        "Kedokteran": 1,
        "Farmasi": 1,
        "Hukum": 1,
        "Manajemen": 2,
        "Akuntansi": 1,
        "Psikologi": 2,
        "Teknik Sipil": 2,
        "Teknik Elektro": 2,
        "Ilmu Komunikasi": 4,
        "Desain Komunikasi Visual (DKV)": 5,
        "Pendidikan Guru (PGSD)": 3,
        "Arsitektur": 5,
        "Sastra Inggris": 4,
    },
    "Teknis": {
        "Teknik Informatika": 5,
        "Sistem Informasi": 4,
        "Kedokteran": 2,
        "Farmasi": 3,
        "Hukum": 1,
        "Manajemen": 1,
        "Akuntansi": 2,
        "Psikologi": 1,
        "Teknik Sipil": 5,
        "Teknik Elektro": 5,
        "Ilmu Komunikasi": 1,
        "Desain Komunikasi Visual (DKV)": 3,
        "Pendidikan Guru (PGSD)": 1,
        "Arsitektur": 4,
        "Sastra Inggris": 1,
    },
    "Leadership": {
        "Teknik Informatika": 2,
        "Sistem Informasi": 3,
        "Kedokteran": 3,
        "Farmasi": 2,
        "Hukum": 4,
        "Manajemen": 5,
        "Akuntansi": 3,
        "Psikologi": 3,
        "Teknik Sipil": 2,
        "Teknik Elektro": 2,
        "Ilmu Komunikasi": 4,
        "Desain Komunikasi Visual (DKV)": 2,
        "Pendidikan Guru (PGSD)": 4,
        "Arsitektur": 2,
        "Sastra Inggris": 1,
    },
}

# =============================================================================
# 7. BIAYA PROGRAM STUDI (Level Biaya Kuliah)
# =============================================================================
# Pemetaan setiap prodi ke level biaya kuliahnya
BIAYA_PRODI: Dict[str, str] = {
    "Teknik Informatika": "Tinggi",
    "Sistem Informasi": "Sedang",
    "Kedokteran": "Tinggi",
    "Farmasi": "Tinggi",
    "Hukum": "Rendah",
    "Manajemen": "Sedang",
    "Akuntansi": "Rendah",
    "Psikologi": "Sedang",
    "Teknik Sipil": "Sedang",
    "Teknik Elektro": "Sedang",
    "Ilmu Komunikasi": "Rendah",
    "Desain Komunikasi Visual (DKV)": "Sedang",
    "Pendidikan Guru (PGSD)": "Rendah",
    "Arsitektur": "Tinggi",
    "Sastra Inggris": "Rendah",
}

# =============================================================================
# 8. MATRIKS KOMPATIBILITAS BIAYA
# =============================================================================
# Skor kompatibilitas antara anggaran mahasiswa dan biaya prodi.
# Kunci luar = anggaran mahasiswa, kunci dalam = biaya prodi.
# Contoh: anggaran 'Rendah' vs biaya prodi 'Tinggi' → skor 1 (tidak cocok).
BIAYA_COMPATIBILITY: Dict[str, Dict[str, int]] = {
    "Rendah": {"Rendah": 5, "Sedang": 2, "Tinggi": 1},
    "Sedang": {"Rendah": 5, "Sedang": 4, "Tinggi": 2},
    "Tinggi": {"Rendah": 5, "Sedang": 5, "Tinggi": 5},
}

# =============================================================================
# 9. FUNGSI-FUNGSI UTILITAS
# =============================================================================


def get_minat_score(minat: str, prodi: str) -> int:
    """Mendapatkan skor kompatibilitas antara minat dan program studi (1-5).

    Args:
        minat: Kategori minat mahasiswa (salah satu dari MINAT_OPTIONS).
        prodi: Nama program studi (salah satu dari DAFTAR_PRODI).

    Returns:
        Skor kompatibilitas 1-5 (5 = sangat cocok, 1 = tidak cocok).
    """
    return MINAT_PRODI_MATRIX[minat][prodi]


def get_bakat_score(bakat: str, prodi: str) -> int:
    """Mendapatkan skor kompatibilitas antara bakat dan program studi (1-5).

    Args:
        bakat: Kategori bakat mahasiswa (salah satu dari BAKAT_OPTIONS).
        prodi: Nama program studi (salah satu dari DAFTAR_PRODI).

    Returns:
        Skor kompatibilitas 1-5 (5 = sangat cocok, 1 = tidak cocok).
    """
    return BAKAT_PRODI_MATRIX[bakat][prodi]


def get_biaya_score(user_budget: str, prodi: str) -> int:
    """Mendapatkan skor kompatibilitas biaya (1-5).

    Semakin tinggi ketidakcocokan anggaran (budget rendah vs biaya tinggi),
    semakin rendah skornya.

    Args:
        user_budget: Anggaran mahasiswa ('Rendah', 'Sedang', atau 'Tinggi').
        prodi: Nama program studi (salah satu dari DAFTAR_PRODI).

    Returns:
        Skor kompatibilitas biaya 1-5.
    """
    prodi_cost = BIAYA_PRODI[prodi]
    return BIAYA_COMPATIBILITY[user_budget][prodi_cost]


def get_all_prodi_scores(minat: str, bakat: str, biaya: str) -> Dict[str, Dict[str, int]]:
    """Mendapatkan skor minat, bakat, dan biaya untuk semua 15 program studi.

    Args:
        minat: Kategori minat mahasiswa (salah satu dari MINAT_OPTIONS).
        bakat: Kategori bakat mahasiswa (salah satu dari BAKAT_OPTIONS).
        biaya: Anggaran mahasiswa ('Rendah', 'Sedang', atau 'Tinggi').

    Returns:
        Dictionary dengan nama prodi sebagai key dan dictionary skor
        {'minat': int, 'bakat': int, 'biaya': int} sebagai value.
    """
    results: Dict[str, Dict[str, int]] = {}
    for prodi in DAFTAR_PRODI:
        results[prodi] = {
            "minat": get_minat_score(minat, prodi),
            "bakat": get_bakat_score(bakat, prodi),
            "biaya": get_biaya_score(biaya, prodi),
        }
    return results


#DESKRIPSI PROGRAM STUDI
PRODI_DESCRIPTIONS: Dict[str, str] = {
    "Teknik Informatika": (
        "Mempelajari pengembangan perangkat lunak, algoritma, kecerdasan buatan, "
        "dan teknologi informasi secara mendalam."
    ),
    "Sistem Informasi": (
        "Menggabungkan ilmu komputer dan manajemen bisnis untuk merancang serta "
        "mengelola sistem informasi organisasi."
    ),
    "Kedokteran": (
        "Mempelajari ilmu kesehatan manusia, diagnosis penyakit, dan penanganan "
        "medis untuk menjadi dokter profesional."
    ),
    "Farmasi": (
        "Mempelajari ilmu obat-obatan, formulasi, dan distribusi farmasi untuk "
        "mendukung pelayanan kesehatan masyarakat."
    ),
    "Hukum": (
        "Mempelajari sistem hukum, peraturan perundang-undangan, dan praktik "
        "peradilan di Indonesia maupun internasional."
    ),
    "Manajemen": (
        "Mempelajari pengelolaan organisasi, strategi bisnis, pemasaran, dan "
        "keuangan perusahaan."
    ),
    "Akuntansi": (
        "Mempelajari pencatatan, pelaporan, dan analisis keuangan untuk "
        "mendukung pengambilan keputusan bisnis."
    ),
    "Psikologi": (
        "Mempelajari perilaku manusia, proses mental, dan penerapan ilmu "
        "psikologi dalam berbagai bidang kehidupan."
    ),
    "Teknik Sipil": (
        "Mempelajari perencanaan, perancangan, dan pembangunan infrastruktur "
        "seperti jalan, jembatan, dan gedung."
    ),
    "Teknik Elektro": (
        "Mempelajari sistem kelistrikan, elektronika, telekomunikasi, dan "
        "teknologi tenaga listrik."
    ),
    "Ilmu Komunikasi": (
        "Mempelajari teori dan praktik komunikasi massa, jurnalistik, "
        "hubungan masyarakat, dan media digital."
    ),
    "Desain Komunikasi Visual (DKV)": (
        "Mempelajari seni desain grafis, multimedia, dan komunikasi visual "
        "untuk menyampaikan pesan secara kreatif."
    ),
    "Pendidikan Guru (PGSD)": (
        "Mempelajari ilmu pendidikan dan metode pengajaran untuk menjadi "
        "guru profesional di sekolah dasar."
    ),
    "Arsitektur": (
        "Mempelajari perancangan bangunan dan ruang yang fungsional, estetis, "
        "dan berkelanjutan."
    ),
    "Sastra Inggris": (
        "Mempelajari bahasa, sastra, dan budaya Inggris serta keterampilan "
        "linguistik untuk karir global."
    ),
}
