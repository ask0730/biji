select  
pk_group,
pk_org,
t1.cyear||'-'||t1.cperiod qj,
t2.name,--人员姓名
t2.id, --证件号码
t2.birthdate, --出生日期
t2.age nl, --年龄
t2.glbdef13, --银行账号
t2.mobile, --手机号
t2.joinworkdate, --参加工作日期
round(t2.glbdef8,2) glbdef8,--总工龄
t3.jobglbdef4, --进入本企业时间
round(t3.jobglbdef7,2) jobglbdef7, --本企业总工龄
a1.name cw_name, --财务组织
a2.name rl_name,  --人力组织
a2.code rl_code, --人力组织编码 
a3.name bm_name, --部门
a4.postname gw_name, --岗位名称
case when substr(a5.postseriescode,1,2)='01' then '经营管理'
        when substr(a5.postseriescode,1,2)='02' then '专业技术'
        when substr(a5.postseriescode,1,2)='03' then '生产技能' else '其他' end gwxl_name, --岗位序列
a6.name lb_name,t3.pk_psncl, --人员类别
a7.name ht_gw_name , --合同信息的岗位工种
case when substr(a5.postseriescode,1,2) in (01,02)  and a7.name='管理岗' then  '否' 
        when substr(a5.postseriescode,1,2)=03 and a7.name='生产岗' then '否' else '是' end  cy ,--是否差异
a8.name xzfa_name, --薪资方案
t6.syjs_date syjs_date, --试用期结束日期
case when a6.name='试用期员工' then '否' 
        else '是' end sfsy --是否试用期满
from wa_data t1 --薪资档案/薪资发放
left join bd_psndoc t2 on t2.pk_psndoc=t1.pk_psndoc --人员基本信息
left join hi_psnjob t3 on t3.pk_psndoc=t2.pk_psndoc  --工作记录
inner  join (select distinct cyear||'-'||cperiod qj from wa_period where dr='0') t4 on t4.qj=t1.cyear||'-'||t1.cperiod  --薪资期间
left join (select * from hi_psndoc_ctrt where lastflag='Y') t5 on t5.pk_psndoc=t2.pk_psndoc  --合同信息
left join (select probegindate syks_date,probenddate syjs_date,pk_psndoc from hi_psndoc_ctrt where probegindate is not null and LASTFLAG='Y')  t6 on t6.pk_psndoc=t2.pk_psndoc --合同试用期
left join org_financeorg a1 on a1.pk_financeorg=t1.pk_financeorg --财务组织
left join org_hrorg a2 on a2.pk_hrorg=t3.pk_hrorg  --人力组织
left join org_dept a3 on a3.pk_dept=t3.pk_dept --HR部门信息
left join om_post a4 on a4.pk_post=t3.pk_post  --岗位信息
left join om_postseries a5 on a5.pk_postseries=t3.pk_postseries --岗位序列
left join bd_psncl a6 on a6.pk_psncl=t3.pk_psncl  --人员类别
left join bd_defdoc a7 on a7.pk_defdoc=t5.glbdef3 --合同信息的岗位工种
left join wa_waclass a8 on a8.pk_wa_class=t1.pk_wa_class --薪资方案 
left join org_orgs a9 on a9.name=a1.name --获取财务组织对应的业务单元，用于关联组织类型
left join bd_defdoc a10 on a10.pk_defdoc=a9.def2  --组织类型
where 
 t2.dr='0' 
and t3.dr='0'
and t1.dr='0'
and t3.ismainjob='Y' --是否主职
and t3.lastflag='Y'  --是否最新
and t3.endflag ='N'  --是否结束
and a8.name not like '%年终奖%'
and a10.name in ('总部','分公司','专业机构','事业部')
--and t4.qj='2024-08'
union
select  
t2.pk_group,
t2.pk_org,
t1.qj qj,
t2.name,--人员姓名
t2.id, --证件号码
t2.birthdate, --出生日期
t2.age nl, --年龄
t2.glbdef13, --银行账号
t2.mobile, --手机号
t2.joinworkdate, --参加工作日期
round(t2.glbdef8,2) glbdef8,--总工龄
t3.jobglbdef4, --进入本企业时间
round(t3.jobglbdef7,2) jobglbdef7, --本企业总工龄
'无发薪' cw_name, --财务组织
a2.name rl_name,  --人力组织
a2.code rl_code, --人力组织编码 
a3.name bm_name, --部门
a4.postname gw_name, --岗位名称
case when substr(a5.postseriescode,1,2)='01' then '经营管理'
        when substr(a5.postseriescode,1,2)='02' then '专业技术'
        when substr(a5.postseriescode,1,2)='03' then '生产技能' else '其他' end gwxl_name, --岗位序列
a6.name lb_name, t3.pk_psncl,--人员类别
a7.name ht_gw_name,  --合同信息的岗位工种
case when substr(a5.postseriescode,1,2) in (01,02)  and a7.name='管理岗' then  '否' 
        when substr(a5.postseriescode,1,2)=03 and a7.name='生产岗' then '否' else '是' end  cy,--是否差异
'无发薪' xzfa_name, --薪资方案
t6.syjs_date syjs_date, --试用期结束日期
case when a6.name='试用期员工' then '否' 
        else '是' end sfsy --是否试用期满
from (select distinct cyear||'-'||cperiod qj from wa_period where dr='0') t1 
left join bd_psndoc t2 on t1.qj=t1.qj  --人员基本信息
left join hi_psnjob t3 on t3.pk_psndoc=t2.pk_psndoc  --工作记录
left join (select * from hi_psndoc_ctrt where lastflag='Y') t5 on t5.pk_psndoc=t2.pk_psndoc  --合同信息
left join (select probegindate syks_date,probenddate syjs_date,pk_psndoc from hi_psndoc_ctrt where probegindate is not null and LASTFLAG='Y')  t6 on t6.pk_psndoc=t2.pk_psndoc --合同试用期
left join org_hrorg a2 on a2.pk_hrorg=t3.pk_hrorg  --人力组织
left join org_dept a3 on a3.pk_dept=t3.pk_dept --HR部门信息
left join om_post a4 on a4.pk_post=t3.pk_post  --岗位信息
left join om_postseries a5 on a5.pk_postseries=t3.pk_postseries --岗位序列
left join bd_psncl a6 on a6.pk_psncl=t3.pk_psncl  --人员类别
left join bd_defdoc a7 on a7.pk_defdoc=t5.glbdef3
where 
 t2.dr='0' 
and t3.dr='0'
and t3.ismainjob='Y' --是否主职
and t3.lastflag='Y'  --是否最新
and t3.poststat='Y' --是否在岗
and t3.endflag ='N'  --是否结束
and a2.name in ('中石油北京天然气管道有限公司','北控篮球俱乐部') and t2.name !='宗锋'