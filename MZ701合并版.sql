select 
count(cjg) cjg--初级工

from(
select --

case when T3.glbdef1.name = '初级工（五级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end  cjg--工人技能等级为初级工

from bd_psndoc bd_psndoc --1.人员基本信息

inner join hi_psnorg hi_psnorg --2.组织关系表
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 --3.人员工作记录表
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join org_orgs org_orgs --4.组织
on org_orgs.pk_org = T1.pk_org 

left outer join org_dept org_dept --5.部门
on org_dept.pk_dept = T1.pk_dept 

left outer join org_adminorg --行政组织
on T1.pk_org = org_adminorg.pk_adminorg

left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl

--民族
left outer join bd_defdoc bd_defdoc_mz
on bd_psndoc.nationality=bd_defdoc_mz.pk_defdoc

--政治面貌
left outer join bd_defdoc bd_defdoc_zzmm
on bd_psndoc.polity=bd_defdoc_zzmm.pk_defdoc

--已聘任工人技能等级
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on org_adminorg.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 
--AND org_adminorg.name = '高压管网分公司'
and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and t1.endflag='N' 
and t1.lastflag='Y' and t1.ismainjob='Y'
and  T1.pk_postseries in ( '10011T100000000098AS' , '10011T100000000098B2' , '10011T100000000098B3' , '10011T100000000098B4' , '10011T100000000098B5' , '10011T100000000098B6' )
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
)a 
select 

count(cjg) zjg--初级工

from(
select  --

case when T3.glbdef1.name = '中级工（四级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end  cjg--工人技能等级为初级工

from bd_psndoc bd_psndoc --1.人员基本信息

inner join hi_psnorg hi_psnorg --2.组织关系表
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 --3.人员工作记录表
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join org_orgs org_orgs --4.组织
on org_orgs.pk_org = T1.pk_org 

left outer join org_dept org_dept --5.部门
on org_dept.pk_dept = T1.pk_dept 

left outer join org_adminorg --行政组织
on T1.pk_org = org_adminorg.pk_adminorg

left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl

--民族
left outer join bd_defdoc bd_defdoc_mz
on bd_psndoc.nationality=bd_defdoc_mz.pk_defdoc

--政治面貌
left outer join bd_defdoc bd_defdoc_zzmm
on bd_psndoc.polity=bd_defdoc_zzmm.pk_defdoc

--已聘任工人技能等级
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on org_adminorg.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 
--AND org_adminorg.name = '高压管网分公司'
and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and t1.endflag='N' 
and t1.lastflag='Y' and t1.ismainjob='Y'
and  T1.pk_postseries in ( '10011T100000000098AS' , '10011T100000000098B2' , '10011T100000000098B3' , '10011T100000000098B4' , '10011T100000000098B5' , '10011T100000000098B6' )
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
)a
select 
count(cjg) gjg--初级工

from(
select

case when T3.glbdef1.name = '高级工（三级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end  cjg--工人技能等级为初级工

from bd_psndoc bd_psndoc --1.人员基本信息

inner join hi_psnorg hi_psnorg --2.组织关系表
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 --3.人员工作记录表
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join org_orgs org_orgs --4.组织
on org_orgs.pk_org = T1.pk_org 

left outer join org_dept org_dept --5.部门
on org_dept.pk_dept = T1.pk_dept 

left outer join org_adminorg --行政组织
on T1.pk_org = org_adminorg.pk_adminorg

left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl

--民族
left outer join bd_defdoc bd_defdoc_mz
on bd_psndoc.nationality=bd_defdoc_mz.pk_defdoc

--政治面貌
left outer join bd_defdoc bd_defdoc_zzmm
on bd_psndoc.polity=bd_defdoc_zzmm.pk_defdoc

--已聘任工人技能等级
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on org_adminorg.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 
--AND org_adminorg.name = '高压管网分公司'
and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and t1.endflag='N' 
and t1.lastflag='Y' and t1.ismainjob='Y'
and  T1.pk_postseries in ( '10011T100000000098AS' , '10011T100000000098B2' , '10011T100000000098B3' , '10011T100000000098B4' , '10011T100000000098B5' , '10011T100000000098B6' )
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
)a 
select 


