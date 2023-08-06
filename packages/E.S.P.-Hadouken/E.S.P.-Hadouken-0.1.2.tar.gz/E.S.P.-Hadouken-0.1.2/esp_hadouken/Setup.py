from os import walk, remove
from os.path import sep, join, exists, realpath, relpath

from Configuration import *

class Setup:

    config = Configuration(local=True)
    description = "\n" + file("description").read()

    @classmethod
    def remove_old_mainfest(self):
        path = "MANIFEST"
        if exists(path):
            remove(path)

    @classmethod
    def build_package_list(self):
        packages = []
        for root, dirs, files in walk("esp_hadouken"):
            packages.append(root.replace(sep, "."))
        return packages

    @classmethod
    def build_data_map(self):
        install_root = self.config["resources-install-path"]
        include = [(install_root, ["config", "Basic.ttf", "hi-scores"])]
        exclude = map(realpath,
                      [".git", "esp_hadouken", "vid", "aud/uncompressed", "aud/mod",
                       "img/local", "dist", "build"])
        for root, dirs, files in walk("."):
            removal = []
            for directory in dirs:
                if realpath(join(root, directory)) in exclude:
                    removal.append(directory)
            for directory in removal:
                dirs.remove(directory)
            if root != ".":
                destination = join(install_root, relpath(root))
                listing = []
                for file_name in files:
                    listing.append(join(root, file_name))
                include.append((destination, listing))
        return include

    @classmethod
    def translate_title(self):
        return self.config["game-title"].replace(" ", "-")
