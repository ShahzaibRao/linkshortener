import http from 'k6/http';
import { check } from 'k6';

const BASE = 'http://127.0.0.1:8080';
const CODE = 'seed000077';  // iska uv pehle 0 hai (sirf seed000042 test hua tha)

export default function () {
  // har iteration = ek naya unique visitor
  const visitor = `user-${__VU}-${__ITER}-${Math.random().toString(36).slice(2, 10)}`;
  const res = http.get(`${BASE}/${CODE}`, {
    headers: { 'X-Visitor-Id': visitor },
    redirects: 0,
  });
  check(res, { 'redirect 307': (r) => r.status === 307 });
}

