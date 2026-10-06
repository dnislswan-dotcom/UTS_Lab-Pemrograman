from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
# Secret key dibutuhkan untuk menggunakan fitur 'flash' (pesan error/sukses)
app.secret_key = 'kunci_rahasia_uts' 

# Fungsi untuk koneksi ke database
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',        # Sesuaikan dengan user MySQL Anda
            password='',        # Sesuaikan dengan password MySQL Anda (kosongkan jika default XAMPP)
            database='uts_pemrograman'
        )
        return connection
    except Error as e:
        print(f"Error koneksi ke MySQL: {e}")
        return None

# ================= READ =================
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM mahasiswa")
    mahasiswa = cursor.fetchall()
    
    # Hitung Lama Studi
    tahun_sekarang = datetime.now().year
    for mhs in mahasiswa:
        mhs['lama_studi'] = tahun_sekarang - mhs['angkatan']
        
    cursor.close()
    conn.close()
    
    return render_template('index.html', data=mahasiswa)

# ================= CREATE =================
@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        nim = request.form['nim']
        nama = request.form['nama']
        program_studi = request.form['program_studi']
        angkatan = request.form['angkatan']
        ipk = request.form['ipk']

        # Validasi Wajib Diisi
        if not nim or not nama or not program_studi or not angkatan or not ipk:
            flash("Error: Semua data wajib diisi (NIM, Nama, Program Studi, Angkatan, IPK)!", "error")
            return redirect(url_for('tambah'))

        # Validasi IPK
        if not (0.00 <= float(ipk) <= 4.00):
            flash("Error: IPK harus berada di rentang 0.00 hingga 4.00!", "error")
            return redirect(url_for('tambah'))

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO mahasiswa (nim, nama, program_studi, angkatan, ipk) VALUES (%s, %s, %s, %s, %s)",
                (nim, nama, program_studi, angkatan, ipk)
            )
            conn.commit()
            flash("Data mahasiswa berhasil ditambahkan!", "success")
            return redirect(url_for('index'))
        except mysql.connector.IntegrityError:
            # Validasi NIM unik
            flash(f"Error: Mahasiswa dengan NIM {nim} sudah terdaftar!", "error")
            return redirect(url_for('tambah'))
        finally:
            cursor.close()
            conn.close()

    return render_template('tambah.html')

# ================= UPDATE =================
@app.route('/edit/<int:nim>', methods=['GET', 'POST'])
def edit(nim):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nama = request.form['nama']
        program_studi = request.form['program_studi']
        angkatan = request.form['angkatan']
        ipk = request.form['ipk']

        # Validasi input
        if not nama or not program_studi or not angkatan or not ipk:
            flash("Error: Nama, Program Studi, Angkatan, dan IPK tidak boleh kosong!", "error")
            return redirect(url_for('edit', nim=nim))

        if not (0.00 <= float(ipk) <= 4.00):
            flash("Error: IPK harus berada di rentang 0.00 hingga 4.00!", "error")
            return redirect(url_for('edit', nim=nim))

        cursor.execute(
            "UPDATE mahasiswa SET nama=%s, program_studi=%s, angkatan=%s, ipk=%s WHERE nim=%s",
            (nama, program_studi, angkatan, ipk, nim)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Data mahasiswa berhasil diubah!", "success")
        return redirect(url_for('index'))

    # Jika GET, ambil data untuk ditampilkan di form edit
    cursor.execute("SELECT * FROM mahasiswa WHERE nim = %s", (nim,))
    mhs = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('edit.html', mhs=mhs)

# ================= DELETE =================
@app.route('/hapus/<int:nim>', methods=['POST'])
def hapus(nim):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mahasiswa WHERE nim = %s", (nim,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Data mahasiswa berhasil dihapus!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)