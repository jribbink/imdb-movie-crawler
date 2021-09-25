from util import string_similarity
import google_api
import re
import regex as patterns

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
    
    def get_knowledge_entity(self):
        query = self.generate_query()
        types = self.identify_type()
        response = google_api.search_knowledge_graph(query = query, types = types)

        elements = []
        for element in response["itemListElement"]:
            element["similarScore"] = string_similarity(query, element["result"]["name"])
            elements.append(element)

        element = max(elements, key=lambda x: x["similarScore"])
        if(element["similarScore"] < 0.9):
            ##raise Exception("Similarity check failed")                    THIS COULD BE BAD!!
            element = elements[0]
            
        return element
    
    def identify_type(self):
        # search for series season/ep identifier
        if re.search(patterns.tv_series_info, self.title):
            return 'TVSeries'

        return 'Movie'

    def generate_query(self):
        query = self.title

        # Move "THE" to front of title
        prefixes = [
            "THE",
            "A"
        ]
        for prefix in prefixes:
            regex = re.compile(", " + prefix)
            if(re.search(regex, query)):
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
            query = "{} {}".format(query, year)

        return query

    def get_year(self):
        year_search = re.search(patterns.year_info, self.title)
        return year_search.groups()[0] if year_search else None