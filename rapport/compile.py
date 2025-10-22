"""Small helper to compile a .tex file to PDF using pdflatex/xelatex.

Usage:
    python compile.py path/to/file.tex
    python compile.py --engine xelatex thesis.tex
    python compile.py --clean report.tex

Behaviour:
- Detects available engine (pdflatex or xelatex) unless overridden.
- Runs the engine twice to resolve references.
- If .bib is present and biber is available, runs biber between engine runs.
- Returns exit code 0 on success, non-zero on failure.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

AUX_EXTS = [
    '.aux', '.log', '.out', '.toc', '.lof', '.lot', '.bbl', '.blg', '.bcf', '.run.xml',
    '.synctex.gz', '.nav', '.snm', '.fdb_latexmk', '.fls'
]


def which_prog(names):
    for n in names:
        p = shutil.which(n)
        if p:
            return n
    return None


def run_cmd(cmd, cwd=None):
    print('> ' + ' '.join(cmd))
    proc = subprocess.run(cmd, cwd=cwd)
    return proc.returncode


def compile_tex(tex_path: Path, engine: str = None, runs: int = 2, use_biber: bool = True, clean: bool = False, outdir: Path = None):
    tex_path = tex_path.resolve()
    if not tex_path.exists():
        print(f"ERROR: {tex_path} not found")
        return 2
    src_dir = tex_path.parent
    name = tex_path.stem
    # default output directory: <src_dir>/build
    if outdir is None:
        outdir = src_dir / 'build'
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if engine is None:
        engine = which_prog(['pdflatex', 'xelatex', 'lualatex'])
        if engine is None:
            print('ERROR: No TeX engine found (pdflatex/xelatex/lualatex). Please install TeX Live or MikTeX.')
            return 3
    else:
        if shutil.which(engine) is None:
            print(f'ERROR: Requested engine "{engine}" not found on PATH')
            return 3

    bib_present = any((src_dir / f).exists() for f in os.listdir(src_dir) if f.endswith('.bib'))
    biber_prog = which_prog(['biber']) if use_biber and bib_present else None

    # First run: instruct engine to write outputs into outdir
    ret = run_cmd([engine, '-interaction=nonstopmode', f'-output-directory={str(outdir)}', str(tex_path.name)], cwd=src_dir)
    if ret != 0:
        print('First LaTeX run failed')
        return ret

    # If biber required
    if biber_prog:
        # run biber on main file (without extension)
        ret = run_cmd([biber_prog, name], cwd=outdir)
        if ret != 0:
            print('Biber failed')
            return ret

    # additional runs
    for i in range(1, runs):
        ret = run_cmd([engine, '-interaction=nonstopmode', f'-output-directory={str(outdir)}', str(tex_path.name)], cwd=src_dir)
        if ret != 0:
            print(f'LaTeX run #{i+1} failed')
            return ret

    pdf_path = outdir / (name + '.pdf')
    print(f'Success: output PDF at {pdf_path}')

    if clean:
        for ext in AUX_EXTS:
            p = outdir / (name + ext)
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass
        print('Cleaned auxiliary files in', outdir)

    return 0


def main():
    parser = argparse.ArgumentParser(description='Compile a .tex file to PDF (pdflatex/xelatex wrapper)')
    parser.add_argument('texfile', nargs='?', help='Path to .tex file (default: current directory finds one)')
    parser.add_argument('--engine', help='LaTeX engine to use (pdflatex/xelatex/lualatex)')
    parser.add_argument('--runs', type=int, default=2, help='Number of engine runs (default 2)')
    parser.add_argument('--no-biber', action='store_true', help='Do not run biber even if .bib exists')
    parser.add_argument('--clean', action='store_true', help='Remove auxiliary files after successful build')
    parser.add_argument('--outdir', help='Output directory for build files (default: ./build relative to .tex)')
    args = parser.parse_args()

    if args.texfile:
        tex_path = Path(args.texfile)
    else:
        # try to find a .tex in cwd
        texs = list(Path('.').glob('*.tex'))
        if not texs:
            print('ERROR: No .tex file provided and none found in current directory')
            return 2
        tex_path = texs[0]

    outdir = Path(args.outdir) if args.outdir else None
    ret = compile_tex(tex_path, engine=args.engine, runs=args.runs, use_biber=not args.no_biber, clean=args.clean, outdir=outdir)
    sys.exit(ret)


if __name__ == '__main__':
    main()
