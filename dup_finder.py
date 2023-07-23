import os
import pprint
import itertools
import hashlib


def sha256sum(filename):
    # https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


def find_dups_by_size(root):
    size_map = {}
    for subdir, dirs, files in os.walk(root):
        for file in files:
            full_size_path = os.path.join(subdir, file)
            file_stats = os.stat(full_size_path)
            size = file_stats.st_size
            if size in size_map:
                size_map[size].append(full_size_path)
            else:
                size_map[size] = [full_size_path]
            # print(os.path.join(subdir, file))
    size_map = {size: files for size, files in size_map.items() if len(files) > 1}
    return size_map


def find_dups_by_hash(size_map):
    hash_map = {}
    for size, file_list in size_map.items():
        for filename in file_list:
            hash = sha256sum(filename)
            if hash in hash_map:
                hash_map[hash].append(filename)
            else:
                hash_map[hash] = [filename]

    hash_map = {hash: files for hash, files in hash_map.items() if len(files) > 1}
    return hash_map


def find_dups(root):
    size_map = find_dups_by_size(root)
    hash_map = find_dups_by_hash(size_map)
    return hash_map


def find_folder_pairs_with_lots_of_dups(hash_map):
    folders_with_dups = {}
    for files in hash_map.values():
        for first, second in itertools.combinations(files, r=2):
            dup_folder_pair = (
                os.path.dirname(first),
                os.path.dirname(second),
            )
            if dup_folder_pair in folders_with_dups:
                folders_with_dups[dup_folder_pair].append((first, second))
            else:
                folders_with_dups[dup_folder_pair] = [(first, second)]
    return folders_with_dups


if __name__ == "__main__":
    hash_map = find_dups("/home/jm/phone_dump_july22_2023")
    pprint.pprint(hash_map)
    folders_with_dups = find_folder_pairs_with_lots_of_dups(hash_map)
    for pair, values in folders_with_dups.items():
        print(f"{pair}: {len(values)}")
