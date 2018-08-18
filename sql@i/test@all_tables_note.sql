use fortest;





select *,length(`data`) from text_data_note;
select count(data_hash) from text_data_note;
select sum(`quote`) from text_data_note;
select  `data`,`data_hash`,`quote` from text_data_note where `data_hash` = "dsfds";
select * from submission_data_note;
select * from submission_data_note where mate ="guid";
select * from submission_data_note where mate ="title";

-- ----------------------------------------------------------------------------------
select * from getaccountsdata_note order by id desc;
select * from getaccountsdata_note  where `order`= 199 order by id desc;
select * from getclipaction_note order by id desc;
select * from getfilinginfo_note order by id desc;
select * from getnotebooks_note order by id desc;
select path,`data` from getnotebooks_note where mate_format ="String" order by id desc;
select path,`data` from getsmartfilinginfo_note where mate_format ="String" order by id desc;


select `data`, length(`data`) from getsmartfilinginfo_note where mate = "snippet";
select * from getsmartfilinginfo_note order by id desc;
select * from gettags_note order by id desc;
select * from setselectedaccount_note order by id desc;
select last_insert_id() from users_note;

select count(distinct `order`) from users_note;