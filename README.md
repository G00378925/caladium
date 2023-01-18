# Caladium

Caladium is my fourth year applied software project, the title of my dissertation is "Malware detection using dynamic heuristic analysis".

Caladium is a platform that contains three subprojects, a Windows GUI application, service side backend, and the sandbox analysis microservice,
technicans will have the ability to setup analysis computers, and add them to the network using the dashboard SPA.

- In `/client` you will find the code for the GUI Tkinter application.

- `/server` contains the Flask server and SPA dashboard.

- `/sandbox` contains the sandbox code, and syscall analysis.

The following is the architecture of the solution:
![test](/dissertation/images/architecture.png)

