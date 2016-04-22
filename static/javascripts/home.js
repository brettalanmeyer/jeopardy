$(function(){

	page("/home/");

	click(".home-option", function(){
		var source = $(this);
		var type = source.data("type");

		entity = type;

		switch(type){
			case "board":
				page("/board/");
				break;
			case "host":
				page("/host/");
				break;
			case "player":
				page("/player/");
				break;
		}
	});

});