count(cjg) js--初级工

from(
select --

case when T3.glbdef1.name = '技师（二级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end  cjg--工人技能等级为初级工

from bd_psndoc bd_psndoc --1.人员基本信息

inner join hi_psnorg hi_psnorg --2.组织关系表
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 --3.人员工作记录表
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join org_orgs org_orgs --4.组织
on org_orgs.pk_org = T1.pk_org 

left outer join org_dept org_dept --5.部门
on org_dept.pk_dept = T1.pk_dept 

left outer join org_adminorg --行政组织
on T1.pk_org = org_adminorg.pk_adminorg

left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl

--民族
left outer join bd_defdoc bd_defdoc_mz
on bd_psndoc.nationality=bd_defdoc_mz.pk_defdoc

--政治面貌
left outer join bd_defdoc bd_defdoc_zzmm
on bd_psndoc.polity=bd_defdoc_zzmm.pk_defdoc

--已聘任工人技能等级
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on org_adminorg.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 
--AND org_adminorg.name = '高压管网分公司'
and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and t1.endflag='N' 
and t1.lastflag='Y' and t1.ismainjob='Y'
and  T1.pk_postseries in ( '10011T100000000098AS' , '10011T100000000098B2' , '10011T100000000098B3' , '10011T100000000098B4' , '10011T100000000098B5' , '10011T100000000098B6' )
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))

)a 
select 
count(cjg) gjjs--初级工

from(
select --

case when T3.glbdef1.name = '高级技师（一级）' and T3.glbdef7.name='已聘任该项技能等级' then 1 else null end  cjg--工人技能等级为初级工

from bd_psndoc bd_psndoc --1.人员基本信息

inner join hi_psnorg hi_psnorg --2.组织关系表
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 --3.人员工作记录表
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join org_orgs org_orgs --4.组织
on org_orgs.pk_org = T1.pk_org 

left outer join org_dept org_dept --5.部门
on org_dept.pk_dept = T1.pk_dept 

left outer join org_adminorg --行政组织
on T1.pk_org = org_adminorg.pk_adminorg

left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl

--民族
left outer join bd_defdoc bd_defdoc_mz
on bd_psndoc.nationality=bd_defdoc_mz.pk_defdoc

--政治面貌
left outer join bd_defdoc bd_defdoc_zzmm
on bd_psndoc.polity=bd_defdoc_zzmm.pk_defdoc

--已聘任工人技能等级
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on org_adminorg.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 
--AND org_adminorg.name = '高压管网分公司'
and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and t1.endflag='N' 
and t1.lastflag='Y' and t1.ismainjob='Y'
and  T1.pk_postseries in ( '10011T100000000098AS' , '10011T100000000098B2' , '10011T100000000098B3' , '10011T100000000098B4' , '10011T100000000098B5' , '10011T100000000098B6' )
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))

)a
select 


count(cjg) wdj--初级工

