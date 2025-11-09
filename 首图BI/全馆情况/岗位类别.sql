select 
    hi_psnjob.pk_psnjob,
    bd_psndoc.code,
    bd_psndoc.name,
    bd_psndoc.age 年龄,
    coalesce(om_postseries.postseriesname, '无') 岗位类别,
    1 as 人数
from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
inner join hi_psnjob hi_psnjob 
on hi_psnjob.pk_psnorg = hi_psnorg.pk_psnorg 
left outer join om_post om_post
on om_post.pk_post = hi_psnjob.pk_post
left outer join om_postseries om_postseries
on om_postseries.pk_postseries = om_post.pk_postseries
left outer join org_adminorg org_adminorg 
on org_adminorg.pk_adminorg = hi_psnjob.pk_org 
left outer join org_dept org_dept 
on org_dept.pk_dept = hi_psnjob.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = hi_psnjob.pk_psnjob 
where 1 = 1 
    and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 
    and hi_psnorg.ENDFLAG = 'N' ) 
    and ( 1 = 1 and hi_psnjob.pk_org in ( select org_adminorg.pk_adminorg from org_adminorg where org_adminorg.enablestate = 2 and org_adminorg.innercode like ( select innercode || '%' from org_adminorg where pk_adminorg = '0001A110000000002SJP' ) and org_adminorg.pk_adminorg not in ( select aosm.pk_adminorg from ( select aos.code, aos.innercode, length ( rtrim( aos.innercode,' ') ) innercodelen from org_hrorg hrorg inner join org_adminorg aos on aos.pk_adminorg = hrorg.pk_hrorg where aos.innercode like ( select innercode || '%' from org_adminorg where pk_adminorg = '0001A110000000002SJP' ) and aos.pk_adminorg <> '0001A110000000002SJP' and hrorg.enablestate = 2 ) sub_hrorg, org_adminorg aosm where sub_hrorg.innercode = substr ( aosm.innercode, 1, sub_hrorg.innercodelen ) ) and org_adminorg.pk_adminorg in ( select pk_adminorg from org_admin_enable ) ) ) and ( hi_psnjob.pk_psnjob in ( select pk_psnjob from hi_psnjob where lastflag = 'Y' and ( ismainjob = 'Y' or ( hi_psnjob.ismainjob = 'N' and hi_psnjob.endflag = 'N' ) ) ) ) and ( hi_psnjob.endflag = 'N' ) and hi_psnjob.pk_org in ( select pk_adminorg from org_admin_enable ) 
order by hi_psnjob.showorder