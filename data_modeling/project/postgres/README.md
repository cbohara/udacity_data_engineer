### Purpose
Sparkify is a music streaming app that wants to better understand what songs their users are listening too.  Currently, they don't have an easy way to query their data, which resides in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

The purpose of this project is to create a database with tables designed to optimize queries for song play analysis.

### Architecture

#### Database
The Postgres database contains tables following the star schema.  

The songplays fact table contains records from log data associated with song plays:

songplay_id, start_time, user_id, song_id, artist_id, session_id, location, user_agent

Any additional information regarding a user, song, artist, or time is needed it can be found in its appropriate dimension table.

users dimension table - users in the app:

user_id, first_name, last_name, gender, level (free or subscriber)

songs dimension table - songs in music database:

song_id, title, artist_id, year, duration

artists dimension table - artists in music database:

artist_id, name, location, latitude, longitude

time dimension table - timestamps of records in songplays broken down into specific units:

start_time, hour, day, week, month, year, weekday

#### ETL
The music streaming logs and song library exist within appropriate subdirectories on the local machine.  These json files were read in leveraging the pandas library.  

For each file and each json object, the fields were parsed and values were transformed based on schema requirements andwere transformed based on schema requirements and inserted into the appropriate table.


### Example queries

Count the number of songs a user listens to on the weekday vs on the weekend

```select u.user_id, sum(t.weekday) as "weekday", \
sum(case when t.weekday = 0 then 1 else 0 end) as "weekend" \
from songplays s \
join users u on (u.user_id = s.user_id) \
join time t on (t.start_time = s.start_time) \
group by u.user_id;
```

