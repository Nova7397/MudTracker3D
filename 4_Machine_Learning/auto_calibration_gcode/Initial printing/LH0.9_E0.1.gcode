; Gcode for test printing LH0.9E0.1
; Saved by User: Mudtracker3D
; Saved at: 2024.10. 21
; Printer Model: Delta WASP 40100 LDM Half 
; First Layer Height: 1.5 mm
; Pre Fill: 2 mm
; Safe Start Speed: 1800 mm/m Length: 0 mm
; Flatten Speed: 1500 mm/m Length: 4 mm
; Retraction Speed: 1500 mm/m Height: 2 mm
M117 Termite Auto Homing ;
G28 ; MOVE TO ORIGIN (HOME)
G21 ; UNITS: MM
G90 ; ABSOLUTE COOD
M82 ; ABSOLUTE EXTRUDE
M117 Termite Printing ;
; END OF HEADER
G92 E0 F0 ;
G0 X-107.5 Y-110 Z3.5 E0 F6000 ; END OF TRAVEL
G1 X-107.5 Y-110 Z1.5 E0.2 F1500 ; END OF RETRACT DOWN
G1 X-7.5 Y-110 Z1.5 E10.2 F1800
G0 X-3.5 Y-110 Z1.5 E10.2 F1500 ; END OF FLATTEN
G0 X-3.5 Y-110 Z3.5 E10.2 F1500 ; END OF RETRACT UP
G92 E0 F0 ; END OF PRINTING PATH 1
G0 X-7.5 Y-110 Z4.4 E0 F6000 ; END OF TRAVEL
G1 X-7.5 Y-110 Z2.4 E0.2 F1500 ; END OF RETRACT DOWN
G1 X-107.5 Y-110 Z2.4 E10.2 F1800
G0 X-111.5 Y-110 Z2.4 E10.2 F1500 ; END OF FLATTEN
G0 X-111.5 Y-110 Z4.4 E10.2 F1500 ; END OF RETRACT UP
G92 E0 F0 ; END OF PRINTING PATH 2
G0 X-107.5 Y-110 Z5.3 E0 F6000 ; END OF TRAVEL
G1 X-107.5 Y-110 Z3.3 E0.2 F1500 ; END OF RETRACT DOWN
G1 X-7.5 Y-110 Z3.3 E10.2 F1800
G0 X-3.5 Y-110 Z3.3 E10.2 F1500 ; END OF FLATTEN
G0 X-3.5 Y-110 Z5.3 E10.2 F1500 ; END OF RETRACT UP
G92 E0 F0 ; END OF PRINTING PATH 3

; START OF FOOTER
Auto Homing ;
G28 X0 Y0 ; MOVE TO ORIGIN (HOME)
LH0.9E0.1 printing done ;