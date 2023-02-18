import platformdirs
import os

author_name = "prane"
app_name = "mono"

data_dir = platformdirs.user_data_dir(app_name, author_name)
data_path = os.path.join(data_dir, "data.json")
