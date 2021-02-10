 $(document).ready(function(e){
 	var csrf_token = "{{ csrf_token() }}";

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    $("#btn").click(function (){
    	$.getJSON("http://localhost:5000/title/"+$("#query").val(), {}, function (data){

    		var cont = '<table class="table">  ' +
				'<thead>' +
				'    <tr>' +
				'      <th scope="col">Название</th>' +
				'      <th scope="col">Автор</th>' +
				'      <th scope="col">ISBN</th>' +
				'      <th scope="col">Фото</th>' +
				'      <th scope="col">Ссылка</th>' +


				'    </tr>' +
				'  </thead> <tbody>'

			$.each(data, function(i, item) {
				console.log(item.author)
				cont += '<tr><th>' + item.title +'</th> <th>' + item.author +'</th> <th>' + item.isbn +'</th> <th><img src="' + item.img +'"></img></th> <th><a href="' + item.url +'">Cсылка</a></th></tr>';
			});
    		cont+="</tbody></table>"
			$('#container').empty();
			$('#container').append(cont);


		})
	});



});
