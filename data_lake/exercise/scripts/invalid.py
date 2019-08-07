def add_incorrect_record():
	global incorrect_records
	incorrect_records += 1

if __name__ == "__main__":
	from pyspark.context import SparkContext
	from pyspark.sql import SparkSession
	from pyspark.sql.functions import udf

	spark = SparkSession\
		.builder\
		.appName("LowerSongTitles")\
		.getOrCreate()
	sc = spark.sparkContext

	path = "/Users/cbohara/git/udacity/data_lake/exercise/data/invalid.json"
	logs = spark.read.json(path)

	incorrect_records = sc.accumulator(0)
	correct_ts = udf(lambda x: 1 if isinstance(x, long) else add_incorrect_record())

	df = logs.where(logs["_corrupt_record"].isNotNull()).withColumn("ts_digit", correct_ts(logs.ts))
	# will get nothing because haven't called an action
	print(incorrect_records.value)
	df.collect()
	# will get 2 records
	print(incorrect_records.value)

	# call action again	
	df.collect()
	# will get 4 records
	print(incorrect_records.value)

	spark.stop()
