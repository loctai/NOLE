$(document).ready(function() {
    let h = window.location.href , g = h.split("#") , f = $("a"); f.length > 0 && f.each(function() { h === this.href && "" !== g[1] && ($(this).closest("li").addClass("active").parent().closest("ul").addClass("show").closest("li").addClass("active"),$(this).closest("a").addClass("active show") ) });
    /**
     * Base variable
    */
   $(document).on("input", ".numeric", function(event) {
    $(this).val($(this).val().replace(/[^0-9\.]/g,''));
    if ((event.which != 46 || $(this).val().indexOf('.') != -1) && (event.which < 48 || event.which > 57)) {
        event.preventDefault();
    }
});
    let lockModalWrapper = $(".lock_modal_bg");
    let allModalWindow   = $(".modal_condition");
    let pageLoader       = $(".page_loader");

    /**
     * Event for lock modal backgorund
    */
    if (lockModalWrapper) {
        lockModalWrapper.on("click", () => {
            // Remove active class from all modal windows & lock modal bg
            allModalWindow.removeClass("active");
            lockModalWrapper.removeClass("active");
        });
    }

    /**
     * Header control
     */
    let headerWrapper = $("#header");

    if (headerWrapper) {
        // Header navigation
        let navigation       = headerWrapper.find(".navigation");
        // Mobile control button
        let controlBtn       = navigation.find(".mobile_control");
        // Mobile menu button
        let mobMenuBtn       = navigation.find(".mobile_menu_control");
        let mobMenuTarget    = navigation.find(".link_list");
        // Mobile account button
        let mobAccountBtn    = navigation.find(".mobile_account_control");
        let mobAccountTarget = headerWrapper.find(".user_data");

        controlBtn.on("click", () => {
            if (headerWrapper.hasClass("active") == false) {
                headerWrapper.addClass("active");
            }
            else {
                headerWrapper.removeClass("active");
            }
        });

        mobMenuBtn.on("click", () => {
            if (mobMenuBtn.hasClass("active") == false) {
                if (mobAccountBtn.hasClass("active") == true) {
                    mobAccountBtn.removeClass("active");
                    mobAccountTarget.removeClass("active");
                }

                mobMenuBtn.addClass("active");
                mobMenuTarget.addClass("active");
            }
            else {
                mobMenuBtn.removeClass("active");
                mobMenuTarget.removeClass("active");
            }
        });
        mobAccountBtn.on("click", () => {
            if (mobAccountBtn.hasClass("active") == false) {
                if (mobMenuBtn.hasClass("active") == true) {
                    mobMenuBtn.removeClass("active");
                    mobMenuTarget.removeClass("active");
                }
                mobAccountBtn.addClass("active");
                mobAccountTarget.addClass("active");
            }
            else {
                mobAccountBtn.removeClass("active");
                mobAccountTarget.removeClass("active");
            }
        });
    }

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
        /* Event for lang link */
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
     * Base tables pagination
    */
    let allPaginationTable = $(".table_pagination");

    if (allPaginationTable) {
        allPaginationTable.each(function() {
            // This
            let ths = $(this);
            // Visible elements on page
            let elementsOnPage = 8;
            // Dots count
            let dotsCount = 0;
            // Table
            let thsTable          = ths.find(".base_table")
            // All table row
            let dealsWrapper      = thsTable.find(".tbody");
            let allDeals          = dealsWrapper.find("tr");
            let dealsLength       = allDeals.length;
            // Pagination wrapper
            let paginationWrapper = ths.find(".table_control");
            // Pagination dots wrapper
            let dotsWrapper       = paginationWrapper.find(".dots_wrapper");
            // Pagination control buttons
            let prevBtn           = paginationWrapper.find("button.prev"),
                nextBtn           = paginationWrapper.find("button.next");

            // Создание Data атрибутов для всех элементов
            function CreateDataNum(target) {
                if (target) {
                    for (i = 0; i <= target.length; i++) {
                        target.eq(i).attr('data-num', (i + 1));
                    }
                }
            }
            // Function for created pagination
            function CreatePagination(wrapper, elementsCount) {
                if (wrapper) {
                    let count = (elementsCount) ? elementsCount : 0;
                    let btnCount = Math.ceil(count / elementsOnPage);

                    for (i = 1; i <= btnCount; i++) {
                        if (i == 1) {
                            wrapper.append(`<div class="dot active" data-page="${i}">${i}</div>`);
                        }
                        else {
                            wrapper.append(`<div class="dot" data-page="${i}">${i}</div>`);
                        }

                        dotsCount++;
                    }
                }
            }
            // Сокрытие элементов и вывод по активной подстранице
            function HideDealElements(page) {
                let activePage = (page) ? page : dotsWrapper.find('.dot.active').attr('data-page');

                allDeals.addClass('hide');

                for (i = (activePage * elementsOnPage); i > ((activePage * elementsOnPage) - elementsOnPage); i--) {
                    dealsWrapper.find(`[data-num="${i}"]`).removeClass('hide');
                }
            }

            // Write data attr on deal wrapper
            CreateDataNum(allDeals);
            // Create pagination on page
            CreatePagination(dotsWrapper, dealsLength);
            // Hide deals on page
            HideDealElements();

            // All dots
            let allDots = dotsWrapper.find(".dot");

            // Function for hide dots
            function HideDotsButton(page) {
                let activePage = (page) ? page : Number(dotsWrapper.find('.dot.active').attr('data-page'));

                allDots.addClass("hide");
                allDots.eq(activePage - 1).removeClass("hide");
                // Condition for after & before dots
                allDots.eq(activePage).removeClass("hide");
                allDots.eq(activePage + 1).removeClass("hide");
                // For first and second dots
                if (activePage == 1) {
                    allDots.eq(activePage + 3).removeClass("hide");
                    allDots.eq(activePage + 2).removeClass("hide");
                }
                else if (activePage == 2) {
                    allDots.eq(activePage + 2).removeClass("hide");
                    allDots.eq(activePage - 2).removeClass("hide");
                }
                else {
                    allDots.eq(activePage - 2).removeClass("hide");
                    allDots.eq(activePage - 3).removeClass("hide");
                }
            }
            // Run first start function
            HideDotsButton();

            allDots.each(function() {
                let thsDot = $(this);

                thsDot.on("click", () => {
                    // Data attr
                    let pageNum = Number(thsDot.attr("data-page"));

                    allDots.removeClass("active");
                    thsDot.addClass("active");

                    HideDotsButton(pageNum);
                    HideDealElements(pageNum);
                });
            });

            function SwipeWithButton(page) {
                let activePage = (page) ? page : Number(dotsWrapper.find('.dot.active').attr('data-page'));

                if (activePage > dotsCount) {
                    activePage = dotsCount;
                }
                else if (activePage <= 0) {
                    activePage = 1;
                }

                allDots.removeClass("active");
                allDots.eq(activePage - 1).addClass("active");

                HideDotsButton(activePage);
                HideDealElements(activePage);
            }

            prevBtn.on("click", () => {
                let activePage = Number(dotsWrapper.find('.dot.active').attr('data-page'));

                SwipeWithButton(activePage - 1);
            });
            nextBtn.on("click", () => {
                let activePage = Number(dotsWrapper.find('.dot.active').attr('data-page'));

                SwipeWithButton(activePage + 1);
            });
        });
    }

    /**
     * Base tabs window
    */
    let allTabsWindows = $(".base_tabs_window");

    if (allTabsWindows) {
        allTabsWindows.each(function() {
            // This
            let ths = $(this);
            // Tabs window control
            let tabsHeader  = ths.find(".tabs_header");
            let tabButtons  = tabsHeader.find(".btn");
            // Tabs window content
            let tabContents = ths.find(".tabs_content");
            // All content block
            let allContents = ths.find(".tabs_content .content_wrapper");

            // Create tabs line for header buttons
            tabsHeader.append(`<span class="tabs_line"></span>`);
            // Tabs header line
            let tabsLine    = tabsHeader.find(".tabs_line");
            // Update style for tabs line on the first tabs button
            tabsLine.css("width", `${tabButtons.eq(0).outerWidth()}px`);
            tabsLine.css("left", `${tabButtons.eq(0).position().left}px`);

            tabButtons.each(function() {
                let thsTab = $(this);
                // Target window class
                let targetClass = thsTab.attr("data-target");

                thsTab.on("click", () => {
                    if ((thsTab.hasClass("active") == false) && (targetClass)) {
                        tabsLine.css("width", `${thsTab.outerWidth()}px`);
                        tabsLine.css("left", `${thsTab.position().left}px`);

                        // Set & remove active on current & old tab button
                        tabButtons.removeClass("active");
                        thsTab.addClass("active");
                        // Set & remove active on current & old window
                        allContents.removeClass("active");
                        tabContents.find(`.${targetClass}`).addClass("active");
                    }
                });
            });
        });
    }

    /**
     * Base beautiful select list
    */
    let allBeautifulSelectLists = $(".beautiful_select_list");

    if (allBeautifulSelectLists) {
        // Number of list
        let listID = 0;

        allBeautifulSelectLists.each(function() {
            // This
            let ths = $(this);
            // List option
            let allOption = ths.find("option");
            // New list & attr
            let newOptionList = "";
            // hasSelected ?
            let selectedName = "";

            // Update list counter
            listID += 1;

            if (allOption) {
                allOption.each(function() {
                    let thsOption = $(this);
                    // Attribute
                    let name     = String(thsOption.text());
                    // Conditions for name
                    if (ths.hasClass("arbitrage_currencies")) {
                        name     = String(thsOption.attr("data-name"));
                    }
                    let value    = Number(thsOption.val());
                    // Conditions for value
                    if (ths.hasClass("arbitrage_currencies") == true) {
                        value    = String(thsOption.val());
                    }
                    else if (ths.hasClass("merchant_list") == true) {
                        value    = String(thsOption.val());
                    }
                    let newClass = (thsOption.attr("selected")) ? "list_block active" : "list_block";
                    let addAttr  = "";
                    // Conditions for additional attribute
                    if (ths.hasClass("withdrawals") == true) {
                        addAttr  = `data-is-currency=${String(thsOption.attr("data-is-currency"))}`;
                    }
                    else if (ths.hasClass("merchant_list") == true) {
                        addAttr  = `data-id=${Number(thsOption.attr("data-id"))}`;
                    }

                    if (thsOption.attr("selected")) {
                        selectedName = name;
                    }

                    newOptionList += `<div class="${newClass}" data-value='${value}' ${addAttr}>
                                            <div class="icon">
                                                <svg width="20px" height="20px" x="0px" y="0px" viewBox="0 0 490.661 490.661" style="enable-background:new 0 0 490.661 490.661;">
                                                    <path d="M453.352,236.091L48.019,1.424c-3.285-1.899-7.36-1.899-10.688,0c-3.285,1.899-5.333,5.419-5.333,9.237v469.333 c0,3.819,2.048,7.339,5.333,9.237c1.643,0.939,3.499,1.429,5.333,1.429c1.856,0,3.691-0.469,5.355-1.429l405.333-234.667 c3.285-1.92,5.312-5.44,5.312-9.237S456.637,237.989,453.352,236.091z"/>
                                                </svg>
                                            </div>
                                            <p class="text">${name}</p>
                                        </div>`;
                });
            }

            // Update events for this new select list
            function SetEventOnNewList() {
                let newList = $(".base_select_list");

                if (newList) {
                    newList.each(function() {
                        // This
                        let thsList      = $(this);
                        // List target - for update selected option in parent list
                        let listTarget   = thsList.attr("data-target");
                        // List header - for click event (open\hide) list
                        let listHeader   = thsList.find(".select_header");
                        let headerText   = listHeader.find(".text");
                        // List option
                        let listOption   = thsList.find(".select_list");
                        let allListBlock = listOption.find(".list_block");

                        // Function for open\close list
                        function ViewSelectList(isOpen) {
                            let status = (isOpen) ? isOpen : false;
                            let listHeight = "116px"; // Basic

                            if (allListBlock.length >= 5) {
                                listHeight = `${(allListBlock.outerHeight(true) * 5) + 4}px`;
                            }

                            if (status == true) {
                                // Close another list (if they open)
                                newList.removeClass("active");
                                newList.find(".select_list").css("height", "0px");

                                // Update css terms for current list
                                listOption.css("height", listHeight);
                                thsList.addClass("active");
                            }
                            else {
                                listOption.css("height", "0px");
                                thsList.removeClass("active");
                            }
                        }

                        // Remove old click event
                        listHeader.unbind("click");
                        // Set new click event
                        listHeader.on("click", () => {
                            if (thsList.hasClass("active") == false) {
                                ViewSelectList(true);
                            }
                            else {
                                ViewSelectList(false);
                            }
                        });

                        // Event for click on list block
                        allListBlock.each(function() {
                            // This
                            let blockThis = $(this);

                            blockThis.on("click", () => {
                                // Attr value & text
                                let blockValue = Number(blockThis.attr("data-value"));
                                let blockText  = String(blockThis.find(".text").text());

                                if (blockThis.hasClass("active") == false) {
                                    // Update active class on current & old element
                                    allListBlock.removeClass("active");
                                    blockThis.addClass("active");
                                    // Update text in header
                                    headerText.text(blockText);
                                    // Set current element on parent list
                                    if (thsList.hasClass("arbitrage_list") == true) {
                                        $(`.${listTarget}`).find(`option[data-name=${blockText}]`).prop("selected", true);
                                    }
                                    else if (ths.hasClass("withdrawals") == true) {
                                        // Check currency type
                                        let isCrypto = blockThis.attr("data-is-currency");
                                        // Set active option
                                        $(`.${listTarget}`).find(`option[value=${blockValue}]`).prop("selected", true);
                                        if (ths.hasClass("withdrawals_balance") == true) {
                                            // Set currency id in hidden input on withdrawals form
                                            $(".withdrawal_currency_id.balance_form").val(blockValue);
                                            // Set method type on withdrawals form
                                            if (isCrypto == 1) {
                                                $(".to_payment_systems.balance_form").prop("checked", false)
                                            }
                                            else if (isCrypto == 0) {
                                                $(".to_payment_systems.balance_form").prop("checked", true)
                                            }
                                        }
                                        else if (ths.hasClass("withdrawals_referrals") == true) {
                                            // Set currency id in hidden input on withdrawals form
                                            $(".withdrawal_currency_id.referral_form").val(blockValue);
                                            // Set method type on withdrawals form
                                            if (isCrypto == 1) {
                                                $(".to_payment_systems.referral_form").prop("checked", false)
                                            }
                                            else if (isCrypto == 0) {
                                                $(".to_payment_systems.referral_form").prop("checked", true)
                                            }
                                        }
                                    }
                                    else if (ths.hasClass("merchant_list") == true) {
                                        $(`.${listTarget}`).find(`option[data-id=${blockThis.attr("data-id")}]`).prop("selected", true);
                                    }
                                    else {
                                        $(`.${listTarget}`).find(`option[value=${blockValue}]`).prop("selected", true);
                                    }
                                        // Close list
                                    ViewSelectList(false);
                                }
                            });
                        });
                    });
                }
            }

            // Function to create a new select list
            function CreateNewSelectList(selected, options, whereCreate) {
                if (whereCreate) {
                    let createWrapper = () => {
                        let className    = (ths.hasClass("arbitrage_currencies")) ? "base_select_list arbitrage_list" : "base_select_list";
                        let selectHeader = `<div class="select_header">
                                                <p class="text">${selected}</p>

                                                <span class="icon">
                                                    <svg x="0px" y="0px" width="20px" height="20px" viewBox="0 0 292.362 292.362" style="enable-background:new 0 0 292.362 292.362;">
                                                        <path d="M286.935,69.377c-3.614-3.617-7.898-5.424-12.848-5.424H18.274c-4.952,0-9.233,1.807-12.85,5.424 C1.807,72.998,0,77.279,0,82.228c0,4.948,1.807,9.229,5.424,12.847l127.907,127.907c3.621,3.617,7.902,5.428,12.85,5.428 s9.233-1.811,12.847-5.428L286.935,95.074c3.613-3.617,5.427-7.898,5.427-12.847C292.362,77.279,290.548,72.998,286.935,69.377z"/>
                                                    </svg>
                                                </span>

                                                <span class="base_select_add_block">
                                                    <img src="/static/account/img/icons/input_add_block.png" alt="Company_name">
                                                </span>
                                            </div>`;
                        let selectList = `<div class="select_list">${options}</div>`;
                        return (`<div class="${className}" data-target="bsl_${listID}">
                                    ${selectHeader}
                                    ${selectList}
                                </div>`);
                    }

                    whereCreate.after(createWrapper());

                    // Update event for a new list
                    SetEventOnNewList();

                    ths.addClass(`bsl_${listID}`);
                }
            }
            // Run function
            CreateNewSelectList(selectedName, newOptionList, ths);
        });
    }

    /**
     * FAQ
    */
    let allFaqWrappers = $(".faq_wrapper");

    if (allFaqWrappers) {
        allFaqWrappers.each(function() {
            let ths = $(this);
            // All FAQ blocks
            let faqBlocks = ths.find(".faq_content .block");
            // All blocks info wrapper
            let faqBlocksInfoWrapper = ths.find(".block_info");

            faqBlocks.each(function() {
                let thsBlock = $(this);
                // Block header for click event
                let blockHeader = thsBlock.find(".block_head");
                // Block info wrapper
                let blockInfoWrapper = thsBlock.find(".block_info");
                // Block text
                let blockText = blockInfoWrapper.find(".text");

                blockHeader.on("click", () => {
                    if (thsBlock.hasClass("active") == false) {
                        // Remove active class & hide all block
                        faqBlocks.removeClass("active");
                        faqBlocksInfoWrapper.css("height", "0px");

                        // Set active class on current faq block
                        thsBlock.addClass("active");
                        blockInfoWrapper.css("height", `${blockText.outerHeight(true)}px`);
                    }
                    else if (thsBlock.hasClass("active") == true) {
                        // Remove active class & hide all block
                        thsBlock.removeClass("active");
                        blockInfoWrapper.css("height", "0px");
                    }
                });
            });

            // Set active class on first faq block
            faqBlocks.eq(0).addClass("active");
            faqBlocks.eq(0).find(".block_info").css("height", `${faqBlocks.eq(0).find(".block_info .text").outerHeight(true)}px`);
        });
    }

    /**
     * Arbitrage deal transactions
    */
    let arbitrageDealTransactions = $(".arbitrage_deals_wrapper");

    if (arbitrageDealTransactions) {
        arbitrageDealTransactions.each(function() {
            // This
            let ths = $(this);
            // Visible elements on page
            let elementsOnPage = 4;
            // Dots count
            let dotsCount = 0;
            // Arbitrage deals
            let dealsWrapper      = ths.find(".big_transaction_wrapper");
            let allDeals          = dealsWrapper.find(".big_transaction_block");
            let dealsLength       = allDeals.length;
            // Pagination wrapper
            let paginationWrapper = ths.find(".deals_control");
            // Pagination dots wrapper
            let dotsWrapper       = paginationWrapper.find(".dots_wrapper");
            // Pagination control buttons
            let prevBtn           = paginationWrapper.find("button.prev"),
                nextBtn           = paginationWrapper.find("button.next");

            // Создание Data атрибутов для всех элементов
            function CreateDataNum(target) {
                if (target) {
                    for (i = 0; i <= target.length; i++) {
                        target.eq(i).attr('data-num', (i + 1));
                    }
                }
            }
            // Function for created pagination
            function CreatePagination(wrapper, elementsCount) {
                if (wrapper) {
                    let count = (elementsCount) ? elementsCount : 0;
                    let btnCount = Math.ceil(count / elementsOnPage);

                    for (i = 1; i <= btnCount; i++) {
                        if (i == 1) {
                            wrapper.append(`<div class="dot active" data-page="${i}">${i}</div>`);
                        }
                        else {
                            wrapper.append(`<div class="dot" data-page="${i}">${i}</div>`);
                        }

                        dotsCount++;
                    }
                }
            }
            // Сокрытие элементов и вывод по активной подстранице
            function HideDealElements(page) {
                let activePage = (page) ? page : dotsWrapper.find('.dot.active').attr('data-page');

                allDeals.addClass('hide');

                for (i = (activePage * elementsOnPage); i > ((activePage * elementsOnPage) - elementsOnPage); i--) {
                    dealsWrapper.find(`[data-num="${i}"]`).removeClass('hide');
                }
            }

            // Write data attr on deal wrapper
            CreateDataNum(allDeals);
            // Create pagination on page
            CreatePagination(dotsWrapper, dealsLength);
            // Hide deals on page
            HideDealElements();

            // All dots
            let allDots = dotsWrapper.find(".dot");

            // Function for hide dots
            function HideDotsButton(page) {
                let activePage = (page) ? page : Number(dotsWrapper.find('.dot.active').attr('data-page'));

                allDots.addClass("hide");
                allDots.eq(activePage - 1).removeClass("hide");
                // Condition for after & before dots
                allDots.eq(activePage).removeClass("hide");
                allDots.eq(activePage + 1).removeClass("hide");
                // For first and second dots
                if (activePage == 1) {
                    allDots.eq(activePage + 3).removeClass("hide");
                    allDots.eq(activePage + 2).removeClass("hide");
                }
                else if (activePage == 2) {
                    allDots.eq(activePage + 2).removeClass("hide");
                    allDots.eq(activePage - 2).removeClass("hide");
                }
                else {
                    allDots.eq(activePage - 2).removeClass("hide");
                    allDots.eq(activePage - 3).removeClass("hide");
                }
            }
            // Run first start function
            HideDotsButton();

            allDots.each(function() {
                let thsDot = $(this);
                // Data attr
                let pageNum = Number(thsDot.attr("data-page"));

                thsDot.on("click", () => {
                    allDots.removeClass("active");
                    thsDot.addClass("active");

                    HideDotsButton(pageNum);
                    HideDealElements(pageNum);
                });
            });

            function SwipeWithButton(page) {
                let activePage = (page) ? page : Number(dotsWrapper.find('.dot.active').attr('data-page'));

                if (activePage > dotsCount) {
                    activePage = dotsCount;
                }
                else if (activePage <= 0) {
                    activePage = 1;
                }

                allDots.removeClass("active");
                allDots.eq(activePage - 1).addClass("active");

                HideDotsButton(activePage);
                HideDealElements(activePage);
            }

            prevBtn.on("click", () => {
                let activePage = Number(dotsWrapper.find('.dot.active').attr('data-page'));

                SwipeWithButton(activePage - 1);
            });
            nextBtn.on("click", () => {
                let activePage = Number(dotsWrapper.find('.dot.active').attr('data-page'));

                SwipeWithButton(activePage + 1);
            });
        });
    }

    /**
     * Partners table control
    */
    let allPartnersTable = $(".partner_line_tables");

    if (allPartnersTable) {
        allPartnersTable.each(function() {
            // This
            let ths = $(this);
            // Control
            let prevBtn = ths.find(".lines_control .prev"),
                nextBtn = ths.find(".lines_control .next");
            let counter = ths.find(".lines_control .active_line");
            // All content
            let contentWrapper = ths.find(".line_tables_content");
            let allContents    = contentWrapper.find(".wrapper_block");
            let contentLength  = allContents.length;
            // Active content
            let active = 1;

            function SwipeContent(n) {
                let activeContent = (n) ? n : contentWrapper.find(".wrapper_block.active").index();

                active = active + activeContent;

                if (active >= contentLength) {
                    active = contentLength;
                }
                else if (active <= 1) {
                    active = 1;
                }

                allContents.removeClass("active");
                allContents.eq(active - 1).addClass("active");
                // Write new counter num
                counter.text(active);
            }

            prevBtn.on("click", () => {
                SwipeContent(-1);
            });
            nextBtn.on("click", () => {
                SwipeContent(1);
            });
        });
    }

    /**
     * Arbitrage slider
    */
    let arbitrageSlider = $(".arbitrage_plan_slider");

    if (arbitrageSlider) {
        arbitrageSlider.each(function() {
            // This
            let ths = $(this);
            // Hidden inputs for form control
            let hiddenInputs     = ths.find(".hidden_inputs");
            // Slides wrapper & all slide
            let slidesWrapper     = ths.find(".slides_wrapper");
            let allSlide          = slidesWrapper.find(".slide_block");
            // Slides count
            let slideLength       = allSlide.length;
            // Slider control
            let controlWrapper    = ths.find(".slides_control");
            // Dots wrapper
            let dotsWrapper       = controlWrapper.find(".dots_wrapper");
            // Control buttons
            let prevBtn           = controlWrapper.find(".btn.prev");
            let nextBtn           = controlWrapper.find(".btn.next");
            // Dots count
            let dotsCount = 0;
            // Active slide
            let active = 1;

            // Swipe plan terms or bot preview
            allSlide.each(function() {
                let thsSlide           = $(this);
                // Current slide data terms
                let termsWrapper       = thsSlide.find(".block_data .data_terms");
                // Button for swipe bot & terms
                let flipBtn            = termsWrapper.find("button.data_flip");
                // Arbitrage modal window
                let modalPlanBuyBtn    = thsSlide.find(".arbitrage_button_modal.buy_plan");
                let modalBotBuyBtn     = thsSlide.find(".arbitrage_button_modal.buy_bot");
                let allArbitrageWindow = $(".arbitrage_modal_window");
                let PlanBuyWindow      = $(".arbitrage_modal_window.arbitrage_modal_buy");
                let BotBuyWindow       = $(".arbitrage_modal_window.bot_modal_buy");
                // Attr for modal window
                let planName           = String(thsSlide.find(".data_preview .name").text());
                let planMinPrice       = String(thsSlide.find(".data_terms .plan_min_price").text());
                let planMaxPrice       = String(thsSlide.find(".data_terms .plan_max_price").text());

                function ViewModalWindow(button) {
                    // Target attr & object
                    let targetAttr = button.attr("target");
                    let targetObj  = $(`.${targetAttr}`);

                    if (targetObj) {
                        // Condition for closing old window if opened new window
                        allArbitrageWindow.removeClass("active");
                        // Set active class on open window
                        targetObj.addClass("active");
                        // Set active class on lock modal background
                        lockModalWrapper.addClass("active");
                    }
                }
                if (allArbitrageWindow) {
                    modalPlanBuyBtn.on("click", () => {
                        // Set new value on object
                        PlanBuyWindow.find(".plan_info .name").text(planName);
                        PlanBuyWindow.find(".plan_info .min_price").text(planMinPrice);
                        PlanBuyWindow.find(".plan_info .max_price").text(planMaxPrice);
                        PlanBuyWindow.find("#plan_invest_amount").attr("min", Number(planMinPrice));
                        PlanBuyWindow.find("#plan_invest_amount").attr("max", Number(planMaxPrice));
                        // Condition for closing old window if opened new window
                        allArbitrageWindow.removeClass("active");
                        // Set active class on lock modal background
                        lockModalWrapper.addClass("active");
                        // Set active class on open window
                        PlanBuyWindow.addClass("active");
                    });
                    modalBotBuyBtn.on("click", () => {
                        // Set new value on object
                        BotBuyWindow.find(".plan_info .plan_name").text(planName);
                        // Condition for closing old window if opened new window
                        allArbitrageWindow.removeClass("active");
                        // Set active class on lock modal background
                        lockModalWrapper.addClass("active");
                        // Set active class on open window
                        BotBuyWindow.addClass("active");
                    });
                }

                flipBtn.on("click", function() {
                    if (termsWrapper.hasClass("is_flipped") == false) {
                        termsWrapper.addClass("is_flipped");
                    }
                    else {
                        termsWrapper.removeClass("is_flipped");
                    }
                });
            });

            // Function for created pagination
            function CreatePagination(wrapper, elementsCount) {
                if (wrapper) {
                    let count = (elementsCount) ? elementsCount : 0;

                    for (i = 1; i <= count; i++) {
                        if (i == 1) {
                            wrapper.append(`<div class="dot active" data-slide="${i}">${i}</div>`);
                        }
                        else {
                            wrapper.append(`<div class="dot" data-slide="${i}">${i}</div>`);
                        }

                        dotsCount++;
                    }
                }
            }
            // Function call
            CreatePagination(dotsWrapper, slideLength);

            // All dots
            let allDots = dotsWrapper.find(".dot");
            // Swipe Slide
            function SwipeSlide(n) {
                let activeContent = (n) ? n : slidesWrapper.find(".slide_block.active").index();

                active = active + activeContent;

                if (active >= slideLength) {
                    active = slideLength;
                }
                else if (active <= 1) {
                    active = 1;
                }

                // Slide hide & view active dot
                allDots.removeClass("active");
                allDots.eq(active - 1).addClass("active");
                // Slide hide & view active slide
                allSlide.removeClass("active");
                allSlide.eq(active - 1).addClass("active");
                // Set checked status on current input
                if (hiddenInputs.hasClass("has_active") == false) {
                    hiddenInputs.find(`input#arbitrage_plan_${active}`).prop("checked", true);
                }
            }

            // Dots control
            allDots.each(function() {
                // This
                let thsDot = $(this);

                thsDot.on("click", () => {
                    // Data attr
                    let slideNum = Number(thsDot.attr("data-slide"));

                    allDots.removeClass("active");
                    thsDot.addClass("active");

                    allSlide.removeClass("active");
                    allSlide.eq(slideNum - 1).addClass("active");

                    active = slideNum;
                    // Set checked status on current input
                    if (hiddenInputs.hasClass("has_active") == false) {
                        hiddenInputs.find(`input#arbitrage_plan_${slideNum}`).prop("checked", true);
                    }
                });
            });
            // Button control
            prevBtn.on("click", () => {
                SwipeSlide(-1);
            });
            nextBtn.on("click", () => {
                SwipeSlide(1);
            });
        });
    }

    /**
     * Partners link copy
    */
    let partnersLink = $(".partner_link");

    if (partnersLink) {
        partnersLink.each(function() {
            let ths = $(this);
            // Copy button
            let copyBtn = ths.find("button.link_copy");
            // Button text attr
            let copyLink   = copyBtn.attr("data-link");
            let baseText   = String(copyBtn.attr("data-base-text"));
            let copiedText = String(copyBtn.attr("data-copied-text"));
            // Copied status
            let isCopied = false;

            copyBtn.on("click", () => {
                if (isCopied == false) {
                    let copyInput = `<input style="position: fixed; top: -200px; left: -200px;" class="link_input" type="text" value="${copyLink}">`;
                    // Update copied status
                    isCopied = true;
                    // Create hidden element with link for copy event
                    copyBtn.append(copyInput);
                    copyBtn.find(".link_input").select();
                    document.execCommand('copy');
                    console.log($(".link_input"), copyBtn.find(".link_input"));
                    copyBtn.find(".link_input").remove();

                    // Update button text
                    copyBtn.find(".btn_text").text(copiedText);

                    setTimeout(function() {
                        // Update copied status
                        isCopied = false;
                        // Update button text
                        copyBtn.find(".btn_text").text(baseText);
                    }, 2500);
                }
            });
        });
    }

    let investCard = $(".pricing-card")
    if(investCard){
        let PlanBuyWindow      = $(".arbitrage_modal_window.arbitrage_modal_buy");
        investCard.each(function() {
            let ths = $(this);
            let submitBtn = ths.find("a.button");
            submitBtn.attr("href", "javascript:void(0)");
            let amount = submitBtn.attr("data-amount");
            let planName           = String(ths.find(".card-left h1").text());
            submitBtn.on("click", () => {
                return;
                $("#amount").val(amount);
                PlanBuyWindow.find(".plan_info .name").text(planName);
                lockModalWrapper.addClass("active");
                PlanBuyWindow.addClass("active");
            })
        });
        let modalInvestment    = $(".arbitrage_modal_window.modal_confirm_investment");
        let btnConfirm = PlanBuyWindow.find('button');
        btnConfirm.on("click", () => {
            $("#overlay-modal").fadeIn(300);　
          /*  modalInvestment.find("img.preview_wallet").attr("src","/static/account/img/loading.gif");
            modalInvestment.find(".plan_info").css("display", "none"); */
            var formData = $('#merchantInvestForm').serializeArray();
            var params = {};
            $.each(formData,function(i, v) {
                params[v.name] = v.value;
            });
            Pub.post(`/account/investment/create-invoice`, params, function (ret, err) {
                if (ret.success == 1) {
                    $("#overlay-modal").fadeOut(300);
                    Pub.toast('Success', 'success');
                    PlanBuyWindow.removeClass("active");
                    setTimeout(() => {
                        location.reload(true);
                    }, 3000);
                    return;
                    modalInvestment.find(".plan_info").css("display", "block")
                    modalInvestment.find(".plan_info .plan_address").text(ret.address);
                    modalInvestment.find(".plan_info .plan_coin").text(`${ret.amount} ` + ' ' + `${ret.currency}`);
                    modalInvestment.find(".plan_info .plan_amount").text(`: $ ${ret.amount_usd}` );
                    let amount_send =String(ret.amount);
                    amount_send = amount_send.replace(".", ',')
                    let add_ = 'https://chart.googleapis.com/chart?chs=180x180&cht=qr&chl=bitcoin:'+ret.address+'?amount='+amount_send+'';
                    modalInvestment.find("img.preview_wallet").attr("src",add_);
                    setInterval(async () => {
                        let response = await fetch("/account/investment/check-status/"+ret.currency)
                        let checkStatus = await response.json()      
                        if(checkStatus.success == 1){
                            modalInvestment.find(".plan_info .waiting").text(`Successful Investment` );
                            modalInvestment.find(".plan_info .waiting").css("color", "green");
                            location.reload(true);
                        }else{
                            modalInvestment.find(".plan_info .plan_coin").text(`${checkStatus.amount_send} ` + ' ' + `${ret.currency}`);
                            add_ = 'https://chart.googleapis.com/chart?chs=180x180&cht=qr&chl=bitcoin:'+ret.address+'?amount='+checkStatus.amount_send+'';
                            modalInvestment.find("img.preview_wallet").attr("src",add_);
                        }

                    }, 10000);
                }
                else {
                    $("#overlay-modal").fadeOut(300);
                    Pub.toast(ret.msg ? ret.msg : "Error!", 'fail', 5000);
                }
            }, (e) => {
                $("#overlay-modal").fadeOut(300);
                Pub.toast('Error! Please try again', 'fail');
                
            })
            
            /* PlanBuyWindow.removeClass("active"); */
            /* modalInvestment.addClass("active"); */
        })
    }
    let action_position = $('.action_position li');
    
    if (action_position){
        action_position.each(function(){
            let ths = $(this);
            let submitBtn = ths.find("input");
            submitBtn.on("change", (e) => {
                let value = e.target.value;
                var params = {'value': value}
                Pub.post(`/account/update-position`, params, function (ret, err) {
                    if (ret.success == 1) {
                        Pub.toast('Success', 'success');
                    }
                    else {
                        Pub.toast('Error!', 'fail');
                    }
                }, (e) => {
                    Pub.toast('Error! Please try again', 'fail');
                })
                
            })
        })
    }

    let tableDailyProfit = $(".table_daily_profit");
    if (tableDailyProfit.length > 0) {
        let rowTable = tableDailyProfit.find('tbody tr');
        let total_usd = 0, total_usdt = 0, total_btc = 0, total_eth = 0, total_trx = 0, total_qtc = 0;
        rowTable.each(function() {
            let ths = $(this);            
            let currency = ths.find('.t_profit_currency').attr("data-currency");
            let amount_coin = ths.find('.t_profit_amount_coin').attr("data-amount_coin");
            let amount_usd = ths.find('.t_profit_amount_usd').attr("data-amount_coin");
            
            let statoshi_to_coin = parseFloat(amount_coin)/100000000
            currency == "BTC" ? 
                total_btc = parseFloat(statoshi_to_coin) + parseFloat(total_btc)
            : currency == "ETH" ? 
                total_eth = parseFloat(statoshi_to_coin) + parseFloat(total_eth)
                : currency == "TRX" ?
                total_trx = parseFloat(statoshi_to_coin) + parseFloat(total_trx)
                : currency == "USD" ?
                total_usd = parseFloat(amount_usd) + parseFloat(total_usd)
                : currency == "QTC" ? 
                total_qtc = parseFloat(statoshi_to_coin) + parseFloat(total_qtc)
                : total_usdt = parseFloat(statoshi_to_coin) + parseFloat(total_usdt);

        })
        $('.total_qtc_profit').text(total_qtc.toFixed(8) + ' QTC');
        $('.total_usd_profit').text(total_usd.toFixed(4) + ' USD');
        $('.total_btc_profit').text(total_btc.toFixed(8) );
        $('.total_usdt_profit').text(total_usdt.toFixed(8) + ' USDT');
        $('.total_eth_profit').text(total_eth.toFixed(8) + ' ETH');
        $('.total_trx_profit').text(total_trx.toFixed(8) + ' TRX');
    }
    let tableDailyProfit_B = $(".table_commission_binary");
    if (tableDailyProfit_B.length > 0) {
        let rowTable = tableDailyProfit_B.find('tbody tr');
        let total_usd = 0, total_usdt = 0, total_btc = 0, total_eth = 0, total_qtc = 0;
        rowTable.each(function() {
            let ths = $(this);            
            let currency = ths.find('.binary_currency').attr("data-currency");
            let amount = ths.find('.binary_amount').attr("data-amount");
            currency == "USD" ? 
            total_usd = parseFloat(total_usd)+ parseFloat(amount) : 
            total_qtc = parseFloat(total_qtc) + parseFloat(amount)/100000000
        })
        $('.total_qtc_binary').text(total_qtc.toFixed(8) + ' QTC');
        $('.total_usd_binary').text(total_usd.toFixed(3) + ' USD');
    }
    let tableDailyProfit_I = $(".table_commission_i");
    if (tableDailyProfit_I.length > 0) {
        let rowTable = tableDailyProfit_I.find('tbody tr');
        let total_usd = 0, total_usdt = 0, total_btc = 0, total_eth = 0, total_qtc = 0;
        rowTable.each(function() {
            let ths = $(this);            
            let currency = ths.find('.i_currency').attr("data-currency");
            let amount = ths.find('.i_amount').attr("data-amount");
            currency == "USD" ? 
            total_usd = parseFloat(total_usd)+ parseFloat(amount) : 
            total_qtc = parseFloat(total_qtc) + parseFloat(amount)/100000000
        })
        $('.total_qtc_i').text(total_qtc.toFixed(8) + ' QTC');
        $('.total_usd_i').text(total_usd.toFixed(3) + ' USD');
    }
    let tableDailyProfit_F = $(".table_commission_f");
    if (tableDailyProfit_F.length > 0) {
        let rowTable = tableDailyProfit_F.find('tbody tr');
        let total_usd = 0, total_usdt = 0, total_btc = 0, total_eth = 0, total_qtc = 0;
        rowTable.each(function() {
            let ths = $(this);            
            let currency = ths.find('.f_currency').attr("data-currency");
            let amount = ths.find('.f_amount').attr("data-amount");
            currency == "USD" ? 
            total_usd = parseFloat(total_usd)+ parseFloat(amount) : 
            total_qtc = parseFloat(total_qtc) + parseFloat(amount)/100000000
        })
        $('.total_qtc_f').text(total_qtc.toFixed(8) + ' QTC');
        $('.total_usd_f').text(total_usd.toFixed(3) + ' USD');
    }
    // Remove page loader
    setTimeout(function() {
        pageLoader.remove();
    }, 250);
    $('#withdrawal_balance_amount_').keyup((e) => {
        console.log($('.qtc_price').attr("data-qtc"));
        $('#withdrawal_balance_amount_trx').val(
            (parseFloat(e.currentTarget.value)/parseFloat($('.qtc_price').attr("data-qtc"))).toFixed(5)
        )
    });
    $('#withdrawal_balance_amount').keyup((e) => {        
        console.log($('.qtc_price').attr("data-qtc"));
        $('#withdrawal_balance_amount_usd').html(
            (parseFloat(e.currentTarget.value)*parseFloat($('.qtc_price').attr("data-qtc"))).toFixed(3)
        )
    });
   
});
function getAddress(currency) {
    var params = {'currency': currency}
    let lockModalWrapper = $(".lock_modal_bg");
    Pub.post(`/account/wallet/get-address`, params, function (ret, err) {
        if (ret.success == 1) {
            let PlanBuyWindow      = $(".arbitrage_modal_window.arbitrage_modal_buy");
            PlanBuyWindow.find(".plan_info b").text(ret.address);
            let add_ = 'https://chart.googleapis.com/chart?chs=180x180&cht=qr&chl=bitcoin:'+ret.address+'';
            PlanBuyWindow.find("img").attr("src",add_);
            lockModalWrapper.addClass("active");
            PlanBuyWindow.addClass("active");
        }
        else {
            Pub.toast('Error!', 'fail');
        }
    }, (e) => {
        Pub.toast('Error! Please try again', 'fail');
    })
}

