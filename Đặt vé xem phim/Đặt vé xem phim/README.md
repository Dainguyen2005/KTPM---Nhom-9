# Đặt vé xem phim

Website demo phục vụ học tập và kiểm thử phần mềm bằng Flask + SQLite.

## Chức năng chính
- 10 phim **Đang chiếu**, 3 phim **Sắp chiếu**, 2 phim **Suất chiếu đặc biệt**.
- Mỗi phim có poster, giới thiệu và nút xem trailer.
- Luồng đặt vé: **Tỉnh/thành → Rạp → Phim → Ngày → Suất chiếu → Loại ghế → Ghế → Thanh toán**.
- 3 loại ghế: **Ghế đơn, Ghế đôi, Ghế VIP** với mức giá demo khác nhau.
- Đăng ký, đăng nhập, quên mật khẩu, Google Demo.
- Vé của tôi, voucher, QR Demo, thẻ Demo, ví điện tử Demo.
- API cho Postman.
- Chatbot trợ lý tra cứu phim, nội dung/trailer, lịch chiếu, rạp, giá ghế, voucher, combo, hướng dẫn đặt vé và vé của tài khoản đang đăng nhập.
- Admin quản lý phim, suất chiếu, voucher, vé và người dùng.

## Chạy project
```powershell
cd "Đặt vé xem phim"
pip install -r requirements.txt
python app.py
```

Lần sau chỉ cần mở đúng thư mục project và chạy:
```powershell
python app.py
```

## Chatbot
- Chatbot dùng dữ liệu hiện có trong SQLite để trả lời các câu hỏi thường gặp, không cần API key.
- Mục “Vé của tôi” chỉ tra cứu vé thuộc tài khoản đang đăng nhập.
- Đây là chatbot theo ý định/câu hỏi thường gặp, chưa phải mô hình AI tạo sinh tự do; nếu không hiểu câu hỏi, chatbot sẽ gợi ý chủ đề hỗ trợ.

## Tài khoản Admin demo
- Email: `admin@demo.local`
- Mật khẩu: `Admin@123`

## Lưu ý
Poster và trailer là dữ liệu demo/đường dẫn công khai; website không phải trang chính thức của bất kỳ hệ thống rạp nào. Thanh toán và Google login trong project là Demo, không giao dịch tiền thật.

- Trailer YouTube được nhúng trực tiếp trên trang chi tiết từng phim.
- Combo bắp nước: 6 lựa chọn mẫu, tính vào tổng tiền vé.


## Đồng bộ dữ liệu Admin → User
- Phim/voucher/combo được lưu trong SQLite và không còn bị dữ liệu demo ghi đè khi khởi động lại.
- Admin có thể quản lý phòng, giá ghế đơn/đôi/VIP và khóa/mở từng ghế.
- Admin có thể chỉnh giá ghế riêng cho từng suất chiếu.
- Admin có thể cập nhật trạng thái vé; vé hủy sẽ giải phóng ghế cho người dùng.
