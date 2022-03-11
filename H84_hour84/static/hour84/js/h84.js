// var HOST = '120.24.175.31:8000';
var HOST = '127.0.0.1:8000';
var socket = new WebSocket('ws://' + HOST + '/wss/chat/');
var index_username = document.querySelector('[name="username"]'),
    index_password = document.querySelector('[name="password"]'),
    index_setting = document.querySelector('[name="setting"]'),
    index_loginbtn = document.querySelector('.index-submit-btn');

index_loginbtn.onclick = function () {
    socket.send(JSON.stringify({
        action: 'login',
        username: index_username.value,
        password: index_password.value,
        setting: index_setting.value,
    }));
}

function login_event(data) {
    if (data['status'] === true) {
        document.querySelector('.index').setAttribute('class', 'index whole-page hide');
        document.querySelector('.app').setAttribute('class', 'app whole-page');
        alert('login success');
        login_success();
    } else {
        document.querySelector('.index-info-message').innerText = data['reason'];
    }
}

function login_success() {
    socket.send(JSON.stringify({
        action: 'load_userinfo',
        username: index_username,
    }));
}

// userinfo friend_list group_list
function load_userinfo(data) {
    var userinfo = data.userinfo,
        friend_list = data.friend_list,
        group_list = data.group_list;
}

function add_frined(username) {

}

function add_group(roomname) {

}

function register_event(data) {

}

function search_event(data) {

}

function message_event(data) {

}


socket.onopen = function () {
    console.log('socket connect success');
}

socket.onmessage = function (e) {
    var data = JSON.parse(e.data);
    console.log(data);
    if (data.action === 'login') {
        login_event(data);
    } else if (data.action == 'register') {
        register_event(data);
    } else if (data.action === 'search') {
        search_event(data);
    } else if (data.action === 'message') {
        message_event(data);
    } else if (data.action == 'load_userinfo') {
        load_userinfo_event(data);
    }
}

socket.onclose = function () {


}
