# Build the differert variants of the document, extract hints and solutions
# to their own chapters

import os
import shutil
import subprocess

build_dir = "__build__"

def build():
    # So far only the UGent version, ebook only.

    # Prepare build directory.
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.mkdir(build_dir)
    # Copy directories.
    chapter_dirs = ["preamble", "helmholtz", "complex", "special", "numeric",
                    "periodic", "dynamic", "styles"]
    for chapter_dir in chapter_dirs:
        shutil.copytree(chapter_dir, os.path.join(build_dir, chapter_dir))
    # Copy files.
    files = ["kaobook.cls", "kaohandt.cls", "main.tex"]
    for file in files:
        shutil.copy(file, os.path.join(build_dir, file))
    # Build.
    subprocess.run(["pdflatex", "-file-line-error", "--synctex=1",
                    "-interaction=nonstopmode",
                    os.path.join(build_dir, "main.tex")])

    
if __name__ == "__main__":
    build()
