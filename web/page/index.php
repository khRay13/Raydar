<html>
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width = device-width, initial-scale = 1, shrink-to-fit = no">
	<meta name="systemname" content="Raydar">
	<meta name="description" content="Shipdt Daily Report">
	<meta name="author" content="Ray">
	<meta name="keywords" content="Raydar; wannacrawl">
	<meta name="copyright" content="FCF Co., Ltd.">
	<meta name="distribution" content="Taiwan">

	<title>Raydar - Daily Report</title>

	<!--JQuery Series-->
	<script src="https://code.jquery.com/jquery-3.5.1.min.js" integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0=" crossorigin="anonymous"></script>
	<script type="text/javascript" src="/js/jquery.cookie.js"></script>

	<!-- Font -->
	<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC&amp;display=swap" rel="stylesheet">

	<!-- Popper.js -->
	<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js" integrity="sha384-b/U6ypiBEHpOf/4+1nzFpr53nxSS+GLCkfwBdFNTxtclqqenISfwAzpKaMNFNmj4" crossorigin="anonymous"></script>

	<!--BootstrapcoreCSS-->
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z" crossorigin="anonymous">

	<!--BootstrapcoreJS-->
	<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js" integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8shuf57BaghqFfPlYxofvL8/KUEfYiJOMMV+rV" crossorigin="anonymous"></script>
	<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js" integrity="sha384-LtrjvnR4Twt/qOuYxE721u19sVFLVSA4hf/rRt6PrZTmiPltdZcI7q7PXQBYTKyf" crossorigin="anonymous"></script>

	<script>
		$(function() {
			var iframe = $("#frm_DailyBK");

			$(window).scroll(function() {
				var width  = $(window).width();
				var scroll = $(window).scrollTop();

				if(scroll >= 100) {
					$(".gototop").fadeIn();
					// 畫面寬度小於560px才顯示menu button
					if (width <= 560) {
						$("#row_head").fadeOut();
						$(".sidemenu").fadeIn();
						$(".sidemenu_content").fadeIn();
						$('#nav', iframe.contents()).css("display", "none")
					}
				} else {
					$("#row_head").fadeIn();
					$(".gototop").fadeOut();
					$(".sidemenu").fadeOut();
					$(".sidemenu_content").fadeOut();
					$('#nav', iframe.contents()).css("display", "")
				}
			});

			$(".sidemenu").click(function() {
				var e_class = $("#side_menu_ctn").attr("class");
				// 依關鍵字做狀態更改
				e_class.includes("slideIn")?sideOut():sideIn();
			});

			function sideIn() {
				$("#side_menu_ctn").removeClass("sidemenu_content_slideOut");
				$("#side_menu_ctn").addClass("sidemenu_content_slideIn");
			}

			function sideOut() {
				$("#side_menu_ctn").removeClass("sidemenu_content_slideIn");
				$("#side_menu_ctn").addClass("sidemenu_content_slideOut");
			}

			$("#side_menu_ul li").on("click", function() {
				var port = {
					"Majuro": 1,
					"Pohnpei": 3,
					"Kosrae": 5,
					"Tarawa": 7,
					"Rabaul": 9,
					"Funafuti": 11,
					"Honiara": 13,
					"Noro": 15,
					"PAGOPAGO": 17,
				}
				var frm = $("#frm_DailyBK");
				let ele = $(this);
				let nav = frm.contents().find("#nav");
				nav.contents()[port[ele.text().trim()]].click();
				sideOut();
			});

			$(".gototop").click(function() {
				$("html,body").animate({
					scrollTop: $("html").offset().top
				});
				return false;
			});
		});
	</script>

	<style>
		iframe {
			min-width: 100%;
		}

		form {
			margin-top: 1em;
			margin-left: 1em;
		}

		#row_head {
			position: fixed;
			z-index: 1;
			min-height: 5%;
			width: 100%;
			display: block;
			background-color: white;
			border-bottom: 1mm double;
			border-color: rgb(0 0 0 / 8%);
		}

		#row_body {
			position: inherit;
			z-index: 0;
		}

		.sidemenu {
			width: 50px;
			height: 50px;
			line-height: 50px;
			text-align: center;
			background: #AAA;
			color: #FFF;
			position: fixed;
			border-radius: 25%;
			top: 26%;
			right: 1.5%;
			text-decoration: none;
			cursor: pointer;
			display: none;
		}

		.sidemenu_content {
			width: 180px;
			top: 26%;
			right: -50%;
			position: fixed;
			background-color: #EEE;
			border-style: solid;
			border-color: #CCC;
		}

		.sidemenu_content_slideIn {
			transition: 0.5s;
			right: 18%;
		}

		.sidemenu_content_slideOut {
			transition: 0.5s;
			right: -50%;
		}

		ul {
			list-style-type: auto;
		}

		li {
			margin: 10 5 10 5;
			font-size: 1.2em;
		}

		li:hover{
			cursor: pointer;
			transition: 0.1s;
			color: blue;
		}

		.gototop {
			width: 50px;
			height: 50px;
			line-height: 50px;
			text-align: center;
			background: #F63E3E;
			color: #FFF;
			position: fixed;
			border-radius: 50%;
			bottom: 1.5%;
			right: 1.5%;
			text-decoration: none;
			cursor: pointer;
			display: none;
		}

	</style>
</head>

