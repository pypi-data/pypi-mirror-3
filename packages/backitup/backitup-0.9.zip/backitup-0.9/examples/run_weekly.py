# We'd run this script however often you want.
# You can make other scripts that call your helper, or set up your
# helper to be invoked via the commandline directly.
import yourhelper
yourhelper.run('weeklybackup.zip',
    r'C:\pythondev',
    r'C:\Users\<username>\Documents\Papers'
)
