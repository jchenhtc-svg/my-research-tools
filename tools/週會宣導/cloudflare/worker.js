/**
 * 週會宣導 — 回應收集用的 Cloudflare Worker
 *
 * 兩個端點：
 *   POST /submit     寫入一則回應到 D1
 *   GET  /responses  讀出回應（可用 ?episode=xxx 篩選單一篇集）
 *
 * SITE_KEY 不是真正的身分驗證，只是一個簡單的防呆／防隨機掃描機器人的
 * 門檻——這個 Worker 網址一旦被知道，理論上任何人都能打，SITE_KEY
 * 只是讓「不小心路過」的機器人寫不進去，不是拿來擋蓄意攻擊的。
 * 部署時用 `npx wrangler secret put SITE_KEY` 設定實際的值。
 */

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*", // 播放器是 file:// 開啟，Origin 會是 "null"，用 * 才會過
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-Site-Key",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...CORS_HEADERS },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    if (url.pathname === "/submit" && request.method === "POST") {
      if (env.SITE_KEY && request.headers.get("X-Site-Key") !== env.SITE_KEY) {
        return json({ error: "unauthorized" }, 401);
      }
      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "invalid json" }, 400);
      }
      const episode = String(body.episode || "").slice(0, 200);
      const question = String(body.question || "").slice(0, 500);
      const response = String(body.response || "").trim().slice(0, 1000);
      const submittedAt = new Date().toISOString();
      if (!episode || !response) {
        return json({ error: "episode and response are required" }, 400);
      }
      await env.DB.prepare(
        "INSERT INTO responses (episode, question, response, submitted_at) VALUES (?, ?, ?, ?)"
      ).bind(episode, question, response, submittedAt).run();
      return json({ ok: true });
    }

    if (url.pathname === "/responses" && request.method === "GET") {
      if (env.SITE_KEY && request.headers.get("X-Site-Key") !== env.SITE_KEY) {
        return json({ error: "unauthorized" }, 401);
      }
      const episode = url.searchParams.get("episode");
      const stmt = episode
        ? env.DB.prepare("SELECT episode, question, response, submitted_at FROM responses WHERE episode = ? ORDER BY id DESC").bind(episode)
        : env.DB.prepare("SELECT episode, question, response, submitted_at FROM responses ORDER BY id DESC");
      const { results } = await stmt.all();
      return json({ responses: results });
    }

    return json({ error: "not found" }, 404);
  },
};
