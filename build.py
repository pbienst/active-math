# Build the different variants of the document, extract hints and solutions
# to their own chapters

import os
import re
import glob
import gzip
import shutil
import subprocess

build_dir = "__build__"

re_exer = re.compile(r"""\\begin{exer}(.*?)\\end{exer}""", re.DOTALL)
re_sol = re.compile(r"""\\begin{sol}(.*?)\\end{sol}""", re.DOTALL)
re_hnt = re.compile(r"""\\begin{hnt}(.*?)\\end{hnt}""", re.DOTALL)
re_yt = re.compile(r"""% youtube: (.+?)\s""", re.DOTALL)
re_jup = re.compile(r"""% jupyter: (.+?)\s""", re.DOTALL)

def process_exer(chapter_dirs):
    with open(os.path.join(build_dir, "solutions.tex"), 'w') as sol_file:
        sol_file.write("""\\chapter{Solutions to selected exercises}
\\setlength{\\columnsep}{18pt}
\\def\\columnseprulecolor{\\color{white}} 
\\begin{multicols*}{2}
""")
        with open(os.path.join(build_dir, "hints.tex"), 'w') as hnt_file:
            hnt_file.write("""\\chapter{Hints for selected exercises}
\\setlength{\\columnsep}{18pt}
\\def\\columnseprulecolor{\\color{white}} 
\\begin{multicols*}{2}
""")        
            chapter_counter = -1 # Preamble
            for chapter_dir in chapter_dirs:
                exer_counter = 0
                chapter_file = glob.glob(os.path.join(build_dir,
                    chapter_dir, "*.tex"))[0]
                chapter_text = open(chapter_file, 'r').read()
                new_chapter_text = chapter_text
                for exer_match in re_exer.finditer(chapter_text):
                    exer_counter += 1
                    exer_label = f"exer_{chapter_counter}_{exer_counter}"
                    sol_label = f"sol_{chapter_counter}_{exer_counter}"
                    hnt_label = f"hnt_{chapter_counter}_{exer_counter}"
                    exer_text = f"\\label{{{exer_label}}}" + exer_match.group(1)
                    # Extract solution.
                    sol_match = re_sol.search(exer_text)
                    if sol_match:
                        link_text = f"Exer. {chapter_counter}.{exer_counter}"
                        sol_file.write(\
                f"\\hyperref[{exer_label}]{{\\textbf{{{link_text}}}}}" + \
                        f"\\label{{{sol_label}}}" + sol_match.group(1) + "\n")
                        exer_text = exer_text.replace(sol_match.group(0), "")
                    # Extract hint.   
                    hnt_match = re_hnt.search(exer_text)
                    if hnt_match:
                        link_text = f"Exer. {chapter_counter}.{exer_counter}"
                        hnt_file.write(\
                f"\\hyperref[{exer_label}]{{\\textbf{{{link_text}}}}}" + \
                        f"\\label{{{hnt_label}}}" + hnt_match.group(1) + "\n")
                        exer_text = exer_text.replace(hnt_match.group(0), "")
                    # Add icons.
                    icons = "\\noindent\\marginnote[\\iconmarginoffset]{"
                    if "% difficulty: trivial" in exer_text:
                        icons += "\\trivial\\,"
                    if "% difficulty: normal" in exer_text:
                        icons += "\\normal\\,"
                    if "% difficulty: hard" in exer_text:
                        icons += "\\hard\\,"
                    if hnt_match:
                        icons += f"\\hyperref[{hnt_label}]{{\\hint}}\\,"
                    if sol_match:
                        icons += f"\\hyperref[{sol_label}]{{\\solution}}\\,"
                    yt_match = re_yt.search(exer_text)
                    if yt_match:
                        icons += \
                f"\\href{{https://youtu.be/{yt_match.group(1)}}}{{\\youtube}}\\,"
                    jup_match = re_jup.search(exer_text)
                    if jup_match:
                        icons += \
                 f"\\href{{{jup_match.group(1)}}}{{\\jupyter}}\\,"                       
                    if "% ugent" in exer_text.lower():
                        icons += "\\ugent"
                    icons += "}"
                    new_chapter_text = new_chapter_text.\
                        replace(exer_match.group(1), icons + exer_text)
                with open(chapter_file, 'w') as outfile:
                    outfile.write(new_chapter_text)
                chapter_counter += 1
            hnt_file.write("\\end{multicols*}")
        sol_file.write("\\end{multicols*}")
        
def build():
    # So far only the UGent version, ebook only.

    # Prepare build directory.
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.mkdir(build_dir)

    # Copy directories.
    chapter_dirs = ["preamble", "helmholtz", "complex", "bessel",
                    "hermite", "numeric", "symmetry", "dynamic", "kk",
                    "postamble"]
    other_dirs = ["styles", "icons"]        
    for chapter_dir in chapter_dirs + other_dirs:
        shutil.copytree(chapter_dir, os.path.join(build_dir, chapter_dir))
    # Copy files.
    files = ["kaobook.cls", "kaohandt.cls", "main.tex"]
    for file in files:
        shutil.copy(file, os.path.join(build_dir, file))
    # Extract answers, hints, ....
    process_exer(chapter_dirs)
    # Build.
    subprocess.run(["pdflatex", "-file-line-error",
                    "-interaction=nonstopmode",
                    "-synctex=-1",
                    "-file-line-error",
                    os.path.join("main.tex")],
                    cwd=build_dir)
    subprocess.run(["biber",
                    os.path.join(build_dir, "main.bcf")],
                    cwd=build_dir)
    for i in range(3):
        subprocess.run(["pdflatex", "-file-line-error",
                    "-interaction=nonstopmode",
                    "-synctex=-1",
                    "-file-line-error",
                    os.path.join("main.tex")],
                    cwd=build_dir)

    shutil.copy(os.path.join(build_dir, "main.pdf"),
                "Mathematics for Photonics - ebook.pdf")

    return 
     
    # Make sure synctex does not refer to the temporary files.
    # Does not work, unfortunately, so I'm still missing something.
    shutil.copy(os.path.join(build_dir, "main.mw"),
                "Mathematics for Photonics - ebook.mw")
    shutil.copy(os.path.join(build_dir, "main.aux"),
                "Mathematics for Photonics - ebook.aux") 

    with open(os.path.join(build_dir, "main.synctex"), 'r') as infile:
        data = infile.read().replace("\\__build__", "")
        data = data.replace("main.mw", "Mathematics for Photonics - ebook.mw" )
        data = data.replace("main.aux", "Mathematics for Photonics - ebook.aux" )
        with open("Mathematics for Photonics - ebook.synctex", 'w') as outfile:
            outfile.write(data)
      
    #with gzip.open(os.path.join(build_dir, "main.synctex.gz"), 'rt') as #infile:
    #    data = infile.read().replace("\\__build__", "")
    #    data = data.replace("main.mw", "Mathematics for Photonics - ebook.#mw" )
    #    data = data.replace("main.aux", "Mathematics for Photonics - ebook.#aux" )
    #    with gzip.open("Mathematics for Photonics - ebook.synctex.gz", 'wt') #as outfile:
    #        outfile.write(data)
 
if __name__ == "__main__":
    build()
