import json
import re
from json import JSONDecodeError

import requests
from bs4 import BeautifulSoup

from Match import Match

config = json.loads(open("config.json", "r").read())
all_matches = []


def updateStat(stat, number):
    stat["sum"] += number
    stat["highest"] = number if number > stat["highest"] or stat["highest"] == -1 else stat["highest"]
    stat["lowest"] = number if number < stat["lowest"] or stat["lowest"] == -1 else stat["lowest"]


def analyze_player(player):
    all_player_matches = [match for match in all_matches if match.get_score(player)]
    if len(all_player_matches) <= 2:
        return
    player_matches_count = len(all_player_matches)
    print(f"{player} appeared in {player_matches_count}/{len(all_matches)} matches ({round(player_matches_count/len(all_matches) * 100)}%)")

    top_frag_count = 0
    bottom_frag_count = 0

    kill = {"sum": 0, "highest": -1, "lowest": -1}
    death = {"sum": 0, "highest": -1, "lowest": -1}
    assist = {"sum": 0, "highest": -1, "lowest": -1}
    mvp = {"sum": 0, "highest": -1, "lowest": -1}
    hsp = {"sum": 0, "highest": -1, "lowest": -1}
    score = {"sum": 0, "highest": -1, "lowest": -1}

    for match in all_player_matches:
        top_frag_count += 1 if match.is_top_fragger(player) else 0
        bottom_frag_count += 1 if match.is_bottom_fragger(player) else 0

        player_score = match.get_score(player)
        updateStat(kill, player_score.k)
        updateStat(death, player_score.d)
        updateStat(assist, player_score.a)
        updateStat(mvp, player_score.mvp)
        updateStat(hsp, player_score.hsp)
        updateStat(score, player_score.score)

    print(f"TopFragger: {top_frag_count} BottomFragger: {bottom_frag_count}")
    print(f"Averages: "
          f"K: {round(kill['sum']/player_matches_count,2)} "
          f"D: {round(death['sum']/player_matches_count,2)} "
          f"A: {round(assist['sum']/player_matches_count,2)} "
          f"Score {round(score['sum']/player_matches_count,2)} "
          f"MVP: {round(mvp['sum']/player_matches_count,2)} "
          f"HS% {round(hsp['sum']/player_matches_count,2)}")
    print(f"Best (individual): "
          f"K: {kill['highest']} "
          f"D: {death['lowest']} "
          f"A: {assist['highest']} "
          f"Score {score['highest']} "
          f"MVP: {mvp['highest']} "
          f"HS% {hsp['highest']}")
    print(f"Worst (individual): "
          f"K: {kill['lowest']} "
          f"D: {death['highest']} "
          f"A: {assist['lowest']} "
          f"Score {score['lowest']} "
          f"MVP: {mvp['lowest']} "
          f"HS% {hsp['lowest']}")
    print()


def analyze():
    players = set()
    for match in all_matches:
        player_score = match.get_score(config["player"])
        if player_score is None:
            raise ValueError(f"Cannot find score for player {config['player']}")
        for score in match.get_scores_for_team(player_score.team):
            players.add(score.player_name)

    for team_player in players:
        analyze_player(team_player)


def handleMatchData(html):
    soup = BeautifulSoup(html, "html.parser")
    matches_html = soup.select(".csgo_scoreboard_inner_right")
    matches = list(map(lambda html_match: Match(html_match), matches_html))
    all_matches.extend(matches)
    print(f"Analyzing {len(all_matches)} Matches:")
    print()
    analyze()
    print("---------------")


def fetch_continue_token():
    url = f"https://steamcommunity.com/profiles/{config['steamId']}/gcpd/730/?tab=matchhistorycompetitive"
    res_text = fetch_url(url)
    if not "g_sGcContinueToken" in res_text:
        raise ValueError("Cannot query games - maybe steamId or steamLoginSecure is wrong")

    soup = BeautifulSoup(res_text, "html.parser")

    if not config.get("player"):
        config["player"] = soup.select_one('.whiteLink').text.strip()

    print(f"Player: {config['player']}")

    try:
        return re.compile("'\s?;").split(re.compile("g_sGcContinueToken\s?=\s?'?").split(res_text)[1])[0]
    except:
        raise ValueError("Failed to get continue_token")


def main():
    continue_token = fetch_continue_token()
    while continue_token:
        # print(f"le token: {continue_token}")
        url = f"https://steamcommunity.com/profiles/{config['steamId']}/gcpd/730?ajax=1&tab=matchhistorycompetitive&continue_token={continue_token}"
        text_res = fetch_url(url)
        try:
            json_res = json.loads(text_res)
        except JSONDecodeError:
            raise ValueError("Cannot query games - maybe steamId or steamLoginSecure is wrong")
        success = json_res["success"]
        if success:
            handleMatchData(json_res["html"])
            continue_token = json_res["continue_token"]
        else:
            print(json_res)
            break


def fetch_url(url):
    headers = {"Cookie": f"steamLoginSecure={config['steamLoginSecure']}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"failed with statuscode {res.status_code}: {res.text}")
        raise ConnectionError()
    return res.text


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
