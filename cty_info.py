import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import io

# API Key của SerpAPI (Thay bằng API của bạn nếu cần)
API_KEY = "b8963334c880b8ed0bf2b4219492435b4da63d82c4f13d68fbd7bae4142d4b33"

# Headers giả lập trình duyệt
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

def get_masothue_link(company_name):
    """Tìm kiếm công ty trên Google để lấy link chuẩn từ masothue.com"""
    search_url = f"https://serpapi.com/search?engine=google&q={company_name}+site:masothue.com&api_key={API_KEY}"
    response = requests.get(search_url)
    results = response.json()

    for result in results.get("organic_results", []):
        if "masothue.com" in result["link"]:
            return result["link"]
    
    return None

def scrape_company_info(company_name, url):
    """Trích xuất thông tin công ty từ masothue.com"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"⚠ Lỗi khi truy cập {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    company_data = {
        "Tên công ty": company_name,
        "Tên quốc tế": "N/A",
        "Tên viết tắt": "N/A",
        "Mã số thuế": "N/A",
        "Địa chỉ": "N/A",
        "Người đại diện": "N/A",
        "Điện thoại": "N/A",
        "Ngày hoạt động": "N/A",
        "Quản lý bởi": "N/A",
        "Loại hình DN": "N/A",
        "Tình trạng": "N/A",
        "Ngành nghề chính": "N/A",
    }

    table = soup.find("table", class_="table-taxinfo")
    if not table:
        st.warning(f"❌ Không tìm thấy dữ liệu trên trang {url}")
        return None

    rows = table.find_all("tr")

    for row in rows:
        columns = row.find_all("td")
        if len(columns) < 2:
            continue  # Nếu không có đủ cột dữ liệu thì bỏ qua

        label = columns[0].text.strip()
        value = columns[1].text.strip()

        if not label or not value:
            continue

        if "Tên quốc tế" in label:
            company_data["Tên quốc tế"] = value
        elif "Tên viết tắt" in label:
            company_data["Tên viết tắt"] = value
        elif "Mã số thuế" in label:
            company_data["Mã số thuế"] = value
        elif "Địa chỉ" in label:
            company_data["Địa chỉ"] = value
        elif "Người đại diện" in label:
            company_data["Người đại diện"] = value
        elif "Điện thoại" in label:
            company_data["Điện thoại"] = value.replace(" Ẩn thông tin", "")
        elif "Ngày hoạt động" in label:
            company_data["Ngày hoạt động"] = value
        elif "Quản lý bởi" in label:
            company_data["Quản lý bởi"] = value
        elif "Loại hình DN" in label:
            company_data["Loại hình DN"] = value
        elif "Tình trạng" in label:
            company_data["Tình trạng"] = value
        elif "Ngành nghề chính" in label:
            company_data["Ngành nghề chính"] = value

    return company_data

# Giao diện Streamlit
st.title("🔍 Tra cứu thông tin công ty")
st.write("Nhập danh sách tên công ty vào bên dưới:")

company_input = st.text_area("Nhập danh sách công ty (mỗi dòng một công ty):")
company_names = [line.strip() for line in company_input.split("\n") if line.strip()]

if st.button("Tra cứu"):
    if not company_names:
        st.warning("Vui lòng nhập ít nhất một tên công ty!")
    else:
        results = []
        
        for idx, company in enumerate(company_names, start=1):
            st.write(f"🔍 Đang tìm kiếm: **{company}**...")
            url = get_masothue_link(company)

            if url:
                st.success(f"✅ Tìm thấy: {url}")
                data = scrape_company_info(company, url)
            else:
                st.warning(f"❌ Không tìm thấy URL cho {company}")
                data = {
                    "Tên công ty": company,
                    "Tên quốc tế": "N/A",
                    "Tên viết tắt": "N/A",
                    "Mã số thuế": "N/A",
                    "Địa chỉ": "N/A",
                    "Người đại diện": "N/A",
                    "Điện thoại": "N/A",
                    "Ngày hoạt động": "N/A",
                    "Quản lý bởi": "N/A",
                    "Loại hình DN": "N/A",
                    "Tình trạng": "N/A",
                    "Ngành nghề chính": "N/A",
                }
            
            results.append(data)
            delay = random.randint(3, 5)
            st.write(f"⏳ Chờ {delay} giây trước khi tiếp tục...\n")
            time.sleep(delay)

        df = pd.DataFrame(results)
        
        # Hiển thị DataFrame
        st.dataframe(df)

        # Xuất file Excel để tải về
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Company Info")
            writer.close()
        
        output.seek(0)
        
        st.download_button(
            label="📥 Tải file Excel",
            data=output,
            file_name="company_info.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

