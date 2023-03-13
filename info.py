import platformdirs
import os

author_name = "prane"
app_name = "mono"

data_dir = platformdirs.user_data_dir(app_name, author_name)
data_path = os.path.join(data_dir, "data.json")

cache_dir = platformdirs.user_cache_dir(app_name, author_name)
cache_path = os.path.join(cache_dir, "cache.json")

if __name__ == "__main__":
    print(f"{data_dir=} {cache_dir=}")
