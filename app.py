import streamlit as st
import google.generativeai as genai
from docxtpl import DocxTemplate
import pandas as pd
import json
import io
from datetime import datetime

st.set_page_config(page_title="Phần Mềm Pháp Lý Đất Đai", layout="wide")
st.title("⚖️ Hệ Thống Xử Lý Hồ Sơ Thừa Kế AI")

if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'nguoi_nhan_chinh' not in st.session_state:
    st.session_state.nguoi_nhan_chinh = None

tab1, tab2, tab3 = st.tabs(["📂 1. Nạp Hồ Sơ", "🧠 2. AI Phân Tích", "🖨️ 3. Xuất Hồ Sơ"])

# --- BƯỚC 1 ---
with tab1:
    api_key = st.text_input("Nhập Google Gemini API Key:", type="password")
    uploaded_files = st.file_uploader("Tải lên Sổ đỏ, CCCD, Khai tử...", type=['pdf', 'jpg', 'png'], accept_multiple_files=True)

    if st.button("Xác nhận & Xử lý"):
        if api_key and uploaded_files:
            st.success("Đã tiếp nhận! Hãy chuyển sang Bước 2.")
            # Dữ liệu giả lập cực kỳ chi tiết khớp 100% với file Master Template
            mock_json = """
            {
                "ho_ten_nguoi_mat": "NGUYỄN VĂN THANH",
                "sinh_nguoi_mat": "05/09/1961",
                "ngay_mat": "03/02/2022",
                "dia_chi_nguoi_mat": "Khu 6, phường Vân Phú, tỉnh Phú Thọ",
                "ho_ten_bo": "Nguyễn Văn Phán",
                "ngay_mat_bo": "08/06/1993",
                "ho_ten_me": "Đinh Thị Tịch",
                "ngay_mat_me": "17/08/2014",
                "tai_san": {
                    "so_gcn": "BM 637293",
                    "so_vao_so_gcn": "1151",
                    "co_quan_cap_gcn": "UBND thành phố Việt Trì",
                    "ngay_cap_gcn": "25/01/2013",
                    "so_thua": "221",
                    "to_ban_do": "17",
                    "dia_chi_thua_dat": "Khu 6, phường Vân Phú, tỉnh Phú Thọ",
                    "dien_tich_tong": "720.2",
                    "dien_tich_ont": "300.0",
                    "dien_tich_cln": "420.2"
                },
                "hang_thua_ke": [
                    {"vai_tro": "Vợ", "ho_ten": "Nguyễn Thị Toán", "cccd": "025165001898", "nam_sinh": "1965", "tinh_trang": "Còn sống", "noi_cap": "Cục CS QLHC về TTXH", "ngay_cap": "17/03/2025", "dia_chi": "Khu 7, phường Vân Phú, tỉnh Phú Thọ"},
                    {"vai_tro": "Con đẻ", "ho_ten": "Nguyễn Văn Thi", "cccd": "025088002483", "nam_sinh": "1988", "tinh_trang": "Còn sống", "noi_cap": "Cục CS QLHC về TTXH", "ngay_cap": "13/04/2021", "dia_chi": "Khu 6, phường Vân Phú, tỉnh Phú Thọ"},
                    {"vai_tro": "Con đẻ", "ho_ten": "Nguyễn Thị Hiện", "cccd": "025191001714", "nam_sinh": "1991", "tinh_trang": "Còn sống", "noi_cap": "Cục CS QLHC về TTXH", "ngay_cap": "03/04/2021", "dia_chi": "Khu 6, phường Vân Phú, tỉnh Phú Thọ"},
                    {"vai_tro": "Con đẻ", "ho_ten": "Nguyễn Thị Dung", "cccd": "025193014135", "nam_sinh": "1993", "tinh_trang": "Còn sống", "noi_cap": "Cục CS QLHC về TTXH", "ngay_cap": "20/09/2024", "dia_chi": "Khu 13, xã Bản Nguyên, tỉnh Phú Thọ"}
                ]
            }
            """
            st.session_state.extracted_data = json.loads(mock_json)
        else:
            st.error("Vui lòng nhập API Key và tải file.")

