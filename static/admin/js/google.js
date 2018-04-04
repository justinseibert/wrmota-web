var map;
var google_site = {};
var audio = {};
var latest_track = null;
var latest_track_duration = 0;
var elem = {
  'map': document.getElementById('map')
};
function initMap() {
  var h = window.innerHeight;
  elem.map.style.height = h+'px';

  var styles = [
    {
      "featureType": "poi",
      "elementType": "labels.text",
      "stylers": [
        {
          "visibility": "off"
        }
      ]
    },
    {
      "featureType": "poi.business",
      "stylers": [
        {
          "visibility": "off"
        }
      ]
    },
    {
      "featureType": "road",
      "elementType": "labels.icon",
      "stylers": [
        {
          "visibility": "off"
        }
      ]
    },
    {
      "featureType": "transit",
      "stylers": [
        {
          "visibility": "off"
        }
      ]
    }
  ];
  var style_map = new google.maps.StyledMapType(styles);
  map = new google.maps.Map(elem.map, {
    center: {
      lat: 40.3358193,
      lng: -75.9466839
    },
    zoom: 17,
    zoomControl: true,
    mapTypeControl: false,
    mapTypeControlOptions: {
      mapTypeId: ['styled_map']
    },
  });
  map.mapTypes.set('styled_map', style_map);
  map.setMapTypeId('styled_map');

  var input = document.getElementById('map-search');
  var searchBox = new google.maps.places.SearchBox(input);
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

  // Bias the SearchBox results towards current map's viewport.
  map.addListener('bounds_changed', function() {
    searchBox.setBounds(map.getBounds());
  });

  var search_markers = [];
  // Listen for the event fired when the user selects a prediction and retrieve
  // more details for that place.
  searchBox.addListener('places_changed', function() {
    var places = searchBox.getPlaces();

    if (places.length == 0) {
      return;
    }

    // Clear out the old search_markers.
    search_markers.forEach(function(marker) {
      marker.setMap(null);
    });
    search_markers = [];

    // For each place, get the icon, name and location.
    var bounds = new google.maps.LatLngBounds();
    places.forEach(function(place) {
      if (!place.geometry) {
        console.log("Returned place contains no geometry");
        return;
      }
      var icon = {
        // url: place.icon,
        size: new google.maps.Size(71, 71),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(17, 34),
        scaledSize: new google.maps.Size(25, 25)
      };
      var marker = new google.maps.Marker({
        map: map,
        icon: icon,
        title: place.name,
        position: place.geometry.location
      })
      var infowindow = new google.maps.InfoWindow({
        content: '<span>'+place.name+'<br>'+place.geometry.location+'</span>'
      });
      marker.addListener('click', function() {
        infowindow.open(map, marker);
      });
      // Create a marker for each place.
      search_markers.push();

      if (place.geometry.viewport) {
        // Only geocodes have viewport.
        bounds.union(place.geometry.viewport);
      } else {
        bounds.extend(place.geometry.location);
      }
    });
    map.fitBounds(bounds);
  });

  create_sites();
}


