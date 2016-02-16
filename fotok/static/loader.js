
function wrapPhoto(photo, omitUser) {
    var date = moment.unix(photo.time);// - new Date().getTimezoneOffset()*60);

    var photoDiv = $('<div>', {class: 'panel panel-default'});
    photoDiv.append($('<div>', {class: 'panel-body'}).append(
        $('<a>', {href: '/photo/' + photo.id}).append(
        $('<img>', {
            src: photo.URL,
            width: photo.width, height: photo.height,
            class: 'img-responsive center-block'
        }))
    ));

    var userText = '';
    if (!omitUser)
        userText = '<span class="glyphicon glyphicon-user"></span>&nbsp;<a href="/user/' + photo.user.id + '" class="panel-title">' + photo.user.username + '</a>';

    photoDiv.append($('<div>', {class: 'panel-footer'}).html(
        userText + '&nbsp;<span class="small" title="' + date.format('LLL') + '">' + date.fromNow() + '</span>'
    ));

    return photoDiv;
}

function wrapComment(comment) {
    var date = moment.unix(comment.time);// - new Date().getTimezoneOffset()*60);

    var commentDiv = $('<div>', {class: 'panel panel-default'});
    commentDiv.append($('<div>', {class: 'panel-heading'}).html(
        '<span class="glyphicon glyphicon-user"></span>&nbsp;<a href="' + comment.author.id + '" class="panel-title">' + comment.author.username + '</a>' +
        '&nbsp;<span class="small" title="' + date.format('LLL') + '">' + date.fromNow() + '</span>'
    ));
    commentDiv.append($('<div>', {class: 'panel-body'}).text(comment.text));

    return commentDiv;
}

function Loader(loadmore, nomore) {
    this.lastId = 0;

    var now = new Date();
    this.lastTimestamp = now.getTime() / 1000;

    if (nomore !== undefined)
        nomore.hide();

    this.loadOne = function(object, handler) {
        this.lastTimestamp = Math.min(this.lastTimestamp, object.time);
        this.lastId = object.id;

        handler(object);
    }

    this.loadMore = function(objects, handler) {
        for (var i = 0; i < objects.length; i++) {
            if (this.lastId != 0 && objects[i].id >= this.lastId)
                continue;

            this.lastTimestamp = Math.min(this.lastTimestamp, objects[i].time);
            this.lastId = objects[i].id;

            handler(objects[i]);
        }
        if (objects.length == 0) {
            if (loadmore !== undefined)
                loadmore.hide();
            if (nomore !== undefined)
                nomore.show();
        }
    };
}
