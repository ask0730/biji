select hi_psnjob.pk_psnjob ,bd_psndoc.code,bd_psndoc.name, 
bd_psndoc.age 年龄, bd_defdoc2 .name 学历,
case when hi_psndoc_edu.lasteducation = 'Y' then '最高学历' 
        when hi_psndoc_edu.lasteducation = 'N' then '非最高学历' end 学历类别,
hi_psndoc_edu.school 学校,
hi_psndoc_edu.lasteducation,
1 as 人数
from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psndoc_edu  hi_psndoc_edu
ON  hi_psndoc_edu.pk_psndoc = bd_psndoc.pk_psndoc 
inner join hi_psnjob hi_psnjob 
on hi_psnjob.pk_psnorg = hi_psnorg.pk_psnorg 
left outer join org_adminorg org_adminorg 
on org_adminorg.pk_adminorg = hi_psnjob.pk_org 
left outer join org_dept org_dept 
on org_dept.pk_dept = hi_psnjob.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = hi_psnjob.pk_psnjob 

  --学历面貌档案
 left join bd_defdoc bd_defdoc2 on hi_psndoc_edu.education = bd_defdoc2.pk_defdoc

where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 
and hi_psnorg.ENDFLAG = 'N' ) 
and  hi_psndoc_edu.lasteducation = 'Y'
and ( 1 = 1 and hi_psnjob.pk_org in ( select org_adminorg.pk_adminorg from org_adminorg where org_adminorg.enablestate = 2 and org_adminorg.innercode like ( select innercode || '%' from org_adminorg where pk_adminorg = '0001A110000000002SJP' ) and org_adminorg.pk_adminorg not in ( select aosm.pk_adminorg from ( select aos.code, aos.innercode, length ( rtrim( aos.innercode,' ') ) innercodelen from org_hrorg hrorg inner join org_adminorg aos on aos.pk_adminorg = hrorg.pk_hrorg where aos.innercode like ( select innercode || '%' from org_adminorg where pk_adminorg = '0001A110000000002SJP' ) and aos.pk_adminorg <> '0001A110000000002SJP' and hrorg.enablestate = 2 ) sub_hrorg, org_adminorg aosm where sub_hrorg.innercode = substr ( aosm.innercode, 1, sub_hrorg.innercodelen ) ) and org_adminorg.pk_adminorg in ( select pk_adminorg from org_admin_enable ) ) ) and ( hi_psnjob.pk_psnjob in ( select pk_psnjob from hi_psnjob where lastflag = 'Y' and ( ismainjob = 'Y' or ( hi_psnjob.ismainjob = 'N' and hi_psnjob.endflag = 'N' ) ) ) ) and ( hi_psnjob.endflag = 'N' ) and hi_psnjob.pk_org in ( select pk_adminorg from org_admin_enable ) order by hi_psnjob.showorder
