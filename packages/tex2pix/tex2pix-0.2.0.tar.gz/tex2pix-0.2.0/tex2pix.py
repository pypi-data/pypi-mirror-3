#! /usr/bin/env python

"""
A little library which renders LaTeX to various formats, using applications on
your system like latex, pdflatex, bibtex, dvips, ps2eps, and convert. LaTeX is
automatically run as many times as necessary to achieve a clean compile (with a
user-provided max number of attempts), and Bibtex processing is supported.

Compilation takes place in temporary directories which are automatically cleaned
up, can be initiated on a file or text string and include extra input files, and
rendering stages are cached to reduce rendering latency.

See also the 'tex' module, for a more established TeX renderer with different
design requirements.

Usage example::

    import tex2pix
    f = open("example.tex")
    r = tex2pix.Renderer(f, runbibtex=True, extras=["example.bib"])
    #r.verbose = True # be loud to the terminal
    #r.rmtmpdir = False # keep the working dir around, for debugging
    print r.mkeps("example.eps")
    print r.mkpng("example.png")
    print r.mkpdf("example.pdf")  # uses cached version from PNG build
    print r.mk("duplicate.pdf") # auto-detect format; uses cached PDF

    print tex2pix.check_latex_package("tikz.sty")
"""

__version__ = "0.2.0"


import os, sys, subprocess, shutil


class ExternalPkgException(Exception):
    def __init__(self, msg):
        Exception.__init__(msg)


## Caching dictionaries for system/LaTeX package-checking results
_pkgCheckResults = {}
_latexpkgCheckResults = {}


