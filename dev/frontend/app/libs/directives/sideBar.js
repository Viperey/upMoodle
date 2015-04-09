angular.module('upmApp').directive('sidebar', function(){

	return {
		restrict: 'EA',
		templateUrl: 'views/sidebar.html',
		controller: function($scope, api, $location, User) {
			$scope.subjects = User.model.subjects
		} 
	};
}); 