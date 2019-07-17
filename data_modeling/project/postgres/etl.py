import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """
    This procedure processes a song file whose filepath has been provided as an argument.
    It extracts the song information in order to store it into the songs table.
    Then it extracts the artist information in order to store it into the artists table.
    :param cur: the cursor variable used to interact with the database
    :param filepath: the song filepath
    """
	# open song file
	df = pd.read_json(filepath, lines=True)

	# insert song record
	song_data = [df.values[0][7], df.values[0][8], df.values[0][0], df.values[0][9], df.values[0][5]]
	cur.execute(song_table_insert, song_data)
	
	# insert artist record
	artist_data = [df.values[0][0], df.values[0][4], df.values[0][2], df.values[0][1], df.values[0][3]]
	cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    This procedure processes a log file whose filepath has been provided as an argument.
    It filters out records for songs that are being played.  If an artist ID and song ID
    are available in the tables it will include the appropriate IDs when updating the songsplay table.
    Additionally the log files contain user data which will be inserted into the users table if the user
    does not exist yet or has changed their subscription level.
    :param cur: the cursor variable used to interact with the database
    :param filepath: the log filepath
    """
	# open log file
	df = pd.read_json(filepath, lines=True)

	# filter by NextSong action
	df = df.loc[df['page'] == 'NextSong']
	
	# convert timestamp column to datetime
	df['ts'] = pd.to_datetime(df['ts'], unit='ms')
	
	# insert time data records
	t = pd.to_datetime(df['ts'], unit='ms')
	time_data = [t, t.dt.hour, t.dt.day, t.dt.week, t.dt.month, t.dt.year, t.dt.weekday]
	column_labels = ['timestamp', 'hour', 'day', 'week', 'month', 'year', 'weekday']
	time_df = pd.DataFrame(dict(zip(column_labels, time_data)))

	for i, row in time_df.iterrows():
		cur.execute(time_table_insert, list(row))

	# load user table
	user_df = [df.values[0][17], df.values[0][2], df.values[0][5], df.values[0][3], df.values[0][7]]
	cur.execute(user_table_insert, user_df)

	# insert songplay records
	for index, row in df.iterrows():
		
		# get songid and artistid from song and artist tables
		cur.execute(song_select, (row.song, row.artist, row.length))
		results = cur.fetchone()
		
		if results:
			songid, artistid = results
		else:
			songid, artistid = None, None

		# insert songplay record
		songplay_data = [row.ts, row.userId, songid, artistid, row.sessionId, row.location, row.userAgent]
		cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
	"""
	This function is responsible for processing the data.  All the appropriate files are gathered.  For each file the
	appropriate procedure will be executed in order to update the appropriate tables in the database.
    :param cur: the cursor variable used to interact with the database
	:param conn: the active database connection variable
	:param filepath: the filepath for the directory containing files to process
	:param func: the function to use when processes the input file
	"""
	# get all files matching extension from directory
	all_files = []
	for root, dirs, files in os.walk(filepath):
		files = glob.glob(os.path.join(root,'*.json'))
		for f in files :
			all_files.append(os.path.abspath(f))

	# get total number of files found
	num_files = len(all_files)
	print('{} files found in {}'.format(num_files, filepath))

	# iterate over files and process
	for i, datafile in enumerate(all_files, 1):
		func(cur, datafile)
		conn.commit()
		print('{}/{} files processed.'.format(i, num_files))


def main():
	conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
	cur = conn.cursor()

	process_data(cur, conn, filepath='data/song_data', func=process_song_file)
	process_data(cur, conn, filepath='data/log_data', func=process_log_file)

	conn.close()


if __name__ == "__main__":
	main()
