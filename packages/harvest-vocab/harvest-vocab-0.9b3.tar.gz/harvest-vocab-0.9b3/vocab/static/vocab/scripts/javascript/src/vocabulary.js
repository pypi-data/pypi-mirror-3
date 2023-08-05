
define(['jquery', 'underscore', 'cilantro/define/viewelement'], function($, _, ViewElement) {
  var breadcrumbsTemplate, browseTemplate, searchResultsTemplate, selectedTemplate, vocabBrowserTemplate;
  breadcrumbsTemplate = '<% for (var b, i = 0; i < breadcrumbs.length; i++) { %>\n    <% b = breadcrumbs[i]; %>\n    <% if (i === (breadcrumbs.length-1)) {%>\n        <h3 title="<%= b.name %>"><%= b.name %></h3>\n    <% } else { %>\n        &raquo; <a href="<%= b.uri %>" title="<%= b.name %>"><%= b.name %></a>\n    <% } %>\n<% } %>';
  browseTemplate = '<li data-id="<%= id %>" data-uri="<%= uri %>" <% if (!terminal) { %>class="folder"<% } %>>\n    <button class="button-add">+</button>\n    <span><%= name %>\n        <% if (attrs) { %>\n            <br><small class="info"><% for (var k in attrs) { %>\n                <%= k %>: <%= attrs[k] %>\n            <% } %></small>\n        <% } %>\n    </span>\n</li>';
  searchResultsTemplate = '<li data-id="<%= id %>" <% if (!terminal) { %>class="folder"<% } %>>\n    <button class="button-add">+</button>\n    <span>\n        <% if (search_only) { %>\n            <span><%= name %></span>\n        <% } else { %>\n            <a href="<%= parent.uri %>"><%= name %></a>\n        <% } %>\n        <% if (attrs) { %>\n            <br><small class="info"><% for (var k in attrs) { %>\n                <%= k %>: <%= attrs[k] %>\n            <% } %></small>\n        <% } %>\n    </span>\n</li>';
  selectedTemplate = '<li data-id="<%= id %>" <% if (!terminal) { %>class="folder"<% } %>>\n    <button class="button-remove">-</button>\n    <% if (search_only) { %>\n        <span><%= name %></span>\n    <% } else { %>\n        <a href="<%= parent.uri %>"><%= name %></a>\n    <% } %>\n</li>';
  vocabBrowserTemplate = '<div class="browser">\n    <% if (!search_only) { %>\n        <div class="tabs">\n            <a class="tab" href="#browse-tab-<%= pk %>">Browse <%= title %></a>\n            <a class="tab" href="#search-tab-<%= pk %>">Search <%= title %></a>\n        </div>\n    <% } %>\n    <div>\n        <% if (!search_only) { %>\n            <div id="browse-tab-<%= pk %>">\n                <div class="breadcrumbs"></div>\n                <ul class="list choices"></ul>\n            </div>\n        <% } %>\n\n        <div id="search-tab-<%= pk %>">\n            <form method="get" action="<%= directory %>">\n                <input type="text" class="search" name="q" placeholder="Search...">\n                <em>Note: only the first 100 results are displayed</em>\n            </form>\n            <div>\n                <ul class="list results">\n                    <li class="start">Enter search terms above. Results can be clicked to go to their location in the Browse tab.</li>\n                </ul>\n            </div>\n        </div>\n\n        <h2>Selected <%= title %></h2>\n        <small>Note: this query is currently limited to getting results having at least ONE of these <%= title.toLowerCase() %>.</small>\n        <ul class="list selected"></ul>\n    </div>\n</div>';
  return ViewElement.extend({
    constructor: function(viewset, concept_pk) {
      this.base(viewset, concept_pk);
      return this.ds = [];
    },
    render: function() {
      var addItem, breadcrumbs, choices, dom, linkItem, objRef, pk, results, search, selected, tabs;
      addItem = function(evt) {
        var target;
        target = $(this).parent();
        objRef.addNode(target.data());
        return false;
      };
      linkItem = function(evt) {
        var item, li;
        item = $(this);
        li = item.parents('li');
        tabs.tabs('toggle', 0);
        objRef.reloadBrowser(item.attr('href'), function() {
          var target;
          target = $('[data-id=' + li.data('id') + ']', objRef.choices);
          return objRef.choices.scrollTo(target, 500, {
            offset: -150,
            onAfter: function() {
              return target.effect('highlight', null, 2000);
            }
          });
        });
        return false;
      };
      objRef = this;
      pk = this.pk = this.concept_pk + '_' + this.viewset.pk;
      dom = this.dom = $(_.template(vocabBrowserTemplate, this.viewset));
      tabs = $('.tabs', dom);
      choices = this.choices = $('.choices', dom);
      selected = this.selected = $('.selected', dom);
      search = this.search = $('.search', dom);
      results = this.results = $('.results', dom);
      breadcrumbs = this.breadcrumbs = $('.breadcrumbs', dom);
      tabs.tabs(false, function(evt, tab) {
        var siblings;
        siblings = tabs.find('.tab');
        siblings.each(function(i, o) {
          return $(o.hash, objRef.dom).hide();
        });
        return $(tab.prop('hash'), objRef.dom).show();
      });
      breadcrumbs.delegate('a', 'click', function() {
        objRef.reloadBrowser($(this).attr('href'));
        return false;
      });
      choices.delegate('button', 'click', addItem);
      results.delegate('button', 'click', addItem);
      results.delegate('a', 'click', linkItem);
      selected.delegate('a', 'click', linkItem);
      choices.delegate('.folder', 'click', function() {
        objRef.reloadBrowser($(this).data('uri'));
        return false;
      });
      selected.delegate('button', 'click', function() {
        var li, target;
        target = $(this);
        li = target.parent();
        objRef.removeNode(li.data());
        li.remove();
        return false;
      });
      return this.execute();
    },
    execute: function() {
      var objRef, results;
      objRef = this;
      results = this.results;
      this.reloadBrowser();
      return this.search.autocomplete2({
        start: function() {
          return results.block();
        },
        success: function(query, resp) {
          results.empty();
          if (!resp.length) {
            results.html('<li class="empty">No results found.</li>');
            return;
          }
          $.each(resp, function(i, o) {
            var li;
            li = objRef.renderListElement(o, searchResultsTemplate);
            return results.append(li);
          });
          objRef.refreshBrowser();
          return results.unblock();
        }
      });
    },
    updateDS: function(evt, new_ds) {
      var key, objRef, operator, _results;
      objRef = this;
      operator = /operator$/;
      this.refreshBrowser();
      if (!$.isEmptyObject(new_ds)) {
        _results = [];
        for (key in new_ds) {
          if (operator.test(key)) continue;
          _results.push($.each(new_ds[key], function(index, instance_id) {
            return $.ajax({
              url: objRef.viewset.directory + instance_id + '/',
              success: function(node) {
                return objRef.addNode(node);
              }
            });
          }));
        }
        return _results;
      }
    },
    updateElement: function(evt, element) {},
    elementChanged: function(evt, element) {},
    reloadBrowser: function(url, callback) {
      var breadcrumbs, objRef;
      url = url || this.viewset.directory;
      callback = callback || function() {};
      objRef = this;
      breadcrumbs = [
        {
          name: 'All',
          uri: this.viewset.directory
        }
      ];
      this.choices.block();
      return $.getJSON(url, function(data) {
        var i, li, n, nodes, tmpl;
        objRef.choices.empty();
        objRef.breadcrumbs.empty();
        if (!$.isArray(data)) {
          nodes = data.children;
          breadcrumbs = breadcrumbs.concat((data.ancestors.length ? data.ancestors : []));
          breadcrumbs.push({
            name: data.name
          });
        } else {
          nodes = data;
        }
        li = void 0;
        n = void 0;
        i = 0;
        while (i < nodes.length) {
          n = nodes[i];
          li = objRef.renderListElement(n, browseTemplate);
          objRef.choices.append(li);
          i++;
        }
        tmpl = _.template(breadcrumbsTemplate, {
          breadcrumbs: breadcrumbs
        });
        objRef.breadcrumbs.html(tmpl);
        objRef.refreshBrowser();
        callback();
        return objRef.choices.unblock();
      });
    },
    renderListElement: function(node, template) {
      var li;
      if (!node.parent) {
        if (!node.ancestors || node.ancestors.length === 0) {
          node.parent = {
            uri: this.viewset.directory
          };
        } else {
          node.parent = {
            uri: node.ancestors[0].uri
          };
        }
      }
      node.search_only = this.viewset.search_only;
      li = $(_.template(template, node));
      li.data(node);
      return li;
    },
    addNode: function(node) {
      var li;
      if (this.ds.indexOf(node.id) < 0) {
        this.ds.push(node.id);
        li = this.renderListElement(node, selectedTemplate);
        this.selected.append(li);
      }
      this.dom.trigger('ElementChangedEvent', [
        {
          name: this.pk,
          value: this.ds
        }
      ]);
      return this.refreshBrowser();
    },
    removeNode: function(node) {
      var i;
      i = void 0;
      if ((i = this.ds.indexOf(node.id)) > -1) this.ds.splice(i, 1);
      this.dom.trigger('ElementChangedEvent', [
        {
          name: this.pk,
          value: (this.ds.length > 0 ? this.ds : 'undefined')
        }
      ]);
      return this.refreshBrowser();
    },
    refreshBrowser: function() {
      var i, id, li, _results;
      $('li', this.choices).removeClass('added');
      $('button', this.choices).attr('disabled', false);
      $('li', this.results).removeClass('added');
      $('button', this.results).attr('disabled', false);
      id = void 0;
      li = void 0;
      i = this.ds.length;
      _results = [];
      while (i--) {
        id = this.ds[i];
        $('li[data-id=' + id + ']', this.choices).addClass('added').find('button').attr('disabled', true);
        _results.push($('li[data-id=' + id + ']', this.results).addClass('added').find('button').attr('disabled', true));
      }
      return _results;
    }
  });
});
