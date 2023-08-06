def create_project(project_name = 'DataProject', config = {}):
    """
    Creates the project and creates a skelton directory
    structure
    
    Params:
      project_name: A string that represents the name of the project
    
      config: A dictionary that represents configuration options.  The structure
      is {"option": value}
        current options:
          git: A boolean that represents if you want a git repo to be init'd
    
          full_structure: A boolean that represents if you'd like the full
          folder structure or a barebones structure
    
          libraries: An array of strings that represents the libraries you'd
          like loaded on `load_project`
    """
    from os import mkdir, chdir, system
    from json import dump
    mkdir(project_name)
    chdir(project_name)
    if config == {}:
        config = {
                   'git': False,
                   'full_structure': False,
                   'packages': [],
                   'logging': False
                  }

    if config['full_structure']:
        folders = [
                   'data',
                   'diagnostics',
                   'doc',
                   'graphs',
                   'lib',
                   'reports',
                   'profiling',
                   'tests',
                   'munge'
                  ]
    else:
        folders = [
                   'data', 
                   'lib', 
                   'munge'
                  ]

    map(mkdir, folders)

    system('touch README.txt')
    if config['git']:
        system('git init')

    with open('.config.json', mode='w') as f:
        dump(config, f)

def load_project():
    """
    Loads the project into the workspace
    
    Does three things currently
      1. Recursively loads you csv files into data frames
         prepending the folder if not in data
      2. Runs files in the munge folder.  These are
         preprocessing scripts
      3. Imports files in lib
    
    """
    from os import listdir, chdir, walk, getcwd
    from os.path import join, split
    from pandas import read_csv
    from json import load
    
    shell = get_ipython()

    with open('.config.json', 'r') as f:
        config = load(f)

    filename = lambda x: x.split('.')[0]

    vars_to_push = {}
    for directory, _, datafiles in walk('data', topdown=False):
        for datafile in datafiles:
            if directory == 'data':
                var_name = filename(datafile)
                read_location = join('data', datafile)
                vars_to_push[var_name] = read_csv(read_location)
            else:
                var_name = split(directory)[-1] + '_' + filename(datafile)
                read_location = join(directory, datafile)
                vars_to_push[var_name] = read_csv(read_location)
    shell.push(vars_to_push)

    mungefiles = listdir('munge')
    for mungefile in mungefiles:
        shell.magic('run -i munge/%s' % mungefile)

    libfiles = listdir('lib')
    libs_to_push = {}
    chdir('lib')
    for libfile in libfiles:
        mod = filename(libfile)
        libs_to_push[mod] = __import__(filename(libfile))

    shell.push(libs_to_push)
    chdir('..')
    packages = config['packages']
    for package in packages:
        shell.runcode('import %s' % package)

    shell.magic_logstart(getcwd().split('/')[-1] + '_logging.py append')
