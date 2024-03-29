//
//  index.js
//  caladium
//
//  Created by Declan Kelly on 12-10-2022.
//  Copyright © 2022 Declan Kelly. All rights reserved.
//

// All other pages inherit from this class
class Page {
    constructor() {
        // Allow event handlers to access the current page
        globalThis.currentPage = this;

        // This is the navigation bar at the top of the page
        this.navigationBar = generateDOM(`(div (hash "class" "clearfix" "children"
                                            (list
                                              (a (hash "class" "float-left" "href" "/"
                                                "children" (list (h1 (hash "innerHTML" "Caladium Dashboard")))))

                                              (button (hash "class" "float-right"
                                                "innerHTML" "Logout" "onclick" logout))
                                              (button (hash "class" "float-right" "style" "background-color: grey; border-color: grey"
                                                "innerHTML" "Preferences" "onclick" openPreferences)))))`, this);
    }

    // Fetch data from Caladium API, includes authorisation token
    async caladiumFetch(method, path, body=undefined) {
        try {
            // These are the parameters for the fetch request
            const caladiumFetchParameters = {
                method: method, headers: {"Authorisation": localStorage["Authorisation"]},
                body: body ? JSON.stringify(body) : undefined
            };
            const resp = await fetch(path, caladiumFetchParameters);
            return await resp.json();
        } catch (exception) {
            // If the fetch fails, then log the user out
            currentPage.logout();
            return {};
        }
    }

    // Called on page load, generates DOM and appends it to document.body
    generateDOM() {
        return generateDOM(this.body, this);
    }

    loadPage(updatePage=false) {
        // Play pageChangeSound
        if (localStorage["pageChangeSound"] == "true")
            pageChangeSound.play();

        // Make sure the page has no HTML elements before appending the new ones
        while (document.body.childNodes[0]) {
            document.body.childNodes[0].remove();
        }

        // Append the new HTML elements
        document.body.append(this.generateDOM());
        const anchorTagArray = document.getElementsByTagName('a');
        for (let i = 0; i < anchorTagArray.length; i++) {
            // Update all links to call loadPage()
            if (!anchorTagArray[i]["href"].startsWith("javascript:"))
                anchorTagArray[i]["href"] = "javascript:loadPage('" + (new URL(anchorTagArray[i]["href"])).pathname + "')";
        }
    }

    // Called when user clicks logout button
    logout() {
        // Remove authorisation token from localStorage and redirect to login page
        localStorage["Authorisation"] = undefined;
        window.location = "/login";
    }

    // Called when user clicks preferences button
    openPreferences() {
        loadPage("/preferences");
    }
}

class IndexPage extends Page {
    constructor() {
        super();
        this.body = ` (div (hash "children"
                        (list
                          navigationBar
                          (div (hash "children" cardList)))))`;

        const card = `(div (hash "class" "row" "onclick" cardOnClickFunc "children"
                        (list
                          (div (hash "class" "column column-75" "children"
                            (list (h1 (hash "innerHTML" pageName)))))
                          (div (hash "class" "column column-25" "children"
                            (list (canvas (hash "id" canvasID))))))))`;

        // This is the list of cards on the index page
        this.pageList = [
            {canvasID: "clients-canvas", cardOnClickFunc: () => loadPage("/clients"), pageName: "Clients"},
            {canvasID: "patterns-canvas", cardOnClickFunc: () => loadPage("/patterns"), pageName: "Patterns"},
            {canvasID: "tasks-canvas", cardOnClickFunc: () => loadPage("/tasks"), pageName: "Tasks"},
            {canvasID: "workers-canvas", cardOnClickFunc: () => loadPage("/workers"), pageName: "Workers"}
        ];

        this.cardList = this.pageList.map(page => generateDOM(card, page));
    }

    loadPage(updatePage=false) {
        super.loadPage("/");
        currentPage.caladiumFetch("GET", "/api/preferences/statistics")
        .then(resp => {
            // This is the data for the piechart
            const piechartData = [
                {"colour": "red", "title": "Malicious", "value": 75},
                {"colour": "green", "title": "Clean", "value": 25}
            ];

            // Render each of the piecharts
            resp.forEach(plotRecord => {
                if (plotRecord["plot_type"] == "barchart")
                    acesulfameBarchart(plotRecord["plot_name"], plotRecord["data"]);
                else
                    acesulfamePiechart(plotRecord["plot_name"], plotRecord["data"]);
            });
        });
    }
}

