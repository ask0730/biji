-- SQL Server 调配/离职申请单数据查询导出脚本
SELECT
    -- 人员基础信息
    psndoc.CODE AS 人员编码,
    suser.user_code AS 账号,
    psndoc.NAME AS 姓名,
    -- 调配核心日期信息
    CONVERT(VARCHAR(10), apply.EFFECTDATE, 23) AS 生效日期,  -- 格式化日期为 yyyy-MM-dd
    apply.STAPPLY_MODE AS 调配方式,
    -- 原组织架构信息
    old_org.NAME AS 组织,
    old_dept.NAME AS 部门,
    old_post.POSTNAME AS 岗位,
    -- 新组织架构信息
    new_org.NAME AS 新组织,
    new_dept.NAME AS 新部门,
    new_post.POSTNAME AS 新岗位,
    -- 流程与审批信息
    apply.WORKFLOW_STATE AS 流程状态,
    apply.OLDPK_PSNCL AS 人员类别,
    apply.BILL_CODE AS 申请单编号,
    CONVERT(VARCHAR(10), apply.APPROVE_TIME, 23) AS 审批时间  -- 格式化审批日期
FROM
    HI_STAPPLY apply
-- 关联人员基本信息表
LEFT JOIN BD_PSNDOC psndoc
    ON apply.PK_PSNDOC = psndoc.PK_PSNDOC
-- 关联用户表
LEFT JOIN sm_user suser
    ON apply.PK_PSNDOC = suser.PK_PSNDOC
-- 关联【原组织】表
LEFT JOIN ORG_ORGS old_org
    ON apply.OLDPK_ORG = old_org.PK_ORG
-- 关联【原部门】表
LEFT JOIN ORG_DEPT old_dept
    ON apply.OLDPK_DEPT = old_dept.PK_DEPT
-- 关联【原岗位】表
LEFT JOIN OM_POST old_post
    ON apply.OLDPK_POST = old_post.PK_POST
-- 关联【新组织】表
LEFT JOIN ORG_ORGS new_org
    ON apply.NEWPK_ORG = new_org.PK_ORG
-- 关联【新部门】表
LEFT JOIN ORG_DEPT new_dept
    ON apply.NEWPK_DEPT = new_dept.PK_DEPT
-- 关联【新岗位】表
LEFT JOIN OM_POST new_post
    ON apply.NEWPK_POST = new_post.PK_POST
-- 筛选条件：生效日期为2025年度
WHERE
    apply.EFFECTDATE >= '2025-01-01'
    AND apply.EFFECTDATE < '2026-01-01'
-- 可选排序：按生效日期、申请单编号排序
ORDER BY
    apply.BILL_CODE ASC;













HI_STAPPLY调配/离职申请单表：
PK_PSNDOC人员主键
STAPPLY_MODE调配方式
WORKFLOW_STATE流程状态
OLDPK_PSNCL人员类别
APPROVE_TIME审批时间：2025.01.01-2025.12.31
NEWPK_ORG新组织
NEWPK_POST新岗位
NEWPK_DEPT新部门
OLDPK_ORG组织
OLDPK_POST岗位
OLDPK_DEPT部门
EFFECTDATE生效日期
BILL_CODE申请单编号


BD_PSNDOC人员基本信息表：
PK_PSNDOC人员
NAME姓名
CODE人员编码

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

关联这些表，生效日期为2025.01.01-2025.12.31：
导出
人员编码，账号，姓名，生效日期，调配方式，组织，部门，岗位，新组织，新部门，新岗位
流程状态，人员类别，调配方式，申请单编号，审批时间
SQL Server 













