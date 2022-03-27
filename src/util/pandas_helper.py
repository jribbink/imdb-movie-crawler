import pandas as pd
from pandas.core.frame import DataFrame
from video import Video, VideoInfo


def videos_to_data_frame(videos: "list[Video]"):
    tuple_videos = []

    for video in videos:
        if hasattr(video, "info") and video.info.is_populated():
            tuple_videos.append(
                (
                    video.info.description.replace(
                        "... Read all",
                        '... <a href="{}">Read all</a>'.format(video.info.imdb_url),
                    ),
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
                    ("http://173.183.83.5/" + video.info.image[7:])
                    if video.info.image is not None
                    else None,
                    video.info.imdb_url,
                    video.category,
                    video.code,
                    video.title,
                    video.rented,
                )
            )

    columns = (
        "post_content",
        "post_title",
        "attribute:pa_directors",
        "attribute:pa_writers",
        "attribute:pa_stars",
        "attribute:pa_genres",
        "attribute:pa_rating",
        "attribute:pa_film-length",
        "attribute:pa_parental-rating",
        "attribute:pa_release-info",
        "images",
        "attribute:pa_imdb-url",
        "attribute:pa_leo-category",
        "attribute:pa_leo-code",
        "attribute:pa_leo-title",
        "attribute:pa_leo-rented",
    )
    df = pd.DataFrame(tuple_videos, columns=columns)
    return df


def save_to_csv(df: DataFrame):
    df.to_csv("df.csv")
