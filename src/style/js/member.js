/**
 * Created with JetBrains WebStorm.
 * User: szq
 * Date: 13-8-4
 * Time: 下午2:49
 * To change this template use File | Settings | File Templates.
 */
Do(function(){
    $('.selectdiv').click(function(){
        var id = $(this).attr('rel');
        $('#'+id).addClass('on');
    })
    $('#sel_relation li').click(function(){
        $('#sel_relation li').show();
        $(this).hide();
        $(this).parent('ul').siblings('em').html($(this).text());
        $('#sel_relation').removeClass('on');
        $(this).parent('ul').siblings('input').val($(this).attr('rel'));

    })
    $(document).bind('click', function (e) {
        if ($(e.target).parents('.selectdiv').length || $(e.target).attr('class') == 'selectdiv') {} else {
            $('.selectdiv').find('ul').removeClass('on');
        }
    })
})