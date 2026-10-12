from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from database import get_db

admin_bp=Blueprint('admin',__name__,url_prefix='/admin')

@admin_bp.before_request
def protect():
    if session.get('role')!='admin': return redirect(url_for('auth.login',next=request.path))

def nav_template(name, **ctx):
    return render_template(name, **ctx)

@admin_bp.route('/')
def dashboard():
    c=get_db(); stats={
        'users':c.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'movies':c.execute('SELECT COUNT(*) FROM movies').fetchone()[0],
        'showtimes':c.execute('SELECT COUNT(*) FROM showtimes').fetchone()[0],
        'rooms':c.execute('SELECT COUNT(*) FROM rooms WHERE active=1').fetchone()[0],
        'tickets':c.execute('SELECT COUNT(*) FROM tickets').fetchone()[0],
        'revenue':c.execute("SELECT COALESCE(SUM(total),0) FROM tickets WHERE payment_status='Đã thanh toán'").fetchone()[0]
    }; recent=c.execute('SELECT t.*,m.title movie_title FROM tickets t LEFT JOIN movies m ON m.id=t.movie_id ORDER BY t.id DESC LIMIT 10').fetchall(); c.close(); return render_template('admin/dashboard.html',stats=stats,recent=recent)

@admin_bp.route('/movies',methods=['GET','POST'])
def movies():
    c=get_db()
    if request.method=='POST':
        mid=request.form.get('id',type=int); data=(request.form['title'],request.form['genre'],request.form.get('duration',type=int) or 0,request.form.get('poster',''),request.form.get('description',''),request.form.get('status','Đang chiếu'),request.form.get('trailer',''))
        if mid:c.execute('UPDATE movies SET title=?,genre=?,duration=?,poster=?,description=?,status=?,trailer=? WHERE id=?',(*data,mid))
        else:c.execute('INSERT INTO movies(title,genre,duration,poster,description,status,trailer) VALUES(?,?,?,?,?,?,?)',data)
        c.commit(); c.close(); return redirect(url_for('admin.movies'))
    rows=c.execute('SELECT * FROM movies ORDER BY id').fetchall(); c.close(); return render_template('admin/movies.html',movies=rows)

@admin_bp.route('/movies/delete/<int:i>',methods=['POST'])
def delete_movie(i):
    c=get_db(); c.execute('DELETE FROM movies WHERE id=?',(i,)); c.commit(); c.close(); return redirect(url_for('admin.movies'))

