(function($) {
    jQuery.fn.show_tree = function(node) {      
               
        positon = node.iconCls.split(" ");

        var line_class = positon[1] + 'line ' + 'linefloor' + node.fl;
        var level_active = positon[0] + 'iconLevel';

        var node_class = positon[1] + '_node ' + 'nodefloor' + node.fl+ ' '+node.level+'_tresss';
        var html = `<div class="${line_class}"></div>`;       
       
        html += !node.empty ?
            `<div class="${node_class} ${level_active}">
                <a class="data-detail">
                    <i class="fa fa- type-${node.level}" onclick="click_node('${node.id}')" value="${node.id}" aria-hidden="true"></i>
                    <div class="__info">
                        <p class="title">${node.name}</p>
                        <p class="_flex">
                            <span>Sponsor:</span>
                            <strong>${node.sponsor}</strong
                        </p>
                        <p class="_flex">
                            <span>Invested:</span>
                            <strong>${node.invest} <sup>$</sup></strong
                        </p>
                        <p class="_flex">
                            <span>Total Left:</span>
                            <strong>${node.team_left} <sup>$</sup></strong
                        </p>
                        <p class="_flex">
                            <span>Total Right:</span>
                            <strong>${node.team_right} <sup>$</sup></strong
                        </p>
                    </div>
                </a>
            <span class="name_node">${node.name}</span>` :
            `<div class="${node_class}">
                <a  data-toggle="tooltip" data-placement="bottom" style="display:block" onclick="click_node_add('${node.p_binary}', '${positon[1]}')" value="${node.p_binary}" >
                    <i class="fa fa-plus-square type-add"></i>
                </a>
                <span class="name_node">ADD TREE</span>`;

        html += `<div id="${node.id}" ></div>`;

        html += '</div>';

        $(this).append(html);
        node.children && $.each(node.children, function(key, value) {

            $('#' + node.id).show_tree(value);
        });


    };
    jQuery.fn.show_infomation = function(node) {

    };
    jQuery.fn.build_tree = function(id, method) {
        let params = {'id_user': id}
        Pub.post(`/account/json_tree`, params, function (ret, err) {
                $('.personal-tree').html('');
                $('.personal-tree').show_tree(ret);
        }, (e) => {
            Pub.toast('Error! Please try again', 'fail');
        })

    };
})(jQuery);

function notice(msg, color = '007eff', time = 3000) {
        return new Promise((resolve, reject) => {
            let wrap = $('<div style="position:fixed; left:calc(50% - 150px); box-shadow:0 5px 25px rgba(0,0,0,0.2); width:320px; top:40px; background:#' + (color ? color : '007eff') + '; border-radius:10px; color:#fff; padding:20px 20px; font:14px/1.2 Tahoma, sans-serif; cursor:pointer; z-index:999999; text-align:center;">' + msg + '</div>')
                .on('click', () => { wrap.remove(); resolve(); })
                .appendTo('body');
            if(time) setTimeout(() => { wrap.remove(); }, time);
        });
}
function check_node(p_binary, positon){
    var posting = $.post( '/account/check-node', { p_binary,  positon} );
    posting.done(function( data ) {
        if(data.success){
            let p_node = $('#__username').val();
            window.location.href = `/auth/signup/${p_node}/${p_binary}_${positon == "left" ? 0 : 1}`;
            /*window.open(`/auth/signup/${p_node}/${p_binary}_${positon == "left" ? 0 : 1}`, '_blank');*/
        }else{
            notice("You cannot add to this position. Please choose the outermost position",'f90')
        }
    });
}

function click_node_add(p_binary, positon) {
    check_node(p_binary, positon) 
    let p_node = $('#__username').val();
    // window.open(`/auth/signup/${p_node}/${p_binary}_${positon == "left" ? 0 : 1}`, '_blank');
};


function click_node(id) {

    jQuery(document).build_tree(id, 'getJsonBinaryTree_Admin');
    $('.tooltip').hide();
    !_.contains(window.arr_lick, id) && window.arr_lick.push(id);    
}
window.arr_lick = [];

function click_back() {
    if (window.arr_lick.length === 0) {
        click_node($('#uid_customer').val());
    } else {
        window.arr_lick = _.initial(window.arr_lick);
        typeof _.last(window.arr_lick) !== 'undefined' ? click_node(_.last(window.arr_lick)) : click_node($('#uid_customer').val());
    }
}

function upto_level(id) {
    var top = jQuery('.personal-tree' + id + ' > div a').eq(0).attr('value');
    jQuery(document).build_tree(top, 'getJsonBinaryTreeUplevel');
}

function goto_bottom_left(id) {
    jQuery(document).build_tree(id, 'goBottomLeft');
}

function goto_bottom_right(id) {
    jQuery(document).build_tree(id, 'goBottomRight');
}

function goto_bottom_left_oftop(id) {
    var top = jQuery('.personal-tree' + id + ' > div a').eq(0).attr('value');
    jQuery(document).build_tree(top, 'goBottomLeft');
}

function goto_bottom_right_oftop(id) {
    var top = jQuery('.personal-tree' + id + ' > div a').eq(0).attr('value');
    jQuery(document).build_tree(top, 'goBottomRight');
}



jQuery(document).ready(function($) {
    click_node($('#uid_customer').val());
});

