$(document).ready(function () {
    $("#menu-toggle-button").on("click", function() {
        $("#sidebar").toggleClass("active");
    });
    /*Should create own cookie stuff...*/
    const cookieInterval = setInterval(function() {
        const cookieButton = $("#cookie-bar-button");
        if(cookieButton.length > 0)
            clearInterval(cookieInterval);
        cookieButton.css("border-radius", "10px");
        cookieButton.css("background", "var(--green)");
        cookieButton.css("color", "var(--white)");
        cookieButton.css("text-decoration", "none");
    }, 200);
    /*Clear the interval after 2 seconds if it
    * has not been cleared already*/
    setTimeout(function() {
        clearInterval(cookieInterval);
    }, 2000);
});