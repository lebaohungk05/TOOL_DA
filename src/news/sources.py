from typing import Dict, List, TypedDict

class PublisherConfig(TypedDict):
    """Configuration shape for each Vietnamese news publisher."""
    base_url: str
    categories: List[str]

# Structured mappings for each publisher's category configurations
PUBLISHERS: Dict[str, PublisherConfig] = {
    "VnExpress": {
        "base_url": "https://vnexpress.net/rss/{cat}.rss",
        "categories": [
            "tin-moi-nhat", "the-gioi", "thoi-su", "kinh-doanh", "giai-tri",
            "the-thao", "phap-luat", "giao-duc", "suc-khoe", "doi-song",
            "du-lich", "khoa-hoc", "so-hoa", "y-kien", "tam-su", "cuoi"
        ]
    },
    "Tuổi Trẻ": {
        "base_url": "https://tuoitre.vn/rss/{cat}.rss",
        "categories": [
            "tin-moi-nhat", "the-gioi", "phap-luat", "kinh-doanh", "xe",
            "van-hoa", "nhip-song-so", "giai-tri", "the-thao", "giao-duc",
            "khoa-hoc", "suc-khoe", "du-lich"
        ]
    },
    "Thanh Niên": {
        "base_url": "https://thanhnien.vn/rss/{cat}.rss",
        "categories": [
            "tin-24h", "thoi-su", "the-gioi", "kinh-te", "doi-song",
            "suc-khoe", "gioi-tre", "giao-duc", "van-hoa", "giai-tri",
            "the-thao", "xe"
        ]
    },
    "VietnamNet": {
        "base_url": "https://vietnamnet.vn/rss/{cat}.rss",
        "categories": [
            "thoi-su", "kinh-doanh", "the-gioi", "giai-tri",
            "the-thao", "doi-song", "giao-duc", "suc-khoe", "thong-tin-truyen-thong",
            "phap-luat", "oto-xe-may", "bat-dong-san"
        ]
    }
}

# Maintain backward compatibility for DEFAULT_FEEDS structure
DEFAULT_FEEDS: Dict[str, List[str]] = {
    "Vietnam_General": [
        pub_info["base_url"].format(cat=cat)
        for pub_info in PUBLISHERS.values()
        for cat in pub_info["categories"]
    ]
}

def resolve_category_to_url(publisher: str, category: str) -> str:
    """
    Resolve a specific publisher category name to its complete absolute RSS URL.

    Args:
        publisher: The exact name of the news publisher (e.g. 'VnExpress').
        category: The raw category key name (e.g. 'so-hoa').

    Returns:
        The fully formatted absolute RSS feed URL.

    Raises:
        ValueError: If the publisher name is unknown or the category is invalid.
    """
    pub_info = PUBLISHERS.get(publisher)
    if not pub_info:
        raise ValueError(f"Unknown publisher: {publisher}")
        
    categories = pub_info.get("categories", [])
    if category not in categories:
        raise ValueError(f"Invalid category '{category}' for publisher '{publisher}'")
        
    base_url = pub_info.get("base_url")
    return base_url.format(cat=category)

def get_all_feeds() -> List[str]:
    """
    Retrieve a deduplicated list of all configured RSS feed URLs.

    Returns:
        A list of deduplicated absolute RSS URLs.
    """
    all_links: List[str] = []
    for links in DEFAULT_FEEDS.values():
        all_links.extend(links)
    return list(set(all_links))
 