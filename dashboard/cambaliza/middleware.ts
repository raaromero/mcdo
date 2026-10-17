// Vercel Routing Middleware: the whole site (page, data and images) sits behind HTTP Basic Auth.
// The password is the DASHBOARD_PASSWORD environment variable on Vercel, never in the repo; any user name works.
export const config = { matcher: "/:path*" };

export default function middleware(request: Request) {
  const want = process.env.DASHBOARD_PASSWORD;
  const auth = request.headers.get("authorization") ?? "";
  if (want && auth.startsWith("Basic ")) {
    const decoded = atob(auth.slice(6));
    if (decoded.slice(decoded.indexOf(":") + 1) === want) return;  // no response: the request goes through
  }
  return new Response("Password required.", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Two-Color Excitation", charset="UTF-8"', "Cache-Control": "no-store" },
  });
}
