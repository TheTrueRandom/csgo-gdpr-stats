from AutoRepr import AutoRepr


class Score(AutoRepr):
    def __init__(self, element, team):
        data = element.find_all("td")
        if len(data) != 8:
            raise InvalidScore("")
        self.team = team
        self.player_name = data[0].text.strip()
        self.ping = int(data[1].text.strip())
        self.k = int(data[2].text.strip())
        self.a = int(data[3].text.strip())
        self.d = int(data[4].text.strip())
        self.mvp = 0 if not data[5].text.strip() else 1 if data[5].text.strip() == "★" else int(data[5].text.strip().replace("★", ""))
        self.hsp = int(data[6].text.strip().split("%")[0]) if "%" in data[6].text else 0
        self.score = int(data[7].text.strip())


class InvalidScore(Exception):
    pass
