
define(['jquery', 'underscore', 'cilantro/define/viewelement', 'order!vendor/jquery.ui'], function($, _, ViewElement) {
  var OPERATIONS, breadcrumbsTemplate, browseTemplate, objectIsEmpty, searchResultsTemplate, stagedTemplate, vocabBrowserTemplate;
  breadcrumbsTemplate = '<% for (var b, i = 0; i < breadcrumbs.length; i++) { %>\n    <% b = breadcrumbs[i]; %>\n    <% if (i === (breadcrumbs.length-1)) {%>\n        <span title="<%= b.name %>"><%= b.name %></span>\n    <% } else { %>\n        <a href="<%= b.uri %>" title="<%= b.name %>"><%= b.name %></a> <span class="breadcrumb-arrow">&rarr;</span>\n    <% } %>\n<% } %>';
  browseTemplate = '<li data-id="<%= id %>" data-uri="<%= uri %>" <% if (!terminal) { %>class="folder"<% } %>>\n    <button class="button-add">+</button>\n    <span class="name"><%= name %>\n        <% if (attrs) { %>\n            <br><small class="info"><% for (var k in attrs) { %>\n                <%= k %>: <%= attrs[k] %>\n            <% } %></small>\n        <% } %>\n    </span>\n</li>';
  searchResultsTemplate = '<li data-id="<%= id %>" <% if (!terminal) { %>class="folder"<% } %>>\n    <button class="button-add">+</button>\n    <span>\n        <% if (search_only) { %>\n            <span><%= name %></span>\n        <% } else { %>\n            <a href="<%= parent.uri %>"><%= name %></a>\n        <% } %>\n        <% if (attrs) { %>\n            <br><small class="info"><% for (var k in attrs) { %>\n                <%= k %>: <%= attrs[k] %>\n            <% } %></small>\n        <% } %>\n    </span>\n</li>';
  stagedTemplate = '<li data-id="<%= id %>" <% if (!terminal) { %>class="folder"<% } %>>\n    <button class=button-remove>&dash;</button>\n    <% if (search_only) { %>\n        <span class=text><%= name %></span>\n    <% } else { %>\n        <a class=text href="<%= parent.uri %>"><%= name %></a>\n    <% } %>\n</li>';
  vocabBrowserTemplate = '<div id="vocab-browser-<%= pk %>" class="vocab-browser">\n    <% if (!search_only) { %>\n        <div class="vocab-tabs tabs">\n            <a class="tab" href="#browse-tab-<%= pk %>">Browse <%= title %></a>\n            <a class="tab" href="#search-tab-<%= pk %>">Search <%= title %></a>\n        </div>\n    <% } %>\n    <div>\n        <% if (!search_only) { %>\n            <div id="browse-tab-<%= pk %>">\n                <div class=vocab-breadcrumbs></div>\n                <ul class="vocab-browse-results list"></ul>\n            </div>\n        <% } %>\n\n        <div id="search-tab-<%= pk %>">\n            <form method="get" action="<%= directory %>">\n                <input type="text" class="vocab-search" name="q" placeholder="Search...">\n                <em>Note: only the first 100 results are displayed</em>\n            </form>\n            <div>\n                <ul class="vocab-search-results list">\n                    <li class="start">Enter search terms above. Results can be clicked to go to their location in the Browse tab.</li>\n                </ul>\n            </div>\n        </div>\n\n        <h2>Selected <%= title %></h2>\n\n        <small>Drag a <%= title.toLowerCase() %> to any bucket to customize\n        your query.</small>\n\n        <div class=vocab-staging>\n            <h3>At least one</h3>\n            <ul id=vocab-optional class=placeholder></ul>\n\n            <h3>Require</h3>\n            <ul id=vocab-require class=placeholder></ul>\n\n            <h3>Exclude</h3>\n            <ul id=vocab-exclude class=placeholder></ul>\n        </div>\n\n    </div>\n</div>';
  OPERATIONS = {
    require: 'all',
    exclude: '-all',
    optional: 'in'
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
      results = this.searchResults = $('.vocab-search-results', dom);
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
      var excludeTarget, optionalTarget, requireTarget, self, sortOptions, stagedItems,
        _this = this;
      stagedItems = $('.vocab-staging', dom);
      self = this;
      sortOptions = {
        forcePlaceholderSize: true,
        forceHelperSize: true,
        containment: this.dom,
        opacity: 0.5,
        cursor: 'move',
        connectWith: '.vocab-staging > ul',
        receive: function(event, ui) {
          var target;
          target = $(this);
          if (target.children().length === 1) target.removeClass('placeholder');
          if (ui.sender.children().length === 0) ui.sender.addClass('placeholder');
          return self.datasource[ui.item.data('id')] = target.data('operator');
        }
      };
      optionalTarget = $('#vocab-optional', dom).sortable(sortOptions);
      optionalTarget.data('operator', 'in');
      excludeTarget = $('#vocab-exclude', dom).sortable(sortOptions);
      excludeTarget.data('operator', '-all');
      requireTarget = $('#vocab-require', dom).sortable(sortOptions);
      requireTarget.data('operator', 'all');
      this.targets = {
        'in': optionalTarget,
        'all': requireTarget,
        '-all': excludeTarget
      };
      stagedItems.on('click', 'li button', function(event) {
        var item;
        item = $(event.target).parent();
        _this.unstageItem(item.data('id'));
        if (item.siblings().length === 0) item.parent().addClass('placeholder');
        item.remove();
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
      var li, target;
      if (operator == null) operator = OPERATIONS.optional;
      if (!this.datasource[node.id]) {
        li = this.renderListElement(node, stagedTemplate, true);
        target = this.targets[operator];
        target.removeClass('placeholder');
        target.append(li);
      }
      this.datasource[node.id] = operator;
      return this.refreshResultState();
    },
    unstageItem: function(id) {
      delete this.datasource[id];
      return this.refreshResultState();
    },
    constructQuery: function() {
      var children, data, event, key, len, operators, value, _ref;
      operators = {};
      data = {
        concept_id: this.concept_pk,
        custom: true
      };
      if (objectIsEmpty(this.datasource)) {
        event = $.Event('InvalidInputEvent');
        event.ephemeral = true;
        event.message = 'No value has been specified.';
        this.dom.trigger(event);
        return;
      }
      _ref = this.datasource;
      for (key in _ref) {
        value = _ref[key];
        if (!operators[value]) operators[value] = [];
        operators[value].push(key);
      }
      if ((len = _.keys(operators).length) === 0) {
        data.value = void 0;
      } else if (len === 1) {
        data.id = this.viewset.pk;
        data.value = operators[value];
        data.operator = value;
      } else {
        children = [];
        for (key in operators) {
          value = operators[key];
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
        var li, node, nodes, tmpl, _i, _len;
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
          node = nodes[_i];
          li = _this.renderListElement(node, browseTemplate);
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
    renderListElement: function(node, template) {
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
      return $(_.template(template, node)).data(node);
    },
    refreshResultState: function() {
      var id, _results;
      if (!this.viewset.search_only) {
        $('li', this.browseResults).removeClass('added');
        $('button', this.browseResults).attr('disabled', false);
      }
      $('li', this.searchResults).removeClass('added');
      $('button', this.searchResults).attr('disabled', false);
      _results = [];
      for (id in this.datasource) {
        if (!this.viewset.search_only) {
          this.browseResults.find('li[data-id=' + id + ']').addClass('added').find('button').attr('disabled', true);
        }
        _results.push(this.searchResults.find('li[data-id=' + id + ']').addClass('added').find('button').attr('disabled', true));
      }
      return _results;
    }
  });
});
