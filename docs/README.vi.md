# Hướng Dẫn Sử Dụng Tool Đối Soát Đơn Shopee

## 1. Mục đích của tool

Tool này dùng để xử lý 2 nhu cầu chính:

1. So sánh file Excel đơn hàng Shopee với file PDF phiếu giao hàng để tìm:
   - đơn bị thiếu trên PDF
   - đơn bị thiếu trên Excel
   - đơn có nội dung sản phẩm bị cắt, bị ẩn, hoặc không đọc đủ trên PDF
   - đơn có chênh lệch số lượng giữa Excel và phần nội dung nhìn thấy trên PDF

2. Tách file Excel Shopee thành danh sách dòng hàng hóa theo từng đơn để phục vụ kho, vận hành, hoặc import sang hệ thống khác.

Tool hiện có 2 cách chạy:

- CLI qua `python main.py`
- web app nội bộ qua `streamlit run streamlit_app.py`

## 2. Yêu cầu môi trường

- `pyenv`
- Python `3.11.10`
- Các package trong [requirements.txt](/Users/hunt2412/hieupvdev/project/automation-daily/requirements.txt)

## 3. Cài đặt môi trường

Chạy lần lượt:

```bash
cd /Users/hunt2412/hieupvdev/project/automation-daily
pyenv install 3.11.10
pyenv local 3.11.10
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Nếu đã cài sẵn Python và `.venv` rồi thì chỉ cần:

```bash
cd /Users/hunt2412/hieupvdev/project/automation-daily
source .venv/bin/activate
pip install -r requirements.txt
```

Sau đó có thể chạy web app nội bộ:

```bash
cd /Users/hunt2412/hieupvdev/project/automation-daily
source .venv/bin/activate
streamlit run streamlit_app.py
```

Nếu báo không tìm thấy `streamlit` thì chạy lại phần cài đặt ở trên và kiểm tra `.venv` đã được activate hay chưa.

## 4. Cấu trúc thư mục thường dùng

- [main.py](/Users/hunt2412/hieupvdev/project/automation-daily/main.py): điểm chạy CLI
- [streamlit_app.py](/Users/hunt2412/hieupvdev/project/automation-daily/streamlit_app.py): điểm chạy web app nội bộ
- [shopee/](/Users/hunt2412/hieupvdev/project/automation-daily/shopee): nơi đặt file Excel và PDF đầu vào
- [output/](/Users/hunt2412/hieupvdev/project/automation-daily/output): nơi sinh file kết quả

## 4.1. Web app nội bộ dùng khi nào

Nên dùng web app khi:

- nhân sự vận hành không muốn chạy terminal
- cần upload file trực tiếp rồi tải kết quả về
- cần xem nhanh metric và bảng lỗi trước khi tải file

Web app hiện có 2 màn hình chính:

- `Compare Orders`: upload 1 file Excel + 1 file PDF, chạy đối soát, xem metric, tải `csv/xlsx/pdf`
- `Extract Item Rows`: upload 1 file Excel, xem trước item rows, tải `csv/xlsx`

Ví dụ file đầu vào hiện có trong project:

- `shopee/Order.all.order_creation_date.20260402_20260406.xlsx`
- `shopee/6. SP Mollis (B4098) - 200 đơn - 06.04.2026 - Đợt 6.pdf`

## 5. Lệnh CLI số 1: `compare`

### 5.1. Công dụng

Lệnh này dùng để:

- đọc file Excel đơn hàng Shopee
- đọc file PDF phiếu giao hàng
- so khớp theo `Mã đơn hàng`
- kiểm tra `Mã vận đơn`, thời gian đặt hàng, tổng số lượng
- đối chiếu item trong Excel với phần `Nội dung hàng` nhìn thấy trên PDF
- xuất báo cáo đối soát ra `csv`, `excel`, hoặc `pdf`

### 5.2. Cú pháp đầy đủ

```bash
python main.py compare \
  --excel "<duong_dan_file_excel>" \
  --pdf "<duong_dan_file_pdf>" \
  --formats csv excel pdf \
  --out-dir "<thu_muc_output>"
```

### 5.3. Lệnh mẫu nên dùng

```bash
python main.py compare \
  --excel "shopee/Order.all.order_creation_date.20260402_20260406.xlsx" \
  --pdf "shopee/6. SP Mollis (B4098) - 200 đơn - 06.04.2026 - Đợt 6.pdf" \
  --formats csv excel pdf \
  --out-dir "output/manual-run"