from(
select --


case when T3.glbdef1.name = '没有取得资格证书' and T3.glbdef7.name='未聘任该项技能等级' then 1 else null end  cjg--工人技能等级为初级

from bd_psndoc bd_psndoc --1.人员基本信息

inner join hi_psnorg hi_psnorg --2.组织关系表
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 --3.人员工作记录表
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join org_orgs org_orgs --4.组织
on org_orgs.pk_org = T1.pk_org 

left outer join org_dept org_dept --5.部门
on org_dept.pk_dept = T1.pk_dept 

left outer join org_adminorg --行政组织
on T1.pk_org = org_adminorg.pk_adminorg

left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl

--民族
left outer join bd_defdoc bd_defdoc_mz
on bd_psndoc.nationality=bd_defdoc_mz.pk_defdoc

--政治面貌
left outer join bd_defdoc bd_defdoc_zzmm
on bd_psndoc.polity=bd_defdoc_zzmm.pk_defdoc

--已聘任工人技能等级
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on org_adminorg.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 
--AND org_adminorg.name = '高压管网分公司'
and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and t1.endflag='N' 
and t1.lastflag='Y' and t1.ismainjob='Y'
and  T1.pk_postseries in ( '10011T100000000098AS' , '10011T100000000098B2' , '10011T100000000098B3' , '10011T100000000098B4' , '10011T100000000098B5' , '10011T100000000098B6' )
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))

)a 
select 
count(code) rybm,--人员编码
count(hz) hz,--民族是汉族
count(bshz) bshz,--民族不是汉族
count(nan) nan ,--性别为男
count(nv) nv,--性别为女
count(zgdy) zgdy,--政治面貌是中共党员
count(n1) n1,--年龄30以下
count(n2) n2,--31到35
count(n3) n3,--26到40
count(n4) n4,--41到45
count(n5) n5,--46到50
count(n6) n6,--51到55
count(n7) n7,--56以上
count(gzjyx) gzjyx,--学历高中及以下
count(dxzk) dxzk,--学历大学专科
count(dxbk) dxbk,--学历大学本科
count(ss) ss,--学历硕士
count(bs) bs --博士
from(
select distinct --
bd_psndoc.code,--人员编码
bd_psndoc.name xm,--姓名
case when bd_defdoc_mz.name = '汉族' then 1 else null end  hz ,--汉族
case when bd_defdoc_mz.name <> '汉族' then 1 else null end  bshz ,--不是汉族
case when bd_psndoc.sex = 1 then 1 else null end nan ,--男性
case when bd_psndoc.sex = 2 then 1 else null end nv ,--女性
case when bd_defdoc_zzmm.name = '中共党员' then 1 else null end zgdy ,--政治面貌是中共党员
case when bd_psndoc.age <= 30 then 1 else null end n1,--年龄小于等于30
case when bd_psndoc.age >=31 and bd_psndoc.age<=35 then 1 else null end n2,
case when bd_psndoc.age >=36 and bd_psndoc.age<=40 then 1 else null end n3,
case when bd_psndoc.age >=41 and bd_psndoc.age<=45 then 1 else null end n4,
case when bd_psndoc.age >=46 and bd_psndoc.age<=50 then 1 else null end n5,
case when bd_psndoc.age >=51 and bd_psndoc.age<=55 then 1 else null end n6,
case when bd_psndoc.age >= 56 then 1 else null end n7,--年龄大于等于56

case when bd_psndoc.edu.code in ('4','41','42','48','49','5','51','59','6','61','62','68','69','7','71','72','73','78','79','8','81','88','89','99','9')  then 1 else null end gzjyx, 
case when bd_psndoc.edu.code in ('3','31','38','39') then 1 else null end dxzk, 
case when bd_psndoc.edu.code in ('2','21','28','29')then 1 else null end dxbk, 
case when bd_psndoc.edu.code in ('1','14','15','16','17','18','19') then 1 else null end ss, 
case when bd_psndoc.edu.code in ('0','11','12','13') then 1 else null end bs
from bd_psndoc bd_psndoc --1.人员基本信息

inner join hi_psnorg hi_psnorg --2.组织关系表
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 --3.人员工作记录表
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join org_orgs org_orgs --4.组织
on org_orgs.pk_org = T1.pk_org 

left outer join org_dept org_dept --5.部门
on org_dept.pk_dept = T1.pk_dept 

left outer join org_adminorg --行政组织
on T1.pk_org = org_adminorg.pk_adminorg

left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl

--民族
left outer join bd_defdoc bd_defdoc_mz
on bd_psndoc.nationality=bd_defdoc_mz.pk_defdoc

--政治面貌
left outer join bd_defdoc bd_defdoc_zzmm
on bd_psndoc.polity=bd_defdoc_zzmm.pk_defdoc

--已聘任工人技能等级
left outer join hi_psndoc_glbdef2 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on org_adminorg.def2 = bd_defdoc_zzlx.pk_defdoc
where 1 = 1 
--AND org_adminorg.name = '高压管网分公司'
and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and t1.endflag='N' 
and t1.lastflag='Y' and t1.ismainjob='Y'
and  T1.pk_postseries in ( '10011T100000000098AS' , '10011T100000000098B2' , '10011T100000000098B3' , '10011T100000000098B4' , '10011T100000000098B5' , '10011T100000000098B6' )
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
)a 