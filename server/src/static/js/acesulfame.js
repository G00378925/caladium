//
//  acesulfame.js
//  acesulfame
//
//  Created by Declan Kelly on 28-01-2023.
//  Copyright © 2023 Declan Kelly. All rights reserved.
//

function get2DContext(canvas) {
    if (typeof(canvas) == "string") return document.getElementById(canvas).getContext("2d");
    return canvas.getContext("2d");
}

function getChartAttributes(canvas, data) {
    return {
        "context": get2DContext(canvas),
        "elementCount": data.length,
        "height": canvas.height,
        "maxValue": data.map(i => i.value).reduce((i, j) => i + j),
        "width": canvas.width
    };
}

function acesulfameBarchart(canvas, data) {
    const attributes = getChartAttributes(canvas, data);
    const context = attributes["context"];

    for (let i = 0; i < attributes.elementCount; i++) {
    }
}

function acesulfamePiechart(canvas, data) {
    const attributes = getChartAttributes(canvas, data);
    const context = attributes["context"];

    console.log(attributes);

    const piePositionX = attributes.height / 2, piePositionY = attributes.height / 2;
    const pieRadius = attributes.height * 0.4;

    let currentRadians = 0;
    data.forEach(slice => {
        const sliceRadians = (Math.PI * 2) * (slice.value / attributes.maxValue);

        context.beginPath();
        context.moveTo(piePositionX, piePositionY);

        context.fillStyle = slice["colour"];
        context.arc(piePositionX, piePositionY, pieRadius, currentRadians, currentRadians + sliceRadians);
        context.fill();

        context.strokeStyle = "black";
        context.stroke();

        context.closePath();
        currentRadians += sliceRadians;
    });

    const textBeginX = piePositionX + pieRadius;
    for (let i = 0; i < data.length; i++) {
    }
}

