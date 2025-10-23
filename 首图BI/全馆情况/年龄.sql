select 
 hi_psnjob.pk_psnjob , bd_psndoc.name,bd_psndoc.age,
case when bd_psndoc.age between 0 and 30 then '三十岁以下'
        when bd_psndoc.age between 31 and 40 then '三十至四十岁'
        when bd_psndoc.age between 41 and 50 then '四十至五十岁'
        when bd_psndoc.age between 51 and 80 then '五十岁以上'
 end 年龄段,
1 as 人数
from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
inner join hi_psnjob hi_psnjob 
on hi_psnjob.pk_psnorg = hi_psnorg.pk_psnorg 
left outer join org_adminorg org_adminorg 
on org_adminorg.pk_adminorg = hi_psnjob.pk_org 
left outer join org_dept org_dept 
on org_dept.pk_dept = hi_psnjob.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = hi_psnjob.pk_psnjob 
where hi_psnjob.pk_psnjob <>'1001A110000000003YVT'
and ( 1 = 1 and hi_psnjob.pk_psnjob <>'1001A110000000003YVT' and hi_psnjob.pk_org in ( select org_adminorg.pk_adminorg from org_adminorg where org_adminorg.enablestate = 2 and org_adminorg.innercode like ( select innercode || '%' from org_adminorg where pk_adminorg = '0001A110000000002SJP' ) and org_adminorg.pk_adminorg not in ( select aosm.pk_adminorg from ( select aos.code, aos.innercode, length ( rtrim( aos.innercode,' ') ) innercodelen from org_hrorg hrorg inner join org_adminorg aos on aos.pk_adminorg = hrorg.pk_hrorg where aos.innercode like ( select innercode || '%' from org_adminorg where pk_adminorg = '0001A110000000002SJP' ) and aos.pk_adminorg <> '0001A110000000002SJP' and hrorg.enablestate = 2 ) sub_hrorg, org_adminorg aosm where sub_hrorg.innercode = substr ( aosm.innercode, 1, sub_hrorg.innercodelen ) ) and org_adminorg.pk_adminorg in ( select pk_adminorg from org_admin_enable ) ) ) and ( hi_psnjob.pk_psnjob in ( select pk_psnjob from hi_psnjob where lastflag = 'Y' and ( ismainjob = 'Y' or ( hi_psnjob.ismainjob = 'N' and hi_psnjob.endflag = 'N' ) ) ) ) and ( hi_psnjob.endflag = 'N' ) and hi_psnjob.pk_org in ( select pk_adminorg from org_admin_enable ) 
order by bd_psndoc.age


