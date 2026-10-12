from flask import Blueprint,render_template,request,redirect,url_for,session
from database import get_db
from helpers import get_ticket,voucher_discount,find_movie,find_showtime,active_vouchers
payment_bp=Blueprint('payment',__name__)
@payment_bp.route('/payment/<int:ticket_id>',methods=['GET','POST'])
def payment(ticket_id):
    if 'user_id' not in session:return redirect(url_for('auth.login'))
    ticket=get_ticket(ticket_id,session['user_id'])
    if not ticket:return 'Không tìm thấy vé',404
    if ticket['payment_status']=='Đã thanh toán':return redirect(url_for('payment.ticket_detail',ticket_id=ticket_id))
    error=success=None
    if request.method=='POST':
        action=request.form.get('action','pay')
        if action=='apply_voucher':
            code=request.form.get('voucher_code','').strip().upper(); original=ticket['original_total'] or ticket['total']; discount=voucher_discount(code,original)
            if discount is None:error='Mã voucher không hợp lệ hoặc đang tắt.'
            else:
                conn=get_db(); conn.execute('UPDATE tickets SET total=?,discount=?,voucher_code=? WHERE id=? AND user_id=?',(original-discount,discount,code,ticket_id,session['user_id'])); conn.commit(); conn.close(); ticket=get_ticket(ticket_id,session['user_id']); success=f'Áp dụng {code} thành công: giảm {discount:,}đ.'
        else:
            method=request.form.get('payment_method','').strip()
            if method not in ['QR Demo','Thẻ ngân hàng Demo','Ví điện tử Demo']:error='Vui lòng chọn phương thức thanh toán.'
            elif method=='Thẻ ngân hàng Demo':
                n=request.form.get('card_number','').replace(' ',''); name=request.form.get('card_name','').strip(); exp=request.form.get('card_expiry','').strip(); cvv=request.form.get('card_cvv','').strip()
                if not n or not name or not exp or not cvv:error='Vui lòng nhập đầy đủ thông tin thẻ Demo.'
                elif not n.isdigit() or len(n)!=16:error='Số thẻ Demo phải gồm 16 chữ số.'
                elif len(cvv) not in (3,4) or not cvv.isdigit():error='Mã CVV Demo phải gồm 3 hoặc 4 chữ số.'
                elif len(exp)!=5 or exp[2]!='/' or not exp[:2].isdigit() or not exp[3:].isdigit():error='Ngày hết hạn phải dạng MM/YY.'
            elif method=='Ví điện tử Demo':
                phone=request.form.get('wallet_phone','').strip(); code=request.form.get('wallet_code','').strip()
                if not phone or not code:error='Vui lòng nhập đầy đủ thông tin ví Demo.'
                elif not phone.isdigit() or len(phone)!=10:error='Số điện thoại ví Demo phải gồm 10 chữ số.'
                elif not code.isdigit() or len(code)!=6:error='Mã xác nhận Demo phải gồm 6 chữ số.'
            if not error:
                conn=get_db(); conn.execute("UPDATE tickets SET payment_method=?,payment_status='Đã thanh toán' WHERE id=? AND user_id=?",(method,ticket_id,session['user_id'])); conn.execute('UPDATE users SET points=points+? WHERE id=?',(max(1,ticket['total']//1000),session['user_id'])); conn.commit(); conn.close(); return redirect(url_for('payment.ticket_detail',ticket_id=ticket_id,paid=1))
    return render_template('payment.html',ticket=ticket,error=error,success=success,vouchers={v['code']:v for v in active_vouchers()})
@payment_bp.route('/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    if 'user_id' not in session:return redirect(url_for('auth.login'))
    ticket=get_ticket(ticket_id,session['user_id'])
    if not ticket:return 'Không tìm thấy vé',404
    return render_template('ticket_detail.html',ticket=ticket,movie=find_movie(ticket['movie_id']),show=find_showtime(ticket['showtime_id']))
