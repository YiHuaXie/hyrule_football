from .match_service import get_hot_match_list, request_hot_match_list, get_match_for_name
from .odds_service import get_odds_for_match

# get_aisa_odds_for_match, get_euro_odds_for_match,

__all__ = [
    "get_hot_match_list",
    "request_hot_match_list",
    "get_match_for_name",
    # "get_aisa_odds_for_match",
    # "get_euro_odds_for_match",
    "get_odds_for_match",
]
