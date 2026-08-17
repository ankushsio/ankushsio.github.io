/**
 * The portfolio is 100% static assets. This Worker is invoked for exactly one path --
 * the resume PDF -- via `assets.run_worker_first` in wrangler.jsonc. Everything else is
 * served directly from the asset store and never reaches this code.
 *
 * The point is the one signal GitHub Pages could never give: who actually pulled the
 * resume. Cloudflare fills request.cf at the edge, so the log line carries geography and
 * the requesting network without any client-side script that an ad blocker can strip.
 */
export default {
  async fetch(request, env) {
    const cf = request.cf ?? {};

    const url = new URL(request.url);

    console.log(
      JSON.stringify({
        event: "resume_download",
        // Preview branches serve the same Worker, so their logs land in the same place.
        // Filter on host to separate real traffic from a *.workers.dev preview.
        host: url.hostname,
        path: url.pathname,
        country: cf.country ?? null,
        city: cf.city ?? null,
        asn: cf.asn ?? null,
        // The organisation behind the ASN -- this is the field that distinguishes a
        // recruiter on a corporate network from a residential ISP or a crawler.
        org: cf.asOrganization ?? null,
        referer: request.headers.get("referer"),
        userAgent: request.headers.get("user-agent"),
      }),
    );

    // Hand back to the asset store; the PDF itself is still served by Cloudflare.
    return env.ASSETS.fetch(request);
  },
};
