class Character:
    def __init__(self, name, title="", description="", image_url="", season_debut=1, 
                 status="Alive", house_id=None, allies=None, enemies=None):
        self._oid = None
        self.name = name
        self.title = title
        self.description = description
        self.image_url = image_url
        self.season_debut = season_debut
        self.status = status
        self.house_id = house_id
        self.allies = allies or []
        self.enemies = enemies or []
        self.comments = []

    def get_id(self):
        return self._oid

    def add_comment(self, comment):
        self.comments.append(comment)

    def __str__(self):
        return f"Character: {self.name} ({self.title})"

    def __repr__(self):
        return f"Character(name='{self.name}', title='{self.title}', status='{self.status}')"