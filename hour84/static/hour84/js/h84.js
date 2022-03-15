// var HOST = '120.24.175.31:8000';
// var HOST = '127.0.0.1:8000';
var HOST = window.location.host;

var socket = new WebSocket('ws://' + HOST + '/wss/chat/');

var pages = '.whole-page';

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
    app_message_input = 'textarea',
    app_right_panel_body = ".app-right-pane-body",
    app_add_room = '.app-roomlist > h3',
    app_add_item = '.chat-item > .add-item',
    app_delete_item = '.chat-item > .delete-item',
    app_chat_item = '.chat-item',
    app_usr_avater = '.app-left-pane-top-userinfo > img';

var setting_page = '.setting',
    setting_profile_pic = '.profile .pic',
    setting_submit_btn = '#submit-btn';

var chatobj_name = '',
    chatobj_type = 'user',
    strangers = [],
    friends = [],
    rooms = [],
    has_init = [],
    user_username = '',
    has_login = false;

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
    } else if (data.action == 'online_user_update') {
        online_user_update_event(data);
    } else if (data.action == 'update_friendlist') {
        update_friendlist_event(data);
    } else if (data.action == 'load_message') {
        load_message_event(data);
    } else {
        console.log('router wrong....');
        // console.log(data);
    }
}

function timenow() {
    var d = new Date();
    return '%Y-%m-%d %H:%M:%S'.replace('%Y', d.getFullYear()).replace('%m', (d.getMonth() + 1)).replace('%d', d.getDate()).replace('%H', d.getHours()).replace('%M', d.getMinutes()).replace('%S', d.getSeconds());
}


function login_success() {
    has_login = true;
    user_username = $(index_username).val();
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
    $(app_username).text(userinfo.username);
    $(app_usertype).text((userinfo.real_in_db) ? "(正式用户)" : "(匿名用户)");
    $(app_online_usernum).text(data.online_usernum);
    friend_list.forEach(ele => {
        add_listitem(ele, 'user');
        friends.push(ele);
    });
}

function add_listitem(_itemname, _listname) {
    console.log('add_listitem:', _listname, ' ', _itemname);
    if (_listname === 'user') {
        _list = $(app_userlist);
        if (_list.has('#user-' + _itemname).length === 0) {
            _node = `<div class="chat-item" id="user-%d">
                        <a class="itemname">%d</a>
                        <a class="add-item"> + </a>
                        <a class="delete-item"> - </a>
                    </div>`.replace('%d', _itemname).replace('%d', _itemname);
            _list.append(_node);
        }
    } else if (_listname === 'room') {
        _list = $(app_roomlist);
        if (_list.has('#room-' + _itemname).length === 0) {
            _node = `<div class="chat-item" id="room-%d">
                        <a class="itemname">%d</a>
                        <a class="delete-item"> - </a>
                    </div>`.replace('%d', _itemname).replace('%d', _itemname);
            _list.append(_node);
        }
    } else if (_listname === 'search') {
        _list = $(app_searchlist);
        if (_list.has('#search-' + _itemname).length === 0) {
            _node = `<div class="chat-item" id="search-%d">
                        <a class="itemname">%d</a>
                        <a class="delete-item"> - </a>
                    </div>`.replace('%d', _itemname).replace('%d', _itemname);
            _list.append(_node);
        }
    } else {
        console.log("add_listitem wrong :", _listname);
    }
}


function search_event(data) {
    console.log("search_event");
    match_list = JSON.parse(data['match_list']);
    $(app_searchlist).html(`<h3>搜索结果：</h3>`);
    if (match_list.length == 0) {
        $(app_searchlist).append(`空空如也`);
    } else {
        match_list.forEach(ele => {
            // console.log(ele);
            add_listitem(ele, 'search');
        });
    }
    $(app_leftlist).hide();
    $(app_searchlist).show();
}

function message_event(data) {
    console.log('message_event');
    if (data['_type'] == 'user') {
        add_listitem(data['_from'], 'user');
        add_messgae(data['_from'], data['_from'], data['content'], data['_type'], data['_time']);
    } else if (data['_type'] == 'room' && data['_from'] != $(app_username).text()) {
        add_messgae(data['_from'], data['_to'], data['content'], data['_type'], data['_time']);
    }
}

function online_user_update_event(data) {
    if (data._type == 'user_offline') {
        $(app_online_usernum).text((parseInt($(app_online_usernum).text()) - 1));
    } else if (data._type == 'user_online') {
        $(app_online_usernum).text((parseInt($(app_online_usernum).text()) + 1));
    }
}

function update_friendlist_event(data) {

}


function load_message_event(data) {
    var _messages = data._messages;
    var _len = _messages.length;
    var FLAG = (data['_type'] === 'user');
    var __roomname;
    if (!FLAG && _len > 0) {
        __roomname = _messages[0][1];
    }
    for (var i = 0; i < _len; i++) {
        var d = _messages[i];
        if (FLAG) { // user messgae
            if (d[0] == user_username) {
                add_messgae(d[0], d[1], d[2], 'user', d[3]);
            } else {
                add_messgae(d[0], d[0], d[2], 'user', d[3]);
            }
        } else { // room message
            add_messgae(d[0], __roomname, d[2], 'room', d[3]);
        }
    }
}

