-- PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE director (
	id INTEGER NOT NULL, 
	last_name VARCHAR(60) NOT NULL, 
	first_name VARCHAR(60) NOT NULL, nation varchar(6), 
	PRIMARY KEY (id)
);
INSERT INTO "director" VALUES(2,'Ki Duck','Kim','KR');
INSERT INTO "director" VALUES(3,'Von Triars','Lars','DK');
INSERT INTO "director" VALUES(6,'Faenza','Roberto','IT');
INSERT INTO "director" VALUES(7,'Leconte','Patrice','FR');
INSERT INTO "director" VALUES(8,'Donnersmak','Florian','DE');
INSERT INTO "director" VALUES(11,'Kraus','Cris','DE');
INSERT INTO "director" VALUES(12,'Truffaut','Françoise','FR');
INSERT INTO "director" VALUES(13,'Olmi','Ermanno','IT');
INSERT INTO "director" VALUES(14,'Fellini','Federico','IT');

CREATE TABLE genre (
	name VARCHAR(15) NOT NULL, 
	PRIMARY KEY (name)
);
INSERT INTO "genre" VALUES('drammatico');
INSERT INTO "genre" VALUES('storico');
INSERT INTO "genre" VALUES('fiabesco');
INSERT INTO "genre" VALUES('b&w');

CREATE TABLE nation (
	cod VARCHAR(4) NOT NULL, 
	nation VARCHAR(20), 
	PRIMARY KEY (cod)
);
INSERT INTO "nation" VALUES('IT','Italy');
INSERT INTO "nation" VALUES('FR','France');
INSERT INTO "nation" VALUES('DE','Germany');
INSERT INTO "nation" VALUES('DK','Denmark');
INSERT INTO "nation" VALUES('US','USA');
INSERT INTO "nation" VALUES('MX','Mexico');
INSERT INTO "nation" VALUES('KR','Korea');

CREATE TABLE actor (
     id INTEGER NOT NULL, 
     first_name VARCHAR(30) NOT NULL, 
     last_name VARCHAR(30), 
     nation_cod VARCHAR(4) REFERENCES "nation" ("cod"),
     PRIMARY KEY (id)
);
INSERT INTO "actor" VALUES(1,'Marcello','Mastroianni','IT');
INSERT INTO "actor" VALUES(2,'Daniel','Autoil','FR');
INSERT INTO "actor" VALUES(3,'Vanessa','Paraise','FR');
INSERT INTO "actor" VALUES(4,'Giulietta','Masina','IT');
INSERT INTO "actor" VALUES(5,'Anthony','Quinn','US');
INSERT INTO "actor" VALUES(6,'Ulrich','Mühe','DE');
INSERT INTO "actor" VALUES(7,'Bud','Spencer','IT');

CREATE TABLE movie (
        id INTEGER NOT NULL, 
        title VARCHAR(60) NOT NULL, 
        description VARCHAR(512), 
        year INTEGER, 
        date_release DATE, 
        director_id INTEGER NOT NULL, 
        image VARCHAR(255), 
        score INTEGER,
PRIMARY KEY (id), 
 CONSTRAINT movie_director_id_fk FOREIGN KEY(director_id) REFERENCES director (id)
);
INSERT INTO "movie" VALUES(3,'Sostiene pereira','Great Mastroianni!',1995,NULL,6,'sostiene-pereira.jpg',3);
INSERT INTO "movie" VALUES(5,'La ragazza sul ponte.','Don''t miss this film',1999,'2008-04-07',7,'la-ragazza-sul-ponte.jpg',2);
INSERT INTO "movie" VALUES(7,'Le vite degli altri','Probably the best film this year',2006,'2007-04-06',8,'le-vite-degli-altri.jpg',3);
INSERT INTO "movie" VALUES(8,'4 minuti',NULL,2006,'2007-05-04',11,NULL,1);
INSERT INTO "movie" VALUES(9,'Cantando dietro il paraventi','Really charming atmosphere...',2002,'2003-10-24',13,'cantando.jpeg',2);
INSERT INTO "movie" VALUES(13,'Jim e Jules',NULL,1963,NULL,12,NULL,1);
INSERT INTO "movie" VALUES(21,'100 chiodi',NULL,2007,'2007-03-30',13,NULL,NULL);
INSERT INTO "movie" VALUES(22,'Dogville',NULL,NULL,'2003-11-07',3,NULL,NULL);
INSERT INTO "movie" VALUES(23,'Soffio',NULL,2007,NULL,2,NULL,NULL);
INSERT INTO "movie" VALUES(25,'Time',NULL,2006,NULL,2,NULL,NULL);
INSERT INTO "movie" VALUES(26,'La Samaritana',NULL,2004,NULL,2,NULL,NULL);
INSERT INTO "movie" VALUES(27,'Ferro 3','very few words indeed',2004,'2008-11-10',2,NULL,NULL);
INSERT INTO "movie" VALUES(28,'Il Capo',NULL,NULL,'2007-01-05',3,NULL,NULL);
INSERT INTO "movie" VALUES(29,'Le onde del destino',NULL,NULL,NULL,3,NULL,NULL);
INSERT INTO "movie" VALUES(30,'L''Arco',NULL,2005,NULL,2,NULL,NULL);
INSERT INTO "movie" VALUES(31,'La signora della porta accanto',NULL,1983,NULL,12,NULL,NULL);
INSERT INTO "movie" VALUES(36,'Il marito della parrucchiera',NULL,1990,NULL,7,NULL,NULL);
INSERT INTO "movie" VALUES(38,'Tango',NULL,1993,NULL,7,NULL,NULL);
INSERT INTO "movie" VALUES(39,'La strada','unforgettable!',1954,NULL,14,NULL,3);
INSERT INTO "movie" VALUES(40,'La leggenda del santo bevitore',NULL,1988,NULL,13,'leggenda.jpeg',NULL);
CREATE INDEX ix_movie_director_id ON movie (director_id);

