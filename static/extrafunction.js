function temperatureUpdate() {
    let temperatureValue = $("#temperature_value");
    let temperatureTime = $("#temperature_time");
    temperatureValue.attr('class', 'count fas fa-spinner fa-pulse');
    temperatureValue.html('');
    $.ajax({
        url: "update/temperature",
        success:
            function(out) {
                temperatureValue.attr('class', 'count');
                temperatureValue.html(out.value + '°');
                temperatureTime.html('Last Updated: ' + out.time);
            }})
}

function brightnessUpdate() {
    let brightValue = $("#brightness_value");
    let brightTime = $("#brightness_time");
    brightValue.attr('class', 'count fas fa-spinner fa-pulse');
    brightValue.html('');
    $.ajax({
    url: "update/brightness",
    success:
        function(out) {
            brightValue.attr('class', 'count');
            brightValue.html(out.value);
            brightTime.html('Last Updated: ' + out.time);
        }})

}

function ledUpdate() {
    let ledValue = $("#led_value");
    let ledTime = $("#led_time");
    ledValue.attr('class', 'count fas fa-spinner fa-pulse');
    ledValue.html('');
    $.ajax({
    url: "update/led",
    success:
        function(out) {
            ledValue.attr('class', 'count');
            ledValue.html(out.value);
            ledTime.html('Last Updated: ' + out.time);
        }})
}

function humidityUpdate() {
    let humidityValue = $("#humidity_value");
    let humidityTime = $("#humidity_time");
    humidityValue.attr('class', 'count fas fa-spinner fa-pulse');
    humidityValue.html('');
    $.ajax({
    url: "update/humidity",
    success:
        function(out) {
            humidityValue.attr('class', 'count');
            humidityValue.html(out.value);
            humidityTime.html('Last Updated: ' + out.time);
        }})
}

document.getElementById("humidity_update").addEventListener("click", humidityUpdate, false);
document.getElementById("led_update").addEventListener("click", ledUpdate, false);
document.getElementById("temperature_update").addEventListener("click", temperatureUpdate, false);
document.getElementById("brightness_update").addEventListener("click", brightnessUpdate, false);

google.charts.load('current', {'packages':['table']});
google.charts.setOnLoadCallback(create_table);

function create_table(){
    $.ajax({
        method: 'POST',
        url: 'api/get_chat',
        success:
            function(data){
                drawTable(data, 'chat_table')
            }
    })
}

function drawTable(data, element_id) {
    dt = new google.visualization.DataTable();
    dt.addColumn('number', 'ID');
    dt.addColumn('string', 'Chat');
    dt.addColumn('boolean', 'Status');
    dt.addColumn('string', 'Date | Time');
    dt.addRows(data);

    showTable(dt, element_id)
}

function showTable(data, element_id){
    var table = new google.visualization.Table(document.getElementById(element_id));
    table.draw(dt, {showRowNumber: false, width: '100%', height: '100%'});

}

function update_all() {
    humidityUpdate();
    temperatureUpdate();
    brightnessUpdate();
    create_table()
}

var load = setInterval(update_all, 10000);