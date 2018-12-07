import 'bootstrap';
import $ from 'jquery';
window.jQuery = $;
window.$ = $;


const makeFlash = (message, category) => {
  category = (typeof category === 'undefined') ? 'secondary' : category;
  $(".flashes").append(`<div class="alert alert-${category} alert-dismissible fade show" role="alert">
    ${message}
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
      <span aria-hidden="true">&times;</span>
    </button>
  </div>`);
};


const clearFlashes = () => {
  $(".flashes").html("");
};


const trackProfileModal = (e) => {
  const button = $(e.target);
  const personaname = button.data('personaname');
  const steamid = button.data('steamid');
  $('#trackModalTitle').text('Track ' + personaname);
  const modal = $('#trackModal');
  $('#track-modal-btn').click((data) => {
    data = {
      steamid: steamid,
      note: $('#track-note').val()
    }
    $.post('/track', data, () => window.location.reload());
  });
  modal.modal()
};


const unTrackProfileModal = (e) => {
  const button = $(e.target)
  const personaname = button.data('personaname');
  const steamid = button.data('steamid');
  let note = button.data('note');
  note = note === '' ? 'None' : note;
  $('#untrack-note').text(note);
  $('#unTrackModalTitle').text('Stop tracking ' + personaname + '?');
  const modal = $('#unTrackModal');
  $('#unTrack-modal-btn').click((data) => {
    data = {
      steamid: steamid
    }
    $.post('/untrack', data, () => window.location.reload());
  });
  modal.modal()
};


$('.track-button').bind("click", trackProfileModal);
$('.untrack-button').bind("click", unTrackProfileModal);

window.makeFlash = makeFlash;
window.clearFlashes = clearFlashes;
