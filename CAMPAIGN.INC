' -- ROOM SETTINGS AND CAMPAIGN COMPLETION --

'THE WALL SHEET CONTAINS ELEVEN COMPLETE ROWS OF EIGHTEEN TILES
Function RoomWallOffset(roomNumber)
 RoomWallOffset=((Max(1,roomNumber)-1) Mod WallThemes)*18
End Function

Function RoomIsTreasure(roomNumber)
 RoomIsTreasure=0
 If roomNumber>0 And roomNumber Mod 4=0 Then RoomIsTreasure=1
End Function

'ZERO MEANS THE FINAL ROOM WAS CLEARED, NOT ANOTHER MAP TO LOAD
Function NextCampaignRoom(roomNumber)
 NextCampaignRoom=0
 If roomNumber<TotalRooms Then NextCampaignRoom=roomNumber+1
End Function

Function CampaignContinuePressed()
 Local button,player,buttons$,keycode
 CampaignContinuePressed=0
 For button=1 To 5
  keycode=KeyDown(button)
  If keycode=32 Or keycode=13 Then CampaignContinuePressed=1
 Next button
 For player=PLN To PLQ
  If CtrlType(player)=1 Then
   buttons$=Right$("00000000000000"+Bin$(CLASSIC(B,3)),14)
   If Mid$(buttons$,1,1)="1" Or Mid$(buttons$,13,1)="1" Then CampaignContinuePressed=1
  EndIf
 Next player
End Function

'THE ORIGINAL TITLE ART FRAMES A DOUBLE BUFFERED VICTORY CELEBRATION
Sub DrawCampaignVictory(frame)
 Local player,message$,burst,ray,age,radius,angle,cx,cy,ax,ay,bx,by,shade
 PAGE COPY 1 TO 2,I
 PAGE WRITE 2
 For burst=0 To 5
  age=(frame+burst*11) Mod 48
  If age<36 Then
   cx=38+(burst*47) Mod 244:cy=40+(burst*29) Mod 148
   radius=age*0.9:shade=255-age*4
   For ray=0 To 7
    angle=ray*0.7853981634+burst*0.3
    ax=cx+Cos(angle)*Max(0,radius-4):ay=cy+Sin(angle)*Max(0,radius-4)+age*age/100
    bx=cx+Cos(angle)*radius:by=cy+Sin(angle)*radius+age*age/100
    If bx>18 And bx<302 And by>25 And by<203 Then
     If burst Mod 2=0 Then
      Line ax,ay,bx,by,1,RGB(shade,shade*0.8,32)
     Else
      Line ax,ay,bx,by,1,RGB(32,shade*0.8,shade)
     EndIf
    EndIf
   Next ray
  EndIf
 Next burst
 Text 160,86,"QUEST COMPLETE","CT",1,2,RGB(255,210,64),RGB(0,0,0)
 message$="ALL "+Str$(TotalRooms)+" ROOMS CONQUERED"
 PrintG(154-Len(message$)*3,113,message$)
 For player=PLN To PLQ
  message$=PlName$(player)+"  SCORE "+Str$(score(player))
  PrintG(154-Len(message$)*3,127+(player-PLN)*12,message$)
 Next player
 message$="CMM2 PORT: MAURO XAVIER"
 PrintG(154-Len(message$)*3,158,message$)
 message$="ORIGINAL GAME: ED LOGG / ATARI"
 PrintG(154-Len(message$)*3,174,message$)
 message$="THANK YOU FOR PLAYING!"
 PrintG(154-Len(message$)*3,190,message$)
 Box 0,228,320,12,0,,RGB(0,0,0)
 If frame>=75 And (frame Mod 40)<30 Then
  message$="SPACE / FIRE: TITLE   ESC: QUIT"
  PrintG(154-Len(message$)*3,230,message$)
 EndIf
 PAGE COPY 2 TO 0,I
End Sub

Sub ShowCampaignVictory
 Local frame,released,pressed
 Play Stop
 StopWAV
 If music=1 Then PlayMOD(13)
 PlayWAV("TREASURE",100)
 PAGE WRITE 6
 CLS
 Load PNG "./IMAGES/INTRO1.PNG",,,8
 PAGE COPY 6 TO 1,I
 PAGE WRITE 1
 Box 16,82,288,122,1,RGB(232,177,45),RGB(0,0,0)
 frame=0:released=0
 Do
  If KeyDown(1)=27 Then Mode 1:Cls:End
  pressed=CampaignContinuePressed()
  If pressed=0 Then released=1
  'SHOW THE ANNOUNCEMENT FOR THREE SECONDS AND REQUIRE A FRESH PRESS
  If frame>=75 And released=1 And pressed=1 Then Exit Do
  DrawCampaignVictory(frame)
  frame=frame+1
  Pause 40
 Loop
End Sub
