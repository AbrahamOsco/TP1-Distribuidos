import csv

def read_csv():
    with open("./data/games/games.csv", newline='') as file_game:
        reader = csv.reader(file_game)
        for i in range(0,3):
            row = next(reader)
            print(f"[Game| Row: {i}]: {row}")
    with open("./data/reviews/dataset.csv", newline='') as file_reviews:
        reader = csv.reader(file_reviews)
        for i in range(0,3):
            row = next(reader)
            print(f"[Review| Row: {i}]: {row}")

def main():
    read_csv()

main()