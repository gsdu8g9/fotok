
function API(sio_url) {
    this.socket = io.connect(sio_url, {
        transports: ['polling']
    });

    this.token = undefined;
    this.authHeader = undefined;
    this.user = undefined;

    this.getToken = function(success) {
        var api = this;
        $.get({
            url: '/api/user/token',
            success: function(data) {
                if (data.result != 'ok') {
                    console.log('getToken error: ' + data.message);
                    return;
                }

                api.token = data.token;
                api.authHeader = 'Basic ' + btoa('user:' + api.token);
                api.user = data.user;

                if (success != undefined)
                    success()
            },
            error: function(jqXHR, status) {
                console.log('getToken HTTP error: ' + status);
            }
        });
    };

    // `closed` indicates whether this API call requires authorization
    this.__doCall = function(name, request, success, method, closed) {
        var api = this;

        if (closed && api.token === undefined) {
            api.getToken(function() { api.__doCall(name, request, success, method); });
            return;
        }

        $.ajax({
            url: name,
            method: method,
            data: request,
            success: function(data) {
                if (data.result == 'error' && data.message == 'NotAuthorized' && closed) {
                    api.getToken(function() { api.__doCall(name, request, success, method); });
                    return
                }
                if (data.result != 'ok') {
                    console.log('error while calling ' + name + ': ' + data.message);
                    return;
                }

                success(data);
            },
            headers: {
                Authorization: api.authHeader
            }
        });
    };

    this.getRecentPhotos = function(success) {
        this.__doCall('/api/feed', {}, success, 'GET');
    };

    this.getPhotos = function(timestamp, success) {
        this.__doCall('/api/feed/' + Math.floor(timestamp), {}, success, 'GET');
    };

    this.getUserSubscriptions = function(user_id, success) {
        this.__doCall('/api/user/' + user_id + '/subscriptions', {}, success, 'GET');
    };

    this.addSubscription = function(user_id, success) {
        this.__doCall('/api/user/' + user_id + '/subscribe', {}, success, 'POST', true);
    };

    this.addComment = function(photo_id, comment, success) {
        this.__doCall('/api/photo/' + photo_id + '/comment', {comment: comment}, success, 'POST', true);
    };

    this.getPhotoRecentComments = function(photo_id, success) {
        this.__doCall('/api/photo/' + photo_id + '/comments', {}, success, 'GET');
    };

    this.getPhotoComments = function(photo_id, timestamp, success) {
        this.__doCall('/api/photo/' + photo_id + '/comments/' + Math.floor(timestamp), {}, success, 'GET');
    };

    this.getUserRecentPhotos = function(user_id, success) {
        this.__doCall('/api/user/' + user_id + '/photos', {}, success, 'GET');
    };

    this.getUserPhotos = function(user_id, timestamp, success) {
        this.__doCall('/api/user/' + user_id + '/photos/' + Math.floor(timestamp), {}, success, 'GET');
    };

    this.addPhoto = function(width, height, success) {
        this.__doCall('/api/photo/add', {width: width, height: height}, success, 'POST', true);
    };

    this.watch = function(channel, event, handler) {
        this.socket.emit('subscribe', {channel: channel});
        this.socket.on(event, handler);
    };

    this.unwatch = function(channel, event) {
        this.socket.emit('unsubscribe', {channel: channel});
        this.socket.off(event);
    };
}
