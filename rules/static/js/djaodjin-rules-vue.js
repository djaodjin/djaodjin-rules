Vue.directive('sortable', {
  inserted: function (el, binding) {
    new Sortable(el, binding.value || {})
  }
})

function isFunction(f){
    // https://stackoverflow.com/a/7356528/1491475
    return f && {}.toString.call(f) === '[object Function]';
}

function isObject(o){
    // https://stackoverflow.com/a/46663081/1491475
    return o instanceof Object && o.constructor === Object
}

var DATE_FORMAT = 'MMM DD, YYYY';

function handleRequestError(resp){
    showErrorMessages(resp);
}

var httpRequestMixin = {
    // basically a wrapper around jQuery ajax functions
    methods: {
        /** This method generates a GET HTTP request to `url` with a query
            string built of a `queryParams` dictionnary.
            It supports the following prototypes:
            - reqGet(url, successCallback)
            - reqGet(url, queryParams, successCallback)
            - reqGet(url, queryParams, successCallback, failureCallback)
            - reqGet(url, successCallback, failureCallback)
            `queryParams` when it is specified is a dictionnary
            of (key, value) pairs that is converted to an HTTP
            query string.
            `successCallback` and `failureCallback` must be Javascript
            functions (i.e. instance of type `Function`).
        */
        reqGet: function(url, arg, arg2, arg3){
            var vm = this;
            var queryParams, successCallback;
            var failureCallback = handleRequestError;
            if(typeof url != 'string') throw 'url should be a string';
            if(isFunction(arg)){
                // We are parsing reqGet(url, successCallback)
                // or reqGet(url, successCallback, errorCallback).
                successCallback = arg;
                if(isFunction(arg2)){
                    // We are parsing reqGet(url, successCallback, errorCallback)
                    failureCallback = arg2;
                } else if( arg2 !== undefined ) {
                    throw 'arg2 should be a failureCallback function';
                }
            } else if(isObject(arg)){
                // We are parsing
                // reqGet(url, queryParams, successCallback)
                // or reqGet(url, queryParams, successCallback, errorCallback).
                queryParams = arg;
                if(isFunction(arg2)){
                    // We are parsing reqGet(url, queryParams, successCallback)
                    // or reqGet(url, queryParams, successCallback, errorCallback).
                    successCallback = arg2;
                    if(isFunction(arg3)){
                        // We are parsing reqGet(url, queryParams, successCallback, errorCallback)
                        failureCallback = arg3;
                    } else if( arg3 !== undefined ){
                        throw 'arg3 should be a failureCallback function';
                    }
                } else {
                    throw 'arg2 should be a successCallback function';
                }
            } else {
                throw 'arg should be a queryParams Object or a successCallback function';
            }
            return $.ajax({
                url: url,
                data: queryParams,
                traditional: true,
            }).done(successCallback).fail(failureCallback);
        },
        /** This method generates a POST HTTP request to `url` with
            contentType 'application/json'.
            It supports the following prototypes:
            - reqPOST(url, data)
            - reqPOST(url, data, successCallback)
            - reqPOST(url, data, successCallback, failureCallback)
            - reqPOST(url, successCallback)
            - reqPOST(url, successCallback, failureCallback)
            `data` when it is specified is a dictionnary of (key, value) pairs
            that is passed as a JSON encoded body.
            `successCallback` and `failureCallback` must be Javascript
            functions (i.e. instance of type `Function`).
        */
        reqPost: function(url, arg, arg2, arg3){
            var vm = this;
            var data, successCallback;
            var failureCallback = handleRequestError;
            if(typeof url != 'string') throw 'url should be a string';
            if(isFunction(arg)){
                // We are parsing reqPost(url, successCallback)
                // or reqPost(url, successCallback, errorCallback).
                successCallback = arg;
                if(isFunction(arg2)){
                    // We are parsing reqPost(url, successCallback, errorCallback)
                    failureCallback = arg2;
                } else if (arg2 !== undefined){
                    throw 'arg2 should be a failureCallback function';
                }
            } else if(isObject(arg)){
                // We are parsing reqPost(url, data)
                // or reqPost(url, data, successCallback)
                // or reqPost(url, data, successCallback, errorCallback).
                data = arg;
                if(isFunction(arg2)){
                    // We are parsing reqPost(url, data, successCallback)
                    // or reqPost(url, data, successCallback, errorCallback).
                    successCallback = arg2;
                    if(isFunction(arg3)){
                        // We are parsing reqPost(url, data, successCallback, errorCallback)
                        failureCallback = arg3;
                    } else if (arg3 !== undefined){
                        throw 'arg3 should be a failureCallback function';
                    }
                } else if (arg2 !== undefined){
                    throw 'arg2 should be a successCallback function';
                }
            } else if (arg !== undefined){
                throw 'arg should be a data Object or a successCallback function';
            }

            return $.ajax({
                url: url,
                contentType: 'application/json',
                data: JSON.stringify(data),
                method: 'POST',
            }).done(successCallback).fail(failureCallback);
        },
        /** This method generates a PUT HTTP request to `url` with
            contentType 'application/json'.
            It supports the following prototypes:
            - reqPUT(url, data)
            - reqPUT(url, data, successCallback)
            - reqPUT(url, data, successCallback, failureCallback)
            - reqPUT(url, successCallback)
            - reqPUT(url, successCallback, failureCallback)
            `data` when it is specified is a dictionnary of (key, value) pairs
            that is passed as a JSON encoded body.
            `successCallback` and `failureCallback` must be Javascript
            functions (i.e. instance of type `Function`).
        */
        reqPut: function(url, arg, arg2, arg3){
            var vm = this;
            var data, successCallback;
            var failureCallback = handleRequestError;
            if(typeof url != 'string') throw 'url should be a string';
            if(isFunction(arg)){
                // We are parsing reqPut(url, successCallback)
                // or reqPut(url, successCallback, errorCallback).
                successCallback = arg;
                if(isFunction(arg2)){
                    // We are parsing reqPut(url, successCallback, errorCallback)
                    failureCallback = arg2;
                } else if (arg2 !== undefined){
                    throw 'arg2 should be a failureCallback function';
                }
            } else if(isObject(arg)){
                // We are parsing reqPut(url, data)
                // or reqPut(url, data, successCallback)
                // or reqPut(url, data, successCallback, errorCallback).
                data = arg;
                if(isFunction(arg2)){
                    // We are parsing reqPut(url, data, successCallback)
                    // or reqPut(url, data, successCallback, errorCallback).
                    successCallback = arg2;
                    if(isFunction(arg3)){
                        // We are parsing reqPut(url, data, successCallback, errorCallback)
                        failureCallback = arg3;
                    } else if (arg3 !== undefined){
                        throw 'arg3 should be a failureCallback function';
                    }
                } else if (arg2 !== undefined){
                    throw 'arg2 should be a successCallback function';
                }
            } else if (arg !== undefined){
                throw 'arg should be a data Object or a successCallback function';
            }

            return $.ajax({
                url: url,
                contentType: 'application/json',
                data: JSON.stringify(data),
                method: 'PUT',
            }).done(successCallback).fail(failureCallback);
        },
        /** This method generates a PATCH HTTP request to `url` with
            contentType 'application/json'.
            It supports the following prototypes:
            - reqPATCH(url, data)
            - reqPATCH(url, data, successCallback)
            - reqPATCH(url, data, successCallback, failureCallback)
            - reqPATCH(url, successCallback)
            - reqPATCH(url, successCallback, failureCallback)
            `data` when it is specified is a dictionnary of (key, value) pairs
            that is passed as a JSON encoded body.
            `successCallback` and `failureCallback` must be Javascript
            functions (i.e. instance of type `Function`).
        */
        reqPatch: function(url, arg, arg2, arg3){
            var vm = this;
            var data, successCallback;
            var failureCallback = handleRequestError;
            if(typeof url != 'string') throw 'url should be a string';
            if(isFunction(arg)){
                // We are parsing reqPatch(url, successCallback)
                // or reqPatch(url, successCallback, errorCallback).
                successCallback = arg;
                if(isFunction(arg2)){
                    // We are parsing reqPatch(url, successCallback, errorCallback)
                    failureCallback = arg2;
                } else if (arg2 !== undefined){
                    throw 'arg2 should be a failureCallback function';
                }
            } else if(isObject(arg)){
                // We are parsing reqPatch(url, data)
                // or reqPatch(url, data, successCallback)
                // or reqPatch(url, data, successCallback, errorCallback).
                data = arg;
                if(isFunction(arg2)){
                    // We are parsing reqPatch(url, data, successCallback)
                    // or reqPatch(url, data, successCallback, errorCallback).
                    successCallback = arg2;
                    if(isFunction(arg3)){
                        // We are parsing reqPatch(url, data, successCallback, errorCallback)
                        failureCallback = arg3;
                    } else if (arg3 !== undefined){
                        throw 'arg3 should be a failureCallback function';
                    }
                } else if (arg2 !== undefined){
                    throw 'arg2 should be a successCallback function';
                }
            } else if (arg !== undefined){
                throw 'arg should be a data Object or a successCallback function';
            }

            return $.ajax({
                url: url,
                contentType: 'application/json',
                data: JSON.stringify(data),
                method: 'PATCH',
            }).done(successCallback).fail(failureCallback);
        },
        /** This method generates a DELETE HTTP request to `url` with a query
            string built of a `queryParams` dictionnary.
            It supports the following prototypes:
            - reqDELETE(url)
            - reqDELETE(url, successCallback)
            - reqDELETE(url, successCallback, failureCallback)
            `successCallback` and `failureCallback` must be Javascript
            functions (i.e. instance of type `Function`).
        */
        reqDelete: function(url, arg, arg2){
            var vm = this;
            var data, successCallback;
            var failureCallback = handleRequestError;
            if(typeof url != 'string') throw 'url should be a string';
            if(isFunction(arg)){
                // We are parsing reqDelete(url, successCallback)
                // or reqDelete(url, successCallback, errorCallback).
                successCallback = arg;
                if(isFunction(arg2)){
                    // We are parsing reqDelete(url, successCallback, errorCallback)
                    failureCallback = arg2;
                } else if (arg2 !== undefined){
                    throw 'arg2 should be a failureCallback function';
                }
            } else if (arg !== undefined){
                throw 'arg should be a successCallback function';
            }

            return $.ajax({
                url: url,
                method: 'DELETE',
            }).done(successCallback).fail(failureCallback);
        },
    }
}

