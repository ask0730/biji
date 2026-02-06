-- SQL Server 调配/离职申请单数据查询脚本
-- 关联多表，筛选2025年度生效数据，导出指定字段
SELECT
    -- 人员基础信息（来自BD_PSNDOC）
    psndoc.CODE AS 人员编码,
    psndoc.NAME AS 姓名,
    psndoc.SEX AS 性别,
    psndoc.AGE AS 年龄,
    -- 原组织名称（来自ORG_ORGS，关联申请单表OLDPK_ORG）
    old_org.NAME AS 组织,
    -- 申请单核心信息（来自HI_STAPPLY）
    CONVERT(VARCHAR(10), apply.EFFECTDATE, 23) AS 生效日期,  -- 格式化日期为 yyyy-MM-dd
    CONVERT(VARCHAR(10), apply.APPROVE_TIME, 23) AS 审批时间,
    apply.BILL_CODE AS 申请单编号,
    -- 人员类别名称（来自BD_PSNCL，关联申请单表OLDPK_PSNCL）
    psncl.NAME AS 人员类别,
    -- 可选补充字段：用户账号（来自sm_user），按需保留/删除
    smu.user_code AS 账号,
    -- 可选补充字段：调配方式、流程状态，按需保留/删除
    apply.STAPPLY_MODE AS 调配方式,
    apply.WORKFLOW_STATE AS 流程状态
FROM
    HI_STAPPLY apply
-- 关联人员基本信息表
INNER JOIN BD_PSNDOC psndoc
    ON apply.PK_PSNDOC = psndoc.PK_PSNDOC
-- 关联用户表（左连接，兼容无账号的人员数据）
LEFT JOIN sm_user smu
    ON apply.PK_PSNDOC = smu.PK_PSNDOC
-- 关联原组织表
INNER JOIN ORG_ORGS old_org
    ON apply.OLDPK_ORG = old_org.PK_ORG
-- 关联人员类别表
INNER JOIN BD_PSNCL psncl
    ON apply.OLDPK_PSNCL = psncl.pk_psncl
-- 筛选条件：生效日期为2025年度（SQL Server标准日期筛选）
WHERE
    apply.EFFECTDATE >= '2025-01-01'
    AND apply.EFFECTDATE < '2026-01-01'
-- 可选排序：按生效日期、审批时间排序
ORDER BY
    apply.EFFECTDATE DESC,
    apply.APPROVE_TIME DESC;



EFFECTDATE生效日期
BILL_CODE申请单编号


BD_PSNDOC人员基本信息表：
PK_PSNDOC人员
NAME姓名
CODE人员编码
SEX性别
AGE年龄

sm_user用户表：
user_code账号
PK_PSNDOC身份_人员信息

ORG_ORGS组织表：
PK_ORG组织主键
NAME组织名称

ORG_DEPT部门表：
PK_DEPT部门主键
NAME名称

OM_POST岗位基本信息：
PK_POST岗位主键
POSTNAME岗位名称


BD_PSNCL人员类别：
pk_psncl人员分类主键
NAME人员分类名称



关联这些表，生效日期为2025.01.01-2025.12.31：
导出
人员编码，姓名，性别，年龄，组织
生效日期，审批时间，申请单编号，人员类别
SQL Server 
