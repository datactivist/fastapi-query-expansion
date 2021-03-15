#! /usr/bin/python
import config as cfg
import os

# Downloading missing embeddings and converting them
print()
print("Downloading missing embeddings, this can take a while...")
os.system("python3 app/preprocess/downloadEmbeddings.py")
print("Downloading done!")
print()

if cfg.deployment_method == "local":
    os.chdir("app/")
    os.system("bash ./prestart.sh -l")
    os.system("uvicorn main:app")
elif cfg.deployment_method == "docker":
    os.system(
        "sudo docker build -t " + cfg.docker_name + ":" + cfg.docker_version + " ."
    )
else:
    raise ValueError(
        "Errors in the config file, deployment method is either 'local' or 'docker'"
    )

