use fortest;
select * from bookmurl;

-- 查询到autocommit默认值为1，执行insert语句后，执行select语句，查询结果包含这些数据
-- 直接退出界面(链接)，重新登录后，select，发现这些数据
select @@autocommit;
select * from bookmurl order by uid desc;
insert into bookmurl(`url`) values("https:www.master@vii.com");

-- 设置autocommit值为0，执行3条insert语句后，
-- 0.执行select语句，查询结果包含这三条数据
-- 1.直接退出界面(链接)，重新登录后，select，并未发现这三条数据
-- 		说明未指明autocommit的时候，数据只是存入缓存，并未真正永久化到数据库中
--      要想永久化，需要主动执行commit语句 
set autocommit = 0;
select @@autocommit;
insert into bookmurl(`url`) values("https:www.notAutocommit.master@i.com");
insert into bookmurl(`url`) values("https:www.notAutocommit@i.master@i.com");
insert into bookmurl(`url`) values("https:www.notAutocommit@vi.master@i.com");
select * from bookmurl order by uid desc;

--  此时要想永久化，需要主动执行commit语句
commit;


select @@autocommit;
START TRANSACTION;
	insert into bookmurl(`url`) values("https:www.START_TRANSACTION@i.master@i.com");
	insert into bookmurl(`url`) values("https:www.START_TRANSACTION@iv.master@i.com");
	insert into bookmurl(`url`) values("https:www.START_TRANSACTION@ix.master@i.com");








 
-- -----------------废弃语句--------------------------------------------------------------------------
select * from userr_ever;
-- drop table userr_ever;
use excodout;
select * from users;

select * from fmate_code;
select * from fline_code;
select * from hash_code where hashid>89;

-- ··· 测试： in 语法查询位于指定集合中的数据值
select * from hash_code order by hashid;
select *from hash_code where hashid in (3,1,90,4,0,2);

select * from users_note order by id desc;
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