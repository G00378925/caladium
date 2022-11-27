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
        return generateDOM(globalThis.currentPage.body, globalThis.currentPage);
    }
}

class IndexPage extends Page {
    constructor() {
        super();
        this.body = ` (div (hash "children"
                        (list
                          (h1 (hash "innerHTML" "Dashboard"))
                          (a (hash "href" "/login" "innerHTML" "Login")))))`;
    }
}

class LoginPage extends Page {
    constructor() {
        super();
        this.body = ` (center (hash "children"
                        (list
                          (h1 (hash "innerHTML" "Login")) (br)
                          (input (hash "type" "text" "id" "username" "placeholder" "Username")) (br)
                          (input (hash "type" "password" "id" "password" "placeholder" "Password")) (br)
                          (button (hash "onclick" loginButtonOnClick "innerHTML" "Login")))))`;
    }

    loginButtonOnClick() {
        alert("loginButtonOnClick");
    }
}

const routes = {
    "/": {
        "body": IndexPage,
        "title": "Dashboard"
    },
    "/login": {
        "body": LoginPage,
        "title": "Login"
    }
};

function loadPage(path) {
    const page = routes[path];
    window.history.replaceState(undefined, "", path);

    while (document.body.childNodes[0]) {
        document.body.childNodes[0].remove();
    }

    document.body.append((new page["body"]()).generateDOM());
    const anchorTagArray = document.getElementsByTagName('a');
    for (let i = 0; i < anchorTagArray.length; i++) {
        anchorTagArray[i]["href"] = "javascript:loadPage('" + (new URL(anchorTagArray[i]["href"])).pathname + "')";
    }

    document.title = page["title"];
}

function initialLoadPage() {
    const path = window.location.pathname;

    if (!routes[path]) {
        loadPage("/");
    } else {
        loadPage(path);
    }
}

