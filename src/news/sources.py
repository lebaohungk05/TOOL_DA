
DEFAULT_FEEDS = {
    "Vietnam_General": [
        f"https://vnexpress.net/rss/{cat}.rss" for cat in ["tin-moi-nhat", "the-gioi", "thoi-su", "kinh-doanh", "giai-tri", "the-thao", "phap-luat", "giao-duc", "suc-khoe", "doi-song", "du-lich", "khoa-hoc", "so-hoa", "xe", "y-kien", "tam-su", "cuoi"]
    ] + [
        f"https://tuoitre.vn/rss/{cat}.htm" for cat in ["tin-moi-nhat", "the-gioi", "phap-luat", "kinh-doanh", "xe", "van-hoa", "nhip-song-so", "giai-tri", "the-thao", "giao-duc", "khoa-hoc", "suc-khoe", "du-lich"]
    ],
    "Global_Major": [
        "http://feeds.bbci.co.uk/news/rss.xml",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "http://feeds.bbci.co.uk/news/business/rss.xml",
        "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "http://rss.cnn.com/rss/edition.rss",
        "http://rss.cnn.com/rss/edition_world.rss",
        "http://rss.cnn.com/rss/edition_technology.rss",
        "http://rss.cnn.com/rss/edition_business.rss",
        "http://rss.cnn.com/rss/edition_space.rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
        "https://www.reutersagency.com/feed/?post_type=best",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.theguardian.com/world/rss",
        "https://www.theguardian.com/international/rss"
    ],
    "Tech_Specialized": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
        "https://www.cnet.com/rss/news/",
        "https://www.zdnet.com/news/rss.xml",
        "https://mashable.com/feeds/rss/all",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.engadget.com/rss.xml"
    ],
    "Finance_Global": [
        "https://www.ft.com/?format=rss",
        "https://www.forbes.com/real-time/feed/",
        "https://www.economist.com/sections/international/rss.xml",
        "https://www.investing.com/rss/news.rss"
    ]
}

def get_all_feeds():
    all_links = []
    for links in DEFAULT_FEEDS.values():
        all_links.extend(links)
    return list(set(all_links)) 