"""
ahp.py - Implementasi Analytic Hierarchy Process (AHP) Murni

Modul ini mengimplementasikan metode AHP secara lengkap dan murni untuk
Sistem Pendukung Keputusan (SPK). AHP digunakan untuk menentukan
bobot prioritas kriteria DAN meranking alternatif — keduanya melalui
perbandingan berpasangan (pairwise comparison).

Dalam AHP Murni:
  1. Bobot kriteria didapat dari matriks perbandingan berpasangan antar kriteria.
  2. Skor setiap alternatif per kriteria juga dinormalisasi melalui perbandingan
     berpasangan antar alternatif (bukan SAW/WP/Fuzzy).
  3. Skor akhir = jumlah (bobot_kriteria × prioritas_lokal_alternatif).

Referensi: Saaty, T.L. (1980). The Analytic Hierarchy Process.
"""

import numpy as np

# Tabel Random Index (RI) oleh Saaty untuk matriks berukuran 1-15
RI_TABLE = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59
}


def create_pairwise_matrix(weights: list) -> np.ndarray:
    """Membuat matriks perbandingan berpasangan dari daftar bobot kepentingan.

    Matriks dibuat dengan rumus:
        matrix[i][j] = weights[i] / weights[j]

    Sifat-sifat matriks yang dihasilkan:
        - Diagonal selalu bernilai 1.0
        - Bersifat resiprokal: matrix[j][i] = 1 / matrix[i][j]

    Args:
        weights: Daftar bobot kepentingan untuk setiap kriteria.
                 Contoh: [5, 3, 7, 2, 4, 6] untuk 6 kriteria.
                 Setiap nilai harus lebih besar dari 0.

    Returns:
        np.ndarray: Matriks perbandingan berpasangan berukuran n×n.

    Raises:
        ValueError: Jika daftar bobot kosong atau mengandung nilai nol/negatif.
    """
    if not weights:
        raise ValueError("Daftar bobot tidak boleh kosong.")

    weights_arr = np.array(weights, dtype=float)

    if np.any(weights_arr <= 0):
        raise ValueError("Semua bobot harus bernilai positif (lebih dari 0).")

    n = len(weights_arr)
    matrix = weights_arr.reshape(n, 1) / weights_arr.reshape(1, n)

    return matrix


def calculate_priority_vector(matrix: np.ndarray) -> np.ndarray:
    """Menghitung vektor prioritas (eigenvector) menggunakan metode rata-rata geometrik.

    Langkah-langkah:
        1. Untuk setiap baris, hitung rata-rata geometrik dari semua elemen.
        2. Normalisasi dengan membagi setiap rata-rata geometrik dengan
           jumlah total semua rata-rata geometrik.

    Args:
        matrix: Matriks perbandingan berpasangan berukuran n×n.

    Returns:
        np.ndarray: Vektor prioritas yang telah dinormalisasi (jumlah = 1.0).

    Raises:
        ValueError: Jika matriks kosong atau bukan matriks persegi.
    """
    if matrix.size == 0:
        raise ValueError("Matriks tidak boleh kosong.")

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Matriks harus berupa matriks persegi (n×n).")

    n = matrix.shape[0]

    geometric_means = np.prod(matrix, axis=1) ** (1.0 / n)

    total = np.sum(geometric_means)

    if total == 0:
        raise ValueError("Total rata-rata geometrik bernilai nol, normalisasi gagal.")

    priority_vector = geometric_means / total

    return priority_vector


def calculate_lambda_max(matrix: np.ndarray, priority_vector: np.ndarray) -> float:
    """Menghitung λmax (nilai eigen maksimum) dari matriks perbandingan berpasangan.

    Metode:
        1. Kalikan matriks dengan vektor prioritas.
        2. Bagi setiap elemen hasil perkalian dengan elemen vektor prioritas
           yang bersesuaian.
        3. Ambil rata-rata dari hasil pembagian tersebut.

    Args:
        matrix: Matriks perbandingan berpasangan berukuran n×n.
        priority_vector: Vektor prioritas hasil perhitungan AHP.

    Returns:
        float: Nilai λmax (lambda max).

    Raises:
        ValueError: Jika ada elemen vektor prioritas bernilai nol.
    """
    if np.any(priority_vector == 0):
        raise ValueError(
            "Vektor prioritas mengandung nilai nol, pembagian tidak dapat dilakukan."
        )

    weighted_sum = matrix @ priority_vector

    ratios = weighted_sum / priority_vector

    lambda_max = float(np.mean(ratios))

    return lambda_max


def calculate_consistency_index(lambda_max: float, n: int) -> float:
    """Menghitung Consistency Index (CI) dari nilai λmax dan ukuran matriks.

    Rumus:
        CI = (λmax - n) / (n - 1)

    Args:
        lambda_max: Nilai eigen maksimum (λmax).
        n: Ukuran matriks (jumlah kriteria).

    Returns:
        float: Nilai Consistency Index (CI).

    Raises:
        ValueError: Jika n kurang dari 2 (CI tidak terdefinisi untuk n=1).
    """
    if n < 2:
        return 0.0

    ci = (lambda_max - n) / (n - 1)
    return ci


