-- MZ701_01
-- t_1 - 基础人员信息
select 
    t1.pk_psndoc, -- 人员主键
    t1.code ry_code, -- 人员编码
    t1.name ry_name, -- 人员姓名
    t1.sex, -- 性别
    t1.age, -- 年龄
    t1.nationality, -- 民族
    t1.polity, -- 政治面貌
    t1.edu, -- 学历
    t2.pk_org, -- 组织主键
    t3.name org_name, -- 组织名称
    t2.pk_dept, -- 部门主键
    t4.name dept_name, -- 部门名称
    t5.name psncl_name, -- 人员类别名称
    t6.name adminorg_name, -- 行政组织名称
    t7.name zzlx_name -- 组织类型名称
from bd_psndoc t1 -- 人员基本信息
    left join hi_psnjob t2 on t2.pk_psndoc = t1.pk_psndoc -- 人员工作记录
    left join org_orgs t3 on t3.pk_org = t2.pk_org -- 组织
    left join org_dept t4 on t4.pk_dept = t2.pk_dept -- 部门
    left join bd_psncl t5 on t5.pk_psncl = t2.pk_psncl -- 人员类别
    left join org_adminorg t6 on t6.pk_adminorg = t2.pk_org -- 行政组织
    left join bd_defdoc t7 on t7.pk_defdoc = t6.def2 -- 组织类型
    left join hi_psnorg t8 on t8.pk_psndoc = t1.pk_psndoc -- 组织关系
where t8.indocflag = 'Y' 
    and t8.psntype = 0
    and t2.endflag = 'N'
    and t2.lastflag = 'Y'
    and t2.ismainjob = 'Y'
    and t2.pk_postseries in ('10011T100000000098AS', '10011T100000000098B2', '10011T100000000098B3', '10011T100000000098B4', '10011T100000000098B5', '10011T100000000098B6')
    and t2.begindate <= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and nvl(t2.enddate, '2099-12-31') >= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and t5.name in (parameter('rylb'))

-- MZ701_02
-- t_1 - 技能等级信息
select 
    t1.pk_psndoc, -- 人员主键
    t6.name skill_level, -- 技能等级
    t7.name skill_status -- 技能状态
from bd_psndoc t1 -- 人员基本信息
    left join hi_psndoc_glbdef2 t2 on t2.pk_psndoc = t1.pk_psndoc -- 技能等级记录
    left join hi_psnorg t3 on t3.pk_psndoc = t1.pk_psndoc -- 组织关系
    left join hi_psnjob t4 on t4.pk_psndoc = t1.pk_psndoc -- 工作记录
    left join bd_psncl t5 on t5.pk_psncl = t4.pk_psncl -- 人员类别
    left join bd_defdoc t6 on t6.pk_defdoc = t2.glbdef1 -- 技能等级定义
    left join bd_defdoc t7 on t7.pk_defdoc = t2.glbdef7 -- 技能状态定义
where t3.indocflag = 'Y' 
    and t3.psntype = 0
    and t4.endflag = 'N'
    and t4.lastflag = 'Y'
    and t4.ismainjob = 'Y'
    and t4.pk_postseries in ('10011T100000000098AS', '10011T100000000098B2', '10011T100000000098B3', '10011T100000000098B4', '10011T100000000098B5', '10011T100000000098B6')
    and t4.begindate <= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and nvl(t4.enddate, '2099-12-31') >= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and t5.name in (parameter('rylb'))

-- MZ701_03
-- t_1 - 合并人员基本信息和技能等级信息
select 
    a.*,
    b.skill_level,
    b.skill_status
from smart('MZ701_01') a
    left join smart('MZ701_02') b on a.pk_psndoc = b.pk_psndoc

-- MZ701_04
-- t_1 - 民族信息
select 
    t1.pk_psndoc,
    t2.name nationality_name
from bd_psndoc t1
    left join bd_defdoc t2 on t1.nationality = t2.pk_defdoc
    left join hi_psnorg t3 on t3.pk_psndoc = t1.pk_psndoc
    left join hi_psnjob t4 on t4.pk_psndoc = t1.pk_psndoc
    left join bd_psncl t5 on t5.pk_psncl = t4.pk_psncl
where t3.indocflag = 'Y' 
    and t3.psntype = 0
    and t4.endflag = 'N'
    and t4.lastflag = 'Y'
    and t4.ismainjob = 'Y'
    and t4.pk_postseries in ('10011T100000000098AS', '10011T100000000098B2', '10011T100000000098B3', '10011T100000000098B4', '10011T100000000098B5', '10011T100000000098B6')
    and t4.begindate <= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and nvl(t4.enddate, '2099-12-31') >= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and t5.name in (parameter('rylb'))

-- MZ701_05
-- t_1 - 政治面貌信息
select 
    t1.pk_psndoc,
    t2.name polity_name
from bd_psndoc t1
    left join bd_defdoc t2 on t1.polity = t2.pk_defdoc
    left join hi_psnorg t3 on t3.pk_psndoc = t1.pk_psndoc
    left join hi_psnjob t4 on t4.pk_psndoc = t1.pk_psndoc
    left join bd_psncl t5 on t5.pk_psncl = t4.pk_psncl
where t3.indocflag = 'Y' 
    and t3.psntype = 0
    and t4.endflag = 'N'
    and t4.lastflag = 'Y'
    and t4.ismainjob = 'Y'
    and t4.pk_postseries in ('10011T100000000098AS', '10011T100000000098B2', '10011T100000000098B3', '10011T100000000098B4', '10011T100000000098B5', '10011T100000000098B6')
    and t4.begindate <= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and nvl(t4.enddate, '2099-12-31') >= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and t5.name in (parameter('rylb'))

