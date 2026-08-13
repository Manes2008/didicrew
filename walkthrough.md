# Walkthrough: Chi Tiết Các Thay Đổi Và Sửa Đổi Logic Kịch Bản

Tài liệu này tóm tắt toàn bộ các file đã được chỉnh sửa trong dự án `videocrew` để giải quyết vấn đề kịch bản 60s bị ngắn và tự động đồng bộ hóa Hook & CTA.

---

## 1. Các File Đã Sửa Đổi (Files Modified)

* **File cấu hình:** [tasks.yaml](file:///d:/Dev/Projects/DEV_PYTHONs/videocrew/videocrew/config/tasks.yaml)
* **File mã nguồn chính:** [engine.py](file:///d:/Dev/Projects/DEV_PYTHONs/videocrew/videocrew/src/core/engine.py)

---

## 2. Chi Tiết Các Thay Đổi Trong Từng File

### A. Trong [tasks.yaml](file:///d:/Dev/Projects/DEV_PYTHONs/videocrew/videocrew/config/tasks.yaml)
* **Độ dài và mật độ từ:** Bổ sung quy tắc mật độ từ đọc thực tế (~2.5 từ/giây). Video 60s bắt buộc phải đạt xấp xỉ 150 từ voiceover và phân bổ đều cho 15 - 20 cảnh (mỗi cảnh 2-4s tương ứng 5-10 từ) để tránh việc AI viết kịch bản quá ngắn.
- **Tách thoại và dẫn chuyện:** Phân chia rõ ràng văn bản đọc thành `[NARRATOR]` (Lời dẫn chuyện kết nối cốt truyện) và `[DIALOGUE - Tên nhân vật]` (Lời thoại nhân vật để trong ngoặc kép).
- **Đồng bộ hóa Hook & CTA:** Thiết lập quy tắc bắt buộc để nội dung Hook ở phần 1 đồng bộ với Scene 1, và nội dung CTA ở phần 4 đồng bộ với Scene cuối.
- **Tích hợp Veo3:** Đồng bộ hóa yếu tố Hook/CTA trực quan vào `Combined Prompt (EN)` của Cảnh 1 và Cảnh cuối để Veo3 sinh video chuẩn xác.

### B. Trong [engine.py](file:///d:/Dev/Projects/DEV_PYTHONs/videocrew/videocrew/src/core/engine.py)
* **Tự động đồng bộ hóa Sequence khóa chính DB (`_auto_reset_db_sequences`):**
  Tích hợp logic tự động đồng bộ hóa (reset) tất cả các sequence khóa chính của tất cả các bảng trong DB về giá trị cực đại (`MAX(id)`) khi khởi tạo `WorkflowEngine`. Điều này giúp khắc phục hoàn toàn lỗi `UniqueViolation` dưới nền hoàn toàn tự động, giải phóng người dùng khỏi việc chạy code SQL thủ công hoặc script cài đặt môi trường ảo DB.
* **Bộ parse thời lượng đa định dạng (`parse_markdown_table_durations`):** 
  Hàm đã được nâng cấp để hỗ trợ parse thời lượng của từng cảnh từ bảng phân cảnh Markdown chuẩn (`|`) lẫn bảng phân tách bằng ký tự TAB (`\t`) do LLM tự sinh.
* **Validator kiểm tra cứng (`validate_script_content`):**
  Tự động đếm số cảnh và cộng dồn thời lượng thực tế của các cảnh. Nếu tổng thời lượng lệch quá 5 giây so với mục tiêu (ví dụ: < 55s đối với video 60s), validator sẽ báo lỗi không hợp lệ.
* **Vòng lặp tự sửa lỗi nghiêm ngặt (Self-Correction Loop):**
  Đưa kết quả của validator vào điều kiện lặp. Khi kịch bản không đạt chuẩn (ví dụ chỉ có 10 cảnh, 36s như bạn đã gặp), hệ thống sẽ gửi phản hồi lỗi chi tiết và bắt buộc LLM phải tự viết lại (chia nhỏ cảnh hoặc thêm tình huống trung gian) cho đến khi đạt tối thiểu 15 cảnh và đủ thời lượng 60s.
* **Sửa thứ tự logic lưu DB:** Đảm bảo khối ghi log DB chạy trước khi hàm `return final_script` để tránh bỏ sót log.

---

## 3. Hướng Dẫn Khởi Động Lại Máy Chủ (Restart Server)

Do Python lưu cache các module đã import, các thay đổi trong file `engine.py` sẽ không có hiệu lực cho đến khi tiến trình Streamlit được khởi động lại.

1. Hãy truy cập vào Terminal/Console đang chạy ứng dụng Streamlit của bạn.
2. Nhấn tổ hợp phím `Ctrl + C` để tắt tiến trình đang chạy.
3. Chạy lại file `run.bat` hoặc lệnh khởi động Streamlit:
   ```bash
   venv\Scripts\streamlit run src/ui/app.py
   ```
