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
    const url = window.location.pathname + "/next/" + songId;

    $.ajax({
        type: "POST",
        url: url,
        data: {
            id: dbId
        },
        dataType: "application/json"
    }).always(
        function (res) {
            const response = JSON.parse(res.responseText);
            player.loadVideoById(response.response);
            player.playVideo();
            updateRelevantElements();
        }
    );
}

function playPreviousSong(dbId, songId) {
    const url = window.location.pathname + "/prev/" + songId;

    $.ajax({
        type: "POST",
        url: url,
        data: {
            id: dbId
        },
        dataType: "application/json"
    }).always(
        function (res) {
            const response = JSON.parse(res.responseText);
            player.loadVideoById(response.response);
            player.playVideo();
            updateRelevantElements();
        }
    );
}


function getActiveButton() {
    return $(".list-group-item-custom > .active ~ .remove-button").first();
}


function updateRelevantElements() {
    $("#song-list-container").load(location.href + " #song-list", function() {
        setBgAndThumbnail();
    });
}


function setBgAndThumbnail() {
    try {
        /**Set background color of body based on the first thumbnails color*/
        const id = getActiveButton().attr("song_id");
        const src = "/static/images/" + id + ".jpg";
        let image = new Image;
        image.src = src;
        const colorThief = new ColorThief();
        image.onload = function () {
            const dominantColor = colorThief.getColor(image);
            const rgb = "rgb("+dominantColor[0]+","+dominantColor[1]+","+dominantColor[2]+")";
            const bg = "linear-gradient("+rgb+","+rgb+", var(--dark) 100%)";
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
        if(id === elems.first().attr("db_id")) {
            let second = elems.children().prevObject[1];
            const secondSongId = second.attr("song_id");
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
        const previousBtn = getActiveButton();
        const id = previousBtn.attr("db_id");
        const songId = previousBtn.attr("song_id");
        const play = $("#play-pause-button");
        if(play.html() === "play") {
            play.click();
        }
        playPreviousSong(id, songId);
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
        const id = btn.attr("db_id");
        const songId = btn.attr("song_id");
        const play = $("#play-pause-button");
        if(play.html() === "play") {
            play.click();
        }
        playNextSong(id, songId);
    });

    /*Refresh list every 5 seconds*/
    setInterval(function() {
        $("#song-list-container").load(location.href + " #song-list");
    }, 50000);

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

});
