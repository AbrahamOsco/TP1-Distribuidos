import csv
import pandas as pd

def read_csv():
    with open("./data/games/games.csv", newline='') as file_game:
        reader = csv.reader(file_game)
        for i in range(0,1):
            row = next(reader)
            print(f"[Game| Row: {i}]: {row}")
    with open("./data/reviews/dataset.csv", newline='') as file_reviews:
        reader = csv.reader(file_reviews)
        for i in range(0,1):
            row = next(reader)
            print(f"[Review| Row: {i}]: {row}")

def read_csv_pandas():
    games_df_columns = ['AppID', 'Name', 'Windows', 'Mac', 'Linux', 'Genres', 'Release date', 'Average playtime forever', 'Positive', 'Negative']
    reviews_df_columns = ['app_id', 'review_text']
    
    games_df = pd.read_csv("./data/games/games.csv", usecols=games_df_columns, nrows=3)
    reviews_df = pd.read_csv("./data/reviews/dataset.csv", usecols=reviews_df_columns, nrows=3)
    games_df["Genres"] = games_df["Genres"].str.lower() 

    games_df.info()
    reviews_df.info()
    get_number_of_games_on_win_linux_mac(games_df)

def get_number_of_games_on_win_linux_mac(game_df):
    windows_supported_games = game_df[game_df["Windows"] == True]


def main():
    read_csv_pandas()



main()