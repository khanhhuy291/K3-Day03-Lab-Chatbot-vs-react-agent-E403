# Định Hướng Bài Toán: Trợ Lý Tìm & Đặt Lịch Xem Nhà Trọ / Căn Hộ Cho Thuê

## 1. Thông tin chung
- **Đề tài:** 10. Trợ Lý Tìm & Đặt Lịch Xem Nhà Trọ / Căn Hộ Cho Thuê
- **Người phụ trách (Role 1):** Product Architect

## 2. Mục tiêu dự án
Xây dựng một **ReAct AI Agent** thông minh có khả năng hỗ trợ người dùng (sinh viên, người đi làm) trong quá trình tìm kiếm chỗ ở và tự động hóa việc đặt lịch hẹn xem phòng. 

## 3. Đánh giá độ phù hợp (Agentic Fit)
Tại sao bài toán này cần dùng **ReAct Agent** thay vì chỉ dùng Chatbot thuần?
- **Hạn chế của Chatbot thuần:** Chỉ có thể cung cấp các lời khuyên chung chung về kinh nghiệm thuê nhà (ví dụ: cách tránh lừa đảo, mẫu hợp đồng), nhưng không thể biết hiện tại đang có những phòng nào trống, giá cả bao nhiêu ở một khu vực cụ thể.
- **Sức mạnh của Agent:** Agent có khả năng gọi các **công cụ (Tools)** để truy xuất cơ sở dữ liệu phòng trọ theo thời gian thực (giá cả, tiện ích, vị trí) và có thể thực hiện hành động (Action) như ghi nhận lịch hẹn vào hệ thống.

## 4. Các Công Cụ (Tools) Đề Xuất Cho Role 2
Để Agent có thể hoạt động hiệu quả, Role 2 (Tool Engineer) cần phát triển tối thiểu 2 tools sau trong `src/tools.py`:

1. **`search_apartments(location: str, max_price: float, min_acreage: float)`**
   - *Mô tả:* Tra cứu danh sách các phòng trọ/căn hộ hiện đang trống dựa trên khu vực (Thành phố/Quận), mức giá tối đa và diện tích tối thiểu.
   - *Đầu ra kỳ vọng:* Chuỗi JSON/Text chứa thông tin các căn hộ phù hợp (Tiêu đề, Địa chỉ, Giá, Diện tích).

2. **`book_viewing(title: str, date: str, user_name: str)`**
   - *Mô tả:* Thực hiện đặt lịch hẹn xem phòng cho khách hàng dựa trên tiêu đề bài đăng (hoặc địa chỉ).
   - *Đầu ra kỳ vọng:* Xác nhận đặt lịch thành công hoặc báo lỗi (nếu thông tin phòng không tồn tại hoặc ngày giờ không hợp lệ).

## 5. Chiến lược Kiểm thử (Test Cases)
Bộ Test Cases đã được Role 1 xây dựng tại `config/test_cases.json` bao gồm 5 kịch bản để kiểm tra mức độ đáp ứng của Agent:
- **Level 1 (Đơn giản):** Hỏi đáp về kinh nghiệm ký hợp đồng, ưu nhược điểm các loại hình thuê nhà (Chatbot tự xử lý).
- **Level 2 (Multi-step - 1 Tool):** Tìm kiếm phòng trọ tại Cầu Giấy dưới 4 triệu (Agent dùng `search_apartments`).
- **Level 3 (Multi-step - 2 Tools):** Tìm căn hộ ở Quận 1 và đặt lịch xem ngay lập tức (Agent dùng `search_apartments` sau đó gọi tiếp `book_viewing`).
- **Level 4 (Edge Case):** Cố tình đưa thông tin sai (Vương quốc Wakanda, giá âm, ngày 30/02) để kiểm thử Guardrail có ngắt Agent thành công hay không.
