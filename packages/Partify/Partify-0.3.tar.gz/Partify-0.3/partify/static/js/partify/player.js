(function() {
  /*
Copyright 2011 Fred Hatfull

This file is part of Partify.

Partify is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Partify is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Partify.  If not, see <http://www.gnu.org/licenses/>.
*/;
  var $, GlobalQueue, Player, Queue, Search, Track, UserQueue, buildRoboHashUrlFromId, secondsToTimeString;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  }, __indexOf = Array.prototype.indexOf || function(item) {
    for (var i = 0, l = this.length; i < l; i++) {
      if (this[i] === item) return i;
    }
    return -1;
  };
  $ = jQuery;
  $(function() {
    window.Partify = window.Partify || {};
    window.Partify.Player = new Player();
    window.Partify.Player.init();
    window.Partify.Queues = window.Partify.Queues || {};
    return window.Partify.Queues.GlobalQueue = window.Partify.Queues.GlobalQueue || {};
  });
  Player = (function() {
    function Player() {
      var up_next_items;
      this.info = {
        artist: '',
        title: '',
        album: '',
        elapsed: 0,
        time: 100,
        date: 1970,
        volume: 0,
        state: 'pause',
        file: '',
        last_global_playlist_update: 0
      };
      this.config = up_next_items = 3;
      this.last_update_time = (new Date()).getTime();
    }
    Player.prototype.init = function() {
      this.initPlayerVisuals();
      this.initPlayerUpdating();
      return this.info.last_global_playlist_update = (new Date()).getTime();
    };
    Player.prototype.initPlayerVisuals = function() {
      $("#player_progress").progressbar({
        value: 0
      });
      return $("#tabs").tabs();
    };
    Player.prototype.initPlayerUpdating = function() {
      this._initPlayerSynchroPolling(3000);
      return this._initPlayerLocalUpdate();
    };
    Player.prototype._initPlayerPushUpdates = function() {
      var worker;
      worker = new Worker('static/js/partify/workers/player_event.js');
      worker.addEventListener('message', __bind(function(e) {
        return console.log(e.data);
      }, this), false);
      return worker.postMessage('Start checking push');
    };
    Player.prototype._initPlayerSynchroPolling = function(poll_frequency) {
      this._synchroPoll();
      return setInterval(__bind(function() {
        return this._synchroPoll();
      }, this), poll_frequency);
    };
    Player.prototype._synchroPoll = function() {
      return $.ajax({
        url: '/player/status/poll',
        method: 'GET',
        data: {
          current: this.info.last_global_playlist_update
        },
        success: __bind(function(data) {
          if (data.elapsed) {
            data.elapsed = parseFloat(data.elapsed);
          }
          data.time = parseFloat(data.time);
          this.updatePlayerInfo(data);
          if (data.global_queue) {
            window.Partify.Queues.GlobalQueue.update(data.global_queue);
          }
          if (data.user_queue) {
            return window.Partify.Queues.UserQueue.update(data.user_queue);
          }
        }, this)
      });
    };
    Player.prototype._initPlayerLocalUpdate = function() {
      return setInterval(__bind(function() {
        return this._playerLocalUpdate();
      }, this), 1000);
    };
    Player.prototype._playerLocalUpdate = function() {
      var last_update_time;
      last_update_time = this.last_update_time;
      this.last_update_time = (new Date()).getTime();
      if (this.info.state === 'play') {
        this.info.elapsed = Math.floor(this.info.elapsed) < this.info.time ? this.info.elapsed + ((this.last_update_time - last_update_time) / 1000) : this.info.elapsed;
        this.updatePlayerProgress();
        if (this.info.elapsed >= this.info.time) {
          this._synchroPoll();
          return window.Partify.Queues.UserQueue.loadPlayQueue();
        }
      }
    };
    Player.prototype.updatePlayerInfo = function(data) {
      var d, info, key, text, value, _i, _len, _ref;
      info = (function() {
        var _ref, _results;
        _ref = this.info;
        _results = [];
        for (key in _ref) {
          value = _ref[key];
          if (data.state !== 'stop') {
            data[key] || (data[key] = this.info[key]);
          }
          this.info[key] = data[key];
          _results.push(key === 'date' ? (d = new Date(data[key]), this.info[key] = d.getFullYear()) : void 0);
        }
        return _results;
      }).call(this);
      _ref = ['artist', 'title', 'album', 'date'];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        text = _ref[_i];
        this._updatePlayerTextFromInfo(text);
      }
      return this.updatePlayerProgress();
    };
    Player.prototype._updatePlayerTextFromInfo = function(info_key) {
      return this._updatePlayerText(info_key, this.info[info_key]);
    };
    Player.prototype._updatePlayerText = function(info_key, data) {
      var info_span;
      info_span = $("#player_info_" + info_key).first();
      return info_span.text(data);
    };
    Player.prototype.updatePlayerProgress = function() {
      var progress;
      progress = Math.round((this.info.elapsed / this.info.time) * 100);
      $("#player_progress").progressbar({
        value: progress
      });
      this._updatePlayerText('elapsed', secondsToTimeString(this.info['elapsed']));
      return this._updatePlayerText('time', secondsToTimeString(this.info['time']));
    };
    return Player;
  })();
  secondsToTimeString = function(seconds) {
    var minutes, time_s;
    seconds = parseInt(Math.round(seconds));
    seconds = Math.floor(seconds);
    minutes = Math.floor(seconds / 60);
    seconds = seconds % 60;
    time_s = "" + minutes + ":";
    time_s += seconds < 10 ? '0' : '';
    time_s += seconds;
    return time_s;
  };
  Array.prototype.remove = function(e) {
    var t, _ref;
    if ((t = this.indexOf(e)) > -1) {
      return ([].splice.apply(this, [t, t - t + 1].concat(_ref = [])), _ref);
    }
  };
  /*
Copyright 2011 Fred Hatfull

This file is part of Partify.

Partify is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Partify is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Partify.  If not, see <http://www.gnu.org/licenses/>.
*/;
  $ = jQuery;
  $(function() {
    window.Partify = window.Partify || {};
    window.Partify.Queues = window.Partify.Queues || {};
    window.Partify.Queues.GlobalQueue = new GlobalQueue($("#party_queue"), $("#up_next_tracks"));
    window.Partify.Queues.UserQueue = new UserQueue($("#user_queue"));
    window.Partify.Config = window.Partify.Config || {};
    window.Partify.Config.lastFmApiKey = config_lastfm_api_key;
    window.Partify.Config.lastFmApiSecret = config_lastfm_api_secret;
    window.Partify.Config.user_id = config_user_id;
    window.Partify.LastCache = new LastFMCache();
    return window.Partify.LastFM = new LastFM({
      apiKey: window.Partify.Config.lastFmApiKey,
      apiSecret: window.Partify.Config.lastFmApiSecret,
      cache: window.Partify.LastCache
    });
  });
  Queue = (function() {
    function Queue(queue_div) {
      this.tracks = new Array();
      this.queue_div = queue_div;
      this.queue_div.sortable({
        placeholder: "queue-placeholder",
        forcePlacerHolderSize: true,
        axis: 'y',
        cancel: 'li.queue_header, li.queue_footer',
        opacity: 0.8,
        items: "li.queue_item_sortable"
      });
      this.queue_div.disableSelection();
      this.queue_div.addClass('queue');
    }
    Queue.prototype.update = function(tracks) {
      var track, _i, _len;
      this.tracks = new Array();
      for (_i = 0, _len = tracks.length; _i < _len; _i++) {
        track = tracks[_i];
        this.tracks.push(new Track(track));
      }
      return this.updateDisplay();
    };
    Queue.prototype.updateDisplay = function() {
      var track, _i, _len, _ref;
      this.queue_div.empty();
      this.queue_div.append(this._buildDisplayHeader());
      _ref = this.tracks;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        track = _ref[_i];
        this.queue_div.append(this._buildDisplayItem(track));
      }
      return this.queue_div.append(this._buildDisplayFooter());
    };
    Queue.prototype._buildDisplayHeader = function() {
      return "        <li class='queue_header span-23 last'>            <span class='span-1 ui-icon ui-icon-arrowthick-2-n-s grip'>&nbsp;</span>            <span class='span-6'>Title</span>            <span class='span-6'>Artist</span>            <span class='span-6'>Album</span>            <span class='span-3'>User</span>            <span class='span-1 last right'>Len</span>        </li>        ";
    };
    Queue.prototype._buildDisplayItem = function(track) {
      return "        <li class='queue_item queue_item_sortable ui-state-default small span-23 last'>            <span class='span-1 ui-icon ui-icon-grip-dotted-vertical grip'>&nbsp;</span>            <span class='span-6'>" + track.title + "</span>            <span class='span-6'>" + track.artist + "</span>            <span class='span-6'>" + track.album + "</span>            <span class='span-3'>" + track.user + "</span>            <span class='span-1 last right'>" + (secondsToTimeString(track.length)) + "</span>        </li>        ";
    };
    Queue.prototype._buildDisplayFooter = function() {
      if (this.tracks.length > 0) {
        return this._buildQueueSummary();
      } else {
        return this._buildNoItemsRow();
      }
    };
    Queue.prototype._buildQueueSummary = function() {
      var t, total_queue_time;
      total_queue_time = ((function() {
        var _i, _len, _ref, _results;
        _ref = this.tracks;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          t = _ref[_i];
          _results.push(t.length);
        }
        return _results;
      }).call(this)).reduce(function(a, b) {
        return a + b;
      });
      return "        <li class='queue_item queue_footer ui-state-default small span-23 last'>            <span class='span-23 last'><center><p>" + this.tracks.length + " tracks - " + (secondsToTimeString(total_queue_time)) + "</p></center></span>        </li>        ";
    };
    Queue.prototype._buildNoItemsRow = function() {
      return "        <li class='queue_item queue_footer ui-state-default small span-23 last'>            <span class='span-23 last'><center><p ><em>There's nothing in this queue right now!</em></p></center></span>        </li>        ";
    };
    Queue.prototype._buildAvatarImage = function(username) {
      return "        <img id='player_info_user_avatar' src='" + (buildRoboHashUrlFromId(username, 70, 70)) + "' />        ";
    };
    Queue.prototype.removeTrack = function(track) {
      return $.ajax({
        url: '/queue/remove',
        type: 'POST',
        data: {
          track_id: track.mpd_id
        },
        success: __bind(function(data) {
          if (data.status === 'ok') {
            this.tracks.remove(track);
            this.updateDisplay();
            return window.Partify.Player._synchroPoll();
          }
        }, this),
        error: __bind(function() {
          return console.log("Could not contact the server!");
        }, this)
      });
    };
    return Queue;
  })();
  GlobalQueue = (function() {
    __extends(GlobalQueue, Queue);
    function GlobalQueue(queue_div, up_next_div) {
      GlobalQueue.__super__.constructor.call(this, queue_div);
      this.up_next_div = up_next_div;
      this.queue_div.sortable('option', 'disabled', true);
    }
    GlobalQueue.prototype.updateDisplay = function() {
      var track, up_next_dsp, _i, _len;
      GlobalQueue.__super__.updateDisplay.call(this);
      this.up_next_div.empty();
      up_next_dsp = this.tracks.slice(1, 4);
      for (_i = 0, _len = up_next_dsp.length; _i < _len; _i++) {
        track = up_next_dsp[_i];
        this.up_next_div.append(this._buildUpNextDisplayItem(track, track.mpd_id === up_next_dsp.slice(-1)[0].mpd_id));
      }
      $("#player_info_user_name").empty();
      $("#player_info_skip_div").empty();
      $("#user_avatar_container").empty();
      if (this.tracks.length > 0) {
        $("#player_info_user_name").append(this.tracks[0].user);
        $("#user_avatar_container").append(this._buildAvatarImage(this.tracks[0].username));
        if (this.tracks[0].user_id === window.Partify.Config.user_id) {
          $("#player_info_skip_div").append("<a href='#' id='player_skip_btn'>Skip My Track</a>");
          $("#player_skip_btn").click(__bind(function(e) {
            this.removeTrack(this.tracks[0]);
            e.stopPropagation();
            return $("#player_skip_btn").remove();
          }, this));
        }
        return window.Partify.LastFM.artist.getInfo({
          artist: this.tracks[0].artist
        }, {
          success: __bind(function(data) {
            var image, image_sizes, images, img_url, preferred_sizes, size, target_size, _j, _len2, _ref;
            images = (_ref = data.artist) != null ? _ref.image : void 0;
            if (images != null) {
              console.log('Got images');
              image_sizes = (function() {
                var _j, _len2, _results;
                _results = [];
                for (_j = 0, _len2 = images.length; _j < _len2; _j++) {
                  image = images[_j];
                  _results.push(image.size);
                }
                return _results;
              })();
              preferred_sizes = ['large', 'medium', 'small'];
              for (_j = 0, _len2 = preferred_sizes.length; _j < _len2; _j++) {
                size = preferred_sizes[_j];
                if (__indexOf.call(image_sizes, size) < 0) {
                  preferred_sizes.remove(size);
                }
              }
              target_size = preferred_sizes[0];
              img_url = (function() {
                var _k, _len3, _results;
                _results = [];
                for (_k = 0, _len3 = images.length; _k < _len3; _k++) {
                  image = images[_k];
                  if (image.size === target_size) {
                    _results.push(image['#text']);
                  }
                }
                return _results;
              })();
              img_url = img_url[0];
              return $('#now_playing_artist_image').attr('src', img_url);
            }
          }, this),
          error: __bind(function(code, message) {
            return console.log("" + code + " - " + message);
          }, this)
        });
      } else {
        return $('#now_playing_artist_image').attr('src', "http://debbiefong.com/images/10%20t.jpg");
      }
    };
    GlobalQueue.prototype._buildDisplayHeader = function() {
      return "        <li class='queue_header span-23 last'>            <span class='span-1 padder'>&nbsp;</span>            <span class='span-6'>Title</span>            <span class='span-6'>Artist</span>            <span class='span-6'>Album</span>            <span class='span-3'>User</span>            <span class='span-1 right'>Time</span>            <span class='span-1 last padder'>&nbsp;</span>        </li>        ";
    };
    GlobalQueue.prototype._buildDisplayItem = function(track) {
      return "        <li class='queue_item queue_item_sortable ui-state-default small span-23 last'>            <span class='span-1 padder'>&nbsp;</span>            <span class='span-6'>" + track.title + "</span>            <span class='span-6'>" + track.artist + "</span>            <span class='span-6'>" + track.album + "</span>            <span class='span-3'>" + track.user + "</span>            <span class='span-1 right'>" + (secondsToTimeString(track.length)) + "</span>            <span class='span-1 last padder'>&nbsp;</span>        </li>        ";
    };
    GlobalQueue.prototype._buildPlayerImage = function(src) {
      return "       <img id='now_playing_artist_image' class='span-3' src='" + src + "' />        ";
    };
    GlobalQueue.prototype._buildUpNextDisplayItem = function(track, last) {
      var comma;
      comma = last ? '' : ', ';
      return "" + track.artist + " - " + track.title + comma;
    };
    return GlobalQueue;
  })();
  UserQueue = (function() {
    __extends(UserQueue, Queue);
    function UserQueue(queue_div) {
      UserQueue.__super__.constructor.call(this, queue_div);
      this.queue_div.bind('sortupdate', __bind(function(e, ui) {
        var priority, track, track_list, _fn, _i, _len, _ref;
        track_list = {};
        priority = 0;
        if (this.tracks[0].id === window.Partify.Queues.GlobalQueue.tracks[0].id) {
          priority = 2;
          track_list[this.tracks[0].id] = 1;
        } else {
          priority = 1;
        }
        _ref = this.queue_div.children("li.queue_item").children('input');
        _fn = __bind(function(track) {
          var t, target_track_id, track_obj, _j, _len2, _ref2;
          target_track_id = parseInt($(track).val());
          _ref2 = this.tracks;
          for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
            t = _ref2[_j];
            if (t.id === target_track_id) {
              track_obj = t;
            }
          }
          track_list[track_obj.id] = priority;
          return priority++;
        }, this);
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          track = _ref[_i];
          _fn(track);
        }
        console.log(track_list);
        return $.ajax({
          url: 'queue/reorder',
          type: 'POST',
          data: track_list,
          success: function(data) {
            if (data.status === 'ok') {
              return console.log('Everything worked out');
            } else {
              return this.error();
            }
          },
          error: __bind(function() {
            console.log('Error reordering the queue!');
            return this.loadPlayQueue();
          }, this)
        });
      }, this));
      this.loadPlayQueue();
    }
    UserQueue.prototype.loadPlayQueue = function() {
      return $.ajax({
        url: 'queue/list',
        type: 'GET',
        success: __bind(function(data) {
          if (data.status === "ok") {
            return this.update(data.result);
          }
        }, this),
        error: __bind(function() {
          return console.log("Failed to populate user play queue!");
        }, this)
      });
    };
    UserQueue.prototype.updateDisplay = function() {
      var track, _i, _len, _ref;
      this.queue_div.empty();
      this.queue_div.append(this._buildDisplayHeader());
      _ref = this.tracks;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        track = _ref[_i];
        if (track.id !== window.Partify.Queues.GlobalQueue.tracks[0].id) {
          this.queue_div.append(this._buildDisplayItem(track));
        }
      }
      this.queue_div.append(this._buildDisplayFooter());
      return this._createRemoveButtons();
    };
    UserQueue.prototype._buildDisplayHeader = function() {
      return "        <li class='queue_header span-23 last'>            <span class='span-1 ui-icon ui-icon-arrowthick-2-n-s grip'>&nbsp;</span>            <span class='span-7'>Title</span>            <span class='span-6'>Artist</span>            <span class='span-6'>Album</span>            <span class='span-2 '>Time</span>            <span class='span-1 last padder'>&nbsp;</span>        </li>        ";
    };
    UserQueue.prototype._buildDisplayItem = function(track) {
      var html;
      return html = "        <li class='queue_item queue_item_sortable ui-state-default small span-23 last'>            <input type='hidden' name='id' value='" + track.id + "'>            <span class='span-1 ui-icon ui-icon-grip-dotted-vertical grip'>&nbsp;</span>            <span class='span-7'>" + track.title + "</span>            <span class='span-6'>" + track.artist + "</span>            <span class='span-6'>" + track.album + "</span>            <span class='span-2'>" + (secondsToTimeString(track.length)) + "</span>            <span class='span-1 right last'><button id='rm_" + track.id + "' class='rm_btn'></button></span>        </li>";
    };
    UserQueue.prototype._createRemoveButtons = function() {
      var track, _i, _len, _ref, _results;
      _ref = this.tracks;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        track = _ref[_i];
        _results.push(this._createRemoveButton(track));
      }
      return _results;
    };
    UserQueue.prototype._createRemoveButton = function(track) {
      var rm_btn;
      rm_btn = $('button#rm_' + track.id);
      rm_btn.button({
        icons: {
          primary: 'ui-icon-close'
        },
        text: false
      });
      return rm_btn.click(__bind(function(e) {
        rm_btn.button('disable');
        rm_btn.button('option', 'icons', {
          primary: 'ui-icon-loading'
        });
        return this.removeTrack(track);
      }, this));
    };
    return UserQueue;
  })();
  buildRoboHashUrlFromId = function(id, dimension_x, dimension_y) {
    return "http://robohash.org/" + id + ".png?size=" + dimension_x + "x" + dimension_y + "&set=any&bgset=any";
  };
  /*
Copyright 2011 Fred Hatfull

This file is part of Partify.

Partify is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Partify is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Partify.  If not, see <http://www.gnu.org/licenses/>.
*/;
  $ = jQuery;
  $(function() {
    window.Partify = window.Partify || {};
    window.Partify.Search = new Search();
    return window.Partify.Search.skin_add_btns();
  });
  Search = (function() {
    Search.results = new Array();
    Search.results_display;
    Search.sortmode = {
      category: "",
      asc: true
    };
    function Search() {
      this.initializeFormHandlers();
      this.initializeSortHandlers();
      this.results_display = $("table#results_table > tbody");
      this.results = new Array();
      this.sortmode = {
        category: "",
        asc: true
      };
    }
    Search.prototype.initializeFormHandlers = function() {
      return $("#track_search_form").submit(__bind(function(e) {
        var album, artist, title;
        e.stopPropagation();
        title = $("input#search_title").val();
        artist = $("input#search_artist").val();
        album = $("input#search_album").val();
        this.processSearch(title, artist, album);
        return false;
      }, this));
    };
    Search.prototype.initializeSortHandlers = function() {
      var category, _i, _len, _ref, _results;
      _ref = ['title', 'artist', 'album'];
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        category = _ref[_i];
        _results.push(__bind(function(category) {
          return $("#results_header_" + category).click(__bind(function(e) {
            e.stopPropagation();
            if (this.sortmode.category === category) {
              this.sortmode.asc = !this.sortmode.asc;
            } else {
              this.sortmode.category = category;
              this.sortmode.asc = true;
            }
            return this.sortResultsBy(this.sortmode.category, this.sortmode.asc);
          }, this));
        }, this)(category));
      }
      return _results;
    };
    Search.prototype.sortResultsBy = function(category, is_ascending, sub_category) {
      var sortfn;
      if (sub_category == null) {
        sub_category = "track";
      }
      sortfn = function(a, b) {
        var cmp_val;
        cmp_val = 0;
        if (a[category] < b[category]) {
          cmp_val = -1;
        }
        if (a[category] > b[category]) {
          cmp_val = 1;
        }
        if (cmp_val === 0) {
          if (a[sub_category] < b[sub_category]) {
            cmp_val = -1;
          }
          if (a[sub_category] > b[sub_category]) {
            cmp_val = 1;
          }
        }
        return cmp_val;
      };
      this.results.sort(sortfn);
      if (!is_ascending) {
        this.results.reverse();
      }
      this.updateResultsDisplay();
      return this.setSortIndicator();
    };
    Search.prototype.setSortIndicator = function() {
      this.clearSortIndicators();
      return $("#results_header_" + this.sortmode.category).append("<span id='sort_indicator_arrow' class='ui-icon ui-icon-triangle-1-" + (this.sortmode.asc ? 'n' : 's') + " grip' style='float:left'>&nbsp;</span>");
    };
    Search.prototype.clearSortIndicators = function() {
      return $("#sort_indicator_arrow").remove();
    };
    Search.prototype.processSearch = function(title, artist, album) {
      var request_data;
      this.results = new Array();
      this._show_wait_spinner();
      this.clearSortIndicators();
      request_data = {};
      if (title !== "") {
        request_data['title'] = title;
      }
      if (artist !== "") {
        request_data['artist'] = artist;
      }
      if (album !== "") {
        request_data['album'] = album;
      }
      return $.ajax({
        url: '/track/search',
        type: 'GET',
        data: request_data,
        success: __bind(function(data) {
          var result, _i, _len, _ref;
          if (data.status === 'ok') {
            _ref = data.results;
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              result = _ref[_i];
              this.results.push(new Track(result));
            }
            return this.updateResultsDisplay();
          } else {
            return this.updateResultsDisplay();
          }
        }, this)
      });
    };
    Search.prototype.addTrack = function(spotify_url, row) {
      return $.ajax({
        url: '/queue/add',
        type: 'POST',
        data: {
          spotify_uri: spotify_url
        },
        success: __bind(function(data) {
          var btn;
          btn = row.children('td').children('button');
          if (data.status === 'ok') {
            btn.button('option', 'icons', {
              primary: 'ui-icon-check'
            });
            window.Partify.Player._synchroPoll();
            return window.Partify.Queues.UserQueue.update(data.queue);
          } else {
            return this._addTrackFail(btn);
          }
        }, this),
        error: __bind(function() {
          return this._addTrackFail(row.children('td').children('button'));
        }, this)
      });
    };
    Search.prototype._addTrackFail = function(btn) {
      btn.addClass('ui-state-error');
      return btn.button('option', 'icons', {
        primary: 'ui-icon-alert'
      });
    };
    Search.prototype.updateResultsDisplay = function() {
      var track, _i, _len, _ref;
      this.results_display.empty();
      if (this.results.length > 0) {
        _ref = this.results;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          track = _ref[_i];
          this.buildResultRow(track);
        }
      } else {
        this.buildEmptyResultRow();
      }
      return this.skin_add_btns();
    };
    Search.prototype.buildResultRow = function(track) {
      var row_html;
      row_html = "        <tr id='" + track.file + "'>            <td class='small'>" + track.title + "</td>            <td class='small'>" + track.artist + "</td>            <td class='small'>" + track.album + "</td>            <td class='small'>" + (secondsToTimeString(track.time)) + "</td>            <td class='small'>" + track.track + "</td>            <td class='small'><button class='add_btn'></button></td>        </tr>        ";
      return this.results_display.append(row_html);
    };
    Search.prototype.buildEmptyResultRow = function() {
      var row_html;
      row_html = "        <tr>            <td colspan='6' class='results_empty small'>                <center><em>No results found. Please try a different search using the form above.</em></center>            </td>        </tr>";
      return this.results_display.append(row_html);
    };
    Search.prototype.skin_add_btns = function() {
      $("button.add_btn").button({
        icons: {
          primary: 'ui-icon-plus'
        },
        text: false
      });
      return $("button.add_btn").click(__bind(function(e) {
        var spotify_url, track_row;
        track_row = $(e.currentTarget).parent('td').parent('tr').first();
        spotify_url = track_row.attr('id');
        this.disableRow(track_row);
        return this.addTrack(spotify_url, track_row);
      }, this));
    };
    Search.prototype.disableRow = function(row) {
      row.children('td').children('button').button('disable');
      return row.children('td').children('button').button('option', 'icons', {
        primary: 'ui-icon-loading'
      });
    };
    Search.prototype._show_wait_spinner = function() {
      this.results_display.empty();
      return this.results_display.append("        <tr>            <td colspan='6' class='results_empty'>                <center><img src='/static/img/loading.gif'></img></center>            </td>        </tr>        ");
    };
    return Search;
  })();
  Track = (function() {
    Track.id = 0;
    Track.title = "";
    Track.artist = "";
    Track.album = "";
    Track.track = "";
    Track.file = "";
    Track.time = "";
    Track.date = "";
    Track.length = "";
    Track.user = "";
    Track.user_id = 0;
    Track.playback_priority = 0;
    Track.user_priority = 0;
    Track.mpd_id = 0;
    function Track(data) {
      this.id = parseInt(data.id) || data.id;
      this.title = data.title;
      this.artist = data.artist;
      this.album = data.album;
      this.track = parseInt(data.track) || data.track;
      this.file = data.file;
      this.time = parseInt(data.time) || data.time;
      this.date = data.date;
      this.length = data.length;
      this.user = data.user;
      this.username = data.username;
      this.user_id = data.user_id;
      this.playback_priority = data.playback_priority;
      this.user_priority = data.user_priority;
      if (data.mpd_id) {
        this.mpd_id = data.mpd_id;
      }
    }
    return Track;
  })();
}).call(this);
