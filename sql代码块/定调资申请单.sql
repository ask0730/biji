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
    '00011T100000000T2LQZ',
    '00011T100000000T2LS1',
    '10011T10000000231T0Z'
);

DELETE FROM wa_psnappaprove
WHERE pk_psnapp IN (
    '00011T100000000T2LQZ',
    '00011T100000000T2LS1',
    '00011T100000000T2AO0',
    '10011T100000001N1576',
    '10011T10000000231P6T',
    '10011T10000000231T0Z'
);