def _check_external_pkg(cmdname):
    if cmdname not in _pkgCheckResults:
        p = subprocess.Popen(["which", cmdname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rtn = p.wait()
        _pkgCheckResults[cmdname] = bool(rtn == 0)
    return _pkgCheckResults[cmdname]


def check_latex_pkg(pkgname):
    if not _check_external_pkg("kpsewhich"):
        print("WARNING: kpsewhich could not be found: check for %s package cannot be run" % pkgname)
        return None
    if pkgname not in _latexpkgCheckResults:
        p = subprocess.Popen(["kpsewhich", pkgname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rtn = p.wait()
        _latexpkgCheckResults[pkgname] = bool(rtn == 0)
    return _latexpkgCheckResults[pkgname]


def check_pdf_pkgs():
    """Test for pdflatex if we need to make a PDF
    TODO: also support making a PDF via latex and dvipdfm?
    """
    return _check_external_pkg("pdflatex")


def check_bitmap_pkgs():
    """Test for convert*and* the PDF producing packages if we need to make a PNG or JPEG
    TODO: also support making bitmaps some other way?
    """
    return _check_external_pkg("convert") and check_pdf_pkgs()


def check_bibtex():
    return _check_external_pkg("bibtex")


def check_dvi_pkgs():
    return _check_external_pkg("latex")


def check_ps_pkgs():
    return _check_external_pkg("dvips") and check_dvi_pkgs()


def check_eps_pkgs():
    return _check_external_pkg("ps2eps") and check_ps_pkgs()



class Renderer(object):
    """Helper object to run LaTeX etc. and clean up afterwards"""

    def __init__(self, texfile=None, tex=None, extras=None, maxiters=5, runbibtex=False):
        """\
        Construct a renderer object, bound to the particular main TeX source supplied
        either as a file with the `texfile` argument, or as a string with the `tex`
        argument.

        Extra files needed for compilation are supplied via the `extras` argument, the
        maximum number of latex/pdflatex runs allowed is given by the `maxiters` argument,
        and if bibtex is to be run, the `runbibtex` argument should be set to True.

        The `maxiters`, and `runbibtex` properties are available after
        initialisation as properties of the renderer object. The TeX source and other
        supplied files are written/copied into a temporary working directory specific
        to the renderer object, which will be removed from the filesystem when the
        renderer is deleted, unless the `rmtmpdir` attribute is set to False. The
        path to the temporary directory is available via the read-only `tmpdir` property.
        """
        assert tex or texfile and not (tex and texfile)
        self.maxiters = maxiters
        self.runbibtex = runbibtex
        self.verbose = False

        self._made_pdf = False
        self._made_dvi = False
        self._made_ps = False
        self._made_eps = False
        self._made_png = False
        self._made_jpg = False
        self._iteration = 0

        import tempfile
        self.tmpdir = tempfile.mkdtemp()
        self.rmtmpdir = True

        if texfile:
            if type(texfile) is str:
                tex = texfile
            elif hasattr(texfile, "read"):
                tex = texfile.read()
        fout = open(self._tmpfile(), "w")
        fout.write(tex)
        fout.close()
        if extras:
            for e in extras:
                shutil.copy(e, self.tmpdir)


    def __del__(self):
        if self.rmtmpdir:
            import shutil
            shutil.rmtree(self.tmpdir)


    def _tmpfile(self, fileext="tex"):
        return os.path.join(self.tmpdir, "mytmp." + fileext)


    def _mktmpprocess(self, cmdlist):
        "Convenience method to reduce repeated subprocess.Popen call noise in what follows."
        import subprocess
        if self.verbose:
            print " ".join(cmdlist)
        return subprocess.Popen(cmdlist, cwd=self.tmpdir,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def mkpdf(self, dest=None):
        "Processing to PDF"
        if not self._made_pdf:
            try:
                if not check_pdf_pkgs():
                    raise ExternalPkgException("Cannot find packages needed to build PDFs")
                if self.runbibtex and not check_bibtex():
                    raise ExternalPkgException("Cannot find bibtex, needed to build this PDF")
                if self._iteration == self.maxiters:
                    self._iteration -= 1
                while not self._made_pdf and self._iteration < self.maxiters:
                    self._iteration += 1
                    p = self._mktmpprocess(["pdflatex", r"\scrollmode\input", "mytmp.tex"])
                    p.wait()
                    if not "LaTeX Warning: There were undefined references." in p.communicate()[0]:
                        self._made_pdf = True
                        break
                    if self.runbibtex:
                        p = self._mktmpprocess(["bibtex", "mytmp"])
                        p.wait()
            except ExternalPkgException:
                raise
            except Exception, e:
                raise Exception("pdflatex could not be run: PDF, PNG, and JPEG format modes cannot work")
        if dest:
            shutil.copyfile(self._tmpfile("pdf"), dest)
            return dest
        else:
            return self._tmpfile("pdf")


    def mkpng(self, dest=None, density=150):
        "Make a PNG bitmap, via PDF"
        self.mkpdf()
        if not self._made_png:
            try:
                if not check_bitmap_pkgs():
                    raise ExternalPkgException("Cannot find packages needed to build PNGs")
                p = self._mktmpprocess(["convert", "-density", str(density), "-flatten", "mytmp.pdf", "mytmp.png"])
                p.wait()
                self._made_png = True
            except ExternalPkgException:
                raise
            except Exception, e:
                raise Exception("convert could not be run: PNG format mode cannot work")
        if dest:
            shutil.copyfile(self._tmpfile("png"), dest)
            return dest
        else:
            return self._tmpfile("png")


    def mkjpg(self, dest=None, density=150, quality=100):
        "Make a JPEG bitmap, via PDF"
        self.mkpdf()
        if not self._made_jpg:
            try:
                if not check_bitmap_pkgs():
                    raise ExternalPkgException("Cannot find packages needed to build JPEGs")
                p = self._mktmpprocess(["convert", "-density", str(density), "-flatten", "-quality", str(quality), "mytmp.pdf", "mytmp.jpg"])
                p.wait()
                self._made_jpg = True
            except ExternalPkgException:
                raise
            except Exception, e:
                raise Exception("convert could not be run: JPEG format mode cannot work")
        if dest:
            shutil.copyfile(self._tmpfile("jpg"), dest)
            return dest
        else:
            return self._tmpfile("jpg")


    def mkdvi(self, dest=None):
        "Make a DVI file from TeX source"
        if not self._made_dvi:
            try:
                if not check_dvi_pkgs():
                    raise ExternalPkgException("Cannot find packages needed to build DVIs")
                if self.runbibtex and not check_bibtex():
                    raise ExternalPkgException("Cannot find bibtex, needed to build this DVI")
                if self._iteration == self.maxiters:
                    self._iteration -= 1
                while not self._made_dvi and self._iteration < self.maxiters:
                    self._iteration += 1
                    p = self._mktmpprocess(["latex", r"\scrollmode\input", "mytmp.tex"])
                    p.wait()
                    if not "LaTeX Warning: There were undefined references." in p.communicate()[0]:
                        self._made_dvi = True
                        break
                    if self.runbibtex:
                        p = self._mktmpprocess(["bibtex", "mytmp"])
                        p.wait()
            except ExternalPkgException:
                raise
            except Exception, e:
                print e
                raise Exception("latex could not be run: EPS format mode cannot work")
        if dest:
            shutil.copyfile(self._tmpfile("dvi"), dest)
            return dest
        else:
            return self._tmpfile("dvi")


    def mkps(self, dest=None):
        "Make a PostScript file, via DVI"
        self.mkdvi()
        if not self._made_ps:
            try:
                if not check_ps_pkgs():
                    raise ExternalPkgException("Cannot find packages needed to build PSs")
                p = self._mktmpprocess(["dvips", "mytmp.dvi", "-o", "mytmp.ps"])
                p.wait()
                self._made_ps = True
            except ExternalPkgException:
                raise
            except Exception, e:
                raise Exception("dvips could not be run: EPS format mode cannot work")
        if dest:
            shutil.copyfile(self._tmpfile("ps"), dest)
            return dest
        else:
            return self._tmpfile("ps")


    def mkeps(self, dest=None):
        "Make an Encapsulated PostScript file, via unencapsulated PostScript"
        self.mkps()
        if not self._made_eps:
            try:
                if not check_eps_pkgs():
                    raise ExternalPkgException("Cannot find packages needed to build EPSs")
                p = self._mktmpprocess(["ps2eps", "mytmp.ps"])
                p.wait()
                self._made_eps = True
            except ExternalPkgException:
                raise
            except Exception, e:
                raise Exception("ps2eps could not be run: EPS format mode cannot work")
        if dest:
            shutil.copyfile(self._tmpfile("eps"), dest)
            return dest
        else:
            return self._tmpfile("eps")


    def mk(self, dest=None):
        """Make an output file, guessing the format from the file extension."""
        try:
            ext = os.path.splitext(dest)[1][1:]
            fnname = "mk" + ext.lower()
            if hasattr(self, fnname):
                getattr(self, fnname).__call__(dest)
            else:
                raise Exception("Couldn't find a supported format for supplied file extension '%s'" % ext)
        except IndexError, re:
            raise Exception("Can't guess format from supplied output filename '%s'" % dest)


################################


if __name__ == "__main__":
    f = open("example.tex")
    r = Renderer(f, runbibtex=True, extras=["example.bib"])
    #r.verbose = True
    #r.rmtmpdir = False
    print _pkgCheckResults
    print _latexpkgCheckResults
    print r.mkeps()
    print r.mk("example.eps")
    print r.mkpng("example.png")
    print r.mkjpg("example.jpg")
    print r.mkpdf("example.pdf")
    print _pkgCheckResults
    print _latexpkgCheckResults
