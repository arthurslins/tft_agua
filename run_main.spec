# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['run_main.py'],
             pathex=['.'],
             binaries=[],
             datas=[
                 (
                     "{$YOURPYTHONENV}/Lib/site-packages/altair/vegalite/v4/schema/vega-lite-schema.json",
                     "./altair/vegalite/v4/schema/"
                 ),
                 (
                     "${YOURPYTHONENV}/Lib/site-packages/streamlit/static",
                     "./streamlit/static"
                 )
            ],
            
            noarchive=False)
pyz = PYZ(...)
exe = EXE(...)