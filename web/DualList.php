<?php
	// Import request packages
	include("head.php");

	// SQL Connection
	try {
		$conn = new PDO("sqlsrv:Server=.\SQLEXPRESS;Database=Shipdt", NULL, NULL);
		$conn->exec("SET CHARACTER SET utf8");
		$conn->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION );
	} catch(Exception $e) {
		die(print_r($e->getMessage()));
	}
?>


<?php
	try{
		$pre = $conn->prepare("SELECT SRNB, CODE, CPNY, VSLName1, ShipType, Capacity, Tracked FROM VesselList ORDER BY ShipType DESC, CPNY, VSLName1");
		$pre->execute();
		$VesselList = $pre->fetchAll();

		// 測試看資料用的
		// foreach ($VesselList as $key => $val) {
		// 	print_r($val);
		// 	echo "</br>";
		// }

	} catch(Exception $e) {
		die(print_r($e->getMessage()));
	}
?>

<style>
	html, body {
		max-width: 100%;
		overflow-x: hidden;
	}
</style>

<form id="duallistbox" action="Ctl_Tracked.php" method="POST">
	<div class="row">
		<div class="col-12" style="text-align: right; margin-top: 1em;">
			<input id="btn_rst" name="btn_rst" type="button" class="btn btn-warning btn-lg" value="重置">
			<input id="btn_smt" name="btn_smt" type="button" class="btn btn-primary btn-lg" value="儲存">
			<input id="hdn_dt1" name="hdn_dt1" type="hidden" value="">
			<input id="hdn_dt2" name="hdn_dt2" type="hidden" value="">
		</div>
	</div>
	<div class="row">
		<div class="col-12">
			<select class="form-control" multiple="multiple" name="groups" size="20">
				<!-- 處理追蹤名單 -->
				<?php
					$array_hdn_inform = array();
					if (count($VesselList)) {
						foreach ($VesselList as $key => $val) {
							if ($val["Tracked"] == "1") {
								if ($val["Capacity"]) {
									echo "<option value=\"".$val["SRNB"]."\">[".$val["ShipType"]."] - ".$val["CPNY"]." - ".$val["VSLName1"]." - ".$val["Capacity"]."</option>";
								} else {
									echo "<option value=\"".$val["SRNB"]."\">[".$val["ShipType"]."] - ".$val["CPNY"]." - ".$val["VSLName1"]."</option>";
								}
							} else if ($val["Tracked"] == "0") {
								if ($val["Capacity"]) {
									echo "<option selected value=\"".$val["SRNB"]."\">[".$val["ShipType"]."] - ".$val["CPNY"]." - ".$val["VSLName1"]." - ".$val["Capacity"]."</option>";
								} else {
									echo "<option selected value=\"".$val["SRNB"]."\">[".$val["ShipType"]."] - ".$val["CPNY"]." - ".$val["VSLName1"]."</option>";
								}
							}

							// 記錄SRNB
							$array_hdn_inform[$val["SRNB"]] = array("CODE" => $val["CODE"]);
						}
					}
				?>

				<!-- DualListBox option sample -->
				<!-- <option value="1">GroupA</option>
				<option selected value="2">GroupB</option> -->
			</select>
		</div>
	</div>
</form>

<script type="text/javascript">
	<?php
		sleep(0.5);
		echo "sessionStorage.setItem('tmp_AddInform', JSON.stringify(".json_encode($array_hdn_inform)."));";
	?>
</script>

<script type="text/javascript">
	// This script for DualListBox initial and setting other functions
	var selectorx = $('select[name="groups"]').bootstrapDualListbox({
		nonSelectedListLabel: '已追蹤名單',
		selectedListLabel: '排除名單',

		moveSelectedLabel: "移除",
		moveAllLabel: "移除所有",
		removeSelectedLabel: "加回",
		removeAllLabel: "加回所有",

		infoText: '共有{0}艘船',
		infoTextFiltered: '找到{0}艘船 ,共有{1}艘船',
		infoTextEmpty: '列表無資料',

		preserveSelectionOnMove: 'moved',
		moveOnSelect: false,
		showFilterInputs: true,

		filterOnValues: true,
		selectorMinimalHeight: 3,
		helperSelectNamePostfix: '_selected',
	});

	// DualListBox內容重置
	$("#btn_rst").click(function() {
		$('#duallistbox').trigger('reset');
		selectorx.bootstrapDualListbox('refresh');
	});
