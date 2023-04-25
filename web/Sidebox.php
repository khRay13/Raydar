<?php
	// Import request packages
	include("head.php");
?>

<script type="text/javascript">
	function refresh_DualList(){
		var duallist_eles = $("#ifm_DualList", window.parent.document).contents();
		var btn_smt = duallist_eles.find("#btn_smt");
		btn_smt.click();
	}
</script>

<?php
	// 偵測回傳值，用於觸發DualList的儲存鈕
	if (isset($_POST["rtn_VSLData"])) {
		unset($_POST["rtn_VSLData"]);
		echo "<script>refresh_DualList();</script>";
	}
?>

<style>
	html, body {
		max-width: 100%;
		overflow-x: hidden;
	}

	div {
		padding-left: 15px !important;
		padding-right: 15px !important;
	}

	.sidebox {
		top: 30px;
		/*left: 5px;*/
		border: 3px dashed;
		/*max-width: 95%;*/
	}
</style>

<div id="sidebox" name="sidebox" class="col-12 sidebox">
	<form id="frm_VSLInfo" name="frm_VSLInfo" action="Upd_VSLData.php" method="POST">
		<div class="form-check">
			<input id="ckb_addconfirm" name="ckb_addconfirm" class="form-check-input" type="checkbox" value="true">
			<label for="ckb_addconfirm" class="form-check-label">加入至</label>
		</div>
		<div class="row">
			<div class="form-check">
				<input class="form-check-input" id="rdo_tracked_1" name="rdo_tracked" type="radio" value="Add" required disabled>
				<label class="form-check-label" for="rdo_tracked_1">追蹤名單</label>
			</div>
			<div class="form-check">
				<input class="form-check-input" id="rdo_tracked_2" name="rdo_tracked" type="radio" value="Del" required disabled>
				<label class="form-check-label" for="rdo_tracked_2">排除名單</label>
			</div>
		</div>
		<hr>
		<p>[ ShipType ]</p>
		<div class="row">
			<div class="form-check form-check-inline">
				<input type="radio" class="form-check-input" id="rdo_shtp_1" name="rdo_shtp" value="C" required>
				<label for="rdo_shtp_1" class="form-check-label">Carrier</label>
			</div>
			<div class="form-check form-check-inline">
				<input type="radio" class="form-check-input" id="rdo_shtp_2" name="rdo_shtp" value="F" required>
				<label for="rdo_shtp_2" class="form-check-label">FV</label>
			</div>
			<div class="form-check form-check-inline">
				<input type="radio" class="form-check-input" id="rdo_shtp_3" name="rdo_shtp" value="N" required>
				<label for="rdo_shtp_3" class="form-check-label">N/A</label>
			</div>
		</div>
		<hr>
		<p>[ Main ]</p>
		<div class="row">
			<span>Code(MMSI)：</span><input id="inp_code" name="inp_code" type="text" placeholder="MMSI_Code" autocomplete="off" value="CODE000" required>
			<span>Company：</span><input id="inp_cpny" name="inp_cpny" type="text" placeholder="Company_Name" value="unknown" required>
			<span>Vessel：</span><input id="inp_vsln" name="inp_vsln" type="text" placeholder="Vessel_Name" autocomplete="off" required>
			<input id="hdn_SRNB" name="hdn_SRNB" type="hidden">
		</div>
		<hr>
		<p>[ Additional ]</p>
		<div class="row">
			<!-- <span>Flag：</span><input id="inp_flag" name="inp_flag" type="text" placeholder="Flag">
			<span>Trader：</span><input id="inp_tdr" name="inp_tdr" type="text" placeholder="Trader"> -->
			<span>Capacity：</span><input id="inp_cpcy" name="inp_cpcy" type="number" placeholder="Capacity" autocomplete="off" value="0">
		</div>
		<div class="row" style="margin-top: 10px !important;">
			<input id="btn_rst" name="btn_rst" type="reset" class="btn btn-warning" value="重填">&nbsp;
			<input id="btn_smt" name="btn_smt" type="submit" class="btn btn-primary" value="送出/修改">
		</div>
	</form>
</div>

<script type="text/javascript">
	$(document).ready(function(){
		$("#btn_rst").click();
	});

	$("#ckb_addconfirm").change(function(){
		let state = $("#ckb_addconfirm").is(":checked");
		if (state) {
			$("#rdo_tracked_1").removeAttr("disabled");
			$("#rdo_tracked_2").removeAttr("disabled");
		} else {
			$("#rdo_tracked_1").attr("disabled", "true");
			$("#rdo_tracked_2").attr("disabled", "true");
		}
	});
</script>

<script type="text/javascript">
	var newWidth = (document.getElementById("sidebox").offsetWidth*0.8).toString(); // Get new width from sidebox.width*0.8
	var inp_code = document.getElementById("inp_code");
	var inp_cpny = document.getElementById("inp_cpny");
	var inp_vsln = document.getElementById("inp_vsln");
	// var inp_flag = document.getElementById("inp_flag");
	// var inp_tdr  = document.getElementById("inp_tdr");
	var inp_cpcy = document.getElementById("inp_cpcy");
	inp_code.style.width = newWidth + "px";
	inp_cpny.style.width = newWidth + "px";
	inp_vsln.style.width = newWidth + "px";
	// inp_flag.style.width = newWidth + "px";
	// inp_tdr.style.width  = newWidth + "px";
	inp_cpcy.style.width = newWidth + "px";
</script>
