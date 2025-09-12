-- 薪资期间实际发薪人原信息（不含年度收入子集申报金额）
-- MZ301_01 MZ301_01公积金缴纳表1
-- t_1 实际发薪
select 
  a3.name xzfa_name, --薪资方案名称
  t2.qj qj,  --薪资期间
  a1.name org_name, --发薪组织名称
  t1.pk_org pk_org, --发薪组织pk
  t1.pk_group pk_group,--发薪组织所属集团pk
  a2.name org_rzname, --任职组织名称
  t3.name ry_name, --人员姓名
  t3.id ry_id,  --身份证
  a4.name ry_jg, --籍贯
  t3.mobile ry_dh,  -- 电话
t3.pk_psndoc pk_psndoc,  --人员主键
  t4.sb_js sb_js, --社保基数
  t4.sb_jf sb_jf --社保缴费
from           wa_data t1  --薪资档案/薪资发放
     inner join (select distinct concat(cyear,concat('-',cperiod)) qj from wa_period where dr='0') t2 on t2.qj=concat(t1.cyear,concat('-',t1.cperiod))  --薪资期间
     left join bd_psndoc t3 on t3.pk_psndoc=t1.pk_psndoc --人员基本信息
     left join (select concat(cyear,concat('-',cperiod)) qj,f_1 sb_js,f_5 sb_jf,pk_psndoc from bm_data where  pk_bm_class ='10011T100000000DMIO5') t4 on t4.qj=t2.qj and t4.pk_psndoc=t1.pk_psndoc --社保缴交-住房公积金
     left join org_orgs a1 on a1.pk_org=t1.pk_org  --发薪组织
     left join org_orgs a2 on a2.pk_org=t1.workorg --薪资档案任职组织
     left join wa_waclass a3 on a3.pk_wa_class=t1.pk_wa_class --薪资方案
     left join bd_defdoc a4 on a4.pk_defdoc=t3.glbdef2 --籍贯
where a3.name not like '%年终奖%' 

-- t_2  上月发薪-新增
select 
t1.pk_psndoc,
a1.name yorg_name,
a2.name yorg_rz_name,
concat(t1.cyear,concat('-',t1.cperiod)) sj_date,
substr(datefmt(dateadd('mm',1,todate(concat(concat(t1.cyear,'-'),concat(concat(t1.cperiod,'-'),'01')))),'YYYY-MM-DD'),1,7) zj_date
from wa_data t1
     left join org_orgs a1 on a1.pk_org=t1.pk_org  --发薪组织
     left join org_orgs a2 on a2.pk_org=t1.workorg --薪资档案任职组织
     left join wa_waclass a3 on a3.pk_wa_class=t1.pk_wa_class --薪资方案
where a3.name not like '%年终奖%'

-- t_3 上月发薪-组织
select 
t1.pk_psndoc,
a1.name yorg_name,
a2.name yorg_rz_name,
concat(t1.cyear,concat('-',t1.cperiod)) sj_date,
substr(datefmt(dateadd('mm',1,todate(concat(concat(t1.cyear,'-'),concat(concat(t1.cperiod,'-'),'01')))),'YYYY-MM-DD'),1,7) zj_date
from wa_data t1
     left join org_orgs a1 on a1.pk_org=t1.pk_org  --发薪组织
     left join org_orgs a2 on a2.pk_org=t1.workorg --薪资档案任职组织
     left join wa_waclass a3 on a3.pk_wa_class=t1.pk_wa_class --薪资方案
where a3.name not like '%年终奖%'
-- 连接条件
-- t_1.ORG_NAME=t_2.YORG_NAME and t_1.QJ=t_2.ZJ_DATE and t_1.PK_PSNDOC=t_2.PK_PSNDOC
-- t_1.PK_PSNDOC=t_3.PK_PSNDOC and t_1.QJ=t_3.ZJ_DATE

