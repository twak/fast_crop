import os



if __name__ == "__main__":

    with open("./tomove.txt", "w") as togo:

        for batch in os.listdir("data/photos"):
            for file in os.listdir(f"data/photos/{batch}"):
                if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg"):
                    print(f"data/photos/{batch}/{file}")

