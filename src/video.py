import util.google_api as google_api
import re
import util.regex as patterns

class QueryInfo:
    def __init__(self, title, type, year = None):
        self.title = title
        self.type = type
        self.year = year
        self.__query_index = 0

    @property
    def __queries(self):
        ret = {
            "default": [
                "{title} {year} {type}" if self.year is not None else "{title} {type}",
                "{title}",
            ]
        }

        ret["Film"] = ret["default"]
        ret["TV Series"] = ret["default"]

        return ret.get(self.type, ret["default"])

    @property
    def query(self):
        if (self.__query_index >= len(self.__queries)):
            return None
        return self.__queries[self.__query_index].format(title = self.title, year = self.year, type = self.type)
    
    def next_query(self):
        self.__query_index += 1

class VideoInfo:
    def __init__(self, *args, **kwargs):
        self.description = kwargs["description"] if "description" in kwargs else None
        self.imdb_title = kwargs["imdb_title"] if "imdb_title" in kwargs else None
        self.directors: list[str] = kwargs["directors"] if "directors" in kwargs else None
        self.writers: list[str] = kwargs["writers"] if "writers" in kwargs else None
        self.stars: list[str] = kwargs["stars"] if "stars" in kwargs else None
        self.genres: list[str] = kwargs["genres"] if "genres" in kwargs else None
        self.rating = kwargs["rating"] if "rating" in kwargs else None
        self.film_length = kwargs["film_length"] if "film_length" in kwargs else None
        self.parental_rating = kwargs["parental_rating"] if "parental_rating" in kwargs else None
        self.release_info = kwargs["release_info"] if "release_info" in kwargs else None
        self.image: str = kwargs["image"] if "image" in kwargs else None
        self.imdb_url = kwargs["imdb_url"] if "imdb_url" in kwargs else None

class Video:
    def __init__(self, *args, **kwargs):
        self.code = kwargs["code"]
        self.title = kwargs["title"]
        self.rented = kwargs["rented"]
        self.online = kwargs["online"]
        self.type = kwargs["type"]
        self.category = kwargs["category"]
        self.criterion = kwargs["criterion"]
        self.search = kwargs["search"]
        if("info" in kwargs):
            self.info: VideoInfo = VideoInfo(**kwargs["info"])
    
    def get_knowledge_entity(self, q = None):
        query = self.generate_query()
        response = google_api.serp_search(q = query)

        print(query)

        if(not "knowledge_graph" in response):
            raise VideoNotFoundException()
            
        return response["knowledge_graph"]

    def correct_query(self, query):
        search_result = google_api.search_custom_search(q=query)
        if "spelling" in search_result:
            return search_result["spelling"]["correctedQuery"]
        else:
            raise VideoNotFoundException()

    def identify_type(self):
        # search for series season/ep identifier
        if re.search(patterns.tv_series_info, self.title):
            return 'TV Series'

        return 'Film'

    @property
    def query(self):
        query = self.title

        # Move "THE" to front of title
        prefixes = [
            r"THE",
            r"A"
        ]
        for prefix in prefixes:
            regex = r", " + prefix
            if(re.search(regex + "(\s|$)", query)):
                query = prefix + " " + re.sub(regex, "", query)

        removals = [
            patterns.closed_parentheses,    # remove all parentheses
            patterns.tv_series_info,        # remove series season/ep identifier *messy, removes until end of string
            patterns.open_parentheses,      # remove open parentheses
            #r"BBC.*"                       # remove BBC identifier and all following
        ]

        for removal in removals:
            query = re.sub(removal, "", query)

        # Add year
        year = self.get_year()
        if year:
            query = "{} ({})".format(query, year)

        # Get type
        type = self.identify_type()

        # Strip query string
        query = query.strip()

        return QueryInfo(query, type, year)

    def get_year(self):
        year_search = re.search(patterns.year_info, self.title)
        return year_search.groups()[0] if year_search else None


class VideoNotFoundException(Exception):
    pass