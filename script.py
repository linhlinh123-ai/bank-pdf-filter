import pdfplumber
import pandas as pd
import os
import glob

def filter_ghtk_smart():
    pdf_files = glob.glob("*.pdf")
    
    # Danh sách từ khóa quét (viết hoa hết để so khớp)
    keywords = ["GHTK", "GIAO HANG TIET KIEM", "GIAOHANGTIETKIEM", "GIAO HÀNG TIẾT KIỆM"]
    
    if not pdf_files:
        print("Lỗi: Không tìm thấy file .pdf nào!")
        return

    for pdf_path in pdf_files:
        output_file = pdf_path.replace(".pdf", ".xlsx")
        print(f"--- Đang quét sâu file: {pdf_path} ---")
        
        all_rows = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        for row in table:
                            # Chuyển cả dòng thành 1 chuỗi chữ hoa để check cho nhanh
                            row_text = " ".join([str(cell).upper() for cell in row if cell])
                            
                            # Nếu chứa bất kỳ từ khóa nào trong danh sách thì hốt luôn
                            if any(kw in row_text for kw in keywords):
                                all_rows.append(row)
            
            if all_rows:
                df = pd.DataFrame(all_rows)
                df.to_excel(output_file, index=False, header=False)
                print(f"-> Ngon! Đã lọc xong {len(all_rows)} giao dịch vào: {output_file}")
            else:
                print(f"-> File này không thấy bóng dáng GHTK.")
        except Exception as e:
            print(f"-> Lỗi: {e}")

if __name__ == "__main__":
    filter_ghtk_smart()