function getCode(e, type) {
    let $target = $(e.target);
    var params = {'type': type}
    let lockModalWrapper = $(".lock_modal_bg");
    let getCodeCls = $('.get_code');
    let codeBtn = getCodeCls.find("a");
    codeBtn.addClass('disabled')
    Pub.post(`/account/wallet/get-otp`, params, function (ret, err) {
        let getCodeCls = $('.get_code');
        let codeBtn = getCodeCls.find("button");
        if (ret.success == 1) {
            Pub.toast('Verification code sent', 'success');
            codeBtn.addClass('disabled')
            let timeleft = 60;
            let downloadTimer = setInterval(function(){
                if(timeleft <= 1){
                    clearInterval(downloadTimer);
                    codeBtn.removeClass('disabled');
                    $target.text(`Get OTP`)
                } else {
                    $target.text(`Time ${timeleft}s`)
                }
                timeleft -= 1;
            }, 1000);
        }
        else {
            codeBtn.removeClass('disabled')
            Pub.toast(ret.msg ? ret.msg : "Error!", 'fail');
        }
    }, (e) => {
        Pub.toast('Error! Please try again', 'fail');
    })
}

function openWithdraw(currency){
    $('.modal_title').html(
        currency =="QTC" ? "Withdraw QTC" 
        : currency == "QTC2" ? "Withdraw QTC Reward"
        : currency == "QTC3" ? "Withdraw QTC"
        : currency == "QTC4" ? "Withdraw QTC Promotion"
        : `Withdraw ${currency}`
    );
    $('#withdrawal_balance_amount_usd').html('0')
    if(currency == "QTC2"){
        $('.wait_time').show();
        $('.qtc_reward').show();
        $('.qtc_balance').hide();
        $('.qtc_promotion').hide();
    } else if(currency == "QTC"){
        $('.wait_time').hide();
        $('.qtc_reward').hide();
        $('.qtc_balance').show();
        $('.qtc_promotion').hide();
    } else if(currency == "QTC4"){
        $('.wait_time').hide();
        $('.qtc_reward').hide();
        $('.qtc_promotion').show();
        $('.qtc_balance').hide();
    }else{
        $('.wait_time').hide()
        $('.qtc_reward').hide();
        $('.qtc_balance').hide();
        $('.qtc_promotion').hide();
    }

    let lockModalWrapper = $(".lock_modal_bg");
    let modalWithdraw    = $(".arbitrage_modal_window.modal_withdraw");
    currency = currency == "USDT.ERC20" ? "USDT" : currency;
    let _img = `/static/account/img/icons/${currency == "QTC3" ||  currency == "QTC4" ? "qtc" : currency.toLowerCase()}.svg`;
    modalWithdraw.find('img').attr("src", _img)
    lockModalWrapper.addClass("active");
    modalWithdraw.addClass("active");
    $('.number_add_code').text(currency == "QTC3" ||  currency == "QTC4" || currency == "QTC2" ? 'QTC' : currency)
    $('input[name="_currency"]').val(currency)
    let frmCryptoWithdraw = $('.withdraw_crypto_form');
    let submitBtn = frmCryptoWithdraw.find("button");
    submitBtn.on("click", (e) => {
        submitBtn.prop('disabled', true)
        var formData = frmCryptoWithdraw.serializeArray();
        var params = {};
        $.each(formData,function(i, v) {
            params[v.name] = v.value;
        });
        Pub.post(`/account/wallet/withdraw-crypto`, params, function (ret, err) {
            if (ret.success == 1) {
                Pub.toast('Success', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            }
            else {
                submitBtn.prop('disabled', false);
                Pub.toast(ret.msg ? ret.msg : "Error!", 'fail');
            }
        }, (e) => {
            Pub.toast('Error! Please try again', 'fail');
            submitBtn.prop('disabled', false);
        })
        
    })
}
function openWithdrawCommission(currency){
    $('.modal_title').html("Withdraw Commission");
    let lockModalWrapper = $(".lock_modal_bg");
    let modalWithdraw    = $(".arbitrage_modal_window.modal_withdraw_commission");
    currency = currency == "USDT.ERC20" ? "USDT" : currency;
    let _img = `/static/account/img/icons/${currency.toLowerCase()}.svg`;
    modalWithdraw.find('img').attr("src", _img)
    lockModalWrapper.addClass("active");
    modalWithdraw.addClass("active");
    $('.number_add_code').text(currency)
    $('input[name="_currency"]').val(currency)
    let frmCryptoWithdraw = $('.withdraw_crypto_form');
    let submitBtn = frmCryptoWithdraw.find("button");
    submitBtn.on("click", (e) => {
        submitBtn.prop('disabled', true)
        var formData = frmCryptoWithdraw.serializeArray();
        var params = {};
        $.each(formData,function(i, v) {
            params[v.name] = v.value;
        });
        Pub.post(`/account/withdraw-commission`, params, function (ret, err) {
            if (ret.success == 1) {
                Pub.toast('Success', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            }
            else {
                submitBtn.prop('disabled', false);
                Pub.toast(ret.msg ? ret.msg : "Error!", 'fail');
            }
        }, (e) => {
            Pub.toast('Error! Please try again', 'fail');
            submitBtn.prop('disabled', false);
        })
        
    })
}
function preview_image(event, _id){
    var reader = new FileReader();
    reader.onload = function(){
        var output = document.getElementById(_id);
        output.className = "active";
        output.style.backgroundImage = `url('${reader.result}')`;
    }
    reader.readAsDataURL(event.target.files[0]);
}
function avatar_change(event){
    var reader = new FileReader();
    reader.onload = function(){
        var output = document.getElementById('preview_avatar');
        output.style.backgroundImage = `url('${reader.result}')`;
        var _btn = document.getElementById('btn_change_avatar');
        _btn.className="active";
    }
    reader.readAsDataURL(event.target.files[0]);
}
function avatar_cancel(event) {
    var output = document.getElementById('preview_avatar');
    output.removeAttribute("style");
    var _btn = document.getElementById('btn_change_avatar');
        _btn.removeAttribute("class");
}