@admin_bp.route('/showtimes',methods=['GET','POST'])
def showtimes():
    c=get_db()
    if request.method=='POST':
        sid=request.form.get('id',type=int); data=(request.form.get('movie_id',type=int),request.form.get('province','Hà Nội'),request.form['cinema'],request.form['date'],request.form['time'],request.form.get('room','Phòng 1'),request.form.get('format','2D'),request.form.get('price',type=int) or 90000,request.form.get('single_price',type=int) or request.form.get('price',type=int) or 90000,request.form.get('double_price',type=int) or 150000,request.form.get('vip_price',type=int) or 120000)
        if sid:c.execute('UPDATE showtimes SET movie_id=?,province=?,cinema=?,date=?,time=?,room=?,format=?,price=?,single_price=?,double_price=?,vip_price=? WHERE id=?',(*data,sid))
        else:sid=c.execute('SELECT COALESCE(MAX(id),0)+1 FROM showtimes').fetchone()[0]; c.execute('INSERT INTO showtimes(id,movie_id,province,cinema,date,time,room,format,price,single_price,double_price,vip_price) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(sid,*data))
        c.commit(); c.close(); return redirect(url_for('admin.showtimes'))
    rows=c.execute('SELECT s.*,m.title movie_title FROM showtimes s JOIN movies m ON m.id=s.movie_id ORDER BY s.date,s.time').fetchall(); movies=c.execute('SELECT * FROM movies ORDER BY title').fetchall(); rooms=c.execute('SELECT * FROM rooms WHERE active=1 ORDER BY province,cinema,name').fetchall(); edit_id=request.args.get('edit',type=int); edit_showtime=c.execute('SELECT * FROM showtimes WHERE id=?',(edit_id,)).fetchone() if edit_id else None; c.close(); return render_template('admin/showtimes.html',showtimes=rows,movies=movies,rooms=rooms,edit_showtime=edit_showtime)

@admin_bp.route('/showtimes/delete/<int:i>',methods=['POST'])
def delete_showtime(i):
    c=get_db(); c.execute('DELETE FROM showtimes WHERE id=?',(i,)); c.commit(); c.close(); return redirect(url_for('admin.showtimes'))

@admin_bp.route('/vouchers',methods=['GET','POST'])
def vouchers():
    c=get_db()
    if request.method=='POST':
        code=request.form['code'].strip().upper(); c.execute('INSERT OR REPLACE INTO vouchers VALUES(?,?,?,?,1)',(code,request.form['type'],request.form.get('value',type=int) or 0,request.form['label'].strip())); c.commit(); c.close(); return redirect(url_for('admin.vouchers'))
    rows=c.execute('SELECT * FROM vouchers ORDER BY code').fetchall(); c.close(); return render_template('admin/vouchers.html',vouchers=rows)

@admin_bp.route('/vouchers/toggle/<code>',methods=['POST'])
def toggle(code):
    c=get_db(); c.execute('UPDATE vouchers SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE code=?',(code,)); c.commit(); c.close(); return redirect(url_for('admin.vouchers'))


@admin_bp.route('/combos',methods=['GET','POST'])
def combos():
    c=get_db()
    if request.method=='POST':
        cid=request.form.get('id',type=int); data=(request.form['name'].strip(),request.form.get('description','').strip(),request.form.get('price',type=int) or 0)
        if cid:c.execute('UPDATE combos SET name=?,description=?,price=? WHERE id=?',(*data,cid))
        else:c.execute('INSERT INTO combos(name,description,price,active) VALUES(?,?,?,1)',data)
        c.commit(); c.close(); return redirect(url_for('admin.combos'))
    rows=c.execute('SELECT * FROM combos ORDER BY id').fetchall(); c.close(); return render_template('admin/combos.html',combos=rows)

@admin_bp.route('/combos/toggle/<int:i>',methods=['POST'])
def toggle_combo(i):
    c=get_db(); c.execute('UPDATE combos SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id=?',(i,)); c.commit(); c.close(); return redirect(url_for('admin.combos'))

@admin_bp.route('/vouchers/delete/<code>',methods=['POST'])
def delete_voucher(code):
    c=get_db(); c.execute('DELETE FROM vouchers WHERE code=?',(code,)); c.commit(); c.close(); return redirect(url_for('admin.vouchers'))

@admin_bp.route('/combos/delete/<int:i>',methods=['POST'])
def delete_combo(i):
    c=get_db(); c.execute('DELETE FROM combos WHERE id=?',(i,)); c.commit(); c.close(); return redirect(url_for('admin.combos'))

@admin_bp.route('/rooms',methods=['GET','POST'])
def rooms():
    c=get_db()
    if request.method=='POST':
        rid=request.form.get('id',type=int); province=request.form.get('province','Hà Nội').strip(); cinema=request.form['cinema'].strip(); name=request.form['name'].strip(); prices=(request.form.get('single_price',type=int) or 90000,request.form.get('double_price',type=int) or 150000,request.form.get('vip_price',type=int) or 120000)
        if rid:
            old = c.execute('SELECT province,cinema,name FROM rooms WHERE id=?',(rid,)).fetchone()
            if old:
                # Keep existing showtimes synchronized when a room is renamed/moved/retpriced.
                c.execute('UPDATE showtimes SET province=?,cinema=?,room=?,single_price=?,double_price=?,vip_price=?,price=? WHERE province=? AND cinema=? AND room=?',
                          (province,cinema,name,*prices,prices[0],old['province'],old['cinema'],old['name']))
            c.execute('UPDATE rooms SET province=?,cinema=?,name=?,single_price=?,double_price=?,vip_price=? WHERE id=?',(province,cinema,name,*prices,rid))
        else:
            cur=c.execute('INSERT INTO rooms(province,cinema,name,single_price,double_price,vip_price) VALUES(?,?,?,?,?,?)',(province,cinema,name,*prices)); rid=cur.lastrowid
            for row in 'ABCDEF':
                st='single' if row in 'ABC' else ('double' if row in 'DE' else 'vip')
                for num in range(1,9): c.execute('INSERT OR IGNORE INTO room_seats(room_id,code,seat_type) VALUES(?,?,?)',(rid,f'{row}{num}',st))
        c.commit(); c.close(); return redirect(url_for('admin.rooms'))
    rows=c.execute('SELECT * FROM rooms ORDER BY province,cinema,name').fetchall(); c.close(); return render_template('admin/rooms.html',rooms=rows)

@admin_bp.route('/rooms/delete/<int:i>',methods=['POST'])
def delete_room(i):
    c=get_db(); used=c.execute('SELECT COUNT(*) FROM showtimes WHERE province=(SELECT province FROM rooms WHERE id=?) AND cinema=(SELECT cinema FROM rooms WHERE id=?) AND room=(SELECT name FROM rooms WHERE id=?)',(i,i,i)).fetchone()[0]
    if used: flash('Không thể xóa phòng đang được dùng trong suất chiếu. Hãy xóa/sửa suất chiếu trước.','error')
    else:
        c.execute('DELETE FROM room_seats WHERE room_id=?',(i,)); c.execute('DELETE FROM rooms WHERE id=?',(i,)); c.commit()
    c.close(); return redirect(url_for('admin.rooms'))

@admin_bp.route('/rooms/<int:room_id>/seats',methods=['GET','POST'])
def seats(room_id):
    c=get_db(); room=c.execute('SELECT * FROM rooms WHERE id=?',(room_id,)).fetchone()
    if not room: c.close(); return 'Không tìm thấy phòng',404
    if request.method=='POST':
        for seat in c.execute('SELECT code FROM room_seats WHERE room_id=?',(room_id,)).fetchall():
            code=seat['code']; active=1 if request.form.get('seat_'+code)=='on' else 0; c.execute('UPDATE room_seats SET active=? WHERE room_id=? AND code=?',(active,room_id,code))
        c.commit(); c.close(); return redirect(url_for('admin.seats',room_id=room_id))
    rows=c.execute('SELECT * FROM room_seats WHERE room_id=? ORDER BY code',(room_id,)).fetchall(); c.close(); return render_template('admin/seats.html',room=room,seats=rows)

@admin_bp.route('/tickets')
def tickets():
    c=get_db(); rows=c.execute('SELECT t.*,m.title movie_title,s.cinema,s.date,s.time,s.room FROM tickets t LEFT JOIN movies m ON m.id=t.movie_id LEFT JOIN showtimes s ON s.id=t.showtime_id ORDER BY t.id DESC').fetchall(); c.close(); return render_template('admin/tickets.html',tickets=rows)

@admin_bp.route('/tickets/<int:i>/status',methods=['POST'])
def ticket_status(i):
    status=request.form.get('status','Đã đặt'); c=get_db(); c.execute('UPDATE tickets SET status=? WHERE id=?',(status,i)); c.commit(); c.close(); return redirect(url_for('admin.tickets'))

@admin_bp.route('/users')
def users():
    c=get_db(); rows=c.execute('SELECT id,name,email,role,points FROM users ORDER BY id DESC').fetchall(); c.close(); return render_template('admin/users.html',users=rows)

@admin_bp.route('/users/<int:i>/role',methods=['POST'])
def role(i):
    c=get_db(); c.execute('UPDATE users SET role=? WHERE id=?',(request.form.get('role','user'),i)); c.commit(); c.close(); return redirect(url_for('admin.users'))