var itemListMixin = {
    data: function(){
        return this.getInitData();
    },
    mixins: [httpRequestMixin],
    methods: {
        getInitData: function(){
            data = {
                url: '',
                itemsLoaded: false,
                items: {
                    results: [],
                    count: 0
                },
                mergeResults: false,
                params: {
                    // The following dates will be stored as `String` objects
                    // as oppossed to `moment` or `Date` objects because this
                    // is how uiv-date-picker will update them.
                    start_at: null,
                    ends_at: null
                },
                getCb: null,
                getCompleteCb: null,
                getBeforeCb: null,
            }
            if( djaodjinSettings.date_range ) {
                if( djaodjinSettings.date_range.start_at ) {
                    data.params['start_at'] = moment(
                        djaodjinSettings.date_range.start_at).format(DATE_FORMAT);
                }
                if( djaodjinSettings.date_range.ends_at ) {
                    // uiv-date-picker will expect ends_at as a String
                    // but DATE_FORMAT will literally cut the hour part,
                    // regardless of timezone. We don't want an empty list
                    // as a result.
                    // If we use moment `endOfDay` we get 23:59:59 so we
                    // add a full day instead.
                    data.params['ends_at'] = moment(
                        djaodjinSettings.date_range.ends_at).add(1,'days').format(DATE_FORMAT);
                }
            }
            return data;
        },
        get: function(){
            var vm = this;
            if(!vm.url) return
            if(!vm.mergeResults){
                vm.itemsLoaded = false;
            }
            if(vm[vm.getCb]){
                var cb = function(res){
                    vm[vm.getCb](res);

                    if(vm[vm.getCompleteCb]){
                        vm[vm.getCompleteCb]();
                    }
                }
            } else {
                var cb = function(res){
                    if(vm.mergeResults){
                        res.results = vm.items.results.concat(res.results);
                    }
                    vm.items = res;
                    vm.itemsLoaded = true;

                    if(vm[vm.getCompleteCb]){
                        vm[vm.getCompleteCb]();
                    }
                }
            }
            if(vm[vm.getBeforeCb]){
                vm[vm.getBeforeCb]();
            }
            vm.reqGet(vm.url, vm.getParams(), cb);
        },
        getParams: function(excludes){
            var vm = this;
            var params = {};
            for( var key in vm.params ) {
                if( vm.params.hasOwnProperty(key) && vm.params[key] ) {
                    if( excludes && key in excludes ) continue;
                    if( key === 'start_at' || key === 'ends_at' ) {
                        params[key] = moment(vm.params[key], DATE_FORMAT).toISOString();
                    } else {
                        params[key] = vm.params[key];
                    }
                }
            }
            return params;
        },
        getQueryString: function(excludes){
            var vm = this;
            var sep = "";
            var result = "";
            var params = vm.getParams(excludes);
            for( var key in params ) {
                if( params.hasOwnProperty(key) ) {
                    result += sep + key + '=' + params[key].toString();
                    sep = "&";
                }
            }
            if( result ) {
                result = '?' + result;
            }
            return result;
        },
        humanizeTotal: function() {
            var vm = this;
            var filter = Vue.filter('humanizeCell');
            return filter(vm.items.total, vm.items.unit, 0.01);
        },
        humanizeBalance: function() {
            var vm = this;
            var filter = Vue.filter('humanizeCell');
            return filter(vm.items.balance, vm.items.unit, 0.01);
        },
    },
}

