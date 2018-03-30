$(document).ready(function() {

    /*Use this notation because of container refreshing*/
    $(document).on("click", ".remove-button", function (evt) {
        evt.preventDefault();
        const songId = this.id;
        const url = window.location.pathname + "/delete/" + songId;
        console.log(url);
        $.ajax({
            type: "POST",
            url: url,
            dataType: "application/json"
        });
        $(this).parent().remove();
    });

    /*Refresh list every 5 seconds*/
    setInterval(function() {
        $("#song-list-container").load(location.href + " #song-list");
    }, 5000);
});