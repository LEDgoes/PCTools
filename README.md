PCTools
=======

Cross-platform control software written in Python to run an LEDgoes matrix from a PC.

There are two versions available: an old Windows-only version written in C#, and the Python/QT version which is much more robust and feature-rich.  Both versions come with source code and binaries on GitHub, but the Python version's stand-alone installer is for Windows only at the moment.  The C# version may be "un-deprecated" if we find it reasonable to publish the apps on the Windows Store.  See below for where to download these applications.

The Python dependencies are:
* Qt5 (5.2+) - GUI
* python-twitter - for Python support
* Pillow - for image & animation processing

The contents of the "Csharp_deprecated" directory contain the entire MSVC 2010 solution file featuring 3 projects.

The LEDgoes PC Interface
------------------------

This program sends serial commands to the LEDgoes matrix so it can display text and animations.

The C# executable is located at https://github.com/LEDgoes/PCTools/blob/master/Csharp_deprecated/LEDgoes%20PC%20Interface/bin/Debug/LEDgoes%20PC%20Interface.exe

The Python installer for Windows is located at https://github.com/LEDgoes/PCTools/blob/master/Python_src/LEDgoes%20Setup.msi.

The LEDgoes Font Maker
----------------------

This program generates source code that you must copy in to a specific part of the Characters.cs file in the LEDgoes PC Interface, then rebuild the PC tools application, in order to render that character as desired.  This application will be streamlined in the Python version to generate a font file so you don't have to mess with any source code.

It is located at https://github.com/LEDgoes/PCTools/blob/master/Csharp_deprecated/LEDgoes%20Font%20Maker/bin/Debug/LEDgoes%20Font%20Maker.exe

Stay tuned for further enhancements on the Python version!
