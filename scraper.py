import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm
import re
import os
from datetime import datetime


headers = {"User-Agent": "Mozilla/5.0"}
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "scraped-data")
os.makedirs(output_dir, exist_ok=True)
checkpoint_path = os.path.join(output_dir, "done.log")
listing_base = "https://guland.vn"

province_slugs = {
    "soc-trang": "Sóc Trăng",
    "ha-noi": "Hà Nội",
    "ha-giang": "Hà Giang",
    "cao-bang": "Cao Bằng",
    "bac-kan": "Bắc Kạn",
    "tuyen-quang": "Tuyên Quang",
    "lao-cai": "Lào Cai",
    "dien-bien": "Điện Biên",
    "lai-chau": "Lai Châu",
    "son-la": "Sơn La",
    "yen-bai": "Yên Bái",
    "hoa-binh": "Hòa Bình",
    "thai-nguyen": "Thái Nguyên",
    "lang-son": "Lạng Sơn",
    "quang-ninh": "Quảng Ninh",
    "bac-giang": "Bắc Giang",
    "phu-tho": "Phú Thọ",
    "vinh-phuc": "Vĩnh Phúc",
    "bac-ninh": "Bắc Ninh",
    "hai-duong": "Hải Dương",
    "hai-phong": "Hải Phòng",
    "hung-yen": "Hưng Yên",
    "thai-binh": "Thái Bình",
    "ha-nam": "Hà Nam",
    "nam-dinh": "Nam Định",
    "ninh-binh": "Ninh Bình",
    "thanh-hoa": "Thanh Hóa",
    "nghe-an": "Nghệ An",
    "ha-tinh": "Hà Tĩnh",
    "quang-binh": "Quảng Bình",
    "quang-tri": "Quảng Trị",
    "thua-thien-hue": "Thừa Thiên Huế",
    "da-nang": "Đà Nẵng",
    "quang-nam": "Quảng Nam",
    "quang-ngai": "Quảng Ngãi",
    "binh-dinh": "Bình Định",
    "phu-yen": "Phú Yên",
    "khanh-hoa": "Khánh Hòa",
    "ninh-thuan": "Ninh Thuận",
    "binh-thuan": "Bình Thuận",
    "kon-tum": "Kon Tum",
    "gia-lai": "Gia Lai",
    "dak-lak": "Đắk Lắk",
    "dak-nong": "Đắk Nông",
    "lam-dong": "Lâm Đồng",
    "binh-phuoc": "Bình Phước",
    "tay-ninh": "Tây Ninh",
    "binh-duong": "Bình Dương",
    "dong-nai": "Đồng Nai",
    "ba-ria-vung-tau": "Bà Rịa - Vũng Tàu",
    "tp-ho-chi-minh": "TP. Hồ Chí Minh",
    "long-an": "Long An",
    "tien-giang": "Tiền Giang",
    "ben-tre": "Bến Tre",
    "tra-vinh": "Trà Vinh",
    "vinh-long": "Vĩnh Long",
    "dong-thap": "Đồng Tháp",
    "an-giang": "An Giang",
    "kien-giang": "Kiên Giang",
    "can-tho": "Cần Thơ",
    "hau-giang": "Hậu Giang",
    "bac-lieu": "Bạc Liêu",
    "ca-mau": "Cà Mau"
}

property_types = [
    "nha-mat-pho-mat-tien", "dat-tho-cu", "can-ho-chung-cu",
    "kho-nha-xuong", "van-phong", "phong-tro", "khach-san"
]

