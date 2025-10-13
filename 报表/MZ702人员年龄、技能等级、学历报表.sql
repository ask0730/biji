-- t_1
select 
gwxl,gslx 
,count(distinct pk_psndoc) zs
,count(distinct case when hz = 1 then pk_psndoc end) hz,count(distinct case when bshz = 1 then pk_psndoc end) bshz
,count(distinct case when nan = 1 then pk_psndoc end) nan ,count(distinct case when nv = 1 then pk_psndoc end) nv
,count(distinct case when zgdy = 1 then pk_psndoc end) zgdy,count(distinct case when bszgdy = 1 then pk_psndoc end) bszgdy
,count(distinct case when n30 = 1 then pk_psndoc end) n30,count(distinct case when n3135 = 1 then pk_psndoc end) n3135,count(distinct case when n3640 = 1 then pk_psndoc end) n3640,count(distinct case when n4145 = 1 then pk_psndoc end) n4145,count(distinct case when n4650 = 1 then pk_psndoc end) n4650,count(distinct case when n5155 = 1 then pk_psndoc end) n5155,count(distinct case when n56 = 1 then pk_psndoc end) n56
,count(distinct case when gzjyx = 1 then pk_psndoc end) gzjyx,count(distinct case when dxzk = 1 then pk_psndoc end) dxzk,count(distinct case when dxbk = 1 then pk_psndoc end) dxbk,count(distinct case when ss = 1 then pk_psndoc end) ss,count(distinct case when bs = 1 then pk_psndoc end) bs
from 
(select bd_psndoc.pk_psndoc,
case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司')
and bd_defdoc_dwszd.name ='京内' then '京内子公司'
when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司')
and bd_defdoc_dwszd.name ='京外' then '京外子公司'
when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司')
and bd_defdoc_dwszd.name ='境外' then '境外子公司'
else '其他' end gslx --公司类型
,case when T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' )  then '经营管理' 
 when T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' ) then '专业技术' end gwxl --岗位序列

,case when bd_defdoc_mz.name = '汉族' then 1 else null end  hz --汉族
,case when bd_defdoc_mz.name <> '汉族' then 1 else null end  bshz --不是汉族
,case when bd_psndoc.sex = 1 then 1 else null end nan --男性
,case when bd_psndoc.sex = 2 then 1 else null end nv --女性
,case when bd_defdoc_zzmm.name = '中共党员' then 1 end zgdy --政治面貌是中共党员
,case when bd_defdoc_zzmm.name <> '中共党员' then 1 end bszgdy --政治面貌不是中共党员
,case when bd_psndoc.age <= 30 then 1 else null end n30--年龄小于等于30
,case when bd_psndoc.age >=31 and bd_psndoc.age<=35 then 1 else null end n3135
,case when bd_psndoc.age >=36 and bd_psndoc.age<=40 then 1 else null end n3640
,case when bd_psndoc.age >=41 and bd_psndoc.age<=45 then 1 else null end n4145
,case when bd_psndoc.age >=46 and bd_psndoc.age<=50 then 1 else null end n4650
,case when bd_psndoc.age >=51 and bd_psndoc.age<=55 then 1 else null end n5155
,case when bd_psndoc.age >= 56 then 1 else null end n56--年龄大于等于56
,case when bd_psndoc.edu.code in ('4','41','42','48','49','5','51','59','6','61','62','68','69','7','71','72','73','78','79','8','81','88','89','99','9')  then 1 else null end gzjyx--高中及以下
,case when bd_psndoc.edu.code in ('3','31','38','39') then 1 else null end dxzk--大学专科
,case when bd_psndoc.edu.code in ('2','21','28','29')then 1 else null end dxbk--大学本科
,case when bd_psndoc.edu.code in ('1','14','15','16','17','18','19') then 1 else null end ss--硕士
,case when bd_psndoc.edu.code in ('0','11','12','13') then 1 else null end bs--博士
,ROW_NUMBER() OVER (PARTITION BY bd_psndoc.pk_psndoc ORDER BY T1.begindate DESC) as rn
From 

bd_psndoc bd_psndoc 
inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 --人员基本信息表
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 



left outer join org_adminorg T2 --组织
ON T2.pk_adminorg = T1.pk_org 

left outer join org_dept org_dept --部门
on org_dept.pk_dept = T1.pk_dept 



Left outer join bd_psncl bd_psncl --人员类别
On T1.pk_psncl = bd_psncl.pk_psncl

Left outer join bd_defdoc bd_defdoc_zzlx--组织类型自定义档案
On T2.def2 = bd_defdoc_zzlx.pk_defdoc

left outer join bd_defdoc bd_defdoc_mz--民族
on bd_defdoc_mz.pk_defdoc = bd_psndoc.nationality

left outer join bd_defdoc bd_defdoc_zzmm--政治面貌
on bd_defdoc_zzmm.pk_defdoc = bd_psndoc.polity

--left outer join om_postseries om_postseries --岗位序列
--on om_postseries.pk_postseries = T1.pk_postseries

left outer join bd_defdoc bd_defdoc_dwszd  --单位所在地
on T2.def4 = bd_defdoc_dwszd.pk_defdoc

where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and t1.lastflag='Y' and t1.ismainjob='Y' 
-- 修改：移除endflag='N'条件，允许查询离职员工
--and (
--bd_defdoc_zzlx.name in ('总部','分公司','专业机构')
--or (bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司')
--and bd_defdoc_dwszd.name ='京内' )
--or (bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司')
--and bd_defdoc_dwszd.name ='京外')
--)
and
(T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' )  or
T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' ))
-- 修改：调整时间条件，允许查询在指定时间范围内有工作经历的员工（包括已离职）
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param1'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in (parameter('zzlx'))
order by T1.showorder)a 
where rn = 1
group by gwxl,gslx order by gwxl,gslx

-- t_2

select count(distinct case when wdj = 1 then pk_psndoc end) wdj,count(distinct case when cj = 1 then pk_psndoc end) cj,count(distinct case when zj = 1 then pk_psndoc end) zj,count(distinct case when fgj = 1 then pk_psndoc end) fgj,count(distinct case when zgj = 1 then pk_psndoc end) zgj,gwxl,gslx from 
(select bd_psndoc.pk_psndoc,
case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司')
and bd_defdoc_dwszd.name ='京内' then '京内子公司'
when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司')
and bd_defdoc_dwszd.name ='京外' then '京外子公司'
when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司')
and bd_defdoc_dwszd.name ='境外' then '境外子公司'
else '其他' end gslx --公司类型
,case when T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' )  then '经营管理' 
 when T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' ) then '专业技术' end gwxl --岗位序列
--总数（排除未评定专业技术职务）
,case when T3.glbdef4.name = '未评定专业技术职务'   then 1 end wdj --无等级
,case when (T3.glbdef4.name = '助理级专业技术职务' or  T3.glbdef4.name = '员级专业技术职务' )    then 1 end cj --初级
,case when T3.glbdef4.name = '中级专业技术职务'   then 1 end zj --中级
,case when T3.glbdef4.name = '副高级专业技术职务'   then 1 end fgj --副高级
,case when T3.glbdef4.name = '正高级专业技术职务'   then 1 end zgj --正高级
,ROW_NUMBER() OVER (PARTITION BY bd_psndoc.pk_psndoc ORDER BY T1.begindate DESC) as rn

from
bd_psndoc bd_psndoc inner join hi_psnorg hi_psnorg 
on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join hi_psnjob T1 --人员基本信息表
ON T1.pk_psndoc = bd_psndoc.pk_psndoc 

left outer join org_adminorg T2 --组织
ON T2.pk_adminorg = T1.pk_org 

left outer join org_dept org_dept --部门1
on org_dept.pk_dept = T1.pk_dept 

left outer join hi_entryapply hi_entryapply 
on hi_entryapply.pk_psnjob = T1.pk_psnjob 

Left outer join bd_psncl bd_psncl --人员类别
On T1.pk_psncl = bd_psncl.pk_psncl

Left outer join bd_defdoc bd_defdoc_zzlx--组织类型自定义档案
On T2.def2 = bd_defdoc_zzlx.pk_defdoc

left outer join bd_defdoc bd_defdoc_mz--民族
on bd_defdoc_mz.pk_defdoc = bd_psndoc.nationality

left outer join bd_defdoc bd_defdoc_zzmm--民族
on bd_defdoc_zzmm.pk_defdoc = bd_psndoc.polity

--left outer join om_postseries om_postseries --岗位序列
--on om_postseries.pk_postseries = T1.pk_postseries

left outer join bd_defdoc bd_defdoc_dwszd  --单位所在地
on T2.def4 = bd_defdoc_dwszd.pk_defdoc

left outer join hi_psndoc_glbdef18 T3 
ON T3.pk_psndoc = bd_psndoc.pk_psndoc 

where 1 = 1 and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
and T1.lastflag='Y' and T1.ismainjob='Y'  and T1.trnsevent <> '4'
and T3.glbdef8 = '10011T10000000001XG7' --是否聘任专业技术职务为'已聘任该项专业技术职务'
-- 修改：移除endflag='N'条件，允许查询离职员工
and
(T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' )  or
T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' ))
-- 修改：调整时间条件，允许查询在指定时间范围内有工作经历的员工（包括已离职）
and T1.begindate<=datefmt(parameter('param2'),'yyyy-mm-dd') and nvl(T1.enddate, '2099-12-31') >= datefmt(parameter('param1'),'yyyy-mm-dd')
and bd_psncl.name in (parameter('rylb'))
and t2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in (parameter('zzlx'))
order by T1.showorder
)a 
where rn = 1
group by gwxl,gslx order by gwxl,gslx


-- 连接结构（使用LEFT JOIN避免数据丢失）
-- t_1 LEFT JOIN t_2 ON t_1.gwxl = t_2.gwxl and t_1.gslx = t_2.gslx
-- t_1 LEFT JOIN t_3 ON t_1.gwxl = t_3.gwxl and t_1.gslx = t_3.gslx
-- t_1 LEFT JOIN t_4 ON t_1.gwxl = t_4.gwxl and t_1.gslx = t_4.gslx
-- t_1 LEFT JOIN t_5 ON t_1.gwxl = t_5.gwxl and t_1.gslx = t_5.gslx
-- t_1 LEFT JOIN t_6 ON t_1.gwxl = t_6.gwxl and t_1.gslx = t_6.gslx