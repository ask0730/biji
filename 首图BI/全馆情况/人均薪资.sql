select 
    cyear 当前年度,
    concat(cyear, cperiod) 当前月度,
    count(distinct wa_data.pk_psndoc) 人数,
    avg(f_21) 人均岗位薪资,
    avg(f_22) 人均薪资,
    avg(f_48) 人均综合补贴,
    avg(f_55) 人均住房补贴,
    sum(f_21) 总岗位薪资,
    sum(f_22) 总薪资,
    sum(f_48) 总综合补贴,
    sum(f_55) 总住房补贴
from wa_data 
inner join bd_psndoc 
on wa_data.pk_psndoc = bd_psndoc.pk_psndoc 
inner join hi_psnjob 
on wa_data.pk_psnjob = hi_psnjob.pk_psnjob 
left outer join org_orgs_v 
on wa_data.WORKORGVID = org_orgs_v.PK_VID 
LEFT OUTER JOIN org_dept_v 
ON wa_data.WORKDEPTVID = org_dept_v.PK_VID 
left outer join om_job 
on hi_psnjob.pk_job = om_job.pk_job
left outer join om_post 
on hi_psnjob.pk_post = om_post.pk_post 
left outer join bd_psncl 
on hi_psnjob.pk_psncl = bd_psncl.pk_psncl 
where wa_data.pk_wa_class = '1001A110000000009V0P' 
and wa_data.stopflag = 'N' 
and wa_data.pk_wa_data in 
( select pk_wa_data from wa_data where wa_data.pk_wa_class = '1001A110000000009V0P' 
  and wa_data.stopflag = 'N' ) 
and wa_data.dr = 0
group by cyear, cperiod
order by cyear desc, cperiod desc
