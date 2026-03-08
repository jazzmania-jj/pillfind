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
    const url = `https://openapi.foodsafetykorea.go.kr/api/${KEY}/I0760/json/1/5/HELT_ITM_GRP_NM=${encoded}`;
    const response = await fetch(url);
    const data = await response.json();

    const rows = data?.I0760?.row || [];
    res.status(200).json({ rows, total: data?.I0760?.total_count || 0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
