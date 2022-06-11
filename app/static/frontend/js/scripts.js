$(document).ready(function() {
    /**
     * Base variable
     */
    let pageLoader       = $(".page_loader");

    /**
     * Base language select
     */
    let languageSelect = $(".user_language");

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
            e.preventDefault();
            langHeader.find(".text").text(e.target.text);
            langWrapper.removeClass("active");
            langList.css("height", "0px");
            $.get( "/lang/" + (e.target.text).toLowerCase(), function( data ) {
                window.location.reload()
            });
        });
    }

    /**
     * Base push message
     */
    let pushMessage = $(".push_message");

    if (pushMessage) {
        pushMessage.each(function() {
            let ths = $(this);
            // Auto close
            let timerClear = false;
            // Timer status bar
            let timerStatusBar = ths.find(".time_bar")
            // Time to hide - in seconds
            let lifeTime = 20,
                maxTime = 20;
            // Timer Identification
            let timerID;
            // Close button
            let closeBtn = ths.find("button.close");

            // Close timer functions
            // Timer
            let timer = (stop) => {
                if (stop == true) {
                    clearTimeout(timerID);
                }
                else {
                    timerID = setTimeout(function UpdateTime() {
                        lifeTime -= 0.1;
                        // Time different in percent for timer status bar
                        let timeDiff = 100 - (((maxTime - lifeTime) / ((maxTime + lifeTime))) * 100);

                        timerStatusBar.css("width", `${timeDiff}%`);

                        if (lifeTime < 0) {
                            RemoveThisPush();
                        }
                        else {
                            timer(false);
                        }
                    }, 100);
                }
            }
            // Stop timer
            function stopTimer() {
                timer(true);
            }

            // Remove this push message
            function RemoveThisPush() {
                timerClear = true;

                ths.addClass("removed");

                setTimeout(() => {
                    ths.remove();
                }, 500);
            }

            // Run close timer
            timer(false);

            ths.on("mouseenter", () => {
                stopTimer();
            });
            ths.on("mouseleave", () => {
                if (timerClear == false) {
                    timer(false);
                }
            });
            closeBtn.on("click", () => {
                clearTimeout(timerID);
                RemoveThisPush();
            });
        });
    }

    /**
     * Smooth scroll
     */
    let allSmoothLinks = $(".smooth_link");

    if (allSmoothLinks) {
        let scrollStatus = false;

        // Smooth scroll function
        function SmoothScroll(offset, activeOffset) {
            // Active scrolling
            if (scrollStatus == false) {
                // Set active scroll status
                scrollStatus = true;

                // Data from scrolling
                let scrollTime   = 1500;
                let scrollOffset = offset ? offset : 0;
                let actualOffset = activeOffset ? activeOffset : 0;

                // Update scroll time
                scrollTime = (actualOffset < scrollOffset) ? scrollOffset - actualOffset : actualOffset - scrollOffset;
                scrollTime = (scrollTime > 2000) ? 2000 : scrollTime;
                scrollTime = (scrollTime < 500) ? 500 : scrollTime;

                $("html").animate({scrollTop: (scrollOffset == 0 ? scrollOffset : scrollOffset + 1)}, scrollTime);

                // When scroll completed - remove scroll status
                setTimeout(() => {
                    // Scroll on zero y offset when target offset == 0
                    if (scrollOffset == 0) {
                        $("html").animate({scrollTop: 0}, 0);
                    }

                    // Update scroll status
                    scrollStatus = false;
                }, (scrollTime + 1));
            }
        }

        allSmoothLinks.each(function() {
            // This
            let ths = $(this);

            ths.on("click", (e) => {
                // Remove base events
                e.preventDefault();

                // Link target
                let target = ths.attr("data-target");
                
                
                // User top offset
                let userTopOffset = window.pageYOffset;
                if($(`.${target}`).length > 0){
                    let targetTopOffset = $(`.${target}`).position().top;

                    SmoothScroll(targetTopOffset, userTopOffset);
                }else{
                    window.location.href="/";
                }
                
            });
        });
    }

    /**
     * Header control
     */
    let headerWrapper = $("#header");
    
    if (headerWrapper) {
        headerWrapper.each(function() {
            let ths = $(this);
            // The goal near which we change the status
            let targetOffset   = 0;
            // Header content
            let headerContent  = headerWrapper.find(".header_wrapper .content");
            // Mobile control
            let mobileControl  = headerContent.find("button.mobile_control");
            // All smooth link for control active status
            let allLinks       = headerContent.find(".navigation_wrapper .navigation .link");
            // Links target position
            let newTargetArray = [];
            allLinks.each(function() {
                if($(`.${$(this).attr("data-target")}`).length > 0){
                    let targetPosition = $(`.${$(this).attr("data-target")}`).position().top;
                
                
                    newTargetArray.push(targetPosition);
                }
               
            });

            // Set/Remove fixed status on header
            function UpdateFixedStatus(target, actualOffset) {
                let targetTopOffset = target ? target : 0;
                let actualTopOffset = actualOffset ? actualOffset : 0;


                if (actualTopOffset >= targetTopOffset) {
                    headerWrapper.addClass("fixed");
                }
                else {
                    headerWrapper.removeClass("fixed");
                }
            }
            // First run function
            UpdateFixedStatus(targetOffset, window.pageYOffset);

            // Check active target and actual offset y position
            function CheckActualOffset(actualPosition, targetsPosition) {
                let position = actualPosition ? actualPosition : null;
                let targets  = targetsPosition ? targetsPosition : null;

                if (position && targets) {
                    targets.forEach((target, index) => {
                        if ((actualPosition >= target)) {
                            allLinks.removeClass("active");
                            allLinks.eq(index).addClass("active");
                        }
                        else if (actualPosition < targets[0]) {
                            allLinks.removeClass("active");
                        }
                    });
                }
            }
            // First run function
            CheckActualOffset(window.pageYOffset, newTargetArray);

            // Scroll event
            $(window).on("scroll", (e) => {
                UpdateFixedStatus(targetOffset, window.pageYOffset);
                CheckActualOffset(window.pageYOffset, newTargetArray);
            });
            // Mobile button event
            mobileControl.on("click", () => {
                if (headerContent.hasClass("active") == false) {
                    headerContent.addClass(("active"));
                }
                else {
                    headerContent.removeClass(("active"));
                }
            });
            // Menu link event
            allLinks.on("click", () => {
                if (headerContent.hasClass("active") == true) {
                    headerContent.removeClass(("active"));
                }
            });
        });
    }

    // Marketing Plans Slider
    let presentSlider = $(".main_present .present_slider");

    if (presentSlider) {
        presentSlider.each(function() {
            let ths = $(this);
            // Slides wrapper
            let slidesWrapper    = ths.find(".slides_wrapper");
            let allSlides        = slidesWrapper.find(".slide_block");
            let slidesLength     = allSlides.length;
            // Active slide
            let activeSlide      = slidesWrapper.find(".slide_block.active").index();
            // Slider control
            let controlWrapper   = ths.find(".slider_control");
            // Dots control
            let dotsWrapper      = controlWrapper.find(".control_dot");
            let allDots          = dotsWrapper.find(".dot");
            // Buttons for control
            let prevBtn          = controlWrapper.find(".control_buttons button.prev"),
                nextBtn          = controlWrapper.find(".control_buttons button.next");

            // Function to switch slides
            function SlidesSwitch(dir) {
                if (dir > 0) {
                    activeSlide++;
                }
                else {
                    activeSlide--;
                }

                if (activeSlide < 0) {
                    activeSlide = slidesLength - 1;
                }
                else if (activeSlide >= slidesLength) {
                    activeSlide = 0;
                }

                // Remove active class on slide and dot
                dotsWrapper.find(".dot.active").removeClass("active");
                slidesWrapper.find(".slide_block.active").removeClass("active");
                // Set active class on slide and dot
                allDots.eq(activeSlide).addClass("active");
                allSlides.eq(activeSlide).addClass("active");
            }

            allDots.each(function() {
                $(this).on("click", () => {
                    // Remove active class on slide and dot
                    dotsWrapper.find(".dot.active").removeClass("active");
                    slidesWrapper.find(".slide_block.active").removeClass("active");
                    // Set active class on slide and dot
                    allDots.eq($(this).index()).addClass("active");
                    allSlides.eq($(this).index()).addClass("active");
                });
            });

            prevBtn.on("click", () => {
                SlidesSwitch(-1);
            });
            nextBtn.on("click", () => {
                SlidesSwitch(1);
            });
        });
    }
    // Marketing Plans Slider end

    // Marketing Plans Slider
    let marketingPlans = $(".main_marketing_plans .plans_slider");

    if (marketingPlans) {
        marketingPlans.each(function() {
            let ths = $(this);
            // Slides wrapper
            let slidesWrapper    = ths.find(".slides_wrapper");
            let allSlides        = slidesWrapper.find(".slide");
            let slidesLength     = allSlides.length;
            // Active slide
            let activeSlide      = slidesWrapper.find(".slide.active").index();
            // Slider control
            let controlWrapper   = ths.find(".slider_control");
            // Buttons for control
            let prevBtn          = controlWrapper.find(".control_buttons button.prev"),
                nextBtn          = controlWrapper.find(".control_buttons button.next");

            // Function to switch slides
            function SlidesSwitch(dir) {
                if (dir > 0) {
                    activeSlide++;
                }
                else {
                    activeSlide--;
                }

                if (activeSlide < 0) {
                    activeSlide = slidesLength - 1;
                }
                else if (activeSlide >= slidesLength) {
                    activeSlide = 0;
                }

                slidesWrapper.find(".slide.active").removeClass("active");
                allSlides.eq(activeSlide).addClass("active");
            }

            prevBtn.on("click", () => {
                SlidesSwitch(-1);
            });
            nextBtn.on("click", () => {
                SlidesSwitch(1);
            });
        });
    }
    // Marketing Plans Slider end

    // Marketing Plans Slider
    let ourTeams = $(".main_our_team");

    if (ourTeams) {
        ourTeams.each(function() {
            let ths = $(this);
            // Slides wrapper
            let membersWrapper     = ths.find(".team_wrapper");
            let allMembers         = membersWrapper.find(".member_wrapper");

            allMembers.each(function() {
                let ths = $(this);

                ths.on("click", () => {
                    if (ths.hasClass("active") == false) {
                        allMembers.removeClass("active");
                        ths.addClass("active");
                    }
                });
            });
        });
    }
    // Marketing Plans Slider end

    // Remove page loader
    setTimeout(function() {
        pageLoader.remove();
    }, 250);
});

