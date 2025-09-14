import requests
from bs4 import BeautifulSoup
import pandas as pd
import time, re, os
from tqdm import tqdm
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========================
# CONFIGURATION
# ========================
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_WORKERS = 16   # number of parallel threads for detail pages
PAGE_SLEEP = 2     # pause between listing pages (seconds)
DETAIL_TIMEOUT = 15  # timeout for detail requests (seconds)
CUTOFF_COUNT = 45  # stop paginating if fewer listings than this on a page
# ========================

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "scraped-data")
os.makedirs(output_dir, exist_ok=True)
checkpoint_dir = os.path.join(output_dir, "checkpoint")
os.makedirs(checkpoint_dir, exist_ok=True)
checkpoint_path = os.path.join(checkpoint_dir, "done.log")
listing_base = "https://guland.vn"

session = requests.Session()
session.headers.update(HEADERS)

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

# ----------------------------
# DETAIL PAGE PARSER (worker)
# ----------------------------
def parse_detail(full_url, province, prop_type):
    try:
        resp = session.get(full_url, timeout=DETAIL_TIMEOUT)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")

        listing_id = "N/A"
        for span in soup.select(".dtl-stl__row span"):
            if "Mã tin" in span.get_text():
                b = span.find("b")
                if b:
                    listing_id = b.get_text(strip=True)
                break

        title_tag = soup.select_one(".dtl-tle")
        if title_tag:
            vip_tag = title_tag.select_one(".vrf-bdg")
            is_vip = bool(vip_tag)
            if vip_tag:
                vip_tag.extract()
            title = title_tag.get_text(strip=True)
        else:
            is_vip, title = False, "N/A"

        def safe_text(sel):
            tag = soup.select_one(sel)
            return tag.get_text(strip=True) if tag else "N/A"

        price = safe_text(".dtl-prc__ttl")
        area = safe_text(".dtl-prc__dtc")
        location = safe_text(".dtl-stl__row > span")

        updated_time = "N/A"
        for span in soup.select(".dtl-stl__row span"):
            text = span.get_text()
            if "Cập nhật" in text:
                updated_time = text.replace("Cập nhật", "").strip()

        def get_detail_value(label):
            tag = soup.find("div", class_="s-dtl-inf__lbl", string=lambda x: x and label in x)
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

        description = safe_text(".dtl-inf__dsr")

        gps_link = soup.select_one("a.map-direction")
        latitude = longitude = "N/A"
        if gps_link:
            href = gps_link.get("href", "")
            match = re.search(r'query=([\d.]+),([\d.]+)', href)
            if match:
                latitude, longitude = match.group(1), match.group(2)

        image_urls = []
        for div in soup.select(".media-thumb-wrap__inner"):
            style = div.get("style", "")
            match = re.search(r"url\('([^']+)'\)", style)
            if match:
                url = match.group(1)
                if not url.endswith("map-icon.jpg"):
                    image_urls.append(url)
        images = "; ".join(image_urls) if image_urls else "N/A"

        avatar_url, agent_role, agent_name, agent_listing_count = "0", "N/A", "N/A", "N/A"
        avatar_tag = soup.select_one(".dtl-aut__avt img")
        if avatar_tag and "profile.png" not in avatar_tag.get("src", ""):
            avatar_url = avatar_tag["src"]

        role_tag = soup.select_one(".dtl-aut__rol")
        if role_tag: agent_role = role_tag.get_text(strip=True)
        name_tag = soup.select_one(".dtl-aut__tle")
        if name_tag: agent_name = name_tag.get_text(strip=True)
        listing_count_tag = soup.select_one(".dtl-aut__stl")
        if listing_count_tag:
            m = re.search(r'(\d+)', listing_count_tag.get_text())
            if m: agent_listing_count = m.group(1)

        scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return [
            title, price, area, location, listing_id, updated_time,
            property_type_label, width, length, bedrooms, bathrooms, floors,
            position, direction, alley_width, road_type,
            description, full_url, latitude, longitude, is_vip, images,
            avatar_url, agent_role, agent_name, agent_listing_count,
            province, prop_type, scraped_at
        ]
    except Exception:
        return None

# ----------------------------
# PARALLEL FETCH FOR A PAGE
# ----------------------------
def fetch_page_details(listings, province, prop_type, max_workers=MAX_WORKERS):
    urls = []
    for item in listings:
        link = item.select_one(".c-sdb-card__tle a")
        if link and link.get("href"):
            href = link["href"]
            urls.append(href if "http" in href else listing_base + href)

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(parse_detail, url, province, prop_type) for url in urls]
        for fut in as_completed(futures):
            res = fut.result()
            if res: results.append(res)
    return results

# ----------------------------
# MAIN LOOP
# ----------------------------
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
                response = session.get(url, timeout=DETAIL_TIMEOUT)
                if response.status_code != 200:
                    print(f"❌ Failed at page {page}")
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                listings = soup.select(".l-sdb-list__single")

                if not listings:
                    print("✅ No more listings found.")
                    break

                print(f"📦 {len(listings)} listings on page {page}")

                # cutoff condition
                last_page = False
                if len(listings) < CUTOFF_COUNT:
                    print(f"ℹ️ Less than {CUTOFF_COUNT} listings → scrape this page and stop pagination after.")
                    last_page = True

                # parallel scrape detail pages
                page_results = fetch_page_details(listings, province, prop_type, max_workers=MAX_WORKERS)
                all_data.extend(page_results)

                page += 1
                if last_page:
                    break
                time.sleep(PAGE_SLEEP)

            # save per province
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