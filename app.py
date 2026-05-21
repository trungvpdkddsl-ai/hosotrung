import streamlit as st
import pandas as pd
import json
import io
from docxtpl import DocxTemplate
from datetime import datetime

st.set_page_config(page_title="Pháp Lý Đất Đai - Bảo Châu", layout="wide")
st.title("⚖️ Hệ Thống Xử Lý Hồ Sơ Thừa Kế AI")

if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'nguoi_nhan_chinh' not in st.session_state:
    st.session_state.nguoi_nhan_chinh = None

tab1, tab2, tab3 = st.tabs(["📂 1. Nạp Hồ Sơ", "🧠 2. AI Phân Tích & Logic", "🖨️ 3. Xuất Hồ Sơ"])

# --- BƯỚC 1: NẠP DỮ LIỆU ---
with tab1:
    api_key = st.text_input("Nhập Google Gemini API Key:", type="password")
    uploaded_files = st.file_uploader("Tải lên Sổ đỏ, CCCD, Khai tử...", type=['pdf', 'jpg', 'png'], accept_multiple_files=True)
    
    col1, col2 = st.columns(2)
    noi_ky = col1.text_input("Nơi ký văn bản:", value="Trung tâm Phục vụ hành chính công phường Vân Phú, tỉnh Phú Thọ")
    loai_so = col2.radio("Loại Sổ đỏ (Để tính tỷ lệ di sản):", ["Cấp cho Hộ gia đình", "Tài sản chung vợ chồng (Cấp cá nhân)"])

    if st.button("Xác nhận & Xử lý"):
        if api_key and uploaded_files:
            # Giả lập dữ liệu có thêm Giới tính, Ngày sinh đầy đủ và Trích lục khai tử
            mock_json = """
            {
                "ho_ten_nguoi_mat": "nguyễn văn thanh",
                "sinh_nguoi_mat": "05/09/1961",
                "ngay_mat": "03/02/2022",
                "dia_chi_nguoi_mat": "Khu 6, phường Vân Phú, tỉnh Phú Thọ",
                
                "ho_ten_bo": "nguyễn văn phán",
                "ngay_mat_bo": "08/06/1993",
                "giay_to_chet_bo": "gia đình không nhớ năm sinh",
                "ho_ten_me": "đinh thị tịch",
                "ngay_mat_me": "17/08/2014",
                "giay_to_chet_me": "theo bản sao trích lục tử số 341/TLKT-BS do UBND phường Vân Phú cấp ngày 12/05/2026",
                
                "tai_san": {
                    "so_gcn": "BM 637293", "so_vao_so_gcn": "1151", "co_quan_cap_gcn": "UBND thành phố Việt Trì",
                    "ngay_cap_gcn": "25/01/2013", "so_thua": "221", "to_ban_do": "17",
                    "dia_chi_thua_dat": "Khu 6, phường Vân Phú, tỉnh Phú Thọ",
                    "dien_tich_tong": "720,2", "dien_tich_ont": "300", "dien_tich_cln": "420,2"
                },
                "hang_thua_ke": [
                    {"vai_tro": "vợ", "ho_ten": "nguyễn thị toán", "gioi_tinh": "nữ", "ngay_sinh": "14/03/1965", "cccd": "025165001898", "noi_cap": "Bộ Công an", "ngay_cap": "17/03/2025", "dia_chi": "Khu 7, phường Vân Phú, tỉnh Phú Thọ"},
                    {"vai_tro": "con đẻ", "ho_ten": "nguyễn văn thi", "gioi_tinh": "nam", "ngay_sinh": "11/05/1988", "cccd": "025088002483", "noi_cap": "Cục cảnh sát", "ngay_cap": "13/04/2021", "dia_chi": "Khu 6, phường Vân Phú, tỉnh Phú Thọ"},
                    {"vai_tro": "con đẻ", "ho_ten": "nguyễn thị hiên", "gioi_tinh": "nữ", "ngay_sinh": "19/07/1991", "cccd": "025191001714", "noi_cap": "Cục cảnh sát", "ngay_cap": "03/04/2021", "dia_chi": "Khu 6, phường Vân Phú, tỉnh Phú Thọ"},
                    {"vai_tro": "con đẻ", "ho_ten": "nguyễn thị dung", "gioi_tinh": "nữ", "ngay_sinh": "26/04/1993", "cccd": "025193014135", "noi_cap": "Bộ Công an", "ngay_cap": "20/09/2024", "dia_chi": "Khu 13, xã Bản Nguyên, tỉnh Phú Thọ"}
                ]
            }
            """
            
            # Tiền xử lý dữ liệu (Viết hoa chữ cái đầu và gán danh xưng)
            raw_data = json.loads(mock_json)
            raw_data['ho_ten_nguoi_mat'] = raw_data['ho_ten_nguoi_mat'].title()
            raw_data['ho_ten_bo'] = raw_data['ho_ten_bo'].title()
            raw_data['ho_ten_me'] = raw_data['ho_ten_me'].title()
            
            for tv in raw_data['hang_thua_ke']:
                tv['ho_ten'] = tv['ho_ten'].title()
                tv['danh_xung'] = "Ông" if tv['gioi_tinh'].lower() == "nam" else "Bà"
                
            st.session_state.extracted_data = raw_data
            st.session_state.noi_ky = noi_ky
            st.session_state.loai_so = loai_so
            st.success("Đã xử lý chuẩn hóa Tên, Giới tính, Ngày sinh. Chuyển sang Bước 2!")

