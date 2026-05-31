
import pandas as pd


#Konstanta pemetaan nilai kategorikal ke numerik
PEER_INFLUENCE_MAP: dict[str, int] = {
    "Positive": 3,
    "Neutral": 2,
    "Negative": 1,
}

MOTIVATION_LEVEL_MAP: dict[str, int] = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
}

# Kolom-kolom wajib yang harus ada di dataset
REQUIRED_COLUMNS: list[str] = [
    "Exam_Score",
    "Peer_Influence",
    "Motivation_Level",
    "Hours_Studied",
]


#Fungsi-fungsi utama 


def load_dataset(filepath: str) -> pd.DataFrame:
    """Memuat dataset dari file CSV dan memvalidasi kolom yang diperlukan.

    Fungsi ini membaca file CSV menggunakan pandas, lalu memeriksa apakah
    semua kolom wajib (Exam_Score, Peer_Influence, Motivation_Level,
    Hours_Studied) tersedia di dalam dataset.

    Parameters
    ----------
    filepath : str
        Path lengkap menuju file CSV yang akan dimuat.

    Returns
    -------
    pd.DataFrame
        DataFrame lengkap hasil pembacaan file CSV.

    Raises
    ------
    FileNotFoundError
        Jika file CSV tidak ditemukan pada path yang diberikan.
    ValueError
        Jika satu atau lebih kolom wajib tidak ditemukan di dalam dataset.
    """
    df: pd.DataFrame = pd.read_csv(filepath)

    # Validasi keberadaan kolom-kolom wajib
    missing_columns: list[str] = [
        col for col in REQUIRED_COLUMNS if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Kolom berikut tidak ditemukan dalam dataset: {', '.join(missing_columns)}. "
            f"Kolom yang tersedia: {', '.join(df.columns.tolist())}"
        )

    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Memproses DataFrame dengan menambahkan kolom-kolom turunan baru.

    Kolom baru yang ditambahkan:
    - ``Peer_Influence_Score``  : Konversi Peer_Influence ke nilai numerik (1-3).
    - ``Motivation_Level_Score``: Konversi Motivation_Level ke nilai numerik (1-3).
    - ``Exam_Score_Normalized`` : Normalisasi Exam_Score ke skala 1-5.

    Nilai yang hilang (NaN) pada kolom kategorikal akan diisi dengan nilai
    tengah (2) setelah pemetaan, sedangkan Exam_Score yang kosong akan
    dihapus (drop) agar normalisasi tetap valid.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame asli hasil dari ``load_dataset()``.

    Returns
    -------
    pd.DataFrame
        Salinan DataFrame yang telah diproses dengan kolom-kolom tambahan.
    """
    #Bekerja pada salinan agar DataFrame asli tidak berubah
    processed: pd.DataFrame = df.copy()

    # Hapus baris yang tidak memiliki Exam_Score karena tidak bisa dinormalisasi
    processed = processed.dropna(subset=["Exam_Score"])

    # ── Konversi Peer_Influence ke skor numerik ──────────────────────────
    processed["Peer_Influence_Score"] = (
        processed["Peer_Influence"]
        .map(PEER_INFLUENCE_MAP)
        .fillna(2)  # Nilai default: Neutral (2)
        .astype(int)
    )

    # ── Konversi Motivation_Level ke skor numerik ────────────────────────
    processed["Motivation_Level_Score"] = (
        processed["Motivation_Level"]
        .map(MOTIVATION_LEVEL_MAP)
        .fillna(2)  # Nilai default: Medium (2)
        .astype(int)
    )

    # ── Normalisasi Exam_Score ke skala 1-5 ──────────────────────────────
    # Formula: 1 + (value - min) / (max - min) * 4
    exam_min: float = processed["Exam_Score"].min()
    exam_max: float = processed["Exam_Score"].max()

    if exam_max == exam_min:
        # Semua nilai sama → tetapkan ke tengah skala (3.0)
        processed["Exam_Score_Normalized"] = 3.0
    else:
        processed["Exam_Score_Normalized"] = (
            1 + (processed["Exam_Score"] - exam_min) / (exam_max - exam_min) * 4
        ).round(4)

    return processed


def get_student_data(df: pd.DataFrame, index: int) -> dict:
    """Mengambil data seorang siswa berdasarkan indeks DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame yang sudah diproses (hasil dari ``preprocess_data()``).
    index : int
        Nomor indeks baris di dalam DataFrame.

    Returns
    -------
    dict
        Dictionary berisi informasi lengkap siswa dengan kunci:
        ``exam_score``, ``exam_score_normalized``, ``peer_influence``,
        ``peer_influence_score``, ``motivation_level``,
        ``motivation_level_score``, ``hours_studied``, ``student_id``.

    Raises
    ------
    IndexError
        Jika indeks berada di luar rentang DataFrame.
    """
    if index not in df.index:
        raise IndexError(
            f"Indeks {index} tidak ditemukan. "
            f"Rentang indeks yang valid: {df.index.min()} – {df.index.max()}"
        )

    row: pd.Series = df.loc[index]

    return {
        "exam_score": row["Exam_Score"],
        "exam_score_normalized": row["Exam_Score_Normalized"],
        "peer_influence": row["Peer_Influence"],
        "peer_influence_score": row["Peer_Influence_Score"],
        "motivation_level": row["Motivation_Level"],
        "motivation_level_score": row["Motivation_Level_Score"],
        "hours_studied": row["Hours_Studied"],
        "student_id": index,
    }


def get_student_label(df: pd.DataFrame, index: int) -> str:
    """Membuat label tampilan untuk siswa, cocok digunakan di selectbox UI.

    Format label:
        ``Siswa {index+1} | Skor: {exam_score} | {motivation_level} | {peer_influence}``

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame yang sudah diproses (hasil dari ``preprocess_data()``).
    index : int
        Nomor indeks baris di dalam DataFrame.

    Returns
    -------
    str
        String label yang merepresentasikan data ringkas siswa.

    Raises
    ------
    IndexError
        Jika indeks berada di luar rentang DataFrame.
    """
    if index not in df.index:
        raise IndexError(
            f"Indeks {index} tidak ditemukan. "
            f"Rentang indeks yang valid: {df.index.min()} – {df.index.max()}"
        )

    row: pd.Series = df.loc[index]

    exam_score = row["Exam_Score"]
    motivation_level = row["Motivation_Level"]
    peer_influence = row["Peer_Influence"]

    return (
        f"Siswa {index + 1} | Skor: {exam_score} | "
        f"{motivation_level} | {peer_influence}"
    )


def get_summary_statistics(df: pd.DataFrame) -> dict:
    """Menghitung statistik ringkasan dari dataset siswa.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame (bisa yang asli maupun yang sudah diproses).

    Returns
    -------
    dict
        Dictionary berisi statistik ringkasan dengan kunci:
        ``total_students``, ``avg_exam_score``, ``max_exam_score``,
        ``min_exam_score``, ``motivation_dist``, ``peer_influence_dist``.
    """
    return {
        "total_students": len(df),
        "avg_exam_score": round(df["Exam_Score"].mean(), 2),
        "max_exam_score": df["Exam_Score"].max(),
        "min_exam_score": df["Exam_Score"].min(),
        "motivation_dist": df["Motivation_Level"].value_counts().to_dict(),
        "peer_influence_dist": df["Peer_Influence"].value_counts().to_dict(),
    }
