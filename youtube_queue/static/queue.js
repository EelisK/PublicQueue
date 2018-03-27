$(document).ready(function() {

    $("#que-appender").on("click", function() {
        const input = $("#id-input").val();
        console.log(input);
        console.log(window.location.pathname);
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {
                song_id: input
            },
            success: function(res) {
                console.log(res);
            },
            dataType: "application/json"
        });
    });

    let player;
    function onYouTubeIframeAPIReady() {
      player = new YT.Player('player', {
        height: '390',
        width: '640',
        videoId: 'M7lc1UVf-VE',
        events: {
          'onReady': onPlayerReady,
          'onStateChange': onPlayerStateChange
        }
      });
    }

    function onPlayerStateChange(event) {
        if (event.data === YT.PlayerState.PLAYING && !done) {
          setTimeout(stopVideo, 6000);
          done = true;
        }
      }
      function stopVideo() {
        player.stopVideo();
      }


    function queVideo(videoId) {
        let suggestedQuality = "144p";
        let startSeconds = 0;
        player.cueVideoById(videoId, startSeconds, suggestedQuality);
    }

});
