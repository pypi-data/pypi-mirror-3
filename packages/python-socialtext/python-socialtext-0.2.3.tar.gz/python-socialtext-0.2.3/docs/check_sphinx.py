import os
import subprocess

def test_linkcheck():
    tmpdir = os.path.abspath(os.path.dirname(__file__))
    doctrees = os.path.join(tmpdir, "_build", "doctrees")
    htmldir = os.path.join(tmpdir, "_build", "html")
    subprocess.check_call(
        ["sphinx-build", "-W", "-blinkcheck",
          "-d", str(doctrees), ".", str(htmldir)])

def test_build_docs():
    tmpdir = os.path.abspath(os.path.dirname(__file__))
    doctrees = os.path.join(tmpdir, "_build", "doctrees")
    htmldir = os.path.join(tmpdir, "_build", "html")
    subprocess.check_call([
        "sphinx-build", "-W", "-bhtml",
          "-d", str(doctrees), ".", str(htmldir)])