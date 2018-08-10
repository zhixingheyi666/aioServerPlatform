select * from bookmurl;
use fortest;
select * from userr_ever;
-- drop table userr_ever;
use excodout;
select * from users;

select * from fmate_code;
select * from fline_code;
select * from hash_code where hashid>89;
select * from user_urls_note order by id desc;
select last_insert_id() from user_urls_note;


select * from user_urls_note where id > 123 order by id ;
select count(distinct `order`) from user_urls_note;
select path, `data` , mate_order, mate_format from user_urls_note where `order` >113  order by id ;
select id,mate, mate_format, `data`,`order` from user_urls_note where path = '.webApiUrlPrefix'  order by id ;


SELECT auto_increment FROM information_schema.tables where table_schema="fortest" and table_name="user_urls_note";
SELECT auto_increment FROM information_schema.tables where table_schema='fortest' and table_name='user_urls_note';

select * from user_urls_note where `order` != 976341 order by mate_order;
select count(distinct mate_order) from user_urls_note where `order` = 377219; -- order by mate_order;
select * from user_urls_note where `order` = 377219 order by mate_order;
select * from user_urls_note where `order` != 377219 order by mate_format;
select path,`data` from user_urls_note where `order` = 377219 order by `data`;
select path, mate, `order` from user_urls_note ;
delete  from user_urls_note where id <374;
truncate table user_urls_note;
alter table user_urls_note change column mate_hash mate_hash binary(20) not null;

insert into `user_urls_note` (`mate_hash`,`path`,`format`,`data`,`order`,`meta`,`mate_order`) values (?,?,?,?,?,?,?);