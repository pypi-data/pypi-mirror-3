import fs.osfs
import fs.path

basedir, _ = fs.path.split(__file__)
basedir = fs.osfs.OSFS(basedir)
files = basedir.opendir('files')