</script>

<script type="text/javascript">
	// 儲存結果
	$("#btn_smt").click(function() {
		var datas1 = new Map(); // For Tracked
		var datas2 = new Map(); // For UnTracked

		var opts1 = document.getElementById("bootstrap-duallistbox-nonselected-list_groups").options;
		for (var i = 0; i < opts1.length; i++) {
			key  = opts1[i].value; // As SRNB
			vals = opts1[i].text.split(" - ");

			shiptype = vals[0].replace(/\[|]/g, "");
			company  = vals[1]
			vslname  = vals[2]
			datas1.set(key, [shiptype, company, vslname]);
		}
		datas1 = Object.fromEntries(datas1);

		var opts2 = document.getElementById("bootstrap-duallistbox-selected-list_groups").options;
		for (var i = 0; i < opts2.length; i++) {
			key  = opts2[i].value; // As SRNB
			vals = opts2[i].text.split(" - ");

			shiptype = vals[0].replace(/\[|]/g, "");
			company = vals[1]
			vslname = vals[2]
			datas2.set(key, [shiptype, company, vslname]);
		}
		datas2 = Object.fromEntries(datas2);

		// Convert map to json and save it
		$("#hdn_dt1").val(JSON.stringify(datas1));
		$("#hdn_dt2").val(JSON.stringify(datas2));

		document.forms["duallistbox"].submit();
	});
</script>

<script type="text/javascript">
	var obj_SRNB = JSON.parse(sessionStorage.getItem("tmp_AddInform"));
	function switchContent(source){
		// get options content & related elements
		var sidebox_eles = $("#ifm_Sidebox", window.parent.document).contents();
		if (source=="1") {
			var slt = $("#bootstrap-duallistbox-nonselected-list_groups :selected");
		// 	var rdo_tracked  = sidebox_eles.find("#rdo_tracked_1");
		} else if (source=="2") {
			var slt = $("#bootstrap-duallistbox-selected-list_groups :selected");
		// 	var rdo_tracked  = sidebox_eles.find("#rdo_tracked_2");
		}
		var slt_val = slt.val();
		var slt_txt = slt.text();
		var slt_txt_contents = slt_txt.split(" - ");
		var val_shtp = slt_txt_contents[0];
		var val_cpny = slt_txt_contents[1];
		var val_vsln = slt_txt_contents[2];
		var val_cpcy = (slt_txt_contents.length == 4) ? slt_txt_contents[3] : 0;

		var rdo_shtp_1 = sidebox_eles.find("#rdo_shtp_1");
		var rdo_shtp_2 = sidebox_eles.find("#rdo_shtp_2");
		var rdo_shtp_3 = sidebox_eles.find("#rdo_shtp_3")
		var inp_code   = sidebox_eles.find("#inp_code");
		var inp_cpny   = sidebox_eles.find("#inp_cpny");
		var inp_vsln   = sidebox_eles.find("#inp_vsln");
		var inp_cpcy   = sidebox_eles.find("#inp_cpcy");
		var hdn_SRNB   = sidebox_eles.find("#hdn_SRNB");

		// action
		// rdo_tracked.prop("checked", true);
		inp_code.val(obj_SRNB[slt_val]["CODE"]);
		inp_cpny.val(val_cpny);
		inp_vsln.val(val_vsln);
		inp_cpcy.val(val_cpcy);
		if (val_shtp == "[C]") {
			rdo_shtp_1.prop("checked", true);
		} else if(val_shtp == "[F]") {
			rdo_shtp_2.prop("checked", true);
		} else if(val_shtp == "[N]") {
			rdo_shtp_3.prop("checked", true);
		} else {
			rdo_shtp_1.prop("checked", false);
			rdo_shtp_2.prop("checked", false);
			rdo_shtp_3.prop("checked", false);
		}
		hdn_SRNB.val(slt_val);
	}

	$("#bootstrap-duallistbox-nonselected-list_groups").click(function(){
		switchContent("1");
	});

	$("#bootstrap-duallistbox-selected-list_groups").click(function(){
		switchContent("2");
	});
</script>
