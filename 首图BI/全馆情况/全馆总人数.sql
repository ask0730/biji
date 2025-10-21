SELECT COUNT(DISTINCT bd_psndoc.pk_psndoc) AS 当前总人数
FROM bd_psndoc  -- 人员档案表
-- 关联最新的岗位信息，确保在职状态
INNER JOIN hi_psnjob T1 
  ON T1.pk_psndoc = bd_psndoc.pk_psndoc
  AND T1.lastflag = 'Y'  -- 最新岗位记录
  AND T1.ismainjob = 'Y'  -- 主岗位（避免兼职重复计数）
  AND T1.endflag = 'N'  -- 岗位未结束（在职）
WHERE 
  bd_psndoc.enablestate = 2  -- 人员状态为“启用”（有效）
;