$(document).ready(function() {
    /**
     * View password on input
     */
    let passwordWrappers = $(".form_block.password_view");

    if (passwordWrappers) {
        passwordWrappers.each(function() {
            let ths = $(this);
            // Control button
            let controlBtn = ths.find("button.view_password");
            // Input for control hidden status
            let input = ths.find("input");

            controlBtn.on("click", () => {
                if (ths.hasClass("active") === false) {
                    controlBtn.addClass("active");
                    ths.addClass("active");
                    input.attr("type", "text");
                }
                else {
                    controlBtn.removeClass("active");
                    ths.removeClass("active");
                    input.attr("type", "password");
                }
            });
        });
    }

    /**
     * Base language select
     */
    let languageSelect = $(".set_language");

    if (languageSelect) {
        // Lang select wrapper
        let langWrapper   = languageSelect.find(".language_select");
        // Lang control
        let langHeader    = langWrapper.find(".select_head");
        // List with language link
        let langList      = langWrapper.find(".select_list");
        // All language links
        let langListLinks = langList.find(".link");

        langHeader.on("click", () => {
            if (langWrapper.hasClass("active") == false) {
                let listHeight = langListLinks.length * langListLinks.outerHeight(true);
                langWrapper.addClass("active");
                langList.css("height", `${listHeight}px`);
            }
            else {
                langWrapper.removeClass("active");
                langList.css("height", "0px");
            }
        });
        // Event for lang link
        langListLinks.on("click", (e) => {
            langHeader.find(".text").text(e.target.text);
            langWrapper.removeClass("active");
            langList.css("height", "0px");
            $.get( "/lang/" + (e.target.text).toLowerCase(), function( data ) {
                window.location.reload()
            });
        });
    }
});
