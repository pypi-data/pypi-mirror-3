long_description = """
Neon is colorful cui utility (on Linux terminal).

Neon is very simple.

example

::

    import sys
    from neon import colorful
    
    sys.stdout.write(colorful("test"))


dynamic color change example

::

    import sys
    from neon import colorful
    
    s = "NEON is colorful cui utility"
    for i in xrange(0, len(s) + 1):
        sys.stdout.write(colorful(s[:i], start=i))
        sys.stdout.flush()
        time.sleep(0.5)
        sys.stdout.write("\r")

""",


from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Software Development",
]

setup(name='neon',
      version=version,
      description="colorful cui utility",
      long_description=long_description,
      classifiers=classifiers,
      keywords='neon colorful cui enjoy happy funny',
      author='yoichi.hiromoto',
      author_email='yoichi.hiromoto@gmail.com',
      url='https://github.com/yoichi-hiromoto/neon',
      license='Python Software Foundation License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
