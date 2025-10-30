select om_job.jobname as 职称, COUNT(*) as 人数
from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psndoc_edu hi_psndoc_edu
ON hi_psndoc_edu.pk_psndoc = bd_psndoc.pk_psndoc and  hi_psndoc_edu.lasteducation = 'Y'
inner join om_job om_job 
on t1.pk_job = om_job.pk_job
left outer join org_adminorg org_adminorg 
on org_adminorg.pk_adminorg = T1.pk_org 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
where 1 = 1 
   and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 
   and hi_psnorg.ENDFLAG = 'N' ) 

   and ( 1 = 1 and T1.pk_org in ( select org_adminorg.pk_adminorg from org_adminorg where org_adminorg.enablestate = 2 and org_adminorg.innercode like ( select innercode || '%' from org_adminorg where pk_adminorg = '0001A110000000002SJP' ) and org_adminorg.pk_adminorg not in ( select aosm.pk_adminorg from ( select aos.code, aos.innercode, length ( rtrim( aos.innercode,' ') ) innercodelen from org_hrorg hrorg inner join org_adminorg aos on aos.pk_adminorg = hrorg.pk_hrorg where aos.innercode like ( select innercode || '%' from org_adminorg where pk_adminorg = '0001A110000000002SJP' ) and aos.pk_adminorg <> '0001A110000000002SJP' and hrorg.enablestate = 2 ) sub_hrorg, org_adminorg aosm where sub_hrorg.innercode = substr ( aosm.innercode, 1, sub_hrorg.innercodelen ) ) and org_adminorg.pk_adminorg in ( select pk_adminorg from org_admin_enable ) ) ) and ( T1.pk_psnjob in ( select pk_psnjob from hi_psnjob inner join ( select min ( recordnum ) over ( partition by pk_psnorg, pk_org ) recordmin, recordnum, pk_psnorg, pk_org from hi_psnjob where ismainjob = 'Y' ) temp on hi_psnjob.recordnum = temp.recordnum and hi_psnjob.pk_psnorg = temp.pk_psnorg and temp.recordmin = temp.recordnum and hi_psnjob.ismainjob = 'Y' union select pk_psnjob from hi_psnjob where ismainjob = 'N' and endflag = 'N' ) ) and ( T1.endflag = 'N' ) and T1.pk_org in ( select pk_adminorg from org_admin_enable ) 
group by om_job.jobname
order by COUNT(*) DESC
