import streamlit as st
import google.generativeai as genai
from docxtpl import DocxTemplate
import pandas as pd
import json
import io

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
st.set_page_config(page_title="Hệ thống AI Đất đai", page_icon="⚖️", layout="wide")
st.title("⚖️ Phần Mềm Xử Lý Hồ Sơ Thừa Kế AI")

# Lưu trữ dữ liệu xuyên suốt các bước
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'nguoi_nhan_chinh' not in st.session_state:
    st.session_state.nguoi_nhan_chinh = None

# ==========================================
# GIAO DIỆN 4 BƯỚC (TABS)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Bước 1: Nạp Dữ Liệu", 
    "🧠 Bước 2: AI Phân Tích", 
    "✍️ Bước 3: Quyết Định", 
    "🖨️ Bước 4: Xuất Hồ Sơ"
])

# --- BƯỚC 1: NẠP DỮ LIỆU ---
with tab1:
    st.header("Tải lên giấy tờ gốc")
    api_key = st.text_input("Nhập Google Gemini API Key của bạn (Bảo mật):", type="password")
    uploaded_files = st.file_uploader("Tải lên Sổ đỏ, CCCD, Khai tử, Hộ khẩu...", type=['pdf', 'jpg', 'png'], accept_multiple_files=True)
    
    if st.button("Xác nhận & Chuyển dữ liệu cho AI"):
        if api_key and uploaded_files:
            genai.configure(api_key=api_key)
            st.success("Đã tiếp nhận hồ sơ. Chuyển sang Bước 2 để phân tích!")
        else:
            st.error("Vui lòng nhập API Key và tải lên ít nhất 1 file.")

# --- BƯỚC 2: AI PHÂN TÍCH QUAN HỆ PHÁP LÝ ---
with tab2:
    st.header("AI Đọc và Trích xuất")
    if st.button("Bắt đầu Phân tích AI"):
        with st.spinner("Đang đọc tài liệu và lập sơ đồ phả hệ..."):
            # LƯU Ý: Trong thực tế, bạn gọi model.generate_content() ở đây.
            # Để demo phần mềm chạy mượt, tôi giả lập kết quả AI trả về chuẩn xác từ hồ sơ bạn vừa cung cấp.
            
            mock_json = """
            {
                "ngay_thang_nam": "12 tháng 05 năm 2026",
                "ho_ten_nguoi_mat": "NGUYỄN VĂN THANH",
                "nam_sinh_nguoi_mat": "1961",
                "ngay_mat": "03/02/2022",
                "dia_chi_nguoi_mat": "Khu 6, phường Vân Phú, tỉnh Phú Thọ",
                "tai_san": {
                    "so_gcn": "BM 637293", "ngay_cap": "25/01/2013",
                    "so_thua": "221", "to_ban_do": "17",
                    "dien_tich_tong": "720.2",
                    "dia_chi": "Khu 6, phường Vân Phú, tỉnh Phú Thọ"
                },
                "hang_thua_ke": [
                    {"vai_tro": "Vợ", "ho_ten": "Nguyễn Thị Toán", "cccd": "025165001898", "tinh_trang": "Còn sống"},
                    {"vai_tro": "Con", "ho_ten": "Nguyễn Văn Thi", "cccd": "025088002483", "tinh_trang": "Còn sống"},
                    {"vai_tro": "Con", "ho_ten": "Nguyễn Thị Hiện", "cccd": "025191001714", "tinh_trang": "Còn sống"},
                    {"vai_tro": "Con", "ho_ten": "Nguyễn Thị Dung", "cccd": "025193014135", "tinh_trang": "Còn sống"}
                ]
            }
            """
            st.session_state.extracted_data = json.loads(mock_json)
            st.success("AI đã phân tích xong! Hãy xem kết quả bên dưới.")
            
    if st.session_state.extracted_data:
        st.subheader("Bản tóm tắt Tài sản & Người để lại di sản")
        st.json({
            "Người để lại di sản": st.session_state.extracted_data['ho_ten_nguoi_mat'],
            "Tài sản (Số Sổ/Thửa/Tờ)": f"{st.session_state.extracted_data['tai_san']['so_gcn']} / {st.session_state.extracted_data['tai_san']['so_thua']} / {st.session_state.extracted_data['tai_san']['to_ban_do']}"
        })
        
        st.subheader("Hàng thừa kế thứ nhất (Do AI phân tích)")
        df = pd.DataFrame(st.session_state.extracted_data['hang_thua_ke'])
        st.dataframe(df, use_container_width=True)

# --- BƯỚC 3: CON NGƯỜI QUYẾT ĐỊNH ---
with tab3:
    st.header("Thiết lập Thỏa thuận")
    if st.session_state.extracted_data:
        st.info("Dựa trên pháp luật, tất cả những người trong Hàng thừa kế thứ nhất đều được hưởng kỷ phần bằng nhau. Tuy nhiên, họ có thể TẶNG CHO lại cho 1 người.")
        
        danh_sach_song = [nguoi['ho_ten'] for nguoi in st.session_state.extracted_data['hang_thua_ke'] if nguoi['tinh_trang'] == "Còn sống"]
        
        nguoi_nhan = st.selectbox("Ai sẽ là người nhận toàn bộ di sản (Những người khác tặng cho lại)?", danh_sach_song)
        
        if st.button("Chốt phương án"):
            st.session_state.nguoi_nhan_chinh = nguoi_nhan
            st.success(f"Đã chốt: Các thành viên sẽ khai nhận và tặng cho toàn bộ phần của mình cho {nguoi_nhan}. Chuyển sang Bước 4!")
    else:
        st.warning("Vui lòng thực hiện Bước 2 trước.")

# --- BƯỚC 4: XUẤT HỒ SƠ ---
with tab4:
    st.header("Tự động điền & Xuất File Word")
    if st.session_state.extracted_data and st.session_state.nguoi_nhan_chinh:
        if st.button("Sinh Bộ Hồ Sơ Pháp Lý"):
            try:
                # 1. Gọi Template
                doc = DocxTemplate("mau_thua_ke.docx")
                
                # 2. Xây dựng Context để nhét vào Word
                data = st.session_state.extracted_data
                context = {
                    "ho_ten_nguoi_mat": data['ho_ten_nguoi_mat'],
                    "ngay_mat": data['ngay_mat'],
                    "so_gcn": data['tai_san']['so_gcn'],
                    "so_thua": data['tai_san']['so_thua'],
                    "dien_tich_tong": data['tai_san']['dien_tich_tong'],
                    "nguoi_nhan_cuoi_cung": st.session_state.nguoi_nhan_chinh
                }
                
                # 3. Render file
                doc.render(context)
                
                # 4. Xuất file cho người dùng tải về
                bio = io.BytesIO()
                doc.save(bio)
                
                st.success("🎉 Hồ sơ đã sẵn sàng!")
                st.download_button(
                    label="⬇️ Tải Bộ Hồ Sơ Hoàn Chỉnh (.docx)",
                    data=bio.getvalue(),
                    file_name=f"HoSo_ThuaKe_{data['ho_ten_nguoi_mat']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"Lỗi khi tạo file (Hãy chắc chắn bạn có file mau_thua_ke.docx cùng thư mục): {e}")
    else:
        st.warning("Vui lòng hoàn thành các bước trước.")