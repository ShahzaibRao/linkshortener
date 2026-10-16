import http from "k6/http";
import { check } from "k6";

export const options = {
  vus: 100,
  duration: "30s",
};

// Test se pehle EK BAAR chalta hai: apna link khud banao
export function setup() {
  const res = http.post(
    "http://127.0.0.1:8080/api/v1/links",
    JSON.stringify({ url: "https://example.com/load-test" }),
    { headers: { "Content-Type": "application/json" } }
  );
  check(res, { "setup: link created": (r) => r.status === 200 });
  return { code: res.json().code };
}

// Har virtual user ye chalata hai; setup() ka return 'data' mein milta hai
export default function (data) {
  const res = http.get(`http://127.0.0.1:8080/api/v1/links/${data.code}/stats`);
  check(res, { "status is 200": (r) => r.status === 200 });
}
