function toLogin(){
    window.location.href="/signin";
}
function toRegister(){
    window.location.href="/signup";
}
Do.ready(function(){
    $('#getvcode').click(function(event) {
		if($('#mobile').val().length > 0){
			$.ajax({
				'url' : '/ajax/vcode?mobile=' + $('#mobile').val() + '&rt='+ Math.floor((Math.random()*100)+1),
				'type' : 'GET',
				'cache' : false,
				'dataType' : 'json',
				'success' : function(result) {
					if(result.status)
					{
						alert('发送成功');
					} else {
						alert('发送失败');
					}
				}
   			 });
		}else{
			alert('请填写手机号');
			$('#mobile').focus();
		}
    return false;
    });
});