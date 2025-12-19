select
t4.qj ,a2.name org_orgs,a1.name faname,
t2.code rycode,t2.name ryname,a3.name,
t1.dr,a4.name grsf,t2.id,t5.NSRBZ ,
a5.name cwfysx,t1.CPAYDATE ff_date,a7.name cw_zzlx,
t1.c_66 xz_cwzysj,t1.f_69 f_69,a1.ts fa_ts,t1.ts da_ts,t3.jobglbdef25,
a8.name org_ns_name
from wa_data t1 --薪资档案/薪资发放
left join bd_psndoc t2 on t2.pk_psndoc=t1.pk_psndoc --人员基本信息
outer apply (
    SELECT TOP 1
        jobglbdef25,
        jobglbdef15
    FROM hi_psnjob
    WHERE pk_psndoc = t2.pk_psndoc
      AND lastflag = 'Y'
      AND ismainjob = 'Y'
    ORDER BY begindate DESC, ts DESC
) t3 --人员最新任职记录
inner  join (select distinct CAST(cyear AS VARCHAR)+'-'+CAST(cperiod AS VARCHAR) qj from wa_period where dr='0') t4 on t4.qj=CAST(t1.cyear AS VARCHAR)+'-'+CAST(t1.cperiod AS VARCHAR)  --薪资期间
left join view_NSRJCXX t5 on t2.id=t5.ZZHM and CAST(t1.CYEAR AS VARCHAR)+'-'+CAST(t1.CPERIOD AS VARCHAR)=SUBSTRING(t5.SDYF,1,7) --报税日志表
left join wa_waclass a1 on a1.pk_wa_class=t1.pk_wa_class --薪资方案
left join  org_orgs a2 on a2.pk_org=t1.pk_org --薪资所属组织
left join org_financeorg a3 on a3.pk_financeorg=t1.pk_financeorg --财务组织
left join bd_defdoc a4 on t2.penelauth=a4.pk_defdoc --个人身份
left join bd_defdoc a5 on t3.jobglbdef15=a5.pk_defdoc --财务费用属性
left join org_orgs a6 on a3.name=a6.name and a6.ISBUSINESSUNIT='Y'--获取财务组织的组织类型主键
left join bd_defdoc  a7 on a6.def2=a7.pk_defdoc  --财务组织类型
left join org_orgs a8 on t1.taxdeclareorg=a8.pk_org  and a6.ISBUSINESSUNIT='Y' --获取纳税申报组织
where t1.dr='0'