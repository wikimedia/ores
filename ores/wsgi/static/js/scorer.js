function getParameterByName(name) {
	name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
	var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
	results = regex.exec(location.search);
	return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function error(msg) {
	var htm = '<div class="ui negative message"><div class="header">We\'re sorry. ORES returned the following error:</div><p>' + msg +'</p></div>';
	return htm;
}

function wikis() {
	$.get('/scores/', function (data) {
		var wikis = data.contexts;
		for (i = 0; i < wikis.length; i++) {
			$('#wikis').append('<div class="item">' + wikis[i] + '</div>');
		}
	});
}

function enableResult() {
	$('#resultButton').attr('class', 'positive ui button');
}
function createTable(data) {
	var htm = '<table class="ui sortable celled table"><thead><tr><th>Wiki</th><th>Model</th><th>Revision ID</th><th>Value</th><th>Score</th></tr></thead>';
	var revids = Object.keys(data);
        if (data.error) {
            return error(data.error.message);
        }
	for (i = 0; i < revids.length; i++) {
                if (data[revids[i]].error) {
                     return error(data[revids[i]].error.message);
		}
		var models = Object.keys(data[revids[i]]);
		for (j = 0; j < models.length; j++) {
                        if (data[revids[i]][models[j]].error) {
				return error(data[revids[i]][models[j]].error.message);
			}
			var outcomes = Object.keys(data[revids[i]][models[j]]["probability"]);
			for (k = 0; k < outcomes.length; k++) {
				htm += '<tr><td>'+$('#wikiDropDownInput').attr('value')+'</td><td>'+models[j]+'</td><td>'+revids[i]+'</td><td>'+outcomes[k]+'</td><td>'+data[revids[i]][models[j]]["probability"][outcomes[k]]+'</td></tr>';
			}
		}
	}
	htm += '</tbody></table>';
	return htm;
}
function loadModels() {
	$('#loading_div').show();
	$.get('/scores/' +  $('#wikiDropDownInput').attr('value') + '/', function(data) {
		$('#modelDropDown').attr('class', 'ui fluid multiple selection dropdown');
		var models = Object.keys(data.models);
		var htm = '<div class="menu">';
		for (i = 0; i < models.length; i++) {
			htm += '<div class="item">' + models[i] + '</div>';
		}
		htm += '</div>';
		$('#modelDropDown').html($('#modelDropDown').html() + htm);
		$('#modelDropDown').dropdown();
		$('#revIds').attr('class', "ui input");
		$('#addMore').attr('class', "ui button");
		$('#loading_div').hide();
	}, "json");
}

function getResults() {
	$('#loading_div').show();
	var revs = '';
	$('.ui.input input').each(function( index ) {
		revs += $(this).val() + '|';
	});
	revs = revs.slice(0, -1);
	var models_url = $('#modelDropDownInput').attr('value').replace(/,/g,'|');
	var url = "/scores/" + $('#wikiDropDownInput').attr('value') + "/?models=" + models_url + "&revids=" + revs;
	$.get(url, function (data) {
		if ($('.table').length) {
			$('.table').html(createTable(data));
		} else {
			$('#resultButton').after(createTable(data));
		}
		$('#loading_div').hide();
		$('.sortable.table').tablesort();
	});
}

wikis();
$('#loading_div').hide();
$('.ui.dropdown').dropdown();
$('#wikiDropDown').change(function() {
	loadModels();
});
$('#addMore').click(function() {
	$('#addMore').last().before('<div class="ui input" id="revIds"><input type="text" placeholder="Insert revid..."></div>');
});
$('#modelDropDown').change( function() {
	$('.ui.input input').change( function() {
		enableResult();
	});
});
$('.ui.input input').change( function() {
	$('#modelDropDown').change( function() {
		enableResult();
	});
});
$('#resultButton').click(function() {
	getResults();
});
if (getParameterByName('wiki')) {
	$(function(){
		var wiki = getParameterByName('wiki');
		$('#wikiDropDownInput').attr('value', wiki);
		$('#defaultWiki').attr('class', 'text');
		$('#defaultWiki').html(wiki);
		loadModels();
	});
}

if (getParameterByName('revids')) {
	$(function(){ setTimeout( function() {
		$('#revIds').remove();
		var htm = '';
		var rev_ids = getParameterByName('revids').split('|');
		for (i = 0; i < rev_ids.length; i++) {
			htm += '<div class="ui input\", id="revIds"><input type="text" placeholder="Insert revid..." value="';
			htm += rev_ids[i] + '"></div>';
		}
		$('#addMore').before(htm)}, 3000);
	});
}

if (getParameterByName('models')) {
	var url_models = getParameterByName('models').split('|');
	$(function(){ setTimeout( function() {
		$('.ui.fluid.dropdown').dropdown('set selected', url_models) }, 3000);
	});
}

if (getParameterByName('wiki') && getParameterByName('revids') && getParameterByName('models')) {
	if ( getParameterByName( 'go' ) ) {
		$(function(){ setTimeout( function() { getResults() }, 3000) });
	}
	$(function(){ setTimeout( function() {
		$('#resultButton').attr('class','positive ui button') }, 3000);
	});
}
