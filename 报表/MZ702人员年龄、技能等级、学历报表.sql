-- 单条查询（无 CTE/子查询）：所有指标用条件聚合一次性计算
select 
  T2.name as zzmc,
  case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
       when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
       when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
       when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司'
  end as gslx,
  case when T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' ) then '经营管理'
       when T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' ) then '专业技术' end as gwxl,
  sum(1) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as zs,
  sum(case when bd_defdoc_mz.name = '汉族' then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as hz,
  sum(case when bd_defdoc_mz.name <> '汉族' then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as bshz,
  sum(case when bd_psndoc.sex = 1 then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as nan,
  sum(case when bd_psndoc.sex = 2 then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as nv,
  sum(case when bd_defdoc_zzmm.name = '中共党员' then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as zgdy,
  sum(case when bd_defdoc_zzmm.name <> '中共党员' then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as bszgdy,
  sum(case when bd_psndoc.age <= 30 then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as n30,
  sum(case when bd_psndoc.age between 31 and 35 then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as n3135,
  sum(case when bd_psndoc.age between 36 and 40 then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as n3640,
  sum(case when bd_psndoc.age between 41 and 45 then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as n4145,
  sum(case when bd_psndoc.age between 46 and 50 then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as n4650,
  sum(case when bd_psndoc.age between 51 and 55 then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as n5155,
  sum(case when bd_psndoc.age >= 56 then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as n56,
  sum(case when bd_psndoc.edu.code in ('4','41','42','48','49','5','51','59','6','61','62','68','69','7','71','72','73','78','79','8','81','88','89','99','9') then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as gzjyx,
  sum(case when bd_psndoc.edu.code in ('3','31','38','39') then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as dxzk,
  sum(case when bd_psndoc.edu.code in ('2','21','28','29') then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as dxbk,
  sum(case when bd_psndoc.edu.code in ('1','14','15','16','17','18','19') then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as ss,
  sum(case when bd_psndoc.edu.code in ('0','11','12','13') then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as bs,
  -- 专业技术职务等级（仅在已聘任、且排除 trnsevent='4' 情况下计数）
  sum(case when T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and T3.glbdef4.name = '未评定专业技术职务' then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as wdj,
  sum(case when T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and (T3.glbdef4.name = '助理级专业技术职务' or T3.glbdef4.name = '员级专业技术职务') then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as cj,
  sum(case when T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and T3.glbdef4.name = '中级专业技术职务' then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as zj,
  sum(case when T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and T3.glbdef4.name = '副高级专业技术职务' then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as fgj,
  sum(case when T3.glbdef8 = '10011T10000000001XG7' and (T1.trnsevent <> '4' or T1.trnsevent is null) and T3.glbdef4.name = '正高级专业技术职务' then 1 else 0 end) over(partition by 
    case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then '母公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京内' then '京内子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='京外' then '京外子公司'
         when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name ='境外' then '境外子公司' end,
    case when T1.pk_postseries in ( '10011T100000000098AQ','10011T100000000098AT','10011T100000000098AU','10011T100000000098AV','10011T100000000098AW','10011T100000000098AX','10011T100000000098AY','10011T100000000098AZ') then '经营管理' else '专业技术' end
  ) as zgj
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
  left outer join hi_psndoc_glbdef18 T3 on T3.pk_psndoc = bd_psndoc.pk_psndoc
where 1 = 1 
  and ( hi_psnorg.indocflag = 'Y' and hi_psnorg.psntype = 0 ) 
  and T1.lastflag='Y' and T1.ismainjob='Y' 
  and (
    T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' )  or
    T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' )
  )
and T1.begindate<='2099-12-31' and nvl(T1.enddate, '2099-12-31') >= '1950-01-01'
and bd_psncl.name in (parameter('rylb'))
  and T2.name in (parameter('zzmc'))
and bd_defdoc_zzlx.name in (parameter('zzlx'))
and (
  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') 
  or (bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name in ('京内','京外','境外'))
)
-- 取消 GROUP BY，使用窗口聚合在公司类型/岗位序列维度聚合
order by 
  case when  bd_defdoc_zzlx.name in ('总部','分公司','专业机构','事业部') then 1
       when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name = '京内' then 2
       when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name = '京外' then 3
       when  bd_defdoc_zzlx.name in ('子公司','子公司下属分公司','子公司下属子公司') and bd_defdoc_dwszd.name = '境外' then 4
       else 5 end,
  case when T1.pk_postseries in ( '10011T100000000098AQ' , '10011T100000000098AT' , '10011T100000000098AU' , '10011T100000000098AV' , '10011T100000000098AW' , '10011T100000000098AX' , '10011T100000000098AY' , '10011T100000000098AZ' ) then 1
       when T1.pk_postseries in ( '10011T100000000098AR' , '10011T100000000098B0' , '10011T100000000098BB' , '10011T100000000098BP' , '10011T100000000098BQ' , '10011T100000000098BT' , '10011T100000000098BU' , '10011T100000000098BV' , '10011T100000000098BW' , '10011T100000000098BX' , '10011T100000000098BY' , '10011T100000000098BZ' , '10011T100000000098C0' , '10011T100000000098C1' , '10011T100000000098C2' , '10011T100000000098C3' , '10011T1000000000A73M' , '10011T100000000098B1' , '10011T100000000098C4' , '10011T100000000098C5' , '10011T100000000098C6' , '10011T100000000098C7' , '10011T100000000098CH' , '10011T100000000098CI' , '10011T100000000098CJ' , '10011T100000000098CK' , '10011T100000000098CL' , '10011T100000000098CM' , '10011T100000000098CN' , '10011T100000000098CO' , '10011T100000000098CP' , '10011T100000000098CQ' , '10011T100000000098CR' , '10011T100000000098CS' , '10011T100000000098CT' , '10011T100000000098CU' , '10011T100000000098DP' , '10011T100000000098DQ' , '10011T100000000098DR' , '10011T100000000098DS' , '10011T100000000098DT' , '10011T100000000098DU' , '10011T100000000098B7' , '10011T100000000098DV' , '10011T100000000098DW' , '10011T100000000098DX' , '10011T100000000098DY' , '10011T100000000098DZ' , '10011T100000000098E0' , '10011T100000000098E1' , '10011T100000000098E2' , '10011T100000000098E3' , '10011T100000000098BA' ) then 2
       else 3 end,
  T2.name
