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
            anchorTagArray[i]["href"] = "javascript:loadPage('" + (new URL(anchorTagArray[i]["href"])).pathname + "')";
        }
    }
}

class IndexPage extends Page {
    constructor() {
        super();
        this.body = ` (div (hash "children"
                        (list
                          (h1 (hash "innerHTML" "Dashboard"))
                          (a (hash "href" "/login" "innerHTML" "Login")) (br)
                          (a (hash "href" "/workers" "innerHTML" "Workers")))))`;
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

class WorkersPage extends Page {
    constructor() {
        super();
        this.body = ` (div (hash "children"
                        (list
                          (input (hash "type" "text" "id" "workerAddress" "placeholder" "0.0.0.0:8080"))
                          (button (hash "onclick" addWorkerOnClick "innerHTML" "Add Worker"))
                          (table (hash "children" workersTable))))`;

        this.tableHeader = `(tr (hash "children"
                              (list
                                (th (hash "innerHTML" "Worker Address"))
                                (th (hash "innerHTML" "Delete Worker")))))`;

        this.tableData = `(tr (hash "children"
                            (list
                              (td (hash "innerHTML" workerAddress))
                              (td (hash "children"
                                (list (button (hash "onclick" workerDeleteFunc "innerHTML" "Delete")))))`;
    }

    loadPage(updatePage=false) {
        this.workersTable = [generateDOM(this.tableHeader, {})];

        fetch("/api/workers")
        .then(resp => resp.json())
        .then(resp => {
            Object.keys(resp).forEach(workerID => {
                const rowParameters = {
                    workerAddress: resp[workerID]["workerAddress"],
                    workerDeleteFunc: () => currentPage.deleteWorker(workerID)
                };
                this.workersTable.push(generateDOM(this.tableData, rowParameters));
            });
            super.loadPage("/");
        });
    }

    addWorkerOnClick() {
        const workerAddress = document.getElementById("workerAddress").value;
        if (workerAddress) {
            fetch("/api/workers", {method: "POST", body: JSON.stringify({workerAddress: workerAddress})})
            .then(resp => resp.json())
            .then(resp => {
                currentPage.loadPage(true);
            });
        }
    }

    deleteWorker(workerID) {
        fetch("/api/workers/" + workerID, {method: "DELETE"})
        .then(resp => resp.json())
        .then(resp => {
            currentPage.loadPage(true);
        });
    }
}

const routes = {
    "/": {
        "body": IndexPage, "title": "Dashboard"
    },
    "/login": {
        "body": LoginPage, "title": "Login"
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

