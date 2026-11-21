# AI Log

## Tools used

- **Claude (claude.ai chat, Claude Opus 5.5)**: explained the brief to me in simple words, wrote the first version of the code (FastAPI server, SQLite storage, SVG drawing, web page) and the README, and helped me fix errors on my laptop from screenshots.
- **Claude Code (VS Code extension, Claude Opus 5.5)**: checked my folder against the assignment PDF, found a bug, made the drawing more detailed (part names, parts list, "est." marks), redesigned the web page into the CraneDraft editor, explained the crane parts to me in simple words, and tested the app with scripts and browser screenshots. It also recorded the silent demo video (an automatic screen recording with captions); the two "decision I'd keep / change" screens at the end are my own words, with only the grammar fixed by Claude. It drafted this log from our chat, and I checked it.
- **DECISIONS.md**: I asked Claude to write this file from my short answers, so it is marked "Written by AI" at the top. My original answers, in my own words, are kept unchanged at the bottom of the file.
- **VS Code**: editing, running the server, and committing to GitHub.

I tested every change myself in the browser and sent screenshots back when something looked wrong.

## Key prompts

These are my real messages (short and informal), shortened and with typos fixed:

1. **Chat:** pasted the full assignment PDF and asked *"tell me what we gonna do now"*. Claude split the work into parts: server + database, drawing, web page, then docs.
2. **Chat:** *"dont build now tell me how"*. Claude explained the four parts (form, server, database, SVG drawing) and the flow before writing any code.
3. **Claude Code:** *"check my folder"* and *"there is also a pdf called take home assignment, check that as well"*. It compared the project with the PDF: all 5 minimum requirements were met, but DECISIONS.md and the video were missing, and design names were not escaped in the SVG.
4. **Claude Code:** *"can we make our drawing more details and easy to understand"*. It added part names (main beam, end carriage, wheel, rail, hoist, hook), a parts list, a "how it moves" list and "(est.)" on every estimated size.
5. **Claude Code:** *"give canvas more space ... by default close the sidebar ... like how canva app works"*. It changed the page into an editor layout: icon bar, side panel, big canvas, zoom bar.

## One time the AI was wrong

When I made the span bigger, the crane in the drawing looked like it moved down and got lower. I asked why. Claude Code first said this was correct: the drawing is to scale, so a wider building must be shrunk more to fit the page. I did not accept that and said again that the crane visibly goes down. Then it found the real problem: the front view was fixed to the bottom of its box, so a wide (more shrunk) building sank and left a big empty space on top. The fix was to centre the view up and down. The scale part of the first answer was right, but "nothing is wrong" was not.

## Other things I checked

- **Page still showed the old drawing.** Claude Code said the new detailed drawing was done, but my page still showed the old one. I sent a screenshot. The server log showed the auto-reload had got stuck on Windows. Restarting the server fixed it.
- **Draw button was not needed.** After the drawing started updating by itself, I asked why we still needed a Draw button. It was removed and only kept on the empty start screen.
- **Load label not in the middle.** I noticed the load label ("15 t") on the beam was not centred and asked for it to be moved to the middle.
- **Name bug.** A design name with "&" or "<" broke the SVG file and could run code in the page. Claude Code found this in its review. Names are now escaped in `drawing.py`.
- **uvicorn not found.** Claude (chat) told me to start the server with `uvicorn main:app --reload`. On my Windows laptop this failed with *"The term 'uvicorn' is not recognized"*, because uvicorn was installed in a folder that is not on PATH. `python -m uvicorn main:app --reload` works, and that is the command in the README.
- **Fixed sizes don't scale.** When I drew a 1 t, 5 m crane, the height above the rail was still 1369, the same as the 10 t, 25 m reference crane. This is listed in the README under known limitations, and every such size is marked "(est.)" on the drawing.
- **Server didn't reload (first day).** After replacing main.py, the home page gave "Not Found". Restarting the server fixed it, and the next error showed `static/index.html` was in the wrong folder.
