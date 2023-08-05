$(function() {
    $('.application').each(function(i, app) {
        console.log($(app).data('name') + " " + $(app).data('group') + " " + $(app).data('version'));
        $('.command', app).each(function(j, com) {
            console.log('\t' + $(com).data('queue'));
        });
    });
})

function action_url(node) {
  var self = $(node);
  var action = self.data('action');
  var params = {};
  var app = self.parents('.application');
  params.name = app.data('name');
  params.group = app.data('group');
  params.version = app.data('version');
  var action = $(node).data('action');
  if($(node).data('fail-id')) {
      params.fail_id = $(node).data('fail-id');
  }
  if($(node).data('type') === 'command') {
      params.queue = self.parents('.command').data('queue');
  }
  return action + '?' + $.param(params);
}

$('.close-button').live('click', function(event){
    event.preventDefault();
    $(this).parents('form').toggle();
});

$('.action').live('click', function(event) {
  event.preventDefault();
  var url = action_url(this);
  $.get(url);
});


$('.link-action').live('click', function(event){
    event.preventDefault();
    var url = action_url(this);
    window.open(url, $($(this).attr('target'), $(this).parents('.toggle-elem')));
})

$('.confirm-action').live('click', function(event) {
    event.preventDefault();
    var self = this;
    var url = action_url(self);
    if(confirm($(self).data('message'))) {
        $.get(url, function(){
            alert('removed');
            $(self).parents('.application').remove();
        })
    } 
});

$('#failed .remove, #failed .requeue').live('click', function(e) {
    var tr = $(this).parents('tr')
    var fid = tr.data('fid');
    $('.'+fid).remove();
});

$('.toggle').live('click', function(event) {
    $($(this).data('target')).toggle();
});