function send_message(_from, _to, message, _type, _time) {
    socket.send(JSON.stringify({
        'action': "message",
        '_type': _type,
        '_from': _from,
        '_to': _to,
        'content': message,
        '_time': _time,
    }));
    add_messgae(_from, _to, message, chatobj_type, _time);
}

function add_messgae(_sender, _pane, message, _type, _time = '') {
    var msg = `<div class="app-message">
    <img src="../../static/hour84/img/tx.jpg">
    <div class="app-message-top-userinfo">%s<a class='message-time'>%t</a></div>%m<hr/>
</div>`;
    console.log('message: from ' + _sender + '\tadd to ' + _pane + '\t:' + message)

    var pane = '#message-pane-%t-%d'.replace('%t', _type).replace("%d", _pane);
    if ($(pane).length == 0) {
        $(app_right_panel_body).append(`<div class="message-pane" id="message-pane-%t-%d"></div>`.replace('%t', _type).replace("%d", _pane));
        $(pane).hide();
    }

    $(pane).append(msg.replace("%s", _sender).replace("%m", message).replace('%t', _time));
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

function load_message(_from, _to, _type) {
    socket.send(JSON.stringify({
        'action': 'load_message',
        '_type': _type,
        '_from': _from,
        '_to': _to,

    }));
}

socket.onopen = function() {
    console.log('socket connect success');
}

socket.onclose = function() {

}

$(document).on('click', app_chat_item, function(e) {
    console.log('chat item clicked...');
    console.log(e);
    e = e.currentTarget;
    _name = $(e).find('.itemname').text();
    if (e.id.startsWith('search')) {
        add_listitem(_name, 'user');
    } else if (e.id.startsWith('user')) {
        chatobj_type = 'user';
    } else if (e.id.startsWith('room')) {
        chatobj_type = 'room';
    } else {
        console.log('chat-item clicked... but something went wrong');
    }
    $(app_chat_item).removeClass('item-active');
    $(e).addClass('item-active');
    change_chatobj(_name);
    if (has_init.indexOf(_name) == -1) {
        load_message(user_username, _name, chatobj_type);
        has_init.push(_name);
    }
})

$(document).on('click', app_add_item, function(e) {
    console.log('app_add_item clicked');
    var _node = $(e.currentTarget).parent('.chat-item');
    var _name = _node.find('.itemname').text();
    if (!friends.includes(_name)) {
        socket.send(JSON.stringify({
            'action': 'update_friendlist',
            '_type': 'add',
            'friend_name': _name,
        }))
    }
    return false;
})

$(document).on('click', app_delete_item, function(e) {
    console.log('app_delete_item clicked');
    var _node = $(e.currentTarget).parent('.chat-item');
    var _name = _node.find('.itemname').text();
    if (!friends.includes(_name)) {
        socket.send(JSON.stringify({
            'action': 'update_friendlist',
            '_type': 'remove',
            'friend_name': _name,
        }))
    }
    return false;
})

$(app_sendmsg_btn).click(function(e) {
    var msg = $(app_message_input).val();
    if (msg.length > 2 && chatobj_name != '') {
        $(app_message_input).val('');
        send_message(user_username, chatobj_name, msg, chatobj_type, timenow());
    }
})

$(document).keydown(function(e) {
    // console.log(e.keyCode);
    if (e.ctrlKey && e.keyCode === 13) {
        has_login ? $(app_sendmsg_btn).click() : $(index_login_btn).click();
    }
});

$(index_login_btn).click(function() {
    socket.send(JSON.stringify({
        action: 'login',
        username: $(index_username).val(),
        password: $(index_password).val(),
        setting: $(index_setting).val(),
    }));
    $(index_info_message).text("");
});

$(app_search_btn).click(function() {
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

$(app_left_userbtn).click(function() {
    $(app_leftlist).hide();
    $(app_userlist).show();
});

$(app_left_roombtn).click(function() {
    $(app_leftlist).hide();
    $(app_roomlist).show();
});

$(app_add_room).click(function() {
    var _room = prompt("请输入你想创建或加入的房间名：");
    socket.send(JSON.stringify({
        'action': 'join_room',
        'roomname': _room
    }));
    add_listitem(_room, 'room');
})

$(app_search_input).keydown(function(e) {
    if (e.keyCode === 13) {
        $(app_search_btn).click();
    }
});

$(app_usr_avater).click(function(e) {
    console.log(10086);
    $(setting_page).toggleClass('hide');
})

$(setting_page).click(function() {
    console.log("setting_page clicked...");
    $(setting_page).toggleClass('hide');
})



function getContextPath() {
    var pathName = window.document.location.pathname;
    var projectName = pathName.substring(0, pathName.substr(1).indexOf(
        '/') + 1);
    return projectName;
}

$(setting_submit_btn).click(function() {
    console.log('setting_submit_btn clicked...')
    _pic = $(setting_profile_pic)[0].files[0];
    var _data = new FormData();
    _data.append('pic', _pic);
    _data.append('username', user_username);
    var base_url = getContextPath();
    $.ajax({
        url: base_url + '/upload',
        type: 'post',
        data: _data,
        processData: false,
        contentType: false,
        success: function(res) {
            console.log(res);
        },
        error: function(res) {

        }
    })
})