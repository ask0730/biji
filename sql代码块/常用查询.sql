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
select * FROM HI_PSNJOB WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005772');
SELECT * FROM HI_PSNJOB WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005772') AND begindate = '2024-06-20';
UPDATE HI_PSNJOB SET jobglbdef25 = CONVERT(DATE, '2026-01-01')  WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00001423')  AND begindate = CONVERT(DATE, '2024-03-01'); 



删除合同信息：
select * from hi_psndoc_ctrt WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00006101');
DELETE FROM hi_psndoc_ctrt WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00006101');


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
select * from hi_psnjob WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005235')
select glbdef7 from hi_psnjob WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005235') and enddate='2025-05-31'

UPDATE hi_psnjob 
SET glbdef7 = NULL 
WHERE pk_psndoc = (SELECT pk_psndoc FROM bd_psndoc WHERE code = '00005235') 
  AND enddate = '2025-05-31';




删除算税结果：
select * from hrp_special_deduction_b where pk_org='00011T1000000000NGYX' and month='01' and year='2026'
delete from hrp_special_deduction_b where pk_org='00011T1000000000NGYX' and month='01' and year='2026'




审批流调资信息维护：
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