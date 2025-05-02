# LaserDeMag.spec

block_cipher = None

a = Analysis(
    ['LaserDeMag/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('LaserDeMag/resources/translations/*.qm', 'LaserDeMag/resources/translations'),
        ('LaserDeMag/resources/icons/*.png', 'LaserDeMag/resources/icons'),
        ('LaserDeMag/resources/styles.qss', 'LaserDeMag/resources'),
    ],
    hiddenimports=[
        "PyQt6.QtWidgets",
        "PyQt6.QtGui",
        "PyQt6.QtCore",
        "PyQt6.QtSvg",
        "PyQt6.QtPrintSupport",
    ],
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
    [],
    exclude_binaries=True,
    name='ThreeTM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='ThreeTM'
)
