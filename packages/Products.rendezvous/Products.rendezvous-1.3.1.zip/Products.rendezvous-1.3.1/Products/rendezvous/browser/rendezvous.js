
var rendezvous = {};


rendezvous.init = function(){
	jq('.template-edit_dates').each(rendezvous.initchoicesselection);
	jq('.template-rendezvous_view').each(rendezvous.inituserchoice);
	jq('#rendezvous-choose-date').click(rendezvous.startdatechoice);
}

rendezvous.initchoicesselection = function(){
	jq('#rendezvous-dates-select a.calendar-date').click(function(){
		/* first submit the form in case it has been modified */
		var formData = jq('form#rendezvous-edit').serialize();
		var formAction = jq('form#rendezvous-edit').attr('action');
		jq.post(formAction, formData, function(){})
	});
}

rendezvous.inituserchoice = function(){
	jq('td.selectable').click(rendezvous.toggleuserchoice)
}

rendezvous.toggleuserchoice = function(){
	var cell = jq(this);
	var input = cell.children('input');
	var span = cell.children('span');
	if(input.attr('value') == ''){
		/* select value */
		cell.removeClass('unavailable');
		cell.removeClass('unknown');
		cell.addClass('available');
		input.attr('value', input.attr('id'));
		span.html('OK');
	}
	else{
		/* unselect value */
		cell.removeClass('available');
		cell.addClass('unavailable');
		input.attr('value', '');
		span.html('');
	}
}

rendezvous.startdatechoice = function(){
	jq('body').css('cursor', 'pointer');
	jq('.rendezvous-datechoice').css('color', 'blue');
	jq('#rendezvous').click(rendezvous.enddatechoice);
	jq('.rendezvous-datechoice').click(rendezvous.selectdatechoice);
}

rendezvous.enddatechoice = function(){
	jq('body').css('cursor', 'default');
	jq('#rendezvous').unbind('click');
	jq('.rendezvous-datechoice').removeAttr('style');
}

rendezvous.selectdatechoice = function(){
	var base_url = jq('base').attr('href');
	var date = jq(this).attr('class').split(' ')[1];
	window.location.href = base_url + '@@rendezvous_create_event?date=' + date;
}
jq(document).ready(rendezvous.init);