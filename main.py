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
    date = date_and_time[0]
    year, month, day = date_and_time[0].split("-")
    time = date_and_time[1].strip()
    time_and_period = date_and_time[1].strip().split(" ")
    hour, minute, second = time_and_period[0].split(":")
    period = time_and_period[1].strip()
    if (period == "PM"):
        hour = pm_conversions[hour]
    else:
        hour = am_conversions[hour]

    user_and_message = datetime_and_message[1].strip()

    # TODO: Count when changes are made to the chat name
    if ("changed the subject" in user_and_message) or ("changed this group's icon" in user_and_message):
        return None, None

    try:
        user_and_message = user_and_message.split(":", 1)
        user = user_and_message[0]
        message = user_and_message[1].strip()
        return [date, year, month, day, time, hour, minute, second, period, user], message
    except:
        return None, None


# Skip the first three lines since they are header information
def skip_header(f):
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
                    try:
                        datapoints.append(' '.join(buffer))
                        df.loc[len(df)] = datapoints
                    except:
                        print(line)
                        print(datapoints)
                        print(buffer)
                        raise Exception
                buffer.clear()
                datapoints, message = get_datapoints(line)
                if datapoints is None:
                    continue
                buffer.append(message)
            else:
                buffer.append(line)
                

cleanse_data()
df = pd.DataFrame(columns=['date', 'year', 'month', 'day', 'time', 'hour', 'minute', 'second', 'period', 'user', 'message'])
parse_data(df)
df.to_pickle(os.getcwd() + "/dummy.pkl")

# df['letter_Count'] = df['message'].apply(lambda s : len(s))
# df['word_Count'] = df['message'].apply(lambda s : len(s.split(' ')))
# df['month'] = df['month'].apply(lambda s : months(s))

# df = pd.read_pickle(os.getcwd() + "/dummy.pkl")

print(df.head())

plt.title("Messages sent per hour")
counts = df['hour'].value_counts()
counts.sort_index(ascending=True, inplace=True)
plt.grid(True)
counts.plot.bar()
plt.xlabel('Hour (EST)')
plt.ylabel('# of Messages')
plt.xticks(rotation=0)

# plt.title("Messages sent per year")
# counts = df['year'].value_counts()
# counts.sort_index(inplace=True)
# plt.grid(True)
# counts.plot.bar()
# plt.xlabel('Year')
# plt.ylabel('# of Messages')
# plt.xticks(rotation=0)

# plt.title("Messages sent per month")
# counts = df['month'].value_counts()
# counts.sort_index(inplace=True)
# plt.grid(True)
# counts.plot.bar()
# plt.xlabel('Month')
# plt.ylabel('# of Messages')
# plt.xticks(rotation=0)

# plt.title("Messages sent per day of the month")
# counts = df['day'].value_counts()
# counts.sort_index(inplace=True)
# plt.grid(True)
# counts.plot.bar()
# plt.xlabel('Day')
# plt.ylabel('# of Messages')
# plt.xticks(rotation=0)

# plt.title("Messages sent per date")
# counts = df['date'].value_counts().head(20)
# # counts.sort_index(inplace=True)
# plt.grid(True)
# counts.plot.bar()
# plt.xlabel('Date')
# plt.ylabel('# of Messages')
# plt.xticks(rotation='vertical')

# plt.title("Messages sent by time")
# counts = df['time'].value_counts().head(25)
# counts.sort_index(inplace=True)
# plt.grid(True)
# counts.plot.bar()
# plt.xlabel('Time')
# plt.ylabel('# of Messages')
# plt.xticks(rotation='vertical')

# plt.title("Messages sent by time period")
# counts = df['period'].value_counts()
# counts.sort_index(inplace=True)
# plt.grid(True)
# counts.plot.pie()

# plt.title("Messages sent by user")
# counts = df['user'].value_counts()
# plt.grid(True)
# counts.plot.barh()
# plt.ylabel('User')
# plt.xlabel('# of Messages')

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

plt.show()
