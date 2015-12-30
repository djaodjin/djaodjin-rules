/*=============================================================================
  Apps
  ============================================================================*/

var app = angular.module("ruleApp", ["ui.bootstrap", "ngDragDrop", "ngRoute",
    "ruleControllers", "ruleServices"]);

app.config(["$resourceProvider", function ($resourceProvider) {
    "use strict";
    // Don't strip trailing slashes from calculated URLs
    $resourceProvider.defaults.stripTrailingSlashes = false;
}]);

// directive for a single list
app.directive("dndList", function() {
    "use strict";

    return function(scope, element, attrs) {

        // variables used for dnd
        var toUpdate;
        var startIndex = -1;

        // watch the model, so we always know what element
        // is at a specific position
        scope.$watch(attrs.dndList, function(value) {
            toUpdate = value;
        }, true);

        // use jquery to make the element sortable (dnd). This is called
        // when the element is rendered
        $(element[0]).sortable({
            items: "tr",
            start: function (event, ui) {
                // on start we define where the item is dragged from
                startIndex = ($(ui.item).index());
            },
            stop: function (event, ui) {
                // on stop we determine the new index of the
                // item and store it there
                var newIndex = ($(ui.item).index());
                var oldRank = toUpdate[startIndex].rank;
                var newRank = toUpdate[newIndex].rank;
                scope.saveOrder(oldRank, newRank);
            },
            axis: "y"
        });
    };
});


/*=============================================================================
  Services
  ============================================================================*/

/* extension to AngularJS to send a PUT request on update instead of a POST. */
var ruleResources = angular.module( "my.resource", [ "ngResource" ] );
ruleResources.factory( "Resource", [ "$resource", function( $resource ) {
    "use strict";
    return function( url, params, methods, options ) {
        var defaults = {
            query: { method: "GET", isArray: false },
            update: { method: "put", isArray: false },
            create: { method: "post" }
        };

        methods = angular.extend( defaults, methods );

        var resource = $resource( url, params, methods, options );

        resource.prototype.$save = function() {
            if ( !this.rank ) {
                this.rank = 0;
                return this.$create();
            }
            else {
                return this.$update();
            }
        };

        return resource;
    };
}]);

var ruleServices = angular.module("ruleServices", ["my.resource"]);

/* Implementation Note:
   *stripTrailingSlashes* is only available in Angularjs 1.3
   Technically we would like to pass stripTrailingSlashes as an option
   which seems possible from the documentation (1.3.0-beta15). Other
   parts of the documentation indicates to set the defaults property directly,
   which we do here. It seems to be a workaround the fact that the options
   are not passed to the call to *resourceFactory* in angular-resource.js.
*/
ruleServices.factory("Rule", ["Resource", "urls",
  function($resource, urls){
    "use strict";
    return $resource(
        // No slash, it is already part of @path.
        urls.rules_api_rule_url, {},
        {saveData: {method: "PATCH", isArray: true},
         update: { method: "put", isArray: false,
                   url: urls.rules_api_rule_url + ":rule",
                   params: {"rule": "@path"}},
         remove: { method: "delete", isArray: false,
                   url: urls.rules_api_rule_url + ":rule",
                   params: {"rule": "@path"}},
         create: { method: "POST" }},
        {stripTrailingSlashes: false}); // only in Angularjs 1.3
  }]);

/*=============================================================================
  Controllers
  ============================================================================*/

var ruleControllers = angular.module("ruleControllers", []);

ruleControllers.controller("RuleListCtrl",
    ["$scope", "$http", "Rule", "urls", function($scope, $http, Rule, urls) {
    "use strict";
    $scope.params = {};
    $scope.itemsPerPage = 25; // Must match on the server-side.
    $scope.maxSize = 5;      // Total number of pages to display
    $scope.currentPage = 1;
    $scope.totalItems = 0;

    $scope.newRule = new Rule();

    $scope.refresh = function() {
        $scope.rules = Rule.query($scope.params, function() {
            /* We cannot watch rules.count otherwise things start
               to snowball. We must update totalItems only when
               it truly changed. */
            if( $scope.rules.count !== $scope.totalItems ) {
                $scope.totalItems = $scope.rules.count;
            }
        });
    };
    $scope.refresh();

    $scope.pageChanged = function() {
        if( $scope.currentPage > 1 ) {
            $scope.params.page = $scope.currentPage;
        } else {
            delete $scope.params.page;
        }
        $scope.refresh();
    };

    $scope.save = function(rule, success) {
        if ( !rule.rank ) {
            rule.rank = 0;
            return Rule.create($scope.params, rule, success, function(data) {
                // error
                showMessages(["An error occurred while creating a rule (" +
                  data.status + " " + data.statusText +
                  "). Please accept our apologies."], "error");
            });
        }
        else {
            return Rule.update($scope.params, rule, success, function(data) {
                // error
                showMessages(["An error occurred while updating a rule (" +
                  data.status + " " + data.statusText +
                  "). Please accept our apologies."], "error");
            });
        }
    };

    $scope.remove = function (idx) {
        Rule.remove({rule: $scope.rules.results[idx].path}, function (success) {
            $scope.rules.results.splice(idx, 1);
        });
    };

    $scope.create = function() {
        $scope.save($scope.newRule, function(result) {
            // success: insert new rule in the list and reset our editor
            // to a new blank.
            $scope.rules.results.push(result);
            $scope.newRule = new Rule();
        });
    };

    /* Click on the is_forward checkbox propagates the change
       through the REST API. */
    $scope.updateForward = function(rule) {
        $scope.save(rule);
    };

    /* Click on the rule op checkbox propagates the change
       through the REST API. */
    $scope.updateAllow = function(rule) {
        $scope.save(rule);
    };

    $scope.saveOrder = function(startIndex, newIndex) {
        Rule.saveData([{oldpos: startIndex, newpos: newIndex}],
            function success(data) {
                $scope.rules = data;
            }, function err(data) {
                // error
                showMessages(["An error occurred while updating a rule (" +
                  data.status + " " + data.statusText +
                  "). Please accept our apologies."], "error");
            });
    };
}]);
