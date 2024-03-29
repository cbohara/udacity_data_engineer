# DROP TABLES

songplay_table_drop = "drop table if exists songplays"
user_table_drop = "drop table if exists users"
song_table_drop = "drop table if exists songs"
artist_table_drop = "drop table if exists artists"
time_table_drop = "drop table if exists time"

# CREATE TABLES

# songplay fact table
# records in log data associated with song plays i.e. records with page NextSong
songplay_table_create = ("""
create table if not exists songplays (
songplay_id serial primary key,
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
user_id integer primary key,
first_name varchar,
last_name varchar,
gender varchar,
level varchar not null
)""")

# song dimension table
# songs in the music DB
song_table_create = ("""
create table if not exists songs (
song_id varchar primary key,
title varchar not null,
artist_id varchar not null,
year integer,
duration numeric
)""")

# artist dimension table
# artists in the music DB
artist_table_create = ("""
create table if not exists artists (
artist_id varchar primary key,
name varchar not null,
location varchar,
latitude numeric,
longitude numeric
)""")

# time dimension table
# timestamps of records in songplays broken down into specific units
time_table_create = ("""
create table if not exists time (
start_time timestamp primary key,
hour integer not null,
day integer not null,
week integer not null,
month integer not null,
year integer not null,
weekday integer not null
)""")

# INSERT RECORDS

songplay_table_insert = ("""
insert into songplays (
start_time,
user_id,
song_id,
artist_id,
session_id,
location,
user_agent
) values (%s, %s, %s, %s, %s, %s, %s)
""")

user_table_insert = ("""
insert into users (
user_id,
first_name,
last_name,
gender,
level
) values (%s, %s, %s, %s, %s)
on conflict (level) do update set level = excluded.level
""")

song_table_insert = ("""
insert into songs (
song_id,
title,
artist_id,
year,
duration)
values (%s, %s, %s, %s, %s)
on conflict (song_id) do nothing
""")

artist_table_insert = ("""
insert into artists (
artist_id,
name,
location,
latitude,
longitude
) values (%s, %s, %s, %s, %s)
on conflict (artist_id) do nothing
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
) values (%s, %s, %s, %s, %s, %s, %s)
on conflict (start_time) do nothing
""")

# FIND SONGS
# query song and artist tables
# input title, artist name, and duration of a song
# input = (row.song, row.artist, row.length)
# return (songid, artistid)
song_select = ("""
select s.song_id, a.artist_id
from songs s join artists a on s.artist_id = a.artist_id
where s.title = %s
and a.name = %s
and s.duration = %s""")

# QUERY LISTS

create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
