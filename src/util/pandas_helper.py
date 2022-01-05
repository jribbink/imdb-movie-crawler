import pandas as pd
from pandas.core.frame import DataFrame
from video import Video

def videos_to_data_frame(videos: 'list[Video]'):
    tuple_videos = []
    for video in videos:
        if(hasattr(video, "info")):
            tuple_videos.append(
                (
                    video.info.description,
                    video.info.imdb_title,
                    "|".join(video.info.directors) if video.info.directors is not None else None,
                    "|".join(video.info.writers) if video.info.writers is not None else None,
                    "|".join(video.info.stars) if video.info.stars is not None else None,
                    "|".join(video.info.genres) if video.info.genres is not None else None,
                    video.info.rating,
                    video.info.film_length,
                    video.info.parental_rating,
                    video.info.release_info,
                    "https://leosvideos.ca/video_images/" + video.info.image[7:],
                    video.info.imdb_url,
                    video.category,
                    video.code,
                    video.title,
                    video.rented,
                )
            )

    columns = (
        "description",
        "imdb_title",
        "attribute:directors",
        "meta:writers",
        "meta:stars",
        "meta:genres",
        "meta:rating",
        "meta:film_length",
        "meta:parental_rating",
        "meta:release_info",
        "images",
        "imdb_url",
        "meta:leo_category",
        "meta:leo_code",
        "meta:leo_title",
        "meta:leo_rented",
    )
    df = pd.DataFrame(tuple_videos, columns=columns)
    return df

def save_to_csv(df: DataFrame):
    df.to_csv("df.csv")