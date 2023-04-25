<?php

	/**
	 * For Tracked Control
	 */
	class Ctl_Tracked
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

		function getCurrentData($stat)
		{
			// 撈出現有資料
			$pre = $this->conn->prepare("SELECT SRNB, Tracked FROM VesselList WHERE Tracked = '".$stat."'");
			$pre->execute();
			$rows = $pre->fetchAll();

			$cur_datas =  array();
			if (count($rows)) {
				foreach ($rows as $key => $row) {
					$cur_datas[$row["SRNB"]] = $row["Tracked"];
				}
				return $cur_datas;
			} else {
				return array();
			}
		}

		function Tracked($new_datas)
		{
			try {
				$current_datas = $this->getCurrentData("1");
				$new_js_datas  = json_decode($new_datas);

				foreach ($new_js_datas as $key => $val) {
					if (!array_key_exists($key, $current_datas)) {
						// 代表要加回
						$sql = "UPDATE VesselList SET Tracked = '1' WHERE SRNB = '".$key."'";
						$pre = $this->conn->prepare($sql);
						$pre->execute();
					}
				}
			} catch (Exception $e) {
				print_r("<h3>Func_Tracked Something Wrong !!</h3></br>");
				die(print_r("<h3>".$e->getMessage()."</h3>"));
			}
		}

		function UnTracked($new_datas)
		{
			try {
				$current_datas = $this->getCurrentData("0");
				$new_js_datas  = json_decode($new_datas);

				foreach ($new_js_datas as $key => $val) {
					if (!array_key_exists($key, $current_datas)) {
						// 代表要移除
						$sql = "UPDATE VesselList SET Tracked = '0' WHERE SRNB = '".$key."'";
						$pre = $this->conn->prepare($sql);
						$pre->execute();
					}
				}
			} catch (Exception $e) {
				print_r("<h3>Func_UnTracked Something Wrong !!</h3></br>");
				die(print_r("<h3>".$e->getMessage()."</h3>"));
			}
		}
	}
?>

<script type="text/javascript">
	function goBack(){
		let _URL = new URL(document.URL);
		window.location.href = _URL.origin+"/DualList.php";
	}
</script>

<p>處理中...</p><br>
<button id="btn_bak" name="btn_bak" onclick="goBack()">RTN</button>

<?php
	// main
	$Ctl = new Ctl_Tracked();
	if (isset($_POST["hdn_dt1"]) && isset($_POST["hdn_dt2"])) {
		$Ctl->Tracked($_POST["hdn_dt1"]);
		$Ctl->UnTracked($_POST["hdn_dt2"]);
		echo "<script type='text/javascript'>document.getElementById('btn_bak').click();</script>";
	} else {
		echo "<br><h3>There's no data be passed.</h3><br>";
	}
?>

