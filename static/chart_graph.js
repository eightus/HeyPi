google.charts.load('current', {packages: ['corechart', 'line']});
google.charts.setOnLoadCallback(create_all);

function create_all() {
    $.ajax({
        method: 'POST',
        url: 'api/get_all',
        success:
            function(data) {
                drawTable(data.data_humidity, 'humidityGraph', '(%)', 'Humidity %');
                drawTable(data.data_temperature, 'temperatureGraph', '(°C)', 'Temperature °C');
                drawTable(data.data_brightness, 'brightnessGraph', '(%)', 'Brightness %');
            }
    })

    // new graph shows number of chats
}

function drawTable(data, element_id, columnText, titleText) {
    dt = new google.visualization.DataTable();
    dt.addColumn('string', 'Time');
    dt.addColumn('number', columnText);
    for (i in data) {
        dt.addRows([data[i]]);
    }

    options = {
        legend: 'none',
        hAxis: {
            title: 'Time: H:M:S'
        },
        vAxis: {
            title: titleText
        }
    };

    drawGraph(dt, options, element_id);

}

function drawGraph(dt, options, element_id) {
    var chart = new google.visualization.LineChart(document.getElementById(element_id));
    chart.draw(dt, options);
}

var load = setInterval(create_all, 1000);
