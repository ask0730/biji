-- MZ704职称专业分布情况（全集团）- 修复版本（解决一人多岗问题）
select 
-- 总数（排除未评定专业技术职务）
count(distinct case when T3.glbdef1.name<>'没有取得资格证书' and bd_defdoc_glbdef6.name = '燃气具安装维修工' then bd_psndoc.pk_psndoc end) wxg,
count(distinct case when T3.glbdef1.name<>'没有取得资格证书' and bd_defdoc_glbdef6.name = '管道燃气客服员' then bd_psndoc.pk_psndoc end) kfy,
count(distinct case when T3.glbdef1.name<>'没有取得资格证书' and bd_defdoc_glbdef6.name = '燃气管网运行工' then bd_psndoc.pk_psndoc end) yxg,
count(distinct case when T3.glbdef1.name<>'没有取得资格证书' and bd_defdoc_glbdef6.name = '压缩天然气场站运行工' then bd_psndoc.pk_psndoc end) zyxg,
count(distinct case when T3.glbdef1.name<>'没有取得资格证书' and bd_defdoc_glbdef6.name = '液化天然气储运工' then bd_psndoc.pk_psndoc end) ccg,
count(distinct case when T3.glbdef1.name<>'没有取得资格证书' and bd_defdoc_glbdef6.name = '压缩机操作工' then bd_psndoc.pk_psndoc end) czg,
count(distinct case when T3.glbdef1.name<>'没有取得资格证书' and bd_defdoc_glbdef6.name = '焊工' then bd_psndoc.pk_psndoc end) hg,
count(distinct case when T3.glbdef1.name<>'没有取得资格证书' and bd_defdoc_glbdef6.name = '高压电工' then bd_psndoc.pk_psndoc end) dg,

-- 高级技师（一级）
count(distinct case when T3.glbdef1.name = '高级技师（一级）' and bd_defdoc_glbdef6.name = '燃气具安装维修工' then bd_psndoc.pk_psndoc end) wxg2,
count(distinct case when T3.glbdef1.name = '高级技师（一级）' and bd_defdoc_glbdef6.name = '管道燃气客服员' then bd_psndoc.pk_psndoc end) kfy2,
count(distinct case when T3.glbdef1.name = '高级技师（一级）' and bd_defdoc_glbdef6.name = '燃气管网运行工' then bd_psndoc.pk_psndoc end) yxg2,
count(distinct case when T3.glbdef1.name = '高级技师（一级）' and bd_defdoc_glbdef6.name = '压缩天然气场站运行工' then bd_psndoc.pk_psndoc end) zyxg2,
count(distinct case when T3.glbdef1.name = '高级技师（一级）' and bd_defdoc_glbdef6.name = '液化天然气储运工' then bd_psndoc.pk_psndoc end) ccg2,
count(distinct case when T3.glbdef1.name = '高级技师（一级）' and bd_defdoc_glbdef6.name = '压缩机操作工' then bd_psndoc.pk_psndoc end) czg2,
count(distinct case when T3.glbdef1.name = '高级技师（一级）' and bd_defdoc_glbdef6.name = '焊工' then bd_psndoc.pk_psndoc end) hg2,
count(distinct case when T3.glbdef1.name = '高级技师（一级）' and bd_defdoc_glbdef6.name = '高压电工' then bd_psndoc.pk_psndoc end) dg2,

-- 技师（二级）
count(distinct case when T3.glbdef1.name = '技师（二级）' and bd_defdoc_glbdef6.name = '燃气具安装维修工' then bd_psndoc.pk_psndoc end) wxg3,
count(distinct case when T3.glbdef1.name = '技师（二级）' and bd_defdoc_glbdef6.name = '管道燃气客服员' then bd_psndoc.pk_psndoc end) kfy3,
count(distinct case when T3.glbdef1.name = '技师（二级）' and bd_defdoc_glbdef6.name = '燃气管网运行工' then bd_psndoc.pk_psndoc end) yxg3,
count(distinct case when T3.glbdef1.name = '技师（二级）' and bd_defdoc_glbdef6.name = '压缩天然气场站运行工' then bd_psndoc.pk_psndoc end) zyxg3,
count(distinct case when T3.glbdef1.name = '技师（二级）' and bd_defdoc_glbdef6.name = '液化天然气储运工' then bd_psndoc.pk_psndoc end) ccg3,
count(distinct case when T3.glbdef1.name = '技师（二级）' and bd_defdoc_glbdef6.name = '压缩机操作工' then bd_psndoc.pk_psndoc end) czg3,
count(distinct case when T3.glbdef1.name = '技师（二级）' and bd_defdoc_glbdef6.name = '焊工' then bd_psndoc.pk_psndoc end) hg3,
count(distinct case when T3.glbdef1.name = '技师（二级）' and bd_defdoc_glbdef6.name = '高压电工' then bd_psndoc.pk_psndoc end) dg3,

