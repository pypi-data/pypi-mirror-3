// This script is used to provide glue code between iframed and twitter
// bootstrap modal. And also providing some convinience method for usage in
// Plone.
//
//
// @author Rok Garbas, Izak Burger
// @version 0.1
// @licstart  The following is the entire license notice for the JavaScript
//            code in this page.
//
// Copyright (C) 2010 Plone Foundation
//
// This program is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by the Free
// Software Foundation; either version 2 of the License.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
// more details.
//
// You should have received a copy of the GNU General Public License along with
// this program; if not, write to the Free Software Foundation, Inc., 51
// Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//
// @licend  The above is the entire license notice for the JavaScript code in
//          this page.
//

/*jshint bitwise:true, curly:true, eqeqeq:true, immed:true, latedef:true,
  newcap:true, noarg:true, noempty:true, nonew:true, plusplus:true,
  regexp:true, undef:true, strict:true, trailing:true, browser:true */
/*global jQuery:false */


(function($) {
"use strict";

// # Namespace
$.plone = $.plone || {};
$.plone.overlay = $.plone.overlay || {};

// # Overlay Object
$.plone.overlay.Overlay = function(el, options) { this.init(el, options); };
$.plone.overlay.Overlay.prototype = {
  init: function(el, options) {
    var self = this;

    self.el_trigger = el;
    self.options = $.extend(true, {
      mask: $.plone.mask,
      filter_selector: 'div#visual-portal-wrapper',
      template: '' +
        '<div class="modal fade">' +
        '  <div class="modal-header">' +
        '    <a class="close" data-dismiss="modal">&times;</a>' +
        '    <h3>Title</h3>' +
        '  </div>' +
        '  <div class="modal-body">Content</div>' +
        '  <div class="modal-footer">Buttons</div>' +
        '</div>'
    }, options);

    self.el_trigger.on('click', function(e) {
      e.preventDefault();
      e.stopPropagation();

      // add overlay element into dom
      if (self.el.parents('body').size() === 0) {
        self.el.hide().prependTo($('body'));
      }

      // load content from link and open overlay
      if (self.loaded_data === undefined) {
        self.load();
      } else {
        self.open();
      }
    });

    // create modal element from template
    self.el = $(self.options.template)
      .modal({ backdrop:false, keyboard: true, show: false })
      .on('click', function(e) { e.preventDefault(); e.stopPropagation(); })
      .on('shown', function() {
          if (self.options.mask) {
            self.options.mask.load();
          }
        })
      .on('hidden', function() {
          if (self.options.mask) {
            self.options.mask.close();
          }
        });

    // TODO: keep all links inside the overlay
    //$('a', self.el).on('click', function(e){
    //  e.preventDefault();
    //  e.stopPropagation();

    //  // TODO: should done with slide left effect
    //  // TODO: we need to connect this with browser history

    //  // for now we hide current overlay and open new overlay
    //  self.modal('hide');
    //  $(this).ploneOverlay();
    //});

    // TODO: check if this is really needed
    //$('[data-dismiss=modal]', self._overlay).on('click', function(e) {
    //    e.preventDefault();
    //    e.stopPropagation();
    //    self.modal('hide');
    //});

  },
  load: function() {
    // Clean up the url
    // Insert ++untheme++ namespace to disable theming. This only works
    // for absolute urls.
    var self = this,
        href = self.el_trigger.attr('href');

    //href = (href.match(/^([^#]+)/)||[])[1];
    //href = href.replace(/^(https?:\/\/[^/]+)\/(.*)/, '$1/++untheme++d/$2');

    // TODO: show spinner

    $.get(href, function(data) {

      self.loaded_data = $(data).filter(self.options.filter_selector);

      if (self.options.after_load) {
        self.options.after_load(self);
      }

      // TODO: hide spinner

      self.open();
    });
  },
  open: function() {
    var self = this;
    self.el.modal('show');
    if (self.options.after_open) {
      self.options.after_open(self);
    }
  }
};

// # jQuery integration 
$.fn.ploneOverlay = function (options) {
  var el = $(this),
      data = el.data('plone-overlay');
  if (data === undefined) {
    data = new $.plone.overlay.Overlay(el, options);
    el.data('plone-overlay', data);
  }
  return data;
};

}(jQuery));
