from distutils.core import setup
import quick_orm

setup(
    name = 'quick_orm',
    version = quick_orm.__version__,
    url = 'http://stackoverflow.com/users/862862/tyler-long',
    license = 'BSD',
    author = quick_orm.__author__,
    author_email = 'tyler4long@gmail.com',
    description = """A python orm which enables you to get started in less than a minute! Super easy to setup and super easy to use, yet super powerful! You would regret that you didn't discorver it earlier!""",
    long_description = open('README').read(),
    packages = ['quick_orm', 'quick_orm.examples', ],
    platforms = 'any',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
