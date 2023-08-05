# RUNME as 'python -m collect.tests.__main__'
import unittest
import collect.tests

def main():
    "Run all of the tests when run as a module with -m."
    suite = collect.tests.get_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    main()