-- 减员
-- MZ301_02 MZ301_02公积金缴纳表2
-- t_1 上月发薪
select 
  a3.name xzfa_name, --薪资方案名称
  substr(datefmt(dateadd('mm',1,todate(concat(concat(t1.cyear,'-'),concat(concat(t1.cperiod,'-'),'01')))),'YYYY-MM-DD'),1,7) qj,  --薪资期间
  a1.name org_name, --发薪组织名称
  t1.pk_org pk_org, --发薪组织pk
  t1.pk_group pk_group,--发薪组织所属集团pk
  a2.name org_rzname, --任职组织名称
  t3.name ry_name, --人员姓名
  t3.id ry_id,  --身份证
  a4.name ry_jg, --籍贯
  t3.mobile ry_dh,  -- 电话
  t3.pk_psndoc pk_psndoc,  --人员主键
  null sb_js, --社保基数
  null sb_jf --社保缴费
from           wa_data t1  --薪资档案/薪资发放
     inner join (select distinct concat(cyear,concat('-',cperiod)) qj from wa_period where dr='0') t2 on t2.qj=concat(t1.cyear,concat('-',t1.cperiod))  --薪资期间
     left join bd_psndoc t3 on t3.pk_psndoc=t1.pk_psndoc --人员基本信息
     left join org_orgs a1 on a1.pk_org=t1.pk_org  --发薪组织
     left join org_orgs a2 on a2.pk_org=t1.workorg --薪资档案任职组织
     left join wa_waclass a3 on a3.pk_wa_class=t1.pk_wa_class --薪资方案
     left join bd_defdoc a4 on a4.pk_defdoc=t3.glbdef2 --籍贯
where a3.name not like '%年终奖%' --and a1.name='集团总部' 
--and substr(datefmt(dateadd('mm',1,todate(concat(concat(t1.cyear,'-'),concat(concat(t1.cperiod,'-'),'01')))),'YYYY-MM-DD'),1,7) in('2025-01','2024-12')

-- t_2 实际发薪
select 
t1.pk_psndoc,
a1.name org_name,
a2.name org_rz_name,
concat(t1.cyear,concat('-',t1.cperiod)) sj_date
from wa_data t1
     left join org_orgs a1 on a1.pk_org=t1.pk_org  --发薪组织
     left join org_orgs a2 on a2.pk_org=t1.workorg --薪资档案任职组织
     left join wa_waclass a3 on a3.pk_wa_class=t1.pk_wa_class --薪资方案
where a3.name not like '%年终奖%'
-- 连接条件
-- t_1.QJ=t_2.SJ_DATE and t_1.PK_PSNDOC=t_2.PK_PSNDOC and t_1.ORG_NAME=t_2.ORG_NAME

-- 关联薪酬期间人员对应的任职日期与异动类型
-- MZ301_03 MZ301_03公积金缴纳表3
-- t_1 实际发薪_任职信息
select  a.*,b.rzks_date,b.rzjs_date,b.rzyd
from (select * from smart('MZ301_02') t1 union all
           select * from smart('MZ301_01') t2
          ) a
left join (select pk_psndoc,begindate rzks_date, 
                  casewhen( case when (enddate) is null then datefmt(date(),'YYYY-MM-DD') else enddate end ) rzjs_date,
                  casewhen( case when (trnsevent) = '1' then '入职' else '非入职' end ) rzyd 
          from hi_psnjob  where ismainjob='Y') b
on a.pk_psndoc=b.pk_psndoc and datefmt(concat(a.qj,'-01'),'YYYY-MM-DD')>=datefmt(b.rzks_date,'YYYY-MM-DD') 
and datefmt(concat(a.qj,'-01'),'YYYY-MM-DD')<=datefmt(b.rzjs_date,'YYYY-MM-DD') 

-- 申报金额（年度工资收入子集）
-- MZ301_04 MZ301_04公积金缴纳表4
-- t_1 表_1
select 
  t1.code ry_code, --人员编码
  t1.name ry_name,--姓名
  t1.pk_psndoc pk_psndoc, --人员主键
  t2.glbdef1 sr_ksdate, --年月标识
  t2.glbdef7 sr_je --申报金额
from      bd_psndoc t1  --人员基本信息
left join hi_psndoc_glbdef25 t2 on t2.pk_psndoc=t1.pk_psndoc --年度工资收入
where t1.dr='0'

