import re
import time
import hashlib
import math


def load_ip_addresses(file_path: str) -> list:
    ip_addresses = []

    ip_pattern = re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    )

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:

        for line in file:

            match = ip_pattern.search(line)

            if match:
                ip = match.group()

                parts = ip.split(".")

                if all(0 <= int(part) <= 255 for part in parts):
                    ip_addresses.append(ip)

    return ip_addresses


def exact_count(ip_addresses: list) -> int:
    return len(set(ip_addresses))


class HyperLogLog:

    def __init__(self, p: int = 14):

        self.p = p
        self.m = 1 << p

        self.registers = [0] * self.m

        if self.m == 16:
            self.alpha = 0.673
        elif self.m == 32:
            self.alpha = 0.697
        elif self.m == 64:
            self.alpha = 0.709
        else:
            self.alpha = 0.7213 / (1 + 1.079 / self.m)

    def _hash(self, item: str) -> int:

        hash_bytes = hashlib.sha1(item.encode("utf-8")).digest()

        return int.from_bytes(hash_bytes[:8], byteorder="big")

    def _leading_zeros(self, value: int, bits: int) -> int:

        if value == 0:
            return bits

        return bits - value.bit_length()

    def add(self, item: str):

        x = self._hash(item)

        index = x >> (64 - self.p)

        remaining_bits = x & ((1 << (64 - self.p)) - 1)

        rank = self._leading_zeros(
            remaining_bits,
            64 - self.p
        ) + 1

        self.registers[index] = max(
            self.registers[index],
            rank
        )

    def count(self) -> int:

        indicator = sum(
            2.0 ** (-register)
            for register in self.registers
        )

        estimate = (
            self.alpha
            * (self.m ** 2)
            / indicator
        )

        empty_registers = self.registers.count(0)

        if estimate <= 2.5 * self.m and empty_registers > 0:

            estimate = (
                self.m
                * math.log(self.m / empty_registers)
            )

        return round(estimate)


def hyperloglog_count(ip_addresses: list) -> int:

    hll = HyperLogLog(p=14)

    for ip in ip_addresses:
        hll.add(ip)

    return hll.count()


def compare_methods(file_path: str):

    ip_addresses = load_ip_addresses(file_path)

    start = time.time()

    exact_result = exact_count(ip_addresses)

    exact_time = time.time() - start

    start = time.time()

    hll_result = hyperloglog_count(ip_addresses)

    hll_time = time.time() - start

    print("\nРезультати порівняння:\n")

    print(
        f"{'':<30}"
        f"{'Точний підрахунок':<25}"
        f"{'HyperLogLog':<20}"
    )

    print("-" * 75)

    print(
        f"{'Унікальні елементи':<30}"
        f"{exact_result:<25}"
        f"{hll_result:<20}"
    )

    print(
        f"{'Час виконання (сек.)':<30}"
        f"{exact_time:<25.6f}"
        f"{hll_time:<20.6f}"
    )
if __name__ == "__main__":

    compare_methods("lms-stage-access.log")