class LoginPage extends Page {
    constructor() {
        super();

        // This is the error message that appears when the user enters invalid credentials
        [this.errMessage, this.errMessageHidden] = [undefined, true];
        this.body = ` (div (hash "children"
                        (list
                          (center (hash "children"
                            (list
                              (h1 (hash "innerHTML" "Login")) (br))))
                          (blockquote (hash "hidden" errMessageHidden "innerHTML" errMessage))
                          (center (hash "children"
                            (list
                              (input (hash "type" "text" "id" "username" "placeholder" "Username")) (br)
                              (input (hash "type" "password" "id" "password" "placeholder" "Password")) (br)
                              (button (hash "onclick" loginButtonOnClick "innerHTML" "Login"))))))))`;
    }

    loginButtonOnClick() {
        const [username, password] = ["username", "password"]
        .map(id => document.getElementById(id).value);

        // Check if the username and password fields are empty
        if (!username.length || !password.length) {
            alert("Either the username or password field is empty.");
            return;
        }

        // Send POST request to login endpoint
        const requestBody = JSON.stringify({"username": username, "password": password});
        fetch("/api/login", {method: "POST", body: requestBody})
        .then(resp => resp.json())
        .then(resp => {
            if (resp["valid"]) {
                localStorage["Authorisation"] = resp["Authorisation"];
                loadPage("/");
            } else {
                // Show the error message
                currentPage.errMessage = resp["message"];
                currentPage.errMessageHidden = false;
                currentPage.loadPage(true);
            }
        })
    }
}

class PreferencesPage extends Page {
    constructor() {
        super();
        this.endpoint = "/api/preferences";

        // I need a space between the two buttons, not (hr)
        // This is the DOM Lisp expression for the preferences page
        this.body = ` (div (hash "children"
                        (list
                          navigationBar
                          (input (hash "type" "password" "id" "newPassword" "placeholder" "New Password"))
                          (button (hash "onclick" changePasswordOnClick "innerHTML" "Update Password"))
                          (hr)
                          (button (hash "onclick" toggleAutoProvision "innerHTML" autoProvisionButtonText))
                          (span (hash "innerHTML" "&nbsp;&nbsp;&nbsp;&nbsp;"))
                          (button (hash "onclick" toggleDynamicAnalysis "innerHTML" dynamicAnalysisButtonText))
                          (hr)
                          (button (hash "onclick" togglePageChangeSound "innerHTML" pageChangeSoundButtonText)))))`;
    }

    loadPage(updatePage=false) {
        currentPage.caladiumFetch("GET", this.endpoint)
        .then(resp => {
            this.preferences = resp;
            this.autoProvisionButtonText = (resp["auto_provision"] ? "Disable" : "Enable") + " Auto Provision";
            this.dynamicAnalysisButtonText = (resp["dynamic_analysis"] ? "Disable" : "Enable") + " Dynamic Analysis";
            this.pageChangeSoundButtonText = (localStorage["pageChangeSound"] == "true" ? "Disable" : "Enable") + " Page Change Sound";
            super.loadPage();
        });
    }

    changePasswordOnClick() {
        const newPassword = document.getElementById("newPassword").value;
        if (newPassword.length == 0) return;

        // Update admin password
        currentPage.caladiumFetch("PUT", currentPage.endpoint, {password: newPassword})
        .then(resp => {currentPage.loadPage(true);});
    }

    toggleAutoProvision() {
        // Toggle the auto provision preference
        currentPage.caladiumFetch("PUT", currentPage.endpoint, {"auto_provision": !currentPage.preferences["auto_provision"]})
        .then(resp => {currentPage.loadPage(true);});
    }

    toggleDynamicAnalysis() {
        // Toggle the dynamic analysis preference
        currentPage.caladiumFetch("PUT", currentPage.endpoint, {"dynamic_analysis": !currentPage.preferences["dynamic_analysis"]})
        .then(resp => {currentPage.loadPage(true);});
    }

    togglePageChangeSound() {
        // Will flip the status of the pageChangeSound
        localStorage["pageChangeSound"] = localStorage["pageChangeSound"] == "true" ? false : true;
        currentPage.loadPage(true);
    }
}

class ListPage extends Page {
    constructor() {
        super();
    }

    loadPage(updatePage=false) {
        this.elementsTable = [generateDOM(this.tableHeader, {})];

        currentPage.caladiumFetch("GET", this.endpoint)
        .then(resp => {
            Object.keys(resp).forEach(elementID => {
                this.elementsTable.push(generateDOM(this.tableData, currentPage.generateRowParameters(resp, elementID)));
            });
            super.loadPage();
        });
    }

