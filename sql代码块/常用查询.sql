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
select * from hi_psnjob where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00001423');--工作记录
select * from hi_psnorg where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00020569');--组织关系
select * from bd_psnjob where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00020569');--人员任职信息
select * from hi_psndoc_wadoc where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00020569');--薪资变动
select * from wa_data where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00020569') and pk_wa_class ='10011T100000000FZXGB';--薪酬
select * from wa_classitem where pk_wa_class ='10011T100000000FZXGB' and cyear='2025' and cperiod='12';--薪资发放项目



更新任职受雇从业日期：
select * FROM HI_PSNJOB WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '10012591');
SELECT * FROM HI_PSNJOB WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005772') AND begindate = '2024-06-20';
UPDATE HI_PSNJOB SET jobglbdef25 = CONVERT(DATE, '2026-03-01')  WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00001423')  AND begindate = CONVERT(DATE, '2024-03-01'); 



删除合同信息：
select * from hi_psndoc_ctrt WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020710');
DELETE FROM hi_psndoc_ctrt WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020710');


直接修改的调配记录在这个表里查记录
select * from bjrq_zy_psn_event where pk_psndoc in(select pk_psndoc from bd_psndoc where name='陈会升')



重推竹云：
SELECT * FROM zy_middle WHERE pk_psndoc IN (SELECT pk_psndoc FROM bd_psndoc WHERE code = '10012564')
DELETE FROM zy_middle WHERE pk_psndoc IN (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020358')
1、在【用户】节点修改人员的创建日期
2、【后台任务监控】节点执行【用户新增传竹云】任务
3、后台任务执行成功后，在【竹云入调离审批日志】节点查看是否推送成功
4、若推送成功，则稍等两分钟执行【下拉获取竹云账户】任务

select pk_psndoc from sm_user where user_code='10012564'
正式环境下载下/nclogs/zy/zy.log,服务器1




根据部门编码查询部门人数：
SELECT 
    org_dept.code AS 部门编码,
    org_dept.name AS 部门名称,
    COUNT(DISTINCT bd_psndoc.pk_psndoc) AS 部门人数
FROM bd_psndoc  -- 人员档案表
INNER JOIN hi_psnjob T1  -- 人员岗位信息表
    ON T1.pk_psndoc = bd_psndoc.pk_psndoc
    AND T1.lastflag = 'Y'  -- 最新岗位记录
    AND T1.ismainjob = 'Y'  -- 主岗位（避免兼职重复计数）
    AND T1.endflag = 'N'  -- 岗位未结束（在职）
INNER JOIN org_dept  -- 部门表
    ON org_dept.pk_dept = T1.pk_dept
WHERE 
    bd_psndoc.enablestate = 2  -- 人员状态为"启用"（有效）
    AND org_dept.code = 'QTH00004'  -- 替换为实际的部门编码
GROUP BY 
    org_dept.code, org_dept.name





查政治面貌：
-- 根据人员编码查询政治面貌
SELECT 
    bd_psndoc.code AS 人员编码,
    bd_psndoc.name AS 姓名,
    CASE 
        WHEN bd_defdoc.name IS NULL THEN '未填写'
        ELSE bd_defdoc.name 
    END AS 政治面貌
FROM bd_psndoc  -- 人员基本信息表
LEFT JOIN bd_defdoc  -- 字典表（政治面貌）
    ON bd_psndoc.polity = bd_defdoc.pk_defdoc
WHERE bd_psndoc.code = '00000935'  -- 替换为实际的人员编码







北森人员推送：
SELECT * FROM mzjh_sync_beisen_psn WHERE pk_psndoc IN (SELECT pk_psndoc FROM bd_psndoc WHERE code = '10012328')

UPDATE mzjh_sync_beisen_psn 
SET 
  userid = '627022117',  
  record_id = '4fac82ad-5639-48fe-8b8f-c970a8775f2a',
  flag = 'Y',  
	TS='2025-12-16 15:31:01'
WHERE pk_psndoc IN (
  SELECT pk_psndoc FROM bd_psndoc WHERE code = '10012328'
);




根据身份证号查参见工作日期：
SELECT ID, JOINWORKDATE 
FROM BD_PSNDOC 
WHERE ID IN (
    '110105198602251544',
    '612732198107091522'
)




查本企业总工龄：
SELECT jobglbdef3  FROM hi_psnjob WHERE pk_psndoc IN (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00019956')




财务费用属性：
SELECT * FROM HI_PSNJOB WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005772') AND begindate = '2024-06-20';


UPDATE HI_PSNJOB
SET jobglbdef15 = '10011T10000000002P1M'
WHERE pk_psndoc = (
    SELECT pk_psndoc 
    FROM bd_psndoc 
    WHERE code = '00005772'
) 
AND begindate = '2024-06-20';




更新考勤组织：
select * from hi_psnjob WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00003952')
select glbdef7 from hi_psnjob WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005235') and enddate='2025-05-31'

UPDATE hi_psnjob 
SET glbdef7 = NULL 
WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005235') 
  AND enddate = '2025-05-31';




删除算税结果：
select * from hrp_special_deduction_b where pk_org='00011T1000000000NGYX' and month='01' and year='2026'
delete from hrp_special_deduction_b where pk_org='00011T1000000000NGYX' and month='01' and year='2026'




审批流定调资信息维护：
SELECT
    w.pk_org,
    (SELECT name FROM org_orgs o WHERE o.pk_org = w.pk_org) AS oraName,
    (SELECT name FROM bd_psndoc d WHERE d.pk_psndoc = w.pk_psndoc) AS psnName,
    (SELECT name FROM wa_item m WHERE m.pk_wa_item = w.pk_wa_item) AS itemName,
    w.begindate,
    w.enddate,
    w.nmoney,
    w.workflowflag -- 是否来自审批流
FROM
    hi_psndoc_wadoc w
WHERE
    w.lastflag = 'Y' -- 最新标志
    AND w.waflag = 'Y' -- 发放标志
    AND w.workflowflag = 'Y' -- 是否来自审批流
    AND EXISTS (
        SELECT 1 
        FROM bd_psndoc d 
        WHERE w.pk_psndoc = d.pk_psndoc 
        AND d.code IN ('00020664')
    );


UPDATE hi_psndoc_wadoc
SET workflowflag = 'N'
WHERE
    lastflag = 'Y'
    AND waflag = 'Y'
    AND workflowflag = 'Y'
    AND pk_psndoc IN (SELECT pk_psndoc FROM bd_psndoc WHERE code IN ('00020664'));
    





更改单据显示状态：
-- 1、将指定单据的状态修改为【已执行】
UPDATE HI_STAPPLY
   SET APPROVE_STATE = 102
 WHERE BILL_CODE = '单据号';

-- 2、审批中心错误消息 - 数据库手动订正处理
-- 2.1 先查询出 该单据+指定用户 对应的错误审批消息数据（用于核对待更新的主键）
SELECT *
  FROM sm_msg_user
 WHERE pk_message IN (SELECT pk_message
                        FROM sm_msg_approve
                       WHERE billno = '单据号')
   AND pk_user IN (SELECT cuserid
                     FROM sm_user
                    WHERE user_name = '用户名称');

-- 2.2 手动更新审批消息为【已读】状态，消除错误提醒
UPDATE sm_msg_user
   SET isread = 'Y'
 WHERE pk_message = '要更新的pk_message';

-- 提交事务，确认以上所有数据库修改生效
COMMIT;






更新人员类别：
select * from hi_psnjob WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00018922') and begindate='2024-10-20'


-- select name from BD_PSNCL where PK_PSNCL='10011T10000000004348'

-- select PK_PSNCL from BD_PSNCL where name='辞职'

UPDATE hi_psnjob 
SET PK_PSNCL = (SELECT PK_PSNCL FROM BD_PSNCL WHERE name = '辞职')
WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00018922') 
  AND begindate = '2024-10-20';







查年假额度：
  SELECT
    b.*,
    attend.psncl_name  AS psnclname,
    attend.staff_code  AS staffcode,
    attend.staff_name  AS staffname,
    attend.dept_name   AS deptname,
    attend.org_name    AS orgname
FROM ts_leave_balance b
JOIN ts_attend_staff attend ON attend.staff_id = b.staffid
    AND attend.last_flag = 1
    AND attend.attend_type != 2
    AND b.tenantid = attend.tenantid
WHERE b.tenantid = '00011T1000000000591O'
  AND b.leavetype = '00011T1000000000591O0000000001'  -- 年假
  AND b.periodtype = '0'                               -- 年度
  AND (attend.staff_code LIKE '%00003952%' OR attend.staff_name LIKE '%00003952%')
  AND b.year = '2026'
  AND b.month IS NULL
  AND attend.last_flag = 1
  AND attend.attend_type <> 2
  AND attend.end_flag = 0
ORDER BY attend.staff_code DESC, attend.staff_name DESC, attend.dept_id DESC
OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY;






财务中间表：
select * from CUX_NCHR_V_SALARYHISTORY where corpcode = '10000003' and A00Z0 = '2026-01'




考勤日报表：ts_daystat


删除日报数据：
select * from ts_daystat where STAFF_ID =(select pk_psndoc from bd_psndoc where code ='00001699');


SELECT * 
FROM ts_daystat 
WHERE STAFF_ID = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00006570')
  AND calendar >= '2026-09-23 00:00:00.000'
  AND calendar < '2026-09-24 00:00:00.000'

  DELETE FROM ts_daystat 
WHERE STAFF_ID = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005771')
  AND calendar >= '2026-01-01 00:00:00.000'
  AND calendar < '2026-02-01 00:00:00.000';




请假类型：
select type_name,type_name2 from ts_leave_type_new

UPDATE ts_leave_type_new
SET type_name2 = 21
WHERE type_name = '带薪病假';




查借调单单据号：
select * from HI_PARTAPPLY where PK_PARTMNG='10011T10000000272DOY'



select 
t1.user_code yh_code,t2.code ry_code,t2.name ry_name,t2.id ry_id,t1.cuserid yh_pk, t3.poststat ry_zt,
t3.BEGINDATE ry_ksdate,t3.pk_psnjob ry_psnjob,t3.glbdef7,t3.LASTFLAG,t3.ISMAINJOB,
t2.EMAIL ry_yx,
a1.code org_code,a1.name org_name,
a2.code dept_code,a2.name dept_name,a2.pk_dept pk_dept,
a3.postcode post_code,a3.postname post_name,
a4.name dept_sjname
from sm_user t1  --用户表
right join bd_psndoc t2 on t1.pk_psndoc=t2.pk_psndoc  --人员基本信息表
left join hi_psnjob t3 on t2.pk_psndoc=t3.pk_psndoc --人员任职记录表
left join org_orgs a1 on t3.pk_org=a1.pk_org --组织档案
left join org_dept a2 on t3.pk_dept=a2.pk_dept --部门档案
left join om_post a3 on t3.pk_post=a3.pk_post --岗位档案
left join org_dept a4 on a2.PK_FATHERORG=a4.pk_dept --上级部门











员工考核信息：
select * from hi_psndoc_ass where pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00004126') and lastflag='Y'

DELETE from hi_psndoc_ass 
where pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00004126') 
and lastflag='Y';



人员试用情况：
select * from hi_psndoc_trial where pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020304') 
UPDATE hi_psndoc_trial SET enddate = '2025-06-26' WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020304');
UPDATE hi_psndoc_trial SET regulardate = '2025-06-27' WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020304');



员工管理范围薪酬委托报错：
SELECT *  FROM hr_relation_psn WHERE assgid IN ( SELECT assgid FROM hi_psnjob  WHERE pk_psndoc IN ( SELECT pk_psndoc   FROM bd_psndoc  WHERE name = '邹永梅')) AND dr = 1 

delete from hr_relation_psn where assgid in(select assgid from hi_psnjob where pk_psndoc in(select pk_psndoc from bd_psndoc where name='邹永梅')) and dr=1



专项附加扣除状态查询：
select * from hrp_special_deduction_log where ts like '%2026-01-01 17%'




nested exception is org.apache.ibatis.exceptions.TooManyResultsException: Expected one result (or null) to be returned by selectOne(), but found: 2：
请假单重复
select * from ts_leave_apply where STAFFID=(select pk_psndoc from bd_psndoc where code ='00000658') and leaveremark='肠胃炎发烧'


DELETE FROM ts_leave_apply 
WHERE STAFFID = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00000658') 
  AND leaveremark = '肠胃炎发烧';


北森日志路径
服务器1，nchome/nclogs/beisen.log


用元数据名查表名：
select defaulttablename  from md_class where name  ='TransferOrderReviewVO'


更新入职申请单生效日期：
UPDATE hi_psnjob
SET BEGINDATE = '2026-03-01'
WHERE PK_PSNJOB IN (
    SELECT PK_PSNJOB
    FROM HI_ENTRYAPPLY
    WHERE BILL_CODE IN ('LYBL202602120001')
)



转单复核生效日期：
select onboarding_date from hi_transfer_order_review where pk_psndoc= (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020707')  

UPDATE hi_transfer_order_review 
SET def15 = '2026-03-01'  
WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020707');





转单复核入职日期：
select onboarding_date from hi_transfer_order_review where pk_psndoc= (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020718')  


UPDATE hi_transfer_order_review 
SET onboarding_date = '2026-03-01 00:00:00'  -- 完整的日期时间值，单引号包裹
WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00020718');






select * from ts_staff_rule_cache where staffid in(SELECT pk_psndoc from bd_psndoc WHERE code='00001838')



删除日月报数据：
select * from ts_daystat where STAFF_ID=(select pk_psndoc from bd_psndoc where code = '00000692') and dept_id='10011T100000001YK73X' and CALENDAR >= CONVERT(DATETIME, '2026-01-01 00:00:00', 120) and CALENDAR <= CONVERT(DATETIME, '2026-01-31 00:00:00', 120);


select * from ts_monthstat where dept_id='10011T100000001YK73X' and STAFF_ID=(select pk_psndoc from bd_psndoc where code = '00000692') and begindate='2026-01-01 00:00:00.000'



查借调单：
select * from HI_PARTAPPLY where PK_PSNDOC=(select pk_psndoc from bd_psndoc where code = '00020236') 



备份表：
-- 1. 先创建备份表（用一个和所有字段兼容的通用结构）
CREATE TABLE huanghui (
    SourceTable NVARCHAR(50), -- 记录数据来源的表名，方便以后区分
    RawData XML,              -- 用XML格式存原始行数据，兼容不同结构
    CreateTime DATETIME DEFAULT GETDATE()
);

-- 2. 插入 HRKQ_LEAVE 的两条数据
INSERT INTO huanghui (SourceTable, RawData)
SELECT 
    'HRKQ_LEAVE',
    (SELECT * FROM HRKQ_LEAVE WHERE PK_PSNDOC=(SELECT pk_psndoc FROM bd_psndoc WHERE code = '00001013') AND billno='QJSQ202602090528' FOR XML RAW);

-- 3. 插入 ts_leave_apply_detail 的两条数据
INSERT INTO huanghui (SourceTable, RawData)
SELECT 
    'ts_leave_apply_detail',
    (SELECT * FROM ts_leave_apply_detail WHERE id = 'cb7d5b2a9abf4e54b5a2b231a6cccab3' FOR XML RAW);

INSERT INTO huanghui (SourceTable, RawData)

select * from huanghui;


ts_leave_apply




取消审批单据：
select * from HRKQ_OVERTIME where BILLNO='JBSQ202604010035'

UPDATE HRKQ_OVERTIME 
SET approvestatus = 2 
WHERE BILLNO = 'JBSQ202604010035';





培训系统：
先生成用户
select * from mzjh_bdsynctime--查看时间--code=0 组织 code=1 人员 code=4 岗位 code=5 部门
select * from mzjh_sync_zxy_data where data_status='2'--表示推送报错--没有记录标识没有推送,删除这个表的推送记录
select * from mzjh_sync_zxy_data where id in ('00020619','00020618','00020736','00020778','00020777','00020756','00020771','00020779','00020776')
update bd_psndoc set ts='2026-04-10 14:23:00' where code='00020745'--更新时间为最新时间，重新执行后台任务：同步人员到培训系统






销差单：

select * from HRKQ_TRIPOFF where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00006475');--销差单主表

select * from ts_business_trip_apply where STAFFID =(select pk_psndoc from bd_psndoc where code ='00006475');--出差、销差共用的中间表

select * from ts_business_trip_revoke_detail where STAFFID =(select pk_psndoc from bd_psndoc where code ='00006475');--销差单子表

实际目的地：def1
出行方式：def2
出差报销天数：def4
其他出行方式：def5
实际开始时间：tripoffbegintime




出差单：

select * from HRKQ_TRIP where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00003439');--出差单主表

select * from ts_business_trip_apply where STAFFID =(select pk_psndoc from bd_psndoc where code ='00003439');--出差、销差共用的中间表

select * from ts_business_trip_apply_detail where STAFFID =(select pk_psndoc from bd_psndoc where code ='00003439');--出差单子表

select tripendtime,def1,tripday from HRKQ_TRIP where BILLNO='0000000360'

结束时间：tripendtime
出差报销天数：def1
出差时长:tripda


delete from HRKQ_TRIP where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00003439');--出差单主表

delete from ts_business_trip_apply where STAFFID =(select pk_psndoc from bd_psndoc where code ='00003439');--出差、销差共用的中间表

delete from ts_business_trip_apply_detail where STAFFID =(select pk_psndoc from bd_psndoc where code ='00003439');--出差单子表





四分产假取消结算：

select * from ts_leave_balance where leavetype='867fed43603645bba8e0decd9f2ad580' and staffid='00011T1000000000RVHQ'

UPDATE ts_leave_balance
SET clearingstate = 1
WHERE leavetype='867fed43603645bba8e0decd9f2ad580' 
  AND staffid='00011T1000000000RVHQ' 
  AND begindatetime='2025-01-01 00:00:00.000';


UPDATE ts_leave_balance 
SET invalidstate = 0 
WHERE leavetype='867fed43603645bba8e0decd9f2ad580' 
  AND staffid='00011T1000000000RVHQ' 
  AND invalidstate=1;






请假类型：
select id from TS_LEAVE_TYPE_NEW where TYPE_NAME='育儿假'
育儿假的主键:54be2247ca7940d3a71c1557b64800c9



select name from TS_LEAVE_TYPE_NEW 







加班转调休，重新转：
select * from ts_overtime_split where staffid in(select pk_psndoc from bd_Psndoc where code='00002000') 
找到你要改的记录的id

取消之后，用这个语句更新下状态，然后再转

update ts_overtime_split set billstatus=1,transferflag=0 where  staffid in(select pk_psndoc from bd_Psndoc where code='00002000') and id='09c3ce7a44624cb2922aea2b80aa48b2'








薪资档案查不到人：
员工管理范围dr改成1
SELECT *  FROM hr_relation_psn WHERE assgid IN ( SELECT assgid FROM hi_psnjob  WHERE pk_psndoc IN ( SELECT pk_psndoc FROM bd_psndoc  WHERE code = '00000248')) and creationtime='2026-05-08 12:46:32'

薪资档案里存的工作记录主键被删了，所以查不出来
SELECT * FROM wa_data WHERE pk_wa_class = N'10011T100000000L5RG0' AND cyear = N'2026' AND cperiod = N'05'  AND dr = 0









月报审批单：

select * from bjrq_monthappr where billno='08c423811bc141748603794378bb2977'


UPDATE bjrq_monthappr
SET approvestatus = 2 
WHERE billno='08c423811bc141748603794378bb2977'


select * from bjrq_monthappr where def1='202601'

and staff_id=(select pk_psndoc from bd_psndoc where code in '00007087')



select * from bjrq_monthappr where staff_id=(select pk_psndoc from bd_psndoc where code='00007087') and begindate='2025-10-01 00:00:00'





SELECT * 
FROM bjrq_monthappr 
WHERE staff_id IN (
    SELECT pk_psndoc 
    FROM bd_psndoc 
    WHERE code IN (
'00007087',
'00008008',
'00008278',
'00011929',
'00012421',
'00010406',
'00010930',
'00010372',
'00010374',
'00010373',
'00010340',
'00010178',
'00010159',
'00010232',
'00010157',
'00010206',
'00010186',
'00010188',
'00005775',
'00002039',
'00002008',
'00008973',
'00008972',
'00009873',
'00009029',
'00009079',
'00018191',
'00018401',
'00019094',
'00019951',
'00020295',
'10012253',
'00020697',
'00020724',
'00020751',
'00020753',
'00020754',
'00020795',
'00020794',
'00020793',
'00020797',
'00020796',
'00020837',
'00020836',
'00020838'
    )
  )	
	and begindate='2026-01-01 00:00:00'









年度工资收入去重：
  select * from hi_psndoc_glbdef25 where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00010113') and begindate='2024-12-01' and glbdef3='466666.18'











  修改工作记录的党组织：
select jobglbdef32 from hi_psnjob where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00003952') and begindate='2025-05-01'


UPDATE hi_psnjob 
SET jobglbdef32 = '10011T1000000012WH3U' 
WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00003952') 
  AND begindate = '2024-02-27';










撤销岗位失败！原因：撤销岗位引起变动的人员，有定调资单据状态为[编写中]、[已提交]、[审核中]的单据：
  select BILLCODE,wa_psnappaprove_b.* from wa_psnappaprove_b inner join wa_psnappaprove on wa_psnappaprove_b.pk_psnapp = wa_psnappaprove.pk_psnapp where wa_psnappaprove_b.pk_psndoc in ( N'00011T100000000QWP20' , N'00011T100000000QWP23' , N'00011T100000000QWP26' , N'00011T100000000QWWKL' , N'00011T100000000QWWKO' , N'00011T100000000QWWKR' ) and wa_psnappaprove.confirmstate in ( N'-1' , N'2' , N'3' )

SELECT
	distinct t1.BILLCODE --单据号
    ,t2.confirmstate --审批状态
    ,a1.user_name   --创建人
    ,t1.dr,t1.PK_PSNAPP --定调资申请单主键
FROM
	WA_PSNAPPAPROVE t1
left join WA_PSNAPPAPROVE_B t2 on t1.PK_PSNAPP=t2.PK_PSNAPP
left join bd_psnjob t3 on t2.pk_psnjob=t3.pk_psnjob
left join sm_user a1 on t1.creator=a1.cuserid
where t1.BILLCODE in ('LYBL202308180029'
)

SELECT
	distinct t1.BILLCODE --单据号
    ,t1.PK_PSNAPP
    ,t2.PK_WA_ITEM
    ,t3.name --薪资项目
    ,t2.PK_PSNAPP_B --定调资申请表体pk
    ,t2.PK_WA_SECLV_APPLY --薪档
FROM
	WA_PSNAPPAPROVE t1
left join WA_PSNAPPAPROVE_B t2 on t1.PK_PSNAPP=t2.PK_PSNAPP
left join WA_CLASSITEM t3 on t2.PK_WA_ITEM=t3.PK_WA_ITEM
where t1.BILLCODE in ('LYBL202308180029')

delete from WA_PSNAPPAPROVE where PK_PSNAPP in (
'10011T100000000YQ47Q')
    
delete from WA_PSNAPPAPROVE_B where PK_PSNAPP in (
'10011T100000000YQ47Q')






修改请假单申请时间：
select * from PUB_WF_INSTANCE where billno='QJSQ202605140057'。
select * from  pub_workflownote  where billno='QJSQ202605140057' and approveresult='Y'
select * from ts_leave_apply_detail where id = 'e7faf8de0e9e43429779455cfa8a3a2c'。
select * from HRKQ_LEAVE where BILLNO='QJSQ202605140057'。

UPDATE ts_leave_apply_detail
SET 
    creationtime = '2026-05-14 10:32:52.257',
    modifiedtime = '2026-05-14 10:32:52.257'
WHERE id = 'e7faf8de0e9e43429779455cfa8a3a2c';


UPDATE HRKQ_LEAVE
SET 
    applydate = '2026-05-14 10:28:12',
    approvetime = '2026-05-14 10:49:24',
    creationtime = '2026-05-14 10:28:12'
WHERE BILLNO = 'QJSQ202605140057';

UPDATE PUB_WF_INSTANCE
SET 
    endts = '2026-05-14 10:49:24',
    startts = '2026-05-14 10:49:24'
WHERE billno = 'QJSQ202605140057';

UPDATE pub_workflownote
SET 
    dealdate = '2026-05-14 10:49:24',
    senddate = '2026-05-14 10:32:53'
WHERE billno = 'QJSQ202605140057' 
  AND approveresult = 'Y';







出差单：

select * from HRKQ_TRIP where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00006575') and BILLNO='0000007524'

select * from ts_business_trip_apply where STAFFID =(select pk_psndoc from bd_psndoc where code ='00006575')--出差、销差共用的中间表;

select * from ts_business_trip_apply_detail where STAFFID =(select pk_psndoc from bd_psndoc where code ='00006575');--出差单子表

select tripendtime,def1,tripday from HRKQ_TRIP where BILLNO='0000007524'




备份表：
delete from HRKQ_TRIP where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00006575') and BILLNO='0000007524'

delete  from ts_business_trip_apply where STAFFID =(select pk_psndoc from bd_psndoc where code ='00006575') and id='ccc821018a884b09b95af2d746760927'

delete  from ts_business_trip_apply_detail where STAFFID =(select pk_psndoc from bd_psndoc where code ='00006575') and id='288a6b44896246468f5a396cc327560f'



CREATE TABLE huanghui (
    SourceTable NVARCHAR(50), -- 记录数据来源的表名，方便以后区分
    RawData XML,              -- 用XML格式存原始行数据，兼容不同结构
    CreateTime DATETIME DEFAULT GETDATE()
);


-- 备份 HRKQ_TRIP 表数据
INSERT INTO huanghui (SourceTable, RawData)
SELECT 
    'HRKQ_TRIP' AS SourceTable,
    (SELECT * FROM HRKQ_TRIP t2 WHERE t2.pk_psndoc = t1.pk_psndoc AND t1.BILLNO = t2.BILLNO FOR XML RAW, ELEMENTS) AS RawData
FROM HRKQ_TRIP t1
WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00006575') 
  AND BILLNO='0000007524';






撤销岗位失败！原因：撤销岗位引起变动的人员，有定调资单据状态为[编写中]、[已提交]、[审核中]的单据：
  select BILLCODE,wa_psnappaprove_b.* from wa_psnappaprove_b inner join wa_psnappaprove on wa_psnappaprove_b.pk_psnapp = wa_psnappaprove.pk_psnapp where wa_psnappaprove_b.pk_psndoc in ( N'00011T100000000QWP20' , N'00011T100000000QWP23' , N'00011T100000000QWP26' , N'00011T100000000QWWKL' , N'00011T100000000QWWKO' , N'00011T100000000QWWKR' ) and wa_psnappaprove.confirmstate in ( N'-1' , N'2' , N'3' )

SELECT
	distinct t1.BILLCODE --单据号
    ,t2.confirmstate --审批状态
    ,a1.user_name   --创建人
    ,t1.dr,t1.PK_PSNAPP --定调资申请单主键
FROM
	WA_PSNAPPAPROVE t1
left join WA_PSNAPPAPROVE_B t2 on t1.PK_PSNAPP=t2.PK_PSNAPP
left join bd_psnjob t3 on t2.pk_psnjob=t3.pk_psnjob
left join sm_user a1 on t1.creator=a1.cuserid
where t1.BILLCODE in ('DDBL202307260024'
)

SELECT
	distinct t1.BILLCODE --单据号
    ,t1.PK_PSNAPP
    ,t2.PK_WA_ITEM
    ,t3.name --薪资项目
    ,t2.PK_PSNAPP_B --定调资申请表体pk
    ,t2.PK_WA_SECLV_APPLY --薪档
FROM
	WA_PSNAPPAPROVE t1
left join WA_PSNAPPAPROVE_B t2 on t1.PK_PSNAPP=t2.PK_PSNAPP
left join WA_CLASSITEM t3 on t2.PK_WA_ITEM=t3.PK_WA_ITEM
where t1.BILLCODE in ('DDBL202307260024')

delete from WA_PSNAPPAPROVE where PK_PSNAPP in (
'10011T100000000WTY6Y')
    
delete from WA_PSNAPPAPROVE_B where PK_PSNAPP in (
'10011T100000000WTY6Y')






改兼职单任职类型：
select * from HI_PARTAPPLY where PK_PSNDOC=(select pk_psndoc from bd_psndoc where id = '140225198612034013') 


select pk_job_type from HI_PARTAPPLY where PK_PSNDOC=(select pk_psndoc from bd_psndoc where id = '410782198901290443') 

select name from bd_defdoc where PK_DEFDOC='10011T100000000EU4F4'

select PK_DEFDOC from bd_defdoc where name='外派'--10011T100000000007Q2


UPDATE HI_PARTAPPLY
SET pk_job_type ='10011T100000000007Q2'
WHERE BILL_code = 'JZBL202605140003';


改兼职单的流程类型：
select * from HI_PARTAPPLY where PK_PSNDOC=(select pk_psndoc from bd_psndoc where id = '110106199803180632') 

select transtypeid from HI_PARTAPPLY where PK_PSNDOC=(select pk_psndoc from bd_psndoc where id = '110106199803180632') 

select * from bd_billtype

select PK_BILLTYPEID from bd_billtype where billtypename='培养锻炼'

UPDATE HI_PARTAPPLY
SET transtypeid ='10011T100000000EU4F5'
WHERE BILL_code = 'JZBL202605140005';






修改出差单申请日期：

select * from HRKQ_TRIP where pk_psndoc = (select pk_psndoc from bd_psndoc where code = '00001747');--出差单主表

select * from ts_business_trip_apply where STAFFID =(select pk_psndoc from bd_psndoc where code ='00001747');--出差、销差共用的中间表

select * from ts_business_trip_apply_detail where STAFFID =(select pk_psndoc from bd_psndoc where code ='00001747');--出差单子表

UPDATE HRKQ_TRIP 
SET 
    applydate = '2026-05-18 15:38:40',
    creationtime = '2026-05-28 15:38:40'
WHERE 
    pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00001747');


UPDATE ts_business_trip_apply 
SET 
    applydate = '2026-05-18 15:42:01.273',
    creationtime = '2026-05-18 15:42:01.273',
    modifiedtime = '2026-05-18 15:42:01.273'
WHERE 
    STAFFID = (select pk_psndoc from bd_psndoc where code ='00001747');

UPDATE ts_business_trip_apply_detail 
SET 
    creationtime = '2026-05-18 15:42:01.280',
    modifiedtime = '2026-05-18 15:42:01.280'
WHERE 
    STAFFID = (select pk_psndoc from bd_psndoc where code ='00001747');

  
--流程实例列表
select * from PUB_WF_INSTANCE where billno='0000007696'--列表
select * from  pub_workflownote  where billno='0000007696' and approveresult='Y'--详情


UPDATE PUB_WF_INSTANCE 
SET 
    startts = '2026-05-18 15:42:01'
WHERE 
    billno = '0000007696';


UPDATE pub_workflownote 
SET senddate = '2026-05-18 15:42:01'
WHERE billno = '0000007696';






请假单，销假单，以及子表：

--休假主表--休假子表--销假子表
select * from ts_leave_apply_detail where STAFFID =(select pk_psndoc from bd_psndoc where code ='00005315');

请假单：
select * from ts_leave_apply_detail where id = '1eb7ddf7bf1143d1ba0a62d1e2042f43'
update ts_leave_apply_detail set leaveendtime = '2026-02-14 13:00:00.000' where id = '1eb7ddf7bf1143d1ba0a62d1e2042f43'

调整单：
select * from ts_leave_off_detail where id = '84b25e894f9c49518039453ccc805f80'
update ts_leave_off_detail set leaveoffendtime = '2026-01-16 13:00:00.000' where id = '84b25e894f9c49518039453ccc805f80'


select * from HRKQ_LEAVE where billno='QJSQ202605190017'

select * from HRKQ_LEAVEOFF where billno='XJSQ202605250005'

UPDATE HRKQ_LEAVE 
SET leaveday = 7, weekdays = 7
WHERE BILLNO = 'QJSQ202605210220';