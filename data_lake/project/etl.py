import configparser
import datetime
import pandas as pd
import os

from pyspark.sql import SparkSession
from pyspark.sql import Window
from pyspark.sql.functions import udf, col, max, row_number, monotonically_increasing_id
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format
from pyspark.sql.types import StructType, StructField, DoubleType, IntegerType, StringType, LongType, DateType, TimestampType


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS']['AWS_ACCESS_KEY_ID'].strip()
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS']['AWS_SECRET_ACCESS_KEY'].strip()


def create_spark_session():
	"""
	Create SparkSession object to connect to the Spark API
	:return: SparkSession object
	"""
	spark = SparkSession \
		.builder \
		.config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
		.getOrCreate()
	return spark


def process_song_data(spark, input_data, output_data):
	"""
	Read in song data from S3 to populate the songs and artists dimesion tables.
	Write to S3 parquet files representing the tables.
	:param spark: SparkSession object
	:param input_data: S3 path containing input song data to process
	:param output_data: S3 path to write parquet files
	:return: None
	"""
	# songs staging dataframe
	song_data = input_data + "song_data/*/*/*/*.json"
	song_schema = StructType([
		StructField("artist_id", StringType()),
		StructField("artist_latitude", DoubleType()),
		StructField("artist_location", StringType()),
		StructField("artist_longitude", DoubleType()),
		StructField("artist_name", StringType()),
		StructField("duration", DoubleType()),
		StructField("num_songs", IntegerType()),
		StructField("song_id", StringType()),
		StructField("title", StringType()),
		StructField("year", IntegerType()),
	])
	df = spark.read.json(song_data, schema=song_schema)

	# songs dimension table
	# song_id, title, artist_id, year, duration
	songs_table = df.distinct().select("song_id", "title", "artist_id", "year", "duration")
	songs_table.write.partitionBy("year", "artist_id").parquet(output_data + "songs")

	# artists dimension table
	# artist_id, name, location, lattitude, longitude
	artists_table = df.distinct(). \
					selectExpr("artist_id","artist_name AS name", \
								"artist_location AS location","artist_latitude AS latitude","artist_longitude AS longitude")
	artists_table.write.parquet(output_data + "artists")


def process_log_data(spark, input_data, output_data):
	"""
	Read in log data from S3 to populate the users and time dimesion tables and the songplays fact table.
	Write to S3 parquet files representing the tables.
	:param spark: SparkSession object
	:param input_data: S3 path containing input song data to process
	:param output_data: S3 path to write parquet files
	:return: None
	"""
	# logs staging dataframe
	log_data = input_data + "log_data/*/*/*.json"
	log_schema = StructType([
		StructField("artist", StringType()),
		StructField("auth", StringType()),
		StructField("firstName", StringType()),
		StructField("gender", StringType()),
		StructField("itemInSession", IntegerType()),
		StructField("lastName", StringType()),
		StructField("length", DoubleType()),
		StructField("level", StringType()),
		StructField("location", StringType()),
		StructField("method", StringType()),
		StructField("page", StringType()),
		StructField("registration", DoubleType()),
		StructField("sessionId", IntegerType()),
		StructField("song", StringType()),
		StructField("status", IntegerType()),
		StructField("ts", LongType()),
		StructField("userAgent", StringType()),
		StructField("userId", StringType()),
	])
	df = spark.read.json(log_data, schema=log_schema)
	df = df.where("page = 'NextSong'")

	# users dimension table
	# user_id, first_name, last_name, gender, level
	users_table = df.withColumn('max_ts', max('ts').over(Window.partitionBy('userId'))).where(col('ts') == col('max_ts')).drop('max_ts')
	users_table = users_table.selectExpr("userId as user_id", "firstName as first_name", "lastName as last_name", "gender", "level")
	#users_table.write.parquet(output_data + "users")

	# time dimension table
	# start_time, hour, day, week, month, year, weekday
	get_timestamp = udf(lambda x: round(x / 1000), LongType())
	df = df.withColumn("timestamp", get_timestamp(df.ts))
	get_datetime =	udf(lambda x: datetime.datetime.fromtimestamp(x / 1000.0), TimestampType())
	df = df.withColumn("datetime", get_datetime(df.ts))
	time_table = df.select("timestamp", "datetime").distinct()
	time_table = time_table.withColumn("hour", hour("datetime"))
	time_table = time_table.withColumn("day", dayofmonth("datetime"))
	time_table = time_table.withColumn("week", weekofyear("datetime"))
	time_table = time_table.withColumn("month", month("datetime"))
	time_table = time_table.withColumn("year", year("datetime"))
	time_table = time_table.withColumn("weekday", date_format("datetime", "u").cast(IntegerType()))
	time_table = time_table.drop("datetime")
	#time_table.write.partitionBy("year", "month").parquet(output_data + "time")

	# songplays fact table
	# songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
	songs_df = spark.read.parquet(output_data + "songs")
	artists_df = spark.read.parquet(output_data + "artists")
	songplays_df = df.join(songs_df, df.song == songs_df.title, how="left")
	songplays_df = songplays_df.drop("artist_id", "year", "location")
	songplays_df = songplays_df.join(artists_df, songplays_df.artist == artists_df.name, how="left")
	songplays_df = songplays_df.withColumn("songplay_id", monotonically_increasing_id())
	songplays_df = songplays_df.withColumn("year", year("datetime"))
	songplays_df = songplays_df.withColumn("month", month("datetime"))
	songplays_table = songplays_df.selectExpr("songplay_id","timestamp AS start_time", "userId AS user_id", "level", "song_id", \
												"artist_id", "sessionId AS session_id", "location", "userAgent AS user_agent", \
												 "year", "month")
	songplays_table.write.partitionBy("year", "month").parquet(output_data + "songplays")


def main():
	spark = create_spark_session()
	input_data = "s3a://udacity-cbohara-input/"
	output_data = "s3a://udacity-cbohara-output/"

	process_song_data(spark, input_data, output_data)
	process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
	main()
