import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import random
from pathlib import Path

#load club lookup
with open("data/club_lookup_tm.json", "r", encoding="utf-8") as f:
    club_lookup = json.load(f)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.6367.208 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def normalize_value(val): #convert market value strings to float
    if not isinstance(val, str) or val.strip() == "-":
        return None
    val = val.replace("€", "").replace("m", "e6").replace("k", "e3").replace(",", "").strip()
    try:
        return float(val)
    except ValueError:
        return None

def get_season_ids(slug, club_id): #get all available seasons for a club by slug and id
    url = f"https://www.transfermarkt.com/{slug}/startseite/verein/{club_id}"
    res = requests.get(url, headers=HEADERS)
    time.sleep(random.uniform(8, 12))
    soup = BeautifulSoup(res.text, "html.parser")
    options = soup.select("select[name='saison_id'] option") #dropdown with season options
    return sorted({opt["value"] for opt in options if opt.get("value").isdigit()}, reverse=True) #get season ids and remove duplicates

def scrape_squad(club, slug, club_id, season_id):
    url = f"https://www.transfermarkt.com/{slug}/kader/verein/{club_id}/saison_id/{season_id}"

    for attempt in range(3):
        res = requests.get(url, headers=HEADERS)
        time.sleep(random.uniform(8, 12))
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", {"class": "items"})
        if not table:
            continue

        players = []
        for row in table.select("tbody > tr"):
            if "odd" in row.get("class", []) or "even" in row.get("class", []): #only process rows with players
                try:
                    name_tag = row.find("td", {"class": "hauptlink"}).find("a") #get <a> tag with player name
                    name = name_tag.text.strip()
                    profile_url = "https://www.transfermarkt.com" + name_tag["href"] #create profile url
                    cols = row.find_all("td") #get all cells in the row
                    position = cols[4].text.strip()
                    age = cols[5].text.strip()
                    nationality = cols[6].img["title"] if cols[6].find("img") else "Unknown" #country flag title
                    market_value = cols[-1].text.strip()

                    players.append({
                        "Name": name,
                        "Profile URL": profile_url,
                        "Position": position,
                        "Age": age,
                        "Nationality": nationality,
                        "Market Value": market_value,
                        "Market Value (€)": normalize_value(market_value),
                        "Club": club.title(),
                        "Slug": slug,
                        "Season": int(season_id)
                    })
                except:
                    continue #skip any row that fails to parse
        if players:
            return players
    return []

def main():
    output_csv = Path("data/player_data_prem.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True) #ensure output directory exists
    all_rows = []

    for club, meta in club_lookup.items():
        slug, club_id = meta["slug"], meta["id"] #extract slug and id from lookup for url
        print(f"{club.title()} (ID: {club_id})")
        try:
            seasons = get_season_ids(slug, club_id) #get season ids for the club
        except Exception as e:
            print(f"Failed to get seasons: {e}")
            continue

        for season in seasons: #loop through each season
            if not (1989 <= int(season) <= 2024): #only scrape desired seasons
                continue
            print(f"   Scraping {season}...", end="")
            try:
                rows = scrape_squad(club, slug, club_id, season) #scrape squad for the season
                if not rows:
                    print("no players found.")
                else:
                    all_rows.extend(rows) #add data to the main list
                    print(f"{len(rows)} players")
            except Exception as e:
                print(f"Error: {e}")
        
        time.sleep(random.uniform(30, 60))

    df = pd.DataFrame(all_rows) #convert to df
    df.to_csv(output_csv, index=False) #save to csv
    print(f"Done. {len(df)} rows saved to {output_csv}")

if __name__ == "__main__":
    main()