const express = require('express');
const session = require('express-session');
const path = require('path');

const app = express();

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(session({
    secret: 'siakad_nodejs_secret_key',
    resave: false,
    saveUninitialized: true
}));

// ==========================================
// DATA DUMMY INTERAKTIF (LOKAL)
// ==========================================
let dataSiswa = [
    { id: 1, nisn: '0054829102', nama: 'Budi Santoso', kelas: 'XII-IPA-1', jk: 'Laki-laki', status: 'Aktif' },
    { id: 2, nisn: '0054829103', nama: 'Siti Aminah', kelas: 'XII-IPA-1', jk: 'Perempuan', status: 'Aktif' }
];

let dataGuru = [
    { id: 1, nip: '198501152010011001', nama: 'Drs. Budi Santoso', mapel: 'Matematika', status: 'PNS' },
    { id: 2, nip: '199003202015022002', nama: 'Siti Nurhaliza, M.Pd', mapel: 'Fisika', status: 'PNS' }
];

let dataMapel = [
    { kode: 'MTK01', nama: 'Matematika Wajib', guru: 'Drs. Budi Santoso', hari: 'Senin', jam: '07:30 - 09:00', ruang: 'XII-IPA-1' },
    { kode: 'FIS01', nama: 'Fisika', guru: 'Siti Nurhaliza, M.Pd', hari: 'Senin', jam: '09:15 - 10:45', ruang: 'Lab Fisika' },
    { kode: 'KIM01', nama: 'Kimia', guru: 'Ahmad Subagja, S.Si', hari: 'Selasa', jam: '07:30 - 09:00', ruang: 'Lab Kimia' }
];

let dataTugas = [
    { id: 1, mapel: 'Matematika', judul: 'Latihan Soal Trigonometri', dl: '2026-10-01', status: 'Belum Dikerjakan' },
    { id: 2, mapel: 'Fisika', judul: 'Laporan Praktikum Hukum Newton', dl: '2026-10-05', status: 'Selesai' }
];

let dataPengumuman = [
    { tgl: '2026-09-20', judul: 'Pelaksanaan UTS Semester Ganjil', isi: 'UTS akan dilaksanakan secara serentak mulai tanggal 12 Oktober 2026.' },
    { tgl: '2026-09-15', judul: 'Kegiatan Ekstrakurikuler Wajib', isi: 'Seluruh siswa kelas X dan XI wajib mengikuti kegiatan Pramuka.' }
];

let statusPresensi = { status: 'Belum Absen', jam: '-' };

// Middleware Cek Auth
function authCheck(req, res, next) {
    if (!req.session.user) return res.redirect('/login');
    next();
}

// ==========================================
// ROUTING APLIKASI
// ==========================================

// Login Page
app.get('/login', (req, res) => {
    res.render('login', { msg: req.query.msg || null });
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    if (username === 'admin' && password === 'admin') {
        req.session.user = { nama: 'Administrator Utama', role: 'admin' };
        return res.redirect('/admin/dashboard');
    } else if (username === 'guru' && password === 'guru') {
        req.session.user = { nama: 'Siti Nurhaliza, M.Pd', role: 'guru' };
        return res.redirect('/dashboard');
    } else if (username === 'siswa' && password === 'siswa') {
        req.session.user = { nama: 'Budi Santoso', role: 'siswa' };
        return res.redirect('/dashboard');
    }
    res.redirect('/login?msg=Username atau Password Salah!');
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/login');
});

// Admin Routes
app.get('/admin/dashboard', authCheck, (req, res) => {
    res.render('layout', {
        page: 'admin_dashboard',
        page_title: 'Dashboard Administrator',
        session: req.session.user,
        msg: req.query.msg,
        dataSiswa, dataGuru, dataMapel, dataPengumuman
    });
});

app.get('/admin/siswa', authCheck, (req, res) => {
    res.render('layout', {
        page: 'admin_siswa',
        page_title: 'Kelola Data Siswa',
        session: req.session.user,
        msg: req.query.msg,
        dataSiswa
    });
});

app.post('/admin/siswa/tambah', authCheck, (req, res) => {
    const { nisn, nama, kelas, jk } = req.body;
    dataSiswa.push({ id: dataSiswa.length + 1, nisn, nama, kelas, jk, status: 'Aktif' });
    res.redirect('/admin/siswa?msg=Siswa Baru Berhasil Ditambahkan!');
});

app.get('/admin/siswa/hapus/:id', authCheck, (req, res) => {
    dataSiswa = dataSiswa.filter(s => s.id != req.params.id);
    res.redirect('/admin/siswa?msg=Data Siswa Berhasil Dihapus!');
});

