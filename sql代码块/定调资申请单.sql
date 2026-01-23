-- 撤销环球时候遇到问题，撤销岗位失败!原因:撤销岗位引起变动的人员，有定调资关闭单据状态为[编写中]、[已提交]、[审核中]的单据


-- 查询
SELECT
    d.pk_psndoc,
    d.name,
    b.pk_psnapp
FROM bd_psndoc d
JOIN wa_psnappaprove_b b
    ON b.pk_psndoc = d.pk_psndoc
WHERE d.code IN (
    '00004658',
    '00004707',
    '00004665',
    '00004687'
);




-- 删除
DELETE FROM wa_psnappaprove_b
WHERE pk_psnapp IN (
    '10011T100000001N18MU'
);

DELETE FROM wa_psnappaprove
WHERE pk_psnapp IN (
    '10011T100000001N18MU'
);











select BILLCODE,wa_psnappaprove_b.* from wa_psnappaprove_b inner join wa_psnappaprove on wa_psnappaprove_b.pk_psnapp = wa_psnappaprove.pk_psnapp where wa_psnappaprove_b.pk_psndoc in ( N'00011T100000000QWP20' , N'00011T100000000QWP23' , N'00011T100000000QWP26' , N'00011T100000000QWWKL' , N'00011T100000000QWWKO' , N'00011T100000000QWWKR' ) and wa_psnappaprove.confirmstate in ( N'-1' , N'2' , N'3' )

SELECT
	distinct t1.BILLCODE --单据号
    ,t2.confirmstate --审批状态
    ,a1.user_name   --创建人
    ,t1.dr,t1.PK_PSNAPP --定调资申请单主键
FROM
	WA_PSNAPPAPROVE t1
left join WA_PSNAPPAPROVE_B t2 on t1.PK_PSNAPP=t2.PK_PSNAPP
left join bd_psnjob t3 on t2.pk_psnjob=t3.pk_psnjob
left join sm_user a1 on t1.creator=a1.cuserid
where t1.BILLCODE in (
,'LYBL202512010001'
,'LYBL202406280002')

SELECT
	distinct t1.BILLCODE --单据号
    ,t1.PK_PSNAPP
    ,t2.PK_WA_ITEM
    ,t3.name --薪资项目
    ,t2.PK_PSNAPP_B --定调资申请表体pk
    ,t2.PK_WA_SECLV_APPLY --薪档
FROM
	WA_PSNAPPAPROVE t1
left join WA_PSNAPPAPROVE_B t2 on t1.PK_PSNAPP=t2.PK_PSNAPP
left join WA_CLASSITEM t3 on t2.PK_WA_ITEM=t3.PK_WA_ITEM
where t1.BILLCODE in ('LYBL202506240004',
'LYBL202505070001',
'LYBL202508180007')

delete from WA_PSNAPPAPROVE where PK_PSNAPP in (
'10011T100000001L2369',
'10011T100000002DUAKI',
'00011T1000000019CHWG',
'10011T1000000028I8I9',
'00011T1000000019CHWG',
'10011T1000000028I8I9',
'10011T1000000023JPBD',
'10011T1000000023JPBD',
'10011T1000000023JPBD')
    
delete from WA_PSNAPPAPROVE_B where PK_PSNAPP in (
'10011T100000001L2369',
'10011T100000002DUAKI',
'00011T1000000019CHWG',
'10011T1000000028I8I9',
'00011T1000000019CHWG',
'10011T1000000028I8I9',
'10011T1000000023JPBD',
'10011T1000000023JPBD',
'10011T1000000023JPBD')