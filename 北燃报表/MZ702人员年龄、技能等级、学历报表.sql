-- 展开组织名称，但数值按公司类型与岗位序列汇总
select 
  agg.orgname,
  agg.gwxl,
  agg.gwxl as gslx,
  agg.zs,
  agg.hz,
  agg.bshz,
  agg.nan,
  agg.nv,
  agg.zgdy,
  agg.bszgdy,
  agg.n30,
  agg.n3135,
  agg.n3640,
  agg.n4145,
  agg.n4650,
  agg.n5155,
  agg.n56,
  agg.gzjyx,
  agg.dxzk,
  agg.dxbk,
  agg.ss,
  agg.bs,
  agg.wdj,
  agg.cj,
  agg.zj,
  agg.fgj,
  agg.zgj,
  cast('' as varchar(20)) as rq,
  cast('' as varchar(200)) as rylb,
  cast('' as varchar(200)) as zzlx,
  cast('' as varchar(200)) as dwszd,
  cast('' as varchar(200)) as zzmc
from (
  select 
    T2.name as orgname,
    case when T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' ) then '经营管理'
         when T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' ) then '专业技术' end as gwxl,
    count(distinct bd_psndoc.pk_psndoc) as zs,
    count(distinct case when bd_defdoc_mz.name = '汉族' then bd_psndoc.pk_psndoc end) as hz,
    count(distinct case when bd_defdoc_mz.name <> '汉族' then bd_psndoc.pk_psndoc end) as bshz,
    count(distinct case when bd_psndoc.sex = 1 then bd_psndoc.pk_psndoc end) as nan,
    count(distinct case when bd_psndoc.sex = 2 then bd_psndoc.pk_psndoc end) as nv,
    count(distinct case when bd_defdoc_zzmm.name = '中共党员' then bd_psndoc.pk_psndoc end) as zgdy,
    count(distinct case when bd_defdoc_zzmm.name <> '中共党员' then bd_psndoc.pk_psndoc end) as bszgdy,
    count(distinct case when bd_psndoc.age <= 30 then bd_psndoc.pk_psndoc end) as n30,
    count(distinct case when bd_psndoc.age between 31 and 35 then bd_psndoc.pk_psndoc end) as n3135,
    count(distinct case when bd_psndoc.age between 36 and 40 then bd_psndoc.pk_psndoc end) as n3640,
    count(distinct case when bd_psndoc.age between 41 and 45 then bd_psndoc.pk_psndoc end) as n4145,
    count(distinct case when bd_psndoc.age between 46 and 50 then bd_psndoc.pk_psndoc end) as n4650,
    count(distinct case when bd_psndoc.age between 51 and 55 then bd_psndoc.pk_psndoc end) as n5155,
    count(distinct case when bd_psndoc.age >= 56 then bd_psndoc.pk_psndoc end) as n56,
    count(distinct case when defdoc.code in ('4','41','42','48','49','5','51','59','6','61','62','68','69','7','71','72','73','78','79','8','81','88','89','99','9') then bd_psndoc.pk_psndoc end) as gzjyx,
    count(distinct case when defdoc.code in ('3','31','38','39') then bd_psndoc.pk_psndoc end) as dxzk,
    count(distinct case when defdoc.code in ('2','21','28','29') then bd_psndoc.pk_psndoc end) as dxbk,
    count(distinct case when defdoc.code in ('1','14','15','16','17','18','19') then bd_psndoc.pk_psndoc end) as ss,
    count(distinct case when defdoc.code in ('0','11','12','13') then bd_psndoc.pk_psndoc end) as bs,
    count(distinct case when (T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and (defdoc_1.name = '未评定专业技术职务' or defdoc_1.name = '没有取得资格证书' or defdoc_1.name is null)) 
                           or (T3.pk_psndoc is null) 
                           or (T3.glbdef8 is null)
                           or (T3.glbdef4 is null)
                      then bd_psndoc.pk_psndoc end) as wdj,
    count(distinct case when T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and (defdoc_1.name = '助理级专业技术职务' or defdoc_1.name = '员级专业技术职务') then bd_psndoc.pk_psndoc end) as cj,
    count(distinct case when T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and defdoc_1.name = '中级专业技术职务' then bd_psndoc.pk_psndoc end) as zj,
    count(distinct case when T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and defdoc_1.name = '副高级专业技术职务' then bd_psndoc.pk_psndoc end) as fgj,
    count(distinct case when T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and defdoc_1.name = '正高级专业技术职务' then bd_psndoc.pk_psndoc end) as zgj
  from 
  bd_psndoc bd_psndoc 
    inner join hi_psnorg hi_psnorg on hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc 
    left outer join hi_psnjob T1 on T1.pk_psndoc = bd_psndoc.pk_psndoc 
    left outer join org_adminorg T2 on T2.pk_adminorg = T1.pk_org 
    left outer join org_dept org_dept on org_dept.pk_dept = T1.pk_dept 
    left outer join bd_psncl bd_psncl on T1.pk_psncl = bd_psncl.pk_psncl
    left outer join bd_defdoc bd_defdoc_zzlx on T2.def2 = bd_defdoc_zzlx.pk_defdoc
    left outer join bd_defdoc bd_defdoc_mz on bd_defdoc_mz.pk_defdoc = bd_psndoc.nationality
    left outer join bd_defdoc bd_defdoc_zzmm on bd_defdoc_zzmm.pk_defdoc = bd_psndoc.polity
    left outer join bd_defdoc bd_defdoc_dwszd on T2.def4 = bd_defdoc_dwszd.pk_defdoc
    left outer join hi_psndoc_glbdef18 T3 on T3.pk_psndoc = bd_psndoc.pk_psndoc and T3.glbdef8 = '10011T10000000001XG7'
    left join bd_defdoc defdoc on bd_psndoc.edu = defdoc.pk_defdoc
    left join bd_defdoc defdoc_1 on T3.glbdef4 = defdoc_1.pk_defdoc
  where 1 = 1 
    and hi_psnorg.psntype = 0
    and T1.ismainjob='Y'
  -- 单日筛选：任职时间包含所选日期
  and T1.begindate<=parameter('rq') and nvl(T1.enddate, '2099-12-31') >= parameter('rq')
    and bd_psncl.name in (parameter('rylb'))
    and bd_defdoc_zzlx.name in (parameter('zzlx'))
    and bd_defdoc_dwszd.name in (parameter('dwszd'))
    and bd_defdoc_zzlx.name is not null
    and bd_defdoc_dwszd.name is not null
    and T2.name in (parameter('zzmc'))
  -- 岗位序列筛选迁移至外层：按列名 agg.gwxl 过滤
  -- 仅保留两大岗位序列编码，排除未归类/空
  and (
      T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' )
      or T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' )
  )
  -- 去重：对每个人在每个组织类型+岗位序列下，在时间段内选择最新的记录
  and T1.pk_psnjob = (
    select top 1 T1_dedup.pk_psnjob
    from hi_psnjob T1_dedup
    left outer join org_adminorg T2_dedup on T2_dedup.pk_adminorg = T1_dedup.pk_org
    left outer join bd_psncl bd_psncl_dedup on T1_dedup.pk_psncl = bd_psncl_dedup.pk_psncl
    left outer join bd_defdoc bd_defdoc_zzlx_dedup on T2_dedup.def2 = bd_defdoc_zzlx_dedup.pk_defdoc
    left outer join bd_defdoc bd_defdoc_dwszd_dedup on T2_dedup.def4 = bd_defdoc_dwszd_dedup.pk_defdoc
    where T1_dedup.pk_psndoc = T1.pk_psndoc
      and T1_dedup.ismainjob='Y'
    -- 单日内有效的记录
    and T1_dedup.begindate<=parameter('rq') and nvl(T1_dedup.enddate, '2099-12-31') >= parameter('rq')
      -- 必须满足主查询的筛选条件（关键修改）
      and bd_psncl_dedup.name in (parameter('rylb'))
      and bd_defdoc_zzlx_dedup.name in (parameter('zzlx'))
      and bd_defdoc_dwszd_dedup.name in (parameter('dwszd'))
      and bd_defdoc_zzlx_dedup.name is not null
      and bd_defdoc_dwszd_dedup.name is not null
      and T2_dedup.name in (parameter('zzmc'))
      -- 同一组织名称
      and T2_dedup.name = T2.name
      -- 同一岗位序列
      and T1_dedup.pk_postseries = T1.pk_postseries
    order by T1_dedup.enddate desc, T1_dedup.begindate desc, T1_dedup.ts desc
  )
  group by 
    T2.name,
    case when T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' ) then '经营管理'
         when T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' ) then '专业技术' end
) agg
where agg.gwxl in (parameter('gwxl'))