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




人员信息常用查询：
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




删除合同信息：
select * from hi_psndoc_ctrt WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00006101');
DELETE FROM hi_psndoc_ctrt WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00006101');


直接修改的调配记录在这个表里查记录
select * from bjrq_zy_psn_event where pk_psndoc in(select pk_psndoc from bd_psndoc where name='陈会升')



重推竹云：
SELECT * FROM zy_middle WHERE pk_psndoc IN (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020358')
DELETE FROM zy_middle WHERE pk_psndoc IN (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020358')
1、在【用户】节点修改人员的创建日期
2、等待后台任务定时执行或在【后台任务监控】节点执行【用户新增传竹云】任务
3、后台任务执行成功后，在【竹云入调离审批日志】节点查看是否推送成功
4、若推送成功，则稍等两分钟执行【下拉获取竹云账户】任务