# --- BƯỚC 2 ---
with tab2:
    if st.session_state.extracted_data:
        data = st.session_state.extracted_data
        st.subheader(f"Di sản của: {data['ho_ten_nguoi_mat']} | Sổ đỏ: {data['tai_san']['so_gcn']}")

        df = pd.DataFrame(data['hang_thua_ke'])
        st.dataframe(df, use_container_width=True)

        danh_sach_song = [nguoi['ho_ten'] for nguoi in data['hang_thua_ke'] if nguoi['tinh_trang'] == "Còn sống"]
        nguoi_nhan_chinh = st.selectbox("Chọn người duy nhất NHẬN di sản (những người khác sẽ Tặng cho):", danh_sach_song)

        if st.button("Lưu phương án thỏa thuận"):
            st.session_state.nguoi_nhan_chinh = nguoi_nhan_chinh
            st.success(f"Đã chốt: Toàn bộ di sản thuộc về {nguoi_nhan_chinh}. Chuyển sang Bước 3!")

# --- BƯỚC 3 ---
with tab3:
    if st.session_state.extracted_data:
        # Kiểm tra xem người dùng đã bấm lưu phương án ở Bước 2 chưa
        if not st.session_state.nguoi_nhan_chinh:
            st.warning("⚠️ Vui lòng quay lại Bước 2 và bấm nút 'Lưu phương án thỏa thuận' trước khi xuất hồ sơ.")
        else:
            if st.button("Sinh Bộ Hồ Sơ Pháp Lý (Word)"):
                data = st.session_state.extracted_data

                # Phân loại người nhận và danh sách tặng cho
                nguoi_nhan_di_san = {}
                danh_sach_tang_cho = []

                for tv in data['hang_thua_ke']:
                    if tv['ho_ten'] == st.session_state.nguoi_nhan_chinh:
                        nguoi_nhan_di_san = tv
                    else:
                        danh_sach_tang_cho.append(tv)

                # Lấy ngày tháng năm hiện tại
                now = datetime.now()

                # Đóng gói TOÀN BỘ dữ liệu để bơm vào Word
                context = {
                    "ngay": now.strftime("%d"),
                    "thang": now.strftime("%m"),
                    "nam": now.strftime("%Y"),

                    "ho_ten_nguoi_mat": data['ho_ten_nguoi_mat'],
                    "sinh_nguoi_mat": data['sinh_nguoi_mat'],
                    "ngay_mat": data['ngay_mat'],
                    "dia_chi_nguoi_mat": data['dia_chi_nguoi_mat'],

                    "ho_ten_bo": data['ho_ten_bo'],
                    "ngay_mat_bo": data['ngay_mat_bo'],
                    "ho_ten_me": data['ho_ten_me'],
                    "ngay_mat_me": data['ngay_mat_me'],

                    "so_gcn": data['tai_san']['so_gcn'],
                    "so_vao_so_gcn": data['tai_san']['so_vao_so_gcn'],
                    "co_quan_cap_gcn": data['tai_san']['co_quan_cap_gcn'],
                    "ngay_cap_gcn": data['tai_san']['ngay_cap_gcn'],
                    "so_thua": data['tai_san']['so_thua'],
                    "to_ban_do": data['tai_san']['to_ban_do'],
                    "dia_chi_thua_dat": data['tai_san']['dia_chi_thua_dat'],
                    "dien_tich_tong": data['tai_san']['dien_tich_tong'],
                    "dien_tich_ont": data['tai_san']['dien_tich_ont'],
                    "dien_tich_cln": data['tai_san']['dien_tich_cln'],

                    "nguoi_nhan": nguoi_nhan_di_san,
                    "danh_sach_tang_cho": danh_sach_tang_cho
                }

                # Kỹ thuật băm nhỏ CCCD thành từng ký tự để rớt đúng vào 12 ô vuông Thuế
                cccd_str = nguoi_nhan_di_san.get('cccd', '000000000000')
                cccd_digits = list(cccd_str.ljust(12, '0')) # Chống lỗi thiếu số
                for i in range(12):
                    context[f"c{i}"] = cccd_digits[i]

                try:
                    doc = DocxTemplate("mau_thua_ke.docx")
                    doc.render(context)

                    bio = io.BytesIO()
                    doc.save(bio)

                    st.success("🎉 Tạo bộ hồ sơ thành công! File đã sẵn sàng.")
                    st.download_button(
                        label="⬇️ Tải Bộ Hồ Sơ Hoàn Chỉnh",
                        data=bio.getvalue(),
                        file_name=f"HoSo_ThuaKe_{data['ho_ten_nguoi_mat']}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Lỗi khi đọc file Word. Hãy chắc chắn tên file trên GitHub chính xác là 'mau_thua_ke.docx'. Chi tiết: {e}")