-- MZ301_03语义模型与年度收入子集汇总，此报表未曾过滤掉一年有两行的情况。
-- MZ301_05 MZ301_05公积金缴纳表5
-- t_1 实际发薪
select 
t1.*,t2.sr_year,t2.sr_je,t2.sr_ksdate,
casewhen( case when t1.rzyd = '入职' and round(substr(t1.qj,1,4),0)-round(substr(t1.rzks_date,1,4),0)=0 and round(substr(t1.qj,1,4),0)=t2.sr_year   then t2.sr_year 
                          when t1.rzyd = '入职' and round(substr(t1.qj,1,4),0)-round(substr(t1.rzks_date,1,4),0)=1 and round(substr(t1.qj,1,4),0)-1=t2.sr_year   then t2.sr_year 
                          when t1.rzyd = '入职' and round(substr(t1.qj,1,4),0)-round(substr(t1.rzks_date,1,4),0)>1 and round(substr(t1.qj,6,7),0)<=6 and round(substr(t1.qj,1,4),0)-2=t2.sr_year
                                    then t2.sr_year
                          when t1.rzyd = '入职' and round(substr(t1.qj,1,4),0)-round(substr(t1.rzks_date,1,4),0)>1 and round(substr(t1.qj,6,7),0)>=7 and round(substr(t1.qj,1,4),0)-1=t2.sr_year
                                    then t2.sr_year
			  when t1.rzyd = '非入职' and round(substr(t1.qj,1,4),0)-substr((select min(n.begindate) zx from hi_psnjob n where n.ismainjob='Y' and n.pk_psndoc=t1.pk_psndoc group by n.pk_psndoc),1,4)=0 and round(substr(t1.qj,1,4),0)=t2.sr_year   then t2.sr_year
			  when t1.rzyd = '非入职' and round(substr(t1.qj,1,4),0)-substr((select min(n.begindate) zx from hi_psnjob n where n.ismainjob='Y' and n.pk_psndoc=t1.pk_psndoc group by n.pk_psndoc),1,4)=1 and round(substr(t1.qj,1,4),0)-1=t2.sr_year   then t2.sr_year
                          when t1.rzyd = '非入职' and round(substr(t1.qj,1,4),0)-substr((select min(n.begindate) zx from hi_psnjob n where n.ismainjob='Y' and n.pk_psndoc=t1.pk_psndoc group by n.pk_psndoc),1,4)>1 and round(substr(t1.qj,6,7),0)<=6 and round(substr(t1.qj,1,4),0)-2=t2.sr_year then t2.sr_year
                          when t1.rzyd = '非入职' and round(substr(t1.qj,1,4),0)-substr((select min(n.begindate) zx from hi_psnjob n where n.ismainjob='Y' and n.pk_psndoc=t1.pk_psndoc group by n.pk_psndoc),1,4)>1 and round(substr(t1.qj,6,7),0)>=7 and round(substr(t1.qj,1,4),0)-1=t2.sr_year then t2.sr_year
else 0 end ) gl
from smart('MZ301_03') t1
left join smart('MZ301_04') t2
on  t1.pk_psndoc=t2.pk_psndoc

MZ301 MZ301公积金缴纳表
-- t_1
select t1.* from smart('MZ301_05') t1 where round(substr(t1.qj,1,4),0)-round(substr(t1.rzks_date,1,4),0)=0 and round(substr(t1.qj,6,7),0)<=06 and 
t1.sr_ksdate=(select min(m.sr_ksdate) zx from smart('MZ301_05') m where round(substr(t1.qj,6,7),0)<=06 and t1.qj=m.qj and t1.pk_psndoc=m.pk_psndoc group by m.pk_psndoc,m.qj)
union
select t1.* from smart('MZ301_05') t1 where round(substr(t1.qj,1,4),0)-round(substr(t1.rzks_date,1,4),0)=0 and round(substr(t1.qj,6,7),0)>=07 and
t1.sr_ksdate=(select max(m.sr_ksdate) zx from smart('MZ301_05') m where round(substr(t1.qj,6,7),0)>=07 and t1.qj=m.qj and t1.pk_psndoc=m.pk_psndoc group by m.pk_psndoc,m.qj)
union
select t1.* from smart('MZ301_05') t1 where round(substr(t1.qj,1,4),0)-round(substr(t1.rzks_date,1,4),0)>=1 and 
t1.sr_ksdate=(select max(m.sr_ksdate) zx from smart('MZ301_05') m where t1.qj=m.qj and t1.pk_psndoc=m.pk_psndoc group by m.pk_psndoc,m.qj)