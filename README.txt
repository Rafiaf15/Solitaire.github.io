# Solitaire Game dengan Flask

Game Solitaire web interaktif yang dibuat dengan Flask, HTML, CSS, dan JavaScript dengan fitur drag-and-drop.

## Struktur Folder

```
solitaire_game/
├── app.py                  # File utama Flask application
├── requirements.txt        # Dependencies Python
├── templates/
│   └── index.html         # Template HTML utama
└── README.md              # File ini
```

## Setup dan Instalasi

### 1. Buat Folder Project
```bash
mkdir solitaire_game
cd solitaire_game
```

### 2. Buat Virtual Environment (Opsional tapi disarankan)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Buat Struktur Folder
```bash
mkdir templates
```

### 5. Copy Files
- Copy kode `app.py` ke file `app.py`
- Copy kode HTML ke file `templates/index.html`
- Copy `requirements.txt`

### 6. Jalankan Aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## Fitur Game

### Gameplay
- **Klondike Solitaire** - Versi solitaire yang paling populer
- **Drag & Drop** - Interface yang mudah digunakan
- **Auto Move** - Otomatis memindahkan kartu ke foundation
- **Scoring System** - Sistem poin dengan bonus
- **Move Counter** - Menghitung jumlah gerakan

### Controls
- **Klik Deck** - Ambil kartu dari deck ke waste pile
- **Drag Kartu** - Seret kartu untuk memindahkan
- **Auto Move** - Otomatis pindahkan kartu yang bisa ke foundation
- **Game Baru** - Mulai permainan baru

### Aturan Permainan
1. **Tableau**: Susun kartu menurun dengan warna bergantian (merah-hitam)
2. **Foundation**: Susun kartu naik dari A-K dengan suit yang sama
3. **Menang**: Semua kartu berhasil dipindahkan ke foundation

## API Endpoints

- `GET /` - Halaman utama game
- `GET /api/game-state` - Mendapatkan state permainan
- `POST /api/new-game` - Memulai permainan baru
- `POST /api/draw-card` - Mengambil kartu dari deck
- `POST /api/move-card` - Memindahkan kartu
- `POST /api/auto-move` - Auto move ke foundation

## Teknologi yang Digunakan

### Backend
- **Flask** - Web framework Python
- **Python Session** - Menyimpan state permainan
- **UUID** - Unique identifier untuk kartu

### Frontend
- **HTML5** - Struktur halaman
- **CSS3** - Styling dan animasi
- **JavaScript ES6** - Interaktivitas dan API calls
- **Drag & Drop API** - Untuk memindahkan kartu

## Customization

### Mengubah Scoring
Edit fungsi di `app.py`:
```python
# Di method move_card()
if target_type == 'foundation':
    self.score += 10  # Ubah nilai ini
elif target_type == 'tableau':
    self.score += 5   # Ubah nilai ini
```

### Mengubah Tampilan
Edit CSS di `templates/index.html`:
- Warna background: `.body { background: ... }`
- Warna kartu: `.card { background: ... }`
- Animasi: Ubah `transition` properties

### Menambah Fitur Hint
Tambahkan method di class `SolitaireGame`:
```python
def get_possible_moves(self):
    """Mengembalikan list gerakan yang mungkin"""
    # Implementation hint system
    pass
```

## Troubleshooting

### Error "Template not found"
Pastikan folder `templates/` ada dan file `index.html` ada di dalamnya.

### Error "Module not found"
Pastikan sudah install dependencies:
```bash
pip install flask
```

### Game tidak menyimpan state
Flask menggunakan session untuk menyimpan state. Pastikan `secret_key` sudah diset di `app.py`.

### Drag & Drop tidak bekerja
Pastikan browser mendukung HTML5 Drag & Drop API. Tested di Chrome, Firefox, Safari modern.

## Development

### Menjalankan dalam Mode Debug
```bash
export FLASK_ENV=development  # Linux/macOS
set FLASK_ENV=development     # Windows
python app.py
```

### Testing
Untuk testing manual:
1. Buka browser ke `http://localhost:5000`
2. Test semua fitur: drag-drop, draw card, auto move
3. Test win condition dengan cheat/debug

### Deployment
Untuk production, ubah:
```python
app.secret_key = 'your-production-secret-key'
app.run(debug=False, host='0.0.0.0')
```

## Screenshots

Game akan terlihat seperti:
- Header dengan judul dan info skor/gerakan
- Area deck dan waste pile
- 4 foundation piles dengan symbol suit
- 7 tableau columns
- Responsive design untuk mobile

## License

Free to use and modify for educational purposes.

## Contributing

Feel free to fork and submit pull requests untuk improvements!