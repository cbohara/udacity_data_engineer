CREATE EXTERNAL TABLE public.us_demographic_dimension_table (
city string,
state string,
median_age double,
male_population int,
female_population int,
total_population int,
number_of_veterans int,
foreign_born int,
average_household_size double,
state_code string,
race string,
count int
race_percent double
)
PARTITIONED BY ( 
state_code string)
LOCATION 's3://udacity-cbohara/demo';
