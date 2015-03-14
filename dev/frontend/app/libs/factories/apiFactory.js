angular.module('upmApp').factory('api', function($http, $cookies){
	var base_url = 'http://127.0.0.1:8000/';
	var user_pics_url = base_url + "media/";

	return {

		getPic : function(url){
			return user_pics_url + url;			
		},

		getUser : function(){
			return $http({ 
				method: 'GET', 
				url:  base_url + 'user/'
			});
		},

		updateUser : function(user){
			return $http({ 
				method: 'POST', 
				url:  base_url + 'user/',
				headers: {'Content-Type': 'application/x-www-form-urlencoded'},
				transformRequest: function(obj) {
					var str = [];
					for(var p in obj)
						str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
					return str.join("&");
				},
				data: user.password ? 
					{email: user.email, name: user.name, nick: user.nick, password: user.password} :
					{email: user.email, name: user.name, nick: user.nick}
			});
		},

		login : function(userEmail, userPassword){
			return $http({ 
				method: 'post', 
				url:  base_url + 'login/',
				headers: {'Content-Type': 'application/x-www-form-urlencoded'},
				transformRequest: function(obj) {
					var str = [];
					for(var p in obj)
						str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
					return str.join("&");
				},
				data : {email: userEmail, password: userPassword}
			});
		},

		signup : function(email, password, nick){
			return $http({ 
				method: 'post', 
				url:  base_url + 'signup/',
				headers: {'Content-Type': 'application/x-www-form-urlencoded'},
				transformRequest: function(obj) {
					var str = [];
					for(var p in obj)
						str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
					return str.join("&");
				},
				data : {email: email, password: password, nick: nick}
			});
		},

		logout : function(){
			return $http({ 
				method: 'POST', 
				url:  base_url + 'logout/'
			});	
		},

		recoverPassword : function(email){
			return $http({ 
				method: 'POST', 
				url:  base_url + 'recover_password/',
				headers: {'Content-Type': 'application/x-www-form-urlencoded'},
				transformRequest: function(obj) {
					var str = [];
					for(var p in obj)
						str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
					return str.join("&");
				},
			data: {email: email}
			});	
		},

		confirmEmail : function(token){  
			return $http({     
				method: 'GET',      
				url:  base_url + 'confirm_email/' + token +"/"
			});
		}
	} 
});  