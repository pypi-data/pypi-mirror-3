def readf(loc):
    return open(loc, 'r', encoding='utf-8').read()

def sep(filename):
    head, content = '', ''
    with open(filename,'r',encoding='utf-8') as f:
        while True:
            line = f.readline()
            if (set(line) in ({'=','\n'},{'=','\n','\r'})) or line == '':
                content = f.read()
                break
            else:
                head += line
        return (head, content)

class Logger:
    def __init__(self):
        import logging, os
        self.logger = logging.getLogger("Seraph")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(os.getcwd()+"/Seraph.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
    def info(self, m):
        self.logger.info(m)
    def error(self, m):
        self.logger.error(m)
