-- Operations: retrospective robust screen; no claim of a live predictive alert.
WITH d AS (SELECT date_key,sum(net_pence)/100.0 net_gbp FROM mart.daily_country GROUP BY 1),
baseline AS (SELECT median(net_gbp) med FROM d),
spread AS (SELECT median(abs(net_gbp-med)) mad FROM d CROSS JOIN baseline)
SELECT d.*,med,mad,.6745*(net_gbp-med)/nullif(mad,0) robust_z,
abs(.6745*(net_gbp-med)/nullif(mad,0))>5 flag
FROM d CROSS JOIN baseline CROSS JOIN spread ORDER BY abs(robust_z) DESC;
