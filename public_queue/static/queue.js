$(document).ready(function() {

    $("#form-clear").on("click", function(evt) {
        evt.preventDefault();
        $("#search-key").val("");
    });

    $(document).on("click", ".song-button",function(evt) {
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
                console.log("SUCCESS");
                handleResponse(data);
            },
            error: function(data) {
                console.log("ERROR");
                handleResponse(data);
            },
            finally: function(data) {
                console.log("FINALLY");
                handleResponse(data);
            },
            dataType: "application/json"
        });
        const dT = 600;
        $("#search-results").animate({height: 0, paddingBottom: 0}, {duration: dT});
        setTimeout(() => {
            $("#search-results").empty();
            $("#song-list-container").load(location.href + " #song-list");
        }, dT);
    });

    $("#search-form").on("submit", function(e) {
        e.preventDefault();
        //Prepare request
        const key = $("#search-key");
        let query = encodeURIComponent(key.val());
        //key.val("");  // clear input after search
        console.log("Query:");
        console.log(query);
        $("#search-results").empty();
        const request = gapi.client.youtube.search.list({
            part: "snippet",
            type: "video",
            q: query,
            maxResults: 10, /*5 is default anyways*/
            safeSearch: "none",
            order: "relevance",
            videoCategoryId: 10, /*10 is music according to this source:
            https://gist.github.com/dgp/1b24bf2961521bd75d6c*/
        });
        //Make the request
        request.execute(function(response) {
            const searchResults = $("#search-results");
            searchResults.css("paddingBottom", "12px");
            let result = response.result;
            console.log(response);
            $.each(result.items, function(index, item) {
                console.log(item);
                const classes = "song-button list-group-item list-group-item-action";
                const elem = $("<button class='"+classes+"' type='button' id='" +
                    item["id"]["videoId"] + "'>" + item["snippet"]["title"] + "" + "</button>");
                searchResults.append(elem);
                //const thumbnail = item["snippet"]["thumbnails"]["default"]["url"];
                //console.log(thumbnail);
                //$("#"+item["id"]["videoId"]).css("background-image: url('" + thumbnail + "');");
            });
            searchResults.css("height", "100%");
        });
    });

    function handleResponse(data) {
        console.log(data);
    }

    /*refresh every 5 seconds*/
    setInterval(function() {
        $("#song-list-container").load(location.href + " #song-list");
    }, 5000);

});

function init() {
    gapi.client.setApiKey("AIzaSyDkkNJHGrVQo6D95PeAfhLrf0lTqGKWmIE");
    gapi.client.load("youtube", "v3", function() {
        console.log("api is ready");
        $("#search-key").prop("disabled", false);
    });
}
