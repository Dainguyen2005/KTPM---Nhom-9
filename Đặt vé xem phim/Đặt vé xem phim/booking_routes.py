from flask import Blueprint,render_template,request,redirect,url_for,session
import re
from config import SEATS,PRICE,SEAT_TYPES
from database import get_db
from helpers import booked_seats,find_movie,find_showtime,all_movies,all_showtimes,active_combos,get_combos_by_ids,active_vouchers,find_room,room_seat_data,seat_prices
booking_bp=Blueprint('booking',__name__)

@booking_bp.route('/booking')
def booking_select():
    if 'user_id' not in session:return redirect(url_for('auth.login',next=url_for('booking.booking_select')))
    province=request.args.get('province',''); cinema=request.args.get('cinema',''); movie_id=request.args.get('movie_id',type=int); date=request.args.get('date','')
    conn=get_db(); provinces=[r[0] for r in conn.execute("SELECT DISTINCT province FROM showtimes ORDER BY province")]; cinemas=[r[0] for r in conn.execute("SELECT DISTINCT cinema FROM showtimes WHERE (? = '' OR province=?) ORDER BY cinema",(province,province)).fetchall()]; dates=[r[0] for r in conn.execute("SELECT DISTINCT date FROM showtimes WHERE (? = '' OR province=?) AND (? = '' OR cinema=?) ORDER BY date",(province,province,cinema,cinema)).fetchall()]; conn.close()
    shows=all_showtimes(movie_id,date or None,cinema or None,province or None)
    return render_template('booking_select.html',provinces=provinces,cinemas=cinemas,dates=dates,movies=all_movies(),shows=shows,province=province,cinema=cinema,movie_id=movie_id,date=date)

@booking_bp.route('/booking/<int:showtime_id>',methods=['GET','POST'])
def booking(showtime_id):
    if 'user_id' not in session:return redirect(url_for('auth.login',next=url_for('booking.booking',showtime_id=showtime_id)))
    show=find_showtime(showtime_id)
    if not show:return 'Không tìm thấy suất chiếu',404
    movie=find_movie(show['movie_id']); booked=booked_seats(showtime_id); error=None
    room=find_room(show['province'],show['cinema'],show['room'])
    room, room_seats = room_seat_data(room['id']) if room else (None, [])
    available_codes=[x['code'] for x in room_seats]
    room_prices=seat_prices(room)
    prices={'single':int(show.get('single_price') or room_prices['single']), 'double':int(show.get('double_price') or room_prices['double']), 'vip':int(show.get('vip_price') or room_prices['vip'])}
    seat_types={k:{'label':SEAT_TYPES[k]['label'],'price':prices[k]} for k in SEAT_TYPES}
    seat_type_map={x['code']:x['seat_type'] for x in room_seats}
    if request.method=='POST':
        name=request.form.get('customer_name','').strip(); phone=request.form.get('phone','').strip(); seats=request.form.get('seats','').strip()
        combo_ids=request.form.getlist('combo_ids')
        if not name or not phone or not seats:error='Vui lòng nhập họ tên, số điện thoại và chọn ghế.'
        elif not re.fullmatch(r'0[35789]\d{8}', phone):error='Số điện thoại không hợp lệ. Vui lòng nhập số di động Việt Nam gồm 10 chữ số, ví dụ 0912345678.'
        else:
            selected=[s.strip() for s in seats.split(',') if s.strip()]
            if any(s not in available_codes for s in selected):error='Ghế không hợp lệ hoặc ghế đã bị khóa bởi Admin.'
            elif len(selected)!=len(set(selected)):error='Không được chọn trùng ghế.'
            elif any(s in booked for s in selected):error='Có ghế bạn chọn đã được đặt.'
            else:
                type_map={x['code']:x['seat_type'] for x in room_seats}
                seat_total=sum(prices[type_map[s]] for s in selected)
                combos=get_combos_by_ids(combo_ids)
                combo_total=sum(int(c['price']) for c in combos)
                combo_items=', '.join(f"{c['name']} ({c['price']:,}đ)" for c in combos)
                total=seat_total+combo_total
                conn=get_db(); cur=conn.execute('INSERT INTO tickets(user_id,customer_name,phone,movie_id,showtime_id,seats,total,original_total,combo_items,combo_total,ticket_name) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(session['user_id'],name,phone,movie['id'],showtime_id,','.join(selected),total,total,combo_items,combo_total,'Vé xem phim - '+movie['title'])); tid=cur.lastrowid; ticket_code=f'DVXP-{tid:06d}'; conn.execute('UPDATE tickets SET ticket_code=? WHERE id=?',(ticket_code,tid)); conn.commit(); conn.close(); return redirect(url_for('payment.payment',ticket_id=tid))
    return render_template('booking.html',movie=movie,show=show,seats=available_codes,booked=booked,error=error,price=show.get('price') or PRICE,seat_types=seat_types,combos=active_combos(),vouchers=active_vouchers(),room=room,seat_type_map=seat_type_map,form_name=request.form.get('customer_name',''),form_phone=request.form.get('phone',''))

@booking_bp.route('/tickets')
def tickets():
    if 'user_id' not in session:return redirect(url_for('auth.login'))
    conn=get_db(); rows=conn.execute('SELECT t.*, m.title AS movie_title FROM tickets t LEFT JOIN movies m ON m.id=t.movie_id WHERE t.user_id=? ORDER BY t.id DESC',(session['user_id'],)).fetchall(); u=conn.execute('SELECT points FROM users WHERE id=?',(session['user_id'],)).fetchone(); conn.close(); return render_template('tickets.html',tickets=rows,points=u['points'] if u else 0)
