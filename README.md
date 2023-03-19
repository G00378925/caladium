<!-- 12:50 19-03-2023 -->
<h1 align="center"><img src="client/pill.ico" width="45px"></img>Caladium</h1>

[![Python badge](https://img.shields.io/badge/language-python3-blue)](https://github.com/G00378925/caladium/search?l=python)
[![JavaScript badge](https://img.shields.io/badge/language-javascript-yellow)](https://github.com/G00378925/caladium/search?l=javascript)
[![Racket badge](https://img.shields.io/badge/language-racket-red)](https://github.com/G00378925/caladium/search?l=racket)
<br>

Caladium is my fourth-year applied software project, the title of my dissertation is "Malware detection using dynamic heuristic analysis".

Caladium is a platform that contains three subprojects, a Windows GUI application, a service side backend, and the sandbox analysis microservice,
technicians can set up analysis computers and add them to the network using the dashboard SPA.

- In `/client` you will find the code for the GUI Tkinter application.

- `/server` contains the Flask server and SPA dashboard.

- `/sandbox` contains the sandbox code and syscall analysis.

## Architecture Diagram
<div align="center"><img src="/dissertation/images/architecture.png" width="500px"></img></div>

- On the left you can find the client side this is everything that isn't running on a server, the single-page application is on the left because it runs in the user's browser.

- The middle is server-side, this contains the central flask server and the CouchDB database instance.

- On the right you will find the sandbox analysis services, these are the computers that are set up to run the sandbox analysis.

## Credits
- ClamAV - [https://www.clamav.net/](https://www.clamav.net/)
- Healthcare Medical Pill Icon - [https://freeicons.io/healthcare-2/healthcare-medical-pill-icon-43053](https://freeicons.io/healthcare-2/healthcare-medical-pill-icon-43053)
