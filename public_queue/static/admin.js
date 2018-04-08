function deleteSongById(dbId, songId) {
    const url = window.location.pathname + "/delete/" + songId;
    return $.ajax({
        type: "POST",
        url: url,
        data: {
            id: dbId
        },
        dataType: "application/json"
    });
}


function playNextSong(dbId, songId) {
    const url = window.location.pathname + "/play/" + songId;

    $.ajax({
        type: "POST",
        url: url,
        data: {
            id: dbId
        },
        dataType: "application/json"
    }).always(
        function (res) {
            console.log(res);
            const response = JSON.parse(res.responseText);
            console.log(response);
            updateRelevantElements();
            player.loadVideoById(response.response);
            player.playVideo();
        }
    );
}

function playSongById(dbId, songId) {
    const url = window.location.pathname + "/play/" + songId;

    $.ajax({
        type: "POST",
        url: url,
        data: {
            id: dbId
        },
        dataType: "application/json"
    }).always(
        function (res) {
            console.log(res);
            const response = JSON.parse(res.responseText);
            console.log(response);
            updateRelevantElements();
            player.loadVideoById(response.response);
            player.playVideo();
        }
    );
}


function getActiveButton() {
    return $(".list-group-item-custom > .active ~ .remove-button").first();
}


function updateRelevantElements() {
    setBgAndThumbnail();
    $("#song-list-container").load(location.href + " #song-list");
}


function setBgAndThumbnail() {
    try {
        /**Set background color of body based on the first thumbnails color*/
        const src = "/static/images/" + $("#song-duration-progress-bar").attr("song-id") + ".jpg";
        let image = new Image;
        image.src = src;
        console.log(image);
        console.log(src);
        const colorThief = new ColorThief();
        image.onload = function () {
            const dominantColor = colorThief.getColor(image);
            const bg = "linear-gradient(180deg,rgb("+dominantColor[0]+","+dominantColor[1]+","+dominantColor[2]+"), var(--dark) 40%)";
            $("body").css("background", bg);
            const thumbnail = $("#list-thumbnail");
            thumbnail.html($(image));
            thumbnail.css("background", "none");
            $(image).css("width", "100%");
            $(image).css("display", "inline-block");
            thumbnail.css("height", "200px");
        };
    } catch(error) {
        console.log(error);
    }
}

$(document).ready(function() {

    setBgAndThumbnail();

    $("#play-pause-button").on("click", function(evt) {
        evt.preventDefault();
        if($(this).html() === "play") {
            $(this).html("pause")
        } else {
            $(this).html("play")
        }
        $("#play-button").click();
    });

    /*Use this notation because of container refreshing*/
    $(document).on("click", ".remove-button", function (evt) {
        evt.preventDefault();
        const id = $(this).attr("db_id");
        const songId = $(this).attr("song_id");
        const elems = $(".remove-button");
        /*TODO*/
        if(this === elems.first().get(0)) {
            console.log("First removed");
            let second = elems.children().prevObject[1];
            console.log(second);
            const secondSongId = second.attr("song_id");
            console.log(secondSongId);
            player.loadVideoById(secondSongId);
            player.playVideo();
        }
        deleteSongById(id, songId);
        //playNextSong(id, songId);
        const dT = 500;
        $(this).parent().animate({height: 0, paddingTop: 0, paddingBottom: 0}, {duration: dT});
        setTimeout(() => $(this).parent().remove(), dT);
    });

    $("#previous-button").on("click", function (e) {
        e.preventDefault();
        const previousBtn = getActiveButton().prev();
        const id = previousBtn.attr("bd_id");
        const songId = previousBtn.attr("song_id");
        //playSongById(id, songId);
    });

    $("#play-button").on("click", function(e) {
       e.preventDefault();
       const elem = $(this);
       const anotherButton = $("#play-pause-button");
       if(elem.attr("is_play") === "false") {
           elem.find(".fa").removeClass();
           elem.find("i").addClass("fa fa-pause");
           elem.attr("is_play", "true");
           if(anotherButton.html() === "play") {
               anotherButton.html("pause");
           }
           player.playVideo();
       } else {
           elem.find(".fa").removeClass();
           elem.find("i").addClass("fa fa-play");
           elem.attr("is_play", "false");
           if(anotherButton.html() === "pause") {
               anotherButton.html("play");
           }
           player.pauseVideo();
       }
    });

    $("#skip-button").on("click", function(evt) {
        evt.preventDefault();
        const btn = getActiveButton();
        console.log(btn);
        const id = btn.attr("db_id");
        const songId = btn.attr("song_id");
        /*btn.parent().remove();
        deleteSongById(id, songId).always(
            function (res) {
                const response = JSON.parse(res.responseText);
                console.log(response);
                player.loadVideoById(response.response);
                player.playVideo();
            }
        );*/
        playNextSong(id, songId);

    });

    /*Refresh list every 5 seconds*/
    setInterval(function() {
        $("#song-list-container").load(location.href + " #song-list");
    }, 5000);

    let no_songs = $(".remove-button").length === 0;

    setInterval(function() {
        const elem = getActiveButton();
        if(elem.length !== 0 && no_songs) {
            const id = elem.first().attr("db_id");
            no_songs = false;
            player.loadVideoById(id);
            player.playVideo();
        } else if(elem.length === 0) {
            no_songs = true;
        }
    }, 5010);

    setInterval(function() {
    }, 1000);

});
