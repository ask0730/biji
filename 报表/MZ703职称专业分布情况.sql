-- t_2
select 
--总数
count(a.gcrq) gcrq
,count(a.gcfrq) gcfrq
,count(a.jj) jj
,count(a.zg) zg
,count(a.kj) kj
,count(a.jsj) jsj
,count(a.tj) tj
,count(a.sj) sj
,count(a.fy) fy
,count(a.da) da
,count(a.xw) xw
from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '工程（燃气）'  then 1 end gcrq --工程
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '工程（非燃气）'  then 1 end gcfrq --工程（非燃气）
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '经济'  then 1 end jj --经济
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '政工'  then 1 end zg --政工
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '会计'  then 1 end kj --会计
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '计算机'  then 1 end jsj --计算机
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '统计'  then 1 end tj --统计
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '审计'  then 1 end sj --审计
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '翻译'  then 1 end fy --翻译
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '档案'  then 1 end da --档案
,case when T3.glbdef4.name <> '未评定专业技术职务' and T3.glbdef6.name = '新闻'  then 1 end xw --新闻

from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef18 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef8 = '10011T10000000001XG7' --是否聘任专业技术职务为'已聘任该项专业技术职务'
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部','子公司','子公司下属分公司','子公司下属子公司')
order by T1.showorder
)a



-- t_3
select 
--总数
count(a.gcrq) gcrq1
,count(a.gcfrq) gcfrq1
,count(a.jj) jj1
,count(a.zg) zg1
,count(a.kj) kj1
,count(a.jsj) jsj1
,count(a.tj) tj1
,count(a.sj) sj1
,count(a.fy) fy1
,count(a.da) da1
,count(a.xw) xw1
from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '工程（燃气）'  then 1 end gcrq --工程
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '工程（非燃气）'  then 1 end gcfrq --工程（非燃气）
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '经济'  then 1 end jj --经济
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '政工'  then 1 end zg --政工
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '会计'  then 1 end kj --会计
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '计算机'  then 1 end jsj --计算机
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '统计'  then 1 end tj --统计
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '审计'  then 1 end sj --审计
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '翻译'  then 1 end fy --翻译
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '档案'  then 1 end da --档案
,case when T3.glbdef4.name = '正高级专业技术职务'  and T3.glbdef6.name = '新闻'  then 1 end xw --新闻

from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef18 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef8 = '10011T10000000001XG7' --是否聘任专业技术职务为'已聘任该项专业技术职务'
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部','子公司','子公司下属分公司','子公司下属子公司')
order by T1.showorder
)a

-- t_4
select 
--总数
count(a.gcrq) gcrq2
,count(a.gcfrq) gcfrq2
,count(a.jj) jj2
,count(a.zg) zg2
,count(a.kj) kj2
,count(a.jsj) jsj2
,count(a.tj) tj2
,count(a.sj) sj2
,count(a.fy) fy2
,count(a.da) da2
,count(a.xw) xw2
from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '工程（燃气）'  then 1 end gcrq --工程
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '工程（非燃气）'  then 1 end gcfrq --工程（非燃气）
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '经济'  then 1 end jj --经济
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '政工'  then 1 end zg --政工
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '会计'  then 1 end kj --会计
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '计算机'  then 1 end jsj --计算机
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '统计'  then 1 end tj --统计
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '审计'  then 1 end sj --审计
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '翻译'  then 1 end fy --翻译
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '档案'  then 1 end da --档案
,case when T3.glbdef4.name = '副高级专业技术职务'  and T3.glbdef6.name = '新闻'  then 1 end xw --新闻

from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef18 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef8 = '10011T10000000001XG7' --是否聘任专业技术职务为'已聘任该项专业技术职务'
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部','子公司','子公司下属分公司','子公司下属子公司')
order by T1.showorder
)a

-- t_5
select 
--总数
count(a.gcrq) gcrq3
,count(a.gcfrq) gcfrq3
,count(a.jj) jj3
,count(a.zg) zg3
,count(a.kj) kj3
,count(a.jsj) jsj3
,count(a.tj) tj3
,count(a.sj) sj3
,count(a.fy) fy3
,count(a.da) da3
,count(a.xw) xw3
from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '工程（燃气）'  then 1 end gcrq --工程
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '工程（非燃气）'  then 1 end gcfrq --工程（非燃气）
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '经济'  then 1 end jj --经济
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '政工'  then 1 end zg --政工
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '会计'  then 1 end kj --会计
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '计算机'  then 1 end jsj --计算机
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '统计'  then 1 end tj --统计
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '审计'  then 1 end sj --审计
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '翻译'  then 1 end fy --翻译
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '档案'  then 1 end da --档案
,case when T3.glbdef4.name = '中级专业技术职务'  and T3.glbdef6.name = '新闻'  then 1 end xw --新闻

from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef18 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef8 = '10011T10000000001XG7' --是否聘任专业技术职务为'已聘任该项专业技术职务'
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部','子公司','子公司下属分公司','子公司下属子公司')
order by T1.showorder
)a



-- t_6
select 
--总数
count(a.gcrq) gcrq4
,count(a.gcfrq) gcfrq4
,count(a.jj) jj4
,count(a.zg) zg4
,count(a.kj) kj4
,count(a.jsj) jsj4
,count(a.tj) tj4
,count(a.sj) sj4
,count(a.fy) fy4
,count(a.da) da4
,count(a.xw) xw4
from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '工程（燃气）'  then 1 end gcrq --工程
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '工程（非燃气）'  then 1 end gcfrq --工程（非燃气）
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '经济'  then 1 end jj --经济
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '政工'  then 1 end zg --政工
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '会计'  then 1 end kj --会计
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '计算机'  then 1 end jsj --计算机
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '统计'  then 1 end tj --统计
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '审计'  then 1 end sj --审计
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '翻译'  then 1 end fy --翻译
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '档案'  then 1 end da --档案
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )  and T3.glbdef6.name = '新闻'  then 1 end xw --新闻

from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef18 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef8 = '10011T10000000001XG7' --是否聘任专业技术职务为'已聘任该项专业技术职务'
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部','子公司','子公司下属分公司','子公司下属子公司')
order by T1.showorder
)a



-- t_7
select 
--总数
count(a.gcrq) gcrq5
from (
select distinct
T1.pk_psnjob 
,bd_psndoc.name
--总数（排除未评定专业技术职务）
,case when T3.glbdef4.name = '未评定专业技术职务'   then 1 end gcrq --工程
from bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join hi_psnjob T1 
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_adminorg T2 
ON T2.pk_adminorg = T1.pk_org 
left outer join hi_psndoc_glbdef18 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 
left outer join org_dept org_dept 
on org_dept.pk_dept = T1.pk_dept 
left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 
left outer join bd_defdoc bd_defdoc_zzlx  --组织类型
on t2.def2 = bd_defdoc_zzlx.pk_defdoc
left outer join bd_psncl  --人员类别
on T1.pk_psncl=bd_psncl.pk_psncl
where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.endflag='N' and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef8 = '10011T10000000001XG7' --是否聘任专业技术职务为'已聘任该项专业技术职务'
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param2'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部','子公司','子公司下属分公司','子公司下属子公司')
order by T1.showorder
)a


-- 连接条件
表2全连接表3 1=1
表2全连接表4 1=1
表2全连接表5 1=1
表2全连接表6 1=1
表2全连接表7 1=1