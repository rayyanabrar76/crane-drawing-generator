# AI Log

## Tools used

- **Claude (claude.ai chat, Claude Opus 5.5)**: explained the brief to me in simple words, wrote the code (FastAPI server, SQLite storage, SVG drawing, web page), the README and this log draft, and helped me fix errors on my laptop from screenshots.
- **VS Code**: editing, running the server, and committing to GitHub.

I tested every part myself in the browser before committing.

## Key prompts

These are my real messages (short, informal), in order:

1. Pasted the full assignment PDF and asked: *"what"* / *"tell me what we gonna do now"*. Claude split the work into parts: server + database, drawing, web page, then docs.
2. *"dont build now tell me how"*. Claude explained the four parts (form, server, database, SVG drawing) and the flow before writing any code.
3. *"okay ig"*. Claude wrote part 1: API with save / list / open / edit / delete and server-side range checks.
4. *"yeah now"*. Claude wrote part 2: the drawing module, taking fixed sizes from the reference drawing and marking them as estimates.
5. Sent a screenshot of the working drawing. Claude wrote part 3: the web page.

## One time the AI was wrong

Claude told me to start the server with `uvicorn main:app --reload`. On my Windows laptop this failed with *"The term 'uvicorn' is not recognized"*. I saw the red error in the terminal and sent it back. The pip output showed uvicorn was installed in a folder that is not on PATH. The fix was `python -m uvicorn main:app --reload`, which works without PATH. I put this version in the README so others don't hit the same problem.

## Other things I checked

- **Fixed sizes don't scale.** When I drew a 1 t, 5 m crane, the height above the rail was still 1369, the same as the 10 t, 25 m reference crane. The AI copied that number from the reference drawing. This is now listed in README under known limitations.
- **Server didn't reload.** After replacing main.py, the home page gave "Not Found". Restarting the server fixed it, and the next error showed `static/index.html` was in the wrong folder.