    // Delete the element with the given ID
    deleteElement(elementID) {
        currentPage.caladiumFetch("DELETE", currentPage.endpoint + '/' + elementID, {})
        .then(resp => {
            currentPage.loadPage(true);
        });
    }

    // Delete all elements
    deleteAllElements() {
        currentPage.caladiumFetch("DELETE", currentPage.endpoint, {})
        .then(resp => {
            currentPage.loadPage(true);
        });
    }
}

class ClientsPage extends ListPage {
    constructor() {
        super();
        this.endpoint = "/api/clients";

        this.body = ` (div (hash "children"
                        (list
                          navigationBar
                          (button (hash "onclick" addClientOnClick "innerHTML" "Provision New Client"))
                          (button (hash "style" "background-color: red; border-color: red"
                            "onclick" deleteAllElements "innerHTML" "Delete All Clients"))
                          (table (hash "children" elementsTable))))`;

        this.tableHeader = `(tr (hash "children"
                              (list
                                (th (hash "innerHTML" "Client ID"))
                                (th (hash "innerHTML" "Get Provision Token"))
                                (th (hash "innerHTML" "Delete Client")))))`;

        this.tableData = `(tr (hash "children"
                            (list
                              (td (hash "innerHTML" clientID))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: blue; border-color: blue"
                                  "onclick" getProvisionTokenFunc "innerHTML" "Copy Token")))))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: red; border-color: red"
                                  "onclick" clientDeleteFunc "innerHTML" "Delete"))))))))`;
    }

    addClientOnClick() {
        currentPage.caladiumFetch("POST", currentPage.endpoint, {})
        .then(resp => {
            currentPage.loadPage(true);
        });
    }

    // Display the token to the user
    getProvisionTokenFunc(provisionToken) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(provisionToken);
            alert("Provisioning token copied to the clipboard.");
        } else {
            alert("Token: " + provisionToken);
        }
    }

    generateRowParameters(resp, elementID) {
        const rowParameters = {
            clientID: resp[elementID]["_id"],
            getProvisionTokenFunc: () => currentPage.getProvisionTokenFunc(resp[elementID]["token"]),
            clientDeleteFunc: () => currentPage.deleteElement(elementID)
        };
        return rowParameters;
    }
}

class PatternsPage extends ListPage {
    constructor() {
        super();
        this.endpoint = "/api/patterns";

        this.body = ` (div (hash "children"
                        (list
                          navigationBar
                          (input (hash "type" "text" "id" "patternString" "placeholder" "Malicious Pattern"))
                          (button (hash "onclick" addPatternOnClick "innerHTML" "Add Pattern"))
                          (button (hash "style" "background-color: red; border-color: red"
                            "onclick" deleteAllElements "innerHTML" "Delete All Patterns"))
                          (table (hash "children" elementsTable))))`;

        this.tableHeader = `(tr (hash "children"
                              (list
                                (th (hash "innerHTML" "Pattern String"))
                                (th (hash "innerHTML" "Delete Pattern")))))`;

        this.tableData = `(tr (hash "children"
                            (list
                              (td (hash "innerHTML" patternString))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: red; border-color: red"
                                  "onclick" patternDeleteFunc "innerHTML" "Delete"))))))))`;
    }

    // Will add a new pattern
    addPatternOnClick() {
        const patternString = document.getElementById("patternString").value;
        if (patternString) {
            currentPage.caladiumFetch("POST", currentPage.endpoint, {"pattern_string": patternString})
            .then(resp => {
                currentPage.loadPage(true);
            });
        }
    }

    generateRowParameters(resp, elementID) {
        const rowParameters = {
            patternString: resp[elementID]["pattern_string"],
            patternDeleteFunc: () => currentPage.deleteElement(elementID)
        };
        return rowParameters;
    }
}

class TasksPage extends ListPage {
    constructor() {
        super();
        this.endpoint = "/api/tasks";

        this.body = ` (div (hash "children"
                        (list
                          navigationBar
                          (button (hash "style" "background-color: red; border-color: red"
                            "onclick" deleteAllElements "innerHTML" "Delete All Tasks"))
                          (table (hash "children" elementsTable))))`;

        this.tableHeader = `(tr (hash "children"
                              (list
                                (th (hash "innerHTML" "Task ID"))
                                (th (hash "innerHTML" "Current State"))
                                (th (hash "innerHTML" "Task Creation Date"))
                                (th (hash "innerHTML" "Delete Task")))))`;

        this.tableData = `(tr (hash "children"
                            (list
                              (td (hash "innerHTML" taskID))
                              (td (hash "innerHTML" taskState))
                              (td (hash "innerHTML" taskCreationTimeStr))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: red; border-color: red"
                                  "onclick" taskDeleteFunc "innerHTML" "Delete"))))))))`;

        this.scanStateLabels = {
            "clean": "Clean",
            "completed": "Completed",
            "executing": "Executing",
            "failed": "Failed",
            "malware_detected": "Malware Detected"
        }
    }