-- 高级工（三级）
count(distinct case when T3.glbdef1.name = '高级工（三级）' and bd_defdoc_glbdef6.name = '燃气具安装维修工' then bd_psndoc.pk_psndoc end) wxg4,
count(distinct case when T3.glbdef1.name = '高级工（三级）' and bd_defdoc_glbdef6.name = '管道燃气客服员' then bd_psndoc.pk_psndoc end) kfy4,
count(distinct case when T3.glbdef1.name = '高级工（三级）' and bd_defdoc_glbdef6.name = '燃气管网运行工' then bd_psndoc.pk_psndoc end) yxg4,
count(distinct case when T3.glbdef1.name = '高级工（三级）' and bd_defdoc_glbdef6.name = '压缩天然气场站运行工' then bd_psndoc.pk_psndoc end) zyxg4,
count(distinct case when T3.glbdef1.name = '高级工（三级）' and bd_defdoc_glbdef6.name = '液化天然气储运工' then bd_psndoc.pk_psndoc end) ccg4,
count(distinct case when T3.glbdef1.name = '高级工（三级）' and bd_defdoc_glbdef6.name = '压缩机操作工' then bd_psndoc.pk_psndoc end) czg4,
count(distinct case when T3.glbdef1.name = '高级工（三级）' and bd_defdoc_glbdef6.name = '焊工' then bd_psndoc.pk_psndoc end) hg4,
count(distinct case when T3.glbdef1.name = '高级工（三级）' and bd_defdoc_glbdef6.name = '高压电工' then bd_psndoc.pk_psndoc end) dg4,

-- 中级工（四级）
count(distinct case when T3.glbdef1.name = '中级工（四级）' and bd_defdoc_glbdef6.name = '燃气具安装维修工' then bd_psndoc.pk_psndoc end) wxg5,
count(distinct case when T3.glbdef1.name = '中级工（四级）' and bd_defdoc_glbdef6.name = '管道燃气客服员' then bd_psndoc.pk_psndoc end) kfy5,
count(distinct case when T3.glbdef1.name = '中级工（四级）' and bd_defdoc_glbdef6.name = '燃气管网运行工' then bd_psndoc.pk_psndoc end) yxg5,
count(distinct case when T3.glbdef1.name = '中级工（四级）' and bd_defdoc_glbdef6.name = '压缩天然气场站运行工' then bd_psndoc.pk_psndoc end) zyxg5,
count(distinct case when T3.glbdef1.name = '中级工（四级）' and bd_defdoc_glbdef6.name = '液化天然气储运工' then bd_psndoc.pk_psndoc end) ccg5,
count(distinct case when T3.glbdef1.name = '中级工（四级）' and bd_defdoc_glbdef6.name = '压缩机操作工' then bd_psndoc.pk_psndoc end) czg5,
count(distinct case when T3.glbdef1.name = '中级工（四级）' and bd_defdoc_glbdef6.name = '焊工' then bd_psndoc.pk_psndoc end) hg5,
count(distinct case when T3.glbdef1.name = '中级工（四级）' and bd_defdoc_glbdef6.name = '高压电工' then bd_psndoc.pk_psndoc end) dg5,

-- 初级工（五级）
count(distinct case when T3.glbdef1.name = '初级工（五级）' and bd_defdoc_glbdef6.name = '燃气具安装维修工' then bd_psndoc.pk_psndoc end) wxg6,
count(distinct case when T3.glbdef1.name = '初级工（五级）' and bd_defdoc_glbdef6.name = '管道燃气客服员' then bd_psndoc.pk_psndoc end) kfy6,
count(distinct case when T3.glbdef1.name = '初级工（五级）' and bd_defdoc_glbdef6.name = '燃气管网运行工' then bd_psndoc.pk_psndoc end) yxg6,
count(distinct case when T3.glbdef1.name = '初级工（五级）' and bd_defdoc_glbdef6.name = '压缩天然气场站运行工' then bd_psndoc.pk_psndoc end) zyxg6,
count(distinct case when T3.glbdef1.name = '初级工（五级）' and bd_defdoc_glbdef6.name = '液化天然气储运工' then bd_psndoc.pk_psndoc end) ccg6,
count(distinct case when T3.glbdef1.name = '初级工（五级）' and bd_defdoc_glbdef6.name = '压缩机操作工' then bd_psndoc.pk_psndoc end) czg6,
count(distinct case when T3.glbdef1.name = '初级工（五级）' and bd_defdoc_glbdef6.name = '焊工' then bd_psndoc.pk_psndoc end) hg6,
count(distinct case when T3.glbdef1.name = '初级工（五级）' and bd_defdoc_glbdef6.name = '高压电工' then bd_psndoc.pk_psndoc end) dg6,

-- 没有取得资格证书
count(distinct case when T3.glbdef1.name = '没有取得资格证书' then bd_psndoc.pk_psndoc end) wzg7

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
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
left outer join bd_defdoc bd_defdoc_glbdef6  --工种分类
on T3.glbdef6 = bd_defdoc_glbdef6.pk_defdoc
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef7.name='已聘任该项技能等级'--是否聘任专业技术职务为'已聘任该项专业技术职务'
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部','子公司','子公司下属分公司','子公司下属子公司')
order by T1.showorder