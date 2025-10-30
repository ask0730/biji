-- MZ701生产技能人员结构报表
-- 统计不同技能等级人员数量及基本信息

-- MZ701_01 MZ701_01民族信息统计
-- t_1 民族统计
select 
    t1.pk_psndoc, -- 人员主键
    t1.code ry_code, -- 人员编码
    t1.name ry_name, -- 人员姓名
    t2.name nationality_name -- 民族名称
from bd_psndoc t1 -- 人员基本信息
    left join bd_defdoc t2 on t1.nationality = t2.pk_defdoc -- 民族字典

-- MZ701_02 MZ701_02性别统计
-- t_1 性别统计
select 
    t1.pk_psndoc, -- 人员主键
    t1.code ry_code, -- 人员编码
    t1.name ry_name, -- 人员姓名
    t1.sex -- 性别
from bd_psndoc t1 -- 人员基本信息

-- MZ701_03 MZ701_03政治面貌统计
-- t_1 政治面貌统计
select 
    t1.pk_psndoc, -- 人员主键
    t1.code ry_code, -- 人员编码
    t1.name ry_name, -- 人员姓名
    t2.name polity_name -- 政治面貌名称
from bd_psndoc t1 -- 人员基本信息
    left join bd_defdoc t2 on t1.polity = t2.pk_defdoc -- 政治面貌字典

-- MZ701_04 MZ701_04年龄结构统计
-- t_1 年龄结构统计
select 
    t1.pk_psndoc, -- 人员主键
    t1.code ry_code, -- 人员编码
    t1.name ry_name, -- 人员姓名
    t1.age -- 年龄
from bd_psndoc t1 -- 人员基本信息

-- MZ701_05 MZ701_05学历结构统计
-- t_1 学历结构统计
select 
    t1.pk_psndoc, -- 人员主键
    t1.code ry_code, -- 人员编码
    t1.name ry_name, -- 人员姓名
    t2.code edu_code, -- 学历编码
    t2.name edu_name -- 学历名称
from bd_psndoc t1 -- 人员基本信息
    left join bd_defdoc t2 on t1.edu = t2.pk_defdoc -- 学历字典

-- MZ701_06 MZ701_06技能等级结构统计
-- t_1 技能等级结构统计
select 
    t1.pk_psndoc, -- 人员主键
    t1.code ry_code, -- 人员编码
    t1.name ry_name, -- 人员姓名
    t2.glbdef1.name skill_level_name, -- 技能等级名称
    t2.glbdef7.name skill_status_name -- 技能状态名称
from bd_psndoc t1 -- 人员基本信息
    left join hi_psndoc_glbdef2 t2 on t2.pk_psndoc = t1.pk_psndoc -- 已聘任工人技能等级

