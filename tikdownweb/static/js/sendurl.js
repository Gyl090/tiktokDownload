
// 获取url发送下载链接到后端的ajax请求
function postUrl(){
    const url = document.getElementById("url").value;
    console.log(url)
    const link = {'msg':url}
    alert("请稍等...")
    $.ajax({
        url:"http://127.0.0.1:5001/download",
        type:"POST",
        dataType: "",
        data: JSON.stringify(link),
        contentType:'application/json;charset=utf-8',
        success: function (){
            alert("已下载完成，点击-保存本地-即可")
        }
    })
}

