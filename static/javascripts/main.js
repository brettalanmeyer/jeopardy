
var hasHost = false;
var hasBoard = false;
var hasPlayers = false;
var entity = $("input[name=entity]").val();

if(entity == "board"){
	page("board");
} else if(entity == "host"){
	page("host");
} else if(entity.startsWith("player")){
	page("player");
}

var socket = io.connect("http://" + document.domain + ':' + location.port);

socket.on("receive-main-entity", function(data){
	console.log(data);
	if(data.hasBoard){
		$(".home-option[data-type=board]").remove();
	}
	if(data.hasHost){
		$(".home-option[data-type=host]").remove();
	}
	if(data.hasPlayer1 || data.hasPlayer2 || data.hasPlayer3){
		$(".home-option[data-type=player]").first().remove();
	}
});

socket.on("receive-reset", function(data){
	window.location = "/reset/";
});

function page(url){
	return $.get(url).done(function(result){
		$("#body").html(result);
	});
}

function click(el, func){
	$("#body").on("click", el, func);
}

function post(el, func){
	$("#body").on("submit", el, function(){
		var source = $(this);
		$.post(source.attr("action"), source.serialize()).done(func);
		return false;
	});
}
