
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

FAMILY_INCOME_MAP: dict[str, int] = {
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
    "Family_Income",
]


#Fungsi-fungsi utama 


def load_dataset(filepath: str) -> pd.DataFrame:
    """Memuat dataset dari file CSV dan memvalidasi kolom yang diperlukan."""
    df: pd.DataFrame = pd.read_csv(filepath)

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
    """Memproses DataFrame dengan menambahkan kolom-kolom turunan baru."""
    processed: pd.DataFrame = df.copy()

    processed = processed.dropna(subset=["Exam_Score"])

    # Konversi Peer_Influence ke skor numerik
    processed["Peer_Influence_Score"] = (
        processed["Peer_Influence"]
        .map(PEER_INFLUENCE_MAP)
        .fillna(2)
        .astype(int)
    )

    # Konversi Motivation_Level ke skor numerik
    processed["Motivation_Level_Score"] = (
        processed["Motivation_Level"]
        .map(MOTIVATION_LEVEL_MAP)
        .fillna(2)
        .astype(int)
    )

    # Konversi Family_Income ke skor numerik
    processed["Family_Income_Score"] = (
        processed["Family_Income"]
        .map(FAMILY_INCOME_MAP)
        .fillna(2)
        .astype(int)
    )

    # Normalisasi Exam_Score ke skala 1-5
    exam_min: float = processed["Exam_Score"].min()
    exam_max: float = processed["Exam_Score"].max()

    if exam_max == exam_min:
        processed["Exam_Score_Normalized"] = 3.0
    else:
        processed["Exam_Score_Normalized"] = (
            1 + (processed["Exam_Score"] - exam_min) / (exam_max - exam_min) * 4
        ).round(4)

    return processed


def get_student_data(df: pd.DataFrame, index: int) -> dict:
    """Mengambil data seorang siswa berdasarkan indeks DataFrame."""
    if index not in df.index:
        raise IndexError(
            f"Indeks {index} tidak ditemukan. "
            f"Rentang indeks yang valid: {df.index.min()} – {df.index.max()}"
        )

    row = df.loc[index]
    if not isinstance(row, pd.Series):
        raise TypeError(
            f"Data pada indeks {index} tidak berbentuk baris tunggal."
        )

    return {
        "exam_score": row["Exam_Score"],
        "exam_score_normalized": row["Exam_Score_Normalized"],
        "peer_influence": row["Peer_Influence"],
        "peer_influence_score": row["Peer_Influence_Score"],
        "motivation_level": row["Motivation_Level"],
        "motivation_level_score": row["Motivation_Level_Score"],
        "hours_studied": row["Hours_Studied"],
        "family_income": row["Family_Income"],
        "family_income_score": row["Family_Income_Score"],
        "student_id": index,
    }


def get_student_label(df: pd.DataFrame, index: int) -> str:
    """Membuat label tampilan untuk siswa."""
    if index not in df.index:
        raise IndexError(
            f"Indeks {index} tidak ditemukan. "
            f"Rentang indeks yang valid: {df.index.min()} – {df.index.max()}"
        )

    row = df.loc[index]
    if not isinstance(row, pd.Series):
        raise TypeError(
            f"Data pada indeks {index} tidak berbentuk baris tunggal."
        )

    exam_score = row["Exam_Score"]
    motivation_level = row["Motivation_Level"]
    peer_influence = row["Peer_Influence"]
    family_income = row.get("Family_Income", "N/A")

    return (
        f"Siswa {index + 1} | Skor: {exam_score} | "
        f"{motivation_level} | {peer_influence} | Income: {family_income}"
    )


def get_summary_statistics(df: pd.DataFrame) -> dict:
    """Menghitung statistik ringkasan dari dataset siswa."""
    family_income_dist = {}
    if "Family_Income" in df.columns:
        family_income_dist = df["Family_Income"].value_counts().to_dict()

    return {
        "total_students": len(df),
        "avg_exam_score": round(df["Exam_Score"].mean(), 2),
        "max_exam_score": df["Exam_Score"].max(),
        "min_exam_score": df["Exam_Score"].min(),
        "motivation_dist": df["Motivation_Level"].value_counts().to_dict(),
        "peer_influence_dist": df["Peer_Influence"].value_counts().to_dict(),
        "family_income_dist": family_income_dist,
    }


def save_dataset(df: pd.DataFrame, filepath: str) -> None:
    """Menyimpan DataFrame ke file CSV."""
    df.to_csv(filepath, index=False)