var itemMixin = {
    mixins: [itemListMixin],
    data: {
        item: {},
        itemLoaded: false,
    },
    methods: {
        get: function(){
            var vm = this;
            if(!vm.url) return
            if(vm[vm.getCb]){
                var cb = vm[vm.getCb];
            } else {
                var cb = function(res){
                    vm.item = res
                    vm.itemLoaded = true;
                }
            }
            vm.reqGet(vm.url, vm.getParams(), cb);
        },
    },
}

var paginationMixin = {
    data: function(){
        return {
            params: {
                page: 1,
            },
            itemsPerPage: djaodjinSettings.itemsPerPage,
            getCompleteCb: 'getCompleted',
            getBeforeCb: 'resetPage',
            qsCache: null,
            isInfiniteScroll: false,
        }
    },
    methods: {
        resetPage: function(){
            var vm = this;
            if(!vm.ISState) return;
            if(vm.qsCache && vm.qsCache !== vm.qs){
                vm.params.page = 1;
                vm.ISState.reset();
            }
            vm.qsCache = vm.qs;
        },
        getCompleted: function(){
            var vm = this;
            if(!vm.ISState) return;
            vm.mergeResults = false;
            if(vm.pageCount > 0){
                vm.ISState.loaded();
            }
            if(vm.params.page >= vm.pageCount){
                vm.ISState.complete();
            }
        },
        paginationHandler: function($state){
            var vm = this;
            if(!vm.ISState) return;
            if(!vm.itemsLoaded){
                // this handler is triggered on initial get too
                return;
            }
            // rudimentary way to detect which type of pagination
            // is active. ideally need to monitor resolution changes
            vm.isInfiniteScroll = true;
            var nxt = vm.params.page + 1;
            if(nxt <= vm.pageCount){
                vm.$set(vm.params, 'page', nxt);
                vm.mergeResults = true;
                vm.get();
            }
        },
    },
    computed: {
        totalItems: function(){
            return this.items.count
        },
        pageCount: function(){
            return Math.ceil(this.totalItems / this.itemsPerPage)
        },
        ISState: function(){
            if(!this.$refs.infiniteLoading) return;
            return this.$refs.infiniteLoading.stateChanger;
        },
        qs: function(){
            return this.getQueryString({page: null});
        },
    }
}

