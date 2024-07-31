class content:
    def __init__(self, text, link_to_text, sport_type, last_changed) -> None:
        self.text = text
        self.link_to_text = link_to_text
        self.sport_type = sport_type
        self.last_changed = last_changed


class query:
    BASE_URL = "127.0.0.1"

    def __init__(self, sports_categories, sort_value, content) -> None:
        self.sports_categories = sports_categories
        self.sort_value = sort_value
        self.content = content
        pass


class sport_categorie:
    def __init__(self, name) -> None:
        self.name = name
        pass