# --- BƯỚC 2: AI PHÂN TÍCH ---
with tab2:
    if st.session_state.extracted_data:
        data = st.session_state.extracted_data
        
        # Tính tỷ lệ di sản
        tong_so_nguoi_ho = len(data['hang_thua_ke']) + 1 # +1 là tính cả người chết
        ty_le_di_san = f"1/{tong_so_nguoi_ho}" if st.session_state.loai_so == "Cấp cho Hộ gia đình" else "1/2"
        st.session_state.ty_le_di_san = ty_le_di_san
        st.session_state.tong_so_nguoi_ho = tong_so_nguoi_ho
        
        st.info(f"Phân tích Logic Pháp lý: Sổ {st.session_state.loai_so} ➡️ Di sản của người mất bằng {ty_le_di_san} quyền sử dụng đất.")

        danh_sach_song = [nguoi['ho_ten'] for nguoi in data['hang_thua_ke']]
        nguoi_nhan_chinh = st.selectbox("Chọn người duy nhất NHẬN di sản (những người khác sẽ Tặng cho):", danh_sach_song)

        if st.button("Lưu phương án thỏa thuận"):
            st.session_state.nguoi_nhan_chinh = nguoi_nhan_chinh
            st.success("Đã lưu. Chuyển sang Bước 3!")

# --- BƯỚC 3: XUẤT HỒ SƠ ---
with tab3:
    if st.session_state.extracted_data and st.session_state.nguoi_nhan_chinh:
        if st.button("Sinh Bộ Hồ Sơ Pháp Lý (Word)"):
            data = st.session_state.extracted_data
            now = datetime.now()

            # Tách riêng người nhận và nhóm tặng cho (để dùng cho phần III Thỏa thuận)
            nguoi_nhan_di_san = {}
            danh_sach_tang_cho = []
            danh_sach_ten_tang_cho = [] # Phục vụ in câu: "do các ông bà A, B, C không có nhu cầu..."

            for tv in data['hang_thua_ke']:
                if tv['ho_ten'] == st.session_state.nguoi_nhan_chinh:
                    nguoi_nhan_di_san = tv
                else:
                    danh_sach_tang_cho.append(tv)
                    danh_sach_ten_tang_cho.append(f"{tv['danh_xung']} {tv['ho_ten']}")

            context = {
                "ngay": now.strftime("%d"), "thang": now.strftime("%m"), "nam": now.strftime("%Y"),
                "noi_ky": st.session_state.noi_ky,
                "ho_ten_nguoi_mat": data['ho_ten_nguoi_mat'],
                "sinh_nguoi_mat": data['sinh_nguoi_mat'],
                "ngay_mat": data['ngay_mat'],
                "dia_chi_nguoi_mat": data['dia_chi_nguoi_mat'],
                "ho_ten_bo": data['ho_ten_bo'], "ngay_mat_bo": data['ngay_mat_bo'], "giay_to_chet_bo": data['giay_to_chet_bo'],
                "ho_ten_me": data['ho_ten_me'], "ngay_mat_me": data['ngay_mat_me'], "giay_to_chet_me": data['giay_to_chet_me'],
                
                # Biến tỷ lệ và danh sách
                "ty_le_di_san": st.session_state.ty_le_di_san,
                "tong_so_nguoi_ho": st.session_state.tong_so_nguoi_ho,
                "danh_sach_thua_ke": data['hang_thua_ke'], # Dùng để in Mục I và II (Đánh số 1,2,3...)
                "chuoi_ten_tang_cho": ", ".join(danh_sach_ten_tang_cho), # In ra: "Ông A, Bà B, Ông C"
                "nguoi_nhan": nguoi_nhan_di_san,
                
                # Tài sản
                "so_gcn": data['tai_san']['so_gcn'], "so_vao_so_gcn": data['tai_san']['so_vao_so_gcn'],
                "co_quan_cap_gcn": data['tai_san']['co_quan_cap_gcn'], "ngay_cap_gcn": data['tai_san']['ngay_cap_gcn'],
                "so_thua": data['tai_san']['so_thua'], "to_ban_do": data['tai_san']['to_ban_do'],
                "dia_chi_thua_dat": data['tai_san']['dia_chi_thua_dat'],
                "dien_tich_tong": data['tai_san']['dien_tich_tong'],
                "dien_tich_ont": data['tai_san']['dien_tich_ont'], "dien_tich_cln": data['tai_san']['dien_tich_cln'],
            }

            try:
                doc = DocxTemplate("mau_thua_ke.docx")
                doc.render(context)
                bio = io.BytesIO()
                doc.save(bio)
                st.download_button(label="⬇️ Tải Bộ Hồ Sơ Hoàn Chỉnh", data=bio.getvalue(), file_name=f"HoSo_ThuaKe_{data['ho_ten_nguoi_mat']}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e:
                st.error(f"Lỗi: {e}")
