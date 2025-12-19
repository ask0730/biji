-- 查询人员编码00004559的最新任职受雇从业日期
-- 使用子查询确保只返回一条记录（即使数据中存在多条lastflag='Y'和ismainjob='Y'的记录）
SELECT 
    bd_psndoc.code AS 人员编码,
    bd_psndoc.name AS 姓名,
    hi_psnjob.jobglbdef25 AS 任职受雇从业日期,
    hi_psnjob.begindate AS 任职开始日期,
    hi_psnjob.enddate AS 任职结束日期
FROM bd_psndoc  -- 人员基本信息表
LEFT JOIN (
    -- 使用子查询，通过排序确保只取最新的一条记录
    SELECT 
        pk_psndoc,
        jobglbdef25,
        begindate,
        enddate
    FROM (
        SELECT 
            pk_psndoc,
            jobglbdef25,
            begindate,
            enddate,
            ROW_NUMBER() OVER (
                PARTITION BY pk_psndoc 
                ORDER BY begindate DESC, ts DESC
            ) AS rn
        FROM hi_psnjob
        WHERE lastflag = 'Y'  -- 最新记录
          AND ismainjob = 'Y'  -- 主职记录
    ) t
    WHERE rn = 1  -- 只取第一条记录
) hi_psnjob
    ON hi_psnjob.pk_psndoc = bd_psndoc.pk_psndoc
WHERE 
    bd_psndoc.code = '00004559'  -- 人员编码
;
