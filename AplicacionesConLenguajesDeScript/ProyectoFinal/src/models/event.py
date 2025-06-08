class Event:
    def __init__(self, name, description="", season=1, episode=1, location="", 
                 importance=1, image_url="", related_characters=None, related_houses=None):
        self._oid = None
        self.name = name
        self.description = description
        self.season = season
        self.episode = episode
        self.location = location
        self.importance = importance  # 1-5 scale
        self.image_url = image_url
        self.related_characters = related_characters or []
        self.related_houses = related_houses or []
        self.comments = []

    def get_id(self):
        return self._oid

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_related_character(self, character_id):
        if character_id not in self.related_characters:
            self.related_characters.append(character_id)

    def add_related_house(self, house_id):
        if house_id not in self.related_houses:
            self.related_houses.append(house_id)

    def __str__(self):
        return f"Event: {self.name} (S{self.season}E{self.episode})"

    def __repr__(self):
        return f"Event(name='{self.name}', season={self.season}, episode={self.episode})"