for province in province_slugs:
    for prop_type in property_types:
        try:
            checkpoint_key = f"{province}|{prop_type}"
            if os.path.exists(checkpoint_path) and checkpoint_key in open(checkpoint_path).read():
                print(f"⏩ Skipping {checkpoint_key}, already scraped.")
                continue

            print(f"\n🌍 Scraping {province} - {prop_type}")
            page = 1
            all_data = []
            while True:
                print(f"\n🔎 Page {page}...")
                url = f"https://guland.vn/mua-ban-{prop_type}-{province}?page={page}"
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"❌ Failed at page {page}")
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                listings = soup.select(".l-sdb-list__single")

                if not listings:
                    print("✅ No more listings found.")
                    break

                print(f"📦 {len(listings)} listings on page {page}")

                for item in tqdm(listings, desc=f"🔄 {province}-{prop_type}-p{page}", unit="listing"):
                    try:
                        detail_url = item.select_one(".c-sdb-card__tle a")["href"]
                        full_url = detail_url if "http" in detail_url else listing_base + detail_url
                        detail_resp = requests.get(full_url, headers=headers)
                        detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

                        listing_id = "N/A"
                        for span in detail_soup.select(".dtl-stl__row span"):
                            if "Mã tin" in span.get_text():
                                b = span.find("b")
                                if b:
                                    listing_id = b.get_text(strip=True)
                                break

                        title_tag = detail_soup.select_one(".dtl-tle")
                        vip_tag = title_tag.select_one(".vrf-bdg")
                        is_vip = bool(vip_tag)
                        if vip_tag:
                            vip_tag.extract()
                        title = title_tag.get_text(strip=True)

                        price = detail_soup.select_one(".dtl-prc__ttl").get_text(strip=True)
                        area = detail_soup.select_one(".dtl-prc__dtc").get_text(strip=True)

                        location = detail_soup.select_one(".dtl-stl__row > span")
                        location = location.get_text(strip=True) if location else "N/A"

                        updated_time = "N/A"
                        for span in detail_soup.select(".dtl-stl__row span"):
                            text = span.get_text()
                            if "Cập nhật" in text:
                                updated_time = text.replace("Cập nhật", "").strip()

                        def get_detail_value(label):
                            tag = detail_soup.find("div", class_="s-dtl-inf__lbl", string=lambda x: x and label in x)
                            return tag.find_next_sibling("div").get_text(strip=True) if tag else "N/A"

                        property_type_label = get_detail_value("Loại BĐS")
                        width = get_detail_value("Chiều ngang")
                        length = get_detail_value("Chiều dài")
                        bedrooms = get_detail_value("Số phòng ngủ")
                        bathrooms = get_detail_value("Số phòng tắm")
                        floors = get_detail_value("Số tầng")
                        position = get_detail_value("Vị trí")
                        direction = get_detail_value("Hướng cửa chính")
                        alley_width = get_detail_value("Đường/hẻm vào rộng")
                        road_type = get_detail_value("Loại đường")

                        description_tag = detail_soup.select_one(".dtl-inf__dsr")
                        description = description_tag.get_text(strip=True) if description_tag else "N/A"

                        gps_link = detail_soup.select_one("a.map-direction")
                        latitude = longitude = "N/A"
                        if gps_link:
                            href = gps_link.get("href", "")
                            match = re.search(r'query=([\d.]+),([\d.]+)', href)
                            if match:
                                latitude, longitude = match.group(1), match.group(2)

                        image_urls = []
                        for div in detail_soup.select(".media-thumb-wrap__inner"):
                            style = div.get("style", "")
                            match = re.search(r"url\('([^']+)'\)", style)
                            if match:
                                url = match.group(1)
                                if not url.endswith("map-icon.jpg"):
                                    image_urls.append(url)

                        images = "; ".join(image_urls) if image_urls else "N/A"

                        avatar_url = "0"
                        agent_role = "N/A"
                        agent_name = "N/A"
                        agent_listing_count = "N/A"

                        avatar_tag = detail_soup.select_one(".dtl-aut__avt img")
                        if avatar_tag:
                            src = avatar_tag.get("src", "")
                            if "profile.png" not in src:
                                avatar_url = src

                        role_tag = detail_soup.select_one(".dtl-aut__rol")
                        if role_tag:
                            agent_role = role_tag.get_text(strip=True)

                        name_tag = detail_soup.select_one(".dtl-aut__tle")
                        if name_tag:
                            agent_name = name_tag.get_text(strip=True)

                        listing_count_tag = detail_soup.select_one(".dtl-aut__stl")
                        if listing_count_tag:
                            match = re.search(r'(\d+)', listing_count_tag.get_text())
                            if match:
                                agent_listing_count = match.group(1)

                        scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        all_data.append([
                            title, price, area, location, listing_id, updated_time,
                            property_type_label, width, length, bedrooms, bathrooms, floors,
                            position, direction, alley_width, road_type,
                            description, full_url, latitude, longitude, is_vip, images,
                            avatar_url, agent_role, agent_name, agent_listing_count,
                            province, prop_type, scraped_at
                        ])
                        time.sleep(0.5)

                    except Exception as e:
                        print(f"⚠️ Listing error: {e}")
                        continue

                page += 1
                time.sleep(2)

            # Save per province
            outpath = os.path.join(output_dir, f"{province}.csv")
            df = pd.DataFrame(all_data, columns=[
                "Title", "Price", "Area", "Location", "Listing ID", "Last Updated",
                "Property Type", "Width", "Length", "Bedrooms", "Bathrooms", "Floors",
                "Position", "Direction", "Alley Width", "Road Type",
                "Description", "URL", "Latitude", "Longitude", "VIP Account", "Images",
                "Avatar", "Agent Role", "Agent Name", "Agent Listing Count",
                "Province", "Property Type Slug", "Scraped At"
            ])

            if os.path.exists(outpath):
                df.to_csv(outpath, mode='a', header=False, index=False, encoding='utf-8-sig')
            else:
                df.to_csv(outpath, index=False, encoding='utf-8-sig')

            with open(checkpoint_path, "a") as log:
                log.write(f"{checkpoint_key}\n")

            print(f"✅ Saved {len(all_data)} listings for {province}-{prop_type}")

        except Exception as err:
            with open(os.path.join(output_dir, "failed.log"), "a") as fail:
                fail.write(f"{province}|{prop_type} - {err}\n")
            print(f"❌ Failed {province}|{prop_type}: {err}")
            continue
