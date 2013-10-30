/**
 * Created with JetBrains WebStorm.
 * User: szq
 * Date: 13-8-5
 * Time: 下午10:49
 * To change this template use File | Settings | File Templates.
 */
var Sys = {};
var ua = navigator.userAgent.toLowerCase();
var s;
(s = ua.match(/msie ([\d.]+)/)) ? Sys.ie = s[1] :
    (s = ua.match(/firefox\/([\d.]+)/)) ? Sys.firefox = s[1] :
        (s = ua.match(/chrome\/([\d.]+)/)) ? Sys.chrome = s[1] :
            (s = ua.match(/opera.([\d.]+)/)) ? Sys.opera = s[1] :
                (s = ua.match(/version\/([\d.]+).*safari/)) ? Sys.safari = s[1] : 0;
Do.add('DD_belatedPNG', {
    path: 'http://static.hualongxiang.com/lib/DD_belatedPNG.js',
    type: 'js'
});
Do.ready(function(){
    var timeout;
    $('#iammember').mouseenter(function(){
        $('#orderlist').show();
    }).mouseleave(function(){
        $('#orderlist').hide();
    });
    $('.dropdown-toggle').on('mouseenter',function(){
        $(this).closest('.dropdown').addClass('open');
    })
    $('.dropdown-toggle').on('mouseleave',function(){
        var _this = $(this);
        timeout = setTimeout(function(){
            _this.closest('.dropdown').removeClass('open');
        },10)
    })
    $('.dropdown-menu > li').mouseenter(function(){
        clearTimeout(timeout);
        $('.dropdown-toggle').unbind();
    })
    $('.dropdown-menu').mouseleave(function(){
        clearTimeout(timeout);
        $(this).closest('.dropdown').removeClass('open');
        $('.dropdown-toggle').on('mouseenter',function(){
            $(this).closest('.dropdown').addClass('open');
        })
        $('.dropdown-toggle').on('mouseleave',function(){
            var _this = $(this);
            console.log(_this);
            timeout = setTimeout(function(){
                _this.closest('.dropdown').removeClass('open');
            },10)
        })
    })

    $.extend({
        login: function () {
            if($('#formforlogin').is(":visible")){$('#formforlogin').hide();};
            var top;
            Sys.chrome ? top=document.body.scrollTop+window.screen.height/4 : top=document.documentElement.scrollTop+window.screen.height/4;
            var left = (document.body.clientWidth - 650) / 2;
            /*var loginhtml = '<form action="/signin" method="post"><div class="global_popwinwapper r5" id="formforlogin" style="display: none;">'
            + '<div class="global_popwin clearfix">'
                + '<div class="blank20"></div>'
                + '<div class="global_pop_title login"><a class="cp close_pop fr mr20 fs14">关闭</a></div>'
                + '<div class="blank20"></div>'
                + '<div class="pop_form">'
                    + '<div class="login_form">'
                        + '<div class="item">'
                            + '<span>帐号：</span><input type="text" name="uname" class="fl">'
                        + '</div>'
                            + '<div class="item">'
                               + '<span>密码：</span><input type="password" name="upasswd" class="fl">'
                            + '</div>'
                                + '<div class="item">'
                                    + '<span>&nbsp;</span><a class="oc fs14">忘记密码</a>'
                                + '</div>'
                                + '<div class="itembut">'
                                    + '<span>&nbsp;</span><input type="button" class="titico bsbut" value="登陆">'
                                + '</div></form>'
                                    + '<div class="blank10"></div>'
                                    + '<div class="itemword">'
                                        + '<p class="fs14">使用合作网站帐号登陆</p>'
                                        + '<a class="global_pop_title xinlang">新浪</a><a class="global_pop_title zhifubao ml20">支付宝</a>'
                                    + '</div>'
                                + '</div>'
                                + '<div class="link_form">'
                                    + '<p class="oc mb20">还没有吉米的厨房的账户？ </p>'
                                    + '<p><input type="button" class="titico sbut" onclick="$.register();" value="免费注册"></p>'
                                    + '</div>'
                                    + '<div class="blank20"></div>'
                                + '</div>'
                            + '</div>'
                        + '</div>';
            $('body').append(loginhtml);*/
            $('#formforlogin').css({'top': top,'left': left}).show();
        },
        register: function () {
            //if($('.global_popwinwapper').length > 0){$('.global_popwinwapper').remove();};
            if($('#formforregister').is(":visible")){$('#formforregister').hide();};
            var top;
            Sys.chrome ? top=document.body.scrollTop+window.screen.height/4 : top=document.documentElement.scrollTop+window.screen.height/4;
            var left = (document.body.clientWidth - 650) / 2;
            /*var loginhtml = '<div class="global_popwinwapper r5" id="formforregister" style="display: none;">'
                + '<div class="global_popwin clearfix">'
                + '<div class="blank20"></div>'
                + '<div class="global_pop_title register"><a class="cp close_pop fr mr20 fs14">关闭</a></div>'
                + '<div class="blank20"></div>'
                + '<div class="pop_form">'
                + '<div class="login_form">'
                + '<div class="item">'
                + '<span>手机号码：</span><input type="text" name="uname" class="fl">'
                + '</div>'
                + '<div class="item">'
                + '<span>设置密码：</span><input type="password" name="upasswd" class="fl">'
                + '</div>'
                + '<div class="item">'
                + '<span>确认密码：</span><input type="password" name="repasswd" class="fl">'
                + '</div>'
                + '<div class="item">'
                + '<span><input type="checkbox" checked></span><a class="oc fs12 agree">同意《吉米的厨房的购物协议》</a>'
                + '</div>'
                + '<div class="itembut">'
                + '<span>&nbsp;</span><input type="button" class="titico bsbut" value="注册">'
                + '</div>'
                + '</div>'
                + '<div class="link_form">'
                + '<p class="oc mb20">已有吉米的厨房的账户？ </p>'
                + '<p><input type="button" class="titico sbut" onclick="$.login();" value="登陆"></p>'
                + '<p class="mt20">或使用合作网站帐号登录</p>'
                + '<p class="mt5"><a class="global_pop_title xinlang">新浪</a><a class="global_pop_title zhifubao ml20">支付宝</a></p>'
                + '</div>'
                + '<div class="blank20"></div>'
                + '</div>'
                + '</div>'
                + '</div>';
            $('body').append(loginhtml);*/
            $('#formforregister').css({'top': top,'left': left}).show();
        }
    })
    $('.close_pop').live('click',function(){
        $(this).parents('.global_popwinwapper').hide();
    })
    /*$('.formforlogin').click(function(e){
        e.preventDefault()
        e.stopPropagation()
        $.login();
    })
    $('.formforregister').click(function(e){
        e.preventDefault()
        e.stopPropagation()
        $.register();
    })*/
	$('.increase').click(function(){
		$(this).siblings('input').val(parseInt($(this).siblings('input').val()) + 1);
		$(this).siblings('input').trigger('change');
	})
	$('.decrease').click(function(){
		var v = parseInt($(this).siblings('input').val()) - 1;
		v > 1 ? v : v = 1;
		$(this).siblings('input').val(v);
		$(this).siblings('input').trigger('change');
	})
	if($('#area').length > 0 ) {
		var areas = [];
		$.ajax({
			url:'/ajax/areas',
			type:'GET',
			dateType:'json',
			success:function(data){
				areas = eval(data);
				var html = "";
				for(i in areas){
					if(areas[i].pid == 0){
						html += '<option value="' + areas[i].name + '" rel="' + areas[i].id + '">' + areas[i].name + '</option>';
					}
				}
				$('#area').html(html);
				$('#area').trigger('change');
			}
		})
		$('#area').live('change',function(){
			var id = $(this).find("option:selected").attr('rel');
			var html = "";
			for(i in areas){
				if(areas[i].pid == id){
					html += '<option value="' + areas[i].name + '">' + areas[i].name + '</option>';
				}
			}
			if( $('#region').length > 0 ){
				$('#region').html(html);
			}else{
				html = '<select name="region" id="region">' + html + '</select>';
				$(this).after(html);
			}
			
		})
	}
	
})