app.get('/admin/guru', authCheck, (req, res) => {
    res.render('layout', {
        page: 'admin_guru',
        page_title: 'Kelola Data Guru',
        session: req.session.user,
        msg: req.query.msg,
        dataGuru
    });
});

app.post('/admin/guru/tambah', authCheck, (req, res) => {
    const { nip, nama, mapel } = req.body;
    dataGuru.push({ id: dataGuru.length + 1, nip, nama, mapel, status: 'PNS' });
    res.redirect('/admin/guru?msg=Guru Baru Berhasil Ditambahkan!');
});

app.get('/admin/mapel', authCheck, (req, res) => {
    res.render('layout', {
        page: 'admin_mapel',
        page_title: 'Kelola Mata Pelajaran',
        session: req.session.user,
        msg: req.query.msg,
        dataMapel
    });
});

app.get('/admin/rekap', authCheck, (req, res) => {
    res.render('layout', {
        page: 'admin_rekap',
        page_title: 'Rekapitulasi Laporan',
        session: req.session.user,
        msg: req.query.msg
    });
});

// Siswa/Guru Routes
app.get('/dashboard', authCheck, (req, res) => {
    res.render('layout', {
        page: 'dashboard',
        page_title: 'Dashboard Utama',
        session: req.session.user,
        msg: req.query.msg
    });
});

app.get('/presensi', authCheck, (req, res) => {
    res.render('layout', {
        page: 'presensi',
        page_title: 'Presensi Kehadiran',
        session: req.session.user,
        msg: req.query.msg,
        statusPresensi
    });
});

app.post('/presensi', authCheck, (req, res) => {
    const now = new Date();
    statusPresensi.status = req.body.status;
    statusPresensi.jam = now.toLocaleTimeString();
    res.redirect('/presensi?msg=Presensi Berhasil Disimpan!');
});

app.get('/jadwal', authCheck, (req, res) => {
    res.render('layout', {
        page: 'jadwal',
        page_title: 'Jadwal Pelajaran',
        session: req.session.user,
        msg: req.query.msg,
        dataMapel
    });
});

app.get('/tugas', authCheck, (req, res) => {
    res.render('layout', {
        page: 'tugas',
        page_title: 'Tugas & PR',
        session: req.session.user,
        msg: req.query.msg,
        dataTugas
    });
});

app.post('/tugas/upload', authCheck, (req, res) => {
    const { tugas_id } = req.body;
    const item = dataTugas.find(t => t.id == tugas_id);
    if (item) item.status = 'Selesai';
    res.redirect('/tugas?msg=Tugas Berhasil Dikumpulkan!');
});

app.get('/nilai', authCheck, (req, res) => {
    res.render('layout', {
        page: 'nilai',
        page_title: 'Transkrip Nilai Akademik',
        session: req.session.user,
        msg: req.query.msg
    });
});

app.get('/materi', authCheck, (req, res) => {
    res.render('layout', {
        page: 'materi',
        page_title: 'Materi & Modul Pembelajaran',
        session: req.session.user,
        msg: req.query.msg
    });
});

app.get('/pengumuman', authCheck, (req, res) => {
    res.render('layout', {
        page: 'pengumuman',
        page_title: 'Pusat Pengumuman',
        session: req.session.user,
        msg: req.query.msg,
        dataPengumuman
    });
});

app.post('/pengumuman/tambah', authCheck, (req, res) => {
    const { judul, isi } = req.body;
    const tgl = new Date().toISOString().split('T')[0];
    dataPengumuman.unshift({ tgl, judul, isi });
    res.redirect('/pengumuman?msg=Pengumuman Berhasil Diterbitkan!');
});

app.get('/kartu', authCheck, (req, res) => {
    res.render('layout', {
        page: 'kartu',
        page_title: 'Kartu Pelajar Digital',
        session: req.session.user,
        msg: req.query.msg
    });
});

app.get('/profil', authCheck, (req, res) => {
    res.render('layout', {
        page: 'profil',
        page_title: 'Pengaturan Profil Saya',
        session: req.session.user,
        msg: req.query.msg
    });
});

app.post('/profil', authCheck, (req, res) => {
    req.session.user.nama = req.body.nama;
    res.redirect('/profil?msg=Nama Profil Berhasil Diperbarui!');
});

app.get('/', (req, res) => res.redirect('/login'));

app.listen(3000, () => {
    console.log('Server SIAKAD Node.js berjalan di http://localhost:3000');
});