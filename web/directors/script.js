L.mapbox.accessToken = 'pk.eyJ1IjoiZG9yc2VnYWwiLCJhIjoiY2o1ZmUyaDJqMGV2ejM2bzEzb2IxcXBpMSJ9.RyTUESYcJTZ2J9mxH_A-1w';

var map = L.mapbox.map('map')
  .setView([39.279806, 2.402989], 3);

var layers = {
    Streets: L.mapbox.tileLayer('mapbox.streets'),
    Outdoors: L.mapbox.tileLayer('mapbox.outdoors'),
    Light: L.mapbox.tileLayer('mapbox.light'),
    Dark: L.mapbox.tileLayer('mapbox.dark'),
    Satellite: L.mapbox.tileLayer('mapbox.satellite')
};

$('#search_title').keyup(search);
$('#search_director').keyup(search);

layers.Streets.addTo(map);
L.control.layers(layers).addTo(map);

var markers = new L.MarkerClusterGroup();
var markers_size = 0;
var items = {};
var curr_markers = [];

var geojsonLayer = omnivore.geojson('directors.geojson', null, L.mapbox.featureLayer())
  .on("ready", function() {
  
    attachPopups();
    
    // Now we can transfer single layers / markers to the marker cluster group.
    markers.addLayer(geojsonLayer); // use the global variable markers.
    markers.eachLayer(function(marker){
      markers_size++;
      var props = marker.feature.properties;
      var name = props.name;
      var item = document.createElement('div');
      item.className = 'item';
      var link = item.appendChild(document.createElement('a'));
      link.href = '#';
      link.className = 'name';
      link.innerHTML = name;
      item.setAttribute('sort_by', name.toLowerCase());
      link.onclick = function() {
          map.setView(marker.getLatLng(), 15);
          marker.openPopup();
      };
      // Marker interaction
      marker.on('click', function(e) {
        map.panTo(marker.getLatLng());
      });
      items[name] = item;
      curr_markers.push(name);   
    });
    map.fitBounds(geojsonLayer.getBounds());
    markers.addTo(map);
    console.log("Total Markers: " + markers_size);
  });


var markerList = document.getElementById('listings');

$('.menu-ui a').on('click', function() {
    $('#search_title').val('');
    $('#search_director').val('');
    filter_by("","");
    map.fitBounds(geojsonLayer.getBounds());
    return false;
});

function itemsArrayEquals(a,b){
    if (a.length != b.length){
        return false;
    }
    for(var i=0; i<a.length; i++){
        var a_name = a[i];
        var b_name = b[i];
        if (a_name != b_name){
            return false;
        }
    }
    return true;
}

function onmove() {
    // Get the map bounds - the top-left and bottom-right locations.
    var inBounds = [],
        bounds = map.getBounds(),
        inArray = {};
    var numOfBounds = 0;
    markers.eachLayer(function(marker) {
        var props = marker.feature.properties;
        var name = props.name;
        // For each marker, consider whether it is currently visible by comparing
        // with the current map bounds.
        if (bounds.contains(marker.getLatLng())) {
            numOfBounds++;
            if (!inArray[name]){
                inBounds.push(name);
                inArray[name] = true;
            }
        }
    });
    inBounds.sort(function(a, b) {
        return a.localeCompare(b);
    });
    if (!itemsArrayEquals(curr_markers, inBounds)){
        markerList.innerHTML = "";
        inBounds.forEach(function(name) {
            markerList.appendChild(items[name]);
        });
        curr_markers = inBounds;
    }
    console.log("Markers in bounds: " + numOfBounds);
    if (numOfBounds == markers_size){
      $('.menu-ui a').removeClass('active');
    }
    else $('.menu-ui a').addClass('active');
}

function search() {
    // get the value of the search input field
    var title = $('#search_title').val().toLowerCase();
    var director = $('#search_director').val().toLowerCase();

    filter_by(title, director);
}

function filter_by(title, director) {
    geojsonLayer.setFilter(filter_feature); // this will "hide" markers that do not match the filter.
    attachPopups();
    
    // replace the content of marker cluster group.
    markers.clearLayers();
    markers.addLayer(geojsonLayer);

    onmove();

    function filter_feature(feature){
        return showMovie(feature, title) && showDirector(feature, director); 
    }
}

function showDirector(feature, query) {
    return feature.properties.name
        .toLowerCase()
        .indexOf(query.toLowerCase()) !== -1;
}

function showMovie(feature, query) {
    var movies = feature.properties.movies;
    for (var i=0; i<movies.length; i++){
      if (movies[i].toLowerCase().indexOf(query) !== -1)
        return true;
    }
    return false;
}

// Need a function because it looks like .setFilter() removes the popup…
function attachPopups() {
  // Create popups.
    geojsonLayer.eachLayer(function (layer) {
      var feature = layer.feature;
      var properties = feature.properties;
      var movies = properties.movies.slice(0,3);
      var date_birth = properties.date_birth;
      if (date_birth == null){
        date_birth = "None";
      }

      var tabs = document.createElement('div');
      tabs.className = 'tabs-ui';
      var info_tab = document.createElement('div');
      info_tab.className = 'tab';
      var info = document.createElement('input');
      info.type = 'radio';
      info.id = idify("info");
      info.name = 'tab-group';
      info.setAttribute('checked', true);
      info_tab.appendChild(info);
      info_tab.innerHTML += '<label for=' + info.id + '>' + "info" + '</label>' +
        '<div class="content">' +
            "<center><b>" + properties.name + "</b></center>" + 
                        "<b>Location:</b> " + properties.location + '<br/>' +
                        "<b>Gender:</b> " + properties.gender + '<br/>' + 
                        "<b>Date of birth:</b> " + date_birth + '<br/>' +
                        "<b>Place of birth:</b> " + properties.places_birth + '<br/>' +
                        "<b>Movies:</b> " + movies + ',...<br/>' +
                        "<a href=\"" + properties.url + "\" target=\"_blank\"><b>DBpedia page</b></a>" +
        '</div>';

      var pic_tab = document.createElement('div');
      pic_tab.className = 'tab';
      var pic = document.createElement('input');
      pic.type = 'radio';
      pic.id = idify("pic");
      pic.name = 'tab-group';
      pic_tab.appendChild(pic);
      pic_tab.innerHTML += '<label for=' + pic.id + '>' + "photo" + '</label>' +
        '<div class="content">' +
            "<center><img src=\"" + properties.photo + "\" alt=\"" + properties.name + "\" style=\"width:200px;height:200px;\"></center>" +
        '</div>';

      tabs.appendChild(info_tab);
      tabs.appendChild(pic_tab);

      layer.bindPopup(tabs); 
    });
}

function idify(str) { return str.replace(/\s+/g, '-').toLowerCase(); }

map.on('move', onmove);

// call onmove off the bat so that the list is populated.
// otherwise, there will be no markers listed until the map is moved.
onmove();
