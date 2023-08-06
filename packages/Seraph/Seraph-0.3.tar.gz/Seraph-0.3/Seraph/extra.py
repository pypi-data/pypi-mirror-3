import os
import Seraph.storage as storage

def init_site(loc="site/"):
    if not loc[-1] == "/":
        loc = loc + "/"
    def unpack(d,root):
        if root and (not os.path.exists(loc+root)):
                os.makedirs(loc+root)
        for i in d.keys():
            if type(d[i]) == type(dict()):
                unpack(d[i],root+"/"+i)
            else:
                f = open(loc+root+'/'+i,'w')
                f.write(getattr(storage,d[i]))
                f.close()
    print("* Begin to construct the inital site \"%s\"" % loc)
    unpack(storage.inital_site,"")
    print('* Construction finished.')

def git_push():
    print('* Git-ing...(Nothing will happen in this version)')
    pass
