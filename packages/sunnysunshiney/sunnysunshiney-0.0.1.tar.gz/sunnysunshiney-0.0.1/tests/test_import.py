from package.unittest import *

class TestImport(TestCase):
    def test_import(self):
        import sunnysunshiney

        self.assertTrue(True, 'sunnysunshiney module imported cleanly')

if __name__ == '__main__':
    main()
