// var HOST = '120.24.175.31:8000';
// var HOST = '127.0.0.1:8000';
var HOST = window.location.host;
var has_login = false;
var socket = new WebSocket('ws://' + HOST + '/wss/chat/');
var index_page = '.index',
    index_username = '[name="username"]',
    index_password = '[name="password"]',
    index_setting = '[name="setting"]',
    index_login_btn = '.index-login-btn',
    index_info_message = '.index-info-message';

var app_page = '.app',
    app_search_input = '.app-left-pane-bottom-top-input',
    app_search_btn = '.app-left-pane-bottom-top-btn',
    app_left_userbtn = '.app-left-userbtn',
    app_left_roombtn = '.app-left-roombtn',
    app_username = '.app-username',
    app_usertype = '.app-usertype',
    app_online_usernum = ".app-online-usernum",
    app_leftlist = '.app-left-list',
    app_userlist = '.app-userlist',
    app_roomlist = '.app-roomlist',
    app_searchlist = '.app-searchlist',
    app_chatobj_name = '.app-chatobj-name',
    app_message_pane = '.message-pane',
    app_sendmsg_btn = '.app-sendmsg-btn',
    // app_message_input = '#app-message-input',
    app_message_input = 'textarea',
    app_right_panel_body = ".app-right-pane-body",
    app_add_room = '.app-roomlist > h3';

var chatobj_name = '',
    chatobj_type = 'user';

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
    } else if (data.action == 'online_user_update') {
        online_user_update_event(data);
    } else {
        console.log('router wrong....');
        // console.log(data);
    }
}



function login_success() {
    has_login = true;
    socket.send(JSON.stringify({
        action: 'load_userinfo'
    }));
}

function login_event(data) {
    console.log('login_event');
    if (data['status'] === true) {
        $(index_page).hide();
        $(app_page).show();
        alert('login success');
        login_success();
    } else {
        $(index_info_message).text(data['reason']);
    }
}


function load_userinfo_event(data) {
    console.log("load_userinfo_event");
    var userinfo = data.userinfo,
        friend_list = JSON.parse(data.friends),
        room_list = data.rooms;
    user = data.userinfo;
    var _uu = userinfo.username + ((userinfo.real_in_db) ? "(正式用户)" : "(匿名用户)");
    $(app_username).text(userinfo.username);
    $(app_usertype).text((userinfo.real_in_db) ? "(正式用户)" : "(匿名用户)");
    $(app_online_usernum).text(data.online_usernum);
    friend_list.forEach(ele => {
        add_listitem(ele, 'user');
    });
}

function add_listitem(_itemname, _listname) {
    if (_listname === 'user') {
        _list = $(app_userlist);
        if (_list.has('#user-' + _itemname).length === 0) {
            _list.append("<button class='chat-item' id='user-%d'>".replace("%d", _itemname) + _itemname + "</button>");
        }
    } else if (_listname === 'room') {
        _list = $(app_roomlist);
        if (_list.has('#room-' + _itemname).length === 0) {
            _list.append("<button class='chat-item' id='room-%d'>".replace("%d", _itemname) + _itemname + "</button>");
        }
    } else if (_listname === 'search') {
        _list = $(app_searchlist);
        if (_list.has('#search-' + _itemname).length === 0) {
            _list.append("<button class='chat-item' id='search-%d'>".replace("%d", _itemname) + _itemname + "</button>");
        }
    } else {
        console.log("add_listitem wrong :", _listname);
    }
}


function search_event(data) {
    console.log("search_event");
    match_list = JSON.parse(data['match_list']);
    $(app_searchlist).html(`<h3>搜索结果：</h3>`);
    match_list.forEach(ele => {
        // console.log(ele);
        add_listitem(ele, 'search');
    });
    $(app_leftlist).hide();
    $(app_searchlist).show();
}

function message_event(data) {
    console.log('message_event');
    // console.log(data);
    if (data['_type'] == 'user') {
        add_messgae(data['_from'], data['content'], data['_from'], data['_type']);
    } else if (data['_type'] == 'room') {
        if (data['_from'] != $(app_username).text())
            add_messgae(data['_from'], data['content'], data['_to'], data['_type']);
    }
}

