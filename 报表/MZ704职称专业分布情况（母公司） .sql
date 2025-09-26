-- t_2
select 
--总数
count(a.wxg) wxg
,count(a.kfy) kfy
,count(a.yxg) yxg
,count(a.zyxg) zyxg
,count(a.ccg) ccg
,count(a.czg)czg
,count(a.hg) hg
,count(a.dg) dg


from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '燃气具安装维修工'  then 1 end wxg
,case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '管道燃气客服员'  then 1 end kfy
,case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '燃气管网运行工'  then 1 end yxg
,case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '压缩天然气场站运行工'  then 1 end zyxg
,case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '液化天然气储运工'  then 1 end ccg
,case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '压缩机操作工'  then 1 end czg
,case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '焊工'  then 1 end hg
,case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '高压电工'  then 1 end dg



from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef7.name='已聘任该项技能等级'--是否聘任专业技术职务为'已聘任该项专业技术职务'
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构')
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
order by T1.showorder
)a


-- t_3
select 
--总数
count(a.wxg) wxg2
,count(a.kfy) kfy2
,count(a.yxg) yxg2
,count(a.zyxg) zyxg2
,count(a.ccg) ccg2
,count(a.czg) czg2
,count(a.hg) hg2
,count(a.dg) dg2


from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '燃气具安装维修工'  then 1 end wxg
,case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '管道燃气客服员'  then 1 end kfy
,case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '燃气管网运行工'  then 1 end yxg
,case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '压缩天然气场站运行工'  then 1 end zyxg
,case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '液化天然气储运工'  then 1 end ccg
,case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '压缩机操作工'  then 1 end czg
,case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '焊工'  then 1 end hg
,case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '高压电工'  then 1 end dg



from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef7.name='已聘任该项技能等级'--是否聘任专业技术职务为'已聘任该项专业技术职务'
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构')
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
order by T1.showorder
)a


-- t_4
select 
--总数
count(a.wxg) wxg3
,count(a.kfy) kfy3
,count(a.yxg) yxg3
,count(a.zyxg) zyxg3
,count(a.ccg) ccg3
,count(a.czg) czg3
,count(a.hg) hg3
,count(a.dg) dg3


from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '燃气具安装维修工'  then 1 end wxg
,case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '管道燃气客服员'  then 1 end kfy
,case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '燃气管网运行工'  then 1 end yxg
,case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '压缩天然气场站运行工'  then 1 end zyxg
,case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '液化天然气储运工'  then 1 end ccg
,case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '压缩机操作工'  then 1 end czg
,case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '焊工'  then 1 end hg
,case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '高压电工'  then 1 end dg


from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef7.name='已聘任该项技能等级'--是否聘任专业技术职务为'已聘任该项专业技术职务'
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构')
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
order by T1.showorder
)a










-- t_5
select 
--总数
count(a.wxg) wxg4
,count(a.kfy) kfy4
,count(a.yxg) yxg4
,count(a.zyxg) zyxg4
,count(a.ccg) ccg4
,count(a.czg) czg4
,count(a.hg) hg4
,count(a.dg) dg4


from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '燃气具安装维修工'  then 1 end wxg
,case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '管道燃气客服员'  then 1 end kfy
,case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '燃气管网运行工'  then 1 end yxg
,case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '压缩天然气场站运行工'  then 1 end zyxg
,case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '液化天然气储运工'  then 1 end ccg
,case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '压缩机操作工'  then 1 end czg
,case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '焊工'  then 1 end hg
,case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '高压电工'  then 1 end dg


from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef7.name='已聘任该项技能等级'--是否聘任专业技术职务为'已聘任该项专业技术职务'
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构')
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
order by T1.showorder
)a


-- t_6
select 
--总数
count(a.wxg) wxg5
,count(a.kfy) kfy5
,count(a.yxg) yxg5
,count(a.zyxg) zyxg5
,count(a.ccg) ccg5
,count(a.czg) czg5
,count(a.hg) hg5
,count(a.dg) dg5


from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '燃气具安装维修工'  then 1 end wxg
,case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '管道燃气客服员'  then 1 end kfy
,case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '燃气管网运行工'  then 1 end yxg
,case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '压缩天然气场站运行工'  then 1 end zyxg
,case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '液化天然气储运工'  then 1 end ccg
,case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '压缩机操作工'  then 1 end czg
,case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '焊工'  then 1 end hg
,case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '高压电工'  then 1 end dg


from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef7.name='已聘任该项技能等级'--是否聘任专业技术职务为'已聘任该项专业技术职务'
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构')
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
order by T1.showorder
)a







-- t_8
select 
--总数
count(a.wzg) wzg7
from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef1.name = '没有取得资格证书'  then 1 end wzg
from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef7.name='已聘任该项技能等级'--是否聘任专业技术职务为'已聘任该项专业技术职务'
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构')
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
order by T1.showorder
)a