    generateRowParameters(resp, elementID) {
        const rowParameters = {
            taskID: resp[elementID]["_id"],
            // Replace the state with a human-readable label.
            taskState: this.scanStateLabels[resp[elementID]["state"]],
            taskCreationTimeStr: resp[elementID]["creation_time_str"],
            taskDeleteFunc: () => currentPage.deleteElement(elementID)
        };
        return rowParameters;
    }
}

class WorkersPage extends ListPage {
    constructor() {
        super();
        this.endpoint = "/api/workers";

        this.body = ` (div (hash "children"
                        (list
                          navigationBar
                          (input (hash "type" "text" "id" "workerAddress" "placeholder" "0.0.0.0:8080"))
                          (button (hash "onclick" addWorkerOnClick "innerHTML" "Add Worker"))
                          (button (hash "style" "background-color: red; border-color: red"
                            "onclick" deleteAllElements "innerHTML" "Delete All Workers"))
                          (table (hash "children" elementsTable))))`;

        this.tableHeader = `(tr (hash "children"
                              (list
                                (th (hash "innerHTML" "Worker Address"))
                                (th (hash "innerHTML" "Ping Worker"))
                                (th (hash "innerHTML" "Kill Worker"))
                                (th (hash "innerHTML" "Delete Worker")))))`;

        this.tableData = `(tr (hash "children"
                            (list
                              (td (hash "innerHTML" workerAddress))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: blue; border-color: blue"
                                  "onclick" workerPingFunc "innerHTML" "Ping")))))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: red; border-color: red"
                                  "onclick" workerKillFunc "innerHTML" "Kill")))))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: red; border-color: red"
                                  "onclick" workerDeleteFunc "innerHTML" "Delete"))))))))`;
    }

    addWorkerOnClick() {
        const workerAddress = document.getElementById("workerAddress").value;
        if (workerAddress) {
            currentPage.caladiumFetch("POST", currentPage.endpoint, {"worker_address": workerAddress})
            .then(resp => {
                currentPage.loadPage(true);
            });
        }
    }

    generateRowParameters(resp, elementID) {
        const rowParameters = {
            workerAddress: resp[elementID]["worker_address"],
            workerPingFunc: () => currentPage.pingWorker(elementID),
            workerKillFunc: () => currentPage.killWorker(elementID),
            workerDeleteFunc: () => currentPage.deleteElement(elementID)
        };
        return rowParameters;
    }

    pingWorker(workerID) {
        currentPage.caladiumFetch("GET", currentPage.endpoint + "/ping/" + workerID)
        .then(resp => {
            alert(workerID + " is alive!");
        });
    }

    killWorker(workerID) {
        // This will kill a worker by ID
        currentPage.caladiumFetch("POST", currentPage.endpoint + "/kill/" + workerID)
    }
}

// These are all the defined pages
const routes = {
    "/": {
        "body": IndexPage, "title": "Dashboard"
    },
    "/clients": {
        "body": ClientsPage, "title": "Clients"
    },
    "/login": {
        "body": LoginPage, "title": "Login"
    },
    "/patterns": {
        "body": PatternsPage, "title": "Patterns"
    },
    "/preferences": {
        "body": PreferencesPage, "title": "Preferences"
    },
    "/tasks": {
        "body": TasksPage, "title": "Tasks"
    },
    "/workers": {
        "body": WorkersPage, "title": "Workers"
    }
};

// Call this function to load a path
function loadPage(path) {
    const page = routes[(new URL(window.location.origin + path)).pathname];
    window.history.replaceState(undefined, "", path);

    // Fetch page title and update it dynamically
    (new page["body"]()).loadPage();
    document.title = page["title"];
}

// Load the page on initial load
function initialLoadPage() {
    // If no specified page, load the index page
    if (!routes[window.location.pathname]) {
        loadPage("/");
    } else {
        // Otherwise, load the specified page
        loadPage(window.location.href.substring(window.location.origin.length));
    }
}

