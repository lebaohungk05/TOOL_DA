
DEFAULT_FEEDS = {
    "Vietnam_General": [
        f"https://vnexpress.net/rss/{cat}.rss" for cat in ["tin-moi-nhat", "the-gioi", "thoi-su", "kinh-doanh", "giai-tri", "the-thao", "phap-luat", "giao-duc", "suc-khoe", "doi-song", "du-lich", "khoa-hoc", "so-hoa", "xe", "y-kien", "tam-su", "cuoi"]
    ] + [
        f"https://tuoitre.vn/rss/{cat}.htm" for cat in ["tin-moi-nhat", "the-gioi", "phap-luat", "kinh-doanh", "xe", "van-hoa", "nhip-song-so", "giai-tri", "the-thao", "giao-duc", "khoa-hoc", "suc-khoe", "du-lich"]
    ] + [
        f"https://thanhnien.vn/rss/{cat}.rss" for cat in ["tin-24h", "thoi-su", "the-gioi", "kinh-te", "doi-song", "suc-khoe", "gioi-tre", "giao-duc", "van-hoa", "giai-tri", "the-thao", "cong-nghe-game", "xe"]
    ] + [
        f"https://vietnamnet.vn/rss/{cat}.rss" for cat in ["tin-moi-nhat", "thoi-su", "kinh-doanh", "the-gioi", "giai-tri", "the-thao", "doi-song", "giao-duc", "suc-khoe", "thong-tin-truyen-thong", "phap-luat", "oto-xe-may", "bat-dong-san"]
    ]
}

def get_all_feeds():
    """Retrieve a deduplicated list of all configured RSS feed URLs."""
    all_links = []
    for links in DEFAULT_FEEDS.values():
        all_links.extend(links)
    return list(set(all_links))
 