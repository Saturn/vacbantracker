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


const trackProfile = (e) => {
  const row = $(e.target).parent().parent()
  const steamid = row.data('steamid');
  const note = '';
  const data = {steamid: steamid,
                note: note};
  $.post('/track', data, () => trackSuccess(row));
};


const trackSuccess = (row) => {
  console.log(row)
};


$('.track-button').bind("click", trackProfile);

window.makeFlash = makeFlash;
window.clearFlashes = clearFlashes;
