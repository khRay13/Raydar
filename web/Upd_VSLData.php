<?php
	/**
	 * For Vessel Data Update
	 */
	class Upd_VSLData
	{
		public $conn;

		function __construct()
		{
			$this->Conn();
		}

		// SQL Connection
		function Conn(){
			try {
				$this->conn = new PDO("sqlsrv:Server=.\SQLEXPRESS;Database=Shipdt", NULL, NULL);
				$this->conn->exec("SET CHARACTER SET utf8");
				$this->conn->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION );
			} catch(Exception $e) {
				print_r("<h3>Func_Conn Something Wrong !!</h3></br>");
				die(print_r("<h3>".$e->getMessage()."</h3>"));
			}
		}

		function chkVessel($CODE, $VSLN) {
			try {
				// 撈出船隻資料
				$pre = $this->conn->prepare("SELECT SRNB FROM VesselList WHERE CODE = '".$CODE."' OR VSLName1 = '".$VSLN."'");
				$pre->execute();
				$rows = $pre->fetchAll();
				if (count($rows)) {
					return true;
				} else {
					return false;
				}
			} catch (Exception $e) {
				print_r("<h3>Func_chkVessel Something Wrong !!</h3></br>");
				die(print_r("<h3>".$e->getMessage()."</h3>"));
			}
		}

		function istVSL($Tracked, $ShipType, $CODE, $CPNY, $VSLN, $CPCY) {
			if ($this->chkVessel($CODE, $VSLN)) {
				echo "<script>alert('CODE或船名已存在，請確認是否誤勾「新增」！！');</script>";
			} else {
				try {
					if ($Tracked == "Add") {
						$sql = "INSERT INTO VesselList(Tracked, ShipType, CODE, CPNY, VSLName1, VSLName2, VSLName3, Capacity) VALUES('1', '".$ShipType."', '".$CODE."', '".$CPNY."', '".$VSLN."', '', '', '".$CPCY."')";
					} else {
						$sql = "INSERT INTO VesselList(Tracked, ShipType, CODE, CPNY, VSLName1, VSLName2, VSLName3, Capacity) VALUES('0', '".$ShipType."', '".$CODE."', '".$CPNY."', '".$VSLN."', '', '', '".$CPCY."')";
					}
					$pre = $this->conn->prepare($sql);
					$pre->execute();
				} catch (Exception $e) {
					print_r("<h3>Func_istVSL Something Wrong !!</h3></br>");
					die(print_r("<h3>".$e->getMessage()."</h3>"));
				}
			}
		}

		function updVSL($SRNB, $ShipType, $CODE, $CPNY, $VSLN, $CPCY){
			try {
				$sql = "UPDATE VesselList SET ShipType = '".$ShipType."', CODE = '".$CODE."', CPNY = '".$CPNY."', VSLName1 = '".$VSLN."', Capacity = '".$CPCY."' WHERE SRNB = '".$SRNB."'";
				echo "<script>console.log(\"".$sql."\");</script>";
				$pre = $this->conn->prepare($sql);
				$pre->execute();
			} catch (Exception $e) {
				print_r("<h3>Func_updVSL Something Wrong !!</h3></br>");
				die(print_r("<h3>".$e->getMessage()."</h3>"));
			}
		}
	}
?>

<p>處理中...</p><br>
<form id="rtn_frm" name="rtn_frm" action="Sidebox.php" method="POST">
	<input id="rtn_VSLData" name="rtn_VSLData" type="hidden" value="true">
	<button id="btn_bak" name="btn_bak" type="submit">RTN</button>
</form>


<?php
	// main
	$Upd = new Upd_VSLData();

	// 第一層檢查是否要新增的防呆
	if (isset($_POST["ckb_addconfirm"])) {
		// 若勾選代表要做insert
		if (
			isset($_POST["rdo_tracked"]) && isset($_POST["rdo_shtp"]) &&
			isset($_POST["inp_code"]) && isset($_POST["inp_cpny"]) &&
			isset($_POST["inp_vsln"]) && isset($_POST["inp_cpcy"])
		) {
			$Upd->istVSL(
				$_POST["rdo_tracked"],
				$_POST["rdo_shtp"], $_POST["inp_code"],
				$_POST["inp_cpny"], $_POST["inp_vsln"], $_POST["inp_cpcy"]
			);
			echo "<script type='text/javascript'>document.forms['rtn_frm'].submit();</script>";
		} else {
			echo "<br><h3>Something wrong when Form POST[upd].</h3><br>";
		}
	} else {
		// 若無勾選代表要做update
		if (
			isset($_POST["rdo_shtp"]) && isset($_POST["hdn_SRNB"]) &&
			isset($_POST["inp_code"]) && isset($_POST["inp_cpny"]) &&
			isset($_POST["inp_vsln"]) && isset($_POST["inp_cpcy"])
		) {
			$Upd->updVSL(
				$_POST["hdn_SRNB"],
				$_POST["rdo_shtp"], $_POST["inp_code"],
				$_POST["inp_cpny"], $_POST["inp_vsln"], $_POST["inp_cpcy"]
			);
			echo "<script type='text/javascript'>document.forms['rtn_frm'].submit();</script>";
		} else {
			echo "<br><h3>Something wrong when Form POST[ist].</h3><br>";
		}
	}
?>