from urllib.parse import quote
import pandas as pd
from pandas.core.frame import DataFrame
from util.util import load_videos
from video import Video, VideoInfo


def videos_to_data_frame(videos: "list[Video]"):
    tuple_videos = []

    explore = set(
        v.info.imdb_url
        for v in videos
        if hasattr(v, "info") and hasattr(v.info, "imdb_url")
    )

    def add_videos(explore_vids):
        video = explore_vids[0]
        if hasattr(video, "info") and video.info.is_populated():
            tuple_videos.append(
                (
                    video.info.description.replace(
                        "... Read all",
                        '... <a href="{}">Read all</a>'.format(video.info.imdb_url),
                    )
                    if video.info.description
                    else "",
                    video.info.imdb_title or video.title,
                    video.info.imdb_title,
                    "|".join(video.info.directors)
                    if video.info.directors is not None
                    else None,
                    "|".join(video.info.writers)
                    if video.info.writers is not None
                    else None,
                    "|".join(video.info.stars)
                    if video.info.stars is not None
                    else None,
                    "|".join(video.info.genres)
                    if video.info.genres is not None
                    else None,
                    video.info.rating,
                    video.info.film_length,
                    video.info.parental_rating,
                    video.info.release_info,
                    ("http://173.183.83.5/" + quote(video.info.image[7:]))
                    if video.info.image is not None
                    else None,
                    video.info.imdb_url,
                    video.category,
                    video.code,
                    video.rented,
                    "|".join(v.title for v in explore_vids),
                    "1|1|1",
                    video.info.sku,
                    "variable",
                    "false",
                )
            )

    for url in explore:
        explore_vids = [v for v in videos if v.info.imdb_url == url and url is not None]
        add_videos(explore_vids)

    missing_vids = [
        v
        for v in videos
        if not hasattr(v, "info")
        or not hasattr(v.info, "imdb_url")
        or v.info.imdb_url is None
    ]
    for vid in missing_vids:
        add_videos([vid])

    columns = (
        "post_content",
        "post_title",
        "imdb_title",
        "attribute:pa_directors",
        "attribute:pa_writers",
        "attribute:pa_stars",
        "attribute:pa_genres",
        "attribute:pa_rating",
        "attribute:pa_film_length",
        "attribute:pa_parental_rating",
        "attribute:pa_release_info",
        "images",
        "attribute:pa_imdb_url",
        "attribute:pa_leo_category",
        "attribute:pa_leo_code",
        "attribute:pa_leo_rented",
        "attribute:pa_leo_title",
        "attribute_data:pa_leo_title",
        "sku",
        "tax:product_type",
        "meta:knowledge_graph",
    )
    df = pd.DataFrame(tuple_videos, columns=columns)
    return df


def get_variation_df(videos: "list[Video]"):
    tuple_videos = []

    for video in videos:
        if not type(video.info) == VideoInfo:
            print("WHAT")
        if hasattr(video, "info") and video.info.is_populated():
            found_index = next(
                (
                    i
                    for i, _ in enumerate(tuple_videos)
                    if tuple_videos[0] == video.title
                    and tuple_videos[1] == video.info.sku
                ),
                None,
            )
            if found_index:
                tuple_videos[found_index][2] += 1
            else:
                tuple_videos.append((video.title, video.info.sku, 1, 0))

    columns = (
        "attribute:pa_leo_title",
        "parent_sku",
        "stock",
        "regular_price",
    )
    df = pd.DataFrame(tuple_videos, columns=columns)
    return df


def save_to_csv(df: DataFrame):
    df.to_csv("df.csv")
