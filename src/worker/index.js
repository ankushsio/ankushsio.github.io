/**
 * Records who arrives at the portfolio, so the question "are the people I send my
 * resume to actually opening it?" has an answer.
 *
 * The resume PDF carries a tagged link (?r=cv), so an arrival with that marker is
 * provably someone holding the resume who acted on it. Anyone who was sent the PDF
 * clicks through to the site but never re-downloads the PDF, which is why logging
 * the download alone missed the entire funnel.
 *
 * Everything here is server-side: no beacon, nothing an ad blocker can strip, and
 * crawlers are visible rather than invisible. What that costs is dwell time and
 * scroll depth, which need client JS. Path sequence per visitor is the better
 * engagement proxy anyway -- "reached a case study" beats "stayed 47 seconds".
 */

/** Coarse first pass only. The `org` column does the real work: corporate link
 *  scanners (SafeLinks, Proofpoint) announce themselves as datacentre ASNs while
 *  claiming to be a browser, and a scanner fetches one URL where a human fetches
 *  several. Treat is_bot as a hint, never as truth. */
const BOT_UA =
  /bot|crawler|spider|slurp|bingpreview|facebookexternalhit|linkedin|slack|whatsapp|telegram|discord|embedly|preview|scanner|monitor|curl|wget|python-requests|headless|lighthouse|pingdom|uptime/i;

function classify(pathname) {
  if (pathname === "/ankush-jain-resume.pdf") return "resume";
  if (pathname === "/robots.txt" || pathname.startsWith("/sitemap")) return "meta";
  if (pathname.startsWith("/_astro/") || pathname === "/favicon.svg") return null;
  return "page";
}

async function visitorHash(ip, ua, day) {
  const bytes = new TextEncoder().encode(`${ip}|${ua}|${day}`);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)]
    .slice(0, 8)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function record(request, url, env) {
  const kind = classify(url.pathname);
  if (!kind || !env.VISITS) return;

  const cf = request.cf ?? {};
  const ua = request.headers.get("user-agent") ?? "";
  const ip = request.headers.get("cf-connecting-ip") ?? "";
  const now = new Date();
  const day = now.toISOString().slice(0, 10);

  await env.VISITS.prepare(
    `INSERT INTO visit
       (ts, day, visitor, kind, host, path, ref, referer, country, city, asn, org, ua, is_bot)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  )
    .bind(
      now.toISOString(),
      day,
      await visitorHash(ip, ua, day),
      kind,
      url.hostname,
      url.pathname,
      url.searchParams.get("r"),
      request.headers.get("referer"),
      cf.country ?? null,
      cf.city ?? null,
      cf.asn ?? null,
      cf.asOrganization ?? null,
      ua,
      BOT_UA.test(ua) ? 1 : 0,
    )
    .run();
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Awaiting resolves headers only -- the body still streams -- so this costs no
    // latency and lets us see the status before deciding to record.
    const response = await env.ASSETS.fetch(request);

    // Record successful responses only, which excludes two kinds of noise.
    //
    // 3xx: html_handling sends /resume to /resume/ with a 307. Logging both hops
    // double-counts every navigation that omits a trailing slash and silently
    // inflates session depth. The query string survives the redirect, so the ?r=
    // marker is still captured on the 200 that follows.
    //
    // 4xx: every public domain is scanned constantly for /xmlrpc.php,
    // /wp-includes/... and friends. Those 404s are not page views, and left in they
    // quickly outnumber real traffic and ruin the "read the last 30 rows" view.
    // Genuinely broken internal links are already caught by the CI coverage check.
    const isSuccess = response.status >= 200 && response.status < 300;

    if (isSuccess) {
      // The write happens in waitUntil so a slow or broken D1 can never delay -- or
      // break -- the page a recruiter is waiting on.
      ctx.waitUntil(
        record(request, url, env).catch((err) => {
          console.log(
            JSON.stringify({ event: "visit_record_failed", message: String(err) }),
          );
        }),
      );
    }

    return response;
  },
};