-- MZ701_06
-- t_1 - 学历信息
select 
    t1.pk_psndoc,
    t2.code edu_code,
    t2.name edu_name
from bd_psndoc t1
    left join bd_defdoc t2 on t1.edu = t2.pk_defdoc
    left join hi_psnorg t3 on t3.pk_psndoc = t1.pk_psndoc
    left join hi_psnjob t4 on t4.pk_psndoc = t1.pk_psndoc
    left join bd_psncl t5 on t5.pk_psncl = t4.pk_psncl
where t3.indocflag = 'Y' 
    and t3.psntype = 0
    and t4.endflag = 'N'
    and t4.lastflag = 'Y'
    and t4.ismainjob = 'Y'
    and t4.pk_postseries in ('10011T100000000098AS', '10011T100000000098B2', '10011T100000000098B3', '10011T100000000098B4', '10011T100000000098B5', '10011T100000000098B6')
    and t4.begindate <= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and nvl(t4.enddate, '2099-12-31') >= datefmt(parameter('param2'), 'yyyy-mm-dd')
    and t5.name in (parameter('rylb'))

-- MZ701_07
-- t_1 - 最终合并数据
select 
    a.*,
    b.nationality_name,
    c.polity_name,
    d.edu_code,
    d.edu_name
from smart('MZ701_03') a
    left join smart('MZ701_04') b on a.pk_psndoc = b.pk_psndoc
    left join smart('MZ701_05') c on a.pk_psndoc = c.pk_psndoc
    left join smart('MZ701_06') d on a.pk_psndoc = d.pk_psndoc

-- MZ701
-- t_1 - 最终统计报表
select 
    -- 技能等级统计
    count(distinct case when skill_level = '初级工（五级）' and skill_status = '已聘任该项技能等级' then pk_psndoc else null end) as cjg, -- 初级工
    count(distinct case when skill_level = '中级工（四级）' and skill_status = '已聘任该项技能等级' then pk_psndoc else null end) as zjg, -- 中级工
    count(distinct case when skill_level = '高级工（三级）' and skill_status = '已聘任该项技能等级' then pk_psndoc else null end) as gjg, -- 高级工
    count(distinct case when skill_level = '技师（二级）' and skill_status = '已聘任该项技能等级' then pk_psndoc else null end) as js, -- 技师
    count(distinct case when skill_level = '高级技师（一级）' and skill_status = '已聘任该项技能等级' then pk_psndoc else null end) as gjjs, -- 高级技师
    count(distinct case when skill_level = '没有取得资格证书' and skill_status = '未聘任该项技能等级' then pk_psndoc else null end) as wdj, -- 无等级
    
    -- 人员基本信息统计
    count(distinct case when 1=1 then pk_psndoc else null end) as rybm, -- 人员编码
    count(distinct case when skill_level is null then pk_psndoc else null end) as wjnl, -- 无技能等级记录的人员数
    count(distinct case when 1=1 then pk_psndoc else null end) as wgzl, -- 工作记录的人员数
    count(distinct case when nationality_name = '汉族' then pk_psndoc else null end) as hz, -- 民族是汉族
    count(distinct case when nationality_name <> '汉族' then pk_psndoc else null end) as bshz, -- 民族不是汉族
    count(distinct case when sex = 1 then pk_psndoc else null end) as nan, -- 性别为男
    count(distinct case when sex = 2 then pk_psndoc else null end) as nv, -- 性别为女
    count(distinct case when polity_name = '中共党员' then pk_psndoc else null end) as zgdy, -- 政治面貌是中共党员
    
    -- 年龄统计
    count(distinct case when age <= 30 and age is not null then pk_psndoc else null end) as n1, -- 年龄30以下
    count(distinct case when age >= 31 and age <= 35 and age is not null then pk_psndoc else null end) as n2, -- 31到35
    count(distinct case when age >= 36 and age <= 40 and age is not null then pk_psndoc else null end) as n3, -- 36到40
    count(distinct case when age >= 41 and age <= 45 and age is not null then pk_psndoc else null end) as n4, -- 41到45
    count(distinct case when age >= 46 and age <= 50 and age is not null then pk_psndoc else null end) as n5, -- 46到50
    count(distinct case when age >= 51 and age <= 55 and age is not null then pk_psndoc else null end) as n6, -- 51到55
    count(distinct case when age >= 56 and age is not null then pk_psndoc else null end) as n7, -- 56以上
    
    -- 学历统计
    count(distinct case when edu_code in ('4','41','42','48','49','5','51','59','6','61','62','68','69','7','71','72','73','78','79','8','81','88','89','99','9') then pk_psndoc else null end) as gzjyx, -- 学历高中及以下
    count(distinct case when edu_code in ('3','31','38','39') then pk_psndoc else null end) as dxzk, -- 学历大学专科
    count(distinct case when edu_code in ('2','21','28','29') then pk_psndoc else null end) as dxbk, -- 学历大学本科
    count(distinct case when edu_code in ('1','14','15','16','17','18','19') then pk_psndoc else null end) as ss, -- 学历硕士
    count(distinct case when edu_code in ('0','11','12','13') then pk_psndoc else null end) as bs -- 博士
from smart('MZ701_07')
