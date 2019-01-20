from AutoRepr import AutoRepr
from Score import Score, InvalidScore


class Match(AutoRepr):
    def __init__(self, element):
        rows = element.find_all("tr")
        self.scores = []
        team = 0
        for row in rows:
            if any(row.select(".csgo_scoreboard_score")):
                team = 1
                continue
            try:
                self.scores.append(Score(row, team))
            except InvalidScore:
                pass
        if len(self.get_scores_for_team(0)) != 5:
            raise ValueError(f"Coult not find 5 scores for team 0 for match {element}")
        if len(self.get_scores_for_team(1)) != 5:
            raise ValueError(f"Coult not find 5 scores for team 1 for match {element}")

    def get_score(self, player):
        for score in self.scores:
            if score.player_name == player:
                return score
        return None

    def get_scores_for_team(self, team):
        return list(list(filter(lambda score: score.team == team, self.scores)))

    def is_top_fragger(self, player):
        team_scores = self.get_scores_for_team(self.get_score(player).team)
        return max(team_scores, key=lambda score: score.score).player_name == player

    def is_bottom_fragger(self, player):
        team_scores = self.get_scores_for_team(self.get_score(player).team)
        return min(team_scores, key=lambda score: score.score).player_name == player
