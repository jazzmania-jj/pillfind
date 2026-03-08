export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const { name } = req.query;
  if (!name) return res.status(400).json({ error: 'name required' });

  const KEY = process.env.FOODSAFETY_API_KEY;
  const encoded = encodeURIComponent(name);

  try {
    // 1차: I-0040 개별인정형 원료인정현황 (751건)
    const r1 = await fetch(`https://openapi.foodsafetykorea.go.kr/api/${KEY}/I-0040/json/1/3/APLC_RAWMTRL_NM=${encoded}`);
    if (r1.ok) {
      const d1 = await r1.json();
      const rows1 = d1?.['I-0040']?.row || [];
      if (rows1.length > 0) {
        const row = rows1[0];
        return res.status(200).json({ rows: [{
          HELT_ITM_GRP_NM: row.APLC_RAWMTRL_NM,
          MLSFC_NM: '개별인정형 기능성원료',
          SCLAS_NM: '건강기능식품',
          FNCLTY_CN: row.FNCLTY_CN,
          DAY_INTK_CN: row.DAY_INTK_CN,
          IFTKN_ATNT_MATR_CN: row.IFTKN_ATNT_MATR_CN,
          source: 'I-0040'
        }], total: 1 });
      }
    }

    // 2차: I-0050 개별인정형 정보 (420건, 상하한 섭취량)
    const r2 = await fetch(`https://openapi.foodsafetykorea.go.kr/api/${KEY}/I-0050/json/1/3/RAWMTRL_NM=${encoded}`);
    if (r2.ok) {
      const d2 = await r2.json();
      const rows2 = d2?.['I-0050']?.row || [];
      if (rows2.length > 0) {
        const row = rows2[0];
        const intake = row.DAY_INTK_LOWLIMIT === row.DAY_INTK_HIGHLIMIT
          ? row.DAY_INTK_LOWLIMIT
          : `${row.DAY_INTK_LOWLIMIT} ~ ${row.DAY_INTK_HIGHLIMIT}`;
        return res.status(200).json({ rows: [{
          HELT_ITM_GRP_NM: row.RAWMTRL_NM,
          MLSFC_NM: '개별인정형 기능성원료',
          SCLAS_NM: '건강기능식품',
          FNCLTY_CN: row.PRIMARY_FNCLTY?.split('\n')[0].replace('(국문) ', ''),
          DAY_INTK_CN: intake,
          IFTKN_ATNT_MATR_CN: row.IFTKN_ATNT_MATR_CN,
          source: 'I-0050'
        }], total: 1 });
      }
    }

    // 3차: I0760 영양DB 조회 (고시형 원료)
    const r3 = await fetch(`https://openapi.foodsafetykorea.go.kr/api/${KEY}/I0760/json/1/3/HELT_ITM_GRP_NM=${encoded}`);
    if (r3.ok) {
      const d3 = await r3.json();
      const rows3 = d3?.I0760?.row || [];
      if (rows3.length > 0) {
        return res.status(200).json({ rows: rows3, total: d3?.I0760?.total_count || 0 });
      }
    }

    res.status(200).json({ rows: [], total: 0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
