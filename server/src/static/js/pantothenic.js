//
//  pantothenic.js
//  pantothenic
//
//  Created by Declan Kelly on 16-11-2022.
//  Copyright © 2022 Declan Kelly. All rights reserved.
//

// Generate DOM from Lisp expression
function generateDOM(expressionStr, parameters) {
    // Helper functions
    const isNumber = (ch) => (ch.charCodeAt(0) >= '0'.charCodeAt(0) && ch.charCodeAt(0) <= '9'.charCodeAt(0)) || ch == '.';
    const isWhitespace = (ch) => ch.trim().length == 0;

    let i = 0;
    while (i < expressionStr.length && isWhitespace(expressionStr[i])) i++;
    if (expressionStr[i++] != '(') return null;

    let expressionList = [];
    // Parse expression
    while (i < expressionStr.length) {
        // Skip whitespace
        while (i < expressionStr.length && isWhitespace(expressionStr[i])) i++;

        // Parse expression
        if (expressionStr[i] == ')') {
            break;
        } else if (expressionStr[i] == '(') {
            expressionList.push(generateDOM(expressionStr.substring(i++), parameters));
            let nestingDepth = 1;

            for (; nestingDepth >= 1 && i < expressionStr.length; i++) {
                if (expressionStr[i] == '(') nestingDepth++;
                else if (expressionStr[i] == ')') nestingDepth--;
            }
            i++;
        } else if (isNumber(expressionStr[i])) {
            let newNumber = expressionStr[i++];

            for (; isNumber(expressionStr[i]) && i < expressionStr.length; i++)
                newNumber += expressionStr[i];

            if (newNumber.includes('.')) expressionList.push(parseFloat(newNumber));
            else expressionList.push(parseInt(newNumber));
        } else if (expressionStr[i] == '"') {
            let newString = expressionStr[++i];
            i++;

            for (; expressionStr[i] != '"' && i < expressionStr.length; i++)
                newString += expressionStr[i];

            expressionList.push(newString);
            i++;
        } else if (!isWhitespace(expressionStr[i])) {
            let newString = expressionStr[i++];

            for (; !isWhitespace(expressionStr[i]) && expressionStr[i] != ')' && i < expressionStr.length; i++)
                newString += expressionStr[i];

            if (expressionList.length == 0) expressionList.push(newString);
            else expressionList.push(parameters[newString]);
        }
    }

    // Expression above got converted to a list
    // Now convert them to HTML elements
    if (expressionList.length == 0) return null;
    switch (expressionList[0]) {
        // Hashes will be used as parameters to attributes
        case "hash": {
            let newHash = {};
            for (let j = 0; j < Math.floor((expressionList.length - 1) / 2); j++)
                newHash[expressionList[(j * 2) + 1]] = expressionList[(j * 2) + 2];
            return newHash;
        }
        // Lists will be used to list children
        case "list": {
            return expressionList.splice(1);
        }
        // Everything else will be used as an HTML element
        default: {
            let newElement = document.createElement(expressionList[0]);
            if (expressionList.length < 2) return newElement;
            if (Object.keys(expressionList[1]).includes("children")) {
                expressionList[1]["children"].forEach(i => {
                    newElement.append(i);
                });
            }
            Object.keys(expressionList[1]).filter(i => i != "children").forEach(i => {
                if (i == "class") newElement.setAttribute(i, expressionList[1][i]);
                else newElement[i] = expressionList[1][i];
            });
            return newElement;
        }
    }
}

