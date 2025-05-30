function open_tab(tab_name) {
    // Declare all variables
    var i, tab_content, tab_links;

    // Get all elements with class="tab_content" and ensure they are hidden
    tab_content = document.getElementsByClassName("tab_content");
    for (i = 0; i < tab_content.length; i++) {
        tab_content[i].style.display = "none";
    }

    // Get all elements with class="tab_links" and remove the class "active"
    tab_links = document.getElementsByClassName("tab_links");
    for (i = 0; i < tab_links.length; i++) {
        tab_links[i].className = tab_links[i].className.replace(" active", "");
    }

    // Show the current tab and mark "active"
    document.getElementById(tab_name).style.display = "block";
    document.getElementById(tab_name + "_tab").className += " active";
}