<body>
	<div id="row_head" name="row_head">
		<form action="" class="form-inline">
			<label for="datepicker">DatePicker：</label>
			<input id="prv_btn" name="prv_brn" type="button" class="form-control btn btn-outline-success" value="🡨" style="margin-right: 5px;" onclick="set_newDate(new Date($('#datepicker').val()), 0)">
			<input id="datepicker" name="datepicker" type="date"   class="form-control" value="" autocomplete="off" style="min-width: 150px;" required>&nbsp;
			<input id="nxt_btn" name="nxt_brn" type="button" class="form-control btn btn-outline-success" value="🡪" onclick="set_newDate(new Date($('#datepicker').val()), 1);">
		</form>
	</div><br>
	<div class="container-fluid">
		<div id="row_body" name="row_body" class="row">
			<div class="col-12">
				<iframe id="frm_DailyBK" name="frm_DailyBK" src="" scrolling="no" frameborder="0"></iframe>
			</div>
		</div>
	</div>
	<div class="sidemenu">Menu</div>
	<div id="side_menu_ctn" name="side_menu_ctn" class="sidemenu_content">
		<ul id="side_menu_ul" name="side_menu_ul">
			<li><string>&nbsp;</string><string>Majuro</string></li>
			<li><string>&nbsp;</string><string>Pohnpei</string></li>
			<li><string>&nbsp;</string><string>Kosrae</string></li>
			<li><string>&nbsp;</string><string>Tarawa</string></li>
			<li><string>&nbsp;</string><string>Rabaul</string></li>
			<li><string>&nbsp;</string><string>Funafuti</string></li>
			<li><string>&nbsp;</string><string>Honiara</string></li>
			<li><string>&nbsp;</string><string>Noro</string></li>
			<li><string>&nbsp;</string><string>PAGOPAGO</string></li>
		</ul>
	</div>
	<div class="gototop">TOP</div>
</body>

<!-- Test Page is exist or not -->
<script>
	function direct2Page(dailyURL) {
		let web_url = new URL(window.location.href);
		$.ajax({
			// url:web_url.origin + '/DailyBK/'+dailyURL,
			url:web_url.origin + '/page/'+dailyURL,
			type:'HEAD',
			error: function()
			{
				document.getElementById("frm_DailyBK").style.height = "700px";
				$("#frm_DailyBK").attr("src", "404NF.php");
			},
			success: function()
			{
				// Default today
				let frm = document.getElementById("frm_DailyBK");
				frm.style.height = frm.contentWindow.document.body.scrollHeight + "px";
				$("#frm_DailyBK").attr("src", dailyURL);
			}
		});
	}
</script>

<!-- This script for document ready -->
<script type="text/javascript">
	var frm = document.getElementById("frm_DailyBK");
	frm.onload = function(){
		let scrollHeight = frm.contentWindow.document.body.scrollHeight;
		if (scrollHeight < 200) {
			frm.style.height = "700px";
		} else {
			frm.style.height = scrollHeight + "px";
		}
	}

	$(document).ready(function(){
		var dt = new Date($.now());
		var yy = (dt.getFullYear()).toString();
		var mm = (dt.getMonth()+1).toString();
			mm = (mm.length == 1) ? "0"+mm : mm;
		var dd = (dt.getDate()).toString();
			dd = (dd.length == 1) ? "0"+dd : dd;
		var today = yy+"-"+mm+"-"+dd;
		$("#datepicker").val(today);
		// $("#datepicker").attr("min", "2021-11-09"); // 有檔案的紀錄起始日(舊)
		$("#datepicker").attr("min", "2022-08-04"); // 有檔案的紀錄起始日
		$("#datepicker").attr("max", today); // max 預設為今天
		document.title = document.querySelector("meta[name='systemname']").content + " - " + "Daily Report (" + today + ")";

		var row_head_height = $("#row_head").height();
		$("#row_body").css("padding-top", row_head_height);

		direct2Page(yy+"/"+mm+"/"+yy+mm+dd+".html");
	});
</script>

<script type="text/javascript">
	// 使用onchange觸發
	$("#datepicker").change(function(){
		let dt = $(this).val().replaceAll("-", "");
		let yy = dt.substring(0,4);
		let mm = dt.substring(4,6);
		direct2Page(yy+"/"+mm+"/" + dt + ".html");
		document.title = document.querySelector("meta[name='systemname']").content + " - " + "Daily Report (" + $(this).val() + ")";
	});

	function set_newDate(dt, symbol) {
		// 格式轉換yyyymmdd
		function cvt(dt) {
			var mm = (dt.getMonth()+1).toString();
			var dd = (dt.getDate()).toString();
				dd = (dd.length == 1) ? "0"+dd : dd;
			return [
				dt.getFullYear(),
				(mm.length == 1 ? "0"+mm : mm),
				(dd.length == 1 ? "0"+dd : dd)
			];
		}

		// 設定常數 -> min:20220804, max:today
		const minDate = new Date("2022-08-04");
		const maxDate = new Date();

		// 依symbol決定往前或往後
		if (symbol == 0) {
			dt.setDate(dt.getDate()-1);
		} else if(symbol == 1) {
			dt.setDate(dt.getDate()+1);
		}

		// 鎖定日期區間
		dt = dt < minDate ? minDate : dt;
		dt = dt > maxDate ? maxDate : dt;

		// 取得新日期進行頁面更換
		let nd = cvt(dt);
		$("#datepicker").val(nd.join("-"));
		direct2Page(nd[0] + "/" + nd[1] + "/" + nd.join("") + ".html");
		document.title = document.querySelector("meta[name='systemname']").content + " - " + "Daily Report (" + nd.join("-") + ")";
	}
</script>
</html>