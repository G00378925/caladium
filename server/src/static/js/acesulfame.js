//
//  acesulfame.js
//  acesulfame
//
//  Created by Declan Kelly on 28-01-2023.
//  Copyright © 2023 Declan Kelly. All rights reserved.
//

function getChartAttributes(canvasID, data) {
    const canvas = document.getElementById(canvasID);
    const context = canvas.getContext("2d");

    function max(arr) {
        if (arr.length == 0) return 0;
        else if (arr.length == 1) return arr[0];

        let maxValue = 0;
        for (let i = 0; i < arr.length; i++) {
            if (arr[i] > maxValue) maxValue = arr[i];
        }
        return maxValue;
    }

    return {
        "context": context,
        "elementCount": data.length,
        "height": canvas.height,
        "maxValue": max(data.map(i => i.value)),
        "totalValue": data.map(i => i.value).reduce((i, j) => i + j),
        "width": canvas.width
    };
}

function acesulfameBarchart(canvasID, data) {
    const attributes = getChartAttributes(canvasID, data);
    const context = attributes.context;

    const barWidth = attributes.width / (attributes.elementCount * 2);
    const barHeight = attributes.height * 0.9;

    for (let i = 0; i < attributes.elementCount; i++) {
        const barX = (barWidth / 2) + (barWidth * (i * 2));
        const barY = barHeight - (barHeight * (data[i].value / attributes.maxValue));

        context.beginPath();
        context.fillStyle = data[i].colour;
        context.rect(barX, barY, barWidth, barHeight - barY);
        context.fill();

        context.strokeStyle = "black";
        context.stroke();
        context.closePath();

        context.beginPath();
        context.font = "20px Arial";
        context.fillStyle = "black";
        context.fillText(data[i].title, barX, attributes.height);
        context.fill();
        context.closePath();
    }
}

function acesulfamePiechart(canvasID, data) {
    const attributes = getChartAttributes(canvasID, data);
    const context = attributes["context"];

    const piePositionX = attributes.height / 2, piePositionY = attributes.height / 2;
    const pieRadius = attributes.height * 0.4;
    const squareSize = 20, textBeginX = piePositionX + pieRadius;

    let currentRadians = 0;
    data.forEach(slice => {
        const sliceRadians = (Math.PI * 2) * (slice.value / attributes.totalValue);

        context.beginPath();
        context.moveTo(piePositionX, piePositionY);

        context.fillStyle = slice.colour;
        context.arc(piePositionX, piePositionY, pieRadius, currentRadians, currentRadians + sliceRadians);
        context.fill();

        context.strokeStyle = "black";
        context.stroke();

        context.closePath();
        currentRadians += sliceRadians;
    });

    for (let i = 0; i < data.length; i++) {
        context.beginPath();
        context.fillStyle = data[i]["colour"];
        context.rect(textBeginX, squareSize * i, squareSize, squareSize);
        context.fill();

        context.strokeStyle = "black";
        context.stroke();
        context.closePath();

        context.beginPath();
        context.font = "20px Arial";
        context.fillStyle = "black";
        context.fillText(data[i].title, textBeginX + (squareSize * 1.5), (squareSize * i) + squareSize);
        context.fill();
        context.closePath();
    }
}

