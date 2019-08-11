import configparser
import datetime
import pandas as pd
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format
from pyspark.sql.types import StructType, StructField, DoubleType, IntegerType, StringType, LongType, DateType, TimestampType


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS']['AWS_ACCESS_KEY_ID'].strip()
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS']['AWS_SECRET_ACCESS_KEY'].strip()


def create_spark_session():
	spark = SparkSession \
		.builder \
		.config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
		.getOrCreate()
	return spark


def process_song_data(spark, input_data, output_data):
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

	songs_table = df.select("title", "artist_id", "year", "duration") 
	songs_table.write.partitionBy("year", "artist_id").parquet(output_data + "songs")
	
	artists_table = df.select("artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude")
	artists_table.write.parquet(output_data + "artists")


def process_log_data(spark, input_data, output_data):
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
  
	users_table = df.select("userId", "firstName", "lastName", "gender", "level")
	users_table.write.parquet(output_data + "users")

	get_datetime =	udf(lambda x: datetime.datetime.fromtimestamp(x / 1000.0), TimestampType())
	df = df.withColumn("datetime", get_datetime(df.ts))
	
	time_table = df.select("ts", "datetime")
	time_table = time_table.withColumn("hour", hour("datetime"))
	time_table = time_table.withColumn("day", dayofmonth("datetime"))
	time_table = time_table.withColumn("week", weekofyear("datetime"))
	time_table = time_table.withColumn("month", month("datetime"))
	time_table = time_table.withColumn("year", year("datetime"))
	time_table = time_table.withColumn("weekday", date_format("datetime", "u"))
	time_table = time_table.drop("datetime")
	time_table.write.partitionBy("year", "month").parquet(output_data + "time")

	# read in song data to use for songplays table
	#song_df = 

	# extract columns from joined song and log datasets to create songplays table 
	#songplays_table = 

	# write songplays table to parquet files partitioned by year and month
	#songplays_table


def main():
	spark = create_spark_session()
	input_data = "s3a://udacity-cbohara-input/"
	output_data = "s3a://udacity-cbohara-output/"

	process_song_data(spark, input_data, output_data)
	process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
	main()
