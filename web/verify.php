<?php
// 預設cookie
if (!isset($_COOKIE["PORT"]) || !isset($_COOKIE["VSLN"])) {
	setcookie("PORT", "99");
	setcookie("VSLN", "INIT");
	setcookie("FLAG", "0");
}

include("head.php");
?>

<html>
	<head>
		<style>
			iframe {
				min-width: 100%;
				min-height: 200%;
			}

			div {
				padding-left: 15px !important;
				padding-right: 15px !important;
			}
		</style>
	</head>
	<body>
		<div class="row" style="max-width: 100%;">
			<form class="form-inline" style="padding-top: 20px !important;">
				<div class="form-group mb-2">
					<label id="lb_VSLN" for="inp_VSLN">Vessel Name：</label>
					<input id="inp_VSLN" type="text" class="form-control" autocomplete="off" required>
				</div>
				<div class="form-group mb-2">
					<label id="lb_PORT" name="lb_PORT" for="drp_PORT">Port：</label>
					<select id="drp_PORT" name="drp_PORT" class="form-control">
						<?php
							$arr = ["01 Majuro", "02 Pohnpei", "03 Kosrae", "04 Tarawa", "05 Rabaul", "06 Funafuti", "07 Honiara", "08 Noro", "09 PAGOPAGO", "10 Victoria", "11 Port_Victoria", "12 Louis", "13 Diego_Suarez", "14 Manta", "15 Posorja", "16 Manzanillo", "17 Mazatlan", "18 Dakar", "19 Abidjan"];
							$cnt = 1;
							foreach ($arr as $key => $val) {
								echo ($cnt < 10) ? "<option value='0{$cnt}'>{$val}</option>" : "<option value='{$cnt}'>{$val}</option>";
								$cnt += 1;
							}
						?>
					</select>
				</div>
				<input id="btn_search" type="button" class="btn btn-primary mb-2" value="Search">
			</form>
		</div>
		<hr>
		<div class="row" style="max-width: 100%; padding-left: 30px !important;">
			<iframe id="frm_data" name="frm_data" src="verify_func.php" frameborder="0"></iframe>
		</div>
	</body>

	<script type="text/javascript">
		$(document).ready(function() {
			var port = $.cookie("PORT");
			if (port != 99) {
				$('select[name=drp_PORT] option[value='+port+']').attr('selected', 'selected');
			}
		});
	</script>

	<script type="text/javascript">
		$("#btn_search").click(function(){
			var vsln = $("#inp_VSLN").val();
			var port = $('select[name=drp_PORT] option').filter(':selected').val();
			if (vsln.trim() === "") {
				alert("Vessel Name");
			} else {
				$.cookie("VSLN", vsln);
				$.cookie("PORT", port);
				location.reload();
			}
		});
	</script>
</html>