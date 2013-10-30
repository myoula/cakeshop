/**
 * Created with JetBrains WebStorm.
 * User: szq
 * Date: 13-8-5
 * Time: 下午10:12
 * To change this template use File | Settings | File Templates.
 */
Do(function(){
    (function($) {
        $('.player').mouseenter(function(){
            $(this).find('.play_b').show();
        }).mouseleave(function(){
                $(this).find('.play_b').hide();
        })
        var pmax = $("#playerbox li").length;
        var pnowindex = 0;
        var ptimeout;
        $('#play_r').click(function(){
            if( (pnowindex + 1) > (pmax - 1) ) {
                pnowindex = 0;
                $("#playerbox").animate({marginLeft:"0px"});
            }else{
                pnowindex = pnowindex + 1;
                $("#playerbox").animate({marginLeft: -pnowindex*960 + "px"});
            }
            if(ptimeout){clearInterval(ptimeout);}
        })
        $('#play_l').click(function(){
            if( (pnowindex - 1) < 0 ) {
                pnowindex = pmax - 1;
                $("#playerbox").animate({marginLeft: -pnowindex*960 + "px"});
            }else{
                pnowindex = pnowindex - 1;
                $("#playerbox").animate({marginLeft: -pnowindex*960 + "px"});
            }
            if(ptimeout){clearInterval(ptimeout);}
        })
        ptimeout = setInterval(function(){
            $('#play_r').trigger('click');
        },5000)
    })(jQuery);



})