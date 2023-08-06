from distutils.core import setup
from distutils.command.install_data import install_data
from os import system, chmod
from os.path import join, exists, basename

from esp_hadouken.Setup import *

config = Setup.config

CLASSIFIERS = ["Topic :: Games/Entertainment",
               "Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games",
               "Topic :: Software Development :: Libraries :: pygame",
               "Programming Language :: Python :: 2.7",
               "Environment :: X11 Applications",
               "Development Status :: 4 - Beta",
               "License :: Freely Distributable",
               "Operating System :: OS Independent"]


class hi_scores_install(install_data):

    def copy_file(self, infile, outfile):
        if self.is_high_scores_file(infile) and exists(join(outfile, infile)):
            print "leaving existing hi-scores file"
            return "", ""
        return install_data.copy_file(self, infile, outfile)

    def run(self):
        install_data.run(self)
        for path in self.outfiles:
            if self.is_high_scores_file(path):
                print "making hi-scores globally writable"
                chmod(path, 0666)

    def is_high_scores_file(self, path):
        return basename(path) == "hi-scores"
    

Setup.remove_old_mainfest()

system("mv hi-scores hi-scores.bk")
system("touch hi-scores")

setup(cmdclass={"install_data": hi_scores_install},
      name=Setup.translate_title(),
      version=config["game-version"],
      description=config["game-summary"],
      long_description=Setup.description,
      license=config["game-license"],
      platforms=config["game-platforms"],
      author=config["contact-name"],
      author_email=config["contact-email"],
      url=config["game-url"],
      download_url=config["game-url"],
      packages=Setup.build_package_list(),
      scripts=["esp-hado"],
      classifiers=CLASSIFIERS,
      requires=["pygame"],
      data_files=Setup.build_data_map())

system("mv hi-scores.bk hi-scores")
