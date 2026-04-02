import streamlit as st
import pdfplumber
import pandas as pd
import io

st.set_page_config(page_title="Bộ lọc Sao kê GHTK", layout="wide")

st.title("📂 Công cụ lọc giao dịch GHTK (Bản Chuẩn)")
st.write("Kéo thả PDF, lọc đúng cột Nợ/Có và tự động định dạng Excel.")

# 1. Nhập từ khóa
keywords_input = st.text_input("Từ khóa lọc (phân tách bằng dấu phẩy):", "GHTK, GIAO HANG TIET KIEM")
keywords = [k.strip().upper() for k in keywords_input.split(",")]

# 2. Chọn file
uploaded_files = st.file_uploader("Chọn các file PDF sao kê", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Bắt đầu lọc dữ liệu"):
        all_data = []
        progress_bar = st.progress(0)
        
        # Tiêu đề chuẩn như m yêu cầu
        headers = ["File", "Ngày giao dịch", "Đối tác", "NH Đối tác", "Diễn giải", "Số bút toán", "Nợ (Debit)", "Có (Credit)"]

        for i, file in enumerate(uploaded_files):
            st.write(f"--- Đang quét: {file.name} ---")
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        for row in table:
                            if len(row) >= 6:
                                row_text = " ".join([str(c).upper() for c in row if c])
                                if any(kw in row_text for kw in keywords):
                                    # Lấy đúng 7 cột từ PDF + 1 cột tên file
                                    clean_row = row[:7] + [None] * (7 - len(row[:7]))
                                    all_data.append([file.name] + clean_row)
            
            progress_bar.progress((i + 1) / len(uploaded_files))

        if all_data:
            # Tạo DataFrame
            df = pd.DataFrame(all_data, columns=headers)

            # --- XỬ LÝ SỐ TIỀN ---
            for col in ["Nợ (Debit)", "Có (Credit)"]:
                # Bỏ dấu phẩy, khoảng trắng và ép về số
                df[col] = df[col].astype(str).str.replace(',', '').str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # --- ĐỊNH DẠNG EXCEL TRONG BỘ NHỚ ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Ket_Qua')
                
                workbook  = writer.book
                worksheet = writer.sheets['Ket_Qua']

                # Định dạng: Xuống dòng + Căn lề trên cùng
                wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
                # Định dạng: Số tiền có dấu phân cách + Căn lề trên cùng
                money_format = workbook.add_format({'num_format': '#,##0', 'valign': 'top', 'border': 1})
                # Định dạng tiêu đề
                header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})

                # Ghi lại tiêu đề với định dạng đẹp
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Thiết lập độ rộng cột
                worksheet.set_column('A:A', 15) # File
                worksheet.set_column('B:B', 12) # Ngày
                worksheet.set_column('C:E', 35, wrap_format) # Đối tác, NH, Diễn giải (Xuống dòng)
                worksheet.set_column('F:F', 20) # Số bút toán
                worksheet.set_column('G:H', 18, money_format) # Nợ, Có (Dạng số)

            st.success(f"Tìm thấy {len(all_data)} giao dịch!")
            st.download_button(
                label="📥 Tải file Excel kết quả xịn",
                data=output.getvalue(),
                file_name="sao_ke_loc_chuan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Không tìm thấy giao dịch nào phù hợp.")