-- MZ701 MZ701生产技能人员结构报表
-- t_1 合并所有统计结果
select 
    -- 民族统计
    count(distinct case when t2_nationality.name = '汉族' then t1.pk_psndoc else null end) as hz, -- 汉族
    count(distinct case when t2_nationality.name <> '汉族' and t2_nationality.name is not null then t1.pk_psndoc else null end) as bshz, -- 少数民族
    
    -- 性别统计
    count(distinct case when t1.sex = 1 then t1.pk_psndoc else null end) as nan, -- 男性
    count(distinct case when t1.sex = 2 then t1.pk_psndoc else null end) as nv, -- 女性
    
    -- 政治面貌统计
    count(distinct case when t2_polity.name = '中共党员' then t1.pk_psndoc else null end) as zgdy, -- 中共党员
    
    -- 年龄结构统计
    count(distinct case when t1.age <= 30 then t1.pk_psndoc else null end) as n1, -- 30岁及以下
    count(distinct case when t1.age >= 31 and t1.age <= 35 then t1.pk_psndoc else null end) as n2, -- 31岁至35岁
    count(distinct case when t1.age >= 36 and t1.age <= 40 then t1.pk_psndoc else null end) as n3, -- 36岁至40岁
    count(distinct case when t1.age >= 41 and t1.age <= 45 then t1.pk_psndoc else null end) as n4, -- 41岁至45岁
    count(distinct case when t1.age >= 46 and t1.age <= 50 then t1.pk_psndoc else null end) as n5, -- 46岁至50岁
    count(distinct case when t1.age >= 51 and t1.age <= 55 then t1.pk_psndoc else null end) as n6, -- 51岁至55岁
    count(distinct case when t1.age >= 56 then t1.pk_psndoc else null end) as n7, -- 56岁及以上
    
    -- 学历结构统计
    count(distinct case when t2_edu.code in ('4','41','42','48','49','5','51','59','6','61','62','68','69','7','71','72','73','78','79','8','81','88','89','99','9') then t1.pk_psndoc else null end) as gzjyx, -- 高中及以下
    count(distinct case when t2_edu.code in ('3','31','38','39') then t1.pk_psndoc else null end) as dxzk, -- 大学专科
    count(distinct case when t2_edu.code in ('2','21','28','29') then t1.pk_psndoc else null end) as dxbk, -- 大学本科
    count(distinct case when t2_edu.code in ('1','14','15','16','17','18','19') then t1.pk_psndoc else null end) as ss, -- 硕士
    count(distinct case when t2_edu.code in ('0','11','12','13') then t1.pk_psndoc else null end) as bs, -- 博士
    
    -- 技能等级结构统计
    count(distinct case when t6.glbdef1.name = '初级工（五级）' and t6.glbdef7.name='已聘任该项技能等级' then t1.pk_psndoc else null end) as cjg, -- 初级工
    count(distinct case when t6.glbdef1.name = '中级工（四级）' and t6.glbdef7.name='已聘任该项技能等级' then t1.pk_psndoc else null end) as zjg, -- 中级工
    count(distinct case when t6.glbdef1.name = '高级工（三级）' and t6.glbdef7.name='已聘任该项技能等级' then t1.pk_psndoc else null end) as gjg, -- 高级工
    count(distinct case when t6.glbdef1.name = '技师（二级）' and t6.glbdef7.name='已聘任该项技能等级' then t1.pk_psndoc else null end) as js, -- 技师
    count(distinct case when t6.glbdef1.name = '高级技师（一级）' and t6.glbdef7.name='已聘任该项技能等级' then t1.pk_psndoc else null end) as gjjs, -- 高级技师
    count(distinct case when t6.glbdef1.name = '没有取得资格证书' and t6.glbdef7.name='未聘任该项技能等级' then t1.pk_psndoc else null end) as wdj, -- 无等级
    
    -- 组织类型和地域合并统计
    count(distinct case when t13.name in ('总部','分公司','专业机构','事业部') then t1.pk_psndoc else null end) as mggtx, -- 母公司体系
    count(distinct case when t13.name in ('子公司','子公司下属分公司','子公司下属子公司') and t12.name = '京内' then t1.pk_psndoc else null end) as jnzgs, -- 京内子公司
    count(distinct case when t13.name in ('子公司','子公司下属分公司','子公司下属子公司') and t12.name = '京外' then t1.pk_psndoc else null end) as jwzgs, -- 京外子公司
    count(distinct case when t13.name in ('子公司','子公司下属分公司','子公司下属子公司') and t12.name = '境外' then t1.pk_psndoc else null end) as jwzgs_out, -- 境外子公司
    
    -- 人员总数
    count(distinct t1.pk_psndoc) as rybm -- 人员编码总数

from bd_psndoc t1 -- 人员基本信息
    left join bd_defdoc t2_nationality on t1.nationality = t2_nationality.pk_defdoc -- 民族字典
    left join bd_defdoc t2_polity on t1.polity = t2_polity.pk_defdoc -- 政治面貌字典
    left join bd_defdoc t2_edu on t1.edu = t2_edu.pk_defdoc -- 学历字典
    left join hi_psndoc_glbdef2 t6 on t6.pk_psndoc = t1.pk_psndoc -- 技能等级
    left join hi_psnorg t7 on t7.pk_psndoc = t1.pk_psndoc -- 组织关系
    left join hi_psnjob t8 on t8.pk_psndoc = t1.pk_psndoc -- 人员工作记录
    left join org_orgs t9 on t9.pk_org = t8.pk_org -- 组织
    -- 移除人员类别JOIN，与简化查询保持一致
    -- left join bd_psncl t11 on t8.pk_psncl = t11.pk_psncl -- 人员类别
    left join bd_defdoc t12 on t12.pk_defdoc = t9.def4 -- 地域字典（def4字段）
    left join bd_defdoc t13 on t13.pk_defdoc = t9.def2 -- 组织类型字典（def2字段）
where 1 = 1
    and t7.indocflag = 'Y' -- 转入人员档案
    and t7.lastflag = 'Y' -- 最新标识
    and t7.psntype = 0
    and t8.endflag = 'N'
    and t8.lastflag = 'Y'
    and t8.ismainjob = 'Y'
    and t8.pk_postseries in ('10011T100000000098AS', '10011T100000000098B2', '10011T100000000098B3', '10011T100000000098B4', '10011T100000000098B5', '10011T100000000098B6')
    -- 添加组织类型和地域过滤条件，与简化查询保持一致
    and t13.name in ('子公司','子公司下属分公司','子公司下属子公司')
    and t12.name = '京外'
    -- 注释掉时间参数和人员类别过滤，与简化查询保持一致
    -- and t8.begindate <= datefmt(parameter('param2'), 'yyyy-mm-dd')
    -- and nvl(t8.enddate, '2099-12-31') >= datefmt(parameter('param2'), 'yyyy-mm-dd')
    -- and t11.name in (parameter('rylb'))
