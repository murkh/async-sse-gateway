// k6 run -e HOST=http://localhost:8000 loadtest/k6.js
// Built-in http buffers the whole body: measures concurrency + completion, not time-to-first-token (needs xk6-sse).
import http from "k6/http";
import { check } from "k6";

const HOST = __ENV.HOST;
if (!HOST) throw new Error("HOST is required: k6 run -e HOST=http://localhost:8000 loadtest/k6.js");

// ~1000 tokens x 50ms = ~50s per stream, matching locustfile.py.
const PROMPT = Array(1000).fill("w").join(" ");

export const options = {
  stages: [
    { duration: "80s", target: 10000 }, // 125 new connections/s
    { duration: "30s", target: 10000 },
    { duration: "10s", target: 0 },
  ],
  thresholds: { checks: ["rate>0.99"] },
};

export default function () {
  const r = http.get(`${HOST}/stream?prompt=${encodeURIComponent(PROMPT)}`, { timeout: "120s" });
  check(r, {
    "status 200": (res) => res.status === 200,
    "done event": (res) => res.body.includes("event: done"),
  });
}
