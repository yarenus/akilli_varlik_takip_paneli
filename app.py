from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3, qrcode, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'audit_log_system_2026'

QR_FOLDER = os.path.join('static', 'qrcodes')
if not os.path.exists(QR_FOLDER): os.makedirs(QR_FOLDER)

# --- TASARIM VE STİL ---
STYLE = """
<script src="https://cdn.tailwindcss.com"></script>
<style> 
    body { background: #020617; color: #e2e8f0; font-family: 'Inter', sans-serif; } 
    .glass { background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; }
    .log-row:hover { background: rgba(59, 130, 246, 0.1); } 
</style>
"""

DASHBOARD_TASARIMI = """
{{ STYLE|safe }}
<div class="min-h-screen p-8">
    <div class="max-w-7xl mx-auto flex justify-between items-center mb-8">
        <h1 class="text-3xl font-black tracking-tighter text-white">AKILLI VARLIK TAKİP PANELİ🏷️</h1>
        <div class="flex gap-4">
            <a href="/dashboard" class="bg-blue-900/20 text-blue-400 border border-blue-900/50 px-4 py-2 rounded-lg hover:bg-blue-600 transition text-xs font-bold">YENİLE</a>
            <a href="/logout" class="bg-red-900/20 text-red-400 border border-red-900/50 px-4 py-2 rounded-lg hover:bg-red-600 hover:text-white transition text-xs font-bold">ÇIKIŞ</a>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="glass p-6 h-fit">
            <h3 class="text-blue-400 font-bold mb-4"> VARLIK KAYDI📋</h3>
            <form action="/item_ekle" method="POST" class="space-y-4 mb-8">
                <input type="text" name="item_name" placeholder="Eşya Adı" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500" required>
                <button class="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-lg font-bold transition">SİSTEME EKLE</button>
            </form>
            
            <div class="overflow-y-auto max-h-[500px]">
                <table class="w-full text-left">
                    <thead>
                        <tr class="text-gray-500 text-[10px] uppercase border-b border-slate-800">
                            <th class="p-4">VARLIK</th>
                            <th class="p-4 text-center">QR</th>
                            <th class="p-4 text-right">İŞLEM</th>
                        </tr>
                    </thead>
                    <tbody>{{ table_html|safe }}</tbody>
                </table>
            </div>
        </div>

        <div class="lg:col-span-2 glass p-6 overflow-hidden">
            <h3 class="text-green-400 font-bold mb-4">🔍 GÜVENLİK DENETİM İZİ  </h3>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="text-gray-500 text-[10px] uppercase border-b border-slate-800">
                            <th class="p-3 text-left text-xs">ZAMAN</th>
                            <th class="p-3 text-left text-xs">EYLEM</th>
                            <th class="p-3 text-left text-xs">DETAY / KONUM</th>
                            <th class="p-3 text-left text-xs">IP</th>
                        </tr>
                    </thead>
                    <tbody>{{ log_html|safe }}</tbody>
                </table>
            </div>
        </div>
    </div>
</div>
"""


