# pylint: disable=C0321,C0103,C0301,E1305,E1121,C0302,C0330,C0111,W0613,W0611,R1705
# -*- coding: utf-8 -*-
import os, sys, time, datetime,inspect


#########################################################################################
def test1():
   from utilmy import (Session,
                       global_verbosity,


                       os_makedirs,
                       os_system ,
                       os_removedirs,


                       pd_read_file,
                       pd_show,


                       git_repo_root,
                       git_current_hash,


                      )
   from utilmy.decorators import timer, profiled, context_profiler
   ############################################################################
   import pandas as pd, random

   ncols = 7
   nrows = 100
   ll = [[ random.random() for i in range(0, ncols)] for j in range(0, nrows) ]
   # Required for it to be detected in Session's globals()
   global df
   df = pd.DataFrame(ll, columns = [str(i) for i in range(0,ncols)])
   n0 = len(df)
   s0 = df.values.sum()
   os.makedirs("data/parquet/", exist_ok= True)

   ##### m_job , n_pool tests  ##############################
   ncopy = 20
   for i in range(0, ncopy) :
      df.to_csv( f"data/parquet/ppf_{i}.csv.gz",  compression='gzip' , index=False)

   df1 = pd_read_file("data/parquet/ppf*.gz", verbose=1, n_pool= 7 )

   assert len(df1) == ncopy * n0,         f"df1 {len(df1) }, original {n0}"
   assert round(df1.values.sum(), 5) == round(ncopy * s0,5), f"df1 {df1.values.sum()}, original {ncopy*s0}"


   ###########################################################
   df.to_csv( "data/parquet/fa0b2.csv.gz",   compression='gzip' , index=False)
   df.to_csv( "data/parquet/fab03.csv.gz",   compression='gzip' , index=False)
   df.to_csv( "data/parquet/fabc04.csv.gz",  compression='gzip' , index=False)
   df.to_csv( "data/parquet/fa0bc05.csv.gz", compression='gzip' , index=False)

   df1 = pd_read_file("data/parquet/fab*.*", verbose=1)
   assert len(df1) == 2 * n0, f"df1 {len(df1) }, original {n0}"


   ##### Stresss n_pool
   df2 = pd_read_file("data/parquet/fab*.*", n_pool=1000 )
   assert len(df2) == 2 * n0, f"df1 {len(df2) }, original {n0}"



   ###################################################################################
   ###################################################################################
   print(git_repo_root())
   assert not git_repo_root() == None, "err git repo"








   ###################################################################################
   ###################################################################################
   os_makedirs('ztmp/ztmp2/myfile.txt')
   os_makedirs('ztmp/ztmp3/ztmp4')
   os_makedirs('/tmp/')
   os_makedirs('/tmp/one/two')
   os_makedirs('/tmp/myfile')
   os_makedirs('/tmp/one/../mydir/')
   os_makedirs('./tmp/test')

   os.system("ls ztmp")

   path = ["/tmp/", "ztmp/ztmp3/ztmp4", "/tmp/", "./tmp/test","/tmp/one/../mydir/"]
   for p in path:
       f = os.path.exists(os.path.abspath(p))
       assert  f == True, "path "


   rev_stat = os_removedirs("ztmp/ztmp2")
   assert not rev_stat == False, "cannot delete root folder"

   res = os_system( f" ls . ",  doprint=True)
   print(res)
   res = os_system( f" ls . ",  doprint=False)







   ###################################################################################
   ###################################################################################
   print('verbosity', global_verbosity(__file__, "config.json", 40,))
   print('verbosity', global_verbosity('../', "config.json", 40,))
   print('verbosity', global_verbosity(__file__))

   verbosity = 40
   gverbosity = global_verbosity(__file__)
   assert gverbosity == 5, "incorrect default verbosity"
   gverbosity =global_verbosity(__file__, "config.json", 40,)
   assert gverbosity == verbosity, "incorrect verbosity "












   ###################################################################################
   ###################################################################################
   sess = Session("ztmp/session")
   sess.save('mysess', globals(), '01')
   os.system("ls ztmp/session")

   sess.save('mysess', globals(), '02')
   sess.show()

   import glob
   flist = glob.glob("ztmp/session/" + "/*")
   for f in flist:
       t = os.path.exists(os.path.abspath(f))
       assert  t == True, "session path not created "

       pickle_created = os.path.exists(os.path.abspath(f + "/df.pkl"))
       assert  pickle_created == True, "Pickle file not created"

   sess.load('mysess')
   sess.load('mysess', None, '02')

   @timer
   def dummy_func():
       time.sleep(2)

   class DummyClass:
       @timer
       def method(self):
           time.sleep(3)

   dummy_func()
   a = DummyClass()
   a.method()


   ###################################################################################
   @profiled
   def profiled_sum():
       return sum(range(100000))

   profiled_sum()

   with context_profiler():
       x = sum(range(1000000))
       print(x)


def test_thread(*args):

    def test_print(*args):
        if len(args) == 0:
            args = list(args).append(1)
        print(args[0]*args[0])
        return args[0]*args[0]

    from utilmy.decorators import os_multithread
    assert os_multithread(function1=(test_print, (5,)),
                          function2=(test_print, (4,)),
                          function3=(test_print, ()))


if __name__ == "__main__":
    test1()
    test_thread()

