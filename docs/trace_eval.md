# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

---

# 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Cần hiểu yêu cầu (khu vực, ngân sách, số phòng), lọc danh sách phù hợp, so sánh và đề xuất lựa chọn tốt nhất. |
| 🛠️ **Tool Interaction** | `5/5` | Phải gọi nhiều công cụ như API tìm nhà, Google Maps, lịch hẹn và hệ thống liên hệ chủ nhà. |
| 🔀 **Dynamic Decision** | `5/5` | Nếu không còn phòng hoặc lịch xem kín thì phải tìm phương án thay thế hoặc đề xuất thời gian khác. |
| ⏳ **Long Horizon** | `4/5` | Quy trình gồm nhiều bước: tìm kiếm → lọc → so sánh → đặt lịch → xác nhận với người dùng. |
| **TỔNG ĐIỂM FIT** | **19/20** | **KẾT LUẬN: RẤT PHÙ HỢP ĐỂ XÂY DỰNG BẰNG REACT AGENT!** |

---

# 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE #3)

**Câu hỏi**: *"Tìm cho tôi căn hộ 1 phòng ngủ ở Quận Bình Thạnh dưới 8 triệu và đặt lịch xem vào chiều thứ Bảy."*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *"Bạn có thể tìm trên các website như Chợ Tốt hoặc Batdongsan.com để xem các căn hộ phù hợp."*
* **Nhận xét**: Chỉ đưa ra lời khuyên chung, không tìm kiếm dữ liệu thực tế và cũng không hỗ trợ đặt lịch xem nhà.

### 🧠 ReAct Agent:

* **Thought 1**: Xác định tiêu chí tìm kiếm: Bình Thạnh, 1 phòng ngủ, giá dưới 8 triệu.

* **Action 1**: `search_rental(location="Bình Thạnh", bedrooms=1, max_price=8000000)`

* **Observation 1**:
```
Tìm thấy 5 căn phù hợp.
- Căn A: 7.5 triệu, cách ĐH HUTECH 800m.
- Căn B: 7.8 triệu, gần Landmark 81.
- Căn C: 6.9 triệu, còn trống từ tuần sau.
```

* **Thought 2**: Chọn các căn còn trống và kiểm tra lịch hẹn của chủ nhà.

* **Action 2**: `check_viewing_schedule(property="Căn A", date="Thứ Bảy chiều")`

* **Observation 2**:
```
Khung giờ còn trống:
- 14:00
- 16:30
```

* **Thought 3**: Đặt lịch xem vào khung giờ sớm nhất.

* **Action 3**:
`book_viewing(property="Căn A", time="14:00")`

* **Observation 3**:
```
Đặt lịch thành công.
Mã xác nhận: VIEW-48231
```

### ✅ Final Answer

*"Mình đã tìm được 5 căn hộ phù hợp với yêu cầu của bạn. Lựa chọn tốt nhất hiện tại là Căn A (1 phòng ngủ, giá 7.5 triệu/tháng, cách HUTECH khoảng 800m). Mình đã đặt lịch xem nhà vào **14:00 chiều thứ Bảy**. Mã xác nhận lịch hẹn là **VIEW-48231**."*

### 📝 Nhận xét

ReAct Agent không chỉ tìm kiếm dữ liệu theo yêu cầu mà còn:
- Hiểu và phân tích tiêu chí của người dùng.
- Gọi nhiều công cụ khác nhau (tìm kiếm, kiểm tra lịch, đặt lịch).
- Tự động xử lý các bước trung gian.
- Hoàn thành toàn bộ quy trình mà người dùng không cần thao tác thêm.

---

# 🧪 3. KẾT QUẢ CHẠY THỬ THỰC TẾ TRÊN REPO

**Ngày chạy thử**: `2026-07-28`  
**Lệnh chạy**: `.venv/bin/python src/app.py`  
**LLM Provider thực tế**: `MockProvider (Offline Mock Mode)`

## Baseline Chatbot

**Câu test đã chạy**: *"Tìm giúp tôi một phòng trọ ở Đống Đa, Hà Nội với ngân sách dưới 2.5 triệu đồng."*

**Output thực tế**:

```text
🤖 [Mock Provider]: Phản hồi giả lập offline cho bài test.
```

**Đánh giá observability**:
- Luồng baseline đã chạy thành công, không lỗi runtime sau khi cài dependencies.
- Kết quả hiện tại chưa phản ánh năng lực thật của mô hình vì đang dùng `MockProvider`.
- Baseline chưa đưa ra dữ liệu thuê trọ cụ thể, nên hiện chỉ dùng để kiểm tra wiring và entrypoint.
- Muốn đánh giá chất lượng thật giữa Chatbot và ReAct Agent, cần cấu hình provider/API key thực thay cho chế độ mock.

---

# 🔁 4. MỐC 3 - REACT LOOP & SAFEGUARDS

**Ngày chạy trace**: `2026-07-28`  
**Lệnh chạy**: `.venv/bin/python src/app.py`  
**Mục tiêu Role 5**: Trích xuất chuỗi `Thought -> Action -> Observation` từ vòng lặp ReAct hiện tại.

## Câu hỏi test thực tế

*"Tìm giúp tôi một phòng trọ ở Đống Đa, Hà Nội với ngân sách dưới 2.5 triệu đồng."*

## Trace Log đã trích xuất

### Step 1

- **Thought**: `Câu hỏi này cần tra cứu phòng phù hợp theo khu vực và ngân sách.`
- **Action**: `search_apartments['Cầu Giấy', 4000000]`
- **Observation**:

```json
{
  "location": "Cầu Giấy",
  "max_price_million_vnd": 4.0,
  "required_amenities": [],
  "count": 2,
  "listings": [
    {
      "id": "APT-001",
      "title": "Phòng studio máy lạnh, cửa sổ, gần Trung Kính",
      "price": 3.7,
      "published": "2026-07-24",
      "acreage": 20,
      "address": "Khu Trung Kính, Cầu Giấy, Hà Nội"
    },
    {
      "id": "APT-002",
      "title": "Phòng khép kín máy lạnh, ban công, thang máy",
      "price": 3.9,
      "published": "2026-07-25",
      "acreage": 22,
      "address": "Khu Yên Hòa, Cầu Giấy, Hà Nội"
    }
  ],
  "notice": "Dữ liệu demo; hãy xác minh tình trạng thực tế trước khi đặt cọc."
}
```

### Final Answer

`Tôi tìm thấy 2 căn phù hợp với điều kiện hiện tại.`

## Đánh giá Guardrails & Trace Quality

- Agent đã chạy qua đúng khung `Thought -> Action -> Observation -> Final Answer`.
- Vòng lặp dừng sớm ở bước 1, không vượt `MAX_ITERATIONS`, nên guardrail giới hạn vòng lặp đang hoạt động.
- Không có lỗi runtime khi gọi tool; tool trả về JSON hợp lệ để quan sát.
- Tuy nhiên, trace cho thấy agent **chưa bám đúng input người dùng**: câu hỏi là `Đống Đa` và `dưới 2.5 triệu`, nhưng action thực tế lại gọi `Cầu Giấy` và `4 triệu`.
- Đây là lỗi logic/orchestration ở `src/app.py`, không phải lỗi observability. Role 4 cần sửa phần mapping từ user query sang đối số tool trước khi nghiệm thu Mốc 3.
