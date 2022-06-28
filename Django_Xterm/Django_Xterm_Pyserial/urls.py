from django.urls import path
from . import views
from .views import Change_Password
from django.contrib.auth.decorators import login_required

urlpatterns = [ 
    path('', views.Index, name='Index'),
    path('logout/', views.Logout_view, name="Logout"),
    path('Password_Change/', login_required(Change_Password.as_view(template_name='Django_Xterm_Pyserial/Password_Change.html'), login_url='Index'), name='Password_Change'),
    path('Change_Password_Done/', views.Change_Password_Done, name='Change_Password_Done'),

    path('ControlPanel/', views.ControlPanel, name="ControlPanel"),
    path('ControlPanel/<path:Name>', views.ControlPanel, name="ControlPanelName"),
    path('SelectedPowerStrip/', views.SelectedPowerStrip, name="SelectedPowerStrip"),
    path('SelectedSocket/', views.SelectedSocket, name="SelectedSocket"),
    path('On_Off_Single/', views.On_Off_Single, name='On_Off_Single'),
    path('On_Off_All/', views.On_Off_All, name='On_Off_All'),
    path('AddPowerStrip/', views.AddPowerStrip, name='AddPowerStrip'),
    path('GetAllPowerStrips/', views.GetAllPowerStrips, name='GetAllPowerStrips'),
    path('DeletePowerStrip/', views.DeletePowerStrip, name='DeletePowerStrip'),
    path('DeleteAllPowerStrip/', views.DeleteAllPowerStrip, name='DeleteAllPowerStrip'),
    path('CheckSerialPort/', views.CheckSerialPort, name='CheckSerialPort'),
    path('ConnectToSerialPort/', views.ConnectToSerialPort, name='ConnectToSerialPort'),

    path('PowerStrips/', views.PowerStrips, name='PowerStrips'),
    path('EditPowerStrip/', views.EditPowerStrip, name='EditPowerStrip'),

    path('Terminal/', views.Terminal, name='Terminal'),
    path('RemoveDevice/', views.RemoveDevice, name='RemoveDevice'),

    path('Groups/', views.Groups, name='Groups'),
    path('Groups/<str:Name>',views.Groups, name='GroupsName'),
    path('GetAllNormalUsersAndDevices/', views.GetAllNormalUsersAndDevices, name='GetAllNormalUsersAndDevices'),
    path('AddGroup/', views.AddGroup, name='AddGroup'),
    path('AddGroupMerge/', views.AddGroupMerge, name='AddGroupMerge'),
    path('AddGroupDelB/', views.AddGroupDelB, name='AddGroupDelB'),
    path('EditGroup/', views.EditGroup, name='EditGroup'),
    path('DeleteGroup/', views.DeleteGroup, name='DeleteGroup'),
    path('AddGroupsFile/', views.AddGroupsFile, name='AddGroupsFile'),
    path('Merge_File/', views.Merge_File, name='Merge_File'),
    path('Delete_Before_File/', views.Delete_Before_File, name='Delete_Before_File'),
    path('DeleteAllGroups/', views.DeleteAllGroups, name='DeleteAllGroups'),
    
    path('Students/', views.Students, name='Students'),
    path('Students/<str:Name>', views.Students, name='StudentsName'),
    path('CreateStudent/', views.CreateStudent, name='CreateStudent'),
    path('DeleteStudents/', views.DeleteStudents, name='DeleteStudents'),
    path('AddStudentsFile/', views.AddStudentsFile, name='AddStudentsFile'),
]