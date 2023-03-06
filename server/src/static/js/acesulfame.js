//
//  acesulfame.js
//  acesulfame
//
//  Created by Declan Kelly on 28-01-2023.
//  Copyright © 2023 Declan Kelly. All rights reserved.
//

// Get chart attributes
function _getChartAttributes(canvasID, data) {
    const canvas = document.getElementById(canvasID);
    const context = canvas.getContext("2d");

    // Get max value inside array
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
        "totalValue": data.map(i => i.value).reduce((i, j) => i + j, 0),
        "width": canvas.width
    };
}

// Render text
function _renderText(context, text, x, y, font) {
        context.beginPath();
        context.font = `20px ${font}`;
        context.fillStyle = "black";
        context.fillText(text, x, y);
        context.fill();
        context.closePath();
}

// Draw bar chart
function acesulfameBarchart(canvasID, data, font="Arial") {
    const attributes = _getChartAttributes(canvasID, data);
    const context = attributes.context;

    const barWidth = attributes.width / (attributes.elementCount * 2);
    const barHeight = attributes.height * 0.8;

    // Draw each bar
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

        const textXDelta = (barWidth / 2) - (data[i].title.length * 5);
        _renderText(context, data[i].title, barX + textXDelta, (attributes.height * 0.95), font);
    }
}

function acesulfamePiechart(canvasID, data, font="Arial") {
    const attributes = _getChartAttributes(canvasID, data);
    const context = attributes["context"];

    const piePositionX = attributes.height / 2, piePositionY = attributes.height / 2;
    const pieRadius = attributes.height * 0.4;
    const squareSize = 20, textBeginX = piePositionX + pieRadius;

    // Draw each slice
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

    // Draw legend
    for (let i = 0; i < data.length; i++) {
        context.beginPath();
        context.fillStyle = data[i]["colour"];
        context.rect(textBeginX, squareSize * i, squareSize, squareSize);
        context.fill();

        context.strokeStyle = "black";
        context.stroke();
        context.closePath();

        _renderText(context, data[i].title, textBeginX + (squareSize * 1.5), (squareSize * i) + squareSize, font);
    }
}

