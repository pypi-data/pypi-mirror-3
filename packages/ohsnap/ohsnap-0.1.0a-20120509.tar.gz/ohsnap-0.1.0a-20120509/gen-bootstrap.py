import virtualenv, textwrap
output = virtualenv.create_bootstrap_script(textwrap.dedent("""
    import os, subprocess
    def after_install(options, home_dir):
        subprocess.call([join(home_dir, 'bin', 'pip'),
            'install', 'setuptools-git'])
        subprocess.call([join(home_dir, 'bin', 'pip'),
            'install', 'Sphnix-PyPi-upload'])
        subprocess.call([join(home_dir, 'bin', 'pip'),
            'install', 'pycli'])
        subprocess.call([join(home_dir, 'bin', 'pip'),
            'install', 'prettytable'])
        subprocess.call([join(home_dir, 'bin', 'pip'),
            'install', 'sphinx'])
"""))
print output
