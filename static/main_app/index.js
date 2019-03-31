function getHashParams() {
  var hashParams = {};
  var e, r = /([^&;=]+)=?([^&;]*)/g,
      q = window.location.hash.substring(1);
  while ( e = r.exec(q)) {
     hashParams[e[1]] = decodeURIComponent(e[2]);
  }
  return hashParams;
}

function getMemberNames() {
  var members = [];
  for(i = 0; i < $('.membername').length; i++) {
    members.push($('.membername')[i].value)
  }
  return members;
}

var params = getHashParams();
console.log(params)

list = $(".list-group")
$(".list-group").empty()

if(params.step == 2) {
  $('.carousel').carousel('next');
  track_names = params.names.split(',')
  // console.log(track_names)
  for(i = 0; i < track_names.length; i++) {
    list.append(`<a id="2" class="nxt next_button list-group-item list-group-item-action">` + track_names[i] + '</a>')
  }
}
else if(params.step == 3) {
  $('.carousel').carousel('next');
}

$('.next_button').click(function() {
  if($(this)[0].id == 1) {
    document.location.href='/login';
    // $('.carousel').carousel('next');
  }
  else if($(this)[0].id == 2) {
    var request = $.ajax({
        url: '/next/',
        type: 'POST',
        data: { 
          name: $(this)[0].innerHTML,
          members: getMemberNames().join(',')
        }
    });
  }
})

$('.add_button').click(function() {
  member_div = $('#member_div');
  member_div.append('<input style="margin-bottom:10px;border-color:green" type="text" placeholder="Member name" class="form-control input-md membername" style="display: inline; width: 70%">')
})