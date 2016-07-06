from cx_Freeze import setup, Executable
import os
import sys
import stat
import glob
import subprocess

builddir='/Users/Natalie/Documents/Insight/KPCC/KPCC_MfN/'

def files_under_dir(dir_name):
    file_list = []
    for root, dirs, files in os.walk(dir_name):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list


includefiles = ['app']
#'pre_processer.py','preproc.py','process.py','report_tools.py','views.py'

#'static', 'templates', 'edit','raw'
#for directory in ('app','app/static', 'app/templates', 'app/edit','app/raw'):
#    includefiles.extend(files_under_dir(directory))


# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
    packages = [ 'jinja2', 'jinja2.ext','email','statsmodels','numpy','sklearn','sklearn.utils.lgamma','scipy','scipy.linalg'],
    excludes = ['collections.abc','tcl', 'ttk', 'tkinter', 'Tkinter'],
    # We can list binary includes here if our target environment is missing them.
    bin_includes = [
        'libcrypto.so.1.0.0',
        'libcrypto.so.10',
        'libgssapi_krb5.so.2',
        'libk5crypto.so.3',
        'libkeyutils.so.1',
        'libssl.so.1.0.1e',
        'libssl.so.10',
        'scipy.linalg._fblas.so'
    ],
    include_files= includefiles,
    include_msvcr= True
    
)

executables = [
    Executable(
        'run.py',
        base = None,
        targetName = 'run.py',
        copyDependentFiles = True,
        compress = True
    )
]
setup(name='kpcc_mfn',
      version = '0.1',
      description = 'App for KPCC Metric for News',
      options = dict(build_exe = buildOptions),
      executables = executables)

## To fix scipy relative reference problems:

def setRelativeReferencePaths(binDir):
    """ For all files in Contents/MacOS, check if they are binaries
        with references to other files in that dir. If so, make those
        references relative. The appropriate commands are applied to all
        files; they will just fail for files on which they do not apply."""
    files = []
    for root, dirs, dir_files in os.walk(binDir):
        files.extend([os.path.join(root, f).replace(binDir + "/", "")
                      for f in dir_files])
    for fileName in files:

        # install_name_tool can't handle zip files or directories
        filePath = os.path.join(binDir, fileName)
        if fileName.endswith('.zip'):
            continue

        # ensure write permissions
        mode = os.stat(filePath).st_mode
        if not (mode & stat.S_IWUSR):
            os.chmod(filePath, mode | stat.S_IWUSR)

        # let the file itself know its place
        subprocess.call(('install_name_tool', '-id',
                         '@executable_path/' + fileName, filePath))

        # find the references: call otool -L on the file
        otool = subprocess.Popen(('otool', '-L', filePath),
                                 stdout=subprocess.PIPE)
        references = otool.stdout.readlines()[1:]

        for reference in references:

            # find the actual referenced file name
            referencedFile = reference.decode().strip().split()[0]

            if (referencedFile.startswith('@loader_path/.dylibs/')
                or referencedFile.startswith('@loader_path/.')
                or referencedFile.startswith('@rpath')):
                # this file is likely an hdf5 file
                print "Found hdf5 file {} referencing {}".format(filePath, referencedFile)

            elif referencedFile.startswith('@'):
                # the referencedFile is already a relative path
                continue

            path, name = os.path.split(referencedFile)

            # some referenced files have not previously been copied to the
            # executable directory - the assumption is that you don't need
            # to copy anything fro /usr or /System, just from folders like
            # /opt this fix should probably be elsewhere though
            # if (name not in files and not path.startswith('/usr') and not
            #        path.startswith('/System')):
            #    print(referencedFile)
            #    self.copy_file(referencedFile,
            #                   os.path.join(self.binDir, name))
            #    files.append(name)

            # see if we provide the referenced file;
            # if so, change the reference
            if name in files:
                newReference = '@executable_path/' + name
                print "Fixing", filePath, "from", referencedFile, "to", newReference
                subprocess.call(('install_name_tool', '-change',
                                 referencedFile, newReference, filePath))


def fix_library_references(built_bin_dir=None):
    setRelativeReferencePaths(binDir=built_bin_dir)
    # dumb hack just to fix PIL._imaging.so
    try:
        PIL_Imaging_file = glob.glob(os.path.join(built_bin_dir, 'PIL._imaging.*'))[0]
        # find the references: call otool -L on the file
        otool = subprocess.Popen(('otool', '-L', PIL_Imaging_file),
                                 stdout=subprocess.PIPE)
        references = otool.stdout.readlines()[1:]
        for reference in references:
            # find the actual referenced file name
            referencedFile = reference.decode().strip().split()[0]
            if referencedFile.startswith('@'):
                # the referencedFile is already a relative path
                # continue
                # for this file we need to correct these
                pass
            path, name = os.path.split(referencedFile)
            if (not path.startswith('/usr')):
                newReference = '@executable_path/' + name
                subprocess.call(('install_name_tool', '-change',
                                 referencedFile, newReference, PIL_Imaging_file))
    except Exception as e:
        print "Could not file PIL._imaging file in", built_bin_dir


if os.path.isdir(os.path.join(builddir, "build/MyApp-2.0.0.app/Contents/MacOS")):
    # fix files in the app directory as well
    fix_library_references(built_bin_dir=os.path.join(builddir, "build/MyApp-2.0.0.app/Contents/MacOS"))

built_bin_dir = glob.glob(os.path.join(builddir, 'build/exe*'))[0]
if os.path.isdir(built_bin_dir):
    # fix files in the app directory as well
    fix_library_references(built_bin_dir=built_bin_dir)