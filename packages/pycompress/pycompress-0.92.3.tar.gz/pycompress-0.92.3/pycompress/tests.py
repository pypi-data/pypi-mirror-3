import unittest
from pycompress import compress, decompress, listarchive
import os
import time
import pycompress

size_filler = """
        Lorem Ipsum is simply dummy text of the printing and typesetting industry.
        Contrary to popular belief, Lorem Ipsum is not simply random text. It has
        roots in a piece of classical Latin literature from 45 BC, making it over
        2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney
        College in Virginia, looked up one of the more obscure Latin words,
        consectetur, from a Lorem Ipsum passage, and going through the cites of
        the word in classical literature, discovered the undoubtable source.
        Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of de Finibus Bonorum
        et Malorum (The Extremes of Good and Evil) by Cicero, written in 45 BC.
        This book is a treatise on the theory of ethics, very popular during the
        Renaissance. The first line of Lorem Ipsum, Lorem ipsum dolor sit amet..,
        comes from a line in section 1.10.32.The standard chunk of Lorem Ipsum
        used since the 1500s is reproduced below for those interested. Sections
        1.10.32 and 1.10.33 from de Finibus Bonorum et Malorum by Cicero are also
        reproduced in their exact original form, accompanied by English versions
        from the 1914 translation by H. Rackham. There are many variations of passages
         of Lorem Ipsum available, but the majority have suffered alteration in some
         form, by injected humour, or randomised words which don't look even slightly
         believable. If you are going to use a passage of Lorem Ipsum, you need to be
         sure there isn't anything embarrassing hidden in the middle of text. All the
         Lorem Ipsum generators on the Internet tend to repeat predefined chunks as
         necessary, making this the first true generator on the Internet. It uses a
         dictionary of over 200 Latin words, combined with a handful of model sentence
         structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem
         Ipsum is therefore always free from repetition, injected humour, or
         non-characteristic words etc.
         """
class TestZPAQFunctions(unittest.TestCase):

    def setUp(self):
        self.source = pycompress.__file__

    def test_compress(self):
        """
        This tests if compression is working properly
        And checks if the file size is less than the original, to make sure,
        it is fullfilling its purpose.
        """
        self.size = os.path.getsize(self.source)
        compress(self.source, '/tmp/tests.zpaq', 'n')
        time.sleep(4)
        self.newsize = os.path.getsize('/tmp/tests.zpaq')
        print "Real Size: %s \nCompressed Size: %s" % (self.size, self.newsize)
        self.assertLessEqual(self.newsize, self.size)

    def test_listarchive(self):
        """
        This tests if decompression is working properly
        """
        self.info = listarchive('/tmp/tests.zpaq')
        if self.info:
            print "Information : %s" % (self.info)
        self.assertIsNotNone(self.info)


    def test_decompress(self):
        """
        This tests if decompression is working properly
        """
        self.source = pycompress.__file__
        compress(self.source, '/tmp/tests.zpaq')
        self.size = os.path.getsize('/tmp/tests.zpaq')
        decompress('/tmp/tests.py', '/tmp/tests.zpaq')
        time.sleep(4)
        self.newsize = os.path.getsize('/tmp/tests.py')
        print "Real Size: %s \n Compressed Size: %s" % (self.size, self.newsize)
        self.assertGreaterEqual(self.newsize, self.size)

if __name__ == '__main__':
    unittest.main()
