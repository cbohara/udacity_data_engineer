CREATE EXTERNAL TABLE public.immigration_fact_table (
id int,
year int,
month int,
state string,
age int,
gender string,
arrival_date date,
departure_date date,
visa_category string,
country string,
continent string)
PARTITIONED BY ( 
year int,
month int)
LOCATION 's3://udacity-cbohara/immigration';
