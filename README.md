<!-- 12:50 19-03-2023 -->
<h1 align="center"><img src="client/pill.ico" width="45px"></img>Caladium</h1>

[![Python badge](https://img.shields.io/badge/language-python3-blue)](https://github.com/G00378925/caladium/search?l=python)
[![JavaScript badge](https://img.shields.io/badge/language-javascript-yellow)](https://github.com/G00378925/caladium/search?l=javascript)
[![Racket badge](https://img.shields.io/badge/language-racket-red)](https://github.com/G00378925/caladium/search?l=racket)

Caladium is my [fourth-year applied software project](https://www.gmit.ie/applied-project-and-minor-dissertation),
the title of my dissertation is "**Malware detection using dynamic heuristic analysis**".
[It can be found here](dissertation/dissertation.pdf)

The project aims to detect malicious files by identifying patterns in them.
Users can upload files to the platform for scanning, and receive real-time feedback on the status.
If a match is found, the user will be prompted to quarantine the file.

The scanning process involves two methods: dynamic analysis and static analysis.
Dynamic analysis involves executing the malware in a sandboxed environment,
which is achieved through the use of [Sandboxie](https://sandboxie-plus.com/).

[Procmon](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon)
is used to log the syscalls performed during the process execution.
Whereas [ClamAV](https://www.clamav.net/), is used to perform static analysis,
it is a free and open-source anti-virus engine that checks a database of known malicious patterns of strings and bytes.

The platform includes a dashboard single-page application for administrators in an enterprise to perform administrative tasks.
The platform comprises three sub-projects: a Windows GUI application, a server-side backend and sandbox analysis workers.
Technicians can set up analysis computers and add them to the platform using the dashboard.

- In `client/src` you will find the code for the Windows GUI Tkinter application.

- `server/src` contains the Flask server and the dashboard SPA can be found in `server/src/static/js`.

- `sandbox/src` contains the code to setup the sandbox and syscall analysis.

If you are looking to setup the platform yourself, instructions can be found under the **Building** header below.
Don't forget to check my [promotional page which can be found here](https://g00378925.github.io/caladium/).
**_Make sure to ask CaladiumBot some questions about the platform, it is powered by GPT 3.5!_**

## Screencast Demonstration

<div align="center">
    <a href="https://www.youtube.com/watch?v=aYbQChGvz88">
        <img src="https://img.youtube.com/vi/aYbQChGvz88/0.jpg" alt="Screencast">
    </a>
</div>

**_Click on the video to open it in YouTube._**

## Features of the Platform
- Client
    + An installer file is created as part of the client's build process,
    which can be downloaded and installed by users. They can also choose to uninstall it from the preferences menu.
    + Upon starting, the client is listening for changes in the `Downloads` directory,
    it will detect new files downloaded by the user and prompt them to scan it.
    + During the scan process, the server will randomly assign a worker to handle the analysis.
    Users will receive real-time feedback with a progress bar and text.
    If the file is identified as malicious, the user will be prompted to quarantine it.
    + The quarantine is a secure storage space for potentially malicious files,
    which can be accessed in the **Quarantine** section.
    Users can view a list of files present in the quarantine and choose to add or restore files.
    + The files stored in the quarantine are encrypted with an XOR cipher to prevent accidental execution of malware.
    + Users can change the scanning directory, which defaults to the `Downloads` directory.
    Users also have the option to unprovision from the platform, which will require them to re-authenticate with the server.

- Dashboard
    + To access the dashboard, the administrator needs to enter a valid username and password, which by default is set as `root`.
    Once logged in, the administrator can navigate to the **Preferences** page to change the default password.
    + The dashboard allows administrators to perform administrative tasks related to **Clients**, **Patterns**, **Tasks** and **Workers**.
    Each of these pages is linked to from the index page and includes a plot that shows relevant data,
    such as the ratio of clean to malicious files for analysis.
    + On the **Clients** page, administrators can provision new clients by generating an authentication token for them.
    + The **Tasks** page lists all past and present tasks and shows their current state, such as `Malware Detected`, `Executing` or `Clean`.
    + The **Preferences** page allows administrators to disable dynamic analysis or auto-provisioning for clients,
    which automatically generates authentication tokens upon installation. This feature can be disabled for security reasons.
    + On the **Workers** page, administrators can add workers by IP address.
    The **Patterns** page is where administrators can input patterns to be identified during dynamic analysis.

- Server
    + Communication through RESTful APIs requires authorisation with an `Authorisation` token in all requests.
    + CouchDB stores persistent data, including records for the `clients`, `patterns`, `tasks` and `workers` tables.
    + Flask is used to construct collections of RESTful APIs for the tables listed above.
    A server thread is created to receive real-time feedback from the sandbox analysis when a new scan task is created.
    + An action is executed when new code is committed to the GitHub repository, running tests found in `server/tests`.
    This is useful to identify any new code that causes problems with the API endpoints, and checks if records can be saved and retrieved.
    [Learn more here](server/README.md).

- Sandbox Analysis
    + The analysis service receives a file to be scanned along with its name,
    and additional parameters such as whether to skip dynamic analysis and a list of patterns to look for when scanning the syscalls.
    + An instance of Procmon is launched, and the file is executed within a Sandboxie instance.
    The analysis service waits for the file to finish executing, and if it takes too long to close, it is automatically terminated.
    The syscalls made by the process are collected, and the analysis service checks them in parallel against the provided patterns.
    + During the scanning process, the analysis service sends log messages back to the client,
    along with a percentage of completion and a status string that indicates the current state.
    Possible states include `executing` and `malware_detected`.
    + After the scan is completed, the analysis service automatically cleans up any files that were created
    during the analysis and prepares itself for another scan.

## Architecture
<div align="center"><img src="/dissertation/images/architecture.png" width="500px"></img></div>

- On the left you can find the client side this is everything that isn't running on a server,
  the single-page application is on the left because it runs in the user's browser.
    + Clients (GUI application and dashboard) communicate with the server using a RESTful API.
    + The browser dashboard is written in JavaScript and doesn't require any external frameworks.
    + The Windows GUI application uses the Tkinter Python library for the GUI,
    and the tkthread library for threads that won't block the Tkinter thread of execution.

- The center is server-side, this contains the central flask server and the CouchDB database instance.
  The server will broker communication between the client and the analysis service.

- On the right you will find the sandbox analysis service(s),
  these are the computers that are set up to run the sandbox analysis.
    + The real-time feedback to passed back to the server using TCP.

## Building
First retrieve the latest build of Caladium, you can do that with this command:
`git clone https://github.com/G00378925/caladium.git`.

Python is a requirement for all the projects, you can
[download and install, the latest version for your system here](https://www.python.org/downloads/).

<!-- --><!-- --><!--        --><!-- --><!-- -->
<!-- --><!-- --><!--        --><!-- --><!-- -->
<!-- --><!-- --><!-- Client --><!-- --><!-- -->
<!-- --><!-- --><!--        --><!-- --><!-- -->
<!-- --><!-- --><!--        --><!-- --><!-- -->
### Client
You must make sure you are on Microsoft Windows for this part as `iexpress.exe` is required.
Run the following commands in `Command Prompt`, making sure you are in the Caladium root directory.
```batch
cd client
python -m pip install -r requirements.txt

rem You will be prompted to enter the IP address of the Caladium server
build.cmd
```
This will result in a `caladium-setup.exe` in the `dist` directory, this is the installer that will be given to users.
<!-- --><!-- --><!--        --><!-- --><!-- -->
<!-- --><!-- --><!--        --><!-- --><!-- -->
<!-- --><!-- --><!-- Server --><!-- --><!-- -->
<!-- --><!-- --><!--        --><!-- --><!-- -->
<!-- --><!-- --><!--        --><!-- --><!-- -->
### Server
To build and run the server, enter the following commands into your terminal, these should work on Linux, macOS and Windows.

You need the address of your CouchDB instance this needs to be put in the environmental variable `COUCHDB_CONNECTION_STR`.
If on Windows use `set COUCHDB_CONNECTION_STR=admin:root@0.0.0.0:5984`,
if on Linux or macOS use `export COUCHDB_CONNECTION_STR=admin:root@0.0.0.0:5984`.
With `admin:root@0.0.0.0:5984` being the CouchDB connection string.

Make sure to swap out `python3` with `python` if executing on Windows.
```batch
cd server/src

python3 -m pip install flask requests
python3 __main__.py
```
The address of the instance will be printed to the terminal.

#### Using Docker
Instead of having to setup an environment manually, you can use the supplied Dockerfile
to setup a reproducible environment, replace the `0.0.0.0:5984` in the commands below like above.

Make sure you have Docker installed on your system, and type the following into your terminal.

```shell
cd server
sudo docker build --tag caladium .
sudo docker run -e COUCHDB_CONNECTION_STR="http://admin:root@0.0.0.0:5984" -p 80:8080 caladium
```
<!-- --><!-- --><!--                  --><!-- --><!-- -->
<!-- --><!-- --><!--                  --><!-- --><!-- -->
<!-- --><!-- --><!-- Sandbox Analysis --><!-- --><!-- -->
<!-- --><!-- --><!--                  --><!-- --><!-- -->
<!-- --><!-- --><!--                  --><!-- --><!-- -->
### Sandbox Analysis
To setup the analysis service on a computer, you must first [install Racket](https://download.racket-lang.org/).
Create a `SysinternalsSuite` directory at the root of your drive, this is usually `C:\SysinternalsSuite`.
Place `Procmon64.exe` in there, you can [download it here](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon).

ClamAV is required for the static analysis, I am using a distribution of ClamAV called ClamWin,
[which can downloaded here](https://clamwin.com/content/view/18/46/), ClamWin will automatically download the latest malware definitions.

Run a new Command Prompt as administrator, and run `cd sandbox && start_sandbox.cmd`.
The analysis service will now poll for tasks, in the case of it crashing it will automatically restart.
Note the IP address and port of the service, in the format `0.0.0.0:8080` and add it to the adminstrator dashboard.

## Credits
- ClamAV - [https://clamwin.com/](https://clamwin.com/)
- Healthcare Medical Pill Icon - 
[https://freeicons.io/healthcare-2/healthcare-medical-pill-icon-43053](https://freeicons.io/healthcare-2/healthcare-medical-pill-icon-43053)