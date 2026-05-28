from typing import Protocol

class ContentFetcherProtocol(Protocol):
    """
    Protocol defining the interface for fetching and extracting article content.
    """
    async def fetch_contents(self, urls: list[str]) -> list[str]:
        """
        Fetch HTML from multiple URLs and return extracted text contents.
        
        Args:
            urls: The target URLs to fetch.
            
        Returns:
            A list of extracted text contents (same order as input).
        """
        ...
