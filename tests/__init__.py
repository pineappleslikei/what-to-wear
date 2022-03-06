import os

# prevent dev server form running (causes the tests to hang)
os.environ['DEV'] = 'OFF'