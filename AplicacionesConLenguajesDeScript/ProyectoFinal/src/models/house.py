class House:
    def __init__(self, name, words="", region="", lord="", description="", image_url=""):
        self._oid = None
        self.name = name
        self.words = words
        self.region = region
        self.lord = lord
        self.description = description
        self.image_url = image_url
        self.comments = []

    def get_id(self):
        return self._oid

    def add_comment(self, comment):
        self.comments.append(comment)

    def __str__(self):
        return f"House: {self.name} of {self.region}"

    def __repr__(self):
        return f"House(name='{self.name}', region='{self.region}', lord='{self.lord}')"