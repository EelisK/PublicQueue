$(document).ready(function() {


    /*const player = window.YT.Player("music_player", {
        width: "768",
        height: "432",
        videoId: "4LfJnj66HVQ",
        events: {
            "onReady": function(event) {
                console.log("Ready");
                console.log(event);
            },
            "onStateChange": function(event) {
                console.log("StateChange");
                console.log(event);
            }
        }
    });

    function queVideo(videoId) {
        let suggestedQuality = "144p";
        let startSeconds = 0;
        player.cueVideoById(videoId, startSeconds, suggestedQuality);
    }*/

    $("#search-form").on("submit", function(e) {
        e.preventDefault();
        //Prepare request
        const key = $("#search-key");
        let query = encodeURIComponent(key.val());
        key.val("");  // clear input after search
        console.log("Query:");
        console.log(query);
        let request = gapi.client.youtube.search.list({
            part: "snippet",
            type: "video",
            q: query,
            maxResults: 5, /*5 is default anyways*/
            order: "relevance",
            videoCategoryId: 10, /*10 is music according to this resource:
            https://gist.github.com/dgp/1b24bf2961521bd75d6c*/
        });
        //Make the request
        request.execute(function(response) {
            let result = response.result;
            console.log(response);
            $("#search-results").empty();
            $.each(result.items, function(index, item) {
                console.log(item);
                const classes = "song-button list-group-item list-group-item-action";
                $("#search-results").append("<button class='"+classes+"' type='button' id='" +
                    item["id"]["videoId"] + "'>" + item["snippet"]["title"] + "" + "</button>");
                //const thumbnail = item["snippet"]["thumbnails"]["default"]["url"];
                //console.log(thumbnail);
                //$("#"+item["id"]["videoId"]).css("background-image: url('" + thumbnail + "');");
            });
            $(".song-button").on("click", function(evt) {
                evt.preventDefault();
                const songId = this.id;
                const songName = this.innerHTML;
                $.ajax({
                    type: "POST",
                    url: window.location.pathname,
                    data: {
                        song_id: songId,
                        song_name: songName
                    },
                    success: function(data) {
                        handleResponse(data);
                    },
                    error: function(data) {
                        handleResponse(data);
                    },
                    dataType: "application/json"
                });
                $("#song-list-container").load(location.href + " #song-list");
                $("#search-results").empty();
            });
        });
    });

    function handleResponse(data) {
        console.log(data);
    }

    setInterval(function() {
        $("#song-list-container").load(location.href + " #song-list");
    }, 5000/*refresh every 5 seconds*/);

    /*$("#que-appender").on("click", function() {
        const input = $("#id-input").val();
        queVideo(input);
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {
                song_id: input
            },
            success: function(data) {
                handleResponse(data);
            },
            error: function(data) {
                handleResponse(data);
            },
            dataType: "application/json"
        });
    });*/

});

function init() {
    gapi.client.setApiKey("AIzaSyDkkNJHGrVQo6D95PeAfhLrf0lTqGKWmIE");
    gapi.client.load("youtube", "v3", function() {
        console.log("api is ready");
        $("#search-key").prop("disabled", false);
    });
}
