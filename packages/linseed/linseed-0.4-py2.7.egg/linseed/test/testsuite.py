import unittest

def run():
    suite = unittest.TestLoader().discover(
        start_dir='.',
        pattern='*_test.py')

    unittest.TextTestRunner(verbosity=1).run(suite)

if __name__ == '__main__':
    run()
