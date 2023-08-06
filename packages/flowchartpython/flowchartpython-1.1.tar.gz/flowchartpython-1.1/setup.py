from distutils.core import setup

def main():
    setup(name = 'flowchartpython',
        version = '1.1',
        description = 'Flowchart Python',
        author = 'J. D. Bartlett',
        author_email = 'josh@bartletts.id.au',
        url = 'http://sqizit.bartletts.id.au/',
        packages = [
            'flowchartpython',
        ],

        scripts = [
            'scripts/flowchartpython',
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
