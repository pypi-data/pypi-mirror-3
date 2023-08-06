from distutils.core import setup

def main():
    setup(name = 'talljosh',
        version = '1.0',
        description = "talljosh's helpers",
        author = 'J. D. Bartlett',
        author_email = 'josh@bartletts.id.au',
        url = 'http://sqizit.bartletts.id.au/',
        packages = [
            'talljosh',
        ],

        requires = [
        ],

        classifiers = [
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
        ],
    )


if __name__ == '__main__':
    main()
