// var HOST = '120.24.175.31:8000';
// var HOST = '127.0.0.1:8000';
var HOST = window.location.host;
var has_login = false;
var socket = new WebSocket('ws://' + HOST + '/wss/chat/');
var index_username = document.querySelector('[name="username"]'),
    index_password = document.querySelector('[name="password"]'),
    index_setting = document.querySelector('[name="setting"]'),
    app_userlist = document.querySelector('.app-userlist'),
    index_login_btn = $('.index-login-btn'),
    app_search_input = $('.app-left-pane-bottom-top-input'),
    app_search_btn = $('.app-left-pane-bottom-top-btn'),
    app_left_userbtn = $('.app-left-userbtn'),
    app_left_roombtn = $('.app-left-roombtn');
var chatobj = '',
    user = '';

function login_success() {
    has_login = true;
    socket.send(JSON.stringify({
        action: 'load_userinfo'
    }));
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


function load_userinfo_event(data) {
    console.log("load_userinfo_event");
    var userinfo = data.userinfo,
        friend_list = JSON.parse(data.friends),
        room_list = data.rooms;
    user = data.userinfo;
    var _uu = userinfo.username + ((userinfo.real_in_db) ? "(正式用户)" : "(匿名用户)");
    document.querySelector('.app-username').innerText = userinfo.username;
    document.querySelector('.app-usertype').innerText = ((userinfo.real_in_db) ? "(正式用户)" : "(匿名用户)");
    friend_list.forEach(ele => {
        add_listitem(ele, 'user');
    });
    $(".app-online-usernum").text(data.online_usernum);
}

function add_listitem(_itemname, _listname) {
    if (_listname === 'user') {
        _list = $('.app-userlist');
        if (_list.has('#user-' + _itemname).length === 0) {
            _list.append("<button class='chat-item' id='user-%d'>".replace("%d", _itemname) + _itemname + "</button>");
        }
    } else if (_listname === 'room') {
        _list = $('.app-roomlist');
        if (_list.has('#room-' + _itemname).length === 0) {
            _list.append("<button class='chat-item' id='room-%d'>".replace("%d", _itemname) + _itemname + "</button>");
        }
    } else if (_listname === 'search') {
        _list = $('.app-searchlist');
        if (_list.has('#search-' + _itemname).length === 0) {
            _list.append("<button class='chat-item' id='search-%d'>".replace("%d", _itemname) + _itemname + "</button>");
        }
    } else {
        console.log("add_listitem wrong :", _listname);
    }
}

function register_event(data) {

}

function search_event(data) {
    console.log("search_event");
    match_list = JSON.parse(data['match_list']);
    $('.app-searchlist').html(`<h3>搜索结果：</h3>`);
    match_list.forEach(ele => {
        console.log(ele);
        add_listitem(ele, 'search');
    })
    $('.app-left-list').hide();
    $('.app-searchlist').show();
}

function message_event(data) {
    console.log('message_event');
    add_messgae(data['_from'], data['content'], data['_from']);
}

function send_message(_from, _to, message) {
    console.log(_from, "->", _to, " : ", message);
    socket.send(JSON.stringify({
        'action': "message",
        '_from': _from,
        '_to': _to,
        'content': message
    }));
    add_messgae(_from, message, _to);
}

function add_messgae(_from, message, _pane) {
    var msg = `<div class="app-message">
    <img src="../../static/hour84/img/tx.jpg">
    <div class="app-message-top-userinfo">%s</div>%m<hr/>
</div>`;
    console.log('add_messgae', _from, message);
    var panname = 'message-pane-%d'.replace("%d", _pane);
    $('#' + panname).append(msg.replace("%s", _from).replace("%m", message));
}

function change_chatobj(_obj) {
    chatobj = _obj;
    $('.app-chatobj-name').text(_obj);
    var panname = 'message-pane-%d'.replace("%d", _obj);
    if ($("#" + panname).length == 0) {
        $(".app-right-pane-body").append(`<div class="message-pane" id="message-pane-%d"></div>`.replace("%d", _obj));
        $("#" + panname).hide();
    }
    $('.message-pane').hide();
    $('#' + panname).show();
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
        // console.log(data);
    }
}

socket.onclose = function() {

}

$(document).on('click', '.chat-item', function(e) {
    console.log(e);
    e = e.currentTarget;
    change_chatobj(e.innerText);
    if (e.id.startsWith('search')) {
        add_listitem(e.innerText, 'user');
    }
})

$('.app-sendmsg-btn').click(function(e) {
    var msg = $('textarea').val();
    // console.log(msg);
    if (msg.length > 2 && chatobj != '') {
        $('textarea').val("");
        send_message(user.username, chatobj, msg);
    }
})

$(document).keydown(function(e) {
    // console.log(e.keyCode);
    if (e.keyCode === 13) {
        has_login ? $('.app-sendmsg-btn').click() : $('.index-login-btn').click();
    }
});

index_login_btn.click(function() {
    socket.send(JSON.stringify({
        action: 'login',
        username: index_username.value,
        password: index_password.value,
        setting: index_setting.value,
    }));
    $('.index-info-message').text("");
});

app_search_btn.click(function() {
    var search_value = app_search_input.val();
    if (search_value.length > 0) {
        app_search_input.val("");
        socket.send(JSON.stringify({
            'action': 'search',
            'content': search_value,
        }));
    } else {
        alert('请输入内容再搜索');
    }
});

app_left_userbtn.click(function() {
    $('.app-left-list').hide();
    $('.app-userlist').show();
});

app_left_roombtn.click(function() {
    $('.app-left-list').hide();
    $('.app-roomlist').show();
});