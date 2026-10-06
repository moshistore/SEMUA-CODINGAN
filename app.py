from datetime import datetime
import psycopg2

# 1. KONEKSI KE DATABASE POSTGRESQL
# Ganti parameter berikut sesuai dengan konfigurasi PostgreSQL kamu
DB_CONFIG = {
    "dbname": "siakad_sma",
    "user": "postgres",
    "password": "12345",  # <-- Masukkan password PostgreSQL kamu di sini 
    "host": "localhost",
    "port": "5432",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# 2. INISIALISASI TABEL DATABASE
def setup_database():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Tabel Pengguna (Login)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL,
                nama VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL -- 'siswa' atau 'guru'
            );
        """
        )

        # Tabel Mata Pelajaran
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mata_pelajaran (
                id SERIAL PRIMARY KEY,
                kode_mapel VARCHAR(10) UNIQUE NOT NULL,
                nama_mapel VARCHAR(100) NOT NULL,
                guru_pengampu VARCHAR(100)
            );
        """
        )

        # Tabel Absensi
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS absensi (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id),
                tanggal DATE NOT NULL,
                jam_masuk TIME,
                jam_pulang TIME,
                status VARCHAR(20) DEFAULT 'Hadir'
            );
        """
        )

        # Tambah data dummy jika tabel pengguna masih kosong
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO users (username, password, nama, role) VALUES 
                ('siswa1', '12345', 'Budi Santoso', 'siswa'),
                ('guru1', '12345', 'Siti Aminah, S.Pd', 'guru');
            """
            )
            cursor.execute(
                """
                INSERT INTO mata_pelajaran (kode_mapel, nama_mapel, guru_pengampu) VALUES 
                ('MTK10', 'Matematika Wajib', 'Siti Aminah, S.Pd'),
                ('BIG10', 'Bahasa Inggris', 'Bambang, M.Pd'),
                ('FIS10', 'Fisika dasar', 'Dewi, S.Si');
            """
            )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error setup database: {e}")


# 3. FITUR-FITUR UTAMA
def absensi_masuk(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    # Cek apakah sudah absen masuk hari ini
    cursor.execute(
        "SELECT * FROM absensi WHERE user_id = %s AND tanggal = %s",
        (user_id, today),
    )
    data = cursor.fetchone()

    if data:
        print("\n[!] Kamu sudah melakukan absensi masuk hari ini!")
    else:
        cursor.execute(
            """
            INSERT INTO absensi (user_id, tanggal, jam_masuk)
            VALUES (%s, %s, %s)
        """,
            (user_id, today, now_time),
        )
        conn.commit()
        print(f"\n[✓] Absensi MASUK berhasil tercatat pada jam: {now_time}")

    cursor.close()
    conn.close()


def absensi_pulang(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    cursor.execute(
        "SELECT * FROM absensi WHERE user_id = %s AND tanggal = %s",
        (user_id, today),
    )
    data = cursor.fetchone()

    if not data:
        print("\n[!] Kamu belum melakukan absensi masuk hari ini!")
    elif data[4] is not None:  # Kolom jam_pulang
        print("\n[!] Kamu sudah melakukan absensi pulang hari ini!")
    else:
        cursor.execute(
            """
            UPDATE absensi SET jam_pulang = %s
            WHERE user_id = %s AND tanggal = %s
        """,
            (now_time, user_id, today),
        )
        conn.commit()
        print(f"\n[✓] Absensi PULANG berhasil tercatat pada jam: {now_time}")

    cursor.close()
    conn.close()


def lihat_mata_pelajaran():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT kode_mapel, nama_mapel, guru_pengampu FROM mata_pelajaran")
    mapel_list = cursor.fetchall()

    print("\n--- DAFTAR MATA PELAJARAN SMA ---")
    print(f"{'Kode':<10} | {'Nama Mata Pelajaran':<25} | {'Guru Pengampu':<20}")
    print("-" * 60)
    for mapel in mapel_list:
        print(f"{mapel[0]:<10} | {mapel[1]:<25} | {mapel[2]:<20}")

    cursor.close()
    conn.close()


# 4. DASHBOARD UTAMA
def dashboard(user):
    user_id, username, _, nama, role = user
    while True:
        print("\n======================================")
        print(f"      DASHBOARD SIAKAD SMA            ")
        print("======================================")
        print(f"Selamat Datang : {nama} ({role.upper()})")
        print("--------------------------------------")
        print("1. Absensi Masuk")
        print("2. Absensi Pulang")
        print("3. Lihat Mata Pelajaran")
        print("4. Logout")
        print("======================================")

        pilihan = input("Pilih Menu (1-4): ")

        if pilihan == "1":
            absensi_masuk(user_id)
        elif pilihan == "2":
            absensi_pulang(user_id)
        elif pilihan == "3":
            lihat_mata_pelajaran()
        elif pilihan == "4":
            print("\nBerhasil Logout. Sampai jumpa!")
            break
        else:
            print("\nPilihan tidak valid!")


# 5. HALAMAN LOGIN
def login():
    print("\n======================================")
    print("         LOGIN SIAKAD SMA             ")
    print("======================================")
    username = input("Username: ")
    password = input("Password: ")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password, nama, role FROM users WHERE username = %s AND password = %s",
        (username, password),
    )
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        print(f"\n[✓] Login Berhasil! Selamat datang {user[3]}.")
        dashboard(user)
    else:
        print("\n[X] Username atau Password salah!")


# PROGRAM UTAMA
if __name__ == "__main__":
    # Pastikan database 'siakad_sma' sudah kamu buat di PostgreSQL sebelum menjalankan script
    setup_database()
    while True:
        print("\n=== SISTEM INFORMASI AKADEMIK (SIAKAD) SMA ===")
        print("1. Login")
        print("2. Keluar Aplikasi")
        pilih = input("Pilih (1/2): ")

        if pilih == "1":
            login()
        elif pilih == "2":
            print("\nTerima kasih telah menggunakan SIAKAD SMA.")
            break
        else:
            print("\nPilihan tidak valid!")