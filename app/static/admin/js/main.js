
$(document).ready(function() {
    moment.locale("en");
    function flask_moment_render(elem) {
        $(elem).text(eval('moment("' + $(elem).data('timestamp') + '").' + $(elem).data('format') + ';'));
        $(elem).removeClass('flask-moment').show();
    }
    function flask_moment_render_all() {
        $('.flask-moment').each(function() {
            flask_moment_render(this);
            if ($(this).data('refresh')) {
                (function(elem, interval) { setInterval(function() { flask_moment_render(elem) }, interval); })(this, $(this).data('refresh'));
            }
        })
    }
    let add_postModal = ('#add_postModal');
    if(add_postModal.length > 0){
        $("#title").keyup(function(){
                var Text = $(this).val();
                Text = Text.toLowerCase();
                Text = Text.replace(/[^a-zA-Z0-9]+/g,'-');
                $("#slug").val(Text);        
        });
    }
    
    let tableInvestment = $(".table_investment");
    if (tableInvestment.length > 0) {
        let rowTable = tableInvestment.find('tbody tr');
        let total_usd = 0, total_usdt = 0, total_btc = 0, total_eth = 0, total_trx = 0;
        rowTable.each(function() {
            flask_moment_render_all();
            let ths = $(this);      
            let $date = ths.find(".flask-moment");
            $date.css("display","block");      
            let usd = ths.find('.amount_usd');
            let currency = ths.find('.amount_coin').attr("data-currency");
            let amount_coin = ths.find('.amount_coin').attr("data-amount_coin");
            
            let statoshi_to_coin = parseFloat(amount_coin)/100000000
            currency == "BTC" ? 
                total_btc = parseFloat(statoshi_to_coin) + parseFloat(total_btc)
            : currency == "ETH" ? 
                total_eth = parseFloat(statoshi_to_coin) + parseFloat(total_eth)
                : currency == "TRX" ? 
                total_trx = parseFloat(statoshi_to_coin) + parseFloat(total_trx)
                : total_usdt = parseFloat(statoshi_to_coin) + parseFloat(total_usdt);

            total_usd = parseFloat(total_usd) + parseFloat(usd.attr("data-usd"));
        })
        $('.total_usd').text(total_usd);
        $('.total_btc').text(total_btc);
        $('.total_usdt').text(total_usdt);
        $('.total_eth').text(total_eth);
        $('.total_trx').text(total_trx);
        var options = {
            page: 8,
            pagination: true
        };
        if(total_usd > 0){
            new List('table_investment', options);
        }      
    }

    let tableWithdraw = $(".table_withdraw");
    if (tableWithdraw.length > 0) {
        let rowTable = tableWithdraw.find('tbody tr');
        let total_usd = 0, total_usdt = 0, total_btc = 0, total_eth = 0, total_qtc = 0, total_trx = 0;
        rowTable.each(function() {
            flask_moment_render_all();
            let ths = $(this);            
            let $date = ths.find(".flask-moment");
            $date.css("display","block");
            let usd = ths.find('.amount_usd');
            let currency = ths.find('.amount_coin').attr("data-currency");
            let amount_coin = ths.find('.amount_coin').attr("data-amount_coin");
            
            let statoshi_to_coin = parseFloat(amount_coin)/100000000
            currency == "BTC" ? 
                total_btc = parseFloat(statoshi_to_coin) + parseFloat(total_btc)
            : currency == "ETH" ? 
                total_eth = parseFloat(statoshi_to_coin) + parseFloat(total_eth)
                : currency == "TRX" ? 
                total_trx = parseFloat(statoshi_to_coin) + parseFloat(total_trx)
                : currency == "QTC" ?
                total_qtc = parseFloat(statoshi_to_coin) + parseFloat(total_qtc) 
                : total_usdt = parseFloat(statoshi_to_coin) + parseFloat(total_usdt);

            total_usd = parseFloat(total_usd) + parseFloat(usd.attr("data-usd"));
        })
        $('.total_usd').text(total_usd.toFixed(2));
        $('.total_btc').text(total_btc);
        $('.total_usdt').text(total_usdt);
        $('.total_eth').text(total_eth);
        $('.total_trx').text(total_trx);
        $(".total_qtc").text(total_qtc);
        var options = {
            page: 8,
            pagination: true
        };
        if(total_usd > 0){
            new List('table_withdraw', options);
        }      
    }



});
const confirmPayment = (id) => {

    Pub.confirm('Confirm payment', `Are you sure?`,
        (cb) => {
        var params = {
            id: id
        }
        Pub.post(`/admin-management-page/pay-withdraw/${id}`, params, function (ret, err) {
            if (ret.success == 1) {
                setTimeout(function () {
                    location.reload()
                }, 2000);
                Pub.toast('Success', 'success');
            }
            else {
                Pub.toast(ret.msg, 'fail');
            }
        }, (e) => {
        Pub.toast('Error! Please try again', 'fail');
        })
    },(cancel)=>{
        return Pub.toast('Cancel', 'fail');
    })
}

const confirmPaymentProfit = (id) => {

    Pub.confirm('Confirm payment', `Are you sure?`,
        (cb) => {
        var params = {
            id: id
        }
        Pub.post(`/admin-management-page/pay-withdraw-profit/${id}`, params, function (ret, err) {
            if (ret.success == 1) {
                setTimeout(function () {
                    location.reload()
                }, 2000);
                Pub.toast('Success', 'success');
            }
            else {
                Pub.toast(ret.msg, 'fail');
            }
        }, (e) => {
        Pub.toast('Error! Please try again', 'fail');
        })
    },(cancel)=>{
        return Pub.toast('Cancel', 'fail');
    })
}

const changeStatusKyc = (id, type) => {

    Pub.confirm('Confirm', `Are you sure?`,
        (cb) => {
        var params = {
            id: id,
            type: type
        }
        Pub.post(`/admin-management-page/update-kyc/${id}`, params, function (ret, err) {
            if (ret.success == 1) {
                setTimeout(function () {
                    location.reload()
                }, 2000);
                Pub.toast('Success', 'success');
            }
            else {
                Pub.toast(ret.msg, 'fail');
            }
        }, (e) => {
        Pub.toast('Error! Please try again', 'fail');
        })
    },(cancel)=>{
        return Pub.toast('Cancel', 'fail');
    })
}

const add_noted_kyc = (id) => {
    $('#note_id').val(id);
    $('#add_noted').modal('show');
}