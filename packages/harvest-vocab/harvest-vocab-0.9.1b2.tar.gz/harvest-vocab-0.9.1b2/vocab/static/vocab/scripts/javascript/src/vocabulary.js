
define(['jquery', 'underscore', 'cilantro/define/viewelement'], function($, _, ViewElement) {
  var OPERATIONS, breadcrumbsTemplate, browseTemplate, objectIsEmpty, searchResultsTemplate, stagedTemplate, vocabBrowserTemplate;
  breadcrumbsTemplate = '<% for (var b, i = 0; i < breadcrumbs.length; i++) { %>\n    <% b = breadcrumbs[i]; %>\n    <% if (i === (breadcrumbs.length-1)) {%>\n        <span title="<%= b.name %>"><%= b.name %></span>\n    <% } else { %>\n        <a href="<%= b.uri %>" title="<%= b.name %>"><%= b.name %></a> <span class="breadcrumb-arrow">&rarr;</span>\n    <% } %>\n<% } %>';
  browseTemplate = '<li data-id="<%= id %>" data-uri="<%= uri %>" <% if (!terminal) { %>class="folder"<% } %>>\n    <button class="button-add">+</button>\n    <span class="name"><%= name %>\n        <% if (attrs) { %>\n            <br><small class="info"><% for (var k in attrs) { %>\n                <%= k %>: <%= attrs[k] %>\n            <% } %></small>\n        <% } %>\n    </span>\n</li>';
  searchResultsTemplate = '<li data-id="<%= id %>" <% if (!terminal) { %>class="folder"<% } %>>\n    <button class="button-add">+</button>\n    <span>\n        <% if (search_only) { %>\n            <span><%= name %></span>\n        <% } else { %>\n            <a href="<%= parent.uri %>"><%= name %></a>\n        <% } %>\n        <% if (attrs) { %>\n            <br><small class="info"><% for (var k in attrs) { %>\n                <%= k %>: <%= attrs[k] %>\n            <% } %></small>\n        <% } %>\n    </span>\n</li>';
  stagedTemplate = '<li data-id="<%= id %>" <% if (!terminal) { %>class="folder"<% } %>>\n    <span class="icon">optional</span>\n    <% if (search_only) { %>\n        <span class=text><%= name %></span>\n    <% } else { %>\n        <a class=text href="<%= parent.uri %>"><%= name %></a>\n    <% } %>\n    <span class="clear">X</span>';
  vocabBrowserTemplate = '<div id="vocab-browser-<%= pk %>" class="vocab-browser">\n    <% if (!search_only) { %>\n        <div class="vocab-tabs tabs">\n            <a class="tab" href="#browse-tab-<%= pk %>">Browse <%= title %></a>\n            <a class="tab" href="#search-tab-<%= pk %>">Search <%= title %></a>\n        </div>\n    <% } %>\n    <div>\n        <% if (!search_only) { %>\n            <div id="browse-tab-<%= pk %>">\n                <div class=vocab-breadcrumbs></div>\n                <ul class="vocab-browse-results list"></ul>\n            </div>\n        <% } %>\n\n        <div id="search-tab-<%= pk %>">\n            <form method="get" action="<%= directory %>">\n                <input type="text" class="vocab-search" name="q" placeholder="Search...">\n                <em>Note: only the first 100 results are displayed</em>\n            </form>\n            <div>\n                <ul class="vocab-search-results list">\n                    <li class="start">Enter search terms above. Results can be clicked to go to their location in the Browse tab.</li>\n                </ul>\n            </div>\n        </div>\n\n        <h2>Selected <%= title %></h2>\n\n        <ul class=vocab-staging-operations>\n            <li class="optional">optional</li>\n            <li class="require">require</li>\n            <li class="exclude">exclude</li>\n        </ul>\n\n        <ul class=vocab-staging></ul>\n\n    </div>\n</div>';
  OPERATIONS = {
    require: 'all',
    exclude: '-all',
    optional: 'in',
    'all': 'require',
    '-all': 'exclude',
    'in': 'optional'
  };
  objectIsEmpty = function(obj) {
    var key;
    for (key in obj) {
      return false;
    }
    return true;
  };
  return ViewElement.extend({
    constructor: function(viewset, concept_pk) {
      this.base(viewset, concept_pk);
      return this.datasource = {};
    },
    _showItemBrowser: function(target) {
      var browseResults, item, li;
      browseResults = this.browseResults;
      item = $(target);
      li = item.parents('li');
      this.tabs.tabs('toggle', 0);
      this.loadBrowseList(item.attr('href'), function() {
        target = browseResults.find("[data-id=" + (li.data('id')) + "]");
        return browseResults.scrollTo(target, 500, {
          offset: -150,
          onAfter: function() {
            return target.effect('highlight', null, 2000);
          }
        });
      });
      return false;
    },
    _renderBrowse: function(dom) {
      var results, tabs,
        _this = this;
      results = this.browseResults = $('.vocab-browse-results', dom);
      results.on('click', 'button', function(event) {
        var target;
        target = $(event.currentTarget).parent();
        _this.stageItem(target.data());
        return false;
      });
      results.on('click', '.folder', function(event) {
        _this.loadBrowseList($(event.currentTarget).data('uri'));
        return false;
      });
      this.tabs = tabs = $('.vocab-tabs', dom);
      tabs.tabs(false, function(evt, tab) {
        var siblings;
        siblings = tabs.find('.tab');
        siblings.each(function(i, o) {
          return $(o.hash, dom).hide();
        });
        return $(tab.prop('hash'), dom).show();
      });
      return this.browseBreadcrumbs = $('.vocab-breadcrumbs', dom).on('click', 'a', function(event) {
        _this.loadBrowseList(event.target.href);
        return false;
      });
    },
    _renderSearch: function(dom) {
      var results, search,
        _this = this;
      search = $('.vocab-search', dom);
      results = $('.vocab-search-results', dom);
      results.on('click', 'button', function(event) {
        var target;
        target = $(event.currentTarget).parent();
        _this.stageItem(target.data());
        return false;
      });
      results.on('click', 'a', function(event) {
        _this._showItemBrowser(event.currentTarget);
        return false;
      });
      return search.autocomplete2({
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
            li = _this.renderListElement(o, searchResultsTemplate);
            return results.append(li);
          });
          _this.refreshResultState();
          return results.unblock();
        }
      });
    },
    _renderStaging: function(dom) {
      var self, stagedItems, vocabOperations,
        _this = this;
      vocabOperations = $('.vocab-staging-operations', dom);
      this.stagedItems = stagedItems = $('.vocab-staging', dom);
      self = this;
      stagedItems.on('click', 'li .icon', function(event) {
        var icon, item, position;
        vocabOperations.off();
        icon = $(this);
        item = icon.parent();
        vocabOperations.on('click', 'li', function(event) {
          var operation;
          operation = $(this);
          icon.text(operation.text());
          item.removeClass('optional require exclude');
          item.addClass(operation.prop('className'));
          self.datasource[item.data('id')] = OPERATIONS[operation.prop('className')];
          return vocabOperations.hide();
        });
        position = item.position();
        return vocabOperations.css({
          top: position.top - item.height() + 1,
          left: position.left + 1
        }).show();
      });
      stagedItems.on('click', 'li .clear', function(event) {
        var item;
        item = $(event.target).parent();
        item.hide();
        _this.unstageItem(item.data('id'));
        return _this.refreshResultState();
      });
      return stagedItems.on('click', 'a', function(event) {
        _this._showItemBrowser(event.currentTarget);
        return false;
      });
    },
    render: function() {
      var dom;
      this.dom = dom = $(_.template(vocabBrowserTemplate, this.viewset));
      this._renderSearch(dom);
      this._renderStaging(dom);
      if (!this.viewset.search_only) {
        this._renderBrowse(dom);
        return this.loadBrowseList();
      }
    },
    stageItem: function(node, operator) {
      var li;
      if (operator == null) operator = OPERATIONS.optional;
      if (!this.datasource[node.id]) {
        li = this.renderListElement(node, stagedTemplate, operator);
        this.stagedItems.append(li);
      }
      this.datasource[node.id] = operator;
      return this.refreshResultState();
    },
    unstageItem: function(id) {
      delete this.datasource[id];
      return this.refreshResultState();
    },
    constructQuery: function() {
      var children, data, key, len, ops, value, _ref;
      ops = {};
      data = {
        concept_id: this.concept_pk,
        custom: true
      };
      _ref = this.datasource;
      for (key in _ref) {
        value = _ref[key];
        if (!ops[value]) ops[value] = [];
        ops[value].push(key);
      }
      if ((len = _.keys(ops).length) === 0) {
        data.value = void 0;
      } else if (len === 1) {
        data.id = this.viewset.pk;
        data.value = ops[value];
        data.operator = value;
      } else {
        children = [];
        for (key in ops) {
          value = ops[key];
          children.push({
            id: this.viewset.pk,
            value: value,
            operator: key,
            concept_id: this.concept_pk
          });
        }
        data.type = 'and';
        data.children = children;
      }
      return this.dom.trigger('ConstructQueryEvent', [data]);
    },
    updateDS: function(evt, data) {
      var child, self, _i, _len, _ref, _results;
      self = this;
      this.refreshResultState();
      if (!objectIsEmpty(data)) {
        if (data.children) {
          _ref = data.children;
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            child = _ref[_i];
            _results.push(self._updateDS(child.value, child.operator));
          }
          return _results;
        } else {
          return self._updateDS(data.value, data.operator);
        }
      }
    },
    _updateDS: function(ids, operator) {
      var self;
      self = this;
      return $.each(ids, function(index, id) {
        return $.ajax({
          url: self.viewset.directory + id + '/',
          success: function(node) {
            return self.stageItem(node, operator);
          }
        });
      });
    },
    updateElement: function(evt, element) {},
    elementChanged: function(evt, element) {},
    loadBrowseList: function(url, callback) {
      var breadcrumbs,
        _this = this;
      this.browseResults.block();
      url = url || this.viewset.directory;
      breadcrumbs = [
        {
          name: 'All',
          uri: this.viewset.directory
        }
      ];
      return $.getJSON(url, function(data) {
        var li, n, nodes, tmpl, _i, _len;
        _this.browseResults.empty();
        _this.browseBreadcrumbs.empty();
        if (!_.isArray(data)) {
          nodes = data.children;
          breadcrumbs = breadcrumbs.concat((data.ancestors.length ? data.ancestors : []));
          breadcrumbs.push({
            name: data.name
          });
        } else {
          nodes = data;
        }
        for (_i = 0, _len = nodes.length; _i < _len; _i++) {
          n = nodes[_i];
          li = _this.renderListElement(n, browseTemplate);
          _this.browseResults.append(li);
        }
        tmpl = _.template(breadcrumbsTemplate, {
          breadcrumbs: breadcrumbs
        });
        _this.browseBreadcrumbs.html(tmpl);
        _this.refreshResultState();
        if (typeof callback === "function") callback();
        return _this.browseResults.unblock();
      });
    },
    renderListElement: function(node, template, operator) {
      var li, optext;
      if (operator == null) operator = OPERATIONS.optional;
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
      optext = OPERATIONS[operator];
      li.addClass(optext).find('.icon').text(optext);
      li.data(node);
      return li;
    },
    refreshResultState: function() {
      var id, _results;
      $('li', this.browseResults).removeClass('added');
      $('button', this.browseResults).attr('disabled', false);
      $('li', this.searchResults).removeClass('added');
      $('button', this.searchResults).attr('disabled', false);
      _results = [];
      for (id in this.datasource) {
        $('li[data-id=' + id + ']', this.browseResults).addClass('added').find('button').attr('disabled', true);
        _results.push($('li[data-id=' + id + ']', this.searchResults).addClass('added').find('button').attr('disabled', true));
      }
      return _results;
    }
  });
});
