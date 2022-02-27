from os.path import exists
from data_transfer.database import Database
from utils import read_csv_file

if __name__ == "__main__":
    DATABASE = Database()

    # Check if the picklist csv exists
    if not exists("data/picklist_upload.csv"):
        print("Picklist upload file not found.")
        exit(1)
    # Load the csv file from picklist
    csvdata = read_csv_file("data/picklist_upload.csv")
    teams = []

    for row in csvdata:
        # Check if the team number and the positions are numbers
        if row[0].isnumeric() and row[1].isnumeric() and row[2].isnumeric():
            # Add the team to the list of teams
            teams.append(
                {"team_number": int(row[0]), "first_rank": int(row[1]), "second_rank": int(row[2])}
            )

    for e in teams:
        # Add each pick list object to the database
        DATABASE.update_document("picklist", e, {"team_number": e["team_number"]})
        # print(e)
