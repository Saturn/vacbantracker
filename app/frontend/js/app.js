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


const trackProfile = (steamid, note) => {
  $.post('/track',
         {steamid: steamid,
          note: note},
         () => window.location.reload());
};


const untrackProfile = (steamid) => {
  $.post('/untrack',
         {steamid: steamid},
         () => window.location.reload());
};


const trackProfileButton = (e) => {
  const button = $(e.target);
  const steamid = button.data('steamid');
  const note = $('.tracking-note').text();
  trackProfile(steamid, note);
};


const untrackProfileButton = (e) => {
  const button = $(e.target);
  const steamid = button.data('steamid');
  untrackProfile(steamid);
};


const trackProfileModal = (e) => {
  const button = $(e.target);
  const personaname = button.data('personaname');
  const steamid = button.data('steamid');
  $('#trackModalTitle').text('Track ' + personaname);
  const modal = $('#trackModal');
  const note = $('#track-note').val();
  $('#track-modal-btn').click(() => trackProfile(steamid, note));
  modal.modal();
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
  $('#unTrack-modal-btn').click(() => untrackProfile(steamid));
  modal.modal()
};


$('.track-button').bind("click", trackProfileModal);
$('.untrack-button').bind("click", unTrackProfileModal);
$('.track-button-profile').bind("click", trackProfileButton);
$('.untrack-button-profile').bind("click", untrackProfileButton);

window.makeFlash = makeFlash;
window.clearFlashes = clearFlashes;
