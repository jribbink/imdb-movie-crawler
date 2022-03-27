class Person:
    def __init__(self, *args, **kwargs):
        self.term_id = kwargs["term_id"]
        self.name = kwargs["name"]
        self.slug = kwargs["slug"]
        self.term_group = kwargs["term_group"]
        self.term_taxonomy_id = kwargs["term_taxonomy_id"]
        self.taxonomy = kwargs["taxonomy"]
        self.description = kwargs["description"]
        self.parent = kwargs["parent"]
        self.count = kwargs["count"]
        self.filter = kwargs["filter"]