def calculate_consistency_ratio(
    matrix: np.ndarray,
) -> tuple[float, float, float, bool]:
    """Menghitung analisis konsistensi lengkap untuk matriks perbandingan berpasangan.

    Langkah-langkah:
        1. Hitung vektor prioritas dari matriks.
        2. Hitung λmax (nilai eigen maksimum).
        3. Hitung Consistency Index (CI).
        4. Cari Random Index (RI) dari tabel RI_TABLE berdasarkan ukuran matriks.
        5. Hitung Consistency Ratio: CR = CI / RI.
        6. Matriks dianggap konsisten jika CR < 0.1 (10%).

    Args:
        matrix: Matriks perbandingan berpasangan berukuran n×n.

    Returns:
        tuple: (CR, CI, lambda_max, is_consistent)
            - CR (float): Consistency Ratio.
            - CI (float): Consistency Index.
            - lambda_max (float): Nilai eigen maksimum.
            - is_consistent (bool): True jika CR < 0.1 (konsisten).

    Raises:
        ValueError: Jika ukuran matriks melebihi 15 (di luar jangkauan tabel RI).
    """
    n = matrix.shape[0]

    if n > 15:
        raise ValueError(
            f"Ukuran matriks ({n}) melebihi batas tabel RI (maksimal 15)."
        )

    priority_vector = calculate_priority_vector(matrix)
    lambda_max = calculate_lambda_max(matrix, priority_vector)
    ci = calculate_consistency_index(lambda_max, n)

    ri = RI_TABLE.get(n, 0.0)

    if ri == 0:
        cr = 0.0
    else:
        cr = ci / ri

    is_consistent = cr < 0.1

    return (cr, ci, lambda_max, is_consistent)


# =============================================================================
# AHP MURNI: Perbandingan Berpasangan Antar Alternatif per Kriteria
# =============================================================================

def build_alternative_pairwise_matrix(
    values: list[float], crit_type: str = "benefit"
) -> np.ndarray:
    """Membangun matriks perbandingan berpasangan antar alternatif untuk satu kriteria.

    Dalam AHP Murni, setiap alternatif dibandingkan satu-satu terhadap alternatif
    lain untuk setiap kriteria. Perbandingan didasarkan pada rasio nilai:
        - Untuk 'benefit': matrix[i][j] = values[i] / values[j]
        - Untuk 'cost'   : matrix[i][j] = values[j] / values[i]  (dibalik)

    Matriks bersifat resiprokal: matrix[j][i] = 1 / matrix[i][j].

    Args:
        values   : Daftar nilai numerik setiap alternatif untuk kriteria ini.
        crit_type: 'benefit' (semakin besar semakin baik) atau
                   'cost' (semakin kecil semakin baik).

    Returns:
        np.ndarray: Matriks perbandingan berpasangan n×n.

    Raises:
        ValueError: Jika values kosong, mengandung nol, atau crit_type tidak valid.
    """
    if not values:
        raise ValueError("Daftar nilai alternatif tidak boleh kosong.")

    arr = np.array(values, dtype=float)

    if np.any(arr <= 0):
        raise ValueError(
            "Semua nilai alternatif harus positif (> 0) agar perbandingan valid."
        )

    if crit_type not in ("benefit", "cost"):
        raise ValueError(
            f"crit_type '{crit_type}' tidak valid. Gunakan 'benefit' atau 'cost'."
        )

    n = len(arr)

    if crit_type == "benefit":
        # Semakin tinggi nilai → semakin unggul → rasio langsung
        matrix = arr.reshape(n, 1) / arr.reshape(1, n)
    else:
        # Semakin rendah nilai → semakin unggul → rasio dibalik
        matrix = arr.reshape(1, n) / arr.reshape(n, 1)

    return matrix


def calculate_local_priorities(
    criteria_scores: dict,
    criteria_names: list[str],
    criteria_types: list[str],
) -> dict[str, np.ndarray]:
    """Menghitung vektor prioritas lokal setiap alternatif untuk setiap kriteria.

    Untuk setiap kriteria:
        1. Kumpulkan nilai mentah semua alternatif.
        2. Bangun matriks perbandingan berpasangan antar alternatif.
        3. Hitung vektor prioritas (eigenvector ternormalisasi) dari matriks tersebut.

    Hasilnya adalah bobot relatif setiap alternatif *per kriteria* — inilah inti
    dari AHP Murni yang membedakannya dari SAW/WP.

    Args:
        criteria_scores: Dict {nama_alternatif: {nama_kriteria: skor}}.
        criteria_names : Daftar nama kriteria sesuai urutan bobot.
        criteria_types : Daftar tipe ('benefit'/'cost') sesuai urutan criteria_names.

    Returns:
        Dict {nama_kriteria: np.ndarray vektor_prioritas_lokal}.
        Urutan elemen vektor sesuai urutan alternatif di criteria_scores.

    Raises:
        ValueError: Jika input tidak konsisten atau mengandung nilai tidak valid.
    """
    if len(criteria_names) != len(criteria_types):
        raise ValueError("Jumlah nama kriteria dan tipe kriteria harus sama.")

    alternative_names = list(criteria_scores.keys())
    local_priorities: dict[str, np.ndarray] = {}

    for crit_name, crit_type in zip(criteria_names, criteria_types):
        raw_values = [
            float(criteria_scores[alt][crit_name])
            for alt in alternative_names
        ]

        pairwise = build_alternative_pairwise_matrix(raw_values, crit_type)
        priority = calculate_priority_vector(pairwise)
        local_priorities[crit_name] = priority

    return local_priorities


