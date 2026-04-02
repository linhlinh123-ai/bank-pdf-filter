import streamlit as st
import pdfplumber
import pandas as pd
import io

st.set_page_config(page_title="Bộ lọc Sao kê GHTK", layout="wide")

st.title("📂 Công cụ lọc giao dịch GHTK")
st.write("Chọn các file PDF sao kê, nhập từ khóa và tải về file Excel kết quả.")

# 1. Nhập từ khóa
keywords_input = st.text_input("Từ khóa lọc (phân tách bằng dấu phẩy):", "GHTK, GIAO HANG TIET KIEM")
keywords = [k.strip().upper() for k in keywords_input.split(",")]

# 2. Chọn file (Cho phép chọn nhiều file cùng lúc)
uploaded_files = st.file_uploader("Chọn các file PDF sao kê", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Bắt đầu lọc dữ liệu"):
        all_data = []
        progress_bar = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            st.write(f"--- Đang quét: {file.name} ---")
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        for row in table:
                            row_text = " ".join([str(cell).upper() for cell in row if cell])
                            if any(kw in row_text for kw in keywords):
                                # Thêm cột tên file để biết dòng này từ đâu ra
                                all_data.append([file.name] + row)
            
            progress_bar.progress((i + 1) / len(uploaded_files))

        if all_data:
            df = pd.DataFrame(all_data)
            
            # Tạo file Excel trong bộ nhớ để cho user tải về
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, header=False)
            
            st.success(f"Tìm thấy {len(all_data)} giao dịch!")
            st.download_button(
                label="📥 Tải file Excel kết quả",
                data=output.getvalue(),
                file_name="ket_qua_loc_sao_ke.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Không tìm thấy giao dịch nào phù hợp.")
