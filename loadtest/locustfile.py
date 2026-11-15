from locust import task
from locust.contrib.fasthttp import FastHttpUser

# ~1000 tokens x 50ms = ~50s per stream: longer than the ramp, so all users hold a connection at once.
PROMPT = " ".join(["w"] * 1000)


class StreamUser(FastHttpUser):
    @task
    def stream(self):
        with self.client.get(
            "/stream",
            params={"prompt": PROMPT},
            stream=True,
            catch_response=True,
        ) as r:
            if r.status_code != 200:
                r.failure(f"status {r.status_code}: {r.error!r}")
                return
            body = "".join(r.iter_content())
            if "event: done" in body:
                r.success()
            else:
                r.failure("stream ended without done event")
