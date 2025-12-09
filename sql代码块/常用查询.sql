- select * from BD_PSNDOC where CODE='10012458'

- select * from BD_PSNDOC where CODE='10012458' and age<19 and birthdate is not null

- select *from view_NSRJCXX

- 使用解决方案附件脚本，清除该人员缓存数据，然后再到【考勤规则】节点，点击列表记录上的“手工排班”按钮，重新排班，重新生成日报数据。
--查询
select * from ts_staff_calendar_history where STAFF_ID =(select pk_psndoc from bd_psndoc where code = '00002306') and CALENDAR >= CONVERT(DATETIME, '2025-02-01 00:00:00', 120) and CALENDAR <= CONVERT(DATETIME, '2025-02-28 00:00:00', 120);--固定班制排班记录
select * from ts_staff_rule_cache where STAFFID =(select pk_psndoc from bd_psndoc where code ='00002306');--缓存记录

--删除
delete from ts_staff_calendar_history where STAFF_ID =(select pk_psndoc from bd_psndoc where code = '00002306') and CALENDAR >= CONVERT(DATETIME, '2025-02-01 00:00:00', 120) and CALENDAR <= CONVERT(DATETIME, '2025-02-28 00:00:00', 120);
delete from ts_staff_rule_cache where STAFFID =(select pk_psndoc from bd_psndoc where code ='00002306');
commit;





select * from bd_psndoc where code = '00020569';--人员基本信息
select * from hi_psnjob where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00020569');--工作记录
select * from hi_psnorg where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00020569');--组织关系
select * from bd_psnjob where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00020569');--人员任职信息
select * from hi_psndoc_wadoc where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00020569');--薪资变动
select * from wa_data where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00020569') and pk_wa_class ='10011T100000000FZXGB';--薪酬
select * from wa_classitem where pk_wa_class ='10011T100000000FZXGB' and cyear='2025' and cperiod='12';--薪资发放项目



更新任职受雇从业日期：
select * FROM HI_PSNJOB WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00018206');
SELECT * FROM HI_PSNJOB WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00018206') AND begindate = '2025-09-08';
UPDATE HI_PSNJOB SET jobglbdef25 = CONVERT(DATE, '2025-12-01')  WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00018206')  AND begindate = CONVERT(DATE, '2025-09-08'); 
