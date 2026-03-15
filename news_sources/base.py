from abc import ABC, abstractmethod


class NewsSource(ABC):
    name: str  # each subclass declares this

    @abstractmethod
    def fetch(self, limit: int = 10) -> list[dict]:
        """
        Returns a list of items, each with keys:
          - title: str
          - url: str
          - created_at: str  (YYYY-MM-DD)
          - points: int      (optional)
        """
        ...
