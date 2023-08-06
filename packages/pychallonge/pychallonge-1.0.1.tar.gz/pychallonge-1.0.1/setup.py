from distutils.core import setup
import challonge


setup(name = "pychallonge",
      author = "Russ Amos",
      author_email = "russminus@gmail.com",
      url = "http://github.com/russ-/pychallonge",
      version = challonge.__version__,
      packages = [
          'challonge',
      ],
      install_requires = [
          'python-dateutil<2.0',
      ]
)