CREATE TABLE movie_casting (
	movie_id INTEGER NOT NULL, 
	actor_id INTEGER NOT NULL, 
	PRIMARY KEY (movie_id, actor_id), 
	 CONSTRAINT movie_actors_fk FOREIGN KEY(movie_id) REFERENCES movie (id), 
	 CONSTRAINT actor_movies_fk FOREIGN KEY(actor_id) REFERENCES actor (id)
);
INSERT INTO "movie_casting" VALUES(3,1);
INSERT INTO "movie_casting" VALUES(5,2);
INSERT INTO "movie_casting" VALUES(5,3);
INSERT INTO "movie_casting" VALUES(39,4);
INSERT INTO "movie_casting" VALUES(39,5);
INSERT INTO "movie_casting" VALUES(7,6);
INSERT INTO "movie_casting" VALUES(9,7);
CREATE TABLE movie_genre (
	movie_id INTEGER NOT NULL, 
	genre_name VARCHAR(15) NOT NULL, 
	PRIMARY KEY (movie_id, genre_name), 
	 CONSTRAINT movie_genres_fk FOREIGN KEY(movie_id) REFERENCES movie (id), 
	 CONSTRAINT genre_movies_fk FOREIGN KEY(genre_name) REFERENCES genre (name)
);
INSERT INTO "movie_genre" VALUES(8,'drammatico');
INSERT INTO "movie_genre" VALUES(3,'storico');
INSERT INTO "movie_genre" VALUES(5,'drammatico');
INSERT INTO "movie_genre" VALUES(7,'drammatico');
INSERT INTO "movie_genre" VALUES(13,'drammatico');
INSERT INTO "movie_genre" VALUES(21,'drammatico');
INSERT INTO "movie_genre" VALUES(3,'drammatico');
INSERT INTO "movie_genre" VALUES(9,'drammatico');
INSERT INTO "movie_genre" VALUES(9,'fiabesco');
INSERT INTO "movie_genre" VALUES(8,'storico');
INSERT INTO "movie_genre" VALUES(7,'storico');
INSERT INTO "movie_genre" VALUES(28,'storico');
INSERT INTO "movie_genre" VALUES(22,'storico');
INSERT INTO "movie_genre" VALUES(13,'b&w');
CREATE TABLE _sqlkit_table (
	name VARCHAR(50) NOT NULL, 
	search_field VARCHAR(50), 
	format VARCHAR(150), 
	PRIMARY KEY (name)
);
INSERT INTO "_sqlkit_table" VALUES('actor','last_name','%(first_name)s %(last_name)s');
INSERT INTO "_sqlkit_table" VALUES('movie','title','%(title)s %(year)s');
INSERT INTO "_sqlkit_table" VALUES('nation','nation','%(nation)s');
CREATE TABLE _sqlkit_field (
	table_name VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description VARCHAR(100), 
	help_text VARCHAR(300), 
	regexp VARCHAR(100), 
	autostart INTEGER, 
	"default" VARCHAR(200), 
	PRIMARY KEY (table_name, name), 
	 FOREIGN KEY(table_name) REFERENCES _sqlkit_table (name)
);
CREATE TABLE all_types (
	id INTEGER NOT NULL, 
	varchar10 VARCHAR(10) NOT NULL, 
	varchar200 VARCHAR(200), 
	text TEXT, 
	uni VARCHAR(10), 
	uni_text TEXT   NOT NULL, 
	date DATE, 
	datetime TIMESTAMP, 
	datetime_tz TIMESTAMP, 
	interval TIMESTAMP, 
	time TIME, 
	time_tz TIME, 
	integer INTEGER, 
	float FLOAT, 
	numeric NUMERIC(8, 2), 
	bool BOOLEAN NOT NULL, 
	bool_null BOOLEAN, 
	PRIMARY KEY (id)
);
INSERT INTO "all_types" VALUES(1,'a ','little','test to see how different type
of data will be rendered by default','you','can chage these renderers and I''d 
be really happy if you hve better
ones...','2009-03-12','2008-06-02 15:30:00.000000','2009-03-15 00:00:00.000000','1970-01-02 00:00:00.000000','12:05:00.000000','12:30:00.000000',1,1.2,1.2,0,0);
INSERT INTO "all_types" VALUES(2,'well','I don''t create','Another record','you','couldn''t test how it is browsing these records.

NOTE: time and time tz  ae just the same, but sqlite doesn''t make a lot of difference as far as I know. test it on PostreSQL.','2009-03-13','2008-06-05 11:15:00.000000','2009-03-14 08:15:00.000000',NULL,NULL,NULL,123,4881.69,4881.69,0,1);
INSERT INTO "all_types" VALUES(3,'thid','is','The last record I write here',NULL,'stop','2009-03-13',NULL,NULL,NULL,NULL,NULL,111,12.34,12.34,0,1);
COMMIT;
