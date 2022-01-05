import re

open_parentheses        = r"\([^)]*"
closed_parentheses      = r"\s*(\(.*\)).*"

year_info               = r"\((\d+)\)"

volume_info             = r"((VOL|VOLUME):.*)|(:?\s*(VOL.?|VOLUME)\s*\d((\s*.*)|$))"        #tested
episode_info            = r"[^A-Za-z]EP:?\s*\d.*"
season_info             = r"SE:.*"
disc_info               = r"(DISC\s*(?:)\s*\d.*)"     ##broken
disc_content_info       = r"(\d+\.\d+.*)"

tv_series_info = "|".join(
    "({})".format(regexpr) for regexpr in
    [
        volume_info,
        episode_info,
        season_info,
        disc_info,
        disc_content_info,
    ]
)