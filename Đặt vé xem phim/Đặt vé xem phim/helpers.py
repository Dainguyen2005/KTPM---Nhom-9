from config import MOVIES, SHOWTIMES, SEATS
from database import get_db

def all_movies(status=None):
    conn=get_db(); q='SELECT * FROM movies'; args=[]
    if status: q+=' WHERE status=?'; args.append(status)
    q+=' ORDER BY id DESC'; rows=conn.execute(q,args).fetchall(); conn.close(); return [dict(r) for r in rows] or ([m for m in MOVIES if not status or m['status']==status])

def all_showtimes(movie_id=None,date=None,cinema=None,province=None):
    conn=get_db(); q='SELECT s.*,m.title movie_title,m.poster,m.status FROM showtimes s JOIN movies m ON m.id=s.movie_id WHERE 1=1'; args=[]
    if movie_id: q+=' AND s.movie_id=?'; args.append(movie_id)
    if date: q+=' AND s.date=?'; args.append(date)
    if cinema: q+=' AND s.cinema=?'; args.append(cinema)
    if province: q+=' AND s.province=?'; args.append(province)
    q+=' ORDER BY s.date,s.time'; rows=conn.execute(q,args).fetchall(); conn.close(); return [dict(r) for r in rows]

def find_movie(i):
    conn=get_db(); r=conn.execute('SELECT * FROM movies WHERE id=?',(i,)).fetchone(); conn.close(); return dict(r) if r else next((m for m in MOVIES if m['id']==i),None)

def find_showtime(i):
    conn=get_db(); r=conn.execute('SELECT * FROM showtimes WHERE id=?',(i,)).fetchone(); conn.close(); return dict(r) if r else next((s for s in SHOWTIMES if s['id']==i),None)

def booked_seats(showtime_id):
    conn=get_db(); rows=conn.execute("SELECT seats FROM tickets WHERE showtime_id=? AND status!='Đã hủy'",(showtime_id,)).fetchall(); conn.close(); out=[]
    for r in rows: out += [x for x in r['seats'].split(',') if x]
    return out

def get_ticket(ticket_id,user_id=None):
    conn=get_db(); r=conn.execute('SELECT * FROM tickets WHERE id=?'+(' AND user_id=?' if user_id is not None else ''),(ticket_id,user_id) if user_id is not None else (ticket_id,)).fetchone(); conn.close(); return r

def active_vouchers():
    conn=get_db(); rows=conn.execute('SELECT * FROM vouchers WHERE active=1 ORDER BY code').fetchall(); conn.close(); return [dict(r) for r in rows]

def voucher_discount(code,amount):
    conn=get_db(); v=conn.execute('SELECT * FROM vouchers WHERE code=? AND active=1',(code.upper().strip(),)).fetchone(); conn.close()
    if not v:return None
    d=int(amount*v['value']/100) if v['type']=='percent' else v['value']; return min(d,amount)


def active_combos():
    conn=get_db(); rows=conn.execute('SELECT * FROM combos WHERE active=1 ORDER BY id').fetchall(); conn.close(); return [dict(r) for r in rows]

def get_combos_by_ids(ids):
    ids=[int(x) for x in ids if str(x).isdigit()]
    if not ids: return []
    conn=get_db(); marks=','.join('?'*len(ids)); rows=conn.execute(f'SELECT * FROM combos WHERE active=1 AND id IN ({marks})',ids).fetchall(); conn.close(); return [dict(r) for r in rows]


def find_room(province, cinema, name):
    conn=get_db(); r=conn.execute('SELECT * FROM rooms WHERE province=? AND cinema=? AND name=? AND active=1',(province,cinema,name)).fetchone(); conn.close(); return dict(r) if r else None

def room_seat_data(room_id):
    conn=get_db(); rows=conn.execute('SELECT * FROM room_seats WHERE room_id=? AND active=1 ORDER BY code',(room_id,)).fetchall(); room=conn.execute('SELECT * FROM rooms WHERE id=?',(room_id,)).fetchone(); conn.close()
    return (dict(room) if room else None, [dict(r) for r in rows])

def seat_prices(room):
    if not room: return {'single':90000,'double':150000,'vip':120000}
    return {'single':int(room['single_price']),'double':int(room['double_price']),'vip':int(room['vip_price'])}
