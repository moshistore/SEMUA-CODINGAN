from datetime import datetime
from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "siakad_full_interactive_secret_key"

# ==========================================
# DATABASE DUMMY LOKAL (Agar Semua Fitur Berfungsi)
# ==========================================
DATA_SISWA = [
    {
        "id": 1,
        "nisn": "0054829102",
        "nama": "Budi Santoso",
        "kelas": "XII-IPA-1",
        "jk": "Laki-laki",
        "status": "Aktif",
    },
    {
        "id": 2,
        "nisn": "0054829103",
        "nama": "Siti Aminah",
        "kelas": "XII-IPA-1",
        "jk": "Perempuan",
        "status": "Aktif",
    },
]

DATA_GURU = [
    {
        "id": 1,
        "nip": "198501152010011001",
        "nama": "Drs. Budi Santoso",
        "mapel": "Matematika",
        "status": "PNS",
    },
    {
        "id": 2,
        "nip": "199003202015022002",
        "nama": "Siti Nurhaliza, M.Pd",
        "mapel": "Fisika",
        "status": "PNS",
    },
]

DATA_MAPEL = [
    {
        "kode": "MTK01",
        "nama": "Matematika Wajib",
        "guru": "Drs. Budi Santoso",
        "hari": "Senin",
        "jam": "07:30 - 09:00",
        "ruang": "XII-IPA-1",
    },
    {
        "kode": "FIS01",
        "nama": "Fisika",
        "guru": "Siti Nurhaliza, M.Pd",
        "hari": "Senin",
        "jam": "09:15 - 10:45",
        "ruang": "Lab Fisika",
    },
    {
        "kode": "KIM01",
        "nama": "Kimia",
        "guru": "Ahmad Subagja, S.Si",
        "hari": "Selasa",
        "jam": "07:30 - 09:00",
        "ruang": "Lab Kimia",
    },
]

DATA_TUGAS = [
    {
        "id": 1,
        "mapel": "Matematika",
        "judul": "Latihan Soal Trigonometri",
        "dl": "2026-10-01",
        "status": "Belum Dikerjakan",
    },
    {
        "id": 2,
        "mapel": "Fisika",
        "judul": "Laporan Praktikum Hukum Newton",
        "dl": "2026-10-05",
        "status": "Selesai",
    },
]

DATA_PENGUMUMAN = [
    {
        "tgl": "2026-09-20",
        "judul": "Pelaksanaan UTS Semester Ganjil",
        "isi": "UTS akan dilaksanakan secara serentak mulai tanggal 12 Oktober 2026.",
    },
    {
        "tgl": "2026-09-15",
        "judul": "Kegiatan Ekstrakurikuler Wajib",
        "isi": "Seluruh siswa kelas X dan XI wajib mengikuti kegiatan Pramuka.",
    },
]

STATUS_PRESENSI_SISWA = {"status": "Belum Absen", "jam": "-"}

