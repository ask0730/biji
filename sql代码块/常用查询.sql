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