use fortest;
select * from table_for_test where `order` >2021;
select * from table_for_test where `order` >2021 and `mate`="author";
select count(*) from table_for_test where `order` >2021 and `mate`="title";
select * from table_for_test where `order` >2021 and `mate`="title";
-- ------------------------------------------------------------------------------------------
select mate_hash from table_for_test where mate_order= 104 and `order` = 1897 into @gethash ;
insert into table_for_test(path,mate,mate_hash,mate_order,`order`,mate_format,`data`)
	values(".subscriptionInfo.currentSku","TestBoolRemark@ix", @gethash,
    -10003,-100,"Bool","False");
-- ----------------------------------------------------------------------------
select * from table_for_test where `mate_format` ="exStorage" and `order` >0;
select * from table_for_test where `mate_order` =0;
select `mate_order`,`data` from table_for_test where `mate_order` = -2 and `order` = -1374;
select * from table_for_test order by `id` desc;
-- -----------------------------------------------
select `mate_order` from table_for_test where `order` = 260 and `path` = ".subscriptionInfo.serviceLevelsEligibleForPurchase";


select * from table_for_test;
select mate_hash from table_for_test where mate_order= 10 and `order` = 1 into @gethash ;
select * from table_for_test where mate_hash = @gethash;
select @gethash;
select * from table_for_test where path = ".subscriptionInfo.serviceLevelsEligibleForPurchase";
insert into table_for_test(path,mate,mate_hash,mate_order,`order`,mate_format,`data`)
	values(".subscriptionInfo.serviceLevelsEligibleForPurchase","TestBoolRemark", @gethash,
    -10002,-100,"Bool","True");

insert into table_for_test(path,mate,mate_hash,mate_order,`order`,mate_format,`data`)
	values("table_for_test.remark","remark", @gethash,
    -201,-10,"String","测试下给Obj添加注释能否成功");
    
update table_for_test set path="table_for_test.subscriptionInfo.serviceLevelsEligibleForPurchase" where `order`="-100";

select * from table_for_test order by `id` desc;
select * from table_for_test where `order`=1499 order by mate_order;
select * from table_for_test where `order`=1374 order by mate_order;
select max(`order`) from table_for_test;
select distinct `order` from table_for_test order by `order` desc;
select * from table_for_test where `order` = 260 order by mate_order;
select * from table_for_test where `order` = 259 order by mate_order;
select * from table_for_test where `mate_order` <0 order by mate_order desc;
update table_for_test set mate_order = 0 where id =259;
select * from table_for_test where mate="notObj" or mate="emptyObj";
select count(*) from table_for_test where `mate_order` <0 and `order`>0 order by mate_order desc;
select * from table_for_test where `order`=260 and `path` = '.subscriptionInfo.serviceLevelsEligibleForPurchase';
select * from table_for_test where `path` like "table_for_test%";
select last_insert_id() from table_for_test;
select * from table_for_test where id =0;
select * from submission_data_note where `mate_format` ="exStorage";
select `data` from submission_data_note where `mate_format` ="exStorage" and `order`=45 into @exstorage;
select @exstorage;

insert into table_for_test(path,mate,mate_hash,mate_order,`order`,mate_format,`data`)
	values(".remark","test_exStorage", @gethash,
    -202,-13,"exStorage",@exstorage);

select * from table_for_test where path =1;



select path, `data` , mate_order, mate_format from table_for_test where `order` =1960  order by id ;
select id,mate, mate_format, `data`,`order` from table_for_test where path = '.subscriptionInfo.currentlySubscribed'  order by id ;


SELECT auto_increment FROM information_schema.tables where table_schema="fortest" and table_name="table_for_test";
SELECT auto_increment FROM information_schema.tables where table_schema='fortest' and table_name='table_for_test';

select * from table_for_test where `order` != 976341 order by mate_order;
select count(distinct mate_order) from table_for_test where `order` = 377219; -- order by mate_order;
select * from table_for_test where `order` = 377219 order by mate_order;
select * from table_for_test where `order` != 377219 order by mate_format;
select path,`data` from table_for_test where `order` = 377219 order by `data`;
select path, mate, `order` from table_for_test ;
delete  from table_for_test where id <374;
truncate table table_for_test;
alter table table_for_test change column mate_hash mate_hash binary(20) not null;

insert into `table_for_test` (`mate_hash`,`path`,`format`,`data`,`order`,`meta`,`mate_order`) values (?,?,?,?,?,?,?);
