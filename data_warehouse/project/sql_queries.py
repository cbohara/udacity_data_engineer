import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "drop table if exists staging_events"
staging_songs_table_drop = "drop table if exists staging_songs"
songplay_table_drop = "drop table if exists songplays"
user_table_drop = "drop table if exists users"
song_table_drop = "drop table if exists songs"
artist_table_drop = "drop table if exists artists"
time_table_drop = "drop table if exists time"


# CREATE TABLES

# stage events data 
staging_events_table_create= ("""
create table if not exists staging_events (
artist varchar,
auth varchar,
firstName varchar,
gender varchar,
itemInSession integer,
lastName varchar,
length real,
level varchar,
location varchar,
method varchar,
page varchar,
registration real,
sessionId integer,
song varchar,
status integer,
ts bigint,
userAgent varchar,
userId integer
)""")

# stage song data
staging_songs_table_create = ("""
create table if not exists staging_songs (
artist_id varchar,
artist_latitude float,
artist_location varchar,
artist_longitude float,
artist_name varchar,
duration float,
num_songs integer,
song_id varchar,
title varchar,
year integer
)""")

# songplay fact table
# records in log data associated with song plays i.e. records with page NextSong
songplay_table_create = ("""
create table if not exists songplays (
songplay_id integer primary key identity(1, 1) not null sortkey,
start_time timestamp not null,
user_id integer not null,
song_id varchar,
artist_id varchar,
session_id integer not null,
location varchar,
user_agent varchar
)""")

# user dimension table
# users in the app 
user_table_create = ("""
create table if not exists users (
user_id integer primary key not null sortkey,
first_name varchar,
last_name varchar,
gender varchar,
level varchar not null
) diststyle all""")

# song dimension table
# songs in the music DB
song_table_create = ("""
create table if not exists songs (
song_id varchar primary key not null sortkey,
title varchar not null,
artist_id varchar not null,
year integer,
duration real
) diststyle all""")

# artist dimension table
# artists in the music DB
artist_table_create = ("""
create table if not exists artists (
artist_id varchar primary key not null sortkey,
name varchar not null,
location varchar,
latitude real,
longitude real
) diststyle all""")

# time dimension table
# timestamps of records in songplays broken down into specific units
time_table_create = ("""
create table if not exists time (
start_time timestamp primary key not null sortkey,
hour integer not null,
day integer not null,
week integer not null,
month integer not null,
year integer not null,
weekday integer not null
) diststyle all""")

# STAGING TABLES

staging_events_copy = ("""
copy staging_events
from {}
iam_role {}
json {}
region {}
""").format(config.get('S3','LOG_DATA'), config.get('IAM_ROLE','ARN'), config.get('S3','LOG_JSONPATH'), config.get('CLUSTER', 'REGION'))

staging_songs_copy = ("""
copy staging_songs
from {}
iam_role {}
json 'auto'
region {}
""").format(config.get('S3','SONG_DATA'), config.get('IAM_ROLE','ARN'), config.get('CLUSTER', 'REGION'))

# FINAL TABLES

songplay_table_insert = ("""
insert into songplays (
start_time,
user_id,
song_id,
artist_id,
session_id,
location,
user_agent
)
select start_time,
user_id,
song_id,
artist_id,
session_id,
location, 
user_agent
from
(select timestamp 'epoch' + ts * (interval '1 second'/1000) as start_time,
userId as user_id,
song,
artist,
sessionId as session_id,
location,
userAgent as user_agent
from staging_events
where userId is not null
and page = 'NextSong') as se
left join 
(select song_id, title from songs) as s
on se.song = s.title
left join
(select artist_id, name from artists) as a
on se.artist = a.name
""")

user_table_insert = ("""
insert into users (
user_id,
first_name,
last_name,
gender,
level)
select 
userId,
firstName,
lastName,
gender,
level
from (
select se.userId, se.firstName, se.lastName, se.gender, se.level
from 
(
(select userId, firstName, lastName, gender, level, ts
from staging_events
where page = 'NextSong') as se
join
(select userId, max(ts) as max_ts from staging_events group by userId) as t
on se.userId = t.userId and se.ts = t.max_ts
)
order by 1)
""")

song_table_insert = ("""
insert into songs (
song_id,
title,
artist_id,
year,
duration)
select 
distinct song_id,
title,
artist_id,
year,
duration
from staging_songs
""")
 
artist_table_insert = ("""
insert into artists (
artist_id,
name,
location,
latitude,
longitude
)
select 
distinct artist_id,
artist_name,
artist_location,
artist_latitude,
artist_longitude
from staging_songs
""")

time_table_insert = ("""
insert into time (
start_time,
hour,
day,
week,
month,
year,
weekday
)
select
t.start_time as start_time,
extract(HOUR from t.start_time) as hour,
extract(DAY from t.start_time) as day,
extract(WEEK from t.start_time) as week,
extract(MONTH from t.start_time) as month,
extract(YEAR from t.start_time) as year,
extract(DW from t.start_time) as weekday
from 
(select distinct start_time
from songplays
order by 1) as t
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [user_table_insert, song_table_insert, artist_table_insert, songplay_table_insert, time_table_insert]
