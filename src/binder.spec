# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

from os.path import join, dirname, abspath, split
from os import sep
import glob

import keyboard
import plyer
import win32clipboard

pkg_data = []

pkg_dir = split(keyboard.__file__)[0]
pkg_data.extend((file, dirname(file).split("site-packages")[1]) for file in glob.iglob(join(pkg_dir,"**{}*".format(sep)), recursive=True))

pkg_dir = split(plyer.__file__)[0]
pkg_data.extend((file, dirname(file).split("site-packages")[1]) for file in glob.iglob(join(pkg_dir,"**{}*".format(sep)), recursive=True))

pkg_dir = split(win32clipboard.__file__)[0]
pkg_data.extend((file, dirname(file).split("site-packages")[1]) for file in glob.iglob(join(pkg_dir,"**{}*".format(sep)), recursive=True))


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=pkg_data + [('binder.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='binder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['binder.ico'],
)
