import pandas as pd
import json
import os

def main():
    try:
        # Lấy đường dẫn của thư mục chứa script hiện tại (thư mục 'data')
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 1. Đọc dữ liệu từ 3 file (tự động nối đường dẫn)
        print("Đang đọc dữ liệu từ các file...")
        df_hn = pd.read_csv(os.path.join(base_dir, 'hn.csv'))
        df_hcm = pd.read_csv(os.path.join(base_dir, 'hcm.csv'))
        df_dn = pd.read_csv(os.path.join(base_dir, 'dn.csv'))

        # Thêm cột 'city' để phân biệt dữ liệu thuộc thành phố nào
        df_hn['city'] = 'Hà Nội'
        df_hcm['city'] = 'Hồ Chí Minh'
        df_dn['city'] = 'Đà Nẵng'

        # 2. Tạo một dataframe tổng hợp từ 3 file
        df_combined = pd.concat([df_hn, df_hcm, df_dn], ignore_index=True)
        print(f"Tổng số dòng ban đầu: {len(df_combined)}")

        # 3. LÀM SẠCH DỮ LIỆU
        print("\n--- ĐANG LÀM SẠCH DỮ LIỆU ---")
        
        # a. Xóa các dòng bị trùng lặp hoàn toàn
        df_clean = df_combined.drop_duplicates()
        
        # b. Xóa các dòng có giá trị rỗng (NaN) ở các cột bắt buộc
        df_clean = df_clean.dropna(subset=['title', 'price', 'acreage', 'address'])
        
        # c. Xóa bỏ các khoảng trắng dư thừa ở đầu và cuối chuỗi (trim)
        df_clean.loc[:, 'title'] = df_clean['title'].str.strip()
        df_clean.loc[:, 'address'] = df_clean['address'].str.strip()
        
        # d. Loại bỏ các dòng dữ liệu nhiễu/bất hợp lý (ví dụ: giá <= 0 hoặc diện tích <= 0)
        df_clean = df_clean[(df_clean['price'] > 0) & (df_clean['acreage'] > 0)]
        
        print(f"Tổng số dòng sau khi làm sạch: {len(df_clean)}")
        print(f"Đã loại bỏ: {len(df_combined) - len(df_clean)} dòng dữ liệu nhiễu/rỗng.")

        # 4. LƯU RA FILE JSON
        output_file = os.path.join(base_dir, 'tong_hop_phong_tro.json')
        
        # Chuyển DataFrame đã clean thành danh sách các dictionary (dạng JSON Array)
        records = df_clean.to_dict(orient='records')
        
        # Ghi ra file JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ Đã lưu dữ liệu làm sạch và tổng hợp thành file JSON: {output_file}")
        
    except FileNotFoundError as e:
        print(f"Lỗi: Không tìm thấy file dữ liệu. Chi tiết: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")

if __name__ == "__main__":
    main()
