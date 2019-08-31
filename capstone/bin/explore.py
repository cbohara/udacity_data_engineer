from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.functions import udf
from pyspark.sql.types import *

spark = SparkSession\
	.builder\
	.appName("Explore immigration data")\
	.getOrCreate()
sc = spark.sparkContext

# id,cicid,i94yr,i94mon,i94cit,i94res,i94port,arrdate,i94mode,i94addr,depdate,i94bir,i94visa,count,dtadfile,visapost,occup,entdepa,entdepd,entdepu,matflag,biryear,dtaddto,gender,insnum,airline,admnum,fltno,visatype
# 2027561,4084316.0,2016.0,4.0,209.0,209.0,HHW,20566.0,1.0,HI,20573.0,61.0,2.0,1.0,20160422,,,G,O,,M,1955.0,07202016,F,,JL,56582674633.0,00782,WT
# i94yr, month should really be IntegerType 
#dtadfile,visapost,occup,entdepa,entdepd,entdepu,matflag,biryear,dtaddto,gender,insnum,airline,admnum,fltno,visatype
#20160422,,,G,O,,M,1955.0,07202016,F,,JL,56582674633.0,00782,WT


im_file = '/Users/cbohara/git/udacity/capstone/data/immigration_data_sample.csv'
im_schema = StructType([
	StructField("id", IntegerType()),
	StructField("cicid", DoubleType()),
	StructField("i94yr", DoubleType()),
	StructField("i94mon", DoubleType()),
	StructField("i94cit", DoubleType()),
])
im_df = spark.read.csv(im_file, schema=im_schema)
im.printSchema()
im.show(5)

#City;State;Median Age;Male Population;Female Population;Total Population;Number of Veterans;Foreign-born;Average Household Size;State Code;Race;Count
demo_file = '/Users/cbohara/git/udacity/capstone/data/us-cities-demographics.csv'
demo_schema = StructType([
	StructField("city", StringType()),
	StructField("state", StringType()),
	StructField("median_age", DoubleType()),
	StructField("male_population", IntegerType()),
	StructField("female_population", IntegerType()),
	StructField("total_population", IntegerType()),
	StructField("number_of_veterans", IntegerType()),
	StructField("foreign_born", IntegerType()),
	StructField("average_household_size", DoubleType()),
	StructField("state_code", StringType()),
	StructField("race", StringType()),
	StructField("count", IntegerType()),
])
# 2892 rows
demo_df = spark.read.csv(demo_file, schema=demo_schema)
demo_df.printSchema()
demo_df.show(5)

spark.stop()
