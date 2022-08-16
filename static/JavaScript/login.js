
function checkLogon(){
  var name = document.getElementById("uname").value;
  var pass = document.getElementById("psw").value;
  if(name=="123" && pass=="123"){
       alert("登录成功！");
       //这里写你页面跳转的语句
       // {#window.location.href="https://dengxj.blog.csdn.net/";#}
          // {#"http://127.0.0.1:5000/portrait/";#}
  }
  else{
        alert("用户名或密码错误！！");
  }
}
