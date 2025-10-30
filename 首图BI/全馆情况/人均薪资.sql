select bd_psndoc.name,bd_psndoc.code,cyear 当前年度,concat(cyear,cperiod) 当前月度,
f_1 ,
(f_21) gwmoney
,(f_22) xjmoney
,(f_48) zhbzmoney
,(f_55) zfbtmoney
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
