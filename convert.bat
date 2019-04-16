set EXE_PATH="C:\Python27\Lib\site-packages\PyQt4"
set UIC=%EXE_PATH%\pyuic4
set RCC=%EXE_PATH%\pyrcc4


call %UIC% -o ui_send1.py ui_send1.ui
call %UIC% -o ui_add_account.py ui_add_account.ui
call %UIC% -o ui_progress.py ui_progress.ui
call %UIC% -o ui_ndr.py ui_ndr.ui
call %UIC% -o ui_recv_host.py ui_recv_host.ui
call %UIC% -o ui_editor.py editor.ui
call %UIC% -o ui_editor_addlink.py editor_add_link.ui
call %UIC% -o ui_editor_addtable.py editor_add_table.ui

call %RCC% -o send1_rc.py send1.qrc

pause
:cmd