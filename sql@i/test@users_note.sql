


SELECT max(`order`) FROM users_note;
select * from users_note order by id desc;
select * from users_note where `order` >110000;
select count(*) from users_note where `order` >110000;
-- delete from users_note where `order` >110000;


select * from users_note where mate_order = 3 and `order` = 90532;
select * from fmate_code;
select * from fline_code;
select * from hash_code where hashid>89;

-- ··· 测试： in 语法查询位于指定集合中的数据值
select * from hash_code order by hashid;
select *from hash_code where hashid in (3,1,90,4,0,2);

select * from users_note order by id desc;
select * from users_note where mate_order <0 order by id desc;

select last_insert_id() from users_note;

select count(distifline_codenct `order`) from users_note;
select path, `data` , mate_order, mate_format from users_note where `order` =1960  order by id ;
select id,mate, mate_format, `data`,`order` from users_note where path = '.subscriptionInfo.currentlySubscribed'  order by id ;


SELECT auto_increment FROM information_schema.tables where table_schema="fortest" and table_name="users_note";
SELECT auto_increment FROM information_schema.tables where table_schema='fortest' and table_name='users_note';

select * from users_note where `order` != 976341 order by mate_order;
select count(distinct mate_order) from users_note where `order` = 377219; -- order by mate_order;
select * from users_note where `order` = 377219 order by mate_order;
select * from users_note where `order` != 377219 order by mate_format;
select path,`data` from users_note where `order` = 377219 order by `data`;
select path, mate, `order` from users_note ;
delete  from users_note where id <374;
truncate table users_note;
alter table users_note change column mate_hash mate_hash binary(20) not null;

insert into `users_note` (`mate_hash`,`path`,`format`,`data`,`order`,`meta`,`mate_order`) values (?,?,?,?,?,?,?);