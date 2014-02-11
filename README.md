PCTools
=======

Cross-platform control software written in Python to run an LEDgoes matrix from a PC.

There are two versions available: a Windows-only version written in C#, and the Python version which, as of right now, still has some exceptions it's spitting out when trying to write serial data to the LEDgoes matrix.  The issues in Python should only take a couple more hours to fix.  The C# comes with source code & binaries, but the Python is currently source only.  See below for the C# executable location.

The Python dependencies are:
Qt5 - GUI
Perhaps others; will be updated with further details

The contents of the "Csharp_deprecated" directory contain the entire MSVC 2010 solution file featuring 3 projects.

The LEDgoes PC Interface sends serial commands to the LEDgoes matrix so it can display text and animations.

The program is located at https://github.com/LEDgoes/PCTools/blob/master/Csharp_deprecated/LEDgoes%20PC%20Interface/bin/Debug/LEDgoes%20PC%20Interface.exe

The LEDgoes Font Maker generates source code that you must copy in to a specific part of the Characters.cs file in the LEDgoes PC Interface, then rebuild the PC tools application, in order to render that character as desired.  This application will be streamlined in the Python version to generate a font file so you don't have to mess with any source code.

The program is located at https://github.com/LEDgoes/PCTools/blob/master/Csharp_deprecated/LEDgoes%20Font%20Maker/bin/Debug/LEDgoes%20Font%20Maker.exe

Stay tuned for further enhancements on the Python version!
