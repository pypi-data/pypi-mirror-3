from distutils.core import setup

setup(name="annotate_regions",
      version="1.0",
      description="GUI for annotating regions in chromosomal copy number profiles",
      author="Toby Dylan Hocking",
      author_email="toby.hocking@inria.fr",
      scripts=["annotate_breakpoints.py"],
      )
