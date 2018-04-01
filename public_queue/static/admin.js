$(document).ready(function() {

    /*Use this notation because of container refreshing*/
    $(document).on("click", ".remove-button", function (evt) {
        evt.preventDefault();
        const id = $(this).attr("song_id");
        //not really needed but good for safety
        const songId = $(this).attr("db_id");
        const url = window.location.pathname + "/delete/" + songId;
        console.log("id: " + id + " songId " + songId);
        console.log(url);
        $.ajax({
            type: "POST",
            url: url,
            data: {
                id: id
            },
            dataType: "application/json"
        });
        const dT = 500;
        $(this).parent().animate({height: 0, paddingTop: 0, paddingBottom: 0}, {duration: dT});
        setTimeout(() => $(this).parent().remove(), dT);
    });

    $("#backward-button").on("click", function(e) {
       e.preventDefault();
    });
    $("#forward-button").on("click", function(e) {
       e.preventDefault();
    });
    $("#play-button").on("click", function(e) {
       e.preventDefault();
       const elem = $(this);
       if(elem.attr("is_play") === "false") {
           elem.find(".fa").removeClass();
           elem.find("i").addClass("fa fa-pause");
           elem.attr("is_play", "true");
           player.playVideo();
       } else {
           elem.find(".fa").removeClass();
           elem.find("i").addClass("fa fa-play");
           elem.attr("is_play", "false");
           player.pauseVideo();
       }
    });

    /*Refresh list every 5 seconds*/
    setInterval(function() {
        $("#song-list-container").load(location.href + " #song-list");
    }, 5000);

    let no_songs = $(".remove-button").length === 0;

    setInterval(function() {
        const elem = $(".remove-button");
        if(elem.length !== 0 && no_songs) {
            const id = elem.first().attr("db_id");
            no_songs = false;
            player.loadVideoById(id);
        } else if(elem.length === 0) {
            no_songs = true;
        }
    }, 5010);
});
