try:
    from pip import main as pipmain
except:
    from pip._internal import main as pipmain
import os


for dirpath, dirnames, filenames in os.walk("."):
    for filename in filenames:
        if filename=="numpy-1.14.5+mkl-cp27-cp27m-win32.whl":
            fullFileName = (os.path.realpath(os.path.join(dirpath, filename)))
pipmain(['install','wheel'])
# pipmain(['uninstall','-y','numpy'])
# pipmain(['uninstall','-y','pandas'])
pipmain(['install',"pandas"])
# pipmain(['uninstall','-y','pygeoprocessing'])
pipmain(['install','pygeoprocessing==0.3.3'])
pipmain(['install','Image'])

pipmain(['install',fullFileName])
