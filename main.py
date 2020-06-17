import os
import re
import pandas as pd
import matplotlib.pyplot as plt

FILENAME = "_chat.txt"

# remove the <200e> character that appears when an image/video is used in a message
def cleanse_data():
    with open(os.getcwd() + "/" + FILENAME, "r+") as file:
        data = file.read()
        data = data.replace(u"\u200e", "")

        file.seek(0)
        file.write(data)
        file.truncate()


# checks if line is in the following format datetime format [XXXX-XX-XX, XX:XX:XX]
def starts_with_datetime(line):
    pattern = '^\[([0-9]+)-([0-9]+)-([0-9]+), ([0-9][0-9]):([0-9][0-9]):([0-9][0-9])\]'
    if re.match(pattern, line):
        return True
    return False


def get_datapoints(line):
    datetime_and_message = line.split("[", 1)[1].split("]", 1)

    date_and_time = datetime_and_message[0].split(",", 1)
    year, month, day = date_and_time[0].split("-")
    hour, minute, second = date_and_time[1].strip().split(":")

    user_and_message = datetime_and_message[1].strip()

    # TODO: Count when changes are made to the chat name
    try:
        user_and_message = user_and_message.split(":", 1)
        user = user_and_message[0]
        message = user_and_message[1].strip()
        return [year, month, day, hour, minute, second, user], message
    except:
        return None, None


# Skip the first three lines since they are header information
def skip_header(f):
    f.readline()
    f.readline()
    f.readline()


def parse_data(df):
    with open(os.getcwd() + "/" + FILENAME, "r") as file:
        skip_header(file)

        buffer = []
        datapoints = []

        while True:
            line = file.readline() 
            if not line: # Stop reading further if end of file has been reached
                break
            line = line.strip()
            if starts_with_datetime(line):
                if len(buffer) > 0:
                    datapoints.append(' '.join(buffer))
                    df.loc[len(df)] = datapoints
                buffer.clear()
                datapoints, message = get_datapoints(line)
                if datapoints is None:
                    continue
                buffer.append(message)
            else:
                buffer.append(line)
                

cleanse_data()
df = pd.DataFrame(columns=['year', 'month', 'day', 'hour', 'minute', 'second', 'user', 'message'])
parse_data(df)

df.to_pickle(os.getcwd() + "/dummy.pkl")
df = pd.read_pickle(os.getcwd() + "/dummy.pkl")

author_value_counts = df['user'].value_counts() # Number of messages per author
top_10_author_value_counts = author_value_counts.head(10) # Number of messages per author for the top 10 most active authors
top_10_author_value_counts.plot.barh() # Plot a bar chart using pandas built-in plotting

plt.show()
