/**
 * Cloudflare Worker — proxy de patitasfelicesspa.cl → Cloud Run
 *
 * Cloud Run enruta según el header Host. Como la región southamerica-west1
 * no soporta "domain mappings", este Worker reescribe el destino al hostname
 * real de Cloud Run para que la petición llegue al servicio correcto.
 *
 * El navegador sigue enviando Origin/Referer = https://patitasfelicesspa.cl,
 * que Django acepta gracias a CSRF_TRUSTED_ORIGINS (ya configurado).
 */
const ORIGIN = "happypaws-app-smah3yfuuq-tl.a.run.app";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    url.hostname = ORIGIN;
    url.protocol = "https:";
    url.port = "";

    const proxied = new Request(url, request);
    // Cloud Run necesita el Host del servicio para enrutar correctamente
    proxied.headers.set("Host", ORIGIN);
    proxied.headers.set("X-Forwarded-Proto", "https");

    return fetch(proxied);
  },
};