if($('#rules-table').length > 0){
var rtable = new Vue({
    el: "#rules-table",
    data: function(){
        return {
            url: djaodjinSettings.urls.rules.api_rules,
            itemsLoaded: false,
            items: {
                results: [],
                count: 0
            },
            params: {},
            ruleModalOpen: false,
            newRule: {
                path: '',
                rank: 0,
                is_forward: false,
            },
            edit_description: [],
        }
    },
    mixins: [
        itemListMixin,
        paginationMixin,
    ],
    methods: {
        moved: function(e){
            var vm = this;
            var oldRank = vm.items.results[e.oldIndex].rank;
            var newRank = vm.items.results[e.newIndex].rank;
            var pos = [{oldpos: oldRank, newpos: newRank}];
            $.ajax({
                method: 'PATCH',
                url: vm.url,
                contentType: 'application/json',
                data: JSON.stringify({"updates": pos}),
            }).done(function (resp) {
// XXX The following does not update the rules as would be expected.
//     As a workaround, we call get() here.
//                vm.items = resp;
//                vm.itemsLoaded = true;
                vm.get();
            }).fail(function(resp){
                showErrorMessages(resp);
            });
        },
        create: function(){
            var vm = this;
            $.ajax({
                method: 'POST',
                url: vm.url,
                contentType: 'application/json',
                data: JSON.stringify(vm.newRule),
            }).done(function (resp) {
                vm.get();
                vm.newRule = {
                    path: '',
                    rank: 0,
                    is_forward: false,
                }
                vm.ruleModalOpen = false;
            }).fail(function(resp){
                vm.ruleModalOpen = false;
                showErrorMessages(resp);
            });
        },
        update: function(rule){
            var vm = this;
            var url = vm.url + rule.path;
            $.ajax({
                method: 'PUT',
                url: url,
                contentType: 'application/json',
                data: JSON.stringify(rule),
            }).done(function (resp) {
                vm.ruleModalOpen = false;
            }).fail(function(resp){
                vm.ruleModalOpen = false;
                showErrorMessages(resp);
            });
        },
        remove: function(idx){
            var vm = this;
            var rule = vm.items.results[idx]
            var url = vm.url + rule.path;
            $.ajax({
                method: 'DELETE',
                url: url,
            }).done(function (resp) {
                vm.params.page = 1;
                vm.get();
            }).fail(function(resp){
                showErrorMessages(resp);
            });
        },
        editDescription: function(idx){
            var vm = this;
            vm.edit_description = Array.apply(
                null, new Array(vm.items.results.length)).map(function() {
                return false;
            });
            vm.$set(vm.edit_description, idx, true)
            // at this point the input is rendered and visible
            vm.$nextTick(function(){
                vm.$refs.edit_description_input[idx].focus();
            });
        },
        saveDescription: function(coupon, idx, event){
            if (event.which === 13 || event.type === "blur" ){
                this.$set(this.edit_description, idx, false)
                this.update(this.items.results[idx])
            }
        },
    },
    mounted: function(){
        this.get();
    }
});

$('#new-rule').on('shown.bs.modal', function(){
    var self = $(this);
    self.find('[name="new_rule_path"]').focus();
});

} // $('#rules-table').length > 0

