//
//  index.js
//  caladium
//
//  Created by Declan Kelly on 12-10-2022.
//  Copyright © 2022 Declan Kelly. All rights reserved.
//

class Page {
    constructor() {
        globalThis.currentPage = this;

        this.navigationBar = generateDOM(`(div (hash "class" "clearfix" "children"
                                            (list
                                              (a (hash "class" "float-left" "href" "/"
                                                "children" (list (h1 (hash "innerHTML" "Caladium Dashboard")))))
                                              (button (hash "class" "float-right"
                                                "innerHTML" "Logout" "onclick" logout))
                                              (button (hash "class" "float-right" "style" "background-color: grey; border-color: grey"
                                                "innerHTML" "Preferences" "onclick" openPreferences)))))`, this);
    }

    async caladiumFetch(method, path, body=undefined) {
        try {
            const caladiumFetchParameters = {
                method: method, body: body ? JSON.stringify(body) : undefined
            };
            const resp = await fetch(path, caladiumFetchParameters);
            return await resp.json();
        } catch (exception) {
            currentPage.logout();
            return {};
        }
    }

    generateDOM() {
        return generateDOM(this.body, this);
    }

    loadPage(updatePage=false) {
        while (document.body.childNodes[0]) {
            document.body.childNodes[0].remove();
        }

        document.body.append(this.generateDOM());
        const anchorTagArray = document.getElementsByTagName('a');
        for (let i = 0; i < anchorTagArray.length; i++) {
            if (!anchorTagArray[i]["href"].startsWith("javascript:"))
                anchorTagArray[i]["href"] = "javascript:loadPage('" + (new URL(anchorTagArray[i]["href"])).pathname + "')";
        }
    }

    logout() {
        localStorage["Authorisation"] = undefined;
        window.location = "/login";
    }

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

        const card = ` (div (hash "class" "row" "onclick" cardOnClickFunc "children"
                         (list
                           (div (hash "class" "column column-75" "children"
                             (list (h1 (hash "innerHTML" pageName)))))
                           (div (hash "class" "column column-25" "children"
                             (list (canvas (hash "id" canvasID))))))))`;

        const pageList = [
            {canvasID: "clients-canvas", cardOnClickFunc: () => loadPage("/clients"), pageName: "Clients"},
            {canvasID: "tasks-canvas", cardOnClickFunc: () => loadPage("/tasks"), pageName: "Tasks"},
            {canvasID: "workers-canvas", cardOnClickFunc: () => loadPage("/workers"), pageName: "Workers"}
        ];

        this.cardList = pageList.map(page => generateDOM(card, page));
    }
}

class LoginPage extends Page {
    constructor() {
        super();
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
        const [username, password] = ["username", "password"].map(id => document.getElementById(id).value);

        if (!username.length || !password.length) {
            alert("Either the username or password field is empty.");
            return;
        }

        const requestBody = JSON.stringify({"username": username, "password": password});
        fetch("/api/login", {method: "POST", body: requestBody})
        .then(resp => resp.json())
        .then(resp => {
            localStorage["Authorisation"] = resp["Authorisation"];
            loadPage("/");
        })
        .catch(err => {
            currentPage.errMessage = err;
            currentPage.errMessageHidden = false;
            currentPage.loadPage(true);
        });
    }
}

class PreferencesPage extends Page {
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
            super.loadPage("/");
        });
    }

    deleteElement(elementID) {
        currentPage.caladiumFetch("DELETE", currentPage.endpoint + "/" + elementID, {})
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
                          (button (hash "onclick" addWorkerOnClick "innerHTML" "Provision New Client"))
                          (table (hash "children" elementsTable))))`;

        this.tableHeader = `(tr (hash "children"
                              (list
                                (th (hash "innerHTML" "Client ID"))
                                (th (hash "innerHTML" "Get Provision Token"))
                                (th (hash "innerHTML" "Delete Client")))))`;

        this.tableData = `(tr (hash "children"
                            (list
                              (td (hash "innerHTML" taskID))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: blue; border-color: blue"
                                  "onclick" getProvisionTokenFunc "innerHTML" "Copy Token"))))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: red; border-color: red"
                                  "onclick" taskDeleteFunc "innerHTML" "Delete"))))))))`;
    }

    generateRowParameters(resp, elementID) {
        const rowParameters = {
            clientID: resp[elementID]["_id"],
            getProvisionTokenFunc: () => currentPage.deleteElement(elementID),
            taskDeleteFunc: () => currentPage.deleteElement(elementID)
        };
        return rowParameters;
    }
}

class PatternsPage extends ListPage {
}

class TasksPage extends ListPage {
    constructor() {
        super();
        this.endpoint = "/api/tasks";

        this.body = ` (div (hash "children"
                        (list
                          navigationBar
                          (table (hash "children" elementsTable))))`;

        this.tableHeader = `(tr (hash "children"
                              (list
                                (th (hash "innerHTML" "Task ID"))
                                (th (hash "innerHTML" "Current State"))
                                (th (hash "innerHTML" "Delete Task")))))`;

        this.tableData = `(tr (hash "children"
                            (list
                              (td (hash "innerHTML" taskID))
                              (td (hash "innerHTML" taskStatus))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: red; border-color: red"
                                  "onclick" taskDeleteFunc "innerHTML" "Delete"))))))))`;
    }

    generateRowParameters(resp, elementID) {
        const rowParameters = {
            taskID: resp[elementID]["_id"],
            taskStatus: resp[elementID]["_id"],
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
                          (table (hash "children" elementsTable))))`;

        this.tableHeader = `(tr (hash "children"
                              (list
                                (th (hash "innerHTML" "Worker Address"))
                                (th (hash "innerHTML" "Ping Worker"))
                                (th (hash "innerHTML" "Delete Worker")))))`;

        this.tableData = `(tr (hash "children"
                            (list
                              (td (hash "innerHTML" workerAddress))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: blue; border-color: blue"
                                  "onclick" workerPingFunc "innerHTML" "Ping")))))
                              (td (hash "children"
                                (list (button (hash "style" "background-color: red; border-color: red"
                                  "onclick" workerDeleteFunc "innerHTML" "Delete"))))))))`;
    }

    addWorkerOnClick() {
        const workerAddress = document.getElementById("workerAddress").value;
        if (workerAddress) {
            currentPage.caladiumFetch("POST", currentPage.endpoint, {workerAddress: workerAddress})
            .then(resp => {
                currentPage.loadPage(true);
            });
        }
    }

    generateRowParameters(resp, elementID) {
        const rowParameters = {
            workerAddress: resp[elementID]["workerAddress"],
            workerPingFunc: () => currentPage.pingWorker(elementID),
            workerDeleteFunc: () => currentPage.deleteElement(elementID)
        };
        return rowParameters;
    }

    pingWorker(workerID) {
        currentPage.caladiumFetch("GET", currentPage.endpoint + "/ping/" + workerID)
        .then(resp => {
            alert(workerID);
        });
    }
}

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

function loadPage(path) {
    const page = routes[(new URL(window.location.origin + path)).pathname];
    window.history.replaceState(undefined, "", path);

    (new page["body"]()).loadPage();
    document.title = page["title"];
}

function initialLoadPage() {
    if (!routes[window.location.pathname]) {
        loadPage("/");
    } else {
        loadPage(window.location.href.substring(window.location.origin.length));
    }
}

