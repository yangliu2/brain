from functools import lru_cache
from brain.memory import Memory


class Cache:

    def __init__(self,
                 memory: Memory,
                 size: int = 1000):
        self.size = size
        self.memory = memory

        # needs to decorate the class methods here with decorator parameter
        self.search_query = lru_cache(self.size)(self.search_query)

    def scan_memory(self):
        pass

    def search_query(self):
        pass


def main():
    memory = Memory(size=10000)
    cache = Cache(memory=memory,
                  size=1000)


if __name__ == "__main__":
    main()