function create_sites(){
  var draggable = (allow_latlngDrag > 0) ? true : false;
  var icon = {
    path: 'm 22,11 a 11,11 0 0 0 -11,-11 11,11 0 0 0 -11,11 11,11 0 0 0 11,11 11,11 0 0 0 11,-11 z',
    fillColor: 'white',
    fillOpacity: 1,
    scale: 0.4,
    strokeColor: '#FF0066',
    strokeWeight: 5,
    anchor: new google.maps.Point(11,11),
  };
  var infowindow = new google.maps.InfoWindow();
  for (var i = 0,s = sites.length; i < s; i++){
    let marker = new google.maps.Marker({
      position: {
        lat: sites[i].lat,
        lng: sites[i].lng,
      },
      icon:icon,
      map: map,
      draggable: draggable,
      ajaxData: sites[i]
    });
    var artist_url = (sites[i].website != '') ? '<a href="http://'+sites[i].website+'" target="_blank">'+sites[i].artist+'</a>' : sites[i].artist;
    var artwork_image = (sites[i].image != null) ? '<div class="row break-light"><a  class="row" href="/media/'+sites[i].image_dir + sites[i].image+'.jpg" target="_blank"><img src="/media/'+sites[i].image_dir + sites[i].image+'-thumbnail.jpg"></a></div>' : '';
    var content = '<div class="row spaced flex-center break-light" style="width:200px">'+
        '<div class="three grid">'+
          '<div id="PLAY_'+sites[i].id+'" data-id="'+sites[i].id+'" class="map-audio-button map-load-button"></div>'+
        '</div>'+
        '<div class="nine grid">'+
          '<b>'+sites[i].address+'</b>'+
          '<br>'+artist_url+
        '</div>'+
      '</div>'+
      artwork_image +
      '<div class="audio-playback-bar">'+
        '<div id="AudioProgress" class="audio-progress"></div>'+
      '</div>';
    var id = sites[i].id;
    google_site[id] = {
      marker: marker,
      audio: 'https://wrmota.org/media/'+sites[i].audio_dir + sites[i].audio
    }
    // audio[id] = new Howl({ src: [audio_file] })
    google.maps.event.addListener(marker, 'click', (function(marker, content, id) {
      return function() {
          if (latest_track){
            latest_track_duration = 0;
            latest_track.stop();
          }
          infowindow.setContent(content);
          infowindow.open(map, marker);
          load_audio(id);
      }
    })(marker, content, id));
    if (draggable){
      google.maps.event.addListener(marker, 'dragend', function(evt){
        updateLatLng(marker.ajaxData, evt.latLng.lat(), evt.latLng.lng());
      });
    }
  }
}

function show_site_from_table(dataset){
  var site = google_site[dataset.id].marker;
  google.maps.event.trigger(site,'click');
  map.panTo(site.position);
}

function load_audio(id){
  var file = google_site[id].audio;
  if (!audio[id]){
    audio[id] = new Howl({
      src: [
        file+'.mp3',
        file+'.ogg',
        file+'.webm',
        file+'.m4a',
      ],
    });
  } else if (audio[id].state() == 'loaded') {
    console.log(id);
    allow_play(id);
  }

  audio[id].on('load', function(){
    console.log(id);
    allow_play(id);
  });
}

function allow_play(id){
  var play_id = '#PLAY_'+id;
  var play_pause = new TouchClick(play_id, play_pause_audio);
  var seek_audio = new TouchClick('.audio-playback-bar', function(elem,evt){
    if(latest_track && latest_track_duration > 0){
      var position = 1 - ((elem.clientWidth - evt.offsetX)/elem.clientWidth);
      latest_track.seek(position*latest_track_duration);
      audio_progress_step();
    }
  })
  $('#PLAY_'+id)
    .removeClass('map-load-button')
    .addClass('map-play-button')
  ;
}

function play_pause_audio(elem,evt){
  var track = audio[elem.dataset.id];
  var id = '#'+elem.id;
  if (track.playing()){
    $(id)
      .removeClass('map-pause-button')
      .addClass('map-play-button')
    ;
    track.pause();
  } else {
    $(id)
      .removeClass('map-play-button')
      .addClass('map-pause-button')
    ;
    latest_track = track;
    latest_track_duration = track.duration();
    track.play();
    audio_progress_step();
  }
}

function audio_progress_step(){
  var seek = latest_track.seek() || 0;
  var progress = Math.round(seek / latest_track_duration * 100) + '%';
  $('#AudioProgress').css({
    width: progress
  })

  if (latest_track.playing()) {
    requestAnimationFrame(audio_progress_step.bind(this));
  }
}

function updateLatLng(marker, lat, lng){
  let data = {
    id: marker.id,
    lat: lat,
    lng: lng
  }
  $.ajax({
      type: "POST",
      url: '/api/v1/post/latLng',
      data: JSON.stringify(data, null, '\t'),
      contentType: 'application/json',
      success: function(data) {
        table.table.ajax.reload();
      },
      error: function(data){
        console.log(data.errors);
      }
  });
}
