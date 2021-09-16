import os
from os import path
import subprocess
import shutil

mqtt_user="ekstrah"
mqtt_pwd="test1234"
tmp_dir_path = "./ekstrah"
if path.exists(tmp_dir_path):
    shutil.rmtree(tmp_dir_path)
    os.mkdir(tmp_dir_path)
else:
    os.mkdir(tmp_dir_path)
tmp_pwd_path = tmp_dir_path + "/"+mqtt_user
creds_str = mqtt_user+":"+mqtt_pwd
with open(tmp_pwd_path, "w") as f:
    f.write(creds_str)
subprocess.call(['bash', './mqtt_pwd_gen.sh', tmp_pwd_path])

        