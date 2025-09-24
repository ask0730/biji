-- MZ704职称专业分布情况（全集团）- 合并查询
select 
-- 总数（排除未评定专业技术职务）
count(case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '燃气具安装维修工' then 1 end) wxg,
count(case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '管道燃气客服员' then 1 end) kfy,
count(case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '燃气管网运行工' then 1 end) yxg,
count(case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '压缩天然气场站运行工' then 1 end) zyxg,
count(case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '液化天然气储运工' then 1 end) ccg,
count(case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '压缩机操作工' then 1 end) czg,
count(case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '焊工' then 1 end) hg,
count(case when T3.glbdef1.name<>'没有取得资格证书' and T3.glbdef3 = '高压电工' then 1 end) dg,

-- 高级技师（一级）
count(case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '燃气具安装维修工' then 1 end) wxg2,
count(case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '管道燃气客服员' then 1 end) kfy2,
count(case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '燃气管网运行工' then 1 end) yxg2,
count(case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '压缩天然气场站运行工' then 1 end) zyxg2,
count(case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '液化天然气储运工' then 1 end) ccg2,
count(case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '压缩机操作工' then 1 end) czg2,
count(case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '焊工' then 1 end) hg2,
count(case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef3 = '高压电工' then 1 end) dg2,

-- 技师（二级）
count(case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '燃气具安装维修工' then 1 end) wxg3,
count(case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '管道燃气客服员' then 1 end) kfy3,
count(case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '燃气管网运行工' then 1 end) yxg3,
count(case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '压缩天然气场站运行工' then 1 end) zyxg3,
count(case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '液化天然气储运工' then 1 end) ccg3,
count(case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '压缩机操作工' then 1 end) czg3,
count(case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '焊工' then 1 end) hg3,
count(case when T3.glbdef1.name = '技师（二级）' and T3.glbdef3 = '高压电工' then 1 end) dg3,

-- 高级工（三级）
count(case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '燃气具安装维修工' then 1 end) wxg4,
count(case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '管道燃气客服员' then 1 end) kfy4,
count(case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '燃气管网运行工' then 1 end) yxg4,
count(case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '压缩天然气场站运行工' then 1 end) zyxg4,
count(case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '液化天然气储运工' then 1 end) ccg4,
count(case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '压缩机操作工' then 1 end) czg4,
count(case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '焊工' then 1 end) hg4,
count(case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef3 = '高压电工' then 1 end) dg4,

-- 中级工（四级）
count(case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '燃气具安装维修工' then 1 end) wxg5,
count(case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '管道燃气客服员' then 1 end) kfy5,
count(case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '燃气管网运行工' then 1 end) yxg5,
count(case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '压缩天然气场站运行工' then 1 end) zyxg5,
count(case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '液化天然气储运工' then 1 end) ccg5,
count(case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '压缩机操作工' then 1 end) czg5,
count(case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '焊工' then 1 end) hg5,
count(case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef3 = '高压电工' then 1 end) dg5,

-- 初级工（五级）
count(case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef3 = '燃气具安装维修工' then 1 end) wxg6,
count(case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef3 = '管道燃气客服员' then 1 end) kfy6,
count(case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef3 = '燃气管网运行工' then 1 end) yxg6,
count(case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef3 = '压缩天然气场站运行工' then 1 end) zyxg6,
count(case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef3 = '液化天然气储运工' then 1 end) ccg6,
count(case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef3 = '压缩机操作工' then 1 end) czg6,
count(case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef3 = '焊工' then 1 end) hg6,
count(case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef3 = '高压电工' then 1 end) dg6,

-- 没有取得资格证书
count(case when T3.glbdef1.name = '没有取得资格证书' then 1 end) wzg7

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
where 1 = 1 
-- and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 )  -- 人员档案标识为有效，人员类型为正式员工 
-- and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef7.name='已聘任该项技能等级'--是否聘任专业技术职务为'已聘任该项专业技术职务'
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部','子公司','子公司下属分公司','子公司下属子公司')
order by T1.showorder