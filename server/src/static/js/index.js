//
//  index.js
//  caladium
//
//  Created by Declan Kelly on 12-10-2022.
//  Copyright © 2022 Declan Kelly. All rights reserved.
//

const routes = {
    "/": {
        "body": ` (div (hash "children"
                      (list
                          (h1 (hash "innerHTML" "Dashboard"))
                          (a (hash "href" "/login" "innerHTML" "Login")))))`,
        "title": "Dashboard"
    },
    "/login": {
        "body": `(h1 (hash "innerHTML" "Login"))`,
        "title": "Login"
    }
};

function loadPage(path) {
    const page = routes[path];
    window.history.replaceState(undefined, "", path);

    while (document.body.childNodes[0]) {
        document.body.childNodes[0].remove();
    }

    document.body.append(generateDOM(page["body"], {}));
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