if($('#rule-list-container').length > 0){
var app = new Vue({
    el: "#rule-list-container",
    data: {
        sessionKey: gettext('Generating...'),
        testUsername: '',
        forward_session: '',
        forward_session_header: '',
        forward_url: '',
    },
    methods: {
        generateKey: function(){
            var vm = this;
            $.ajax({
                method: 'PUT',
                url: djaodjinSettings.urls.rules.api_generate_key,
            }).done(function (resp) {
                vm.sessionKey = resp.enc_key;
            }).fail(function(resp){
                vm.sessionKey = gettext("ERROR");
                showErrorMessages(resp);
            });
        },
        getSessionData: function(){
            var vm = this;
            var url = djaodjinSettings.urls.rules.api_session_data + "/" + vm.testUsername;
            $.ajax({
                method: 'GET',
                url: url,
            }).done(function(resp) {
                vm.forward_session = resp.forward_session;
                vm.forward_session_header = resp.forward_session_header;
                vm.forward_url = resp.forward_url;
            }).fail(function(resp){
                showErrorMessages(resp);
            });
        },
        update: function(submitEntryPoint) {
            var vm = this;
            var data = {
                authentication: vm.$refs.authentication.value,
                welcome_email: vm.$refs.welcomeEmail.checked,
                session_backend: vm.$refs.sessionBackend.value,
            }
            if( submitEntryPoint ) {
                data['entry_point'] = vm.$refs.entryPoint.value;
            }
            $.ajax({
                method: 'PUT',
                url: djaodjinSettings.urls.rules.api_detail,
                contentType: 'application/json',
                data: JSON.stringify(data),
            }).done(function (resp) {
                showMessages([gettext("Update successful.")], "success");
            }).fail(function(resp){
                showErrorMessages(resp);
            });
        },
    },
})
}

