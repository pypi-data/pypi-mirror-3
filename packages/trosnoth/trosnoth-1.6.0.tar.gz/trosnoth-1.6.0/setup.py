import sys
from distutils.core import setup

trosnoth_version = '1.6.0'
additional_dlls = [
    'pygame/SDL_ttf.dll',
    'pygame/libvorbis-0.dll',
    'pygame/libvorbisfile-3.dll',
    'pygame/libfreetype-6.dll',
    'pygame/SDL_mixer.dll',
    'pygame/libogg-0.dll',
]

def main():
    if 'py2exe' in sys.argv:
        import py2exe

        # Make sure py2exe knows which data files to include.
        import os
        paths = [
            'trosnoth/data/achievements',
            'trosnoth/data/blocks',
            'trosnoth/data/config',
            'trosnoth/data/fonts',
            'trosnoth/data/music',
            'trosnoth/data/sound',
            'trosnoth/data/sprites',
            'trosnoth/data/startupMenu',
            'trosnoth/data/statGeneration',
            'trosnoth/data/themes',
            'trosnoth/data/themes/pirate',
            'trosnoth/data/themes/pirate/blocks',
            'trosnoth/data/themes/pirate/config',
            'trosnoth/data/themes/pirate/fonts',
            'trosnoth/data/themes/pirate/sprites',
            'trosnoth/data/themes/pirate/startupMenu',
            'trosnoth/data/web',
        ]

        data = []
        for path in paths:
            files = []
            for filename in os.listdir(path):
                if filename in ('__init__.py', '__init__.pyc'):
                    continue
                fn = os.path.join(path, filename)
                if os.path.isfile(fn):
                    files.append(fn)
            data.append((path, files))

        moreargs = {
            'console': [
                {'script': 'scripts/trosnoth',
                    'icon_resources': [(1, 'wininstall/icon.ico')]
                },
                'scripts/trosnoth-server',
            ],
            'data_files': data,
            'options': {
                'py2exe': {
                    'includes': 'zope.interface,pygame._view,trosnoth.ais.alpha,trosnoth.ais.simple,trosnoth.ais.john,trosnoth.ais.test',
                },
            },
       }
    else:
        moreargs = {}

    setup(name = 'trosnoth',
        version = trosnoth_version,
        description = 'Trosnoth network platform game',
        author = 'J.D. Bartlett et al',
        author_email = 'josh@trosnoth.org',
        url = 'http://www.trosnoth.org/',
        packages = ['trosnoth',
            'trosnoth.ais',
            'trosnoth.data',
            'trosnoth.data.blocks',
            'trosnoth.data.fonts',
            'trosnoth.data.music',
            'trosnoth.data.sound',
            'trosnoth.data.sprites',
            'trosnoth.data.startupMenu',
            'trosnoth.data.statGeneration',
            'trosnoth.data.themes',
            'trosnoth.gamerecording',
            'trosnoth.gui',
            'trosnoth.gui.fonts',
            'trosnoth.gui.framework',
            'trosnoth.gui.menu',
            'trosnoth.gui.screenManager',
            'trosnoth.gui.sound',
            'trosnoth.model',
            'trosnoth.network',
            'trosnoth.rsa',
            'trosnoth.run',
            'trosnoth.tools',
            'trosnoth.trosnothgui',
            'trosnoth.trosnothgui.ingame',
            'trosnoth.trosnothgui.pregame',
            'trosnoth.trosnothgui.settings',
            'trosnoth.utils',
            'trosnoth.web',
            ],
        # Mapping says which files each package needs.
        package_data = {
            'trosnoth.data.blocks': ['*.block', '*.png', '*.bmp'],
            'trosnoth.data.fonts': ['*.ttf', '*.TTF', '*.txt'],
            'trosnoth.data.music': ['*.ogg'],
            'trosnoth.data.sound': ['*.ogg'],
            'trosnoth.data.sprites': ['*.png', '*.bmp'],
            'trosnoth.data.startupMenu': ['*.png', '*.txt'],
            'trosnoth.data.statGeneration': ['*.htm'],
            'trosnoth.data.themes': ['pirate/info.txt',
                'pirate/blocks/*.png', 'pirate/config/*.cfg',
                'pirate/fonts/*', 'pirate/sprites/*',
                'pirate/startupMenu/*'],
            'trosnoth.data': ['config/*.cfg', 'achievements/*.png', 'web/*.png'],
            'trosnoth': ['gpl.txt']
        },

        scripts = ['scripts/trosnoth', 'scripts/trosnoth-server'],
        long_description = 'Trosnoth is a very very addictive and fun network team game.' ,

        requires = [
            'pygame (>=1.7)',
            'twisted (>=2.4)'
        ],

        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications',
            'Framework :: Twisted',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Topic :: Games/Entertainment :: Arcade',
            'Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games',
        ],
        **moreargs
    ) 


if __name__ == '__main__':
    main()
