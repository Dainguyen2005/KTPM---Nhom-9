import sqlite3
from config import DB, MOVIES, SHOWTIMES, VOUCHERS, COMBOS

def get_db():
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row
    return conn

def add_column_if_missing(conn,table,column,definition):
    cols=[r['name'] for r in conn.execute(f'PRAGMA table_info({table})').fetchall()]
    if column not in cols: conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')

def init_db():
    conn=get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'user',points INTEGER NOT NULL DEFAULT 0)")
    conn.execute("CREATE TABLE IF NOT EXISTS movies(id INTEGER PRIMARY KEY,title TEXT NOT NULL,genre TEXT NOT NULL,duration INTEGER NOT NULL,poster TEXT DEFAULT '',description TEXT DEFAULT '',status TEXT NOT NULL DEFAULT 'Đang chiếu',trailer TEXT DEFAULT '')")
    conn.execute("CREATE TABLE IF NOT EXISTS showtimes(id INTEGER PRIMARY KEY,movie_id INTEGER NOT NULL,province TEXT DEFAULT 'Hà Nội',cinema TEXT NOT NULL,date TEXT NOT NULL,time TEXT NOT NULL,room TEXT DEFAULT 'Phòng 1',format TEXT DEFAULT '2D',price INTEGER NOT NULL DEFAULT 90000,single_price INTEGER NOT NULL DEFAULT 90000,double_price INTEGER NOT NULL DEFAULT 150000,vip_price INTEGER NOT NULL DEFAULT 120000)")
    conn.execute("CREATE TABLE IF NOT EXISTS vouchers(code TEXT PRIMARY KEY,type TEXT NOT NULL,value INTEGER NOT NULL,label TEXT NOT NULL,active INTEGER NOT NULL DEFAULT 1)")
    conn.execute("CREATE TABLE IF NOT EXISTS combos(id INTEGER PRIMARY KEY,name TEXT NOT NULL,description TEXT DEFAULT '',price INTEGER NOT NULL,active INTEGER NOT NULL DEFAULT 1)")
    conn.execute("CREATE TABLE IF NOT EXISTS rooms(id INTEGER PRIMARY KEY AUTOINCREMENT,province TEXT NOT NULL,cinema TEXT NOT NULL,name TEXT NOT NULL,active INTEGER NOT NULL DEFAULT 1,single_price INTEGER NOT NULL DEFAULT 90000,double_price INTEGER NOT NULL DEFAULT 150000,vip_price INTEGER NOT NULL DEFAULT 120000,UNIQUE(cinema,name))")
    conn.execute("CREATE TABLE IF NOT EXISTS room_seats(id INTEGER PRIMARY KEY AUTOINCREMENT,room_id INTEGER NOT NULL,code TEXT NOT NULL,seat_type TEXT NOT NULL,active INTEGER NOT NULL DEFAULT 1,UNIQUE(room_id,code))")
    conn.execute("CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,customer_name TEXT NOT NULL,phone TEXT NOT NULL,movie_id INTEGER NOT NULL,showtime_id INTEGER NOT NULL,seats TEXT NOT NULL,total INTEGER NOT NULL,payment_method TEXT NOT NULL DEFAULT 'Chưa thanh toán',payment_status TEXT NOT NULL DEFAULT 'Chưa thanh toán',original_total INTEGER NOT NULL DEFAULT 0,discount INTEGER NOT NULL DEFAULT 0,voucher_code TEXT DEFAULT '',combo_items TEXT DEFAULT '',combo_total INTEGER NOT NULL DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP,status TEXT NOT NULL DEFAULT 'Đã đặt',ticket_code TEXT DEFAULT '',ticket_name TEXT DEFAULT '')")
    add_column_if_missing(conn,'movies','trailer',"TEXT DEFAULT ''")
    add_column_if_missing(conn,'showtimes','province',"TEXT DEFAULT 'Hà Nội'")
    add_column_if_missing(conn,'showtimes','single_price','INTEGER NOT NULL DEFAULT 0')
    add_column_if_missing(conn,'showtimes','double_price','INTEGER NOT NULL DEFAULT 0')
    add_column_if_missing(conn,'showtimes','vip_price','INTEGER NOT NULL DEFAULT 0')
    for c,d in [('role',"TEXT NOT NULL DEFAULT 'user'"),('points','INTEGER NOT NULL DEFAULT 0')]: add_column_if_missing(conn,'users',c,d)
    for c,d in [('combo_items',"TEXT DEFAULT ''"),('combo_total','INTEGER NOT NULL DEFAULT 0'),('payment_method',"TEXT NOT NULL DEFAULT 'Chưa thanh toán'"),('payment_status',"TEXT NOT NULL DEFAULT 'Chưa thanh toán'"),('original_total','INTEGER NOT NULL DEFAULT 0'),('discount','INTEGER NOT NULL DEFAULT 0'),('voucher_code',"TEXT DEFAULT ''"),('created_at','TEXT DEFAULT CURRENT_TIMESTAMP'),('status',"TEXT NOT NULL DEFAULT 'Đã đặt'"),('ticket_code',"TEXT DEFAULT ''"),('ticket_name',"TEXT DEFAULT ''")]: add_column_if_missing(conn,'tickets',c,d)

    # Seed demo movies only when the table is empty. Admin edits must survive restart.
    if conn.execute('SELECT COUNT(*) FROM movies').fetchone()[0] == 0:
        for m in MOVIES:
            conn.execute('INSERT INTO movies(id,title,genre,duration,poster,description,status,trailer) VALUES(?,?,?,?,?,?,?,?)',(m['id'],m['title'],m['genre'],m['duration'],m['poster'],m['description'],m['status'],m['trailer']))

    # Repair known broken default demo poster URLs in existing databases.
    # Only replace known URLs from this project's defaults; preserve posters set manually by Admin.
    poster_repairs = {
        7: (
            'https://wikizilla-images.s3.us-east-va.perf.cloud.ovh.us/6/61/GxKTNE_DarkPoster.png',
            ['https://image.tmdb.org/t/p/w500/1R7L7Y5M4w8b6n4m5c2Xv5hK9pD.jpg'],
        ),
        8: (
            'https://images.contentstack.io/v3/assets/blt13adb7e2033fcee5/blt1e1cf5d611f2c0b1/692babb5ea1ba383ac47d99d/KungFuPanda4_keyart_desktop_2000x3000.jpg?width=2560',
            [
                'https://image.tmdb.org/t/p/w500/kDp1vUBnMpe8ak4rjgl3cLELq7u.jpg',
                'https://images.contentstack.io/v3/assets/blt13adb7e2033fcee5/blt6e141555629644b7/693390d4c039e66219300868/KungFuPanda4_Digital_Poster.jpg?width=1000',
            ],
        ),
        10: (
            'https://image.tmdb.org/t/p/w500/n3Z0VF6LhtbgG6mgZnd6wDRdXHN.jpg',
            [
                'https://image.tmdb.org/t/p/w500/exBqFnXUFMZkAGfcOv6GbIMg6iW.jpg',
                'https://image.tmdb.org/t/p/w500/xDGbZ0JJ3mYaGKy4Nzd9Kph6M9D.jpg',
                'https://www.impawards.com/2024/posters/wicked.jpg',
                'https://www.impawards.com/2024/wicked.html',
            ],
        ),
        13: (
            'https://image.tmdb.org/t/p/w500/hwmwTFtMbzxAWbIOp1RyyiOCyx0.jpg',
            [
                'https://image.tmdb.org/t/p/w500/aLVkiINlIeCkcZIzb7XHzPVNC9b.jpg',
                'https://image.tmdb.org/t/p/w500/aLVkiINlIeCkcZIzb7XHzPYgO6L.jpg',
                'https://www.impawards.com/2024/posters/moana_two.jpg',
            ],
        ),
        15: (
            'https://image.tmdb.org/t/p/w500/tIeluhaXHU5oZivBA5pNx1oW1WS.jpg',
            [
                'https://image.tmdb.org/t/p/w500/nvvIkqTtiHeJPZB1VkNUjlWx9R.jpg',
                'https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkbljG6D8.jpg',
            ],
        ),
        11: (
            'https://lumiere-a.akamaihd.net/v1/images/47_coral3_payoff_1sht_uk_ea714d86.jpeg?region=0%2C0%2C743%2C1100',
            ['https://image.tmdb.org/t/p/w500/6lVq2wV2c0m5Q5c4n8x5h0Q5x2V.jpg'],
        ),
        12: (
            'https://lumiere-a.akamaihd.net/v1/images/g_movies_toystory5_homeentannounce_poster_d124485b.jpeg?region=0%2C0%2C1300%2C730',
            ['https://image.tmdb.org/t/p/w500/yFjH5W1p0Z8h3L1s4g9J8V7b5dE.jpg'],
        ),
    }
    for movie_id, (new_poster, old_posters) in poster_repairs.items():
        placeholders = ','.join('?' for _ in old_posters)
        conn.execute(
            f'UPDATE movies SET poster=? WHERE id=? AND poster IN ({placeholders})',
            [new_poster, movie_id, *old_posters],
        )

    # Keep existing showtimes; add demo schedules only when the table is empty.
    if conn.execute('SELECT COUNT(*) FROM showtimes').fetchone()[0] == 0:
        for s in SHOWTIMES:
            conn.execute('INSERT INTO showtimes(id,movie_id,province,cinema,date,time,room,format,price,single_price,double_price,vip_price) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(s['id'],s['movie_id'],s['province'],s['cinema'],s['date'],s['time'],s['room'],s['format'],s['price'],s['price'],150000,120000))
    conn.execute("UPDATE showtimes SET province='Hà Nội' WHERE province IS NULL OR province=''")
    conn.execute("UPDATE showtimes SET single_price=CASE WHEN single_price=0 THEN price ELSE single_price END, double_price=CASE WHEN double_price=0 THEN 150000 ELSE double_price END, vip_price=CASE WHEN vip_price=0 THEN 120000 ELSE vip_price END")
    if conn.execute('SELECT COUNT(*) FROM combos').fetchone()[0]==0:
        for c in COMBOS: conn.execute('INSERT INTO combos(id,name,description,price,active) VALUES(?,?,?,?,1)',(c['id'],c['name'],c['description'],c['price']))

    if conn.execute('SELECT COUNT(*) FROM vouchers').fetchone()[0]==0:
        for code,v in VOUCHERS.items(): conn.execute('INSERT INTO vouchers VALUES(?,?,?,?,1)',(code,v['type'],v['value'],v['label']))
    # Seed rooms from the demo schedule only once, then let Admin manage them.
    if conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0] == 0:
        room_keys = conn.execute('SELECT DISTINCT province,cinema,room FROM showtimes ORDER BY province,cinema,room').fetchall()
        for province, cinema, name in room_keys:
            cur = conn.execute('INSERT INTO rooms(province,cinema,name) VALUES(?,?,?)',(province,cinema,name))
            room_id = cur.lastrowid
            for row in 'ABCDEF':
                seat_type = 'single' if row in 'ABC' else ('double' if row in 'DE' else 'vip')
                for num in range(1,9):
                    conn.execute('INSERT INTO room_seats(room_id,code,seat_type) VALUES(?,?,?)',(room_id,f'{row}{num}',seat_type))

    from werkzeug.security import generate_password_hash
    email='admin@demo.local'
    if not conn.execute('SELECT 1 FROM users WHERE email=?',(email,)).fetchone():
        conn.execute('INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)',('Quản trị viên',email,generate_password_hash('Admin@123'),'admin'))
    else: conn.execute("UPDATE users SET role='admin' WHERE email=?",(email,))
    conn.execute('UPDATE tickets SET original_total=total WHERE original_total=0')
    # Give existing and new tickets a stable human-readable code and ticket name.
    conn.execute("UPDATE tickets SET ticket_code='DVXP-' || printf('%06d', id) WHERE ticket_code IS NULL OR ticket_code=''")
    conn.execute("UPDATE tickets SET ticket_name='Vé xem phim - ' || COALESCE((SELECT title FROM movies WHERE movies.id=tickets.movie_id), 'Phim') WHERE ticket_name IS NULL OR ticket_name=''")
    conn.commit(); conn.close()