```

### 5.4. Ý nghĩa các tham số

- `--excel`: đường dẫn file Excel export từ Shopee
- `--pdf`: đường dẫn file PDF phiếu giao hàng
- `--formats`: các định dạng muốn xuất, gồm:
  - `csv`
  - `excel`
  - `pdf`
- `--out-dir`: thư mục chứa kết quả

Nếu không truyền `--out-dir`, tool sẽ tự tạo thư mục dạng:

```bash
output/YYYYMMDD-HHMMSS
```

### 5.5. Ví dụ lọc chỉ xuất đơn lỗi

Nếu chỉ muốn xuất các dòng đang có vấn đề:

```bash
python main.py compare \
  --excel "shopee/Order.all.order_creation_date.20260402_20260406.xlsx" \
  --pdf "shopee/6. SP Mollis (B4098) - 200 đơn - 06.04.2026 - Đợt 6.pdf" \
  --formats csv excel \
  --only mismatch missing-in-pdf \
  --out-dir "output/review-only"
```

`--only` hỗ trợ các trạng thái:

- `matched`
- `mismatch`
- `missing-in-excel`
- `missing-in-pdf`

## 6. Kết quả của lệnh `compare`

### 6.1. Các file được sinh ra

Tùy theo `--formats`, tool sẽ sinh:

- `comparison.csv`
- `comparison.xlsx`
- `comparison.pdf`

### 6.2. Ý nghĩa các trạng thái

- `matched`: đơn có trong cả Excel và PDF, các kiểm tra chính đều pass
- `mismatch`: đơn có trong cả 2 nguồn nhưng có ít nhất 1 lỗi cần xem
- `missing-in-excel`: đơn có trong PDF nhưng không có trong Excel
- `missing-in-pdf`: đơn có trong Excel nhưng không có trong PDF

### 6.3. Các cột quan trọng trong file compare

- `order_id`: mã đơn hàng dùng để đối soát
- `status`: trạng thái đối soát
- `notes`: ghi chú tổng hợp lý do lỗi
- `excel_waybill`: mã vận đơn lấy từ Excel
- `pdf_waybill`: mã vận đơn lấy từ PDF
- `excel_total_quantity`: tổng số lượng sản phẩm từ Excel
- `pdf_total_quantity`: tổng số lượng được ghi ở header PDF
- `pdf_visible_quantity`: tổng số lượng parser thực sự nhìn thấy trong phần `Nội dung hàng` của PDF
- `item_match_status`: trạng thái đối chiếu item
- `missing_excel_items`: các item bị thiếu hoặc bị cắt trên PDF, lấy từ Excel
- `unclear_pdf_items`: nội dung item PDF đọc được nhưng không đủ chắc chắn để map
- `pdf_page_number`: số trang PDF chứa đơn đó

### 6.4. Cách hiểu `quantity_match`

`quantity_match` không chỉ so:

- `excel_total_quantity`
với
- `pdf_total_quantity`

Mà đang so cả 3 giá trị:

- `excel_total_quantity`
- `pdf_total_quantity`
- `pdf_visible_quantity`

Vì vậy có thể xảy ra trường hợp:

- `excel_total_quantity = pdf_total_quantity`
- nhưng `quantity_match = no`

Lý do là phần `Nội dung hàng` trên PDF bị cắt, nên parser không nhìn thấy đủ tất cả item hoặc không nhìn thấy đủ `SL:` của từng item.

### 6.5. Cách hiểu cột `missing_excel_items`

Đây là cột rất quan trọng cho kho.

Mỗi item sẽ nằm trên một dòng riêng trong cùng một ô, format:

```text
[SKU4 - Tên phân loại hàng - xSố lượng]
```

Ví dụ:

```text
[BM5A - Xanh Cá Heo - x1]
[FM5A - Vàng Sinh Vật Biển - x1]
```

Ý nghĩa:

- `SKU4`: lấy 4 ký tự đầu của cột `SKU phân loại hàng`
- `Tên phân loại hàng`: lấy từ Excel
- `xSố lượng`: số lượng còn thiếu hoặc chưa xác minh được trên PDF

### 6.6. Khi nào một item bị đưa vào `missing_excel_items`

Tool sẽ đưa item vào `missing_excel_items` khi:

- item đó có trong Excel nhưng không đọc thấy đủ trên PDF
- item trên PDF bị cắt phần nội dung
- item trên PDF không có đủ `SL:` để xác minh
- parser không thể map chắc chắn item PDF với item Excel

### 6.7. Khi nào cần xem thêm `unclear_pdf_items`

`unclear_pdf_items` giữ lại phần text nhìn thấy được trên PDF để người dùng kiểm tra bằng mắt.

Cặp cột nên xem cùng nhau là:

- `missing_excel_items`
- `unclear_pdf_items`

Hiểu đơn giản:

- `missing_excel_items`: dữ liệu chuẩn lấy từ Excel
- `unclear_pdf_items`: phần đang nhìn thấy hoặc đang bị lỗi trên PDF

## 7. Lệnh CLI số 2: `extract-items`

### 7.1. Công dụng

Lệnh này dùng để tách file Excel Shopee ra thành danh sách dòng hàng hóa chi tiết theo từng đơn.

Phù hợp khi cần:

- đưa dữ liệu cho kho
- import sang hệ thống khác
- lọc theo mã đơn hàng, mã vật tư, số lượng
- làm bảng tổng hợp hàng theo ngày

### 7.2. Cú pháp đầy đủ

```bash
python main.py extract-items \
  --excel "<duong_dan_file_excel>" \
  --format excel \
  --out-file "<duong_dan_file_ket_qua>"
