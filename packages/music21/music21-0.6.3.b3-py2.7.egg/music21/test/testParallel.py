


from music21.test import test



def run():
    modGather = test.ModuleGather()
    #modules = modGather.load(restoreEnvironmentDefaults=False)
    modules = modGather.modulePaths

    max = 4
    msg = []
    i = 0

    for fp in modules:
        if fp.endswith('__init__.py'):
            continue
        # get the next bundle of file paths
        msg.append(fp)
        i += 1

        if i >= max:
            msg = 'python ' + ' & python '.join(msg) + ' wait'
            print msg
            msg = []
            i = 0
        

if __name__ == '__main__':
    run()