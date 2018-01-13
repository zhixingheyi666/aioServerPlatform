//通过javascript脚本实现获取table的父元素的宽度。
$(window).resize(function () {
    var twidth = $('#thin-padding').width();
    $('#thin-padding table').width(twidth);
});

//文档加载完毕执行
$(document).on('ready', function () {

    var twidth = $('#thin-padding').width();
    $('#thin-padding table').width(twidth);

    //关键字着色
    $('[id^=LC]').each(function () {
        var keyP = $('#keywords p');
        if (keyP) {
            console.log(keyP);
            var former = $(this).html();
            // 取得 分词 后的 关键词，并构造正则字串
            var keywords = '';
            for (i = 0; i < keyP.length; i++) {
                keywords = keywords + $(keyP[i]).text() + '|';
            }
            keywords = keywords.substring(0, keywords.length - 1);
            // $(this).css('color','white').css('background-color','#204B56');
            var reI = new RegExp(keywords, 'g');
            // repalce 函数中 $& 代表与正则相匹配的字串
            var line = former.replace(reI, "<span class='theme-keyword'>$&</span>");
            $(this).html(line);
        }
        console.log('No keywords');

    });
});

/*
    $('.col-md-4 form').on('submit', function (event) {
        console.log(event.type);
        alert('(Bubble stage)The event type of this Form:  ' + event.type);
        alert('succeed!');
    });

   $('#form').on('submit', function(e) {
       e.preventDefault();
       var data = $('form').serialize();
       alert('Form will be submitted');
       jQuery.get('/', data );
   });
测试1，OK
           $('button').on('click',function (event) {
               event.preventDefault();
               console.log(event.type);
               alert(event.type);
               alert('submit!');
           });
测试2，OK
           $('#testForm').on('click',function (event) {
               event.preventDefault();
               console.log(event.type);
               alert(event.type);
               alert('submit!');
           });
测试3，OK
       $('.col-md-4 form [type=submit]').click(function (event) {
           alert('(Bubble stage)The event type of this Button:  ' + event.type);
           alert('You have clicked this submit button and the Form will be submitted soon.')
       });

       changeStatus = function (event) {
           alert(event.type + ' event on Checkbox has being triggerd.')
       }
       $('[type=checkbox]').click(function (event) {
           changeStatus(event);
       });

*/