```

### 7.3. Lệnh mẫu nên dùng

Xuất ra Excel:

```bash
python main.py extract-items \
  --excel "shopee/Order.all.order_creation_date.20260402_20260406.xlsx" \
  --format excel \
  --out-file "output/order-items.xlsx"
```

Xuất ra CSV:

```bash
python main.py extract-items \
  --excel "shopee/Order.all.order_creation_date.20260402_20260406.xlsx" \
  --format csv \
  --out-file "output/order-items.csv"
```

### 7.4. Ý nghĩa các tham số

- `--excel`: đường dẫn file Excel Shopee
- `--format`: `excel` hoặc `csv`
- `--out-file`: đường dẫn file đầu ra

Nếu không truyền `--out-file`, tool sẽ tự sinh file trong:

```bash
output/<timestamp>/order-items.xlsx
```

hoặc:

```bash
output/<timestamp>/order-items.csv
```

## 8. Kết quả của lệnh `extract-items`

File kết quả sẽ là bảng item-level, thường có các cột kiểu:

- `Mã đơn hàng`
- `Mã vật tư`
- `Số lượng`
- `Total Order`
- `Ngày xử lý đơn hàng`
- `Ngày xử lý đơn hàng detail`
- `Ngày đặt hàng`

### 8.1. Ý nghĩa một số cột

- `Mã đơn hàng`: mã đơn Shopee
- `Mã vật tư`: mã hàng dùng cho kho/hệ thống
- `Số lượng`: số lượng của dòng đó
- `Total Order`: tỷ lệ `Số lượng` của dòng trên tổng số lượng trong đơn
- `Ngày xử lý đơn hàng`: ngày xử lý ở format `dd/mm/yyyy`
- `Ngày xử lý đơn hàng detail`: ngày giờ xử lý ở format `dd/mm/yyyy hh:mm`

### 8.2. Nguồn lấy ngày xử lý

Tool ưu tiên:

1. `Ngày gửi hàng`
2. nếu trống thì lấy `Ngày xuất hàng`
3. nếu vẫn trống thì lấy `Thời gian giao hàng`

## 9. Cách chạy nhanh cho người dùng cuối

### Trường hợp 1: chỉ cần kiểm tra phiếu PDF có bị cắt item không

```bash
python main.py compare \
  --excel "shopee/Order.all.order_creation_date.20260402_20260406.xlsx" \
  --pdf "shopee/6. SP Mollis (B4098) - 200 đơn - 06.04.2026 - Đợt 6.pdf" \
  --formats csv \
  --only mismatch missing-in-pdf \
  --out-dir "output/review"
```

Sau đó mở:

- `output/review/comparison.csv`

và tập trung xem các cột:

- `status`
- `notes`
- `missing_excel_items`
- `unclear_pdf_items`
- `pdf_page_number`

### Trường hợp 2: chỉ cần xuất danh sách hàng từ Excel

```bash
python main.py extract-items \
  --excel "shopee/Order.all.order_creation_date.20260402_20260406.xlsx" \
  --format excel \
  --out-file "output/order-items.xlsx"
```

## 10. Một số lưu ý thực tế

- PDF phải là PDF text-based. Nếu là ảnh scan thì parser sẽ không đọc ổn định.
- Khi Shopee đổi template PDF, một số marker có thể lệch và tool sẽ báo `pdf template requires review`.
- Nếu phiếu PDF quá dài và phần `Nội dung hàng` bị cắt, nên tin dữ liệu Excel hơn dữ liệu nhìn thấy trên PDF.
- `missing_excel_items` là cột dành cho việc kiểm lại hàng thiếu hoặc hàng bị ẩn/cắt trên phiếu.

## 11. Chạy test

```bash
python -m unittest discover -s tests -v
```

## 12. Tài liệu liên quan

- Bản README hiện tại: [README.md](/Users/hunt2412/hieupvdev/project/automation-daily/docs/README.md)
- CLI implementation: [cli.py](/Users/hunt2412/hieupvdev/project/automation-daily/shopee_compare/cli.py)
