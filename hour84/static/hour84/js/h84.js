// var HOST = '120.24.175.31:8000';
var HOST = '127.0.0.1:8000';
var ignore_login = true;
var socket = new WebSocket('ws://' + HOST + '/wss/chat/');
var index_username = document.querySelector('[name="username"]'),
    index_password = document.querySelector('[name="password"]'),
    index_setting = document.querySelector('[name="setting"]'),
    index_loginbtn = document.querySelector('.index-login-btn'),
    app_userlist = document.querySelector('.app-userlist');
var chatobj = '',
    user = '';

index_loginbtn.onclick = function() {
    socket.send(JSON.stringify({
        action: 'login',
        username: index_username.value,
        password: index_password.value,
        setting: index_setting.value,
    }));
    $('.index-info-message').text("");
}

function login_event(data) {
    console.log('login_event');
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
        action: 'load_userinfo'
    }));
}

// userinfo friend_list group_list
function load_userinfo_event(data) {
    print("load_userinfo_event");
    var userinfo = data.userinfo,
        friend_list = JSON.parse(data.friends),
        room_list = data.rooms;
    user = data.userinfo;
    var _uu = userinfo.username + ((userinfo.real_in_db) ? "(正式用户)" : "(匿名用户)");
    document.querySelector('.app-username').innerText = userinfo.username;
    document.querySelector('.app-usertype').innerText = ((userinfo.real_in_db) ? "(正式用户)" : "(匿名用户)");
    friend_list.forEach(ele => {
        add_frined(ele);
    });
    $(".app-online-usernum").text(data.online_usernum);
}

function add_frined(username) {
    $('.app-userlist').append("<button class='chat-friend'>" + username + "</button>");
}

function add_group(roomname) {

}

function register_event(data) {

}

function search_event(data) {

}

function message_event(data) {
    console.log(data);
    add_messgae(data['_from'], data['content']);

}

function send_message(_from, _to, message) {
    console.log(_from, "->", _to, " : ", message);
    socket.send(JSON.stringify({
        'action': "message",
        '_from': _from,
        '_to': _to,
        'content': message
    }));

    add_messgae(_from, message);
}

function add_messgae(_from, message) {
    console.log('add_messgae', _from, message);
    $(".app-msgs").append(
        "<p>" + _from + " : " + "</p>" +
        "<p>" + message + "</p>"
    )
}

function change_chatobj(_obj) {
    chatobj = _obj;
    $('.app-chatobj-name').text(_obj);

}

socket.onopen = function() {
    console.log('socket connect success');
}

socket.onmessage = function(e) {
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
    } else {
        console.log('router wrong....');
        console.log(data);
    }
}

socket.onclose = function() {


}

$(document).on('click', '.chat-friend', function(e) {
    // console.log(e);
    _name = e.currentTarget.innerText;
    change_chatobj(_name);
})

$('.app-sendmsg-btn').click(function(e) {
    var msg = $('textarea').val();
    $('textarea').text("");
    send_message(user.username, chatobj, msg);
})