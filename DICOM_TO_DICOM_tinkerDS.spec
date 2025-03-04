# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['DICOM_TO_DICOM_tinkerDS.py'],
    pathex=[],
    binaries=[],
    datas=[('Plantilla CT/Plantilla_CT.dcm', 'Plantilla CT'), ('Plantilla SPECT/Plantilla_SPECT.dcm', 'Plantilla SPECT'), ('Plantilla PET/Plantilla_PET.dcm', 'Plantilla PET'), ('Plantilla RTDOSE/Plantilla_RTDOSE.dcm', 'Plantilla RTDOSE'), ('Plantilla MRI/Plantilla_MRI.dcm', 'Plantilla MRI')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DICOM_TO_DICOM_tinkerDS',
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
)
