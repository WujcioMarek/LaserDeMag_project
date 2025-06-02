# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['LaserDeMag/ui/gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('LaserDeMag/resources','resources'),
        ('C:/Users/Marek/PycharmProjects/LaserDeMag_project/.venv/Lib/site-packages/udkm1Dsim/parameters', 'udkm1Dsim/parameters'),
    ],
    hiddenimports=collect_submodules('udkm1Dsim'),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LaserDeMagApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='LaserDeMag/resources/images/logo_light.ico',
)