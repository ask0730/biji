SELECT
  d.code  AS dept_code,
  d.name  AS dept_name,
  p.code  AS parent_dept_code,
  p.name  AS parent_dept_name,
  o.code  AS org_code,
  o.name  AS org_name
FROM org_dept d
LEFT JOIN org_dept p
  ON p.pk_dept = d.pk_fatherorg
LEFT JOIN org_orgs o
  ON o.pk_org = d.pk_org
WHERE d.enablestate = 2  -- 仅启用部门；如需全部可注释本行
ORDER BY o.code, ISNULL(p.code, '0'), d.code;