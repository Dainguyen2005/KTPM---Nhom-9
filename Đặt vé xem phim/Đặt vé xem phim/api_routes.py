from flask import Blueprint,request,jsonify,session
import re
from config import SEATS,PRICE
from database import get_db
from helpers import booked_seats,all_movies,all_showtimes
api_bp=Blueprint('api',__name__)
@api_bp.route('/api/movies')
def api_movies():return jsonify(all_movies())
@api_bp.route('/api/showtimes')
def api_showtimes():return jsonify(all_showtimes(request.args.get('movie_id',type=int),request.args.get('date'),request.args.get('cinema')))
@api_bp.route('/api/tickets',methods=['GET'])
def api_tickets():
    conn=get_db(); rows=conn.execute('SELECT * FROM tickets ORDER BY id DESC').fetchall(); conn.close(); return jsonify([dict(r) for r in rows])
@api_bp.route('/api/tickets',methods=['POST'])
def api_create_ticket():
    data=request.get_json(silent=True) or {}; required=['customer_name','phone','movie_id','showtime_id','seats']
    if any(f not in data for f in required):return jsonify(success=False,message='Thiếu trường dữ liệu bắt buộc'),400
    if not isinstance(data.get('phone'),str) or not re.fullmatch(r'0[35789]\d{8}', data['phone']):return jsonify(success=False,message='Số điện thoại không hợp lệ. Nhập số di động Việt Nam gồm 10 chữ số.'),400
    seats=data['seats']
    if not isinstance(seats,list) or not seats:return jsonify(success=False,message='seats phải là một danh sách không rỗng'),400
    if any(s not in SEATS for s in seats) or len(seats)!=len(set(seats)):return jsonify(success=False,message='Danh sách ghế không hợp lệ'),400
    show=next((s for s in all_showtimes() if s['id']==data['showtime_id']),None); movie=next((m for m in all_movies() if m['id']==data['movie_id']),None)
    if not movie or not show or show['movie_id']!=data['movie_id']:return jsonify(success=False,message='Phim hoặc suất chiếu không tồn tại'),404
    if any(s in booked_seats(data['showtime_id']) for s in seats):return jsonify(success=False,message='Có ghế đã được đặt'),409
    total=len(seats)*(show.get('price') or PRICE); conn=get_db(); cur=conn.execute('INSERT INTO tickets(user_id,customer_name,phone,movie_id,showtime_id,seats,total,original_total,ticket_name) VALUES(?,?,?,?,?,?,?,?,?)',(session.get('user_id'),data['customer_name'],data['phone'],data['movie_id'],data['showtime_id'],','.join(seats),total,total,'Vé xem phim - '+movie['title'])); tid=cur.lastrowid; ticket_code=f'DVXP-{tid:06d}'; conn.execute('UPDATE tickets SET ticket_code=? WHERE id=?',(ticket_code,tid)); conn.commit(); conn.close(); return jsonify(success=True,ticket_id=tid,ticket_code=ticket_code,ticket_name='Vé xem phim - '+movie['title'],total=total,payment_status='Chưa thanh toán'),201
