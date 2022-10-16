//
//  index.js
//  caladium
//
//  Created by Declan Kelly on 12-10-2022.
//  Copyright © 2022 Declan Kelly. All rights reserved.
//

const routes = {
    "/": {
        "body": "<h1>Dashboard</h1><a href=\"/login\">Login</a>",
        "title": "Dashboard"
    },
    "/login": {
        "body": "<h1>Login</h1>",
        "title": "Login"
    }
};

function loadPage(path) {
    const page = routes[path];
    window.history.replaceState(undefined, "", path);

    while (document.body.childNodes[0]) {
        document.body.childNodes[0].remove();
    }

    document.write(page["body"]);
    const aTagArray = document.getElementsByTagName('a');
    for (let i = 0; i < aTagArray.length; i++) {
        aTagArray[i]["href"] = "javascript:loadPage('" + (new URL(aTagArray[i]["href"])).pathname + "')";
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

