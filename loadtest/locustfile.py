from locust import HttpUser, task


class StreamUser(HttpUser):
    @task
    def stream(self):
        with self.client.get(
            "/stream",
            params={"prompt": "load test prompt"},
            stream=True,
            catch_response=True,
        ) as r:
            if r.status_code != 200:
                r.failure(f"status {r.status_code}")
                return
            for line in r.iter_lines(decode_unicode=True):
                if line == "event: done":
                    r.success()
                    return
            r.failure("stream ended without done event")
