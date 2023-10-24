function getSectionsName(){
			res = [];
			$('.navButton').each(function(){
				res.push($(this).attr('id').split('_')[0]);
			})
			
			return res;
		}
		
		function readDatefromLS(field){
			let newObject = window.localStorage.getItem("feedDates");
			jsonObj = JSON.parse(newObject);
			
			return jsonObj[field]
		}
		
		function writeDateIntoLS(field, value){
			lsObject = window.localStorage.getItem("feedDates");
			if (lsObject){
				jsonObj = JSON.parse(lsObject);
				jsonObj[field] = value;
				window.localStorage.setItem("feedDates", JSON.stringify(jsonObj));
			} else {
				newObj = {};
				newObj[field] = value;
				window.localStorage.setItem("feedDates", JSON.stringify(newObj));
			}
			
			return true;
		} 
		
		function isYesterday(date) {
		  const yesterday = new Date();
		  yesterday.setUTCDate(yesterday.getUTCDate() - 1);

		  dateUTC = date.toUTCString().split(" ").slice(1, 4).join(' ')
		  yesterdayUTC = yesterday.toUTCString().split(" ").slice(1, 4).join(' ')

		  if (yesterdayUTC === dateUTC) {
			return true;
		  }

		  return false;
		}
		
		
		function updateNewDay(){
			var todayDate = new Date();
			var update = false;
			newObj = JSON.parse(window.localStorage.getItem("feedDates"));
			if (localStorage.feedDates){
				jsonObj = JSON.parse(window.localStorage.getItem("feedDates"));
				for (var key in jsonObj){
					date = new Date(jsonObj[key]);
					splitted = key.split('_');
					section = splitted[0]
					day = splitted[1]
					if (day == 'today' && jsonObj[key] !=0 && todayDate.getUTCDate() != date.getUTCDate()){
						if (isYesterday(date)){
							update = true;
							newObj[section + '_' + 'yesterday'] = new Date(jsonObj[key]).toUTCString();
							newObj[section + '_' + 'today'] = 0;
						} else{
							newObj[section + '_' + 'yesterday'] = 0;
							newObj[section + '_' + 'today'] = 0;
							update = true;
						}
						
					} else {
						continue
					}
				}
				if (update){
					window.localStorage.setItem("feedDates", JSON.stringify(newObj));
				}
			} else {
				return
			}
		}
		
		function generateAbout(){
			$('.filterRow').prop('hidden', true);
			$("#mainDiv").empty();
				
				aboutContent = '<div class="jumbotron">' + 
				  '<h1 class="display-5">Hello, friend!</h1>' +
				  '<p class="lead">My name is Mike and I made this website for infosecurity enthusiasts, bug hunters and everybody who interested in actual infosec news, blogposts and CVEs.</p>' +
				  '<p class="lead">' + 
					'You can suggest new RSS feed and I\'ll consider it for inclusion as source of information.'+
				  '</p>' +
				  '<p class="lead">' +
					'<ul>' + 
						'<li><i class="bi-github" style="font-size: 1rem; color: white;"></i> <a href="https://github.com/mike-n1" style="color:orange;">mike-n1</a></li>' +
						'<li><i class="bi-twitter-x" style="font-size: 1rem; color: white;"></i> <a href="https://twitter.com/m1ke_n1" style="color:orange;">m1ke_n1</a></li>' +
						'<li><i class="bi-telegram" style="font-size: 1rem; color: white;"></i> <a href="https://t.me/WebSecHack" style="color:orange;">WebSecHack</a> (RU only)</li>' +
					'<ul>' +
				  '</p>' +
				'</div>';
				
				$("#mainDiv").append(aboutContent);
		}
		
		function fillPage(pageName){
			
			window.currentPage = pageName;	
			
			switch (pageName){
			
				case 'blogs_today':
					jsonPath = "/states/today.json";
					break
				
				case 'blogs_yesterday':
					jsonPath = "/states/yesterday.json";
					break;
				case 'cve_today':
					jsonPath = "/states/cve_today.json";
					break;
				case 'cve_yesterday':
					jsonPath = "/states/cve_yesterday.json";
					break;
				case 'about':
					generateAbout();
					return;
					break;
					
				default:
					jsonPath = "/states/today.json";
					window.currentPage = 'blogs_today';	
			}
			if ($(".filterRow").prop("hidden")){
				$('.filterRow').removeAttr('hidden');
			}
			
			updateNewDay();
			
			if (!localStorage.feedDates){
				lastView = null;
			} else{
				lastView = new Date(readDatefromLS(window.currentPage));
			}
			
			$.ajaxSetup({ cache: false });
			$.getJSON(jsonPath, function(data) {
				window.utcStr = new Date().toUTCString();
				$.each( data, function(key, val) {
					$("#mainDiv").append($("<h3>").attr('class', 'itemh3 display-6').text(key));
					ulElem = $("<ul>");
					$.each(val, function(keyItem, valItem){
						liElem = $("<li>");
						aElement = $("<a>");
						
						aElement.attr('href', valItem['entry']['link']);
						aElement.attr('target','_blank');
						aElement.attr('class','link-light link-underline-opacity-25 link-underline-opacity-75-hover');
						aElement.text(valItem['entry']['title']);
						
						if (lastView){
							itemDate = new Date(valItem['fetchDate'] + 'Z');
							if (itemDate < lastView){
								aElement.text(valItem['entry']['title']);
								liElem.attr("class", "mb-2").append(aElement)
							} else {
								aElement.text(valItem['entry']['title']);
								liElem.attr("class", "mb-2").append(aElement)
								liElem.append(' <span class="badge rounded-pill bg-Success newBadge" style="font-size:0.7rem;">new</span>')
							}
						} else {
							aElement.text(valItem['entry']['title']);
							liElem.attr("class", "mb-2").append(aElement)
							liElem.append(' <span class="badge rounded-pill text-bg-success newBadge" style="font-size:0.7rem;">new</span>')
						}
						ulElem.append(liElem)
					})
					$("#mainDiv").append(ulElem);
				});
				mainDivLen = $('#mainDiv').html().length
				if (mainDivLen == 0){
					//$('#markAllButton').prop('hidden', true);
					$('#mainDiv').append('<h3>No items at the moment!</h3>');
					if (window.autoUpdate){
						writeDateIntoLS(window.currentPage, window.utcStr);
					} 
				} else{
					if (window.autoUpdate){
						writeDateIntoLS(window.currentPage, window.utcStr);
					} else {
						$('#markAllButton').removeAttr('hidden');
					}
				}
				
			}).fail(function() {
				$('#markAllButton').prop('hidden', true);
				$('#mainDiv').append('<h3 align="center">No items at the moment!</h3>')
			  	});
			
		}
		
		
		function updatePage(pageName){
			splittedName = pageName.split('_')
			if (splittedName.length == 2){
				window.location.hash = '#/' + splittedName[0] + '/' + splittedName[1]
			} else {
				window.location.hash = '#/' + splittedName[0]
			}
			$("#mainDiv").empty();
			fillPage(pageName)
		}
		
		$(document).ready(function(){
			if (window.localStorage.getItem("autoUpdate")){
				window.autoUpdate = JSON.parse(window.localStorage.getItem("autoUpdate"));
				if (!window.autoUpdate){
					$('#flexSwitchCheckChecked').prop('checked', false);
					$('#markAllButton').removeAttr('hidden');
				} else {
					$('#flexSwitchCheckChecked').prop('checked', true);
					$('#markAllButton').prop('hidden', true);
				}
			} else {
				window.localStorage.setItem("autoUpdate", false);
				window.autoUpdate = JSON.parse(window.localStorage.getItem("autoUpdate"));
				$('#markAllButton').removeAttr('hidden');
			}
			if (window.location.hash){
				splittedPageName = window.location.hash.substring(2).split('/')
				if (splittedPageName.length == 2){
					if (['today', 'yesterday'].includes(splittedPageName[1]) && getSectionsName().includes(splittedPageName[0])){
						$('input[type=radio][name=daySelector][id=' + splittedPageName[1] + ']').prop("checked", true);
						$('.navButton').each(function(){
							if ($(this).attr('id') == splittedPageName[0] + '_button') {
								$(this).addClass('active');
							} else {
								$(this).removeClass('active');
							}
						})
						fillPage(splittedPageName[0] + '_' + splittedPageName[1]);
					} else {
						fillPage('blogs_today');
					}
				} else {
					$('.navButton').each(function(){
						if ($(this).attr('id') == splittedPageName[0] + '_button') {
							$(this).addClass('active');
						} else {
							$(this).removeClass('active');
						}
					})
					fillPage(splittedPageName[0])
				}
			} else{
				fillPage('blogs_today');
			}
		})
		
		$('.navButton').on('click', function(){
			if ( $( this ).hasClass('active') ){
				return
			} else {
				$('.navButton').each(function(){
						$(this).removeClass('active');
				})
				$( this ).addClass('active');
				pageName = $( this ).attr('id').split('_')[0]
				if (!(pageName == 'about')){
					pageName = $( this ).attr('id').split('_')[0] + '_today';
					$('input[type=radio][name=daySelector][id=today]').prop("checked", true);
					updatePage(pageName);
				} else {
					updatePage(pageName);
				}	
			}
		})
		
		$('#flexSwitchCheckChecked').change(function(){
			if (this.checked) {
				window.localStorage.setItem("autoUpdate", true);
				window.autoUpdate = JSON.parse(window.localStorage.getItem("autoUpdate"))
				$('#markAllButton').prop('hidden', true);
			} else {
				window.localStorage.setItem("autoUpdate", false);
				window.autoUpdate = JSON.parse(window.localStorage.getItem("autoUpdate"))
				$('#markAllButton').removeAttr('hidden');
			}
		})
		
		$('#markAllButton').on('click', function(){
			writeDateIntoLS(window.currentPage, window.utcStr);
			$('.newBadge').remove();
		
		})
		
		$(document).on('click', 'a', function (e) {
			if ($(this).attr('href') == '#') {
				e.preventDefault();
			}
		});
		
		$('input[type=radio][name=daySelector]').change(function() {
			if (this.id == 'today'){
				section = window.currentPage.split('_')[0];
				updatePage(section + '_today')
			} else {
				section = window.currentPage.split('_')[0];
				updatePage(section + '_yesterday')
			}
		});