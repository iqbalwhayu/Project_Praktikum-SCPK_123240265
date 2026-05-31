"""
ahp.py - Implementasi Analytic Hierarchy Process (AHP)

Modul ini mengimplementasikan metode AHP secara lengkap untuk
Sistem Pendukung Keputusan (SPK). AHP digunakan untuk menentukan
bobot prioritas kriteria dan meranking alternatif berdasarkan
perbandingan berpasangan (pairwise comparison).

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

    # Hitung vektor prioritas
    priority_vector = calculate_priority_vector(matrix)

    # Hitung λmax
    lambda_max = calculate_lambda_max(matrix, priority_vector)

    # Hitung CI
    ci = calculate_consistency_index(lambda_max, n)

    # Cari RI dari tabel
    ri = RI_TABLE.get(n, 0.0)

    # Hitung CR (tangani kasus RI = 0)
    if ri == 0:
        # Untuk matriks 1×1 atau 2×2, CR otomatis 0 (selalu konsisten)
        cr = 0.0
    else:
        cr = ci / ri

    # Cek konsistensi
    is_consistent = cr < 0.1

    return (cr, ci, lambda_max, is_consistent)


def normalize_benefit(values: list) -> list:
    """Normalisasi kriteria bertipe benefit (semakin tinggi semakin baik).

    Rumus:
        normalized = value / max(values)

    Args:
        values: Daftar nilai mentah dari suatu kriteria benefit.

    Returns:
        list: Daftar nilai yang telah dinormalisasi (0.0 - 1.0).

    Raises:
        ValueError: Jika daftar nilai kosong atau semua nilai nol.
    """
    if not values:
        raise ValueError("Daftar nilai tidak boleh kosong.")

    max_val = max(values)

    if max_val == 0:
        raise ValueError(
            "Nilai maksimum adalah 0, normalisasi benefit tidak dapat dilakukan."
        )

    return [v / max_val for v in values]


def normalize_cost(values: list) -> list:
    """Normalisasi kriteria bertipe cost (semakin rendah semakin baik).

    Rumus:
        normalized = min(values) / value

    Args:
        values: Daftar nilai mentah dari suatu kriteria cost.

    Returns:
        list: Daftar nilai yang telah dinormalisasi (0.0 - 1.0).

    Raises:
        ValueError: Jika daftar nilai kosong atau mengandung nilai nol.
    """
    if not values:
        raise ValueError("Daftar nilai tidak boleh kosong.")

    if any(v == 0 for v in values):
        raise ValueError(
            "Daftar nilai mengandung angka 0, normalisasi cost tidak dapat dilakukan "
            "(pembagian dengan nol)."
        )

    min_val = min(values)

    return [min_val / v for v in values]


def calculate_final_scores(
    criteria_scores: dict,
    priority_vector: np.ndarray,
    criteria_names: list,
    criteria_types: list,
) -> dict:
    """Menghitung skor akhir setiap alternatif berdasarkan bobot AHP dan normalisasi.

    Langkah-langkah:
        1. Untuk setiap kriteria, kumpulkan semua nilai dari seluruh alternatif.
        2. Normalisasi menggunakan metode benefit atau cost sesuai tipe kriteria.
        3. Hitung skor tertimbang: sum(nilai_normalisasi × bobot) untuk setiap alternatif.

    Args:
        criteria_scores: Dictionary dengan nama alternatif sebagai key dan
                         dictionary {nama_kriteria: skor} sebagai value.
                         Contoh:
                         {
                             'Teknik Informatika': {
                                 'nilai': 4.5, 'minat': 5, 'bakat': 5,
                                 'psikologi': 3, 'motivasi': 3, 'biaya': 1
                             },
                             'Sistem Informasi': {
                                 'nilai': 3.0, 'minat': 4, 'bakat': 3,
                                 'psikologi': 4, 'motivasi': 4, 'biaya': 2
                             }
                         }
        priority_vector: Array numpy berisi bobot AHP untuk setiap kriteria.
        criteria_names: Daftar nama kriteria sesuai urutan priority_vector.
        criteria_types: Daftar tipe kriteria ('benefit' atau 'cost')
                        sesuai urutan criteria_names.

    Returns:
        dict: Dictionary dengan nama alternatif sebagai key dan skor akhir
              sebagai value.

    Raises:
        ValueError: Jika input tidak valid atau tidak konsisten.
    """
    if not criteria_scores:
        raise ValueError("Data skor kriteria tidak boleh kosong.")

    if len(criteria_names) != len(criteria_types):
        raise ValueError(
            "Jumlah nama kriteria dan tipe kriteria harus sama."
        )

    if len(criteria_names) != len(priority_vector):
        raise ValueError(
            "Jumlah kriteria harus sama dengan panjang vektor prioritas."
        )

    alternative_names = list(criteria_scores.keys())

    # nilai mentah per kriteria dari semua alternatif
    raw_values: dict[str, list] = {name: [] for name in criteria_names}
    for alt_name in alternative_names:
        scores = criteria_scores[alt_name]
        for crit_name in criteria_names:
            raw_values[crit_name].append(scores[crit_name])

    # 
    # Normalisasi setiap kriteria sesuai tipenya
    normalized_values: dict[str, list] = {}
    for crit_name, crit_type in zip(criteria_names, criteria_types):
        values = raw_values[crit_name]
        if crit_type == "benefit":
            normalized_values[crit_name] = normalize_benefit(values)
        elif crit_type == "cost":
            normalized_values[crit_name] = normalize_cost(values)
        else:
            raise ValueError(
                f"Tipe kriteria '{crit_type}' tidak valid. "
                "Gunakan 'benefit' atau 'cost'."
            )

    # Hitung skor akhir untuk setiap alternatif
    final_scores: dict[str, float] = {}
    for i, alt_name in enumerate(alternative_names):
        score = 0.0
        for j, crit_name in enumerate(criteria_names):
            normalized_val = normalized_values[crit_name][i]
            weight = priority_vector[j]
            score += normalized_val * weight
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

    # Urutkan berdasarkan skor secara menurun
    sorted_alternatives = sorted(
        final_scores.items(), key=lambda x: x[1], reverse=True
    )

    # Buat daftar tuple dengan peringkat
    ranked = [
        (rank + 1, name, score)
        for rank, (name, score) in enumerate(sorted_alternatives)
    ]

    return ranked
