"""Bloom filter — "kya ye code exist karta hai?" ka tez jawab.

- "nahi hai" → 100% pakka (false negative kabhi nahi)
- "shayad hai" → ho sakta hai ghalat ho (false positive) — isi liye DB/Redis check zaroori hai
- Items store nahi karta, sirf unke nishan (bits) — isi liye chhota hai
"""

import hashlib
import math


class BloomFilter:
    def __init__(self, capacity: int, error_rate: float = 0.01):
        # Kitne bits chahiye? Formula: m = -(n * ln(p)) / (ln2)^2
        self.size = int(-(capacity * math.log(error_rate)) / (math.log(2) ** 2))
        # Kitne hash functions? k = (m/n) * ln2
        self.hash_count = max(1, int((self.size / capacity) * math.log(2)))
        # Bits ki patti (bytearray = har byte mein 8 bits)
        self.bits = bytearray((self.size + 7) // 8)
        self.capacity = capacity

    def _positions(self, key: str):
        # 2 hash se k positions (double hashing trick)
        h1 = int(hashlib.md5(key.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size

    def add(self, key: str) -> None:
        """Naya key filter mein daalo."""
        for pos in self._positions(key):
            self.bits[pos // 8] |= 1 << (pos % 8)

    def __contains__(self, key: str) -> bool:
        """'code' in filter → True = shayad hai, False = pakka nahi hai."""
        return all(
            self.bits[pos // 8] & (1 << (pos % 8))
            for pos in self._positions(key)
        )

    def stats(self) -> dict:
        return {
            "size_kb": round(self.size / 8 / 1024, 2),
            "hash_functions": self.hash_count,
            "capacity": self.capacity,
        }

