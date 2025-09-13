-- MZ701生产技能人员结构报表 - 合并版
-- 统计不同技能等级人员数量及基本信息
select 
    -- 技能等级统计
    count(case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end) as cjg,  -- 初级工
    count(case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end) as zjg,  -- 中级工
    count(case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end) as gjg,  -- 高级工
    count(case when T3.glbdef1.name = '技师（二级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end) as js,   -- 技师
    count(case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end) as gjjs, -- 高级技师
    count(case when T3.glbdef1.name = '没有取得资格证书' and T3.glbdef7.name='未聘任该项技能等级' then 1 else null end) as wdj, -- 无等级
    
    -- 人员基本信息统计
    count(distinct bd_psndoc.code) as rybm,  -- 人员编码总数
    count(case when bd_defdoc_mz.name = '汉族' then 1 else null end) as hz,     -- 汉族
    count(case when bd_defdoc_mz.name <> '汉族' then 1 else null end) as bshz, -- 非汉族
    count(case when bd_psndoc.sex = 1 then 1 else null end) as nan,            -- 男性
    count(case when bd_psndoc.sex = 2 then 1 else null end) as nv,             -- 女性
    count(case when bd_defdoc_zzmm.name = '中共党员' then 1 else null end) as zgdy, -- 中共党员
    
    -- 年龄分布统计
    count(case when bd_psndoc.age <= 30 then 1 else null end) as n1,  -- 30岁以下
    count(case when bd_psndoc.age >= 31 and bd_psndoc.age <= 35 then 1 else null end) as n2,  -- 31-35岁
    count(case when bd_psndoc.age >= 36 and bd_psndoc.age <= 40 then 1 else null end) as n3,  -- 36-40岁
    count(case when bd_psndoc.age >= 41 and bd_psndoc.age <= 45 then 1 else null end) as n4,  -- 41-45岁
    count(case when bd_psndoc.age >= 46 and bd_psndoc.age <= 50 then 1 else null end) as n5,  -- 46-50岁
    count(case when bd_psndoc.age >= 51 and bd_psndoc.age <= 55 then 1 else null end) as n6,  -- 51-55岁
    count(case when bd_psndoc.age >= 56 then 1 else null end) as n7,  -- 56岁以上
    
    -- 学历分布统计
    count(case when bd_psndoc.edu.code in ('4','41','42','48','49','5','51','59','6','61','62','68','69','7','71','72','73','78','79','8','81','88','89','99','9') then 1 else null end) as gzjyx, -- 高中及以下
    count(case when bd_psndoc.edu.code in ('3','31','38','39') then 1 else null end) as dxzk,  -- 大学专科
    count(case when bd_psndoc.edu.code in ('2','21','28','29') then 1 else null end) as dxbk,  -- 大学本科
    count(case when bd_psndoc.edu.code in ('1','14','15','16','17','18','19') then 1 else null end) as ss,  -- 硕士
    count(case when bd_psndoc.edu.code in ('0','11','12','13') then 1 else null end) as bs     -- 博士

from bd_psndoc bd_psndoc -- 1.人员基本信息

inner join hi_psnorg hi_psnorg -- 2.组织关系表
    on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 -- 3.人员工作记录表
    ON T1.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join org_orgs org_orgs -- 4.组织
    on org_orgs.pk_org = T1.pk_org 

left outer join org_dept org_dept -- 5.部门
    on org_dept.pk_dept = T1.pk_dept 

left outer join org_adminorg -- 行政组织
    on T1.pk_org = org_adminorg.pk_adminorg

left outer join bd_psncl -- 人员类别
    on T1.pk_psncl = bd_psncl.pk_psncl

-- 民族
left outer join bd_defdoc bd_defdoc_mz
    on bd_psndoc.nationality = bd_defdoc_mz.pk_defdoc

-- 政治面貌
left outer join bd_defdoc bd_defdoc_zzmm
    on bd_psndoc.polity = bd_defdoc_zzmm.pk_defdoc

-- 已聘任工人技能等级
left outer join hi_psndoc_glbdef2 T3 
    ON T3.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join bd_defdoc bd_defdoc_zzlx -- 组织类型
    on org_adminorg.def2 = bd_defdoc_zzlx.pk_defdoc

where 1 = 1 
    -- AND org_adminorg.name = '高压管网分公司'
    and (hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0) 
    and t1.endflag = 'N' 
    and t1.lastflag = 'Y' 
    and t1.ismainjob = 'Y'
    and T1.pk_postseries in ('10011T100000000098AS', '10011T100000000098B2', '10011T100000000098B3', '10011T100000000098B4', '10011T100000000098B5', '10011T100000000098B6')
    and T1.begindate <= datefmt(parameter('param2'), 'yyyy-mm-dd') 
    and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and bd_psncl.name in (parameter('rylb')) 