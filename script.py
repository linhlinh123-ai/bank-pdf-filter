import pdfplumber
import pandas as pd
import os
import glob

def filter_ghtk_separate():
    # Tìm tất cả file pdf trong thư mục
    pdf_files = glob.glob("*.pdf")
    
    if not pdf_files:
        print("Lỗi: Không tìm thấy file .pdf nào trong folder!")
        return

    for pdf_path in pdf_files:
        output_file = pdf_path.replace(".pdf", ".xlsx")
        print(f"--- Đang lọc file: {pdf_path} ---")
        
        all_rows = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        for row in table:
                            # Lọc GHTK (không phân biệt hoa thường)
                            if any("GHTK" in str(cell).upper() for cell in row if cell):
                                all_rows.append(row)
            
            if all_rows:
                df = pd.DataFrame(all_rows)
                df.to_excel(output_file, index=False, header=False)
                print(f"-> Xong! Đã tạo file: {output_file}")
            else:
                print(f"-> File này không có giao dịch GHTK nào.")
        except Exception as e:
            print(f"-> Lỗi khi xử lý file {pdf_path}: {e}")

if __name__ == "__main__":
    filter_ghtk_separate()