function online_user_update_event(data) {
    console.log(parseInt($(app_online_usernum).text()));
    if (data._type == 'user_offline') {
        $(app_online_usernum).text((parseInt($(app_online_usernum).text()) - 1));
    } else if (data._type == 'user_online') {
        $(app_online_usernum).text((parseInt($(app_online_usernum).text()) + 1));
    }
}


function send_message(_from, _to, message) {
    // console.log(_from, "->", _to, " : ", message);
    socket.send(JSON.stringify({
        'action': "message",
        '_from': _from,
        '_to': _to,
        'content': message,
        '_type': chatobj_type,
    }));
    add_messgae(_from, message, _to, chatobj_type);
}

function add_messgae(_from, message, _pane, _type) {
    var msg = `<div class="app-message">
    <img src="../../static/hour84/img/tx.jpg">
    <div class="app-message-top-userinfo">%s</div>%m<hr/>
</div>`;
    console.log('add_messgae', _from, message, _type);
    
    var pane = '#message-pane-%t-%d'.replace('%t', _type).replace("%d", _pane);
    // console.log(panname);
    if ($(pane).length == 0) {
        $(app_right_panel_body).append(`<div class="message-pane" id="message-pane-%t-%d"></div>`.replace('%t', _type).replace("%d", _pane));
        $(pane).hide();
    }
    $(pane).append(msg.replace("%s", _from).replace("%m", message));
    // console.log($('#' + panname)[0].scrollHeight);
    var _height = $(pane)[0].scrollHeight;
    $(app_right_panel_body).scrollTop(_height);
}

function change_chatobj(_obj) {
    chatobj_name = _obj;
    $(app_chatobj_name).text(_obj);
    var _pane = '#message-pane-%t-%d'.replace('%t', chatobj_type).replace("%d", chatobj_name);
    if ($(_pane).length == 0) {
        $(app_right_panel_body).append(`<div class="message-pane" id="message-pane-%t-%d"></div>`.replace('%t', chatobj_type).replace("%d", _obj));
        $(_pane).hide();
    }
    $(app_message_pane).hide();
    $(_pane).show();
}

socket.onopen = function () {
    console.log('socket connect success');
}

socket.onclose = function () {

}

$(document).on('click', '.chat-item', function (e) {
    e = e.currentTarget;
    if (e.id.startsWith('search')) {
        add_listitem(e.innerText, 'user');
    } else if (e.id.startsWith('user')) {
        chatobj_type = 'user';
    } else if (e.id.startsWith('room')) {
        chatobj_type = 'room';
    } else {
        console.log('chat-item clicked... but something went wrong');
    }
    change_chatobj(e.innerText);
    console.log('name:' + chatobj_name);
    console.log('type:' + chatobj_type);
})

$(app_sendmsg_btn).click(function (e) {
    var msg = $(app_message_input).val();
    if (msg.length > 2 && chatobj_name != '') {
        $(app_message_input).val('');
        send_message($(app_username).text(), chatobj_name, msg);
    }
})

$(document).keydown(function (e) {
    // console.log(e.keyCode);
    if (e.ctrlKey && e.keyCode === 13) {
        has_login ? $(app_sendmsg_btn).click() : $(index_login_btn).click();
    }
});

$(index_login_btn).click(function () {
    socket.send(JSON.stringify({
        action: 'login',
        username: $(index_username).val(),
        password: $(index_password).val(),
        setting: $(index_setting).val(),
    }));
    $(index_info_message).text("");
});

$(app_search_btn).click(function () {
    var search_value = $(app_search_input).val();
    if (search_value.length > 0) {
        $(app_search_input).val("");
        socket.send(JSON.stringify({
            'action': 'search',
            'content': search_value,
        }));
    } else {
        alert('请输入内容再搜索');
    }
});

$(app_left_userbtn).click(function () {
    $(app_leftlist).hide();
    $(app_userlist).show();
});

$(app_left_roombtn).click(function () {
    $(app_leftlist).hide();
    $(app_roomlist).show();
});

$(app_add_room).click(function () {
    var _room = prompt("请输入你想创建或加入的房间名：");
    socket.send(JSON.stringify({
        'action': 'join_room',
        'roomname': _room
    }));
    add_listitem(_room, 'room');
})
