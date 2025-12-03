# Setup Database MySQL untuk Kedai Hauna POS

## Langkah-langkah Setup:

### 1. Install XAMPP
- Download XAMPP dari https://www.apachefriends.org/
- Install XAMPP di komputer Anda
- Jalankan XAMPP Control Panel

### 2. Start MySQL Service
- Buka XAMPP Control Panel
- Klik tombol **Start** pada MySQL
- Pastikan status MySQL menjadi **Running** (hijau)

### 3. Buat Database
- Klik tombol **Admin** pada MySQL di XAMPP Control Panel
- Atau buka browser dan akses: http://localhost/phpmyadmin
- Klik tab **SQL**
- Copy semua isi file `database.sql`
- Paste ke SQL editor
- Klik tombol **Go** untuk execute

### 4. Install Python Dependencies
```bash
pip install mysql-connector-python
```

Atau install semua dependencies:
```bash
pip install -r requirements.txt
```

### 5. Konfigurasi Database (Opsional)
Jika password MySQL Anda bukan default, edit file `db_config.py`:

```python
self.host = "localhost"
self.user = "root"
self.password = ""  # Ganti dengan password MySQL Anda
self.database = "kedai_hauna"
```

### 6. Jalankan Aplikasi
```bash
python kasir_tkinter_v2.py
```

## Fitur Database:

✅ **Auto-save ke MySQL** - Setiap transaksi otomatis tersimpan ke database
✅ **Backup JSON** - Tetap menyimpan backup di transactions.json
✅ **Offline Mode** - Jika MySQL tidak tersedia, otomatis pakai JSON
✅ **Real-time Stats** - Statistik langsung dari database
✅ **Transaction History** - Riwayat transaksi tersimpan permanen

## Troubleshooting:

### Error: "Tidak dapat terhubung ke database"
**Solusi:**
1. Pastikan XAMPP sudah running
2. Pastikan MySQL service aktif (hijau di XAMPP)
3. Pastikan database 'kedai_hauna' sudah dibuat
4. Cek username/password di db_config.py

### Error: "Table doesn't exist"
**Solusi:**
1. Buka phpMyAdmin
2. Jalankan ulang file database.sql
3. Pastikan semua tabel ter-create

### Aplikasi tetap pakai JSON
**Solusi:**
- Aplikasi akan otomatis fallback ke JSON jika MySQL error
- Cek console untuk error message
- Fix error MySQL, lalu restart aplikasi

## Struktur Database:

### Tabel: transactions
- id (Primary Key)
- transaction_id (Unique)
- customer_name
- payment_method
- subtotal, tax, total
- created_at (Timestamp)

### Tabel: transaction_items
- id (Primary Key)
- transaction_id (Foreign Key)
- item_id, item_name, variant
- price, quantity, subtotal

### Tabel: menu_items (Opsional)
- id, name, price
- image_path, has_variant, variants
- is_active, created_at

## Keuntungan Pakai MySQL:

1. **Data Permanen** - Tidak hilang meski aplikasi ditutup
2. **Multi-user** - Bisa diakses dari beberapa komputer
3. **Backup Mudah** - Export database dari phpMyAdmin
4. **Query Cepat** - Pencarian dan filter lebih cepat
5. **Scalable** - Bisa handle ribuan transaksi

## Migrasi dari JSON ke MySQL:

Jika Anda sudah punya data di transactions.json, data akan tetap tersimpan sebagai backup. Transaksi baru akan otomatis masuk ke MySQL.
