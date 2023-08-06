#import plac
#from importer2 import FakeImporter
#print plac.Interpreter.call(FakeImporter, ['dsn', 'help'])

class C(object):
    commands = ['write']
    def write(self):
        pass

if __name__ == '__main__':
    import plac; plac.Interpreter.call(C)
