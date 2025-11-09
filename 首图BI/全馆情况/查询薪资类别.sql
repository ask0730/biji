-- 查询薪资类别信息
select 
    pk_wa_class 薪资类别主键,
    code 编码,
    name 名称
from wa_waclass
where pk_wa_class = '1001A110000000009V0P'

-- 如果需要查看该薪资类别下的数据统计，可以使用以下查询：
-- select 
--     count(*) 记录数,
--     count(distinct pk_psndoc) 人员数,
--     min(cyear || '-' || cperiod) 最早期间,
--     max(cyear || '-' || cperiod) 最晚期间
-- from wa_data
-- where pk_wa_class = '1001A110000000009V0P'
--     and stopflag = 'N'
--     and dr = 0

