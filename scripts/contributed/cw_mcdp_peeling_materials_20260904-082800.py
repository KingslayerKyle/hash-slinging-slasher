"""Recovers uncarried mcdp ceiling peeling materials in Cold War."""
import sys

def main():
    missions = ["stk", "kgb", "ame", "nam", "yam", "cub", "tak", "arm", "dug", "hub"]
    for m in missions:
        for i in range(1, 10):
            sys.stdout.write(f"mcdp/mtl_{m}_ceiling_peeling_{i:02d}\n")
            sys.stdout.write(f"mcdp/mtl_{m}_ceiling_peeling_{i}\n")

if __name__ == "__main__":
    main()
