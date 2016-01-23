function getParameterByName(name) {
	name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
	var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
	results = regex.exec(location.search);
	return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function error(msg) {
	var htm = '<div class="alert alert-danger" style="padding-top: 15px"><div class="header">We\'re sorry. ORES returned the following error:</div><p>' + msg +'</p></div>';
	return htm;
}

function wikis() {
	$.get('/scores/', function (data) {
		var wikis = data.contexts;
		for (i = 0; i < wikis.length; i++) {
			$('#wikis').append('<li><a>' + wikis[i] + '</a></li>');
		}
		$('#wikiDropDownInput').removeAttr('disabled');
		$('#wikisList li > a').click(function(e){
    			loadModels(this.innerHTML);
		});
	});
}

function enableResult() {
	$('#resultButton').removeAttr('disabled');
}
function createTable(data) {
	var htm = '<div class="col-md-6 col-md-offset-3" style="margin-top: 3em; margin-bottom: 3em;">';
	htm += '<table class="celled table sortable"><thead><tr><th>Wiki</th><th>Model</th><th>Revision ID</th>';
	htm += '<th>Value</th><th>Score</th></tr></thead>';
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
	htm += '</tbody></table></div>';
	return htm;
}
function loadModels(wiki) {
	$.get('/scores/' +  wiki + '/', function(data) {
		var htm = '<ul style="padding-top: 15px; padding-left: 0px" id="modelSelection"><h5>Select models</h5>';
		var models = Object.keys(data.models);
		for (i = 0; i < models.length; i++) {
			htm += '<li class="checkbox"><label><input type="checkbox" value="' + models[i] + '">' + models[i] + '</label></li>\n\n';
		}
		htm += '</ul>';
		if ($('#modelSelection').length) {
			$('#modelSelection').replaceWith(htm);
		} else {
			$('#wikisList').after(htm);
		}
		$('#revIds').removeAttr('disabled');
	}, "json");
	$('#wikiDropDownInput').html(wiki + '<wiki-icon icon="caret-down"></wiki-icon>');
	$('#wikiDropDownInput').attr('value', wiki);
}

function getResults() {
	var revs = $('#revIds').val().replace(',', '|');
	var models_url = '';
	$('input:checked').each(function() {
		models_url += $(this).val() + '|';
	});
	models_url = models_url.slice(0, -1);
	var url = "/scores/" + $('#wikiDropDownInput').attr('value') + "/?models=" + models_url + "&revids=" + revs;
	$.get(url, function (data) {
		if ($('.table').length) {
			$('.table').html(createTable(data));
		} else {
			$('#afterThis').after(createTable(data));
		}
		$('.sortable.table').tablesort();
	}, datatype='jsonp');
}

wikis();
$('#revIds').click( function() {
	enableResult();
});
$('#resultButton').click(function() {
	getResults();
});
if (getParameterByName('wiki')) {
	$(function(){
		loadModels(getParameterByName('wiki'));
	});
}

if (getParameterByName('revids')) {
	$(function(){ setTimeout( function() {
			$('#revIds').val(getParameterByName('revids').replace('|', ','));
		}, 3000);
	});
}

if (getParameterByName('models')) {
	var url_models = getParameterByName('models').split('|');
	$(function(){ setTimeout( function() {
		for (i = 0; i < url_models.length; i++) {
			$(':input[value="'+ url_models[i] + '"]').prop('checked', true);
		}
	}, 3000)});
}

if (getParameterByName('wiki') && getParameterByName('revids') && getParameterByName('models')) {
	if ( getParameterByName( 'go' ) ) {
		$(function(){ setTimeout( function() { getResults() }, 3000) });
	}
	$(function(){ setTimeout( function() {
		enableResult();
	}, 3000)});
}