# ==========================================
# BASE LAYOUT TEMPLATE
# ==========================================
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - SIAKAD PRO</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --bg-body: #f8fafc; --card-bg: #ffffff; --text-color: #0f172a; }
        body.dark-mode { --bg-body: #0f172a; --card-bg: #1e293b; --text-color: #f8fafc; }
        body { background-color: var(--bg-body); color: var(--text-color); transition: 0.3s; }
        .sidebar { min-height: 100vh; background: #0f172a; color: white; }
        .nav-link { color: #94a3b8; border-radius: 10px; padding: 10px 15px; margin-bottom: 5px; }
        .nav-link:hover, .nav-link.active { color: white; background: #2563eb; }
        .card-custom { background-color: var(--card-bg); border-radius: 16px; border: 1px solid #e2e8f0; }
    </style>
</head>
<body>
<div class="container-fluid">
    <div class="row">
        <!-- SIDEBAR -->
        <div class="col-lg-2 sidebar p-3 sticky-top" style="height: 100vh; overflow-y: auto;">
            <div class="d-flex align-items-center mb-4">
                <i class="fa-solid fa-graduation-cap text-warning fa-2x me-2"></i>
                <h5 class="fw-bold mb-0 text-white">SIAKAD PRO</h5>
            </div>
            <hr class="border-secondary">
            <ul class="nav flex-column">
                {% if session['role'] == 'admin' %}
                    <li class="nav-item"><a class="nav-link {% if page == 'admin_dashboard' %}active{% endif %}" href="/admin/dashboard"><i class="fa-solid fa-gauge me-2"></i> Dashboard Admin</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'admin_siswa' %}active{% endif %}" href="/admin/siswa"><i class="fa-solid fa-users me-2"></i> Data Siswa</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'admin_guru' %}active{% endif %}" href="/admin/guru"><i class="fa-solid fa-chalkboard-user me-2"></i> Data Guru</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'admin_mapel' %}active{% endif %}" href="/admin/mapel"><i class="fa-solid fa-book me-2"></i> Kelola Mapel</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'admin_rekap' %}active{% endif %}" href="/admin/rekap"><i class="fa-solid fa-file-invoice me-2"></i> Rekap Laporan</a></li>
                {% else %}
                    <li class="nav-item"><a class="nav-link {% if page == 'dashboard' %}active{% endif %}" href="/dashboard"><i class="fa-solid fa-chart-pie me-2"></i> Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'presensi' %}active{% endif %}" href="/presensi"><i class="fa-solid fa-fingerprint me-2"></i> Presensi Kehadiran</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'jadwal' %}active{% endif %}" href="/jadwal"><i class="fa-solid fa-calendar-week me-2"></i> Jadwal Pelajaran</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'tugas' %}active{% endif %}" href="/tugas"><i class="fa-solid fa-list-check me-2"></i> Tugas & PR</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'nilai' %}active{% endif %}" href="/nilai"><i class="fa-solid fa-award me-2"></i> Transkrip Nilai</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'materi' %}active{% endif %}" href="/materi"><i class="fa-solid fa-book-open me-2"></i> Materi & Modul</a></li>
                    <li class="nav-item"><a class="nav-link {% if page == 'kartu' %}active{% endif %}" href="/kartu"><i class="fa-solid fa-id-card me-2"></i> Kartu Digital</a></li>
                {% endif %}
                <li class="nav-item"><a class="nav-link {% if page == 'pengumuman' %}active{% endif %}" href="/pengumuman"><i class="fa-solid fa-bullhorn me-2"></i> Pengumuman</a></li>
                <li class="nav-item"><a class="nav-link {% if page == 'profil' %}active{% endif %}" href="/profil"><i class="fa-solid fa-user me-2"></i> Profil Saya</a></li>
            </ul>
            <div class="mt-auto pt-4">
                <button class="btn btn-outline-light w-100 rounded-pill mb-2 btn-sm" onclick="document.body.classList.toggle('dark-mode')"><i class="fa-solid fa-moon me-1"></i> Mode Gelap</button>
                <a href="/logout" class="btn btn-danger w-100 rounded-pill btn-sm"><i class="fa-solid fa-power-off me-1"></i> Logout</a>
            </div>
        </div>

        <!-- KONTEN UTAMA -->
        <div class="col-lg-10 p-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h3 class="fw-bold mb-0">{{ page_title }}</h3>
                    <small class="text-muted">Portal Sistem Informasi Akademik SMA</small>
                </div>
                <span class="badge bg-primary px-3 py-2 rounded-pill"><i class="fa-solid fa-user me-1"></i> {{ session['nama'] }} ({{ session['role'].upper() }})</span>
            </div>

            {% if msg %}
            <div class="alert alert-success alert-dismissible fade show rounded-3" role="alert">
                <i class="fa-solid fa-check-circle me-1"></i> {{ msg }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            {% endif %}

            {{ content | safe }}
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# ==========================================
# HALAMAN LOGIN
# ==========================================
HTML_LOGIN = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8"><title>Login - SIAKAD</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #0f172a; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .card-login { background: white; border-radius: 20px; width: 100%; max-width: 400px; padding: 30px; }
    </style>
</head>
<body>
    <div class="card-login shadow-lg">
        <div class="text-center mb-4">
            <h3 class="fw-bold text-primary">SIAKAD LOGIN</h3>
            <p class="text-muted small">Pilih peran akun untuk masuk</p>
        </div>
        {% if msg %}<div class="alert alert-danger text-center p-2 small">{{ msg }}</div>{% endif %}
        <form method="POST">
            <div class="mb-3">
                <label class="form-label font-weight-bold">Username</label>
                <input type="text" class="form-control" name="username" placeholder="admin / guru / siswa" required>
            </div>
            <div class="mb-3">
                <label class="form-label font-weight-bold">Password</label>
                <input type="password" class="form-control" name="password" placeholder="Masukkan password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100 py-2 fw-bold">Masuk Sekarang</button>
        </form>
        <div class="mt-4 p-2 bg-light rounded text-center small text-muted">
            <b>Info Login Cepat:</b><br>
            Admin: <code>admin</code> / <code>admin</code><br>
            Guru: <code>guru</code> / <code>guru</code><br>
            Siswa: <code>siswa</code> / <code>siswa</code>
        </div>
    </div>
</body>
</html>
"""


# ==========================================
# HELPER RENDER
# ==========================================
def render_page(page_name, page_title, content_template, **kwargs):
    if "role" not in session:
        return redirect(url_for("login"))
    inner_content = render_template_string(content_template, **kwargs)
    return render_template_string(
        BASE_LAYOUT,
        page=page_name,
        page_title=page_title,
        title=page_title,
        content=inner_content,
        msg=request.args.get("msg"),
    )


# ==========================================
# ROUTING APLIKASI
# ==========================================


@app.route("/", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u == "admin" and p == "admin":
            session["nama"], session["role"] = "Administrator Utama", "admin"
            return redirect(url_for("admin_dashboard"))
        elif u == "guru" and p == "guru":
            session["nama"], session["role"] = (
                "Siti Nurhaliza, M.Pd",
                "guru",
            )
            return redirect(url_for("dashboard"))
        elif u == "siswa" and p == "siswa":
            session["nama"], session["role"] = "Budi Santoso", "siswa"
            return redirect(url_for("dashboard"))
        else:
            msg = "Username atau Password salah!"
    return render_template_string(HTML_LOGIN, msg=msg)


# --- ROUTE ADMIN ---
@app.route("/admin/dashboard")
def admin_dashboard():
    tpl = """
    <div class="row g-3 mb-4">
        <div class="col-md-3"><div class="card card-custom p-3 bg-primary text-white"><h6>Total Siswa</h6><h2>{{ data_siswa|length }}</h2></div></div>
        <div class="col-md-3"><div class="card card-custom p-3 bg-success text-white"><h6>Total Guru</h6><h2>{{ data_guru|length }}</h2></div></div>
        <div class="col-md-3"><div class="card card-custom p-3 bg-warning text-white"><h6>Mata Pelajaran</h6><h2>{{ data_mapel|length }}</h2></div></div>
        <div class="col-md-3"><div class="card card-custom p-3 bg-danger text-white"><h6>Pengumuman</h6><h2>{{ data_p|length }}</h2></div></div>
    </div>
    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3">Aksi Cepat Admin</h5>
        <div class="d-flex gap-2">
            <a href="/admin/siswa" class="btn btn-outline-primary"><i class="fa-solid fa-users me-1"></i> Kelola Siswa</a>
            <a href="/admin/guru" class="btn btn-outline-success"><i class="fa-solid fa-user-tie me-1"></i> Kelola Guru</a>
            <a href="/admin/mapel" class="btn btn-outline-warning"><i class="fa-solid fa-book me-1"></i> Kelola Mapel</a>
        </div>
    </div>
    """
    return render_page(
        "admin_dashboard",
        "Dashboard Administrator",
        tpl,
        data_siswa=DATA_SISWA,
        data_guru=DATA_GURU,
        data_mapel=DATA_MAPEL,
        data_p=DATA_PENGUMUMAN,
    )


@app.route("/admin/siswa", methods=["GET", "POST"])
def admin_siswa():
    if request.method == "POST":
        DATA_SISWA.append(
            {
                "id": len(DATA_SISWA) + 1,
                "nisn": request.form["nisn"],
                "nama": request.form["nama"],
                "kelas": request.form["kelas"],
                "jk": request.form["jk"],
                "status": "Aktif",
            }
        )
        return redirect(
            url_for("admin_siswa", msg="Siswa Baru Berhasil Ditambahkan!")
        )

    tpl = """
    <div class="card card-custom p-4 mb-4">
        <h5 class="fw-bold mb-3">Tambah Siswa Baru</h5>
        <form method="POST" class="row g-3">
            <div class="col-md-3"><input type="text" name="nisn" class="form-control" placeholder="NISN" required></div>
            <div class="col-md-3"><input type="text" name="nama" class="form-control" placeholder="Nama Lengkap" required></div>
            <div class="col-md-3"><input type="text" name="kelas" class="form-control" placeholder="Kelas (ex: XII-IPA-1)" required></div>
            <div class="col-md-3">
                <select name="jk" class="form-select"><option>Laki-laki</option><option>Perempuan</option></select>
            </div>
            <div class="col-12"><button type="submit" class="btn btn-primary"><i class="fa-solid fa-plus me-1"></i> Simpan Siswa</button></div>
        </form>
    </div>

    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3">Daftar Data Siswa</h5>
        <table class="table table-hover align-middle">
            <thead><tr><th>ID</th><th>NISN</th><th>Nama Siswa</th><th>Kelas</th><th>Gender</th><th>Status</th><th>Aksi</th></tr></thead>
            <tbody>
                {% for s in data %}
                <tr>
                    <td>{{ s.id }}</td><td>{{ s.nisn }}</td><td class="fw-bold">{{ s.nama }}</td><td>{{ s.kelas }}</td><td>{{ s.jk }}</td>
                    <td><span class="badge bg-success">{{ s.status }}</span></td>
                    <td><a href="/admin/siswa/hapus/{{ s.id }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Hapus data?')"><i class="fa-solid fa-trash"></i> Hapus</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    """
    return render_page("admin_siswa", "Kelola Data Siswa", tpl, data=DATA_SISWA)


@app.route("/admin/siswa/hapus/<int:id>")
def admin_siswa_hapus(id):
    global DATA_SISWA
    DATA_SISWA = [s for s in DATA_SISWA if s["id"] != id]
    return redirect(url_for("admin_siswa", msg="Data siswa berhasil dihapus!"))


@app.route("/admin/guru", methods=["GET", "POST"])
def admin_guru():
    if request.method == "POST":
        DATA_GURU.append(
            {
                "id": len(DATA_GURU) + 1,
                "nip": request.form["nip"],
                "nama": request.form["nama"],
                "mapel": request.form["mapel"],
                "status": "PNS",
            }
        )
        return redirect(
            url_for("admin_guru", msg="Data Guru Berhasil Ditambahkan!")
        )

    tpl = """
    <div class="card card-custom p-4 mb-4">
        <h5 class="fw-bold mb-3">Tambah Guru Baru</h5>
        <form method="POST" class="row g-3">
            <div class="col-md-4"><input type="text" name="nip" class="form-control" placeholder="NIP" required></div>
            <div class="col-md-4"><input type="text" name="nama" class="form-control" placeholder="Nama Guru" required></div>
            <div class="col-md-4"><input type="text" name="mapel" class="form-control" placeholder="Mata Pelajaran" required></div>
            <div class="col-12"><button type="submit" class="btn btn-success"><i class="fa-solid fa-plus me-1"></i> Simpan Guru</button></div>
        </form>
    </div>

    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3">Daftar Pengajar</h5>
        <table class="table table-hover align-middle">
            <thead><tr><th>NIP</th><th>Nama Guru</th><th>Mata Pelajaran</th><th>Status</th></tr></thead>
            <tbody>
                {% for g in data %}
                <tr><td>{{ g.nip }}</td><td class="fw-bold">{{ g.nama }}</td><td>{{ g.mapel }}</td><td><span class="badge bg-primary">{{ g.status }}</span></td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    """
    return render_page("admin_guru", "Kelola Data Guru", tpl, data=DATA_GURU)


@app.route("/admin/mapel")
def admin_mapel():
    tpl = """
    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3">Daftar Mata Pelajaran & Jadwal</h5>
        <table class="table table-hover">
            <thead><tr><th>Kode</th><th>Mata Pelajaran</th><th>Pengampu</th><th>Hari/Jam</th><th>Ruang</th></tr></thead>
            <tbody>
                {% for m in data %}
                <tr><td><code>{{ m.kode }}</code></td><td class="fw-bold">{{ m.nama }}</td><td>{{ m.guru }}</td><td>{{ m.hari }}, {{ m.jam }}</td><td>{{ m.ruang }}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    """
    return render_page(
        "admin_mapel", "Kelola Mata Pelajaran", tpl, data=DATA_MAPEL
    )


@app.route("/admin/rekap")
def admin_rekap():
    tpl = """
    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3"><i class="fa-solid fa-print me-2"></i> Rekapitulasi Laporan Akademik</h5>
        <p class="text-muted">Unduh laporan resmi sekolah dalam format dokumen siap cetak.</p>
        <div class="d-flex gap-2">
            <button class="btn btn-outline-primary" onclick="alert('Mengunduh Rekap Nilai...')"><i class="fa-solid fa-download me-1"></i> Cetak Rekap Nilai</button>
            <button class="btn btn-outline-success" onclick="alert('Mengunduh Rekap Presensi...')"><i class="fa-solid fa-download me-1"></i> Cetak Rekap Presensi</button>
        </div>
    </div>
    """
    return render_page("admin_rekap", "Rekap Laporan", tpl)


# --- ROUTE SISWA & GURU ---
@app.route("/dashboard")
def dashboard():
    tpl = """
    <div class="card card-custom p-4 bg-primary text-white mb-4">
        <h3 class="fw-bold">Selamat Datang, {{ session['nama'] }}!</h3>
        <p class="mb-0">Akses seluruh menu akademik secara langsung dari panel sebelah kiri.</p>
    </div>
    <div class="row g-3">
        <div class="col-md-4"><a href="/presensi" class="card card-custom p-4 text-center text-decoration-none text-dark"><i class="fa-solid fa-fingerprint fa-3x text-primary mb-2"></i><h5>Presensi</h5></a></div>
        <div class="col-md-4"><a href="/jadwal" class="card card-custom p-4 text-center text-decoration-none text-dark"><i class="fa-solid fa-calendar-week fa-3x text-success mb-2"></i><h5>Jadwal</h5></a></div>
        <div class="col-md-4"><a href="/nilai" class="card card-custom p-4 text-center text-decoration-none text-dark"><i class="fa-solid fa-award fa-3x text-warning mb-2"></i><h5>Nilai</h5></a></div>
    </div>
    """
    return render_page("dashboard", "Dashboard Utama", tpl)


@app.route("/presensi", methods=["GET", "POST"])
def presensi():
    if request.method == "POST":
        STATUS_PRESENSI_SISWA["status"] = request.form["status"]
        STATUS_PRESENSI_SISWA["jam"] = datetime.now().strftime("%H:%M:%S")
        return redirect(
            url_for("presensi", msg="Presensi Berhasil Disimpan!")
        )

    tpl = """
    <div class="row g-4">
        <div class="col-md-6">
            <div class="card card-custom p-4">
                <h5 class="fw-bold mb-3">Form Presensi Harian</h5>
                <p>Status Presensi Hari Ini: <span class="badge bg-info">{{ p.status }} ({{ p.jam }})</span></p>
                <form method="POST">
                    <div class="mb-3">
                        <select name="status" class="form-select">
                            <option value="Hadir">Hadir Tepat Waktu</option>
                            <option value="Sakit">Sakit</option>
                            <option value="Izin">Izin</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Kirim Kehadiran</button>
                </form>
            </div>
        </div>
    </div>
    """
    return render_page(
        "presensi", "Presensi Kehadiran", tpl, p=STATUS_PRESENSI_SISWA
    )


@app.route("/jadwal")
def jadwal():
    tpl = """
    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3">Jadwal Pelajaran</h5>
        <table class="table table-hover">
            <thead><tr><th>Hari</th><th>Mata Pelajaran</th><th>Pengampu</th><th>Jam</th><th>Ruang</th></tr></thead>
            <tbody>
                {% for m in data %}
                <tr><td><span class="badge bg-secondary">{{ m.hari }}</span></td><td class="fw-bold">{{ m.nama }}</td><td>{{ m.guru }}</td><td>{{ m.jam }}</td><td>{{ m.ruang }}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    """
    return render_page("jadwal", "Jadwal Pelajaran", tpl, data=DATA_MAPEL)


@app.route("/tugas", methods=["GET", "POST"])
def tugas():
    if request.method == "POST":
        tid = int(request.form["tugas_id"])
        for t in DATA_TUGAS:
            if t["id"] == tid:
                t["status"] = "Selesai"
        return redirect(
            url_for("tugas", msg="Tugas Berhasil Dikumpulkan!")
        )

    tpl = """
    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3">Daftar Tugas & PR</h5>
        <table class="table table-hover align-middle">
            <thead><tr><th>Mata Pelajaran</th><th>Judul Tugas</th><th>Batas Waktu</th><th>Status</th><th>Aksi</th></tr></thead>
            <tbody>
                {% for t in data %}
                <tr>
                    <td class="fw-bold">{{ t.mapel }}</td><td>{{ t.judul }}</td><td>{{ t.dl }}</td>
                    <td><span class="badge {% if t.status == 'Selesai' %}bg-success{% else %}bg-warning{% endif %}">{{ t.status }}</span></td>
                    <td>
                        {% if t.status != 'Selesai' %}
                        <form method="POST" style="display:inline;">
                            <input type="hidden" name="tugas_id" value="{{ t.id }}">
                            <button type="submit" class="btn btn-sm btn-outline-primary"><i class="fa-solid fa-upload"></i> Upload Tugas</button>
                        </form>
                        {% else %}
                        <span class="text-success small"><i class="fa-solid fa-circle-check"></i> Terkirim</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    """
    return render_page("tugas", "Tugas & PR", tpl, data=DATA_TUGAS)


@app.route("/nilai")
def nilai():
    tpl = """
    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3">Transkrip Nilai Akademik</h5>
        <table class="table table-bordered">
            <thead class="table-light"><tr><th>Mata Pelajaran</th><th>Tugas</th><th>UTS</th><th>UAS</th><th>Nilai Akhir</th><th>Predikat</th></tr></thead>
            <tbody>
                <tr><td>Matematika Wajib</td><td>85</td><td>90</td><td>88</td><td class="fw-bold">87.6</td><td><span class="badge bg-success">A</span></td></tr>
                <tr><td>Fisika</td><td>80</td><td>85</td><td>82</td><td class="fw-bold">82.3</td><td><span class="badge bg-primary">B</span></td></tr>
                <tr><td>Kimia</td><td>90</td><td>88</td><td>92</td><td class="fw-bold">90.0</td><td><span class="badge bg-success">A</span></td></tr>
            </tbody>
        </table>
    </div>
    """
    return render_page("nilai", "Transkrip Nilai", tpl)


@app.route("/materi")
def materi():
    tpl = """
    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3">Materi & Modul Pembelajaran PDF</h5>
        <div class="list-group">
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div><b>[Matematika]</b> Bab 1 - Trigonometri Dasar.pdf</div>
                <button class="btn btn-sm btn-outline-primary" onclick="alert('Mengunduh Modul Matematika Bab 1...')"><i class="fa-solid fa-download me-1"></i> Unduh Modul</button>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div><b>[Fisika]</b> Bab 2 - Dinamika Rotasi & Benda Tegar.pdf</div>
                <button class="btn btn-sm btn-outline-primary" onclick="alert('Mengunduh Modul Fisika Bab 2...')"><i class="fa-solid fa-download me-1"></i> Unduh Modul</button>
            </div>
        </div>
    </div>
    """
    return render_page("materi", "Materi & Modul", tpl)


@app.route("/pengumuman", methods=["GET", "POST"])
def pengumuman():
    if request.method == "POST" and session.get("role") == "admin":
        DATA_PENGUMUMAN.insert(
            0,
            {
                "tgl": datetime.now().strftime("%Y-%m-%d"),
                "judul": request.form["judul"],
                "isi": request.form["isi"],
            },
        )
        return redirect(
            url_for("pengumuman", msg="Pengumuman Baru Berhasil Ditambahkan!")
        )

    tpl = """
    {% if session['role'] == 'admin' %}
    <div class="card card-custom p-4 mb-4">
        <h5 class="fw-bold mb-3">Buat Pengumuman Baru</h5>
        <form method="POST">
            <div class="mb-3"><input type="text" name="judul" class="form-control" placeholder="Judul Pengumuman" required></div>
            <div class="mb-3"><textarea name="isi" class="form-control" rows="3" placeholder="Isi Pengumuman" required></textarea></div>
            <button type="submit" class="btn btn-danger"><i class="fa-solid fa-bullhorn me-1"></i> Terbitkan Pengumuman</button>
        </form>
    </div>
    {% endif %}

    <div class="card card-custom p-4">
        <h5 class="fw-bold mb-3">Papan Pengumuman Sekolah</h5>
        {% for p in data %}
        <div class="border-bottom mb-3 pb-2">
            <span class="badge bg-secondary mb-1">{{ p.tgl }}</span>
            <h6 class="fw-bold text-primary mb-1">{{ p.judul }}</h6>
            <p class="text-muted mb-0 small">{{ p.isi }}</p>
        </div>
        {% endfor %}
    </div>
    """
    return render_page("pengumuman", "Pengumuman", tpl, data=DATA_PENGUMUMAN)


@app.route("/kartu")
def kartu():
    tpl = """
    <div class="d-flex justify-content-center">
        <div class="card card-custom p-4 text-center text-white bg-dark" style="max-width: 380px; border-radius: 20px;">
            <i class="fa-solid fa-graduation-cap fa-3x text-warning mb-2"></i>
            <h4 class="fw-bold">KARTU PELAJAR DIGITAL</h4>
            <hr class="border-secondary">
            <h5 class="fw-bold mb-0 text-info">{{ session['nama'] }}</h5>
            <p class="small text-muted mb-2">NISN: 0054829102</p>
            <span class="badge bg-success px-3 py-2 rounded-pill">Siswa Aktif SMA Premier</span>
        </div>
    </div>
    """
    return render_page("kartu", "Kartu Digital", tpl)


@app.route("/profil", methods=["GET", "POST"])
def profil():
    if request.method == "POST":
        session["nama"] = request.form["nama"]
        return redirect(
            url_for("profil", msg="Nama profil berhasil diperbarui!")
        )

    tpl = """
    <div class="card card-custom p-4" style="max-width: 500px;">
        <h5 class="fw-bold mb-3">Pengaturan Profil Saya</h5>
        <form method="POST">
            <div class="mb-3">
                <label class="form-label fw-bold">Nama Lengkap</label>
                <input type="text" name="nama" class="form-control" value="{{ session['nama'] }}" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-bold">Peran Hak Akses</label>
                <input type="text" class="form-control" value="{{ session['role'].upper() }}" readonly disabled>
            </div>
            <button type="submit" class="btn btn-primary"><i class="fa-solid fa-save me-1"></i> Simpan Perubahan</button>
        </form>
    </div>
    """
    return render_page("profil", "Profil Saya", tpl)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)