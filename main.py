import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from dicts import months, am_conversions, pm_conversions

FILENAME = "_chat.txt"

# remove the <200e> character that appears when an image/video is used in a message
def cleanse_data():
    with open(os.getcwd() + "/" + FILENAME, "r+") as file:
        data = file.read()
        data = data.replace(u"\u200e", "").replace(u"\u200e", "") .replace(u"\u200e", "")

        file.seek(0)
        file.write(data)
        file.truncate()


# checks if line is in the following format datetime format [XXXX-XX-XX, XX:XX:XX]
def starts_with_datetime(line):
    pattern = '^\[([0-9]+)-([0-9]+)-([0-9]+), ([0-9]+):([0-9]+):([0-9]+) (AM|PM)\]'
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
                if len(buffer) > 0:
                    datapoints.append(' '.join(buffer))
                    df.loc[len(df)] = datapoints
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
df['letter_Count'] = df['message'].apply(lambda s : len(s))
df['word_Count'] = df['message'].apply(lambda s : len(s.split(' ')))
df.to_pickle(os.getcwd() + "/dummy.pkl")

# df = pd.read_pickle(os.getcwd() + "/dummy.pkl")

print(df.head())

# plt.title("Messages sent per hour")
# counts = df['hour'].value_counts()
# counts.sort_index(inplace=True)
# plt.grid(True)
# counts.plot.bar()
# plt.xlabel('Hour (PST)')
# plt.ylabel('# of Messages')
# plt.xticks(rotation=0)

# plt.title("Messages sent per year")
# counts = df['year'].value_counts()
# counts.sort_index(inplace=True)
# plt.grid(True)
# counts.plot.bar()
# plt.xlabel('Year')
# plt.ylabel('# of Messages')
# plt.xticks(rotation=0)

# plt.title("Messages sent by user")
# counts = df['user'].value_counts()
# counts.sort_index(inplace=True)
# plt.grid(True)
# counts.plot.barh()
# plt.ylabel('User')
# plt.xlabel('# of Messages')
# plt.xticks(rotation=0)

# plt.title("Images sent by user")
# image_df = df[df['message'] == 'image omitted']
# user_image_counts = image_df['user'].value_counts()
# user_image_counts.plot.barh()
# plt.grid(True)
# plt.ylabel('User')
# plt.xlabel('# of Messages')

# plt.title("Videos sent by user")
# video_df = df[df['message'] == 'video omitted']
# user_video_counts = video_df['user'].value_counts()
# user_video_counts.plot.barh()
# plt.title("Videos sent by user")
# plt.grid(True)
# plt.ylabel('User')
# plt.xlabel('# of Messages')

# plt.title("Deleted messages per user")
# deleted_msg_others_df = df[df['message'] == ('This message was deleted.')]
# deleted_msg_you_df = df[df['message'] == ('You deleted this message.')]
# result = pd.concat([deleted_msg_others_df, deleted_msg_you_df])
# counts = result['user'].value_counts()
# counts.plot.barh()
# plt.grid(True)
# plt.ylabel('User')
# plt.xlabel('# of Messages')

# plt.title("Who @'s others the most?")
# result = df[df['message'].str.contains("@[0-9A-Za-z]+", regex=True)]
# counts = result['user'].value_counts()
# counts.plot.barh()
# plt.grid(True)
# plt.ylabel('User')
# plt.xlabel('# of Messages')

# plt.title("Who gets @'d the most?")
# result = df[df['message'].str.contains("@[0-9A-Za-z]+", regex=True)]
# counts = result['user'].value_counts()
# counts.plot.barh()
# plt.grid(True)
# plt.ylabel('User')
# plt.xlabel('# of Messages')

# plt.show()