def get_db():
    conn = sqlite3.connect('takip_sistemi.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS items 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             item_name TEXT, 
             unique_code TEXT)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS system_logs 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             action_type TEXT, 
             details TEXT, 
             ip_address TEXT,
             timestamp TEXT)''')
        conn.commit()


def add_log(action_type, details):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Cihaz bilgisini daha detaylı yakalamak için user-agent kullanımı
    agent = request.user_agent
    brand = "Mobil Cihaz" if agent.platform in ['iphone', 'android'] else "Bilgisayar"
    browser = agent.browser.capitalize() if agent.browser else ""
    device_info = f"{brand} ({agent.platform}) - {browser}"
    
    details = f"{details} | Cihaz: {device_info}"
    time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with get_db() as conn:
        conn.execute("INSERT INTO system_logs (action_type, details, ip_address, timestamp) VALUES (?,?,?,?)",
                     (action_type, details, ip, time))
        conn.commit()
def get_location(ip):
    return "Amasya, Türkiye"


@app.route('/')
def index():
    if 'user' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('register'))

@app.route('/kayit', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        
        with get_db() as conn:
            # kullanıcı var mı kontrol etme
            existing_user = conn.execute("SELECT * FROM users WHERE username = ?", (user,)).fetchone()
            
            if existing_user:
                # Kullanıcı varsa şifreyi kontrol et
                if existing_user['password'] == pw:
                    session['user'] = user
                    add_log('SİSTEME GİRİŞ', f'"{user}" giriş yaptı.')
                    return redirect(url_for('dashboard'))
                else:
                    return render_template_string(f"{STYLE}<div class='flex h-screen items-center justify-center'><div class='glass p-10 text-center'><h2 class='text-red-400 font-bold'>Hatalı Şifre!</h2><a href='/kayit' class='text-blue-400 underline'>Tekrar Dene</a></div></div>")
            else:
                # Kullanıcı yoksa yeni kayıt oluştur
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pw))
                conn.commit()
                session['user'] = user
                add_log('YENİ KAYIT', f'"{user}" hesabı oluşturuldu ve giriş yapıldı.')
                return redirect(url_for('dashboard'))
                
    return render_template_string(f"""{STYLE}
        <div class='flex h-screen items-center justify-center'>
            <form method='post' class='glass p-10 w-96'>
                <h2 class='text-2xl font-bold mb-6 text-center text-blue-400'>🛡️Kullanıcı-Envanter Girişi</h2>
                <input name='username' placeholder='Yönetici Adı' class='w-full p-3 mb-4 rounded bg-slate-800 text-white border border-slate-700' required>
                <input type='password' name='password' placeholder='Güvenlik Şifresi' class='w-full p-3 mb-6 rounded bg-slate-800 text-white border border-slate-700' required>
                <button class='w-full bg-blue-600 py-3 rounded font-bold hover:bg-blue-500 transition'>Sistemi Başlat</button>
                <p class='text-[10px] text-gray-500 mt-4 text-center'>*İlk girişte yazdığınız şifre parolanız olarak belirlenir.</p>
            </form>
        </div>""")
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    with get_db() as conn:
        # İŞTE BURASI: items ve system_logs tablolarını birleştiriyoruz
        query = """
            SELECT 
                system_logs.log_id, 
                system_logs.action_type, 
                system_logs.ip_address, 
                system_logs.timestamp, 
                items.item_name 
            FROM system_logs 
            LEFT JOIN items ON system_logs.details LIKE '%' || items.unique_code || '%'
            ORDER BY system_logs.timestamp DESC
        """
        logs = conn.execute(query).fetchall()
        items = conn.execute("SELECT * FROM items").fetchall()
        
    return render_template('dashboard.html', items=items, logs=logs)

@app.route('/item_ekle', methods=['POST'])
def add_item():
    name = request.form.get('item_name')
    code = os.urandom(3).hex()
    
    
    qr_link = f"http://10.149.137.1:5000/label/{code}"
    
    
    qrcode.make(qr_link).save(f"static/qrcodes/{code}.png")
    
    with get_db() as conn:
        conn.execute("INSERT INTO items (item_name, unique_code) VALUES (?, ?)", (name, code))
        conn.commit()
    
    add_log('VERİ EKLEME', f"Yeni varlık: {name}")
    return redirect(url_for('dashboard'))

@app.route('/label/<code>')
def label(code):
    with get_db() as conn:
        # Veritabanından eşya ismini çekiyoruz
        item = conn.execute("SELECT item_name FROM items WHERE unique_code = ?", (code,)).fetchone()
        
    if not item:
        return "Varlık bulunamadı!", 404
        
    item_name = item['item_name']
    
    
    add_log('QR TARAMA', f"'{item_name}' adlı varlık tarandı. Konum: {get_location(request.remote_addr)}")

    
    return render_template_string(f"""
    {STYLE}
    <div class="flex h-screen items-center justify-center p-6">
        <div class="glass p-8 w-full max-w-md text-center">
            <h2 class="text-2xl font-bold text-blue-400 mb-2">📦 {item_name.upper()} BULUNDU</h2>
            <p class="text-gray-400 mb-6">Şu an <strong>{item_name}</strong> adlı varlığı denetliyorsunuz.</p>
            
            <form action="/bildir/{code}" method="POST" class="space-y-4">
                <textarea name="msg" placeholder="Güvenlik notu bırakın (Örn: Rektörlük binasına bıraktım)..." 
                          class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:outline-none" rows="3" required></textarea>
                
                <input type="text" name="contact" placeholder="Adınız veya Telefonunuz (İsteğe bağlı)" 
                       class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:outline-none text-sm">
                
                <button class="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-lg font-bold transition text-white uppercase">
                    BİLDİRİMİ GÖNDER
                </button>
            </form>
        </div>
    </div>
    """)

@app.route('/bildir/<code>', methods=['POST'])
def bildir(code):
    msg = request.form.get('msg')
    contact = request.form.get('contact', 'Anonim') 
    
    with get_db() as conn:
        item = conn.execute("SELECT item_name FROM items WHERE unique_code = ?", (code,)).fetchone()
        item_name = item['item_name'] if item else code
    
   
    log_detayi = f"'{item_name}' için not: {msg} | İletişim: {contact}"
    add_log('GÜVENLİK BİLDİRİMİ', log_detayi)
    
   
    return render_template_string(f"{STYLE}<div class='flex h-screen items-center justify-center'><div class='glass p-12 text-center'><h2 class='text-3xl font-bold text-green-400'>İŞLEM BAŞARILI</h2><p class='mt-4 text-gray-400'>Bildiriminiz güvenli ağ üzerinden gönderildi.</p><a href='/dashboard' class='mt-6 inline-block text-blue-400 underline'>Panele Dön</a></div></div>")

@app.route('/sil/<code>')
def sil(code):
    if 'user' not in session: return redirect(url_for('register'))
    
    with get_db() as conn:
       
        item = conn.execute("SELECT item_name FROM items WHERE unique_code = ?", (code,)).fetchone()
        
        if item:
            item_name = item['item_name']
            # Veritabanından silme işlemi
            conn.execute("DELETE FROM items WHERE unique_code = ?", (code,))
            conn.commit()
            
            
            try:
                add_log('VARLIK SİLİNDİ', f"'{item_name}' (Kod: {code}) sistemden tamamen silindi.")
            except:
                print("Log tablosu bulunamadığı için silme işlemi loglanamadı.")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('register'))

if __name__ == '__main__':
    init_db() 
    app.run(debug=True, host='0.0.0.0', port=5000)