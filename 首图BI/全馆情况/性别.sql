SELECT 
    T1.pk_psnjob,
    bd_psndoc.code,
    bd_psndoc.name,
    bd_psndoc.age 年龄,
    CASE 
        WHEN bd_psndoc.sex = 1 THEN '男'
        WHEN bd_psndoc.sex = 2 THEN '女'
        ELSE '未知'
    END AS 性别,
    1 AS 人数
FROM bd_psndoc bd_psndoc  -- 人员档案表
-- 关联最新的岗位信息，确保在职状态
INNER JOIN hi_psnjob T1 
    ON T1.pk_psndoc = bd_psndoc.pk_psndoc
    AND T1.lastflag = 'Y'  -- 最新岗位记录
    AND T1.ismainjob = 'Y'  -- 主岗位（避免兼职重复计数）
    AND T1.endflag = 'N'  -- 岗位未结束（在职）
WHERE 
    bd_psndoc.enablestate = 2  -- 人员状态为"启用"（有效）
ORDER BY T1.showorder


