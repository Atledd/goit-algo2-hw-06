import hashlib


class BloomFilter:
    def __init__(self, size: int, num_hashes: int):
        if not isinstance(size, int) or size <= 0:
            raise ValueError("size має бути додатним цілим числом")
        if not isinstance(num_hashes, int) or num_hashes <= 0:
            raise ValueError("num_hashes має бути додатним цілим числом")

        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size

    def _hashes(self, item: str):
        for i in range(self.num_hashes):
            data = f"{item}_{i}".encode("utf-8")
            hash_value = int(hashlib.sha256(data).hexdigest(), 16)
            yield hash_value % self.size

    def add(self, item: str):
        if not isinstance(item, str) or item == "":
            return

        for index in self._hashes(item):
            self.bit_array[index] = 1

    def contains(self, item: str) -> bool:
        if not isinstance(item, str) or item == "":
            return False

        return all(self.bit_array[index] == 1 for index in self._hashes(item))


def check_password_uniqueness(bloom_filter: BloomFilter, passwords: list) -> dict:
    results = {}

    for password in passwords:
        if not isinstance(password, str) or password == "":
            results[str(password)] = "некоректний пароль"
        elif bloom_filter.contains(password):
            results[password] = "вже використаний"
        else:
            results[password] = "унікальний"
            bloom_filter.add(password)

    return results


if __name__ == "__main__":
    bloom = BloomFilter(size=1000, num_hashes=3)

    existing_passwords = ["password123", "admin123", "qwerty123"]

    for password in existing_passwords:
        bloom.add(password)

    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]

    results = check_password_uniqueness(bloom, new_passwords_to_check)

    for password, status in results.items():
        print(f"Пароль '{password}' — {status}.")
