SELECT
  org_id,
  org_name,
  COALESCE(org_location_raw, 'unknown') AS org_location,
  COALESCE(org_type_raw, 'unknown') AS org_type,
  0 AS headcount
FROM (
  -- A：所有启用组织
  SELECT
    oa.pk_adminorg AS org_id,
    oa.name AS org_name,
    loc.name AS org_location_raw,
    orgtype.name AS org_type_raw,
    0 AS has_people
  FROM org_adminorg oa
  LEFT JOIN bd_defdoc orgtype ON oa.def2 = orgtype.pk_defdoc
  LEFT JOIN bd_defdoc loc     ON oa.def4 = loc.pk_defdoc
  WHERE oa.enablestate = 2

  UNION ALL

  -- B：有人在职的启用组织（人和岗位均满足在职口径）
  SELECT
    t2.pk_adminorg AS org_id,
    t2.name AS org_name,
    loc2.name AS org_location_raw,
    orgtype2.name AS org_type_raw,
    1 AS has_people
  FROM bd_psndoc
  INNER JOIN hi_psnorg       ON hi_psnorg.pk_psndoc = bd_psndoc.pk_psndoc
  INNER JOIN hi_psnjob  t1   ON t1.pk_psndoc = bd_psndoc.pk_psndoc
  INNER JOIN org_adminorg t2 ON t2.pk_adminorg = t1.pk_org
  LEFT JOIN bd_defdoc orgtype2 ON t2.def2 = orgtype2.pk_defdoc
  LEFT JOIN bd_defdoc loc2     ON t2.def4 = loc2.pk_defdoc
  WHERE
    bd_psndoc.enablestate = 2
    AND t2.enablestate = 2
    AND hi_psnorg.indocflag = 'Y'
    AND hi_psnorg.psntype = 0
    AND t1.endflag = 'N'
    AND t1.lastflag = 'Y'
    AND t1.ismainjob = 'Y'
    AND t1.trnsevent <> '4'
  GROUP BY
    t2.pk_adminorg, t2.name, loc2.name, orgtype2.name
) x
GROUP BY
  org_id, org_name, org_location_raw, org_type_raw
HAVING SUM(x.has_people) = 0
ORDER BY org_name