def calculate_final_scores(
    criteria_scores: dict,
    priority_vector: np.ndarray,
    criteria_names: list[str],
    criteria_types: list[str],
) -> dict:
    """Menghitung skor akhir AHP Murni untuk setiap alternatif.

    Alur AHP Murni (berbeda dari SAW/WP):
        1. Untuk setiap kriteria, bangun matriks perbandingan berpasangan
           antar alternatif berdasarkan nilai mentah mereka.
        2. Dari matriks tersebut, hitung vektor prioritas lokal
           (bobot relatif alternatif untuk kriteria itu).
        3. Skor akhir alternatif = Σ (bobot_kriteria × prioritas_lokal_alternatif).

    Ini berbeda dari SAW yang memakai normalisasi max-value atau min-value
    secara langsung tanpa pembentukan matriks perbandingan.

    Args:
        criteria_scores : Dict {nama_alternatif: {nama_kriteria: skor}}.
        priority_vector : Vektor bobot kriteria hasil AHP (panjang = jumlah kriteria).
        criteria_names  : Daftar nama kriteria sesuai urutan priority_vector.
        criteria_types  : Daftar tipe ('benefit'/'cost') sesuai urutan criteria_names.

    Returns:
        dict: {nama_alternatif: skor_akhir_float}.

    Raises:
        ValueError: Jika input tidak valid atau tidak konsisten.
    """
    if not criteria_scores:
        raise ValueError("Data skor kriteria tidak boleh kosong.")

    if len(criteria_names) != len(criteria_types):
        raise ValueError("Jumlah nama kriteria dan tipe kriteria harus sama.")

    if len(criteria_names) != len(priority_vector):
        raise ValueError(
            "Jumlah kriteria harus sama dengan panjang vektor prioritas."
        )

    alternative_names = list(criteria_scores.keys())

    # ── Langkah AHP Murni: hitung prioritas lokal per kriteria ──────────
    local_priorities = calculate_local_priorities(
        criteria_scores, criteria_names, criteria_types
    )

    # ── Agregasi: skor akhir = Σ (bobot_kriteria × prioritas_lokal) ─────
    final_scores: dict[str, float] = {}
    for i, alt_name in enumerate(alternative_names):
        score = 0.0
        for j, crit_name in enumerate(criteria_names):
            weight = priority_vector[j]
            local_priority = local_priorities[crit_name][i]
            score += weight * local_priority
        final_scores[alt_name] = score

    return final_scores


def rank_alternatives(final_scores: dict) -> list[tuple]:
    """Meranking alternatif berdasarkan skor akhir secara menurun (descending).

    Args:
        final_scores: Dictionary dengan nama alternatif sebagai key dan
                      skor akhir sebagai value.

    Returns:
        list[tuple]: Daftar tuple berisi (peringkat, nama_alternatif, skor),
                     diurutkan dari skor tertinggi ke terendah.
                     Peringkat dimulai dari 1.

    Raises:
        ValueError: Jika dictionary skor kosong.
    """
    if not final_scores:
        raise ValueError("Data skor akhir tidak boleh kosong.")

    sorted_alternatives = sorted(
        final_scores.items(), key=lambda x: x[1], reverse=True
    )

    ranked = [
        (rank + 1, name, score)
        for rank, (name, score) in enumerate(sorted_alternatives)
    ]

    return ranked


# =============================================================================
# Fungsi bantu: ringkasan matriks lokal (untuk ditampilkan di UI jika diperlukan)
# =============================================================================

def get_local_priority_tables(
    criteria_scores: dict,
    criteria_names: list[str],
    criteria_types: list[str],
) -> dict[str, dict]:
    """Menghasilkan ringkasan matriks perbandingan lokal per kriteria.

    Berguna untuk menampilkan transparansi perhitungan AHP di antarmuka.

    Returns:
        Dict {nama_kriteria: {'matrix': np.ndarray, 'priority': np.ndarray}}
    """
    alternative_names = list(criteria_scores.keys())
    result = {}

    for crit_name, crit_type in zip(criteria_names, criteria_types):
        raw_values = [
            float(criteria_scores[alt][crit_name])
            for alt in alternative_names
        ]
        pairwise = build_alternative_pairwise_matrix(raw_values, crit_type)
        priority = calculate_priority_vector(pairwise)
        result[crit_name] = {
            "matrix": pairwise,
            "priority": priority,
            "alternative_names": alternative_names,
        }

    return result
