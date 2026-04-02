import pdfplumber
import pandas as pd
import os

def filter_ghtk():
    pdf_path = "input.pdf"
    output_file = "output.xlsx"
    keyword = "GHTK"
    all_rows = []

    if not os.path.exists(pdf_path):
        print("Lỗi: Không tìm thấy file input.pdf trong thư mục!")
        return

    print("Đang lọc 800 trang, đợi tí...")
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table:
                    # Lọc dòng chứa chữ GHTK (không phân biệt hoa thường)
                    if any(keyword.upper() in str(cell).upper() for cell in row if cell):
                        all_rows.append(row)

    if all_rows:
        df = pd.DataFrame(all_rows)
        df.to_excel(output_file, index=False, header=False)
        print(f"Xong! Đã lưu kết quả vào {output_file}")
    else:
        print("Không tìm thấy giao dịch GHTK nào.")

if __name__ == "__main__":
    filter_ghtk()