if($('#user-engagement-container').length > 0){
var app = new Vue({
    el: "#user-engagement-container",
    data: {
        url: djaodjinSettings.urls.rules.api_user_engagement,
    },
    mixins: [
        itemListMixin,
    ],
    computed: {
        tags: function(){
            var tags = [];
            this.items.results.forEach(function(e){
                tags = tags.concat(e.engagements).filter(function(value, index, self){
                    return self.indexOf(value) === index;
                });
            });
            return tags;
        }
    },
    mounted: function(){
        this.get();
    },
});
}

if($('#engagement-users-container').length > 0){
new Vue({
    el: "#engagement-users-container",
    mixins: [itemMixin],
    data: function(){
        return {
            url: djaodjinSettings.urls.rules.api_engagement,
            params: {
                timezone: moment.tz.guess(),
            },
            getCb: 'getAndChart',
        }
    },
    methods: {
        getAndChart: function(res){
            var vm = this;
            vm.itemLoaded = true;
            vm.$set(vm.item, 'activeUsers', res.active_users);
            vm.$set(vm.item, 'engagements', res.engagements);
            var el = vm.$refs.engagementChart;

            // nvd3 is available on djaoapp
            if(vm.item.engagements.length === 0 || !el || !nv) return;

            nv.addGraph(function() {
                var data = [{
                    "key": "Engagements",
                    "values": vm.item.engagements.map(function(e){
                      return {
                        "label": e.slug,
                        "value" : e.count
                      }
                    })
                }];
                var chart = nv.models.multiBarHorizontalChart()
                    .x(function(d) { return d.label })
                    .y(function(d) { return d.value })
                    .barColor(nv.utils.defaultColor())
                    .showValues(true)
                    .showLegend(false)
                    .showControls(false)
                    .showXAxis(false)
                    .showYAxis(false)
                    .groupSpacing(0.02)
                    .margin({top: 0, right: 0, bottom: 0, left: 0});

                d3.select(el)
                    .datum(data)
                    .call(chart);

                // centering logic
                var height = parseInt(d3.select(".positive rect").attr('height'));
                var y = (height / 2) + 3; // 3 is a magic number
                // add labels inside bars
                d3.selectAll(".positive").append("text")
                    .style('fill', 'white')
                    .text(function(d){ return d.label })
                    .attr('x', '10')
                    .attr('y', y)

                chart.tooltip.enabled(false);

                nv.utils.windowResize(chart.update);

                return chart;
            });
        },
    },
    mounted: function(){
        this.get();
    }
})
}
