import sys, os

extensions = ['sphinx.ext.autodoc']
templates_path = []
source_suffix = '.rst'
master_doc = 'index'
project = u'django_nadb'
copyright_holder = 'Daniel Aronne'
copyright = u'2012, %s' % copyright_holder
exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_theme = 'default'
htmlhelp_basename = '%sdoc' % project
latex_documents = [
  ('index', '%s.tex' % project, u'%s Documentation' % project,
   copyright_holder, 'manual'),
]
man_pages = [
    ('index', project, u'%s Documentation' % project,
     [copyright_holder], 1)
]

sys.path.insert(0, os.pardir)
m = __import__('nadb')

version = m.__version__
release = version
